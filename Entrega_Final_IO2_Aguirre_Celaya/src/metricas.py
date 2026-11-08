"""
Cálculo de fórmulas teóricas (M/M/1 y M/M/c), intervalos de confianza al 95 %
mediante t de Student (n = 30, gl = 29) y pruebas de hipótesis t de Student
entre escenarios (pareadas por semilla común e independientes).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from src.utils import student_t_critico, student_t_pvalue_bilateral


@dataclass(frozen=True)
class TeoricoMMC:
    lam: float
    mu: float
    c: int
    rho: float
    p0: float
    lq: float
    l: float
    wq: float
    w: float


def formulas_teoricas_mmc(lam: float, mu: float, c: int = 1) -> TeoricoMMC:
    """Calcula los indicadores exactos en estado estacionario para M/M/1 o M/M/c (Erlang-C)."""
    rho = lam / (c * mu)
    if rho >= 1.0:
        raise ValueError(f"El sistema no es estable: rho = {rho:.4f} >= 1.")

    a = lam / mu
    suma = sum((a ** n) / math.factorial(n) for n in range(c))
    termino_cola = ((a ** c) / math.factorial(c)) * (1.0 / (1.0 - rho))
    p0 = 1.0 / (suma + termino_cola)

    lq = (p0 * (a ** c) * rho) / (math.factorial(c) * ((1.0 - rho) ** 2))
    wq = lq / lam
    w = wq + (1.0 / mu)
    l = lam * w
    return TeoricoMMC(lam=lam, mu=mu, c=c, rho=rho, p0=p0, lq=lq, l=l, wq=wq, w=w)


@dataclass(frozen=True)
class ResumenEstadistico:
    n: int
    gl: int
    media: float
    desvio: float
    error_estandar: float
    t_critico: float
    semiamplitud: float
    ic_inf: float
    ic_sup: float
    minimo: float
    maximo: float


def resumen_t_student(valores: Sequence[float], confianza: float = 0.95) -> ResumenEstadistico:
    """
    Calcula media muestral, desviación estándar muestral (n - 1) e intervalo de
    confianza bilateral usando la distribución t de Student con gl = n - 1.
    """
    n = len(valores)
    if n < 2:
        raise ValueError("Se requieren al menos 2 observaciones para calcular IC con t de Student.")
    gl = n - 1
    media = sum(valores) / n
    var = sum((x - media) ** 2 for x in valores) / gl
    desvio = math.sqrt(max(0.0, var))
    ee = desvio / math.sqrt(n)
    t_crit = student_t_critico(gl, confianza)
    semi = t_crit * ee
    return ResumenEstadistico(
        n=n,
        gl=gl,
        media=media,
        desvio=desvio,
        error_estandar=ee,
        t_critico=t_crit,
        semiamplitud=semi,
        ic_inf=media - semi,
        ic_sup=media + semi,
        minimo=min(valores),
        maximo=max(valores),
    )


@dataclass(frozen=True)
class ResultadoPruebaT:
    comparacion: str
    media_a: float
    media_b: float
    diferencia_media: float  # A - B
    cambio_porcentual: float  # 100 * (B - A) / A cuando A != 0
    desvio_diferencias: float
    ic95_dif_inf: float
    ic95_dif_sup: float
    t_pareado: float
    gl_pareado: int
    p_pareado: float
    t_welch: float
    gl_welch: float
    p_welch: float
    significativa_005: bool


def comparar_escenarios_t_student(
    nombre_comp: str,
    muestra_a: Sequence[float],
    muestra_b: Sequence[float],
    confianza: float = 0.95,
) -> ResultadoPruebaT:
    """
    Ejecuta tanto la prueba t de Student para muestras pareadas (réplicas con
    semillas emparejadas, gl = n - 1 = 29, Law 2015) como la prueba t de Welch
    de dos muestras independientes como control adicional.
    """
    if len(muestra_a) != len(muestra_b):
        raise ValueError("Las muestras a comparar deben tener la misma cantidad de réplicas.")
    n = len(muestra_a)
    gl_p = n - 1

    media_a = sum(muestra_a) / n
    media_b = sum(muestra_b) / n
    difs = [a - b for a, b in zip(muestra_a, muestra_b)]
    media_d = sum(difs) / n
    var_d = sum((d - media_d) ** 2 for d in difs) / gl_p
    sd_d = math.sqrt(max(0.0, var_d))
    ee_d = sd_d / math.sqrt(n)
    t_crit = student_t_critico(gl_p, confianza)
    semi_d = t_crit * ee_d

    if ee_d > 1e-15:
        t_par = media_d / ee_d
        p_par = student_t_pvalue_bilateral(t_par, gl_p)
    else:
        t_par = 0.0 if abs(media_d) <= 1e-15 else math.copysign(math.inf, media_d)
        p_par = 1.0 if abs(media_d) <= 1e-15 else 0.0

    # Prueba t de dos muestras independientes (Welch-Satterthwaite)
    var_a = sum((a - media_a) ** 2 for a in muestra_a) / gl_p
    var_b = sum((b - media_b) ** 2 for b in muestra_b) / gl_p
    ee_w_sq = (var_a / n) + (var_b / n)
    if ee_w_sq > 1e-15:
        t_welch = (media_a - media_b) / math.sqrt(ee_w_sq)
        num_gl = ee_w_sq ** 2
        den_gl = ((var_a / n) ** 2) / gl_p + ((var_b / n) ** 2) / gl_p
        gl_welch = num_gl / den_gl if den_gl > 1e-30 else float(2 * gl_p)
        p_welch = student_t_pvalue_bilateral(t_welch, gl_welch)
    else:
        t_welch = 0.0 if abs(media_a - media_b) <= 1e-15 else math.copysign(math.inf, media_a - media_b)
        gl_welch = float(2 * gl_p)
        p_welch = 1.0 if abs(media_a - media_b) <= 1e-15 else 0.0

    cambio_pct = (100.0 * (media_b - media_a) / media_a) if abs(media_a) > 1e-12 else 0.0

    return ResultadoPruebaT(
        comparacion=nombre_comp,
        media_a=media_a,
        media_b=media_b,
        diferencia_media=media_d,
        cambio_porcentual=cambio_pct,
        desvio_diferencias=sd_d,
        ic95_dif_inf=media_d - semi_d,
        ic95_dif_sup=media_d + semi_d,
        t_pareado=t_par,
        gl_pareado=gl_p,
        p_pareado=p_par,
        t_welch=t_welch,
        gl_welch=gl_welch,
        p_welch=p_welch,
        significativa_005=(p_par < 0.05),
    )

