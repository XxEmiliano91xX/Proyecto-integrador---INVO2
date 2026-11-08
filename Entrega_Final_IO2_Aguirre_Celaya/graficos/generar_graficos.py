"""
Generación reproducible de las figuras del Trabajo Final Integrador (IO2 - UCASAL).

Utiliza pandas para cargar, estructurar y resumir los resultados ya simulados
(`data/replicas_principales.csv` y `data/resultados_experimentos.json`) y matplotlib
para renderizar las 4 figuras de la Sección 6.4 en alta resolución (300 DPI), con
formato numérico en español (coma decimal) e intervalos de confianza al 95 % (t de Student, gl=29).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Directorio local de caché de fuentes de Matplotlib para evitar advertencias en Windows
_DIR_MPL_CACHE = Path(__file__).resolve().parent / ".mplcache"
_DIR_MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_DIR_MPL_CACHE))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


# Paleta sobria académica (apta para daltónicos y legible en escala de grises)
COLOR_E1 = "#4A5568"  # Gris pizarra oscuro (sistema actual)
COLOR_E2 = "#D97706"  # Ámbar / ocre (ventana tau=10 sin recomendador)
COLOR_E3 = "#0F766E"  # Verde azulado profundo / teal (propuesta completa E3)
COLOR_SEC = "#1D4ED8"  # Azul académico complementario
COLOR_ALERTA = "#B91C1C"  # Rojo sobrio para líneas de referencia


def fmt_coma(valor: float, decimales: int = 1) -> str:
    """Formatea un número flotante usando coma decimal estilo español."""
    return f"{valor:.{decimales}f}".replace(".", ",")


def eje_coma(decimales: int = 1) -> FuncFormatter:
    """Devuelve un formateador de ticks con coma decimal."""
    return FuncFormatter(lambda x, _: fmt_coma(x, decimales))


def configurar_estilo_academico() -> None:
    """Configura parámetros globales de matplotlib con estética limpia de informe universitario."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
            "font.size": 10.5,
            "axes.titlesize": 11.8,
            "axes.titleweight": "bold",
            "axes.labelsize": 10.5,
            "axes.edgecolor": "#CBD5E1",
            "axes.linewidth": 0.9,
            "axes.grid": True,
            "grid.color": "#E2E8F0",
            "grid.linestyle": "--",
            "grid.linewidth": 0.75,
            "grid.alpha": 0.85,
            "xtick.labelsize": 9.8,
            "ytick.labelsize": 9.8,
            "legend.fontsize": 9.2,
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#CBD5E1",
            "figure.facecolor": "#FFFFFF",
            "savefig.facecolor": "#FFFFFF",
            "savefig.dpi": 300,
        }
    )


def cargar_insumos(raiz: Path) -> tuple[pd.DataFrame, dict]:
    """Lee el CSV de las 90 réplicas principales con pandas y el JSON maestro de experimentos."""
    ruta_csv = raiz / "data" / "replicas_principales.csv"
    ruta_json = raiz / "data" / "resultados_experimentos.json"

    df_replicas = pd.read_csv(ruta_csv)
    with ruta_json.open("r", encoding="utf-8") as f:
        datos_json = json.load(f)
    return df_replicas, datos_json


