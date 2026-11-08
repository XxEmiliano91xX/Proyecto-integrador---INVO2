"""
Motor de simulación de eventos discretos (SED) basado en heapq (FEL):
1. Modo estacionario abierto (M/M/1 y M/M/c) para verificación analítica (Sección 5.1).
2. Modo jornada finita para las asambleas docentes de Salta Capital en los
   escenarios E1, E2 y E3 con números aleatorios comunes por réplica (Sección 3 y 5.3).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
import math

from src.recomendador import (
    Cargo,
    ContextoPadron,
    Docente,
    EstadoAsamblea,
    candidatas,
    pronosticar,
)
from src.utils import (
    ALPHA_SUAVIZACION,
    GeneradorAleatorio,
    PROB_AUSENCIA,
    SIGMA_LN,
    S_HAT_INICIAL,
    T_AUSENCIA,
    T_PASE_SIN_OFERTA,
    VENTANA_AVISO_MIN,
    lognormal_desde_z,
)


@dataclass
class ResultadoMMC:
    lam: float
    mu: float
    c: int
    wq_medio: float
    w_medio: float
    lq_tiempo: float
    l_tiempo: float
    p0_tiempo: float
    utilizacion: float


def simular_cola_abierta_mmc(
    lam: float,
    mu: float,
    c: int = 1,
    n_warmup: int = 10_000,
    n_medidos: int = 100_000,
    semilla: int = 100,
) -> ResultadoMMC:
    """
    Simula una cola abierta M/M/c (disciplina FCFS) mediante lista de eventos futuros (heapq).
    Descarta los primeros 'n_warmup' arribos para alcanzar régimen estacionario y mide
    sobre los siguientes 'n_medidos' clientes e integrales continuas exactas en [t_ini, t_fin].
    """
    rng = GeneradorAleatorio(semilla)
    n_total_arribos = n_warmup + n_medidos

    # Eventos en FEL: (tiempo, orden_desempate, tipo_evento, id_cliente)
    # tipo_evento: 0 = SALIDA, 1 = ARRIBO
    fel: list[tuple[float, int, int, int]] = []
    seq = 0

    t_primero = rng.exponential(lam)
    heapq.heappush(fel, (t_primero, seq, 1, 0))
    seq += 1

    reloj = 0.0
    servidores_ocupados = 0
    cola_fcfs: deque[tuple[int, float]] = deque()

    # Acumuladores continuos en la ventana estacionaria [t_inicio_med, t_fin_med]
    midiendo_tiempo = False
    t_inicio_med = 0.0
    t_fin_med = 0.0
    t_ultimo_cambio = 0.0
    area_cola = 0.0
    area_sistema = 0.0
    tiempo_vacio = 0.0

    # Acumuladores por cliente para los clientes con índice en [n_warmup, n_warmup + n_medidos)
    suma_wq = 0.0
    suma_w = 0.0
    clientes_medidos_completados = 0

    def actualizar_areas(t_nuevo: float) -> None:
        nonlocal t_ultimo_cambio, area_cola, area_sistema, tiempo_vacio
        if not midiendo_tiempo:
            t_ultimo_cambio = t_nuevo
            return
        dt = t_nuevo - t_ultimo_cambio
        if dt > 0.0:
            n_q = len(cola_fcfs)
            n_s = n_q + servidores_ocupados
            area_cola += n_q * dt
            area_sistema += n_s * dt
            if n_s == 0:
                tiempo_vacio += dt
            t_ultimo_cambio = t_nuevo

    while fel:
        t_ev, _, tipo_ev, cid = heapq.heappop(fel)
        actualizar_areas(t_ev)
        reloj = t_ev

        if tipo_ev == 1:  # ARRIBO
            if cid == n_warmup:
                midiendo_tiempo = True
                t_inicio_med = reloj
                t_ultimo_cambio = reloj
            elif cid == n_total_arribos:
                # Cierre exacto de la ventana temporal estacionaria en el arribo n_warmup + n_medidos
                midiendo_tiempo = False
                t_fin_med = reloj

            # Agendar próximo arribo hasta cubrir la ventana + clientes medidos
            if cid < n_total_arribos:
                t_sig = reloj + rng.exponential(lam)
                heapq.heappush(fel, (t_sig, seq, 1, cid + 1))
                seq += 1

            # Si es el arribo centinela cid == n_total_arribos, no necesitamos medirlo;
            # pero sigue entrando al sistema si aún faltan salir clientes medidos previos.
            if servidores_ocupados < c:
                servidores_ocupados += 1
                dur_serv = rng.exponential(mu)
                if n_warmup <= cid < n_total_arribos:
                    suma_w += dur_serv
                heapq.heappush(fel, (reloj + dur_serv, seq, 0, cid))
                seq += 1
            else:
                cola_fcfs.append((cid, reloj))

        else:  # SALIDA
            if n_warmup <= cid < n_total_arribos:
                clientes_medidos_completados += 1
                if clientes_medidos_completados >= n_medidos and not midiendo_tiempo:
                    break

            if cola_fcfs:
                sig_cid, t_arr_sig = cola_fcfs.popleft()
                espera = reloj - t_arr_sig
                dur_serv = rng.exponential(mu)
                if n_warmup <= sig_cid < n_total_arribos:
                    suma_wq += espera
                    suma_w += espera + dur_serv
                heapq.heappush(fel, (reloj + dur_serv, seq, 0, sig_cid))
                seq += 1
            else:
                servidores_ocupados -= 1

    duracion_ventana = t_fin_med - t_inicio_med
    lq_est = area_cola / duracion_ventana
    l_est = area_sistema / duracion_ventana
    p0_est = tiempo_vacio / duracion_ventana
    wq_est = suma_wq / n_medidos
    w_est = suma_w / n_medidos

    return ResultadoMMC(
        lam=lam,
        mu=mu,
        c=c,
        wq_medio=wq_est,
        w_medio=w_est,
        lq_tiempo=lq_est,
        l_tiempo=l_est,
        p0_tiempo=p0_est,
        utilizacion=(l_est - lq_est) / c,
    )


@dataclass
class ResultadoReplicaAsamblea:
    escenario: str
    replica: int
    wq_atendidos: float
    wq_primer_turno: float
    w_convocados: float
    lq: float
    t_total_min: float
    t_total_horas: float
    pct_reintentos: float
    pct_vacantes_cubiertas: float
    pct_sin_oferta: float
    satisfaccion_media: float
    mae_aviso: float
    pct_afectacion_merito_llamados: float
    pct_afectacion_merito_sobre_reintentos: float
    cant_llamados_principal: int
    cant_atendidos_unicos: int
    cant_derivados_reintento: int
    cant_afectados_merito: int
    cant_cargos_cubiertos: int
    cant_casos_A: int
    cant_casos_B: int
    cant_casos_C: int
    # Pares (theta_mc, theta_base_actual, y_real) registrados en los preavisos para evaluar MSE/RMSE
    registros_pronostico: list[tuple[float, float, int]]


def _elegir_cargo_adjudicado(
    docente: Docente,
    caso: str,
    estado: EstadoAsamblea,
    sugeridas_aviso: list[str],
    puntajes_aviso: dict[str, float],
    u_azar: float,
) -> Cargo | None:
    """
    Selecciona el cargo concreto a adjudicar según las reglas de la Sección 3.5.4 (Casos A, B y C).
    """
    ctx = estado.contexto
    # Reunir cargos compatibles actualmente libres agrupados por escuela
    cargos_por_escuela: dict[str, list[Cargo]] = {}
    todos_compatibles: list[Cargo] = []
    for cargo in ctx.cargos_lista:
        if (
            estado.vacantes_cargo.get(cargo.id_cargo, 0) > 0
            and cargo.nivel == docente.nivel
            and cargo.especialidad == docente.especialidad
        ):
            cargos_por_escuela.setdefault(cargo.id_escuela, []).append(cargo)
            todos_compatibles.append(cargo)

    if not todos_compatibles:
        return None

    def tomar_mejor_cargo_de_escuela(id_esc: str) -> Cargo:
        lista_c = cargos_por_escuela[id_esc]
        for c in lista_c:
            if c.turno in docente.turnos_set:
                return c
        return lista_c[0]

    # Caso A: primera escuela con vacante compatible siguiendo el orden estricto de L_i (1 a 5)
    if caso == "A":
        for id_esc in docente.preferencias:
            if id_esc in cargos_por_escuela:
                return tomar_mejor_cargo_de_escuela(id_esc)

    # Caso B (solo E3): entre las escuelas recomendadas del aviso previo que siguen libres,
    # elige la mejor ubicada en preferencias_ocultas (6 a 10) o, si ninguna coincide, la de mayor Puntaje_ij
    if caso == "B":
        libres_sug = [eid for eid in sugeridas_aviso if eid in cargos_por_escuela]
        if libres_sug:
            for oculta_id in docente.preferencias_ocultas:
                if oculta_id in libres_sug:
                    return tomar_mejor_cargo_de_escuela(oculta_id)
            mejor_sug = max(
                libres_sug,
                key=lambda eid: (puntajes_aviso.get(eid, 0.0), -ctx.distancias[docente.id][eid]),
            )
            return tomar_mejor_cargo_de_escuela(mejor_sug)

    # Caso C (y respaldo si justo otro canal paralelo ocupó la escuela durante el turno):
    cands_ki = [
        eid for eid in candidatas(docente, estado, excluir_lista_inicial=False)
        if eid in cargos_por_escuela
    ]
    if cands_ki:
        set_ki = set(cands_ki)
        for pref_id in docente.ranking_real_10:
            if pref_id in set_ki:
                return tomar_mejor_cargo_de_escuela(pref_id)
        idx_sel = min(len(cands_ki) - 1, int(u_azar * len(cands_ki)))
        return tomar_mejor_cargo_de_escuela(cands_ki[idx_sel])

    # Si K_i está vacío pero quedan cargos compatibles fuera de su radio/turno habitual
    idx_rem = min(len(todos_compatibles) - 1, int(u_azar * len(todos_compatibles)))
    return todos_compatibles[idx_rem]


def simular_asamblea(
    escenario: str,
    contexto: ContextoPadron,
    c: int = 1,
    tau: float = 10.0,
    p_rec: float = 0.70,
    R_MC: int = 200,
    pesos: tuple[float, float, float] = (0.40, 0.40, 0.20),
    semilla_replica: int = 1000,
    registrar_pronostico: bool = False,
) -> ResultadoReplicaAsamblea:
    """
    Ejecuta una réplica completa de la asamblea docente en el escenario E1, E2 o E3.
    Utiliza números aleatorios sincronizados por docente y ronda para reducir varianza
    entre escenarios (Common Random Numbers, Law 2015) y ejecuta los 3 asserts automáticos
    de consistencia al cierre (Sección 5.1).
    """
    if escenario not in ("E1", "E2", "E3"):
        raise ValueError(f"Escenario inválido: {escenario}")

    usa_ventana_y_reintentos = escenario in ("E2", "E3")
    usa_recomendador = escenario == "E3"

    # 1. Pre-sortear números aleatorios sincronizados por docente (ronda 1 y ronda 2)
    rng_doc = GeneradorAleatorio(semilla_replica)
    rng_mc = GeneradorAleatorio(semilla_replica + 900_000)

    sorteos_doc: dict[str, dict[int, tuple[float, float, float, float]]] = {}
    docentes_ordenados = sorted(contexto.docentes_lista, key=lambda d: d.puntaje, reverse=True)
    for d in docentes_ordenados:
        sorteos_doc[d.id] = {
            1: (rng_doc.random(), rng_doc.normal(0.0, 1.0), rng_doc.random(), rng_doc.random()),
            2: (rng_doc.random(), rng_doc.normal(0.0, 1.0), rng_doc.random(), rng_doc.random()),
        }

    estado = EstadoAsamblea(contexto)

    # Colas: principal (ordenada por puntaje decreciente) y secundaria de reintentos
    cola_principal: deque[Docente] = deque(docentes_ordenados)
    cola_reintentos: list[Docente] = []  # Se mantiene ordenada por puntaje decreciente

    # Seguimiento exacto de esperas individuales Q_i e integral continua N_cola(t)
    en_cola: dict[str, bool] = {d.id: True for d in docentes_ordenados}
    t_entrada_cola: dict[str, float] = {d.id: 0.0 for d in docentes_ordenados}
    q_acum: dict[str, float] = {d.id: 0.0 for d in docentes_ordenados}
    q_primer_turno: dict[str, float] = {}
    area_cola = 0.0
    reloj = 0.0

    # Estado de los c servidores (mesas/comisiones)
    serv_docente: list[Docente | None] = [None] * c
    serv_inicio: list[float] = [0.0] * c
    serv_sin_oferta: list[bool] = [False] * c
    serv_ronda: list[int] = [0] * c
    serv_caso: list[str] = [""] * c
    serv_turno_id: list[int] = [-1] * c

    # Estimador dinámico de horario (Sección 3.4)
    s_hat = S_HAT_INICIAL
    avisados_hora: dict[str, float] = {}
    errores_aviso: list[float] = []
    atendidos_en_cero: set[str] = set()

    # Datos guardados del aviso enriquecido en E3
    sugeridas_guardadas: dict[str, tuple[list[str], dict[str, float]]] = {}
    pronosticos_pendientes: dict[str, tuple[dict[str, float], dict[str, float]]] = {}
    registros_pronostico: list[tuple[float, float, int]] = []

    # Contadores y registros para métricas y controles de consistencia
    puntajes_inicio_principal: list[float] = []
    llamados_principal: set[str] = set()
    atendidos_unicos: set[str] = set()
    derivados_reintento: set[str] = set()
    sin_oferta_en_reintento: set[str] = set()
    llamados_conteo = {"total": 0, "sin_oferta": 0}
    casos_conteo = {"A": 0, "B": 0, "C": 0}

    adjudicaciones: dict[str, Cargo] = {}
    puntajes_ganadores_por_perfil: dict[tuple[str, str], list[float]] = {}

    # Lista de Eventos Futuros (FEL) con heapq:
    # (tiempo_evento, seq, tipo_evento, id_turno, id_servidor)
    # tipo_evento: 'FIN_SIN_OFERTA', 'FIN_AUSENCIA', 'FIN_ELECCION', 'VENCE_VENTANA'
    fel: list[tuple[float, int, str, int, int]] = []
    seq_ev = 0
    contador_turno = 0

    def avanzar_reloj(t_nuevo: float) -> None:
        nonlocal reloj, area_cola
        dt = t_nuevo - reloj
        if dt > 0.0:
            n_esperando = len(cola_principal) + len(cola_reintentos)
            area_cola += n_esperando * dt
            reloj = t_nuevo

    def iniciar_turno_en_mesa(id_mesa: int, docente: Docente, ronda: int) -> None:
        nonlocal seq_ev, contador_turno
        # Cerrar tramo de espera en cola de este docente
        q_acum[docente.id] += reloj - t_entrada_cola[docente.id]
        en_cola[docente.id] = False

        atendidos_unicos.add(docente.id)
        llamados_conteo["total"] += 1
        if ronda == 1:
            q_primer_turno[docente.id] = reloj
            llamados_principal.add(docente.id)
            puntajes_inicio_principal.append(docente.puntaje)
            if reloj == 0.0:
                atendidos_en_cero.add(docente.id)
            if docente.id in avisados_hora:
                errores_aviso.append(abs(avisados_hora[docente.id] - reloj))

        # Si tenía un pronóstico pendiente en E3, contrastar theta_ij contra realidad y_ij en su turno
        if registrar_pronostico and ronda == 1 and docente.id in pronosticos_pendientes:
            theta_mc_map, theta_base_map = pronosticos_pendientes.pop(docente.id)
            for esc_id, th_mc in theta_mc_map.items():
                th_base = theta_base_map[esc_id]
                # Evaluar sobre las escuelas que estaban abiertas al emitir el aviso
                if th_base > 0.5:
                    y_real = 1 if estado.escuela_tiene_vacante_compatible(docente, esc_id) else 0
                    registros_pronostico.append((th_mc, th_base, y_real))

        contador_turno += 1
        tid = contador_turno
        serv_docente[id_mesa] = docente
        serv_inicio[id_mesa] = reloj
        serv_ronda[id_mesa] = ronda
        serv_turno_id[id_mesa] = tid

        # 1. Chequear si quedan vacantes compatibles para (nivel, especialidad)
        if not estado.tiene_oferta_perfil(docente.nivel, docente.especialidad):
            serv_sin_oferta[id_mesa] = True
            serv_caso[id_mesa] = "SIN_OFERTA"
            llamados_conteo["sin_oferta"] += 1
            if ronda == 2:
                sin_oferta_en_reintento.add(docente.id)
            heapq.heappush(fel, (reloj + T_PASE_SIN_OFERTA, seq_ev, "FIN_SIN_OFERTA", tid, id_mesa))
            seq_ev += 1
            return

        serv_sin_oferta[id_mesa] = False
        u_aus, z_ln, u_rec, _ = sorteos_doc[docente.id][ronda]

        # 2. Chequear ausencia o corte de conexión (probabilidad p = 0.08)
        if u_aus < PROB_AUSENCIA:
            serv_caso[id_mesa] = "AUSENCIA"
            heapq.heappush(fel, (reloj + T_AUSENCIA, seq_ev, "FIN_AUSENCIA", tid, id_mesa))
            seq_ev += 1
            return

        # 3. Docente conectado con oferta compatible: clasificar en Caso A, B o C (Sección 3.5.4)
        tiene_lista_libre = any(
            estado.escuela_tiene_vacante_compatible(docente, eid)
            for eid in docente.preferencias
        )
        if tiene_lista_libre:
            caso = "A"
            mult = 1.0
        elif usa_recomendador:
            sug_prev, _ = sugeridas_guardadas.get(docente.id, ([], {}))
            alguna_sug_libre = any(
                estado.escuela_tiene_vacante_compatible(docente, eid)
                for eid in sug_prev
            )
            if alguna_sug_libre and u_rec < p_rec:
                caso = "B"
                mult = 2.0
            else:
                caso = "C"
                mult = 4.0
        else:
            caso = "C"
            mult = 4.0

        serv_caso[id_mesa] = caso
        casos_conteo[caso] += 1

        t_eleccion = lognormal_desde_z(z_ln, mult * docente.tiempo_decision_medio, SIGMA_LN)

        # Agendar fin de elección y (en E2/E3) evento competitivo de vencimiento de ventana tau
        heapq.heappush(fel, (reloj + t_eleccion, seq_ev, "FIN_ELECCION", tid, id_mesa))
        seq_ev += 1
        if usa_ventana_y_reintentos:
            heapq.heappush(fel, (reloj + tau, seq_ev, "VENCE_VENTANA", tid, id_mesa))
            seq_ev += 1

    def asignar_mesas_libres() -> None:
        if estado.total_vacantes_libres <= 0:
            return
        for m in range(c):
            if serv_docente[m] is not None:
                continue
            if cola_principal:
                sig_doc = cola_principal.popleft()
                iniciar_turno_en_mesa(m, sig_doc, ronda=1)
            elif cola_reintentos:
                # La cola secundaria solo se atiende cuando ya pasó toda la cola principal
                # Para c > 1 verificamos además que no quede ningún turno de ronda 1 en curso
                hay_ronda1_en_mesa = any(
                    serv_docente[k] is not None and serv_ronda[k] == 1 for k in range(c)
                )
                if not hay_ronda1_en_mesa:
                    sig_doc = cola_reintentos.pop(0)
                    iniciar_turno_en_mesa(m, sig_doc, ronda=2)

    def emitir_avisos_anticipados() -> None:
        """Recalcula E[T_k] y emite el aviso único de 10 min en E2 y E3 (Sección 3.4 y 3.5.3)."""
        if not usa_ventana_y_reintentos or estado.total_vacantes_libres <= 0:
            return

        suma_rem_mesas = 0.0
        docentes_en_mesa_con_oferta: list[Docente] = []
        for m in range(c):
            d_m = serv_docente[m]
            if d_m is not None:
                t_trans = reloj - serv_inicio[m]
                esp_m = T_PASE_SIN_OFERTA if serv_sin_oferta[m] else s_hat
                suma_rem_mesas += max(0.0, esp_m - t_trans)
                if not serv_sin_oferta[m] and serv_caso[m] != "AUSENCIA":
                    docentes_en_mesa_con_oferta.append(d_m)

        # Recorrer docentes pendientes en la cola principal
        lista_espera = list(cola_principal)
        suma_previos = 0.0

        for idx_cola, d_k in enumerate(lista_espera):
            e_tk = reloj + (suma_rem_mesas + suma_previos) / c
            if (
                d_k.id not in avisados_hora
                and d_k.id not in atendidos_en_cero
                and (e_tk - reloj) <= VENTANA_AVISO_MIN + 1e-9
            ):
                avisados_hora[d_k.id] = e_tk
                if usa_recomendador:
                    previos = docentes_en_mesa_con_oferta + lista_espera[:idx_cola]
                    est_aviso = EstadoAsamblea(
                        contexto,
                        vacantes_cargo=estado.vacantes_cargo,
                        docentes_previos=previos,
                    )
                    theta_mc, sug_top3, punt_cands = pronosticar(
                        d_k,
                        est_aviso,
                        R_MC=R_MC,
                        k=3,
                        pesos=pesos,
                        tau=tau,
                        rng=rng_mc,
                    )
                    sugeridas_guardadas[d_k.id] = (sug_top3, punt_cands)
                    if registrar_pronostico:
                        theta_base = {
                            eid: (
                                1.0
                                if est_aviso.escuela_tiene_vacante_compatible(d_k, eid)
                                else 0.0
                            )
                            for eid in theta_mc
                        }
                        pronosticos_pendientes[d_k.id] = (theta_mc, theta_base)

            esp_dk = (
                s_hat
                if estado.tiene_oferta_perfil(d_k.nivel, d_k.especialidad)
                else T_PASE_SIN_OFERTA
            )
            suma_previos += esp_dk

    # Apertura del acto en t = 0: ocupan las c mesas los primeros postulantes y salen primeros avisos
    asignar_mesas_libres()
    emitir_avisos_anticipados()

    # Bucle principal de eventos discretos (FEL)
    while fel:
        t_ev, _, tipo_ev, tid_ev, m_ev = heapq.heappop(fel)
        # Si el evento corresponde a un turno ya cancelado (ej. el competitivo que perdió), ignorar
        if serv_docente[m_ev] is None or serv_turno_id[m_ev] != tid_ev:
            continue

        avanzar_reloj(t_ev)

        doc_actual = serv_docente[m_ev]
        assert doc_actual is not None
        ronda_actual = serv_ronda[m_ev]
        caso_actual = serv_caso[m_ev]
        s_obs = reloj - serv_inicio[m_ev]

        # Liberar servidor
        serv_docente[m_ev] = None
        serv_turno_id[m_ev] = -1

        # Actualizar suavización exponencial simple si el docente tenía oferta al iniciar su turno
        if caso_actual != "SIN_OFERTA":
            s_hat = ALPHA_SUAVIZACION * s_obs + (1.0 - ALPHA_SUAVIZACION) * s_hat

        if tipo_ev == "FIN_SIN_OFERTA":
            # Se retira como sin oferta en t_pase = 0.5 min
            pass

        elif tipo_ev in ("FIN_AUSENCIA", "VENCE_VENTANA"):
            # En E2/E3 y primera ronda pasa a cola secundaria de reintentos conservando puntaje P_i
            if usa_ventana_y_reintentos and ronda_actual == 1:
                derivados_reintento.add(doc_actual.id)
                cola_reintentos.append(doc_actual)
                cola_reintentos.sort(key=lambda d: d.puntaje, reverse=True)
                t_entrada_cola[doc_actual.id] = reloj
                en_cola[doc_actual.id] = True

        elif tipo_ev == "FIN_ELECCION":
            # El docente confirma vacante dentro del turno
            _, _, _, u_azar = sorteos_doc[doc_actual.id][ronda_actual]
            sug_prev, punt_prev = sugeridas_guardadas.get(doc_actual.id, ([], {}))
            cargo_sel = _elegir_cargo_adjudicado(
                doc_actual, caso_actual, estado, sug_prev, punt_prev, u_azar
            )
            if cargo_sel is not None:
                estado.descontar_cargo(cargo_sel)
                adjudicaciones[doc_actual.id] = cargo_sel
                puntajes_ganadores_por_perfil.setdefault(
                    (cargo_sel.nivel, cargo_sel.especialidad), []
                ).append(doc_actual.puntaje)

                # Condición de cierre inmediato al cubrirse el último cargo vacante (Sección 3.1)
                if estado.total_vacantes_libres == 0:
                    # Cancelar cualquier otro servidor en paralelo y cerrar el acto en reloj
                    for k_m in range(c):
                        serv_docente[k_m] = None
                        serv_turno_id[k_m] = -1
                    break

        asignar_mesas_libres()
        emitir_avisos_anticipados()

        # Si no quedan servidores ocupados ni docentes en ninguna cola, finaliza la jornada
        if all(sd is None for sd in serv_docente) and not cola_principal and not cola_reintentos:
            break

    t_total = reloj
    # Acumular espera hasta T_total para los docentes que seguían en alguna fila al cierre
    for d in docentes_ordenados:
        if en_cola[d.id]:
            q_acum[d.id] += t_total - t_entrada_cola[d.id]
            en_cola[d.id] = False

    # ========================================================================
    # 3 CHEQUEOS AUTOMÁTICOS DE CONSISTENCIA (Sección 5.1)
    # ========================================================================
    lq_integral = area_cola / t_total if t_total > 0 else 0.0
    lq_suma_q = sum(q_acum.values()) / t_total if t_total > 0 else 0.0

    # Assert 1: Igualdad temporal exacta de la Ley de Little finita
    assert abs(lq_integral - lq_suma_q) < 1e-9, (
        f"Fallo Ley de Little temporal: integral={lq_integral:.12f} vs suma_Q={lq_suma_q:.12f}"
    )

    # Assert 2: Conservación estricta de vacantes y compatibilidad de nivel/especialidad
    assert all(v >= 0 for v in estado.vacantes_cargo.values()), "Vacantes negativas detectadas."
    assert len(adjudicaciones) <= len(contexto.cargos_lista), "Exceso de cargos adjudicados."
    for doc_id, cargo_adj in adjudicaciones.items():
        d_obj = contexto.docentes[doc_id]
        assert (d_obj.nivel, d_obj.especialidad) == (cargo_adj.nivel, cargo_adj.especialidad), (
            f"Incompatibilidad detectada para {doc_id} en {cargo_adj.id_cargo}"
        )

    # Assert 3: Respeto estricto del orden decreciente de puntaje P_i en la cola principal
    for idx_p in range(len(puntajes_inicio_principal) - 1):
        assert puntajes_inicio_principal[idx_p] > puntajes_inicio_principal[idx_p + 1], (
            "Violación del orden de mérito en cola principal."
        )

    # ========================================================================
    # Cálculo de métricas de desempeño de la réplica (Sección 3.6)
    # ========================================================================
    wq_atendidos = (
        sum(q_acum[did] for did in atendidos_unicos) / len(atendidos_unicos)
        if atendidos_unicos
        else 0.0
    )
    wq_primer_turno_val = (
        sum(q_primer_turno.values()) / len(q_primer_turno)
        if q_primer_turno
        else 0.0
    )
    w_convocados = sum(q_acum.values()) / len(docentes_ordenados)

    n_llamados_princ = len(llamados_principal)
    pct_reintentos = (
        100.0 * len(derivados_reintento) / n_llamados_princ
        if usa_ventana_y_reintentos and n_llamados_princ > 0
        else 0.0
    )

    total_vacantes_ofrecidas = sum(cg.vacantes for cg in contexto.cargos_lista)
    pct_cubiertas = 100.0 * len(adjudicaciones) / total_vacantes_ofrecidas
    total_llamados = llamados_conteo["total"]
    pct_sin_oferta = (
        100.0 * llamados_conteo["sin_oferta"] / total_llamados
        if total_llamados > 0
        else 0.0
    )

    # Satisfacción media sobre los docentes designados (escala 0 a 1, Sección 3.6.7)
    suma_sat = 0.0
    for doc_id, cargo_adj in adjudicaciones.items():
        d_obj = contexto.docentes[doc_id]
        if cargo_adj.id_escuela in d_obj.ranking_real_10:
            puesto = d_obj.ranking_real_10.index(cargo_adj.id_escuela) + 1  # 1..10
            sat = round(1.10 - 0.10 * puesto, 2)
        else:
            sat = 0.05
        suma_sat += sat
    satisfaccion_media = suma_sat / len(adjudicaciones) if adjudicaciones else 0.0

    mae_aviso = sum(errores_aviso) / len(errores_aviso) if errores_aviso else 0.0

    # Casos afectados en su mérito por reintento (Sección 3.6.9)
    afectados_merito = 0
    if usa_ventana_y_reintentos:
        for doc_id in derivados_reintento:
            if doc_id in adjudicaciones:
                continue
            d_obj = contexto.docentes[doc_id]
            # Verificar si se agotaron las vacantes compatibles antes de poder adjudicar en reintento
            sin_vacante_al_reintentar = (
                (doc_id in sin_oferta_en_reintento)
                or (not estado.tiene_oferta_perfil(d_obj.nivel, d_obj.especialidad))
                or (estado.total_vacantes_libres == 0)
            )
            ganadores_perfil = puntajes_ganadores_por_perfil.get(
                (d_obj.nivel, d_obj.especialidad), []
            )
            desplazado_por_menor_puntaje = any(p_gan < d_obj.puntaje for p_gan in ganadores_perfil)
            if sin_vacante_al_reintentar and desplazado_por_menor_puntaje:
                afectados_merito += 1

    # Expresado sobre docentes llamados en cola principal (refleja reducción de casos E2 -> E3)
    # y también sobre el subconjunto enviado a reintento
    pct_afect_llamados = (
        100.0 * afectados_merito / n_llamados_princ
        if usa_ventana_y_reintentos and n_llamados_princ > 0
        else 0.0
    )
    pct_afect_sobre_reint = (
        100.0 * afectados_merito / len(derivados_reintento)
        if usa_ventana_y_reintentos and derivados_reintento
        else 0.0
    )

    return ResultadoReplicaAsamblea(
        escenario=escenario,
        replica=semilla_replica,
        wq_atendidos=wq_atendidos,
        wq_primer_turno=wq_primer_turno_val,
        w_convocados=w_convocados,
        lq=lq_integral,
        t_total_min=t_total,
        t_total_horas=t_total / 60.0,
        pct_reintentos=pct_reintentos,
        pct_vacantes_cubiertas=pct_cubiertas,
        pct_sin_oferta=pct_sin_oferta,
        satisfaccion_media=satisfaccion_media,
        mae_aviso=mae_aviso,
        pct_afectacion_merito_llamados=pct_afect_llamados,
        pct_afectacion_merito_sobre_reintentos=pct_afect_sobre_reint,
        cant_llamados_principal=n_llamados_princ,
        cant_atendidos_unicos=len(atendidos_unicos),
        cant_derivados_reintento=len(derivados_reintento),
        cant_afectados_merito=afectados_merito,
        cant_cargos_cubiertos=len(adjudicaciones),
        cant_casos_A=casos_conteo["A"],
        cant_casos_B=casos_conteo["B"],
        cant_casos_C=casos_conteo["C"],
        registros_pronostico=registros_pronostico,
    )
