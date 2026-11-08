# Resultados Completos de las Simulaciones y Análisis Estadístico

> **Nota para Pablo:** Acá dejé volcadas todas las corridas actualizadas tras verificar y corregir las 40 escuelas reales de Salta Capital (se reemplazaron escuelas duplicadas o de La Caldera por establecimientos verificados de Capital con su `cue_anexo` real, y se incorporó la columna `niveles` en `escuelas.csv` para que cada cargo, preferencia y recomendación respete estrictamente la compatibilidad edilicia Inicial/Primario vs. Secundario). Todas las tablas mantienen la coma decimal de `Informe_Final_Integrado_v3.md`, los IC al 95 % con $t$ de Student ($n = 30$, $gl = 29$, $t_{29;\,0,975} = 2,0452$), las pruebas de hipótesis pareadas, las 4 figuras en 300 DPI en la carpeta separada `graficos/salida/` y los textos redactados listos para copiar y pegar.
>
> * **Recordatorio para actualizar la Sección 4 y 5 del informe:** en la tabla de `data/escuelas.csv` (sección 4.2) conviene agregar la fila de la columna `niveles` (`inicial;primario` o `secundario`); en la sección 4.4 aclarar que la ejecución completa corre en Python 3 estándar (`src/` con `python -m src.correr_experimentos`, sin dependencias externas) y los gráficos en `graficos/generar_graficos.py` (`pandas` + `matplotlib`); y en la sección 5.2.1/6.2 sumar *Hit Rate@1* junto a *Hit Rate@3* para evidenciar la calidad de ordenamiento frente a un conjunto filtrado medio de $|\bar{K}_i| = 13,39$ escuelas.
> * **Scripts de simulación (Python 3 estándar):** `src/utils.py`, `src/generar_datos.py`, `src/recomendador.py`, `src/simulation.py`, `src/metricas.py` y `src/correr_experimentos.py`.
> * **Módulo separado de gráficos (`pandas` + `matplotlib`):** `graficos/generar_graficos.py` y salidas PNG en `graficos/salida/`.
> * **Datos y salidas crudas:** `data/escuelas.csv` (40 escuelas reales de Capital), `data/cargos.csv` (100 vacantes coherentes por nivel), `data/docentes.csv` (300 docentes, `semilla = 2026`), `data/replicas_principales.csv` (las 90 corridas individuales de E1, E2 y E3) y `data/resultados_experimentos.json`.

---

## 0. Frase lista para completar el RESUMEN (línea 63 del informe)

> Los resultados sobre 30 réplicas independientes muestran que aplicar únicamente el límite de $\tau = 10$ minutos por turno (E2) prácticamente no acorta la jornada respecto del sistema actual ($T_{\text{total}}$ pasa de 541,14 a 538,79 min; $-0,4\,\%$, $p = 0,790$) ni mejora la espera general del padrón ($W_{\text{conv}}$ varía $+1,2\,\%$, $p = 0,406$), y en cambio empeora un **21,4 %** la espera acumulada de quienes son llamados ($W_q$ sube de 260,47 a 316,17 min; $p < 0,001$) debido a la doble espera de los docentes enviados a reintentos. En contraste, al sumar la precarga de preferencias, el recomendador multicriterio y el pronóstico Monte Carlo en el aviso previo (E3), la duración total de la jornada cae un **15,0 %** (de 9,02 h a 7,67 h, ahorrando 81,2 minutos; $p < 0,001$), la espera media de los 300 convocados baja un **13,7 %** (de 416,44 a 359,26 min; $p < 0,001$), la espera hasta el primer llamado disminuye un **10,7 %** (260,47 a 232,73 min; $p < 0,001$) manteniendo virtualmente empatada la espera acumulada con E1 ($263,64$ vs. $260,47\text{ min}$, $p = 0,628$) pero un **16,6 % por debajo de E2** ($p < 0,001$), y los casos derivados a reintento bajan del **16,86 % al 13,71 %** ($-18,7\,\%$, reduciendo un **20,6 %** los postulantes desplazados en su mérito).

---

## 6. RESULTADOS Y ANÁLISIS *(listo para trasladar al informe)*

### 6.1. Resultados de la verificación del simulador ($M/M/1$ y $M/M/c$)

Para comprobar que el motor de eventos discretos (`src/simulation.py`) maneja sin sesgos el reloj, la lista de eventos futuros (`heapq`) y las colas antes de cargarle las reglas particulares de la asamblea docente, corrimos **30 réplicas independientes** de los modelos markovianos abiertos vistos en clase. En cada réplica se descartaron los primeros 10.000 arribos como período de calentamiento (*warm-up*) y se midieron los 100.000 clientes siguientes en régimen estacionario, calculando intervalos de confianza al 95 % con la distribución $t$ de Student ($gl = 29$, $t_{29;\,0,975} = 2,0452$):

| Modelo de prueba | Métrica | Valor teórico exacto | Media simulada $\bar{X}$ | Desvío $s$ | IC 95 % ($t$ de Student, $gl=29$) | Error relativo (%) | ¿Contiene valor teórico? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$M/M/1$ ($\lambda=4, \mu=6$)** | $W_q$ (h) | 0,3333 | 0,3344 | 0,0070 | $[0,3318 \,;\, 0,3370]$ ($0,3344 \pm 0,0026$) | 0,32 % | Sí |
| **$M/M/1$ ($\lambda=4, \mu=6$)** | $L_q$ (clientes) | 1,3333 | 1,3383 | 0,0297 | $[1,3272 \,;\, 1,3493]$ ($1,3383 \pm 0,0111$) | 0,37 % | Sí |
| **$M/M/1$ ($\lambda=4, \mu=6$)** | $W$ (h) | 0,5000 | 0,5010 | 0,0075 | $[0,4982 \,;\, 0,5038]$ ($0,5010 \pm 0,0028$) | 0,20 % | Sí |
| **$M/M/1$ ($\lambda=4, \mu=6$)** | $L$ (clientes) | 2,0000 | 2,0051 | 0,0322 | $[1,9931 \,;\, 2,0171]$ ($2,0051 \pm 0,0120$) | 0,26 % | Sí |
| **$M/M/1$ ($\lambda=4, \mu=6$)** | $P_0$ | 0,3333 | 0,3331 | 0,0032 | $[0,3319 \,;\, 0,3343]$ ($0,3331 \pm 0,0012$) | 0,06 % | Sí |
| **$M/M/1$ ($\lambda=2, \mu=3$)** | $W_q$ (h) | 0,6667 | 0,6644 | 0,0171 | $[0,6580 \,;\, 0,6708]$ ($0,6644 \pm 0,0064$) | 0,34 % | Sí |
| **$M/M/1$ ($\lambda=2, \mu=3$)** | $L_q$ (clientes) | 1,3333 | 1,3291 | 0,0353 | $[1,3159 \,;\, 1,3423]$ ($1,3291 \pm 0,0132$) | 0,32 % | Sí |
| **$M/M/2$ ($\lambda=2, \mu=3$)** | $W_q$ (h) | 0,0417 | 0,0418 | 0,0011 | $[0,0414 \,;\, 0,0422]$ ($0,0418 \pm 0,0004$) | 0,27 % | Sí |
| **$M/M/2$ ($\lambda=2, \mu=3$)** | $L_q$ (clientes) | 0,0833 | 0,0835 | 0,0023 | $[0,0827 \,;\, 0,0844]$ ($0,0835 \pm 0,0009$) | 0,26 % | Sí |
| **$M/M/2$ ($\lambda=2, \mu=3$)** | $P_0$ | 0,5000 | 0,4998 | 0,0022 | $[0,4990 \,;\, 0,5006]$ ($0,4998 \pm 0,0008$) | 0,05 % | Sí |

