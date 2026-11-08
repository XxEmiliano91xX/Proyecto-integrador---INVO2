"""
Generador reproducible de los conjuntos de datos de Salta Capital (semilla = 2026):
- data/escuelas.csv (40 escuelas estatales reales del Departamento Capital, con niveles habilitados)
- data/cargos.csv   (100 cargos vacantes respetando nivel edilicio, especialidad y turno)
- data/docentes.csv (300 docentes con puntajes, domicilios, filtros y preferencias compatibles)
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from src.utils import GeneradorAleatorio, haversine_km

SEMILLA_DATOS: int = 2026

# 40 establecimientos educativos estatales reales del Departamento Capital (Salta),
# verificados contra el padrón Edusalta / CUE-Anexo oficiales:
# - 24 establecimientos de Nivel Inicial y Primario (20 urbanos + 4 periurbanos/rurales)
# - 16 establecimientos de Nivel Secundario (14 urbanos + 2 periurbanos/rurales)
# Formato: (id_escuela, cue_anexo, nombre, latitud, longitud, zona, tipo, prestigio_corredor, niveles)
ESCUELAS_SALTA_CAPITAL: list[tuple[str, str, str, float, float, str, str, float, str]] = [
    # --- INICIAL / PRIMARIO CENTRO (4 urbanas) ---
    ("ESC01", "660001200", "Escuela N.° 4001 Juan Bautista Alberdi", -24.7890, -65.4186, "centro", "urbana", 1.00, "inicial;primario"),
    ("ESC02", "660093100", "Escuela N.° 4002 Mariano Cabezón", -24.7931, -65.4052, "centro", "urbana", 0.96, "inicial;primario"),
    ("ESC03", "660050600", "Escuela N.° 4017 Pte. Domingo Faustino Sarmiento", -24.7911, -65.4079, "centro", "urbana", 0.98, "inicial;primario"),
    ("ESC04", "660031400", "Escuela N.° 4022 Dr. Benjamín Zorrilla", -24.7888, -65.4112, "centro", "urbana", 0.94, "inicial;primario"),
    # --- INICIAL / PRIMARIO NORTE (4 urbanas) ---
    ("ESC05", "660031700", "Escuela N.° 4018 Dr. José Vicente Solá", -24.7690, -65.4072, "norte", "urbana", 0.86, "inicial;primario"),
    ("ESC06", "660041400", "Escuela N.° 4029 Dr. Nicolás Avellaneda", -24.7285, -65.4090, "norte", "urbana", 0.84, "inicial;primario"),
    ("ESC07", "660059600", "Escuela N.° 4031 Pedro Bonifacio Palacios", -24.7324, -65.4018, "norte", "urbana", 0.78, "inicial;primario"),
    ("ESC08", "660052900", "Escuela N.° 4043 Mons. Carlos Mariano Pérez", -24.7352, -65.4035, "norte", "urbana", 0.79, "inicial;primario"),
    # --- INICIAL / PRIMARIO SUR (4 urbanas) ---
    ("ESC09", "660060400", "Escuela N.° 4030 Dr. Mariano Moreno", -24.8435, -65.4395, "sur", "urbana", 0.85, "inicial;primario"),
    ("ESC10", "660035600", "Escuela N.° 4035 Prof. Alejandro Gauffin", -24.8355, -65.4255, "sur", "urbana", 0.83, "inicial;primario"),
    ("ESC11", "660051000", "Escuela N.° 4036 Dr. Augusto Raúl Cortazar", -24.8330, -65.4290, "sur", "urbana", 0.87, "inicial;primario"),
    ("ESC12", "660108200", "Escuela N.° 4700 Legado Gral. Belgrano", -24.8505, -65.4320, "sur", "urbana", 0.76, "inicial;primario"),
    # --- INICIAL / PRIMARIO ESTE (4 urbanas) ---
    ("ESC13", "660045500", "Escuela N.° 4003 Dr. Joaquín Castellanos", -24.8035, -65.3945, "este", "urbana", 0.85, "inicial;primario"),
    ("ESC14", "660066600", "Escuela N.° 4645 25 de Mayo de 1810", -24.7995, -65.3995, "este", "urbana", 0.84, "inicial;primario"),
    ("ESC15", "660134800", "Escuela N.° 4774 Gral. Juan José Valle", -24.8280, -65.3770, "este", "urbana", 0.64, "inicial;primario"),
    ("ESC16", "660144400", "Escuela N.° 4811 2 de Mayo Crucero ARA Gral. Belgrano", -24.8365, -65.3812, "este", "urbana", 0.62, "inicial;primario"),
    # --- INICIAL / PRIMARIO OESTE (4 urbanas) ---
    ("ESC17", "660047700", "Escuela N.° 4005 Juan Carlos Dávalos", -24.7975, -65.4395, "oeste", "urbana", 0.81, "inicial;primario"),
    ("ESC18", "660061100", "Escuela N.° 4014 San José", -24.8045, -65.4425, "oeste", "urbana", 0.78, "inicial;primario"),
    ("ESC19", "660002900", "Escuela N.° 4015 Remedios de Escalada de San Martín", -24.7830, -65.4245, "oeste", "urbana", 0.84, "inicial;primario"),
    ("ESC20", "660052100", "Escuela N.° 4034 Santa Lucía", -24.8075, -65.4445, "oeste", "urbana", 0.74, "inicial;primario"),
    # --- INICIAL / PRIMARIO PERIURBANA / RURAL (4 rurales del Depto. Capital) ---
    ("ESC21", "660005600", "Escuela N.° 4053 Gral. Rudecindo Alvarado (San Luis)", -24.8550, -65.5050, "periurbana", "rural", 0.55, "inicial;primario"),
    ("ESC22", "660046800", "Escuela N.° 4055 José Manuel Estrada (Villa San Lorenzo)", -24.7325, -65.4860, "periurbana", "rural", 0.58, "inicial;primario"),
    ("ESC23", "660057100", "Escuela N.° 4304 Nuestra Señora del Carmen (La Ciénaga)", -24.8280, -65.4985, "periurbana", "rural", 0.50, "inicial;primario"),
    ("ESC24", "660046700", "Escuela N.° 4317 Tte. Cnel. Calixto Gauna (Finca Las Costas)", -24.7640, -65.5120, "periurbana", "rural", 0.48, "inicial;primario"),
    # --- SECUNDARIO CENTRO (3 urbanas) ---
    ("ESC25", "660067200", "Escuela de Comercio N.° 5076 Dr. Arturo Illia", -24.7848, -65.4110, "centro", "urbana", 0.93, "secundario"),
    ("ESC26", "660078700", "Colegio Secundario N.° 5080 Dr. Manuel Antonio Castro", -24.7885, -65.4050, "centro", "urbana", 0.95, "secundario"),
    ("ESC27", "660003900", "Escuela de Comercio N.° 5083 Dr. Victorino de la Plaza", -24.7835, -65.4085, "centro", "urbana", 0.91, "secundario"),
    # --- SECUNDARIO NORTE (3 urbanas) ---
    ("ESC28", "660031800", "Colegio Secundario N.° 5028 Reyes Católicos (Tres Cerritos)", -24.7685, -65.3925, "norte", "urbana", 0.86, "secundario"),
    ("ESC29", "660052600", "Colegio Secundario N.° 5035 Batalla de Salta (Castañares)", -24.7320, -65.4025, "norte", "urbana", 0.80, "secundario"),
    ("ESC30", "660027600", "Colegio Secundario N.° 5048 Juana Manuela Gorriti (P. Belgrano)", -24.7265, -65.4110, "norte", "urbana", 0.77, "secundario"),
    # --- SECUNDARIO SUR (3 urbanas) ---
    ("ESC31", "660035500", "Colegio Secundario N.° 5027 Gral. José de San Martín", -24.8155, -65.4240, "sur", "urbana", 0.83, "secundario"),
    ("ESC32", "660060900", "Colegio Secundario N.° 5033 Dr. Ernesto Miguel Aráoz (Intersindical)", -24.8428, -65.4350, "sur", "urbana", 0.76, "secundario"),
    ("ESC33", "660045400", "Colegio Secundario N.° 5071 Juan Carlos Saravia (Limache)", -24.8510, -65.4305, "sur", "urbana", 0.75, "secundario"),
    # --- SECUNDARIO ESTE (3 urbanas) ---
    ("ESC34", "660059800", "Colegio Secundario N.° 5024 Sargento Cabral (Villa Mitre)", -24.7965, -65.3885, "este", "urbana", 0.81, "secundario"),
    ("ESC35", "660003300", "Colegio Secundario N.° 5038 América Latina (Villa Lavalle)", -24.8215, -65.4040, "este", "urbana", 0.73, "secundario"),
    ("ESC36", "660051500", "Colegio Secundario N.° 5070 María Teresa Cadena de Hessling (V. Juanita)", -24.8050, -65.3845, "este", "urbana", 0.74, "secundario"),
    # --- SECUNDARIO OESTE (2 urbanas) ---
    ("ESC37", "660027000", "Colegio Secundario N.° 5026 20 de Febrero", -24.7845, -65.4235, "oeste", "urbana", 0.84, "secundario"),
    ("ESC38", "660052000", "Colegio Secundario N.° 5056 San José de Calasanz (B.° San José)", -24.8040, -65.4420, "oeste", "urbana", 0.75, "secundario"),
    # --- SECUNDARIO PERIURBANA / RURAL (2 rurales del Depto. Capital) ---
    ("ESC39", "660130600", "Colegio Secundario N.° 5164 (Atocha)", -24.8154, -65.4779, "periurbana", "rural", 0.50, "secundario"),
    ("ESC40", "660144800", "Colegio Secundario N.° 5176 (Villa Esmeralda - San Luis)", -24.8555, -65.5045, "periurbana", "rural", 0.53, "secundario"),
]

# Distribución de los 100 cargos y 300 docentes por (nivel, especialidad)
PERFILES_ESPECIALIDAD: list[tuple[str, str, int, int]] = [
    ("primario", "maestro_grado", 42, 126),
    ("inicial", "maestro_jardín", 20, 60),
    ("primario", "educación_física", 10, 30),
    ("secundario", "matemática", 10, 30),
    ("secundario", "lengua", 9, 27),
    ("secundario", "inglés", 9, 27),
]

# Núcleos residenciales de Salta Capital (lat, lon, dispersión, peso poblacional, zona)
NUCLEOS_RESIDENCIALES: list[tuple[float, float, float, float, str]] = [
    (-24.7890, -65.4110, 0.010, 0.18, "centro"),
    (-24.7420, -65.4060, 0.014, 0.22, "norte"),
    (-24.8390, -65.4350, 0.015, 0.24, "sur"),
    (-24.8120, -65.3810, 0.014, 0.18, "este"),
    (-24.7880, -65.4480, 0.014, 0.18, "oeste"),
]


def generar_archivos_datos(directorio_salida: str | Path = "data", semilla: int = SEMILLA_DATOS) -> None:
    """Genera de forma determinística escuelas.csv, cargos.csv y docentes.csv."""
    out_dir = Path(directorio_salida)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = GeneradorAleatorio(semilla)

    esc_niv_map = {esc[0]: frozenset(esc[8].split(";")) for esc in ESCUELAS_SALTA_CAPITAL}

    # 1. Guardar data/escuelas.csv
    ruta_escuelas = out_dir / "escuelas.csv"
    with ruta_escuelas.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_escuela", "cue_anexo", "nombre", "latitud", "longitud", "zona", "tipo", "niveles"])
        for esc in ESCUELAS_SALTA_CAPITAL:
            writer.writerow([esc[0], esc[1], esc[2], f"{esc[3]:.4f}", f"{esc[4]:.4f}", esc[5], esc[6], esc[8]])

    # Turnos base ofrecidos históricamente por cada escuela (para similitud de contenido T_ij)
    turnos_base_escuela: dict[str, list[str]] = {}
    for esc in ESCUELAS_SALTA_CAPITAL:
        id_esc, _, _, _, _, _, tipo, _, niveles_str = esc
        nivs = niveles_str.split(";")
        if tipo == "rural":
            turnos_base_escuela[id_esc] = ["mañana", "tarde"]
        elif "secundario" in nivs:
            turnos_base_escuela[id_esc] = ["mañana", "tarde", "noche"]
        else:
            turnos_base_escuela[id_esc] = ["mañana", "tarde"]

    # 2. Generar data/cargos.csv (100 cargos respetando el nivel edilicio y priorizando vacantes periféricas)
    peso_vacante_zona = {
        "centro": 0.45,     # Pocas vacantes libres en el centro (se agotan rápido)
        "norte": 1.25,
        "sur": 1.35,
        "este": 1.55,
        "oeste": 1.30,
        "periurbana": 1.40,
    }

    prim_escs = [esc for esc in ESCUELAS_SALTA_CAPITAL if "primario" in esc_niv_map[esc[0]]]
    sec_escs = [esc for esc in ESCUELAS_SALTA_CAPITAL if "secundario" in esc_niv_map[esc[0]]]

    def sample_sin_rep_ciclico(
        pool_esc: list[tuple[str, str, str, float, float, str, str, float, str]],
        k: int,
    ) -> list[tuple[str, str, str, float, float, str, str, float, str]]:
        elegidas: list[tuple[str, str, str, float, float, str, str, float, str]] = []
        while len(elegidas) < k:
            falta = min(len(pool_esc), k - len(elegidas))
            pesos_z = [peso_vacante_zona[e[5]] for e in pool_esc]
            elegidas.extend(rng.sample_ponderado_sin_reposicion(pool_esc, pesos_z, falta))
        return elegidas

    # Nivel Inicial y Primario: cada una de las 24 escuelas cubre al menos 1 cargo de Maestro de Grado
    escs_mg = list(prim_escs) + sample_sin_rep_ciclico(prim_escs, 42 - len(prim_escs))
    escs_mj = sample_sin_rep_ciclico(prim_escs, 20)
    escs_ef = sample_sin_rep_ciclico(prim_escs, 10)

    # Nivel Secundario: distribuir Matemática (10), Lengua (9) e Inglés (9) sin repetir escuela
    # dentro de cada especialidad y cubriendo los 16 colegios secundarios al menos una vez.
    escs_mat = rng.sample_ponderado_sin_reposicion(
        sec_escs, [peso_vacante_zona[e[5]] for e in sec_escs], 10
    )
    sin_cubrir_1 = [e for e in sec_escs if e not in escs_mat]
    cubiertas_1 = [e for e in sec_escs if e in escs_mat]
    escs_len = sin_cubrir_1 + rng.sample_ponderado_sin_reposicion(
        cubiertas_1, [peso_vacante_zona[e[5]] for e in cubiertas_1], 9 - len(sin_cubrir_1)
    )
    sin_cubrir_2 = [e for e in sec_escs if e not in escs_mat and e not in escs_len]
    resto_ing = [e for e in sec_escs if e not in sin_cubrir_2]
    escs_ing = sin_cubrir_2 + rng.sample_ponderado_sin_reposicion(
        resto_ing, [peso_vacante_zona[e[5]] for e in resto_ing], 9 - len(sin_cubrir_2)
    )

    asignaciones: list[tuple[tuple[str, str, str, float, float, str, str, float, str], str, str]] = (
        [(e, "primario", "maestro_grado") for e in escs_mg]
        + [(e, "inicial", "maestro_jardín") for e in escs_mj]
        + [(e, "primario", "educación_física") for e in escs_ef]
        + [(e, "secundario", "matemática") for e in escs_mat]
        + [(e, "secundario", "lengua") for e in escs_len]
        + [(e, "secundario", "inglés") for e in escs_ing]
    )

    cargos_generados: list[dict[str, str | int]] = []
    escuelas_con_oferta: dict[tuple[str, str], set[str]] = {}

    for contador_cargo, (esc, nivel, especialidad) in enumerate(asignaciones, start=1):
        id_esc = esc[0]
        u_turno = rng.random()
        if nivel == "secundario":
            if u_turno < 0.42:
                turno = "mañana"
            elif u_turno < 0.80:
                turno = "tarde"
            else:
                turno = "noche"
        else:
            turno = "mañana" if u_turno < 0.52 else "tarde"

        cargos_generados.append(
            {
                "id_cargo": f"C{contador_cargo:03d}",
                "id_escuela": id_esc,
                "nivel": nivel,
                "especialidad": especialidad,
                "turno": turno,
                "vacantes": 1,
            }
        )
        escuelas_con_oferta.setdefault((nivel, especialidad), set()).add(id_esc)

    ruta_cargos = out_dir / "cargos.csv"
    with ruta_cargos.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id_cargo", "id_escuela", "nivel", "especialidad", "turno", "vacantes"]
        )
        writer.writeheader()
        writer.writerows(cargos_generados)

    # 3. Generar data/docentes.csv (300 docentes con puntajes únicos en [20.00, 100.00])
    puntajes_usados: set[int] = set()
    puntajes_cent: list[int] = []
    while len(puntajes_cent) < 300:
        g1 = rng.exponential(1.0) + rng.exponential(1.0)
        g2 = rng.exponential(1.0) + rng.exponential(1.0) + rng.exponential(1.0) + 0.6 * rng.exponential(1.0)
        beta_val = g1 / (g1 + g2)
        val_cent = int(round((20.0 + 80.0 * beta_val) * 100))
        val_cent = max(2000, min(10000, val_cent))
        if val_cent not in puntajes_usados:
            puntajes_usados.add(val_cent)
            puntajes_cent.append(val_cent)

    puntajes_cent.sort(reverse=True)

    # Armar vector de 300 especialidades y barajarlo determinísticamente
    bolsa_perfiles: list[tuple[str, str]] = []
    for nivel, especialidad, _, cant_doc in PERFILES_ESPECIALIDAD:
        bolsa_perfiles.extend([(nivel, especialidad)] * cant_doc)
    for idx in range(len(bolsa_perfiles) - 1, 0, -1):
        j = rng.randint(0, idx)
        bolsa_perfiles[idx], bolsa_perfiles[j] = bolsa_perfiles[j], bolsa_perfiles[idx]

    docentes_generados: list[dict[str, str | int]] = []
    pesos_nucleos = [n[3] for n in NUCLEOS_RESIDENCIALES]

    for idx in range(300):
        id_doc = f"D{idx + 1:03d}"
        puntaje = puntajes_cent[idx] / 100.0
        nivel, especialidad = bolsa_perfiles[idx]
        m_i = rng.uniform(1.0, 3.0)

        # Sortear domicilio en Salta Capital
        nucleo = rng.sample_ponderado_sin_reposicion(NUCLEOS_RESIDENCIALES, pesos_nucleos, 1)[0]
        lat_dom = nucleo[0] + rng.normal(0.0, nucleo[2])
        lon_dom = nucleo[1] + rng.normal(0.0, nucleo[2])
        zona_dom = nucleo[4]

        acepta_rural = 1 if rng.random() < 0.30 else 0
        if acepta_rural == 1:
            radio_max = rng.uniform(15.0, 25.0)
        else:
            radio_max = rng.uniform(8.0, 15.0)

        # Turnos disponibles (1 o 2 turnos)
        u_t = rng.random()
        if nivel == "secundario":
            if u_t < 0.55:
                turnos_doc = ["mañana", "tarde"]
            elif u_t < 0.72:
                turnos_doc = ["mañana"]
            elif u_t < 0.86:
                turnos_doc = ["tarde"]
            else:
                turnos_doc = ["tarde", "noche"]
        else:
            if u_t < 0.65:
                turnos_doc = ["mañana", "tarde"]
            elif u_t < 0.84:
                turnos_doc = ["mañana"]
            else:
                turnos_doc = ["tarde"]

        # Solo escuelas del nivel correspondiente (y urbanas si acepta_rural == 0)
        escuelas_nivel = [
            esc for esc in ESCUELAS_SALTA_CAPITAL if nivel in esc_niv_map[esc[0]]
        ]
        escuelas_tipo = [
            esc for esc in escuelas_nivel if acepta_rural == 1 or esc[6] == "urbana"
        ]
        distancias_esc = {
            esc[0]: haversine_km(lat_dom, lon_dom, esc[3], esc[4])
            for esc in escuelas_tipo
        }
        dentro_radio = [esc for esc in escuelas_tipo if distancias_esc[esc[0]] <= radio_max]
        min_req = min(12, len(escuelas_tipo))
        if len(dentro_radio) < min_req:
            dists_ordenadas = sorted(distancias_esc.values())
            limite_sup = 25.0 if acepta_rural == 1 else 15.0
            radio_max = min(limite_sup, max(radio_max, dists_ordenadas[min_req - 1] + 0.5))
            dentro_radio = [esc for esc in escuelas_tipo if distancias_esc[esc[0]] <= radio_max]

        pool_pref = dentro_radio if len(dentro_radio) >= 10 else escuelas_tipo

        # Atracción realista hacia corredores céntricos y zona afín de transporte
        zonas_posibles = ["centro", "norte", "sur", "este", "oeste"]
        u_za = rng.random()
        if u_za < 0.45:
            zona_afin = "centro"
        elif u_za < 0.80:
            zona_afin = zona_dom
        else:
            zona_afin = rng.choice(zonas_posibles)

        utilidades: dict[str, float] = {}
        for esc in pool_pref:
            id_esc, _, _, _, _, zona_esc, _, prestigio, _ = esc
            dist = distancias_esc[id_esc]
            score_cercania = max(0.05, 1.0 - dist / max(radio_max, 12.0))
            afinidad_zona = 1.0 if zona_esc == zona_afin else (0.55 if zona_esc == zona_dom else 0.10)
            coincide_turno = 1.0 if (set(turnos_doc) & set(turnos_base_escuela[id_esc])) else 0.25
            ruido_personal = rng.normal(0.0, 0.42)

            utilidad = (
                0.95 * score_cercania
                + 3.20 * prestigio
                + 0.85 * afinidad_zona
                + 0.45 * coincide_turno
                + ruido_personal
            )
            utilidades[id_esc] = math.exp(2.50 * utilidad)

        # Lista L_i visible (hasta M = 5 escuelas) estrictamente entre las escuelas que
        # efectivamente ofrecen vacantes compatibles con (nivel, especialidad) en el acto
        escuelas_ofertadas = escuelas_con_oferta[(nivel, especialidad)]
        u_m = rng.random()
        if len(escuelas_ofertadas) <= 12:
            m_vis = 3
        else:
            m_vis = 3 if u_m < 0.50 else (4 if u_m < 0.85 else 5)

        pool_visibles = [eid for eid in utilidades if eid in escuelas_ofertadas]
        if len(pool_visibles) < m_vis:
            faltantes = sorted(
                (eid for eid in escuelas_ofertadas if eid not in utilidades),
                key=lambda eid: distancias_esc.get(eid, 99.0),
            )
            pool_visibles.extend(faltantes)
            for eid in pool_visibles:
                utilidades.setdefault(eid, 0.01)

        visibles = rng.sample_ponderado_sin_reposicion(
            pool_visibles,
            [utilidades[eid] for eid in pool_visibles],
            min(m_vis, len(pool_visibles)),
        )

        # Preferencias ocultas (5 opciones adicionales compatibles con el nivel y tipo)
        pool_ocultas = [eid for eid in utilidades if eid not in visibles]
        if len(pool_ocultas) < 5:
            extras_niv = [esc[0] for esc in escuelas_nivel if esc[0] not in visibles and esc[0] not in pool_ocultas]
            pool_ocultas.extend(extras_niv)
            for eid in pool_ocultas:
                utilidades.setdefault(eid, 0.01)

        ocultas = rng.sample_ponderado_sin_reposicion(
            pool_ocultas,
            [utilidades[eid] for eid in pool_ocultas],
            5,
        )

        docentes_generados.append(
            {
                "id": id_doc,
                "puntaje": f"{puntaje:.2f}",
                "tiempo_decision_medio": f"{m_i:.2f}",
                "nivel": nivel,
                "especialidad": especialidad,
                "latitud": f"{lat_dom:.4f}",
                "longitud": f"{lon_dom:.4f}",
                "preferencias": ";".join(visibles),
                "radio_max_km": f"{radio_max:.2f}",
                "turnos": ";".join(turnos_doc),
                "acepta_rural": acepta_rural,
                "preferencias_ocultas": ";".join(ocultas),
            }
        )

    ruta_docentes = out_dir / "docentes.csv"
    with ruta_docentes.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "puntaje",
                "tiempo_decision_medio",
                "nivel",
                "especialidad",
                "latitud",
                "longitud",
                "preferencias",
                "radio_max_km",
                "turnos",
                "acepta_rural",
                "preferencias_ocultas",
            ],
        )
        writer.writeheader()
        writer.writerows(docentes_generados)


if __name__ == "__main__":
    generar_archivos_datos()
    print("Datos generados exitosamente en data/escuelas.csv, data/cargos.csv y data/docentes.csv.")
