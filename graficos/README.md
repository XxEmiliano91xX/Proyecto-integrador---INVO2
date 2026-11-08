# Módulo de Gráficos (`graficos/`)

Carpeta aislada para generar las figuras de la **Sección 6.4** del informe final usando `pandas` y `matplotlib`, leyendo directamente los resultados ya corridos en `data/replicas_principales.csv` y `data/resultados_experimentos.json` (sin necesidad de re-ejecutar las simulaciones).

## Cómo regenerar las figuras

```powershell
# 1. Crear entorno virtual (una sola vez)
python -m venv .venv

# 2. Instalar dependencias (una sola vez)
.\.venv\Scripts\python.exe -m pip install -r graficos/requirements.txt

# 3. Generar las 4 figuras en 300 DPI
.\.venv\Scripts\python.exe graficos/generar_graficos.py
```

## Figuras exportadas en `graficos/salida/`

1. `fig1_boxplot_duracion_escenarios.png` — Diagrama de cajas, réplicas individuales ($n = 30$) y media $\pm$ IC 95 % ($t$ de Student) de la duración total $T_{\text{total}}$ en horas y minutos para E1, E2 y E3.
2. `fig2_sensibilidad_ventana_tau.png` — Sensibilidad respecto de la ventana $\tau \in \{6, 8, 10, 12, 15\}\text{ min}$: evolución de las esperas ($W_q$ y $W_{\text{conv}}$) y porcentaje de pases a la cola de reintentos.
3. `fig3_sensibilidad_comisiones_c.png` — Reducción de la duración de jornada ($T_{\text{total}}$) y de la espera general ($W_{\text{conv}}$) al habilitar $c \in \{1, 2, 3\}$ comisiones simultáneas.
4. `fig4_adopcion_recomendador_y_montecarlo.png` — Sensibilidad a la tasa de adopción del recomendador $p_{\text{rec}} \in \{0,30; 0,50; 0,70; 0,90\}$ y aporte del pronóstico Monte Carlo ($R_{\text{MC}} = 200$ vs. sin pronóstico).