**Lectura de verificación y controles internos (`assert`):**
* En todos los casos evaluados el error relativo frente a las fórmulas exactas de cátedra quedó **por debajo del 0,40 %** y los intervalos de confianza al 95 % contuvieron al parámetro teórico exacto. También pudimos ver en vivo el salto no lineal de Erlang-C que habíamos estudiado en la unidad de múltiples servidores: para $\lambda = 2$ y $\mu = 3$ clientes/h, pasar de $c = 1$ a $c = 2$ servidores desploma $W_q$ de $0,6644\text{ h}$ ($\approx 39,9\text{ min}$) a $0,0418\text{ h}$ ($\approx 2,5\text{ min}$).
* Asimismo, en el **100 % de las corridas de horizonte finito** ejecutadas (tanto en las 90 corridas centrales de E1, E2 y E3 como en todas las configuraciones de sensibilidad) se cumplieron sin excepción los tres chequeos automáticos de consistencia: (1) coincidencia exacta hasta precisión de punto flotante ($< 10^{-9}$) entre la integral temporal continua de la fila y la igualdad finita de Little $L_q = \frac{1}{T_{\text{total}}} \sum_{i=1}^{300} Q_i$; (2) conservación estricta de las 100 vacantes y compatibilidad de nivel edilicio y especialidad en cada cargo adjudicado; y (3) orden estrictamente decreciente de puntaje $P_i$ en todos los inicios de primer turno de la cola principal.

---

### 6.2. Desempeño del recomendador (*Hit Rate@3* / *Hit Rate@1*) y del pronóstico Monte Carlo ($MSE$ / $RMSE$)

#### 6.2.1. Evaluación y calibración del recomendador multicriterio

Siguiendo el protocolo de validación fuera de muestra de la sección 5.2.1 sobre los $N = 300$ docentes (ocultando sus opciones 6 a 10 de `preferencias_ocultas` y simulando agotadas sus 5 escuelas visibles de $L_i$, filtrando estrictamente por nivel edilicio, especialidad, radio máximo y turnos con un tamaño medio del conjunto candidato $|\bar{K}_i| = 13,39$ escuelas por docente), recorrimos las 231 combinaciones de pesos $(w_d, w_t, w_c)$ sobre la grilla de paso $0,05$. Para observar con nitidez la capacidad de ordenamiento más allá de acertar en un subconjunto de tamaño medio 13,39, incorporamos también la métrica estricta de acierto en la primera sugerencia (*Hit Rate@1*):

| Configuración evaluada | Pesos $(w_d \,;\, w_t \,;\, w_c)$ | Hit Rate@3 (%) | Mejora @3 vs. azar | Hit Rate@1 (%) | Mejora @1 vs. azar |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Elección al azar dentro del filtro $K_i$ | — | 75,02 % | — | 35,73 % | — |
| Escuelas más pedidas (popularidad general) | — | 94,00 % | +18,98 pp (+25,3 %) | 62,33 % | +26,61 pp (+74,5 %) |
| Solo coincidencia con otros docentes ($C_{ij}$) | $(0,00 \,;\, 0,00 \,;\, 1,00)$ | 90,67 % | +15,64 pp (+20,9 %) | 61,67 % | +25,94 pp (+72,6 %) |
| Solo parecido con su lista ($T_{ij}$) | $(0,00 \,;\, 1,00 \,;\, 0,00)$ | 92,33 % | +17,31 pp (+23,1 %) | 66,00 % | +30,27 pp (+84,7 %) |
| Solo cercanía en km ($D_{ij}$) | $(1,00 \,;\, 0,00 \,;\, 0,00)$ | 93,67 % | +18,64 pp (+24,9 %) | 66,33 % | +30,61 pp (+85,7 %) |
| Recomendador híbrido (pesos iniciales) | $(0,50 \,;\, 0,20 \,;\, 0,30)$ | 97,00 % | +21,98 pp (+29,3 %) | 68,67 % | +32,94 pp (+92,2 %) |
| **Recomendador combinado (óptimo de grilla)** | **$(0,40 \,;\, 0,40 \,;\, 0,20)$** | **97,33 %** | **+22,31 pp (+29,7 %)** | **69,67 %** | **+33,94 pp (+95,0 %)** |

**Qué aprendimos al calibrar los pesos y al distinguir *Hit Rate@3* de *Hit Rate@1*:** Al corregir los edificios escolares para respetar la compatibilidad real por nivel (`inicial;primario` en 24 escuelas y `secundario` en 16 colegios de Capital), el conjunto candidato $K_i$ se redujo a un promedio realista de **$13,39$ establecimientos** (en lugar de mezclar niveles distintos). Con 5 preferencias ocultas dentro de ~13 candidatos, hasta una selección aleatoria acierta alguna en el Top 3 el 75,02 % de las veces; por eso sumar **Hit Rate@1** resultó clave para validar que el algoritmo realmente ordena bien arriba de la lista: pasó de **35,73 % al azar a 69,67 % (+95,0 %, casi el doble)** en la posición N.° 1 y a **97,33 % en el Top 3**. Además, la búsqueda en grilla encontró un óptimo muy intuitivo en **$(w_d = 0,40 \,;\, w_t = 0,40 \,;\, w_c = 0,20)$**: el 80 % del peso prioriza la cercanía geográfica al domicilio y la similitud de zona/turno, dejando un 20 % para desempate por coincidencia con colegas. Igual que aclaramos en la metodología, tomamos estos porcentajes con prudencia porque las preferencias se generaron de forma sintética.

#### 6.2.2. Precisión del pronóstico de disponibilidad por simulación Monte Carlo

En las 30 réplicas del Escenario 3 se registraron en total **$n = 22.748$ evaluaciones** de escuelas abiertas al momento de emitir el aviso de 10 minutos (de las cuales **$3.312$ correspondieron a escuelas en disputa directa**, es decir, establecimientos por los que también competían docentes ubicados justo delante en la fila). Comparamos la probabilidad pronosticada $\theta_{ij}$ con $R_{\text{MC}} = 200$ pasadas contra el resultado real $y_{ij} \in \{0, 1\}$ al iniciar el turno del docente:

| Método de estimación en el preaviso (30 réplicas) | $MSE$ medio $\pm$ IC 95 % | Desvío $s$ ($MSE$) | $RMSE$ medio $\pm$ IC 95 % | $MSE$ solo en vacantes en disputa ($n=3.312$) | Observación |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Pronóstico Monte Carlo ($R_{\text{MC}} = 200$)** | **$0,0147 \pm 0,0010$** $[0,0136 \,;\, 0,0157]$ | 0,0028 | **$0,1205 \pm 0,0043$** $[0,1162 \,;\, 0,1248]$ | **$0,1006 \pm 0,0053$** $[0,0953 \,;\, 0,1058]$ | Anticipa el consumo de vacantes de los 2 a 5 turnos previos |
| **Sin pronóstico (mirar solo si hoy está libre)** | **$0,0511 \pm 0,0021$** $[0,0490 \,;\, 0,0533]$ | 0,0057 | **$0,2258 \pm 0,0047$** $[0,2210 \,;\, 0,2305]$ | **$0,3550 \pm 0,0191$** $[0,3360 \,;\, 0,3741]$ | Asume $\theta_{ij}=1$ para toda escuela abierta en ese instante |

* **Prueba $t$ de Student pareada sobre el $MSE$ ($gl = 29$):** la diferencia media es $\bar{D} = 0,0365$ ($\text{IC } 95\,\%: [0,0346 \,;\, 0,0384]$), con **$t = 39,22$** y **$p = 1,11 \times 10^{-26}$**, lo que representa una **reducción del 71,3 % en el $MSE$** (y del **46,6 % en el $RMSE$**). Donde más se nota su utilidad práctica es en las vacantes disputadas por turnos inmediatos ($n = 3.312$ pares): mirar solo la foto estática del momento del aviso alcanza un error de $MSE = 0,3550$, mientras que las 200 pasadas rápidas anticipan qué colega de adelante va a tomar ese cargo y reducen el error un **71,7 %** ($MSE = 0,1006$).

---

### 6.3. Comparación principal entre escenarios (E1, E2 y E3 — 30 réplicas)

#### Tabla resumida (formato directo para la Sección 6.3 del informe)

