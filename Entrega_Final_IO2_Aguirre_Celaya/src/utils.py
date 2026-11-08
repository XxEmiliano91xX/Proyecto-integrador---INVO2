"""
Funciones auxiliares, constantes globales, generadores aleatorios controlados
y utilidades estadísticas exactas (distribución t de Student) para el simulador.
"""

from __future__ import annotations

import math
import random
from typing import Sequence, TypeVar

T = TypeVar("T")

# Parámetros globales del modelo (Sección 3.7 de Informe_Final_Integrado_v3.md)
SIGMA_LN: float = 0.8
RADIO_TIERRA_KM: float = 6371.0
PROB_AUSENCIA: float = 0.08
T_AUSENCIA: float = 5.0
T_PASE_SIN_OFERTA: float = 0.5
ALPHA_SUAVIZACION: float = 0.20
S_HAT_INICIAL: float = 3.0
VENTANA_AVISO_MIN: float = 10.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia geodésica en kilómetros mediante la fórmula de Haversine."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return RADIO_TIERRA_KM * c


def mu_lognormal(media: float, sigma: float = SIGMA_LN) -> float:
    """Despeja mu_LN = ln(m) - sigma^2 / 2 para que E[T] = media."""
    if media <= 0.0:
        raise ValueError(f"La media log-normal debe ser positiva, recibido: {media}")
    return math.log(media) - 0.5 * (sigma ** 2)


def lognormal_desde_z(z: float, media: float, sigma: float = SIGMA_LN) -> float:
    """Transforma una normal estándar Z ~ N(0,1) en LogNormal con esperanza 'media'."""
    return math.exp(mu_lognormal(media, sigma) + sigma * z)


class GeneradorAleatorio:
    """
    Generador pseudoaleatorio reproducible con interfaz limpia para simulación.
    Encapsula random.Random(semilla) (Mersenne Twister determinístico multiplataforma).
    """

    def __init__(self, semilla: int | None = None) -> None:
        self._rng = random.Random(semilla)

    def random(self) -> float:
        return self._rng.random()

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def normal(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        return self._rng.gauss(mu, sigma)

    def exponential(self, tasa_lambda: float) -> float:
        """Tiempo exponencial con tasa lambda (media 1 / tasa_lambda)."""
        u = self._rng.random()
        while u <= 1e-15:
            u = self._rng.random()
        return -math.log(u) / tasa_lambda

    def lognormal_media(self, media: float, sigma: float = SIGMA_LN) -> float:
        """Sortea T ~ LogNormal con esperanza igual a 'media' y dispersión 'sigma'."""
        z = self._rng.gauss(0.0, 1.0)
        return lognormal_desde_z(z, media, sigma)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        return self._rng.choice(seq)

    def sample_ponderado_sin_reposicion(
        self, elementos: Sequence[T], pesos: Sequence[float], k: int
    ) -> list[T]:
        """Muestreo sin reposición proporcional al peso (algoritmo de Efraimidis-Spirakis)."""
        if k > len(elementos):
            raise ValueError("k no puede superar el tamaño de la población disponible.")
        claves: list[tuple[float, T]] = []
        for elem, w in zip(elementos, pesos):
            peso = max(w, 1e-12)
            u = self._rng.random()
            while u <= 1e-15:
                u = self._rng.random()
            # Clave u^(1/w) equivalente a ordenar por log(u)/w (mayor es mejor)
            claves.append((math.log(u) / peso, elem))
        claves.sort(key=lambda par: par[0], reverse=True)
        return [par[1] for par in claves[:k]]


# ============================================================================
# Funciones exactas para la distribución t de Student (fracción continua Lentz)
# ============================================================================

def _betacf(a: float, b: float, x: float) -> float:
    """Fracción continua de Lentz para la función beta incompleta regularizada."""
    max_iter = 200
    eps = 3.0e-15
    fpmin = 1.0e-300

    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        del_h = d * c
        h *= del_h
        if abs(del_h - 1.0) < eps:
            break
    return h


def beta_incompleta_reg(a: float, b: float, x: float) -> float:
    """Función beta incompleta regularizada I_x(a, b) con precisión de máquina."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    bt = math.exp(a * math.log(x) + b * math.log(1.0 - x) - lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def student_t_cdf(t_val: float, gl: float) -> float:
    """Función de distribución acumulada F(t) para t de Student con 'gl' grados de libertad."""
    if gl <= 0.0:
        raise ValueError("Los grados de libertad deben ser positivos.")
    if t_val == 0.0:
        return 0.5
    x = gl / (gl + t_val * t_val)
    p = 0.5 * beta_incompleta_reg(0.5 * gl, 0.5, x)
    return 1.0 - p if t_val > 0.0 else p


def student_t_pvalue_bilateral(t_val: float, gl: float) -> float:
    """Valor-p bilateral exacto P(|T| >= |t_val|) con 'gl' grados de libertad."""
    if math.isinf(t_val):
        return 0.0
    x = gl / (gl + t_val * t_val)
    return beta_incompleta_reg(0.5 * gl, 0.5, x)


def student_t_critico(gl: float, nivel_confianza: float = 0.95) -> float:
    """
    Cuantil crítico positivo t_{gl; 1 - alpha/2} (ej. gl=29, conf=0.95 -> 2.045229642).
    """
    objetivo = 0.5 + 0.5 * nivel_confianza
    lo, hi = 0.0, 50.0
    while student_t_cdf(hi, gl) < objetivo:
        hi *= 2.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if student_t_cdf(mid, gl) < objetivo:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