def generar_figura_1_boxplot(df_replicas: pd.DataFrame, datos_json: dict, dir_salida: Path) -> Path:
    """
    Figura 1: Diagrama de cajas (boxplot) + dispersión de las 30 réplicas + media ± IC 95 %
    de la duración total de la asamblea T_total (en horas y minutos) para E1, E2 y E3.
    """
    escenarios = ["E1", "E2", "E3"]
    etiquetas = [
        "E1: Sistema actual\n(sin límite τ)",
        "E2: Ventana τ = 10 min\n+ aviso y reintentos",
        "E3: τ = 10 min + precarga,\nrecomendador y Monte Carlo",
    ]
    colores = [COLOR_E1, COLOR_E2, COLOR_E3]

    resumen_pd = (
        df_replicas.groupby("escenario", sort=False)["t_total_horas"]
        .agg(["count", "mean", "std", "median", "min", "max"])
        .reindex(escenarios)
    )

    series_horas = [
        df_replicas.loc[df_replicas["escenario"] == esc, "t_total_horas"].to_numpy()
        for esc in escenarios
    ]

    fig, ax = plt.subplots(figsize=(9.4, 5.5))

    bp = ax.boxplot(
        series_horas,
        positions=[1, 2, 3],
        widths=0.44,
        patch_artist=True,
        showmeans=False,
        medianprops={"color": "#111827", "linewidth": 2.0},
        whiskerprops={"color": "#475569", "linewidth": 1.2},
        capprops={"color": "#475569", "linewidth": 1.2},
        flierprops={"marker": "o", "markersize": 4.5, "alpha": 0.6, "markeredgecolor": "#475569"},
        zorder=2,
    )

    for patch, col in zip(bp["boxes"], colores):
        patch.set_facecolor(col)
        patch.set_alpha(0.26)
        patch.set_edgecolor(col)
        patch.set_linewidth(1.6)

    for idx, (esc, vals, col) in enumerate(zip(escenarios, series_horas, colores), start=1):
        n_pts = len(vals)
        offsets = [((k % 7) - 3) * 0.022 for k in range(n_pts)]
        xs = [idx + off for off in offsets]
        ax.scatter(
            xs,
            vals,
            color=col,
            alpha=0.55,
            s=22,
            edgecolors="white",
            linewidths=0.4,
            zorder=3,
            label="Réplicas individuales (n = 30)" if idx == 1 else None,
        )

        info_ic = datos_json["escenarios_principales"][esc]["t_total_horas"]
        media_h = info_ic["media"]
        semi_h = info_ic["semiamplitud"]
        media_min = datos_json["escenarios_principales"][esc]["t_total_min"]["media"]

        ax.errorbar(
            idx + 0.27,
            media_h,
            yerr=semi_h,
            fmt="D",
            color=col,
            ecolor=col,
            elinewidth=1.8,
            capsize=5,
            capthick=1.5,
            markersize=6.5,
            zorder=4,
            label="Media muestral ± IC 95 % (t Student)" if idx == 1 else None,
        )

        texto_caja = (
            f"Media: {fmt_coma(media_h, 2)} h\n"
            f"({fmt_coma(media_min, 1)} min)\n"
            f"± {fmt_coma(semi_h, 2)} h"
        )
        ax.annotate(
            texto_caja,
            xy=(idx + 0.27, media_h),
            xytext=(idx + 0.33, media_h),
            fontsize=8.8,
            va="center",
            ha="left",
            color="#1E293B",
            bbox={
                "boxstyle": "round,pad=0.26",
                "facecolor": "#F8FAFC",
                "edgecolor": col,
                "alpha": 0.94,
                "linewidth": 0.9,
            },
        )

    m_e1 = resumen_pd.loc["E1", "mean"]
    m_e3 = resumen_pd.loc["E3", "mean"]
    pct_red_e3 = abs((m_e3 - m_e1) / m_e1 * 100.0)
    ahorro_min_e3 = (
        datos_json["escenarios_principales"]["E1"]["t_total_min"]["media"]
        - datos_json["escenarios_principales"]["E3"]["t_total_min"]["media"]
    )
    p_ttot = datos_json["pruebas_t_escenarios"]["E1_vs_E3"]["t_total_min"]["p_pareado"]
    txt_p = "p < 0,001" if p_ttot < 0.001 else f"p = {fmt_coma(p_ttot, 3)}"

    min_global = float(df_replicas["t_total_horas"].min())
    max_global = float(df_replicas["t_total_horas"].max())
    rango_y = max(1.0, max_global - min_global)
    y_inf = min_global - 0.16 * rango_y
    y_sup = max_global + 0.16 * rango_y

    ax.annotate(
        f"Reducción E1 → E3: −{fmt_coma(pct_red_e3, 1)} % (−{fmt_coma(ahorro_min_e3, 1)} min; {txt_p})",
        xy=(3, m_e3),
        xytext=(0.45, 0.06),
        xycoords="axes fraction",
        textcoords="axes fraction",
        fontsize=9.2,
        fontweight="bold",
        color=COLOR_E3,
        ha="center",
        va="bottom",
        bbox={"boxstyle": "round,pad=0.32", "facecolor": "#F0FDFA", "edgecolor": COLOR_E3, "linewidth": 1.0},
    )

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(etiquetas)
    ax.set_xlim(0.55, 3.88)
    ax.set_ylim(y_inf, y_sup)
    ax.set_ylabel("Duración total de la asamblea, $T_{\\mathrm{total}}$ (horas)")
    ax.yaxis.set_major_formatter(eje_coma(1))
    ax.set_title(
        "Figura 1. Distribución de la duración total de la asamblea por escenario (30 réplicas, c = 1)",
        pad=12,
    )

    ax_min = ax.secondary_yaxis("right", functions=(lambda h: h * 60.0, lambda m: m / 60.0))
    ax_min.set_ylabel("Equivalente en minutos (min)", color="#475569")
    ax_min.yaxis.set_major_formatter(eje_coma(0))

    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)

    fig.tight_layout()
    ruta_out = dir_salida / "fig1_boxplot_duracion_escenarios.png"
    fig.savefig(ruta_out, dpi=300)
    plt.close(fig)
    return ruta_out