| Indicador de desempeño (Media $\pm$ IC 95 %, $n=30, gl=29$) | E1 (Actual sin límite) | E2 (Ventana $\tau=10$ min + Reintentos) | E3 (Asistido: Recomendador + Pronóstico MC) |
| :--- | :---: | :---: | :---: |
| Espera media acumulada de los atendidos, $W_q$ (min) | $260,47 \pm 12,07$ | $316,17 \pm 16,87$ | **$263,64 \pm 15,49$** *(empate vs. E1; $-16,6\,\%$ vs. E2)* |
| *(Ref.) Espera hasta el 1.° turno en cola principal, $W_1$ (min)* | $260,47 \pm 12,07$ | $271,09 \pm 14,51$ | **$232,73 \pm 13,24$** *(−10,7 % vs. E1)* |
| Espera media sobre los 300 convocados, $W_{\text{conv}}$ (min) | $416,44 \pm 15,85$ | $421,43 \pm 14,25$ | **$359,26 \pm 13,78$** *(−13,7 % vs. E1)* |
| Cantidad media de docentes en fila, $L_q$ (docentes) | $230,96 \pm 1,34$ | $234,87 \pm 1,54$ | $234,64 \pm 1,60$ |
| Duración total de la asamblea, $T_{\text{total}}$ (min) | $541,14 \pm 21,22$ | $538,79 \pm 19,93$ | **$459,97 \pm 19,72$** *(−15,0 % vs. E1)* |
| Duración total de la asamblea, $T_{\text{total}}$ (horas) | $9,02 \pm 0,35\text{ h}$ | $8,98 \pm 0,33\text{ h}$ | **$7,67 \pm 0,33\text{ h}$** |
| Derivación a cola de reintentos (%) | No aplica (0 %) | $16,86 \pm 1,07\,\%$ | **$13,71 \pm 0,90\,\%$** |
| Cargos vacantes cubiertos (%) | $100,00 \pm 0,00\,\%$ | $100,00 \pm 0,00\,\%$ | $100,00 \pm 0,00\,\%$ |
| Docentes llamados sin oferta compatible (%) | $18,39 \pm 1,94\,\%$ | $19,10 \pm 2,66\,\%$ | $20,37 \pm 2,57\,\%$ |
| Satisfacción media de los adjudicatarios (0 a 1) | $0,590 \pm 0,004$ | $0,609 \pm 0,007$ | $0,586 \pm 0,006$ *(sin dif. sig. vs. E1)* |
| Error medio del aviso de horario, $MAE$ (min) | No aplica | **$3,77 \pm 0,15$** | $3,82 \pm 0,13$ *(sin dif. sig. vs. E2)* |
| Casos afectados en su mérito por reintento* | 0,00 % | 100 % de reintentos ($16,86 \pm 1,07\,\%$ de llamados; $26,7$ doc.) | **100 % de reintentos ($13,71 \pm 0,90\,\%$ de llamados; $21,2$ doc.)** |

> *\*Notas aclaratorias sobre tres indicadores clave de la tabla:*
> * **Por qué en E3 la espera de 1.° turno ($W_1 = 232,73\text{ min}$) cae significativo vs. E1 ($-10,7\,\%$, $p < 0,001$) mientras que la espera acumulada ($W_q = 263,64\text{ min}$) empata estadísticamente con E1 ($p = 0,628$):** En E1 nadie tiene segunda vuelta ($W_q = W_1$). En E3, el **86,3 %** de quienes llegan a mesa se atiende una sola vez y espera casi **28 minutos menos** que en E1; sin embargo, el **13,7 %** derivado a reintentos ($21,2$ docentes por corte de red o vencimiento de ventana) suma toda la espera residual hasta que se llama la ronda final al cierre del acto ($Q_i = Q_{i,1} + Q_{i,2}$), lo que compensa el ahorro en el promedio acumulado de atendidos. Aun así, E3 recorta **$W_q$ en $-52,53\text{ min}$ ($-16,6\,\%$) frente a E2**, donde el abuso de reintentos dispara $W_q$ a $316,17\text{ min}$.
> * **Afectación de mérito:** Con 300 postulantes distribuidos en especialidades con razón aproximada 3:1 frente a 100 vacantes ($c=1$), los 100 cargos se agotan siempre en la primera pasada de la cola principal (en promedio tras llamar a **133,6** docentes en E1, **158,1** en E2 y **153,7** en E3). Como la cola secundaria recién corre luego de terminar el padrón principal, el **100 % de los docentes enviados a reintento** queda desplazado por postulantes de menor puntaje. Al comparar las cifras absolutas por acto, E3 baja los afectados de **$26,70$ a $21,20$ docentes ($-20,6\,\%$, $p < 0,001$)**.
> * **Sobre la satisfacción media ($0,590$ en E1 vs. $0,586$ en E3 vs. $0,609$ en E2):** E3 mantiene estadísticamente la **misma satisfacción que el sistema actual E1 ($p = 0,120$, diferencia no significativa)** ahorrando 81 minutos de jornada. En E2 da levemente más alta ($0,609$) por un efecto colateral no deseable: muchos docentes de Caso C (60,0 por acto en E2 vs. 32,2 en E3) son expulsados por el reloj tras agotarse sus 5 opciones visibles, cediendo indirectamente cargos a postulantes más abajo de otra zona/especialidad que aún conservaban intacto su Top 5 — elevando el promedio de adjudicatarios a costa de perjudicar el mérito de 26,7 colegas.

#### Desglose estadístico completo por escenario ($n = 30, gl = 29, t_{29;\,0,975} = 2,0452$)

| Métrica | Escenario | Media $\bar{X}$ | Desvío estándar $s$ | Error estándar $s/\sqrt{30}$ | IC 95 % $[\text{Lím. Inf.} \,;\, \text{Lím. Sup.}]$ | Mínimo – Máximo (30 rép.) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$W_q$ atendidos (min)** | E1 | 260,47 | 32,33 | 5,90 | $[248,40 \,;\, 272,55]$ | 199,14 – 320,43 |
| | E2 | 316,17 | 45,18 | 8,25 | $[299,30 \,;\, 333,04]$ | 251,66 – 465,14 |
| | E3 | 263,64 | 41,49 | 7,57 | $[248,15 \,;\, 279,13]$ | 210,34 – 396,68 |
| **$W_1$ primer turno (min)** | E1 | 260,47 | 32,33 | 5,90 | $[248,40 \,;\, 272,55]$ | 199,14 – 320,43 |
| | E2 | 271,09 | 38,86 | 7,10 | $[256,57 \,;\, 285,60]$ | 226,54 – 400,21 |
| | E3 | 232,73 | 35,47 | 6,48 | $[219,49 \,;\, 245,98]$ | 185,66 – 349,83 |
| **$W_{\text{conv}}$ 300 doc. (min)** | E1 | 416,44 | 42,44 | 7,75 | $[400,59 \,;\, 432,29]$ | 359,27 – 512,41 |
| | E2 | 421,43 | 38,17 | 6,97 | $[407,18 \,;\, 435,68]$ | 359,40 – 525,55 |
| | E3 | 359,26 | 36,90 | 6,74 | $[345,48 \,;\, 373,04]$ | 298,23 – 451,63 |
| **$L_q$ (docentes)** | E1 | 230,96 | 3,58 | 0,65 | $[229,62 \,;\, 232,30]$ | 224,78 – 238,27 |
| | E2 | 234,87 | 4,11 | 0,75 | $[233,33 \,;\, 236,40]$ | 225,72 – 242,10 |
| | E3 | 234,64 | 4,30 | 0,78 | $[233,04 \,;\, 236,25]$ | 226,75 – 242,94 |
| **$T_{\text{total}}$ (min)** | E1 | 541,14 | 56,83 | 10,38 | $[519,92 \,;\, 562,36]$ | 464,84 – 679,39 |
| | E2 | 538,79 | 53,38 | 9,75 | $[518,86 \,;\, 558,73]$ | 451,18 – 683,47 |
| | E3 | 459,97 | 52,82 | 9,64 | $[440,25 \,;\, 479,69]$ | 368,26 – 595,30 |
| **% Reintentos** | E1 | 0,00 % | 0,00 % | 0,00 % | $[0,00 \,;\, 0,00]\,\%$ | 0,00 – 0,00 % |
| | E2 | 16,86 % | 2,85 % | 0,52 % | $[15,79 \,;\, 17,92]\,\%$ | 10,14 – 23,19 % |
| | E3 | 13,71 % | 2,40 % | 0,44 % | $[12,82 \,;\, 14,61]\,\%$ | 8,70 – 18,42 % |
| **Vacantes cubiertas (%)** | E1 / E2 / E3 | 100,00 % | 0,00 % | 0,00 % | $[100,00 \,;\, 100,00]\,\%$ | 100,00 – 100,00 % |
| **Sin oferta (%)** | E1 | 18,39 % | 5,20 % | 0,95 % | $[16,45 \,;\, 20,33]\,\%$ | 8,94 – 29,03 % |
| | E2 | 19,10 % | 7,11 % | 1,30 % | $[16,44 \,;\, 21,75]\,\%$ | 4,35 – 35,86 % |
| | E3 | 20,37 % | 6,90 % | 1,26 % | $[17,80 \,;\, 22,95]\,\%$ | 6,15 – 38,25 % |
| **Satisfacción (0 a 1)** | E1 | 0,590 | 0,010 | 0,002 | $[0,587 \,;\, 0,594]$ | 0,571 – 0,611 |
| | E2 | 0,609 | 0,019 | 0,003 | $[0,602 \,;\, 0,616]$ | 0,569 – 0,656 |
| | E3 | 0,586 | 0,015 | 0,003 | $[0,580 \,;\, 0,591]$ | 0,548 – 0,609 |
| **$MAE$ aviso (min)** | E2 | 3,77 | 0,41 | 0,08 | $[3,62 \,;\, 3,93]$ | 3,00 – 5,10 |
| | E3 | 3,82 | 0,35 | 0,06 | $[3,69 \,;\, 3,95]$ | 3,11 – 4,56 |
| **% Afectación mérito** | E2 | 16,86 % | 2,85 % | 0,52 % | $[15,79 \,;\, 17,92]\,\%$ | 10,14 – 23,19 % |
| *(sobre llamados)* | E3 | 13,71 % | 2,40 % | 0,44 % | $[12,82 \,;\, 14,61]\,\%$ | 8,70 – 18,42 % |
| **Docentes afectados** | E2 | 26,70 | 5,66 | 1,03 | $[24,59 \,;\, 28,81]$ | 14 – 41 doc. |
| *(cantidad por acto)* | E3 | 21,20 | 5,08 | 0,93 | $[19,30 \,;\, 23,10]$ | 12 – 34 doc. |

