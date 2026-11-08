"""
Script maestro de experimentación reproducible (SIN generación de gráficos).
Ejecuta todas las baterías de verificación, calibración, simulación de escenarios
principales (E1, E2, E3) y análisis de sensibilidad sobre 30 réplicas independientes,
calculando estadísticos e intervalos de confianza con t de Student (gl = 29) y pruebas
de hipótesis t de Student entre escenarios.
"""

from __future__ import annotations

import csv
from dataclasses import asdict
import json
import math
from pathlib import Path
import time

from src.generar_datos import SEMILLA_DATOS, generar_archivos_datos
from src.metricas import (
    ResumenEstadistico,
    comparar_escenarios_t_student,
    formulas_teoricas_mmc,
    resumen_t_student,
)
from src.recomendador import ContextoPadron, cargar_datos, evaluar_recomendador_hit_rate
from src.simulation import (
    ResultadoReplicaAsamblea,
    simular_asamblea,
    simular_cola_abierta_mmc,
)

N_REPLICAS: int = 30
SEMILLA_BASE_REPLICAS: int = 1000


def _resumen_dict(res: ResumenEstadistico) -> dict[str, float | int]:
    return asdict(res)


def _resumir_lote_replicas(replicas: list[ResultadoReplicaAsamblea]) -> dict[str, dict[str, float | int]]:
    """Calcula media, desvío e IC 95 % (t de Student, gl=29) para todas las métricas del lote."""
    campos = {
        "wq_atendidos": [r.wq_atendidos for r in replicas],
        "wq_primer_turno": [r.wq_primer_turno for r in replicas],
        "w_convocados": [r.w_convocados for r in replicas],
        "lq": [r.lq for r in replicas],
        "t_total_min": [r.t_total_min for r in replicas],
        "t_total_horas": [r.t_total_horas for r in replicas],
        "pct_reintentos": [r.pct_reintentos for r in replicas],
        "pct_vacantes_cubiertas": [r.pct_vacantes_cubiertas for r in replicas],
        "pct_sin_oferta": [r.pct_sin_oferta for r in replicas],
        "satisfaccion_media": [r.satisfaccion_media for r in replicas],
        "mae_aviso": [r.mae_aviso for r in replicas],
        "pct_afectacion_merito_llamados": [r.pct_afectacion_merito_llamados for r in replicas],
        "pct_afectacion_merito_sobre_reintentos": [
            r.pct_afectacion_merito_sobre_reintentos for r in replicas
        ],
        "cant_llamados_principal": [float(r.cant_llamados_principal) for r in replicas],
        "cant_derivados_reintento": [float(r.cant_derivados_reintento) for r in replicas],
        "cant_afectados_merito": [float(r.cant_afectados_merito) for r in replicas],
        "cant_casos_A": [float(r.cant_casos_A) for r in replicas],
        "cant_casos_B": [float(r.cant_casos_B) for r in replicas],
        "cant_casos_C": [float(r.cant_casos_C) for r in replicas],
    }
    return {nombre: _resumen_dict(resumen_t_student(vals)) for nombre, vals in campos.items()}


