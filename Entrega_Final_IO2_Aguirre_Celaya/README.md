# Universidad Católica de Salta — Facultad de Ingeniería
## Investigación Operativa II (2026) — Trabajo Final Integrador
### Sistema de turnos dinámicos con recomendación de vacantes para las asambleas de designación docente en Salta

**Integrantes:**
* Emiliano Javier Aguirre — DNI 45.770.631
* Pablo Celaya — DNI 45.115.839

**Cátedra:**
* Profesor Titular: Mg. Ing. Gustavo Ramiro Rivadera
* Profesor Auxiliar: Ing. Gustavo Flores Vargas

---

## 1. Contenido del paquete de entrega

Este paquete contiene todos los entregables requeridos por la Sección 6 de la consigna oficial (`Trabajo_Final_IO2_2026.md`):

* `Informe_Final_IO2_2026_Aguirre_Celaya.docx`: informe completo en formato Microsoft Word con portada, ecuaciones nativas, tablas formateadas y gráficos incrustados (19 páginas de desarrollo, cumpliendo con la pauta de 12 a 20 páginas de la Modalidad A).
* `Informe_Final_IO2_2026_Aguirre_Celaya.pdf`: copia idéntica exportada en PDF para visualización y lectura directa.
* `notebooks/experimentos.ipynb`: notebook de Jupyter interactivo con la verificación analítica ($M/M/1$ y $M/M/c$), calibración de modelos y visualización de resultados.
* `src/`: código fuente modular en Python 3 estándar (no requiere librerías externas para la simulación).
  * `src/utils.py`: distancias geodésicas (Haversine), sorteo log-normal y control de semillas.
  * `src/generar_datos.py`: generación reproducible de los datasets.
  * `src/recomendador.py`: filtrado por nivel edilicio, puntaje multicriterio y pronóstico Monte Carlo ($R_{\text{MC}} = 200$).
  * `src/simulation.py`: motor de eventos discretos (`heapq`).
  * `src/metricas.py`: métricas de colas, Little finita y pruebas estadísticas pareadas.
  * `src/correr_experimentos.py`: script principal que ejecuta todas las validaciones y réplicas.
* `data/`: datos de entrada y salidas experimentales:
  * `data/escuelas.csv`: 40 escuelas públicas reales de Salta Capital con su CUE verificado y nivel edilicio.
  * `data/cargos.csv`: 100 vacantes por nivel y turno.
  * `data/docentes.csv`: padrón de 300 docentes (semilla = 2026).
  * `data/replicas_principales.csv`: detalle réplica a réplica de las 90 corridas centrales.
  * `data/resultados_experimentos.json`: archivo JSON con los resultados numéricos consolidados.
* `graficos/`: scripts y figuras de resultados en alta resolución (300 DPI):
  * `graficos/salida/fig1_boxplot_duracion_escenarios.png`: duración y esperas entre E1, E2 y E3.
  * `graficos/salida/fig2_sensibilidad_ventana_tau.png`: sensibilidad de la ventana $\tau$.
  * `graficos/salida/fig3_sensibilidad_comisiones_c.png`: sensibilidad de comisiones simultáneas $c$.
  * `graficos/salida/fig4_adopcion_recomendador_y_montecarlo.png`: sensibilidad de adopción $p_{\text{rec}}$ y ablación Monte Carlo.

---

## 2. Instrucciones de reproducción

El motor de simulación fue programado usando exclusivamente la biblioteca estándar de Python 3, por lo que puede ejecutarse directamente sin instalar paquetes adicionales.

### A. Ejecución de la simulación y experimentos
Desde la raíz de la carpeta de entrega, abrir una terminal y ejecutar:

```powershell
python -m src.correr_experimentos
```

Esto ejecuta automáticamente:
1. La verificación contra los modelos teóricos $M/M/1$ y $M/M/c$.
2. La calibración del recomendador y del pronóstico Monte Carlo.
3. Las 30 réplicas independientes de E1, E2 y E3 con pruebas $t$ de Student pareadas ($gl = 29$).
4. Todos los análisis de sensibilidad ($\tau \in \{6, 8, 10, 12, 15\}$, $c \in \{1, 2, 3\}$, $p_{\text{rec}}$ y ablación).
5. Guarda las salidas en `data/resultados_experimentos.json` y `data/replicas_principales.csv`.

### B. Regeneración de los gráficos (opcional)
Si se desea regenerar las 4 figuras en alta resolución (`graficos/salida/`), se requiere `pandas` y `matplotlib`:

```powershell
pip install -r requirements.txt
python graficos/generar_graficos.py
```

### C. Exploración interactiva vía Jupyter Notebook
Para revisar los resultados de manera interactiva:

```powershell
jupyter notebook notebooks/experimentos.ipynb
```