*(Conteo medio de tipos de atención en la cola principal: **E1** = $51,6$ Casos A y $48,4$ Casos C sobre $133,6$ llamados; **E2** = $56,2$ Casos A y $60,0$ Casos C sobre $158,1$ llamados; **E3** = $53,5$ Casos A, $25,6$ Casos B guiados y $32,2$ Casos C sobre $153,7$ llamados).*

---

### 6.3.1. Pruebas de hipótesis $t$ de Student entre escenarios (E1 vs. E2, E2 vs. E3 y E1 vs. E3)

Como diseñamos el experimento con **números aleatorios comunes sincronizados por réplica y docente** (*Common Random Numbers*, Law, 2015), la prueba estadística exacta para contrastar escenarios es la **prueba $t$ de Student para muestras pareadas** sobre las diferencias réplica a réplica $D_r = X_{A,r} - X_{B,r}$ con $n = 30$ y $gl = 29$ ($\alpha = 0,05$, bilateral). Como control de robustez calculamos también el valor-$p$ de Welch para muestras independientes:

| Comparación | Métrica | Diferencia media $\bar{D} = \bar{X}_A - \bar{X}_B$ | Variación relativa ($A \to B$) | IC 95 % de la diferencia | Estadístico $t$ ($gl=29$) | Valor-$p$ bilateral (pareado) | Valor-$p$ (Welch indep.) | ¿Significativa ($\alpha=0,05$)? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1 vs. E2** | $W_q$ atendidos (min) | $-55,70$ | **+21,38 %** (empeora) | $[-69,41 \,;\, -41,98]$ | $-8,31$ | $3,71 \times 10^{-9}$ | $1,18 \times 10^{-6}$ | **Sí** (empeora en E2) |
| **E1 vs. E2** | $W_1$ primer turno (min) | $-10,61$ | $+4,07\,\%$ | $[-23,76 \,;\, +2,53]$ | $-1,65$ | $0,1095$ | $0,2551$ | **No** |
| **E1 vs. E2** | $W_{\text{conv}}$ 300 doc. (min) | $-4,99$ | $+1,20\,\%$ | $[-17,10 \,;\, +7,12]$ | $-0,84$ | $0,4060$ | $0,6337$ | **No** |
| **E1 vs. E2** | $L_q$ (docentes) | $-3,91$ | $+1,69\,\%$ | $[-5,40 \,;\, -2,42]$ | $-5,36$ | $9,45 \times 10^{-6}$ | $2,37 \times 10^{-4}$ | **Sí** |
| **E1 vs. E2** | $T_{\text{total}}$ (min) | $+2,34$ | $-0,43\,\%$ | $[-15,50 \,;\, +20,19]$ | $+0,27$ | $0,7903$ | $0,8699$ | **No** |
| **E1 vs. E2** | Sin oferta (%) | $-0,71\text{ pp}$ | $+3,86\,\%$ | $[-3,56 \,;\, +2,14]$ | $-0,51$ | $0,6148$ | $0,6606$ | **No** |
| **E1 vs. E2** | Satisfacción (0–1) | $-0,019$ | $+3,21\,\%$ | $[-0,026 \,;\, -0,012]$ | $-5,69$ | $3,70 \times 10^{-6}$ | $1,35 \times 10^{-5}$ | **Sí** (sesgo por desplazados) |
| **E2 vs. E3** | $W_q$ atendidos (min) | $+52,53$ | **$-16,61\,\%$** | $[+45,55 \,;\, +59,52]$ | $+15,38$ | $1,75 \times 10^{-15}$ | $1,72 \times 10^{-5}$ | **Sí** ($p < 0,001$) |
| **E2 vs. E3** | $W_1$ primer turno (min) | $+38,35$ | **$-14,15\,\%$** | $[+32,45 \,;\, +44,26]$ | $+13,29$ | $7,31 \times 10^{-14}$ | $1,88 \times 10^{-4}$ | **Sí** ($p < 0,001$) |
| **E2 vs. E3** | $W_{\text{conv}}$ 300 doc. (min) | $+62,17$ | **$-14,75\,\%$** | $[+55,78 \,;\, +68,56]$ | $+19,89$ | $1,92 \times 10^{-18}$ | $2,82 \times 10^{-8}$ | **Sí** ($p < 0,001$) |
| **E2 vs. E3** | $L_q$ (docentes) | $+0,22$ | $-0,10\,\%$ | $[-0,56 \,;\, +1,01]$ | $+0,59$ | $0,5631$ | $0,8375$ | **No** |
| **E2 vs. E3** | $T_{\text{total}}$ (min) | $+78,82$ | **$-14,63\,\%$** | $[+70,83 \,;\, +86,82]$ | $+20,16$ | $1,33 \times 10^{-18}$ | $3,52 \times 10^{-7}$ | **Sí** ($p < 0,001$) |
| **E2 vs. E3** | % Reintentos | $+3,15\text{ pp}$ | **$-18,66\,\%$** | $[+2,45 \,;\, +3,85]$ | $+9,18$ | $4,38 \times 10^{-10}$ | $2,25 \times 10^{-5}$ | **Sí** ($p < 0,001$) |
| **E2 vs. E3** | Docentes afectados mérito | $+5,50\text{ doc.}$ | **$-20,60\,\%$** | $[+4,48 \,;\, +6,52]$ | $+11,05$ | $6,52 \times 10^{-12}$ | $2,10 \times 10^{-4}$ | **Sí** ($p < 0,001$) |
| **E2 vs. E3** | Sin oferta (%) | $-1,28\text{ pp}$ | $+6,68\,\%$ | $[-2,81 \,;\, +0,26]$ | $-1,70$ | $0,1006$ | $0,4835$ | **No** |
| **E2 vs. E3** | $MAE$ aviso (min) | $-0,05$ | $+1,40\,\%$ | $[-0,14 \,;\, +0,04]$ | $-1,17$ | $0,2514$ | $0,5971$ | **No** |
| **E2 vs. E3** | Satisfacción (0–1) | $+0,024$ | $-3,88\,\%$ | $[+0,016 \,;\, +0,031]$ | $+6,40$ | $5,29 \times 10^{-7}$ | $1,57 \times 10^{-6}$ | **Sí** |
| **E1 vs. E3** | $W_q$ atendidos (min) | $-3,17$ | $+1,22\,\%$ | $[-16,38 \,;\, +10,05]$ | $-0,49$ | $0,6279$ | $0,7429$ | **No** *(compensado por reintentos)* |
| **E1 vs. E3** | **$W_1$ primer turno (min)** | **$+27,74$** | **$-10,65\,\%$** | **$[+15,86 \,;\, +39,63]$** | **$+4,77$** | **$4,75 \times 10^{-5}$** | **$2,47 \times 10^{-3}$** | **Sí ($p < 0,001$)** |
| **E1 vs. E3** | **$W_{\text{conv}}$ 300 doc. (min)** | **$+57,18$** | **$-13,73\,\%$** | **$[+43,79 \,;\, +70,56]$** | **$+8,74$** | **$1,29 \times 10^{-9}$** | **$7,28 \times 10^{-7}$** | **Sí ($p < 0,001$)** |
| **E1 vs. E3** | $L_q$ (docentes) | $-3,69$ | $+1,60\,\%$ | $[-5,20 \,;\, -2,17]$ | $-4,99$ | $2,62 \times 10^{-5}$ | $6,57 \times 10^{-4}$ | **Sí** |
| **E1 vs. E3** | **$T_{\text{total}}$ (min)** | **$+81,17$** | **$-15,00\,\%$** | **$[+62,50 \,;\, +99,83]$** | **$+8,90$** | **$8,75 \times 10^{-10}$** | **$3,84 \times 10^{-7}$** | **Sí ($p < 0,001$)** |
| **E1 vs. E3** | Sin oferta (%) | $-1,99\text{ pp}$ | $+10,80\,\%$ | $[-4,88 \,;\, +0,90]$ | $-1,41$ | $0,1705$ | $0,2132$ | **No** |
| **E1 vs. E3** | Satisfacción (0–1) | $+0,005$ | $-0,79\,\%$ | $[-0,001 \,;\, +0,011]$ | $+1,60$ | $0,1196$ | $0,1654$ | **No** *(misma calidad que E1)* |