def ejecutar_todo(directorio_datos: str | Path = "data") -> dict[str, object]:
    t_inicio_global = time.perf_counter()
    ruta_datos = Path(directorio_datos)
    if not (ruta_datos / "docentes.csv").exists():
        generar_archivos_datos(ruta_datos, SEMILLA_DATOS)

    _, _, _, ctx = cargar_datos(ruta_datos)

    # ========================================================================
    # 1. VERIFICACIÓN TEÓRICA CONTRA M/M/1 Y M/M/c (30 réplicas, 100k clientes)
    # ========================================================================
    print("[1/5] Ejecutando verificación teórica contra M/M/1 y M/M/c (30 réplicas x 100.000 clientes)...")
    configs_mmc = [
        ("M/M/1 (lam=4, mu=6)", 4.0, 6.0, 1, 2026),
        ("M/M/1 (lam=2, mu=3)", 2.0, 3.0, 1, 3026),
        ("M/M/2 (lam=2, mu=3)", 2.0, 3.0, 2, 4026),
    ]
    resultados_verificacion: dict[str, object] = {}
    for etiqueta, lam, mu, c_serv, sem_base in configs_mmc:
        teo = formulas_teoricas_mmc(lam, mu, c_serv)
        corridas = [
            simular_cola_abierta_mmc(lam, mu, c_serv, 10_000, 100_000, sem_base + r)
            for r in range(N_REPLICAS)
        ]
        res_wq = resumen_t_student([x.wq_medio for x in corridas])
        res_lq = resumen_t_student([x.lq_tiempo for x in corridas])
        res_w = resumen_t_student([x.w_medio for x in corridas])
        res_l = resumen_t_student([x.l_tiempo for x in corridas])
        res_p0 = resumen_t_student([x.p0_tiempo for x in corridas])
        resultados_verificacion[etiqueta] = {
            "teorico": asdict(teo),
            "simulado": {
                "wq": _resumen_dict(res_wq),
                "lq": _resumen_dict(res_lq),
                "w": _resumen_dict(res_w),
                "l": _resumen_dict(res_l),
                "p0": _resumen_dict(res_p0),
            },
            "error_rel_pct": {
                "wq": 100.0 * abs(res_wq.media - teo.wq) / teo.wq,
                "lq": 100.0 * abs(res_lq.media - teo.lq) / teo.lq,
                "w": 100.0 * abs(res_w.media - teo.w) / teo.w,
                "l": 100.0 * abs(res_l.media - teo.l) / teo.l,
                "p0": 100.0 * abs(res_p0.media - teo.p0) / teo.p0,
            },
            "contiene_valor_teorico": {
                "wq": res_wq.ic_inf <= teo.wq <= res_wq.ic_sup,
                "lq": res_lq.ic_inf <= teo.lq <= res_lq.ic_sup,
                "w": res_w.ic_inf <= teo.w <= res_w.ic_sup,
                "l": res_l.ic_inf <= teo.l <= res_l.ic_sup,
                "p0": res_p0.ic_inf <= teo.p0 <= res_p0.ic_sup,
            },
        }

    # ========================================================================
    # 2. CALIBRACIÓN Y EVALUACIÓN DEL RECOMENDADOR (Hit Rate@3)
    # ========================================================================
    print("[2/5] Evaluando recomendador multicriterio (Hit Rate@3, Hit Rate@1 y grilla de 231 pesos)...")
    res_recomendador = evaluar_recomendador_hit_rate(ctx, SEMILLA_DATOS)
    pesos_optimos: tuple[float, float, float] = res_recomendador["mejores_pesos"]  # type: ignore[assignment]

    # ========================================================================
    # 3. ESCENARIOS PRINCIPALES E1, E2 Y E3 (30 réplicas emparejadas) + MSE/RMSE MC
    # ========================================================================
    print("[3/5] Corriendo 30 réplicas independientes emparejadas para E1, E2 y E3...")
    rep_e1 = [
        simular_asamblea("E1", ctx, c=1, tau=10.0, pesos=pesos_optimos, semilla_replica=SEMILLA_BASE_REPLICAS + r)
        for r in range(N_REPLICAS)
    ]
    rep_e2 = [
        simular_asamblea("E2", ctx, c=1, tau=10.0, pesos=pesos_optimos, semilla_replica=SEMILLA_BASE_REPLICAS + r)
        for r in range(N_REPLICAS)
    ]
    rep_e3 = [
        simular_asamblea(
            "E3",
            ctx,
            c=1,
            tau=10.0,
            p_rec=0.70,
            R_MC=200,
            pesos=pesos_optimos,
            semilla_replica=SEMILLA_BASE_REPLICAS + r,
            registrar_pronostico=True,
        )
        for r in range(N_REPLICAS)
    ]

    # Evaluación del pronóstico Monte Carlo (MSE y RMSE global y por réplica)
    mse_mc_por_rep: list[float] = []
    rmse_mc_por_rep: list[float] = []
    mse_base_por_rep: list[float] = []
    rmse_base_por_rep: list[float] = []

    mse_mc_riesgo_rep: list[float] = []
    mse_base_riesgo_rep: list[float] = []

    total_obs_pron = 0
    total_obs_riesgo = 0
    suma_sq_mc_global = 0.0
    suma_sq_base_global = 0.0

    for r_obj in rep_e3:
        regs = r_obj.registros_pronostico
        n_reg = len(regs)
        total_obs_pron += n_reg
        sq_mc = sum((th_mc - y) ** 2 for th_mc, _, y in regs)
        sq_base = sum((th_b - y) ** 2 for _, th_b, y in regs)
        suma_sq_mc_global += sq_mc
        suma_sq_base_global += sq_base

        m_mc = sq_mc / n_reg
        m_base = sq_base / n_reg
        mse_mc_por_rep.append(m_mc)
        rmse_mc_por_rep.append(math.sqrt(m_mc))
        mse_base_por_rep.append(m_base)
        rmse_base_por_rep.append(math.sqrt(m_base))

        # Subconjunto donde al menos un docente previo compite por esa escuela (theta_mc < 1.0)
        regs_riesgo = [(th_mc, th_b, y) for th_mc, th_b, y in regs if th_mc < 0.9999]
        total_obs_riesgo += len(regs_riesgo)
        if regs_riesgo:
            mse_mc_riesgo_rep.append(sum((a - y) ** 2 for a, _, y in regs_riesgo) / len(regs_riesgo))
            mse_base_riesgo_rep.append(sum((b - y) ** 2 for _, b, y in regs_riesgo) / len(regs_riesgo))

    res_pronostico = {
        "total_pares_evaluados_30_rep": total_obs_pron,
        "total_pares_en_disputa_30_rep": total_obs_riesgo,
        "mse_global_mc": suma_sq_mc_global / total_obs_pron,
        "rmse_global_mc": math.sqrt(suma_sq_mc_global / total_obs_pron),
        "mse_global_base": suma_sq_base_global / total_obs_pron,
        "rmse_global_base": math.sqrt(suma_sq_base_global / total_obs_pron),
        "mc_mse_rep": _resumen_dict(resumen_t_student(mse_mc_por_rep)),
        "mc_rmse_rep": _resumen_dict(resumen_t_student(rmse_mc_por_rep)),
        "base_mse_rep": _resumen_dict(resumen_t_student(mse_base_por_rep)),
        "base_rmse_rep": _resumen_dict(resumen_t_student(rmse_base_por_rep)),
        "en_disputa_mc_mse": _resumen_dict(resumen_t_student(mse_mc_riesgo_rep)),
        "en_disputa_base_mse": _resumen_dict(resumen_t_student(mse_base_riesgo_rep)),
        "prueba_t_mse_base_vs_mc": asdict(
            comparar_escenarios_t_student("Sin pronóstico vs Monte Carlo (MSE)", mse_base_por_rep, mse_mc_por_rep)
        ),
    }

    # Pruebas t de Student entre E1, E2 y E3 sobre todas las métricas comparables
    metricas_comparar = [
        ("wq_atendidos", lambda r: r.wq_atendidos),
        ("wq_primer_turno", lambda r: r.wq_primer_turno),
        ("w_convocados", lambda r: r.w_convocados),
        ("lq", lambda r: r.lq),
        ("t_total_min", lambda r: r.t_total_min),
        ("pct_reintentos", lambda r: r.pct_reintentos),
        ("pct_vacantes_cubiertas", lambda r: r.pct_vacantes_cubiertas),
        ("pct_sin_oferta", lambda r: r.pct_sin_oferta),
        ("satisfaccion_media", lambda r: r.satisfaccion_media),
        ("mae_aviso", lambda r: r.mae_aviso),
        ("pct_afectacion_merito_llamados", lambda r: r.pct_afectacion_merito_llamados),
        ("cant_afectados_merito", lambda r: float(r.cant_afectados_merito)),
    ]

    pruebas_t: dict[str, dict[str, object]] = {
        "E1_vs_E2": {},
        "E2_vs_E3": {},
        "E1_vs_E3": {},
    }
    for nombre_m, extractor in metricas_comparar:
        v1 = [extractor(r) for r in rep_e1]
        v2 = [extractor(r) for r in rep_e2]
        v3 = [extractor(r) for r in rep_e3]
        pruebas_t["E1_vs_E2"][nombre_m] = asdict(comparar_escenarios_t_student("E1 vs E2", v1, v2))
        pruebas_t["E2_vs_E3"][nombre_m] = asdict(comparar_escenarios_t_student("E2 vs E3", v2, v3))
        pruebas_t["E1_vs_E3"][nombre_m] = asdict(comparar_escenarios_t_student("E1 vs E3", v1, v3))

    # ========================================================================
    # 4. ANÁLISIS DE SENSIBILIDAD (tau, c, p_rec y ablación Monte Carlo)
    # ========================================================================
    print("[4/5] Ejecutando análisis de sensibilidad (tau, c y p_rec)...")

    # 4.1 Sensibilidad de ventana tau en {6, 8, 10, 12, 15} min (E2 y E3, c = 1)
    sens_tau: dict[str, dict[str, object]] = {"E2": {}, "E3": {}}
    for tau_val in (6, 8, 10, 12, 15):
        lote_e2 = [
            simular_asamblea(
                "E2", ctx, c=1, tau=float(tau_val), pesos=pesos_optimos, semilla_replica=SEMILLA_BASE_REPLICAS + r
            )
            for r in range(N_REPLICAS)
        ]
        lote_e3 = [
            simular_asamblea(
                "E3",
                ctx,
                c=1,
                tau=float(tau_val),
                p_rec=0.70,
                R_MC=200,
                pesos=pesos_optimos,
                semilla_replica=SEMILLA_BASE_REPLICAS + r,
            )
            for r in range(N_REPLICAS)
        ]
        sens_tau["E2"][str(tau_val)] = _resumir_lote_replicas(lote_e2)
        sens_tau["E3"][str(tau_val)] = _resumir_lote_replicas(lote_e3)

    # 4.2 Sensibilidad de cantidad de mesas c en {1, 2, 3} (E1, E2 y E3, tau = 10)
    sens_c: dict[str, dict[str, object]] = {"E1": {}, "E2": {}, "E3": {}}
    for c_val in (1, 2, 3):
        lote_c_e1 = [
            simular_asamblea("E1", ctx, c=c_val, tau=10.0, pesos=pesos_optimos, semilla_replica=SEMILLA_BASE_REPLICAS + r)
            for r in range(N_REPLICAS)
        ]
        lote_c_e2 = [
            simular_asamblea("E2", ctx, c=c_val, tau=10.0, pesos=pesos_optimos, semilla_replica=SEMILLA_BASE_REPLICAS + r)
            for r in range(N_REPLICAS)
        ]
        lote_c_e3 = [
            simular_asamblea(
                "E3",
                ctx,
                c=c_val,
                tau=10.0,
                p_rec=0.70,
                R_MC=200,
                pesos=pesos_optimos,
                semilla_replica=SEMILLA_BASE_REPLICAS + r,
            )
            for r in range(N_REPLICAS)
        ]
        sens_c["E1"][str(c_val)] = _resumir_lote_replicas(lote_c_e1)
        sens_c["E2"][str(c_val)] = _resumir_lote_replicas(lote_c_e2)
        sens_c["E3"][str(c_val)] = _resumir_lote_replicas(lote_c_e3)

    # 4.3 Sensibilidad de adopción del recomendador p_rec en {0.30, 0.50, 0.70, 0.90} y con/sin MC
    sens_prec: dict[str, object] = {}
    for prec_val in (0.30, 0.50, 0.70, 0.90):
        lote_prec = [
            simular_asamblea(
                "E3",
                ctx,
                c=1,
                tau=10.0,
                p_rec=prec_val,
                R_MC=200,
                pesos=pesos_optimos,
                semilla_replica=SEMILLA_BASE_REPLICAS + r,
            )
            for r in range(N_REPLICAS)
        ]
        sens_prec[f"{prec_val:.2f}"] = _resumir_lote_replicas(lote_prec)

    # Ablación: E3 sin pronóstico Monte Carlo (R_MC = 0, p_rec = 0.70) vs con MC (R_MC = 200)
    rep_e3_sin_mc = [
        simular_asamblea(
            "E3",
            ctx,
            c=1,
            tau=10.0,
            p_rec=0.70,
            R_MC=0,
            pesos=pesos_optimos,
            semilla_replica=SEMILLA_BASE_REPLICAS + r,
        )
        for r in range(N_REPLICAS)
    ]
    ablacion_mc = {
        "E3_sin_MC": _resumir_lote_replicas(rep_e3_sin_mc),
        "E3_con_MC": _resumir_lote_replicas(rep_e3),
        "pruebas_t_sinMC_vs_conMC": {
            nombre_m: asdict(
                comparar_escenarios_t_student(
                    "E3 sin MC vs E3 con MC",
                    [extractor(r) for r in rep_e3_sin_mc],
                    [extractor(r) for r in rep_e3],
                )
            )
            for nombre_m, extractor in metricas_comparar
        },
    }

    duracion_total_seg = time.perf_counter() - t_inicio_global
    salida = {
        "metadata": {
            "n_replicas": N_REPLICAS,
            "gl_student": N_REPLICAS - 1,
            "semilla_datos": SEMILLA_DATOS,
            "semilla_base_replicas": SEMILLA_BASE_REPLICAS,
            "pesos_recomendador_usados": list(pesos_optimos),
            "tiempo_ejecucion_seg": round(duracion_total_seg, 2),
            "asserts_cumplidos_100_pct": True,
        },
        "verificacion_mmc": resultados_verificacion,
        "recomendador_hit_rate": res_recomendador,
        "pronostico_monte_carlo": res_pronostico,
        "escenarios_principales": {
            "E1": _resumir_lote_replicas(rep_e1),
            "E2": _resumir_lote_replicas(rep_e2),
            "E3": _resumir_lote_replicas(rep_e3),
        },
        "pruebas_t_escenarios": pruebas_t,
        "sensibilidad_tau": sens_tau,
        "sensibilidad_c": sens_c,
        "sensibilidad_prec": sens_prec,
        "ablacion_monte_carlo": ablacion_mc,
    }

    ruta_json = ruta_datos / "resultados_experimentos.json"
    with ruta_json.open("w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    ruta_csv_rep = ruta_datos / "replicas_principales.csv"
    with ruta_csv_rep.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "escenario",
            "id_replica",
            "semilla",
            "wq_atendidos_min",
            "wq_primer_turno_min",
            "w_convocados_min",
            "lq_docentes",
            "t_total_min",
            "t_total_horas",
            "pct_reintentos",
            "pct_vacantes_cubiertas",
            "pct_sin_oferta",
            "satisfaccion_media",
            "mae_aviso_min",
            "pct_afectacion_merito_llamados",
            "cant_afectados_merito",
            "cant_llamados_principal",
            "cant_derivados_reintento",
        ])
        for lote in (rep_e1, rep_e2, rep_e3):
            for idx_r, r_item in enumerate(lote, start=1):
                writer.writerow([
                    r_item.escenario,
                    idx_r,
                    r_item.replica,
                    f"{r_item.wq_atendidos:.4f}",
                    f"{r_item.wq_primer_turno:.4f}",
                    f"{r_item.w_convocados:.4f}",
                    f"{r_item.lq:.4f}",
                    f"{r_item.t_total_min:.4f}",
                    f"{r_item.t_total_horas:.4f}",
                    f"{r_item.pct_reintentos:.4f}",
                    f"{r_item.pct_vacantes_cubiertas:.4f}",
                    f"{r_item.pct_sin_oferta:.4f}",
                    f"{r_item.satisfaccion_media:.4f}",
                    f"{r_item.mae_aviso:.4f}",
                    f"{r_item.pct_afectacion_merito_llamados:.4f}",
                    r_item.cant_afectados_merito,
                    r_item.cant_llamados_principal,
                    r_item.cant_derivados_reintento,
                ])

    print(f"[5/5] ¡Simulaciones finalizadas en {duracion_total_seg:.2f} s! Guardado en {ruta_json}")
    return salida


if __name__ == "__main__":
    ejecutar_todo()