def generar_figura_2_sensibilidad_tau(datos_json: dict, dir_salida: Path) -> Path:
    """
    Figura 2: Evolución de los tiempos de espera (W_q y W_conv) y del porcentaje de derivación
    a reintentos al variar la ventana máxima de decisión tau en {6, 8, 10, 12, 15} minutos.
    """
    filas = []
    for esc in ("E2", "E3"):
        for tau_str, metricas in datos_json["sensibilidad_tau"][esc].items():
            filas.append(
                {
                    "escenario": esc,
                    "tau": int(tau_str),
                    "wq_media": metricas["wq_atendidos"]["media"],
                    "wq_ic": metricas["wq_atendidos"]["semiamplitud"],
                    "wconv_media": metricas["w_convocados"]["media"],
                    "wconv_ic": metricas["w_convocados"]["semiamplitud"],
                    "ttot_media": metricas["t_total_min"]["media"],
                    "reint_media": metricas["pct_reintentos"]["media"],
                    "reint_ic": metricas["pct_reintentos"]["semiamplitud"],
                }
            )
    df_tau = pd.DataFrame(filas).sort_values(["escenario", "tau"])

    df_e2 = df_tau[df_tau["escenario"] == "E2"]
    df_e3 = df_tau[df_tau["escenario"] == "E3"]
    wq_e1 = datos_json["escenarios_principales"]["E1"]["wq_atendidos"]["media"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 5.4))

    # --- Panel A: Tiempos medios de espera W_q y W_conv ---
    ax1.errorbar(
        df_e2["tau"],
        df_e2["wq_media"],
        yerr=df_e2["wq_ic"],
        marker="s",
        linestyle="-",
        linewidth=2.0,
        capsize=4,
        color=COLOR_E2,
        label="E2 — $W_q$ (atendidos)",
    )
    ax1.errorbar(
        df_e3["tau"],
        df_e3["wq_media"],
        yerr=df_e3["wq_ic"],
        marker="o",
        linestyle="-",
        linewidth=2.2,
        capsize=4,
        color=COLOR_E3,
        label="E3 — $W_q$ (atendidos)",
    )
    ax1.plot(
        df_e3["tau"],
        df_e3["wconv_media"],
        marker="^",
        linestyle="--",
        linewidth=1.9,
        color=COLOR_SEC,
        label="E3 — $W_{\\mathrm{conv}}$ (300 convocados)",
    )
    ax1.axhline(
        wq_e1,
        color=COLOR_E1,
        linestyle=":",
        linewidth=1.5,
        label=f"Referencia E1 $W_q$ ({fmt_coma(wq_e1, 1)} min)",
    )

    fila_opt = df_e3.loc[df_e3["ttot_media"].idxmin()]
    tau_opt = int(fila_opt["tau"])
    y_opt_wconv = float(fila_opt["wconv_media"])
    ttot_opt = float(fila_opt["ttot_media"])
    ax1.axvline(tau_opt, color="#94A3B8", linestyle="-.", linewidth=1.1, alpha=0.8)

    y_min_a = min(float((df_e3["wq_media"] - df_e3["wq_ic"]).min()), wq_e1)
    y_max_a = max(float((df_e2["wq_media"] + df_e2["wq_ic"]).max()), float(df_e3["wconv_media"].max()))
    rango_a = max(20.0, y_max_a - y_min_a)

    en_derecha = tau_opt >= 11
    loc_leg_a = "upper left" if en_derecha else "upper right"
    x_anot_a = 13.1 if en_derecha else 8.0

    ax1.annotate(
        f"Mínimo E3 ($\\tau = {tau_opt}$ min)\n$W_{{\\mathrm{{conv}}}}$ = {fmt_coma(y_opt_wconv, 1)} min\n$T_{{\\mathrm{{total}}}}$ = {fmt_coma(ttot_opt, 1)} min",
        xy=(tau_opt, y_opt_wconv),
        xytext=(x_anot_a, y_max_a + 0.25 * rango_a),
        fontsize=8.3,
        color=COLOR_SEC,
        fontweight="bold",
        ha="center",
        bbox={"boxstyle": "round,pad=0.26", "facecolor": "#EFF6FF", "edgecolor": COLOR_SEC, "linewidth": 0.9},
        arrowprops={"arrowstyle": "->", "color": COLOR_SEC, "lw": 1.15},
    )

    ax1.set_xticks([6, 8, 10, 12, 15])
    ax1.set_xlim(5.3, 15.7)
    ax1.set_ylim(y_min_a - 0.12 * rango_a, y_max_a + 0.56 * rango_a)
    ax1.set_xlabel("Ventana máxima de atención por turno, $\\tau$ (minutos)")
    ax1.set_ylabel("Tiempo medio de espera (minutos)")
    ax1.yaxis.set_major_formatter(eje_coma(0))
    ax1.set_title("(a) Evolución de las esperas medias ($W_q$ y $W_{\\mathrm{conv}}$)", pad=10)
    ax1.legend(loc=loc_leg_a, fontsize=8.3)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Panel B: Porcentaje de derivación a reintentos ---
    ax2.errorbar(
        df_e2["tau"],
        df_e2["reint_media"],
        yerr=df_e2["reint_ic"],
        marker="s",
        linestyle="-",
        linewidth=2.0,
        capsize=4,
        color=COLOR_E2,
        label="E2 (sin recomendador)",
    )
    ax2.errorbar(
        df_e3["tau"],
        df_e3["reint_media"],
        yerr=df_e3["reint_ic"],
        marker="o",
        linestyle="-",
        linewidth=2.2,
        capsize=4,
        color=COLOR_E3,
        label="E3 (con recomendador + Monte Carlo)",
    )
    ax2.axhline(
        8.0,
        color=COLOR_ALERTA,
        linestyle=":",
        linewidth=1.5,
        label="Piso técnico por desconexiones (p = 8,0 %)",
    )
    ax2.axvline(tau_opt, color="#94A3B8", linestyle="-.", linewidth=1.1, alpha=0.8)

    # Etiquetas fuera de las barras de error para evitar superposición
    for _, fila in df_e2.iterrows():
        y_top = fila["reint_media"] + fila["reint_ic"] + 0.55
        ax2.text(
            fila["tau"],
            y_top,
            f"{fmt_coma(fila['reint_media'], 1)} %",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color=COLOR_E2,
            bbox={"boxstyle": "round,pad=0.10", "facecolor": "#FFFFFF", "edgecolor": "none", "alpha": 0.80},
        )
    for _, fila in df_e3.iterrows():
        y_bot = fila["reint_media"] - fila["reint_ic"] - 0.55
        if y_bot < 9.0:
            # Si quedaría sobre la línea roja de p = 8,0 %, ubicar por debajo de esa referencia
            y_bot = min(7.45, y_bot - 0.6)
        ax2.text(
            fila["tau"],
            y_bot,
            f"{fmt_coma(fila['reint_media'], 1)} %",
            ha="center",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color=COLOR_E3,
            bbox={"boxstyle": "round,pad=0.10", "facecolor": "#FFFFFF", "edgecolor": "none", "alpha": 0.80},
        )

    ax2.set_xticks([6, 8, 10, 12, 15])
    ax2.set_xlim(5.3, 15.7)
    y_max_b = float((df_e2["reint_media"] + df_e2["reint_ic"]).max())
    ax2.set_ylim(4.0, max(28.0, y_max_b + 5.5))
    ax2.set_xlabel("Ventana máxima de atención por turno, $\\tau$ (minutos)")
    ax2.set_ylabel("Docentes derivados a cola de reintentos (%)")
    ax2.yaxis.set_major_formatter(eje_coma(0))
    ax2.set_title("(b) Derivación a reintentos vs. piso de desconexión", pad=10)
    ax2.legend(loc="upper right", fontsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle(
        "Figura 2. Análisis de sensibilidad respecto de la ventana máxima $\\tau$ (IC 95 % t de Student, c = 1)",
        fontsize=12.4,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    ruta_out = dir_salida / "fig2_sensibilidad_ventana_tau.png"
    fig.savefig(ruta_out, dpi=300)
    plt.close(fig)
    return ruta_out


def generar_figura_3_sensibilidad_c(datos_json: dict, dir_salida: Path) -> Path:
    """
    Figura 3: Reducción de la duración de jornada (en horas) y de la espera general W_conv (en min)
    al habilitar c en {1, 2, 3} comisiones de atención simultáneas para E1, E2 y E3.
    """
    filas = []
    for esc in ("E1", "E2", "E3"):
        for c_str, metricas in datos_json["sensibilidad_c"][esc].items():
            filas.append(
                {
                    "escenario": esc,
                    "c": int(c_str),
                    "horas_media": metricas["t_total_horas"]["media"],
                    "horas_ic": metricas["t_total_horas"]["semiamplitud"],
                    "wconv_media": metricas["w_convocados"]["media"],
                    "wconv_ic": metricas["w_convocados"]["semiamplitud"],
                }
            )
    df_c = pd.DataFrame(filas).sort_values(["c", "escenario"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 5.4))

    ancho = 0.25
    posiciones_c = [1, 2, 3]
    desplazamientos = {"E1": -ancho, "E2": 0.0, "E3": ancho}
    colores = {"E1": COLOR_E1, "E2": COLOR_E2, "E3": COLOR_E3}
    nombres = {
        "E1": "E1: Sin límite",
        "E2": "E2: τ = 10 min",
        "E3": "E3: τ = 10 min + Rec. + MC",
    }

    # --- Panel A: Duración total en horas ---
    for esc in ("E1", "E2", "E3"):
        sub = df_c[df_c["escenario"] == esc].sort_values("c")
        xs = [c_val + desplazamientos[esc] for c_val in sub["c"]]
        barras = ax1.bar(
            xs,
            sub["horas_media"],
            width=ancho * 0.92,
            yerr=sub["horas_ic"],
            capsize=4,
            color=colores[esc],
            alpha=0.88,
            edgecolor="#1E293B",
            linewidth=0.7,
            error_kw={"elinewidth": 1.3, "ecolor": "#1E293B"},
            label=nombres[esc],
        )
        for rect, val_h, ic_h in zip(barras, sub["horas_media"], sub["horas_ic"]):
            ax1.text(
                rect.get_x() + rect.get_width() / 2.0,
                val_h + ic_h + 0.16,
                f"{fmt_coma(val_h, 2)} h",
                ha="center",
                va="bottom",
                fontsize=8.3,
                fontweight="bold" if esc == "E3" else "normal",
                color="#0F172A",
            )

    ax1.axhline(
        4.0,
        color=COLOR_SEC,
        linestyle="--",
        linewidth=1.3,
        alpha=0.85,
        label="Referencia media jornada (4,0 h)",
    )
    ax1.set_xticks(posiciones_c)
    ax1.set_xticklabels(["c = 1 comisión", "c = 2 comisiones", "c = 3 comisiones"])
    max_h = float((df_c["horas_media"] + df_c["horas_ic"]).max())
    ax1.set_ylim(0, max_h * 1.18)
    ax1.set_ylabel("Duración total de la jornada, $T_{\\mathrm{total}}$ (horas)")
    ax1.yaxis.set_major_formatter(eje_coma(1))
    ax1.set_title("(a) Duración total del acto público ($T_{\\mathrm{total}}$)", pad=10)
    ax1.legend(loc="upper right", fontsize=8.6)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Panel B: Espera media general W_conv en minutos ---
    for esc in ("E1", "E2", "E3"):
        sub = df_c[df_c["escenario"] == esc].sort_values("c")
        xs = [c_val + desplazamientos[esc] for c_val in sub["c"]]
        barras = ax2.bar(
            xs,
            sub["wconv_media"],
            width=ancho * 0.92,
            yerr=sub["wconv_ic"],
            capsize=4,
            color=colores[esc],
            alpha=0.88,
            edgecolor="#1E293B",
            linewidth=0.7,
            error_kw={"elinewidth": 1.3, "ecolor": "#1E293B"},
            label=nombres[esc],
        )
        for rect, val_m, ic_m in zip(barras, sub["wconv_media"], sub["wconv_ic"]):
            ax2.text(
                rect.get_x() + rect.get_width() / 2.0,
                val_m + ic_m + 7.0,
                f"{fmt_coma(val_m, 0)}",
                ha="center",
                va="bottom",
                fontsize=8.3,
                fontweight="bold" if esc == "E3" else "normal",
                color="#0F172A",
            )

    ax2.set_xticks(posiciones_c)
    ax2.set_xticklabels(["c = 1 comisión", "c = 2 comisiones", "c = 3 comisiones"])
    max_wconv_c = float((df_c["wconv_media"] + df_c["wconv_ic"]).max())
    ax2.set_ylim(0, max_wconv_c * 1.18)
    ax2.set_ylabel("Espera media sobre 300 convocados, $W_{\\mathrm{conv}}$ (min)")
    ax2.yaxis.set_major_formatter(eje_coma(0))
    ax2.set_title("(b) Espera media del padrón convocado ($W_{\\mathrm{conv}}$, en min)", pad=10)
    ax2.legend(loc="upper right", fontsize=8.6)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle(
        "Figura 3. Impacto de habilitar múltiples comisiones en paralelo ($c \\in \\{1, 2, 3\\}$, $\\tau = 10$ min, IC 95 %)",
        fontsize=12.4,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    ruta_out = dir_salida / "fig3_sensibilidad_comisiones_c.png"
    fig.savefig(ruta_out, dpi=300)
    plt.close(fig)
    return ruta_out


def generar_figura_4_adopcion_y_mc(datos_json: dict, dir_salida: Path) -> Path:
    """
    Figura 4: (a) Sensibilidad del Escenario 3 al porcentaje de adopción del recomendador
    p_rec en {0,30; 0,50; 0,70; 0,90} frente a E1 y E2; y (b) efecto del pronóstico Monte Carlo
    sobre el error cuadrático medio (MSE) de disponibilidad y el desempeño del preaviso.
    """
    filas_prec = []
    e2_base = datos_json["escenarios_principales"]["E2"]
    filas_prec.append(
        {
            "p_rec_pct": 0,
            "ttot_media": e2_base["t_total_min"]["media"],
            "ttot_ic": e2_base["t_total_min"]["semiamplitud"],
            "wconv_media": e2_base["w_convocados"]["media"],
            "wconv_ic": e2_base["w_convocados"]["semiamplitud"],
        }
    )
    for prec_str, metricas in datos_json["sensibilidad_prec"].items():
        filas_prec.append(
            {
                "p_rec_pct": int(round(float(prec_str) * 100)),
                "ttot_media": metricas["t_total_min"]["media"],
                "ttot_ic": metricas["t_total_min"]["semiamplitud"],
                "wconv_media": metricas["w_convocados"]["media"],
                "wconv_ic": metricas["w_convocados"]["semiamplitud"],
            }
        )
    df_prec = pd.DataFrame(filas_prec).sort_values("p_rec_pct")

    ttot_e1 = datos_json["escenarios_principales"]["E1"]["t_total_min"]["media"]
    ttot_e2 = e2_base["t_total_min"]["media"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 5.4))

    # --- Panel A: Curva de adopción p_rec ---
    ax1.axhline(
        ttot_e1,
        color=COLOR_E1,
        linestyle=":",
        linewidth=1.5,
        label=f"Referencia E1 $T_{{\\mathrm{{total}}}}$ ({fmt_coma(ttot_e1, 1)} min)",
    )
    ax1.axhline(
        ttot_e2,
        color=COLOR_E2,
        linestyle="-.",
        linewidth=1.3,
        alpha=0.85,
        label=f"Referencia E2 $T_{{\\mathrm{{total}}}}$ ({fmt_coma(ttot_e2, 1)} min)",
    )
    ax1.errorbar(
        df_prec["p_rec_pct"],
        df_prec["ttot_media"],
        yerr=df_prec["ttot_ic"],
        marker="o",
        linewidth=2.2,
        capsize=4,
        color=COLOR_E3,
        label="E3 — Duración total $T_{\\mathrm{total}}$ (min)",
    )
    ax1.errorbar(
        df_prec["p_rec_pct"],
        df_prec["wconv_media"],
        yerr=df_prec["wconv_ic"],
        marker="s",
        linestyle="--",
        linewidth=1.9,
        capsize=4,
        color=COLOR_SEC,
        label="E3 — Espera general $W_{\\mathrm{conv}}$ (min)",
    )

    # Etiquetas de T_total posicionadas debajo de la barra de error para no tocar las líneas E1/E2
    for _, fila in df_prec[df_prec["p_rec_pct"] > 0].iterrows():
        es_base = int(fila["p_rec_pct"]) == 70
        y_lbl = fila["ttot_media"] - fila["ttot_ic"] - 6.0
        ax1.text(
            fila["p_rec_pct"],
            y_lbl,
            f"{fmt_coma(fila['ttot_media'], 1)} min" + ("\n(base)" if es_base else ""),
            ha="center",
            va="top",
            fontsize=8.3,
            fontweight="bold" if es_base else "normal",
            color=COLOR_E3,
        )

    ax1.set_xticks([0, 30, 50, 70, 90])
    ax1.set_xticklabels(["0 %\n(E2)", "30 %", "50 %", "70 %\n(base)", "90 %"])
    ax1.set_xlim(-6, 98)
    y_min_p = float((df_prec["wconv_media"] - df_prec["wconv_ic"]).min())
    y_max_p = max(ttot_e1, ttot_e2, float((df_prec["ttot_media"] + df_prec["ttot_ic"]).max()))
    rango_p = max(20.0, y_max_p - y_min_p)
    ax1.set_ylim(y_min_p - 0.16 * rango_p, y_max_p + 0.36 * rango_p)
    ax1.set_xlabel("Adopción efectiva del recomendador en el aviso previo, $p_{\\mathrm{rec}}$")
    ax1.set_ylabel("Minutos (media ± IC 95 %)")
    ax1.yaxis.set_major_formatter(eje_coma(0))
    ax1.set_title("(a) Sensibilidad a la tasa de adopción ($p_{\\mathrm{rec}}$)", pad=10)
    ax1.legend(loc="upper right", fontsize=8.3, ncol=1)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Panel B: Comparación Con vs. Sin pronóstico Monte Carlo ---
    pron = datos_json["pronostico_monte_carlo"]
    abl = datos_json["ablacion_monte_carlo"]

    df_mc = pd.DataFrame(
        [
            {
                "variante": "Sin Monte Carlo\n($R_{\\mathrm{MC}} = 0$, foto estática)",
                "mse_global": pron["base_mse_rep"]["media"],
                "mse_ic": pron["base_mse_rep"]["semiamplitud"],
                "mse_disputa": pron["en_disputa_base_mse"]["media"],
                "mse_disputa_ic": pron["en_disputa_base_mse"]["semiamplitud"],
                "ttot_min": abl["E3_sin_MC"]["t_total_min"]["media"],
            },
            {
                "variante": "Con Monte Carlo\n($R_{\\mathrm{MC}} = 200$ pasadas)",
                "mse_global": pron["mc_mse_rep"]["media"],
                "mse_ic": pron["mc_mse_rep"]["semiamplitud"],
                "mse_disputa": pron["en_disputa_mc_mse"]["media"],
                "mse_disputa_ic": pron["en_disputa_mc_mse"]["semiamplitud"],
                "ttot_min": abl["E3_con_MC"]["t_total_min"]["media"],
            },
        ]
    )

    x_mc = [0, 1]
    w_mc = 0.32
    b1 = ax2.bar(
        [x - w_mc / 2 for x in x_mc],
        df_mc["mse_global"],
        width=w_mc * 0.92,
        yerr=df_mc["mse_ic"],
        capsize=4,
        color=COLOR_SEC,
        alpha=0.86,
        edgecolor="#1E293B",
        linewidth=0.7,
        label="$MSE$ global (toda escuela libre)",
    )
    b2 = ax2.bar(
        [x + w_mc / 2 for x in x_mc],
        df_mc["mse_disputa"],
        width=w_mc * 0.92,
        yerr=df_mc["mse_disputa_ic"],
        capsize=4,
        color=COLOR_E2,
        alpha=0.86,
        edgecolor="#1E293B",
        linewidth=0.7,
        label="$MSE$ en vacantes disputadas ($\\theta_{ij} < 1$)",
    )

    for rect, val, ic in zip(b1, df_mc["mse_global"], df_mc["mse_ic"]):
        ax2.text(
            rect.get_x() + rect.get_width() / 2.0,
            val + ic + 0.012,
            fmt_coma(val, 4),
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#0F172A",
        )
    for rect, val, ic in zip(b2, df_mc["mse_disputa"], df_mc["mse_disputa_ic"]):
        ax2.text(
            rect.get_x() + rect.get_width() / 2.0,
            val + ic + 0.012,
            fmt_coma(val, 4),
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#0F172A",
        )

    t_sin = df_mc.loc[0, "ttot_min"]
    t_con = df_mc.loc[1, "ttot_min"]
    sat_sin = abl["E3_sin_MC"]["satisfaccion_media"]["media"]
    sat_con = abl["E3_con_MC"]["satisfaccion_media"]["media"]
    p_sat = abl["pruebas_t_sinMC_vs_conMC"]["satisfaccion_media"]["p_pareado"]
    txt_p_sat = "p < 0,001" if p_sat < 0.001 else f"p = {fmt_coma(p_sat, 3)}"
    pct_caida_mse = abs((df_mc.loc[1, "mse_global"] - df_mc.loc[0, "mse_global"]) / df_mc.loc[0, "mse_global"] * 100.0)
    pct_caida_disp = abs((df_mc.loc[1, "mse_disputa"] - df_mc.loc[0, "mse_disputa"]) / df_mc.loc[0, "mse_disputa"] * 100.0)

    resumen_mc_txt = (
        "Aporte específico de Monte Carlo ($p_{\\mathrm{rec}}$ = 0,70):\n"
        f"• $MSE$ global: −{fmt_coma(pct_caida_mse, 1)} % | En disputa: −{fmt_coma(pct_caida_disp, 1)} %\n"
        f"• $T_{{\\mathrm{{total}}}}$: {fmt_coma(t_sin, 2)} → {fmt_coma(t_con, 2)} min ({fmt_coma(t_con - t_sin, 2)} min)\n"
        f"• Satisfacción: {fmt_coma(sat_sin, 3)} → {fmt_coma(sat_con, 3)} ({txt_p_sat})"
    )
    ax2.text(
        0.98,
        0.72,
        resumen_mc_txt,
        transform=ax2.transAxes,
        ha="right",
        va="top",
        fontsize=8.2,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#F8FAFC", "edgecolor": "#94A3B8", "linewidth": 0.9},
    )

    ax2.set_xticks(x_mc)
    ax2.set_xticklabels(df_mc["variante"])
    ax2.set_xlim(-0.5, 1.55)
    max_mse_y = max(float((df_mc["mse_global"] + df_mc["mse_ic"]).max()), float((df_mc["mse_disputa"] + df_mc["mse_disputa_ic"]).max()))
    ax2.set_ylim(0, max(0.55, max_mse_y * 1.28))
    ax2.set_ylabel("Error cuadrático medio de disponibilidad ($MSE$)")
    ax2.yaxis.set_major_formatter(eje_coma(2))
    ax2.set_title("(b) Precisión del pronóstico Monte Carlo en el preaviso", pad=10)
    ax2.legend(loc="upper right", fontsize=8.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle(
        "Figura 4. Sensibilidad a la adopción del recomendador ($p_{\\mathrm{rec}}$) y aporte del pronóstico Monte Carlo",
        fontsize=12.4,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    ruta_out = dir_salida / "fig4_adopcion_recomendador_y_montecarlo.png"
    fig.savefig(ruta_out, dpi=300)
    plt.close(fig)
    return ruta_out


def main() -> None:
    raiz = Path(__file__).resolve().parent.parent
    dir_salida = Path(__file__).resolve().parent / "salida"
    dir_salida.mkdir(parents=True, exist_ok=True)

    configurar_estilo_academico()
    df_replicas, datos_json = cargar_insumos(raiz)

    rutas = [
        generar_figura_1_boxplot(df_replicas, datos_json, dir_salida),
        generar_figura_2_sensibilidad_tau(datos_json, dir_salida),
        generar_figura_3_sensibilidad_c(datos_json, dir_salida),
        generar_figura_4_adopcion_y_mc(datos_json, dir_salida),
    ]

    print("Figuras generadas correctamente en 300 DPI:")
    for r in rutas:
        print(f" - {r.relative_to(raiz)}")


if __name__ == "__main__":
    main()