*(En las tres configuraciones la cobertura de vacantes fue exactamente del 100 % en las 30 réplicas, por lo que no hay diferencia estadística en cobertura).*

---

### 6.4. Gráficos y análisis de sensibilidad (sobre 30 réplicas por punto)

Las 4 figuras correspondientes a esta sección quedaron exportadas en PNG (300 DPI, coma decimal e IC 95 % de $t$ de Student) en `graficos/salida/` listas para incrustar en el informe:

* **Figura 1 (Comparación de escenarios):** `![Figura 1](graficos/salida/fig1_boxplot_duracion_escenarios.png)`
* **Figura 2 (Sensibilidad de ventana $\tau$):** `![Figura 2](graficos/salida/fig2_sensibilidad_ventana_tau.png)`
* **Figura 3 (Sensibilidad de comisiones $c$):** `![Figura 3](graficos/salida/fig3_sensibilidad_comisiones_c.png)`
* **Figura 4 (Adopción $p_{\text{rec}}$ y aporte Monte Carlo):** `![Figura 4](graficos/salida/fig4_adopcion_recomendador_y_montecarlo.png)`

#### 6.4.1. Experimento 2: Sensibilidad respecto de la ventana máxima de turno $\tau$ ($c = 1$)

| Escenario y ventana $\tau$ | $W_q$ atendidos (min) | $W_{\text{conv}}$ 300 doc. (min) | $L_q$ (doc.) | $T_{\text{total}}$ (min) | $T_{\text{total}}$ (h) | % Reintentos | Docentes afectados mérito | $MAE$ aviso (min) | Satisfacción (0–1) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E2 — $\tau = 6$ min** | $332,25 \pm 17,00$ ($s=45,54$) | $411,34 \pm 13,62$ ($s=36,49$) | $234,33 \pm 1,47$ | $527,01 \pm 18,83$ ($s=50,43$) | $8,78 \pm 0,31$ | $27,57 \pm 1,39\,\%$ | $49,07 \pm 3,21$ | $2,88 \pm 0,10$ | $0,633 \pm 0,007$ |
| **E2 — $\tau = 8$ min** | $323,01 \pm 17,67$ ($s=47,33$) | $417,00 \pm 14,06$ ($s=37,64$) | $234,74 \pm 1,68$ | $533,58 \pm 20,25$ ($s=54,23$) | $8,89 \pm 0,34$ | $20,92 \pm 1,06\,\%$ | $34,77 \pm 2,52$ | $3,32 \pm 0,14$ | $0,618 \pm 0,007$ |
| **E2 — $\tau = 10$ min** | $316,17 \pm 16,87$ ($s=45,18$) | $421,43 \pm 14,25$ ($s=38,17$) | $234,87 \pm 1,54$ | $538,79 \pm 19,93$ ($s=53,38$) | $8,98 \pm 0,33$ | $16,86 \pm 1,07\,\%$ | $26,70 \pm 2,11$ | $3,77 \pm 0,15$ | $0,609 \pm 0,007$ |
| **E2 — $\tau = 12$ min** | $302,58 \pm 13,07$ ($s=34,99$) | $418,85 \pm 12,72$ ($s=34,05$) | $235,55 \pm 1,45$ | $533,71 \pm 17,02$ ($s=45,59$) | $8,90 \pm 0,28$ | $13,96 \pm 1,03\,\%$ | $20,90 \pm 1,77$ | $4,16 \pm 0,18$ | $0,602 \pm 0,006$ |
| **E2 — $\tau = 15$ min** | $296,84 \pm 14,41$ ($s=38,59$) | $422,45 \pm 14,18$ ($s=37,96$) | $235,83 \pm 1,36$ | $537,76 \pm 19,31$ ($s=51,71$) | $8,96 \pm 0,32$ | $11,68 \pm 0,90\,\%$ | $16,90 \pm 1,62$ | $4,50 \pm 0,22$ | $0,597 \pm 0,005$ |
| **E3 — $\tau = 6$ min** | $280,37 \pm 15,27$ ($s=40,91$) | $356,76 \pm 12,10$ ($s=32,39$) | $234,75 \pm 1,77$ | $456,57 \pm 17,79$ ($s=47,63$) | $7,61 \pm 0,30$ | $22,83 \pm 1,15\,\%$ | $38,73 \pm 2,74$ | $3,03 \pm 0,12$ | $0,594 \pm 0,006$ |
| **E3 — $\tau = 8$ min** | $270,71 \pm 17,07$ ($s=45,72$) | $357,82 \pm 14,32$ ($s=38,34$) | $234,67 \pm 1,92$ | $458,26 \pm 20,90$ ($s=55,97$) | $7,64 \pm 0,35$ | $16,96 \pm 1,25\,\%$ | $27,30 \pm 2,64$ | $3,45 \pm 0,14$ | $0,588 \pm 0,005$ |
| **E3 — $\tau = 10$ min** | $263,64 \pm 15,49$ ($s=41,49$) | $359,26 \pm 13,78$ ($s=36,90$) | $234,64 \pm 1,60$ | $459,97 \pm 19,72$ ($s=52,82$) | $7,67 \pm 0,33$ | $13,71 \pm 0,90\,\%$ | $21,20 \pm 1,90$ | $3,82 \pm 0,13$ | $0,586 \pm 0,006$ |
| **E3 — $\tau = 12$ min** | $253,98 \pm 11,43$ ($s=30,61$) | $355,24 \pm 11,37$ ($s=30,45$) | $235,53 \pm 1,59$ | $452,80 \pm 15,49$ ($s=41,49$) | $7,55 \pm 0,26$ | $11,53 \pm 0,97\,\%$ | $17,03 \pm 1,65$ | $4,13 \pm 0,14$ | $0,584 \pm 0,006$ |
| **E3 — $\tau = 15$ min** | **$246,67 \pm 11,77$** ($s=31,52$) | **$355,24 \pm 12,83$** ($s=34,35$) | $236,31 \pm 1,48$ | **$451,33 \pm 17,47$** ($s=46,79$) | **$7,52 \pm 0,29$** | **$9,92 \pm 1,03\,\%$** | **$14,03 \pm 1,62$** | $4,41 \pm 0,18$ | $0,581 \pm 0,005$ |

