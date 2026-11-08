"""
Módulo de recomendación multicriterio de escuelas y pronóstico rápido de
disponibilidad por simulación Monte Carlo para el Escenario 3 (E3).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.utils import GeneradorAleatorio, PROB_AUSENCIA, SIGMA_LN, haversine_km


@dataclass(frozen=True)
class Escuela:
    id_escuela: str
    cue_anexo: str
    nombre: str
    latitud: float
    longitud: float
    zona: str
    tipo: str  # 'urbana' o 'rural'
    niveles: frozenset[str] = frozenset({"inicial", "primario", "secundario"})


@dataclass(frozen=True)
class Cargo:
    id_cargo: str
    id_escuela: str
    nivel: str
    especialidad: str
    turno: str
    vacantes: int


@dataclass(frozen=True)
class Docente:
    idx: int
    id: str
    puntaje: float
    tiempo_decision_medio: float
    nivel: str
    especialidad: str
    latitud: float
    longitud: float
    preferencias: tuple[str, ...]
    preferencias_set: frozenset[str]
    radio_max_km: float
    turnos: tuple[str, ...]
    turnos_set: frozenset[str]
    acepta_rural: int
    preferencias_ocultas: tuple[str, ...]
    preferencias_ocultas_set: frozenset[str]
    ranking_real_10: tuple[str, ...]


class ContextoPadron:
    """
    Almacena las matrices estáticas precalculadas del padrón (distancias Haversine,
    cercanía D_ij, afinidad colaborativa C_ij y turnos ofrecidos por escuela)
    para evitar recálculos redundantes durante las réplicas de simulación.
    """

    def __init__(
        self,
        escuelas: list[Escuela],
        cargos: list[Cargo],
        docentes: list[Docente],
    ) -> None:
        self.escuelas_lista = escuelas
        self.escuelas: dict[str, Escuela] = {e.id_escuela: e for e in escuelas}
        self.ids_escuelas: tuple[str, ...] = tuple(e.id_escuela for e in escuelas)
        self.cargos_lista = cargos
        self.docentes_lista = docentes
        self.docentes: dict[str, Docente] = {d.id: d for d in docentes}

        # Turnos ofrecidos originalmente en cada escuela según cargos.csv
        turnos_orig: dict[str, set[str]] = {e.id_escuela: set() for e in escuelas}
        for c in cargos:
            turnos_orig[c.id_escuela].add(c.turno)
        self.turnos_originales_escuela: dict[str, frozenset[str]] = {
            esc_id: frozenset(ts) for esc_id, ts in turnos_orig.items()
        }

        # Matriz de distancias d_ij y puntaje de cercanía D_ij = max(0, 1 - d_ij / R_i)
        self.distancias: dict[str, dict[str, float]] = {}
        self.score_cercania: dict[str, dict[str, float]] = {}
        for d in docentes:
            dist_d: dict[str, float] = {}
            cerc_d: dict[str, float] = {}
            for e in escuelas:
                dist = haversine_km(d.latitud, d.longitud, e.latitud, e.longitud)
                dist_d[e.id_escuela] = dist
                cerc_d[e.id_escuela] = max(0.0, 1.0 - dist / d.radio_max_km) if d.radio_max_km > 0 else 0.0
            self.distancias[d.id] = dist_d
            self.score_cercania[d.id] = cerc_d

        # Matriz de filtrado colaborativo C_ij (ecuación de la Sección 3.5.2, solo usa L_i visibles)
        self.score_colaborativo: dict[str, dict[str, float]] = {}
        for d_i in docentes:
            pesos_por_escuela: dict[str, float] = {e.id_escuela: 0.0 for e in escuelas}
            denom = 0.0
            set_i = d_i.preferencias_set
            for d_k in docentes:
                if d_k.id == d_i.id:
                    continue
                inter = len(set_i & d_k.preferencias_set)
                if inter > 0:
                    denom += inter
                    for esc_k in d_k.preferencias:
                        pesos_por_escuela[esc_k] += inter
            if denom > 0.0:
                self.score_colaborativo[d_i.id] = {
                    esc_id: val / denom for esc_id, val in pesos_por_escuela.items()
                }
            else:
                self.score_colaborativo[d_i.id] = pesos_por_escuela

        # Popularidad general (frecuencia en listas visibles L_k de todo el padrón)
        conteo_pop: dict[str, int] = {e.id_escuela: 0 for e in escuelas}
        for d in docentes:
            for esc_id in d.preferencias:
                conteo_pop[esc_id] += 1
        self.popularidad_general = conteo_pop


class EstadoAsamblea:
    """
    Representa el estado dinámico de vacantes abiertas y la fila de docentes
    en un instante puntual de la asamblea (o de una prueba del recomendador).
    """

    def __init__(
        self,
        contexto: ContextoPadron,
        vacantes_cargo: dict[str, int] | None = None,
        docentes_previos: list[Docente] | None = None,
        turnos_virtuales_por_escuela: dict[str, frozenset[str]] | None = None,
    ) -> None:
        self.contexto = contexto
        self.docentes_previos: list[Docente] = docentes_previos or []
        self._turnos_virtuales = turnos_virtuales_por_escuela

        if turnos_virtuales_por_escuela is not None:
            # Modo de validación offline del recomendador sobre el resto del padrón (Sección 5.2.1)
            self.vacantes_cargo = {}
            self.total_vacantes_libres = sum(1 for ts in turnos_virtuales_por_escuela.values() if ts)
            self.por_perfil_escuela_turnos: dict[tuple[str, str], dict[str, dict[str, int]]] = {}
        else:
            self.vacantes_cargo = (
                dict(vacantes_cargo)
                if vacantes_cargo is not None
                else {c.id_cargo: c.vacantes for c in contexto.cargos_lista}
            )
            self.total_vacantes_libres = 0
            self.por_perfil_escuela_turnos = {}
            for c in contexto.cargos_lista:
                v = self.vacantes_cargo.get(c.id_cargo, 0)
                if v > 0:
                    self.total_vacantes_libres += v
                    clave_p = (c.nivel, c.especialidad)
                    mapa_esc = self.por_perfil_escuela_turnos.setdefault(clave_p, {})
                    mapa_turnos = mapa_esc.setdefault(c.id_escuela, {})
                    mapa_turnos[c.turno] = mapa_turnos.get(c.turno, 0) + v

    def turnos_libres_compatibles(self, docente: Docente, id_escuela: str) -> frozenset[str]:
        """Devuelve los turnos con vacante abierta compatible para 'docente' en 'id_escuela'."""
        if self._turnos_virtuales is not None:
            return self._turnos_virtuales.get(id_escuela, frozenset())
        mapa_esc = self.por_perfil_escuela_turnos.get((docente.nivel, docente.especialidad))
        if not mapa_esc:
            return frozenset()
        mapa_turnos = mapa_esc.get(id_escuela)
        if not mapa_turnos:
            return frozenset()
        return frozenset(t for t, cant in mapa_turnos.items() if cant > 0)

    def escuela_tiene_vacante_compatible(self, docente: Docente, id_escuela: str) -> bool:
        """Indica si 'id_escuela' conserva al menos 1 vacante compatible con el perfil del docente."""
        if self._turnos_virtuales is not None:
            return bool(self._turnos_virtuales.get(id_escuela))
        mapa_esc = self.por_perfil_escuela_turnos.get((docente.nivel, docente.especialidad))
        if not mapa_esc:
            return False
        mapa_turnos = mapa_esc.get(id_escuela)
        return bool(mapa_turnos and any(cant > 0 for cant in mapa_turnos.values()))

    def tiene_oferta_perfil(self, nivel: str, especialidad: str) -> bool:
        """Indica si queda al menos una vacante libre para (nivel, especialidad) en toda la asamblea."""
        if self._turnos_virtuales is not None:
            return any(bool(ts) for ts in self._turnos_virtuales.values())
        mapa_esc = self.por_perfil_escuela_turnos.get((nivel, especialidad))
        if not mapa_esc:
            return False
        return any(
            cant > 0
            for mapa_t in mapa_esc.values()
            for cant in mapa_t.values()
        )

    def descontar_cargo(self, cargo: Cargo) -> None:
        """Descuenta 1 vacante del cargo adjudicado manteniendo sincronizado el índice rápido."""
        actual = self.vacantes_cargo.get(cargo.id_cargo, 0)
        if actual <= 0:
            raise ValueError(f"Intento de descontar cargo agotado: {cargo.id_cargo}")
        self.vacantes_cargo[cargo.id_cargo] = actual - 1
        self.total_vacantes_libres -= 1

        clave_p = (cargo.nivel, cargo.especialidad)
        mapa_esc = self.por_perfil_escuela_turnos[clave_p]
        mapa_t = mapa_esc[cargo.id_escuela]
        mapa_t[cargo.turno] -= 1
        if mapa_t[cargo.turno] <= 0:
            del mapa_t[cargo.turno]
        if not mapa_t:
            del mapa_esc[cargo.id_escuela]


def cargar_datos(directorio: str | Path = "data") -> tuple[list[Escuela], list[Cargo], list[Docente], ContextoPadron]:
    """Lee escuelas.csv, cargos.csv y docentes.csv y construye el ContextoPadron."""
    base = Path(directorio)

    escuelas: list[Escuela] = []
    with (base / "escuelas.csv").open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            niv_raw = row.get("niveles", "").strip()
            if niv_raw:
                niveles = frozenset(x.strip() for x in niv_raw.split(";") if x.strip())
            else:
                nom_l = row["nombre"].lower()
                if "secundario" in nom_l or "comercio" in nom_l or "polimodal" in nom_l:
                    niveles = frozenset({"secundario"})
                else:
                    niveles = frozenset({"inicial", "primario"})
            escuelas.append(
                Escuela(
                    id_escuela=row["id_escuela"],
                    cue_anexo=row["cue_anexo"],
                    nombre=row["nombre"],
                    latitud=float(row["latitud"]),
                    longitud=float(row["longitud"]),
                    zona=row["zona"],
                    tipo=row["tipo"],
                    niveles=niveles,
                )
            )

    cargos: list[Cargo] = []
    with (base / "cargos.csv").open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cargos.append(
                Cargo(
                    id_cargo=row["id_cargo"],
                    id_escuela=row["id_escuela"],
                    nivel=row["nivel"],
                    especialidad=row["especialidad"],
                    turno=row["turno"],
                    vacantes=int(row["vacantes"]),
                )
            )

    docentes: list[Docente] = []
    with (base / "docentes.csv").open("r", encoding="utf-8") as f:
        for idx, row in enumerate(csv.DictReader(f)):
            prefs = tuple(x for x in row["preferencias"].split(";") if x)
            ocultas = tuple(x for x in row["preferencias_ocultas"].split(";") if x)
            turnos = tuple(x for x in row["turnos"].split(";") if x)
            docentes.append(
                Docente(
                    idx=idx,
                    id=row["id"],
                    puntaje=float(row["puntaje"]),
                    tiempo_decision_medio=float(row["tiempo_decision_medio"]),
                    nivel=row["nivel"],
                    especialidad=row["especialidad"],
                    latitud=float(row["latitud"]),
                    longitud=float(row["longitud"]),
                    preferencias=prefs,
                    preferencias_set=frozenset(prefs),
                    radio_max_km=float(row["radio_max_km"]),
                    turnos=turnos,
                    turnos_set=frozenset(turnos),
                    acepta_rural=int(row["acepta_rural"]),
                    preferencias_ocultas=ocultas,
                    preferencias_ocultas_set=frozenset(ocultas),
                    ranking_real_10=prefs + ocultas,
                )
            )

    contexto = ContextoPadron(escuelas, cargos, docentes)
    return escuelas, cargos, docentes, contexto


def candidatas(
    docente: Docente,
    estado: EstadoAsamblea,
    excluir_lista_inicial: bool = True,
) -> list[str]:
    """
    Arma el conjunto K_i (Sección 3.5.1): escuelas con al menos una vacante libre
    compatible con el nivel/especialidad del docente que cumplen simultáneamente:
    distancia d_ij <= R_i, turno compatible y condición urbano/rural.
    """
    ctx = estado.contexto
    dists = ctx.distancias[docente.id]
    resultado: list[str] = []

    for id_esc in ctx.ids_escuelas:
        if excluir_lista_inicial and id_esc in docente.preferencias_set:
            continue
        esc = ctx.escuelas[id_esc]
        if docente.nivel not in esc.niveles:
            continue
        if esc.tipo == "rural" and docente.acepta_rural == 0:
            continue
        if dists[id_esc] > docente.radio_max_km:
            continue
        turnos_libres = estado.turnos_libres_compatibles(docente, id_esc)
        if not turnos_libres:
            continue
        if not (turnos_libres & docente.turnos_set):
            continue
        resultado.append(id_esc)

    return resultado


def puntaje_escuela_candidata(
    docente: Docente,
    id_escuela: str,
    estado: EstadoAsamblea,
    pesos: tuple[float, float, float] = (0.50, 0.20, 0.30),
) -> float:
    """
    Calcula Puntaje_ij = w_d * D_ij + w_t * T_ij + w_c * C_ij (Sección 3.5.2).
    """
    w_d, w_t, w_c = pesos
    ctx = estado.contexto

    # 1. Cercanía al domicilio D_ij
    d_ij_score = ctx.score_cercania[docente.id][id_escuela]

    # 2. Parecido con las escuelas precargadas en L_i (T_ij)
    esc_j = ctx.escuelas[id_escuela]
    turnos_libres_j = estado.turnos_libres_compatibles(docente, id_escuela)
    if docente.preferencias:
        acum_t = 0.0
        for id_s in docente.preferencias:
            esc_s = ctx.escuelas[id_s]
            turnos_s = ctx.turnos_originales_escuela[id_s]
            ind_zona = 1.0 if esc_j.zona == esc_s.zona else 0.0
            ind_tipo = 1.0 if esc_j.tipo == esc_s.tipo else 0.0
            ind_turno = 1.0 if (turnos_libres_j & turnos_s) else 0.0
            acum_t += (ind_zona + ind_tipo + ind_turno) / 3.0
        t_ij_score = acum_t / len(docente.preferencias)
    else:
        t_ij_score = 0.0

    # 3. Coincidencia con elecciones de colegas similares (C_ij)
    c_ij_score = ctx.score_colaborativo[docente.id][id_escuela]

    return w_d * d_ij_score + w_t * t_ij_score + w_c * c_ij_score


def recomendar(
    docente: Docente,
    estado: EstadoAsamblea,
    k: int = 3,
    pesos: tuple[float, float, float] = (0.50, 0.20, 0.30),
) -> list[str]:
    """
    Ordena las escuelas candidatas j in K_i \\ L_i por Puntaje_ij decreciente
    y devuelve las k mejores alternativas (Sección 3.5.2).
    """
    cands = candidatas(docente, estado, excluir_lista_inicial=True)
    if not cands:
        return []
    dists = estado.contexto.distancias[docente.id]
    puntuadas = [
        (puntaje_escuela_candidata(docente, esc_id, estado, pesos), -dists[esc_id], esc_id)
        for esc_id in cands
    ]
    puntuadas.sort(reverse=True)
    return [item[2] for item in puntuadas[:k]]


def pronosticar(
    docente: Docente,
    estado: EstadoAsamblea,
    R_MC: int = 200,
    k: int = 3,
    pesos: tuple[float, float, float] = (0.50, 0.20, 0.30),
    tau: float = 10.0,
    rng: GeneradorAleatorio | None = None,
) -> tuple[dict[str, float], list[str], dict[str, float]]:
    """
    Ejecuta R_MC micro-simulaciones Monte Carlo de los docentes previos a 'docente'
    para estimar la probabilidad theta_ij de que cada escuela llegue con vacante
    compatible libre al turno de 'docente' (Sección 3.5.3).

    Retorna:
      - theta: dict id_escuela -> probabilidad estimada theta_ij en [0, 1]
      - sugeridas: top k escuelas alternativas ordenadas por Puntaje_ij * theta_ij
      - puntajes_cands: dict id_escuela -> Puntaje_ij de las candidatas evaluadas
    """
    ctx = estado.contexto
    cands = candidatas(docente, estado, excluir_lista_inicial=True)
    puntajes_cands = {
        esc_id: puntaje_escuela_candidata(docente, esc_id, estado, pesos)
        for esc_id in cands
    }

    escuelas_interes = list(dict.fromkeys(list(docente.preferencias) + cands))

    # Caso sin pronóstico hacia adelante (R_MC <= 0): mirar solo disponibilidad actual
    if R_MC <= 0 or not estado.docentes_previos:
        theta_actual: dict[str, float] = {
            esc_id: (1.0 if estado.escuela_tiene_vacante_compatible(docente, esc_id) else 0.0)
            for esc_id in escuelas_interes
        }
        dists = ctx.distancias[docente.id]
        ordenadas = sorted(
            cands,
            key=lambda eid: (puntajes_cands[eid] * theta_actual[eid], -dists[eid]),
            reverse=True,
        )
        return theta_actual, ordenadas[:k], puntajes_cands

    generador = rng if rng is not None else GeneradorAleatorio(12345)

    # Filtrar únicamente docentes previos de la misma (nivel, especialidad), ya que
    # otros niveles/especialidades no consumen vacantes compatibles con 'docente'.
    clave_obj = (docente.nivel, docente.especialidad)
    previos_mismo_perfil = [
        h for h in estado.docentes_previos if (h.nivel, h.especialidad) == clave_obj
    ]

    if not previos_mismo_perfil:
        theta_directo = {
            esc_id: (1.0 if estado.escuela_tiene_vacante_compatible(docente, esc_id) else 0.0)
            for esc_id in escuelas_interes
        }
        dists = ctx.distancias[docente.id]
        ordenadas = sorted(
            cands,
            key=lambda eid: (puntajes_cands[eid] * theta_directo[eid], -dists[eid]),
            reverse=True,
        )
        return theta_directo, ordenadas[:k], puntajes_cands

    # Instantánea compacta de vacantes abiertas para clave_obj: id_escuela -> [turno, ...]
    mapa_base = estado.por_perfil_escuela_turnos.get(clave_obj, {})
    turnos_base: dict[str, dict[str, int]] = {
        esc_id: dict(mapa_t) for esc_id, mapa_t in mapa_base.items() if mapa_t
    }

    conteo_libre: dict[str, int] = {esc_id: 0 for esc_id in escuelas_interes}

    for _ in range(R_MC):
        # Copia liviana de vacantes compatibles abiertas por escuela y turno
        libres_mc: dict[str, dict[str, int]] = {
            esc_id: dict(mt) for esc_id, mt in turnos_base.items()
        }

        for h in previos_mismo_perfil:
            if not libres_mc:
                break
            # Probabilidad p de desconexión o falla en ese turno
            if generador.random() < PROB_AUSENCIA:
                continue

            # Verificar si alguna escuela de L_h sigue con vacante libre
            esc_elegida: str | None = None
            for esc_lh in h.preferencias:
                if esc_lh in libres_mc:
                    esc_elegida = esc_lh
                    break

            media_mc = 2.0 if esc_elegida is not None else 8.0
            t_sim = generador.lognormal_media(media_mc, SIGMA_LN)
            if t_sim > tau:
                continue

            if esc_elegida is None:
                # L_h agotada: busca dentro de sus filtros K_h (sin usar preferencias_ocultas)
                dists_h = ctx.distancias[h.id]
                opciones_kh: list[str] = []
                for esc_id, mt in libres_mc.items():
                    esc_obj = ctx.escuelas[esc_id]
                    if esc_obj.tipo == "rural" and h.acepta_rural == 0:
                        continue
                    if dists_h[esc_id] > h.radio_max_km:
                        continue
                    if any(t_k in h.turnos_set for t_k in mt):
                        opciones_kh.append(esc_id)
                if opciones_kh:
                    esc_elegida = generador.choice(opciones_kh)
                else:
                    esc_elegida = generador.choice(list(libres_mc.keys()))

            # Descontar 1 vacante de esc_elegida (priorizando turno compatible con h)
            mt_elegida = libres_mc[esc_elegida]
            turno_tomado: str | None = None
            for t_pref in h.turnos:
                if mt_elegida.get(t_pref, 0) > 0:
                    turno_tomado = t_pref
                    break
            if turno_tomado is None:
                turno_tomado = next(iter(mt_elegida.keys()))

            mt_elegida[turno_tomado] -= 1
            if mt_elegida[turno_tomado] <= 0:
                del mt_elegida[turno_tomado]
            if not mt_elegida:
                del libres_mc[esc_elegida]

        for esc_id in escuelas_interes:
            if esc_id in libres_mc:
                conteo_libre[esc_id] += 1

    theta = {esc_id: conteo_libre[esc_id] / R_MC for esc_id in escuelas_interes}
    dists = ctx.distancias[docente.id]
    ordenadas = sorted(
        cands,
        key=lambda eid: (puntajes_cands[eid] * theta[eid], -dists[eid]),
        reverse=True,
    )
    return theta, ordenadas[:k], puntajes_cands


def evaluar_recomendador_hit_rate(
    contexto: ContextoPadron,
    semilla_azar: int = 2026,
) -> dict[str, object]:
    """
    Ejecuta la evaluación y calibración del recomendador de la Sección 5.2.1:
    oculta las preferencias 6 a 10 de los 300 docentes, simula agotadas las 5 de L_i
    y evalúa Hit Rate@3 sobre el resto del padrón para líneas base y grilla de 231 pesos.
    """
    rng = GeneradorAleatorio(semilla_azar)
    docentes = contexto.docentes_lista
    n_doc = len(docentes)

    # Preconstruir estados de prueba por docente (las 5 escuelas de L_i agotadas,
    # el resto del padrón con sus turnos originales disponibles)
    estados_doc: list[EstadoAsamblea] = []
    cands_doc: list[list[str]] = []

    # Precalcular los 3 componentes (D_ij, T_ij, C_ij) para acelerar la grilla de 231 pesos
    componentes_doc: list[dict[str, tuple[float, float, float]]] = []

    for d in docentes:
        turnos_virt = {
            esc_id: (
                frozenset()
                if (
                    esc_id in d.preferencias_set
                    or d.nivel not in contexto.escuelas[esc_id].niveles
                )
                else contexto.turnos_originales_escuela[esc_id]
            )
            for esc_id in contexto.ids_escuelas
        }
        est = EstadoAsamblea(contexto, turnos_virtuales_por_escuela=turnos_virt)
        estados_doc.append(est)
        cands = candidatas(d, est, excluir_lista_inicial=True)
        cands_doc.append(cands)

        comp_d: dict[str, tuple[float, float, float]] = {}
        for esc_id in cands:
            d_val = puntaje_escuela_candidata(d, esc_id, est, (1.0, 0.0, 0.0))
            t_val = puntaje_escuela_candidata(d, esc_id, est, (0.0, 1.0, 0.0))
            c_val = puntaje_escuela_candidata(d, esc_id, est, (0.0, 0.0, 1.0))
            comp_d[esc_id] = (d_val, t_val, c_val)
        componentes_doc.append(comp_d)

    # 1. Azar dentro del filtro K_i (promedio sobre 100 sorteos por docente para estabilidad)
    aciertos3_azar_acum = 0.0
    aciertos1_azar_acum = 0.0
    for d, cands in zip(docentes, cands_doc):
        if not cands:
            continue
        k_sel = min(3, len(cands))
        hits3_d = 0
        hits1_d = 0
        for _ in range(100):
            elegidas = rng.sample_ponderado_sin_reposicion(cands, [1.0] * len(cands), k_sel)
            if any(e in d.preferencias_ocultas_set for e in elegidas):
                hits3_d += 1
            if elegidas and elegidas[0] in d.preferencias_ocultas_set:
                hits1_d += 1
        aciertos3_azar_acum += hits3_d / 100.0
        aciertos1_azar_acum += hits1_d / 100.0
    hr_azar = 100.0 * aciertos3_azar_acum / n_doc
    hr1_azar = 100.0 * aciertos1_azar_acum / n_doc

    # 2. Popularidad general (dentro del filtro K_i para comparación justa de ordenamiento)
    aciertos3_pop = 0
    aciertos1_pop = 0
    for d, cands in zip(docentes, cands_doc):
        dists = contexto.distancias[d.id]
        ord_pop = sorted(
            cands,
            key=lambda eid: (contexto.popularidad_general[eid], -dists[eid]),
            reverse=True,
        )[:3]
        if any(e in d.preferencias_ocultas_set for e in ord_pop):
            aciertos3_pop += 1
        if ord_pop and ord_pop[0] in d.preferencias_ocultas_set:
            aciertos1_pop += 1
    hr_pop = 100.0 * aciertos3_pop / n_doc
    hr1_pop = 100.0 * aciertos1_pop / n_doc

    def medir_pesos(w_d: float, w_t: float, w_c: float) -> tuple[float, float]:
        hits3 = 0
        hits1 = 0
        for d, cands, comp_d in zip(docentes, cands_doc, componentes_doc):
            dists = contexto.distancias[d.id]
            top3 = sorted(
                cands,
                key=lambda eid: (
                    w_d * comp_d[eid][0] + w_t * comp_d[eid][1] + w_c * comp_d[eid][2],
                    -dists[eid],
                ),
                reverse=True,
            )[:3]
            if any(e in d.preferencias_ocultas_set for e in top3):
                hits3 += 1
            if top3 and top3[0] in d.preferencias_ocultas_set:
                hits1 += 1
        return 100.0 * hits3 / n_doc, 100.0 * hits1 / n_doc

    hr_cercania, hr1_cercania = medir_pesos(1.0, 0.0, 0.0)
    hr_parecido, hr1_parecido = medir_pesos(0.0, 1.0, 0.0)
    hr_colab, hr1_colab = medir_pesos(0.0, 0.0, 1.0)
    hr_inicial, hr1_inicial = medir_pesos(0.50, 0.20, 0.30)

    # Búsqueda exhaustiva en la grilla de paso 0.05 (231 combinaciones en el símplex)
    mejor_hr = -1.0
    mejor_hr1 = -1.0
    mejores_pesos = (0.50, 0.20, 0.30)
    total_combinaciones = 0

    for i_d in range(21):
        for i_t in range(21 - i_d):
            i_c = 20 - i_d - i_t
            w_d = round(i_d * 0.05, 2)
            w_t = round(i_t * 0.05, 2)
            w_c = round(i_c * 0.05, 2)
            total_combinaciones += 1
            hr3, hr1 = medir_pesos(w_d, w_t, w_c)
            # Desempate jerárquico: 1) mayor Hit Rate@3, 2) mayor Hit Rate@1, 3) cercanía al peso inicial
            dist_ini = abs(w_d - 0.50) + abs(w_t - 0.20) + abs(w_c - 0.30)
            dist_mejor = (
                abs(mejores_pesos[0] - 0.50)
                + abs(mejores_pesos[1] - 0.20)
                + abs(mejores_pesos[2] - 0.30)
            )
            tupla_cand = (round(hr3, 9), round(hr1, 9), round(-dist_ini, 9))
            tupla_best = (round(mejor_hr, 9), round(mejor_hr1, 9), round(-dist_mejor, 9))
            if tupla_cand > tupla_best:
                mejor_hr = hr3
                mejor_hr1 = hr1
                mejores_pesos = (w_d, w_t, w_c)

    return {
        "n_docentes": n_doc,
        "combinaciones_evaluadas": total_combinaciones,
        "tamano_medio_Ki": sum(len(c) for c in cands_doc) / n_doc,
        "hr_azar": hr_azar,
        "hr_popularidad": hr_pop,
        "hr_solo_cercania": hr_cercania,
        "hr_solo_parecido": hr_parecido,
        "hr_solo_colaborativo": hr_colab,
        "hr_pesos_iniciales": hr_inicial,
        "mejores_pesos": mejores_pesos,
        "hr_mejor_grilla": mejor_hr,
        "hr1_azar": hr1_azar,
        "hr1_popularidad": hr1_pop,
        "hr1_solo_cercania": hr1_cercania,
        "hr1_solo_parecido": hr1_parecido,
        "hr1_solo_colaborativo": hr1_colab,
        "hr1_pesos_iniciales": hr1_inicial,
        "hr1_mejor_grilla": mejor_hr1,
    }