* **Hallazgo clave sobre $\tau$:** Con las 40 escuelas filtradas estrictamente por nivel edilicio, observamos un resultado muy revelador: ni en E2 ni en E3 recortar agresivamente el reloj ($\tau = 6$ o $8$ minutos) logra acelerar la jornada ($T_{\text{total}}$ queda prácticamente plano alrededor de ~527–539 min en E2 y ~451–460 min en E3, con $W_{\text{conv}} \approx 355\text{–}359\text{ min}$), **pero sí castiga fuertemente el mérito**, disparando los docentes desplazados hasta **$38,73$ en E3** y **$49,07$ en E2**. En cambio, **a medida que $\tau$ crece hacia $12\text{ o }15$ minutos en E3**, se permite que quienes ya están decidiendo entre las sugerencias cierren su elección sin pasar innecesariamente a segunda ronda: los reintentos bajan hasta **$9,92\,\%$** ($14,03$ afectados, apenas $+1,9\text{ pp}$ por encima del piso técnico inevitable del $8\,\%$ de caídas de red), **$W_q$ desciende por debajo de E1 ($246,67\text{ min}$ frente a $260,47$)** y **$T_{\text{total}}$ alcanza su mínimo en $\tau = 15$ min ($451,33\text{ min} = 7,52\text{ h}$)**, con la sola contrapartida leve de elevar el error de aviso $MAE$ de $3,82$ a $4,41\text{ min}$. Por eso, para implementar en Salta resulta incluso más conveniente fijar **$\tau = 12$ a $15$ minutos dentro de E3** que $\tau = 10$.

#### 6.4.2. Experimento 3: Sensibilidad respecto de la cantidad de comisiones simultáneas $c$ ($\tau = 10$ min)

| Escenario y mesas $c$ | $W_q$ atendidos (min) | $W_{\text{conv}}$ 300 doc. (min) | $L_q$ (doc.) | $T_{\text{total}}$ (min) | $T_{\text{total}}$ (h) | % Reintentos | % Afectación mérito | $MAE$ aviso (min) | Satisfacción (0–1) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1 — $c = 1$** | $260,47 \pm 12,07$ ($s=32,33$) | $416,44 \pm 15,85$ ($s=42,44$) | $230,96 \pm 1,34$ | $541,14 \pm 21,22$ ($s=56,83$) | $9,02 \pm 0,35$ | 0,00 % | 0,00 % | — | $0,590 \pm 0,004$ |
| **E1 — $c = 2$** | $132,00 \pm 5,54$ ($s=14,84$) | $208,85 \pm 7,63$ ($s=20,43$) | $228,28 \pm 1,53$ | $274,59 \pm 10,35$ ($s=27,72$) | $4,58 \pm 0,17$ | 0,00 % | 0,00 % | — | $0,594 \pm 0,004$ |
| **E1 — $c = 3$** | $88,83 \pm 3,79$ ($s=10,14$) | $140,28 \pm 5,08$ ($s=13,60$) | $225,85 \pm 1,58$ | $186,44 \pm 7,07$ ($s=18,93$) | $3,11 \pm 0,12$ | 0,00 % | 0,00 % | — | $0,596 \pm 0,004$ |
| **E2 — $c = 1$** | $316,17 \pm 16,87$ ($s=45,18$) | $421,43 \pm 14,25$ ($s=38,17$) | $234,87 \pm 1,54$ | $538,79 \pm 19,93$ ($s=53,38$) | $8,98 \pm 0,33$ | $16,86 \pm 1,07\,\%$ | $16,86 \pm 1,07\,\%$ | $3,77 \pm 0,15$ | $0,609 \pm 0,007$ |
| **E2 — $c = 2$** | $158,38 \pm 8,49$ ($s=22,73$) | $209,61 \pm 7,22$ ($s=19,34$) | $232,96 \pm 1,59$ | $270,22 \pm 10,32$ ($s=27,64$) | $4,50 \pm 0,17$ | $16,35 \pm 1,04\,\%$ | $16,12 \pm 1,02\,\%$ | $3,44 \pm 0,17$ | $0,611 \pm 0,007$ |
| **E2 — $c = 3$** | $105,04 \pm 5,48$ ($s=14,67$) | $138,65 \pm 4,60$ ($s=12,31$) | $231,12 \pm 1,74$ | $180,19 \pm 6,75$ ($s=18,09$) | $3,00 \pm 0,11$ | $15,92 \pm 1,02\,\%$ | $15,54 \pm 1,02\,\%$ | $3,57 \pm 0,21$ | $0,613 \pm 0,006$ |
| **E3 — $c = 1$** | $263,64 \pm 15,49$ ($s=41,49$) | $359,26 \pm 13,78$ ($s=36,90$) | $234,64 \pm 1,60$ | $459,97 \pm 19,72$ ($s=52,82$) | $7,67 \pm 0,33$ | $13,71 \pm 0,90\,\%$ | $13,71 \pm 0,90\,\%$ | $3,82 \pm 0,13$ | $0,586 \pm 0,006$ |
| **E3 — $c = 2$** | **$131,68 \pm 7,34$** ($s=19,65$) | **$179,08 \pm 6,58$** ($s=17,61$) | $232,66 \pm 1,67$ | **$231,26 \pm 9,65$** ($s=25,83$) | **$3,85 \pm 0,16$** | $13,34 \pm 0,93\,\%$ | $13,14 \pm 0,94\,\%$ | $3,52 \pm 0,16$ | $0,587 \pm 0,005$ |
| **E3 — $c = 3$** | **$87,74 \pm 4,68$** ($s=12,53$) | **$118,98 \pm 4,11$** ($s=11,00$) | $230,87 \pm 1,76$ | **$154,86 \pm 6,22$** ($s=16,65$) | **$2,58 \pm 0,10$** | $13,01 \pm 0,84\,\%$ | $12,53 \pm 0,87\,\%$ | $3,53 \pm 0,17$ | $0,587 \pm 0,005$ |

* **Hallazgo clave sobre $c$:** Al habilitar una segunda comisión en E3 ($c = 2$), la duración completa de la asamblea cae de **$7,67$ horas a $3,85$ horas** ($231,26\text{ min}$, siendo la única configuración con $c = 2$ que baja por debajo de la línea de media jornada de 4 horas, frente a $4,58\text{ h}$ de E1 y $4,50\text{ h}$ de E2), y con $c = 3$ desciende a **$2,58$ horas** ($154,86\text{ min}$). Además, en todos los niveles de $c$, el Escenario 3 mantiene una ventaja sostenida del **15,0 % al 16,9 %** menos duración total que E1.

#### 6.4.3. Experimento 4: Sensibilidad respecto de la adopción del recomendador ($p_{\text{rec}}$) y aporte del pronóstico Monte Carlo en E3 ($c = 1, \tau = 10$ min)

| Configuración evaluada en E3 | Casos B por acto | $W_q$ atendidos (min) | $W_{\text{conv}}$ 300 doc. (min) | $T_{\text{total}}$ (min) | $T_{\text{total}}$ (h) | % Reintentos | Docentes afectados mérito | Satisfacción (0–1) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E3 con $p_{\text{rec}} = 0,30$** (adopción baja) | $12,0 \pm 1,2$ | $291,56 \pm 16,69$ ($s=44,70$) | $392,91 \pm 15,31$ ($s=41,01$) | $502,54 \pm 21,44$ ($s=57,42$) | $8,38 \pm 0,36$ | $15,43 \pm 1,05\,\%$ | $24,10 \pm 2,04$ | $0,597 \pm 0,007$ |
| **E3 con $p_{\text{rec}} = 0,50$** (adopción media) | $19,0 \pm 1,2$ | $275,68 \pm 15,78$ ($s=42,25$) | $373,72 \pm 14,41$ ($s=38,60$) | $478,03 \pm 20,63$ ($s=55,24$) | $7,97 \pm 0,34$ | $14,41 \pm 0,95\,\%$ | $22,37 \pm 1,96$ | $0,594 \pm 0,006$ |
| **E3 con $p_{\text{rec}} = 0,70$** (caso base, con MC) | $25,6 \pm 1,3$ | **$263,64 \pm 15,49$** ($s=41,49$) | **$359,26 \pm 13,78$** ($s=36,90$) | **$459,97 \pm 19,72$** ($s=52,82$) | **$7,67 \pm 0,33$** | **$13,71 \pm 0,90\,\%$** | **$21,20 \pm 1,90$** | $0,586 \pm 0,006$ |
| **E3 con $p_{\text{rec}} = 0,90$** (adopción alta) | $33,2 \pm 1,3$ | $244,53 \pm 12,14$ ($s=32,51$) | $337,11 \pm 11,56$ ($s=30,95$) | $430,30 \pm 15,98$ ($s=42,79$) | $7,17 \pm 0,27$ | $12,61 \pm 0,91\,\%$ | $19,07 \pm 1,69$ | $0,579 \pm 0,005$ |
| *Ablación:* **E3 sin Monte Carlo** ($R_{\text{MC}}=0, p_{\text{rec}}=0,70$) | $25,7 \pm 1,3$ | $264,04 \pm 15,49$ ($s=41,48$) | $359,95 \pm 13,80$ ($s=36,95$) | $460,95 \pm 19,77$ ($s=52,95$) | $7,68 \pm 0,33$ | $13,78 \pm 0,89\,\%$ | $21,30 \pm 1,89$ | $0,584 \pm 0,005$ |

* **Hallazgo clave sobre $p_{\text{rec}}$ y el aporte específico de Monte Carlo:**
  1. **Robustez frente a baja adopción:** Incluso en el escenario pesimista donde apenas el 30 % de los docentes sin vacantes iniciales sigue las alternativas sugeridas ($p_{\text{rec}} = 0,30$), E3 ya recorta la duración total de la jornada en **38,6 minutos respecto de E1** ($502,54$ vs. $541,14\text{ min}$, $-7,1\,\%$) y en **36,3 minutos respecto de E2** ($502,54$ vs. $538,79\text{ min}$). Con adopción alta ($p_{\text{rec}} = 0,90$), la jornada baja a **$430,30\text{ min}$ ($7,17\text{ h}$, $-20,5\,\%$ respecto de E1)**.
  2. **Qué aporta el recomendador vs. qué aporta Monte Carlo (lectura honesta de la ablación):** Al aislar ambos módulos comparando E3 con $R_{\text{MC}} = 200$ frente a E3 con $R_{\text{MC}} = 0$, comprobamos con claridad que casi todo el ahorro de duración y reintentos frente a E2 ($-77,8\text{ min}$ sin MC y $-78,8\text{ min}$ con MC) proviene de **tener precarga de listas + recomendador multicriterio**. Las diferencias en tiempos y reintentos imputables únicamente a Monte Carlo ($460,95 \to 459,97\text{ min}$, $-0,98\text{ min}$, $p = 0,151$) no resultaron estadísticamente significativas en este padrón depurado porque cada docente tiene en promedio 13,4 alternativas válidas; en cambio, el aporte estadísticamente significativo de Monte Carlo apareció en la **precisión del aviso previo ($MSE$ cae un $-71,3\,\%$, $p < 10^{-25}$)** y en la **satisfacción media de los adjudicatarios** ($0,584 \to 0,586$, $t = -2,41$, $p = 0,023$), ya que evita recomendar en el Top 3 escuelas cuya única vacante va a desaparecer en los próximos 2 a 5 turnos.

---

## 7. ANÁLISIS INTEGRADOR Y REFLEXIÓN DEL EXPERIMENTO

Al analizar en conjunto las corridas de los tres escenarios sobre el padrón verificado de Salta Capital, hubo varias cosas que nos sorprendieron con respecto a la intuición que teníamos antes de programar el simulador y que nos ayudaron a conectar la teoría de colas vista en la materia con lo que pasa en un acto público real:

### 1. ¿Cuál escenario funcionó mejor y por qué E2 por sí solo se quedó corto?
Sin dudas **el escenario que mejor funcionó fue el Escenario 3 (E3)**. Antes de correr las 30 réplicas, pensábamos que el simple hecho de poner un tope de reloj de $\tau = 10$ minutos en el Escenario 2 ya iba a recortar bastante la jornada y las esperas. Sin embargo, los datos nos dieron una lección clarísima: **en E2 la duración total prácticamente no se movió ($538,79$ vs. $541,14\text{ min}$ en E1; $p = 0,790$, no significativa), la espera sobre los 300 convocados tampoco cambió ($p = 0,406$), y la espera acumulada de quienes fueron llamados ($W_q$) empeoró un 21,4 %** (subió de $260,47$ a $316,17\text{ min}$, $p < 0,001$).

Revisando qué ocurría paso a paso dentro de cada réplica entendimos la causa física de ese resultado:
* En una asamblea con cupo fijo de 100 cargos, el acto **no termina a una hora prefijada, sino recién cuando se adjudican las 100 vacantes**. Cuando en E2 un docente llega desorientado sin vacantes en su lista (Caso C, promedio $60,0$ por acto), consume los 10 minutos completos frente a la mesa y el reloj le corta el turno sin elegir cargo: **esos 10 minutos de servidor se perdieron igual pero cubrieron 0 vacantes**. Para lograr cubrir ese puesto libre, la mesa tiene que llamar a más docentes hacia abajo en el padrón ($158,1$ llamados en E2 frente a $133,6$ en E1), que también suelen estar desorientados.
* Además, los ~$26,7$ docentes derivados a reintento en E2 suman a su espera inicial toda la demora restante hasta la ronda final ($Q_i = Q_{i,1} + Q_{i,2}$), disparando el promedio $W_q$.
* Recién al pasar a **E3**, cuando al aviso de 10 minutos antes le sumamos el semáforo de disponibilidad y 3 escuelas compatibles sugeridas, atacamos el verdadero cuello de botella del sistema: **aumentamos la tasa efectiva de servicio $\mu$** convirtiendo búsquedas largas desde cero (Caso C baja casi a la mitad, de $60,0$ a $32,2$) en elecciones pre-pensadas (Caso B = $25,6$ docentes). Ahí sí el acto se acorta **81,2 minutos ($459,97\text{ min} = 7,67\text{ h}$, $-15,0\,\%$, $p < 0,001$)**, $W_{\text{conv}}$ cae un **$-13,7\,\%$** ($-57,2\text{ min}$), la espera hasta el primer turno ($W_1$) baja un **$-10,7\,\%$** ($232,73\text{ min}$) y los reintentos bajan un **$-18,7\,\%$** respecto de E2. Lo valioso que sí aporta E2 (y E3 conserva) es eliminar la incertidumbre horaria mediante el estimador exponencial ($\alpha = 0,20$), logrando un error medio muy razonable de $MAE \approx 3,8\text{ min}$.

### 2. El balance delicado entre achicar la espera y no perjudicar el orden de mérito
Uno de los aprendizajes más importantes del trabajo apareció al observar el costo real de la cola de reintentos sobre el orden de mérito. En los papeles sonaba completamente justo plantear *"si alguien se pasa de $\tau$ o se le corta internet, pasa a reintentos conservando su puntaje"*. Pero al simular 300 docentes para 100 vacantes vimos dos efectos concretos:
1. **Desplazamiento del mérito al cierre de la ronda principal:** Como la relación postulantes/vacantes ronda 3:1 en todas las especialidades, las 100 vacantes se agotan siempre cerca de mitad de tabla (alrededor del puesto 134–158). Al abrirse la cola de reintentos recién tras llamar a los 300 inscriptos, el **100 % de los docentes enviados a reintento** se encuentra sin cargos disponibles de su especialidad mientras otros de menor puntaje sí adjudicaron. Por esa misma razón, en E3 la espera acumulada $W_q$ de los atendidos empata estadísticamente con E1 ($263,64$ vs. $260,47\text{ min}$, $p = 0,628$), aunque casi el 86 % espere mucho menos en su primer turno ($232,73\text{ min}$).
2. **Qué nos enseñó el análisis de $\tau$ sobre cómo proteger mejor el mérito:** Al verificar estrictamente la compatibilidad edilicia por nivel, descubrimos que achicar $\tau$ a 6 u 8 minutos no ahorra prácticamente nada de tiempo total, pero deja desplazados a **$38,7$ docentes por acto** en E3 ($49,1$ en E2). Por el contrario, **subir la ventana de E3 a $\tau = 12$ o $15$ minutos** baja los afectados a **$17,0$ y $14,0$ docentes** (acercándose muchísimo al piso técnico inevitable del $8\,\%$ de desconexiones), reduce además la espera acumulada $W_q$ por debajo de E1 ($254,0$ y $246,7\text{ min}$) y sostiene la jornada en **$\approx 7,52\text{–}7,55$ horas**.
3. **Propuesta reglamentaria surgida del experimento:** Para eliminar el desplazamiento injusto de quienes sufren una caída involuntaria de red, en una implementación real convendría **reinsertar al docente apenas $k = 5$ o $10$ puestos más abajo dentro de la misma ronda principal** (o reservarle una ventana corta de reconexión), en lugar de mandarlo al final después del puesto 300.

### 3. Cosas que nos llamaron la atención frente a la teoría de colas vista en clase
1. **Por qué $L_q$ subió ligeramente de $230,96$ (E1) a $234,64$ (E3) cuando E3 duró 81 minutos menos:** Al principio nos desconcertó ver que bajar la duración de la asamblea en un 15 % aumentaba levemente $L_q$. Al aplicar la versión de horizonte finito de la Ley de Little lo entendimos al instante:
   $$L_q = \frac{300 \cdot W_{\text{conv}}}{T_{\text{total}}}$$
   Como los 300 docentes están esperando desde $t = 0$ y la asamblea termina apenas se asignan las 100 vacantes (cuando aún queda casi medio padrón sin ser llamado), tanto el numerador ($W_{\text{conv}}$, $-13,7\,\%$) como el denominador ($T_{\text{total}}$, $-15,0\,\%$) bajan casi en idéntica proporción; como $T_{\text{total}}$ cayó un poquito más que $W_{\text{conv}}$, el cociente $L_q$ creció apenas un $1,6\,\%$. Es una diferencia conceptual fuerte frente a los modelos estacionarios abiertos ($M/M/1$), donde $\lambda$ es constante y bajar $W_q$ reduce proporcionalmente $L_q$.
2. **Diferencia entre sumar servidores en $M/M/c$ abierto vs. en una asamblea cerrada:** En la verificación teórica vimos que pasar de $M/M/1$ a $M/M/2$ con $\lambda = 2, \mu = 3$ reducía $W_q$ **16 veces** ($0,6644\text{ h} \to 0,0418\text{ h}$) porque el sistema pasaba a estar ocioso la mitad del tiempo ($P_0 = 0,50$). En cambio, en la asamblea con 300 inscriptos presentes en $t = 0$, las mesas operan al **100 % de ocupación continua ($P_0 = 0$)** desde el minuto cero hasta adjudicar la última vacante; por eso pasar de $c = 1$ a $c = 2$ y $c = 3$ divide $T_{\text{total}}$ de forma casi lineal ($1/c$: $460,0 \to 231,3 \to 154,9\text{ min}$ en E3). De todas formas el impacto práctico es contundente: **E3 con $c = 2$ comisiones ($3,85\text{ h}$)** resuelve en un único turno matutino una asamblea que hoy lleva 9 horas.

### 4. Limitaciones que reconocemos en nuestro modelo
Siendo honestos con el alcance del experimento, hay varios supuestos que simplifican la realidad y conviene tener presentes:
* **Parámetros comportamentales sintéticos:** Aunque trabajamos con 40 edificios reales verificados del Departamento Capital y sus coordenadas e instituciones por nivel, no hay cronometrajes públicos oficiales de cuánto tarda cada docente frente a mesa ni encuestas históricas de preferencias. Los multiplicadores ($\times 2$ en Caso B y $\times 4$ en Caso C), la dispersión log-normal ($\sigma = 0,8$), la tasa de desconexión ($p = 0,08$) y la adopción ($p_{\text{rec}} = 0,70$) son supuestos razonables para contrastar estrategias, pero los tiempos absolutos deben leerse como **órdenes de magnitud comparativos** entre E1, E2 y E3.
* **Recomendador evaluado sobre preferencias generadas y peso de Monte Carlo:** La grilla logró un *Hit Rate@1* del $69,67\,\%$ (+95 % sobre el azar en $K_i$) y un *Hit Rate@3* del $97,33\,\%$, validando la coherencia del puntaje multicriterio frente a datos sintéticos de cercanía, turno y afinidad; con postulantes reales seguramente influirían otros factores (líneas de SAETA específicas, compatibilidad con otros cargos o clima institucional). Además, en la ablación observamos que el ahorro grueso de tiempo viene de la dupla precarga + recomendador, mientras que Monte Carlo brilla reduciendo un **71,3 % el error de disponibilidad** y sosteniendo la **satisfacción de adjudicación** ($p = 0,023$).
* **Cargos indivisibles vs. horas cátedra de Secundaria:** Respetamos qué edificios corresponden a Nivel Inicial/Primario (24 escuelas) y cuáles a Nivel Secundario (16 colegios), pero modelamos cada vacante secundaria también como un cargo unitario por docente. En un sistema productivo para Nivel Secundario habría que agregar control de incompatibilidad horaria por módulos de horas cátedra repartidos entre distintos colegios.

---

## 8. Punto 4 de CONCLUSIONES *(listo para pegar en la línea 596 del informe)*

> 4. En las 30 réplicas ejecutadas sobre el caso representativo verificado de Salta Capital ($N = 300$ docentes, $V_{\text{tot}} = 100$ vacantes y $E_{\text{tot}} = 40$ escuelas públicas reales diferenciadas por nivel edilicio), se comprobó mediante pruebas $t$ de Student pareadas ($gl = 29$) que aplicar únicamente el límite de tiempo $\tau = 10$ minutos (E2) no produce mejoras significativas en la duración total de la jornada ($538,79 \pm 19,93\text{ min}$ frente a $541,14 \pm 21,22\text{ min}$ en E1; $-0,4\,\%$, $p = 0,790$) ni en la espera general del padrón ($W_{\text{conv}} = 421,43\text{ min}$, $p = 0,406$), y en cambio incrementa significativamente un **21,4 %** la espera acumulada de quienes son llamados ($W_q = 316,17 \pm 16,87\text{ min}$; $p < 0,001$) debido a la doble espera de los $26,7$ postulantes derivados a reintento. Por el contrario, el sistema asistido con precarga, recomendador calibrado (*Hit Rate@3* = 97,33 % y *Hit Rate@1* = 69,67 %, casi el doble que el azar) y pronóstico Monte Carlo ($MSE = 0,0147$, un 71,3 % menor que sin pronóstico) del **Escenario 3 (E3)** logra mejoras estadísticamente muy significativas ($p < 0,001$): recorta un **15,0 %** la duración total de la asamblea hasta **$459,97 \pm 19,72\text{ min}$ ($7,67 \pm 0,33\text{ h}$, ahorrando 81,2 minutos)**, disminuye un **13,7 %** la espera media sobre los 300 convocados ($359,26 \pm 13,78\text{ min}$), baja un **10,7 %** la espera hasta el primer turno ($232,73 \pm 13,24\text{ min}$) y mantiene la espera acumulada $W_q$ ($263,64 \pm 15,49\text{ min}$) estadísticamente igual a E1 ($p = 0,628$) y un **16,6 % inferior a E2** ($p < 0,001$), con idéntico nivel de satisfacción que el sistema actual ($p = 0,120$). Además, E3 baja los reintentos del **16,86 % al 13,71 %** ($-18,7\,\%$) y reduce un **20,6 %** la afectación de mérito (de $26,70$ a $21,20$ docentes desplazados por acto). A partir del análisis de sensibilidad, se recomienda operar con **E3 extendiendo la ventana a $\tau = 12$ o $15$ minutos** (donde $T_{\text{total}}$ baja levemente a $451\text{–}453\text{ min}$, $W_q$ cae por debajo de E1 hasta $246,67\text{ min}$ y los afectados en su mérito se reducen a $14\text{–}17$ docentes, cerca del piso del 8 % de desconexiones) y, cuando exista disponibilidad administrativa, desdoblar la atención por nivel/especialidad en **$c = 2$ comisiones simultáneas**, resolviendo la jornada completa en **$3,85 \pm 0,16\text{ horas}$ ($231,26\text{ min}$)** dentro de un único turno matutino.

---

## Anexo Rápido: Cómo volver a correr simulaciones y gráficos

Todo el proyecto separa el motor de simulación (Python 3 estándar sin dependencias externas) del módulo de visualización (`pandas` + `matplotlib` en `graficos/`):

```powershell
# 1. Regenerar data/escuelas.csv, data/cargos.csv y data/docentes.csv (semilla = 2026)
python -m src.generar_datos

# 2. Ejecutar todas las validaciones, las 30 réplicas de E1/E2/E3 y todas las sensibilidades
#    (guarda todo en data/resultados_experimentos.json y data/replicas_principales.csv)
python -m src.correr_experimentos

# 3. Regenerar las 4 figuras en 300 DPI desde graficos/salida/ usando el entorno virtual con pandas
.\.venv\Scripts\python.exe graficos\generar_graficos.py
```
