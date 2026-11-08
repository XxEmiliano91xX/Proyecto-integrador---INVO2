### Registros de dudas

> **Fecha:**
> [YYYY-MM-DD].
> **Persona:**
> Emiliano o Pablo
>
> **Titulo:**
> Titulo corto que resuma la informacion.
>
> **Asunto:**
> Descripción clara y concreta de la duda, observacion u otra cosa.
>
> **Respuesta:**
> _(Completar cuando se resuelva)_

---

> **Fecha:**
> 2026-11-05.
> **Persona:**
    Pablo
>
> **Titulo:**
> Explicación intuitiva de conceptos clave del informe (`v3`)
>
> **Asunto:**
> Repaso con ejemplos del propio informe sobre: caso representativo vs. $n > 30$ (30 réplicas), simulación Monte Carlo, análisis de sensibilidad, lista de eventos futuros (FEL y `heapq`), período de calentamiento (*warm-up*), prioridad no apropiativa, distribución log-normal y suavización exponencial simple.

**Respuesta:**

¡Dale! Te explico cada concepto con ejemplos de tu propio informe. Son conceptos bastante intuitivos una vez que se les ve la lógica.

---

## 1. ¿Qué significa "caso representativo"? ¿Tiene que ver con n > 30?

**No, no tiene que ver con el n > 30.** Son dos ideas distintas:

- **Caso representativo** significa que elegiste un *ejemplo concreto y manejable* que se parece lo suficiente a la realidad como para que lo que aprendas de él sirva para el problema general. Tu caso (300 docentes, 100 cargos, 40 escuelas, Salta Capital) no es *todas* las asambleas de la provincia, pero tiene sus características típicas: más postulantes que cargos, orden por puntaje, escuelas repartidas por zonas, etc. Si el sistema funciona bien ahí, hay razones para pensar que funcionaría en casos parecidos.
- **n > 30** es una regla práctica de estadística sobre el *tamaño de muestra*: con más de ~30 observaciones, la media muestral se aproxima bien a una normal (Teorema Central del Límite).

Donde sí aparece el 30 en tu informe es en las **30 réplicas**: corrés la simulación 30 veces con distintas semillas aleatorias. Ahí sí hay una lógica parecida a la de estadística: con 30 réplicas podés calcular promedios e intervalos de confianza razonablemente confiables. Pero las 30 réplicas son *cuántas veces repetís el experimento*, no *qué tan representativo es el caso*.

---

## 2. ¿Qué es Monte Carlo?

Es una forma de **estimar una probabilidad repitiendo muchas veces un experimento aleatorio en la computadora** y contando qué fracción de veces pasó lo que te interesa.

**Ejemplo simple:** querés saber la probabilidad de sacar suma 7 con dos dados. Podrías hacer la cuenta matemática, o podrías tirar los dados virtualmente 10.000 veces y contar cuántas veces dio 7. Si dio 1.670 veces, estimás ~16,7 %. (La respuesta exacta es 1/6 ≈ 16,67 %.)

**En tu informe (sección 3.5.3):** faltan 10 minutos para el turno de un docente y hay 2 a 5 docentes delante. No sabés exactamente qué van a elegir, porque hay azar (¿se desconecta?, ¿tarda más de 10 min?, ¿qué escuela elige?). Entonces:

1. Simulás 200 veces cómo les va a esos docentes de adelante.
2. En cada pasada anotás si la escuela X llegó con vacante libre al turno del docente.
3. Si en 150 de las 200 pasadas seguía libre, estimás una **probabilidad de 150/200 = 75 %** de que siga disponible.

Esa probabilidad es el "semáforo" que se le muestra al docente. La ventaja es que no necesitás una fórmula complicada: simulás y contás.

---

## 3. ¿Qué es un análisis de sensibilidad?

Es **cambiar un parámetro a la vez y ver cuánto cambian los resultados**, para saber qué tan dependientes son tus conclusiones de los valores que supusiste.

Pensalo así: vos *supusiste* que $\tau = 10$ minutos, que $p_{\text{rec}} = 0{,}70$ (70 % sigue la recomendación), etc. Pero esos números no son datos medidos, son supuestos razonables. La pregunta honesta es: **¿y si me equivoqué?**

Por eso en tu Experimento 2 probás $\tau \in \{6, 8, 10, 12, 15\}$ y en el Experimento 4 probás $p_{\text{rec}} \in \{0{,}3;\ 0{,}5;\ 0{,}7;\ 0{,}9\}$. Si E3 es mejor que E1 incluso cuando solo el 30 % sigue la recomendación, tu conclusión es **robusta**. Si solo es mejor cuando el 90 % la sigue, tu conclusión es **frágil** y hay que decirlo.

---

## 4. Lista de eventos futuros (FEL)

En una simulación de eventos discretos, el sistema **solo cambia en momentos puntuales** (alguien empieza su turno, alguien confirma un cargo, se vence el tiempo límite). Entre eventos no pasa nada, así que no tiene sentido simular segundo a segundo.

La **FEL (Future Event List)** es una "agenda" ordenada de los eventos que ya están programados para ocurrir, del más próximo al más lejano. El programa hace esto en loop:

1. Saca de la agenda el evento más próximo.
2. **Salta el reloj** directamente a la hora de ese evento.
3. Ejecuta el evento (actualiza el estado) y, si corresponde, **agenda nuevos eventos**.
4. Repite.

**Ejemplo con tu asamblea:**

| Reloj | Evento sacado de la FEL | Qué pasa | Se agenda |
| :-: | :-- | :-- | :-- |
| 0,0 | Inicio turno D001 | Sortea que tarda 1,8 min | Fin turno D001 en t=1,8 |
| 1,8 | Fin turno D001 | Asigna cargo, mesa libre | Inicio turno D002 en t=1,8 |
| 1,8 | Inicio turno D002 | Sortea que tarda 14 min, pero τ=10 | Vence ventana en t=11,8 |
| 11,8 | Vence ventana D002 | Pasa a reintentos | Inicio turno D003 en t=11,8 |

Fijate que el reloj saltó de 1,8 a 11,8 sin simular los 10 minutos intermedios. Eso es lo que hace eficiente a la simulación.

**¿Por qué `heapq`?** Es la estructura de Python que mantiene una lista siempre ordenada de forma eficiente: sacar el mínimo (el evento más próximo) es muy rápido aunque haya miles de eventos. Se le llama "cola de prioridad".

---

## 5. Período de calentamiento (*warm-up*)

Cuando simulás un sistema que **empieza vacío** pero que en la realidad funciona de forma continua (un banco, una guardia de hospital), los primeros minutos de simulación no son representativos: la fila arranca en cero, algo que casi nunca pasa en el "régimen normal". Entonces se **descartan los primeros datos** (el calentamiento) para medir solo cuando el sistema ya se estabilizó.

**En tu informe aparece en dos lugares, con tratamientos opuestos:**

- **Verificación M/M/1 (sección 5.1):** sí lo usás. Descartás los primeros 10.000 clientes porque ahí querés comparar contra la fórmula de régimen estacionario, y esa fórmula supone que el sistema ya "se estabilizó".
- **Asamblea docente (sección 2.4):** **no** lo usás, y tiene lógica: la asamblea *realmente* empieza con los 300 docentes esperando y termina cuando se cubren los cargos. Ese arranque "desde cero" **es parte del fenómeno que querés medir**, no un artefacto. Descartarlo sería borrar justo lo que te interesa.

---

## 6. ¿Por qué "prioridad no apropiativa"?

Hay dos ideas en la frase:

- **Prioridad:** se atiende primero al de mayor puntaje $P_i$ (no es FIFO por orden de llegada).
- **No apropiativa (*non-preemptive*):** una vez que alguien **empezó** a ser atendido, **nadie lo puede desplazar**, ni siquiera alguien con mayor prioridad.

**Analogía:** estás en el médico y pasás a consultorio. Si llega alguien con una urgencia más grave (más prioridad), en un sistema *apropiativo* te sacarían a mitad de consulta para atenderlo. En uno *no apropiativo*, esa persona espera a que termines.

En tu caso: como el orden se define de antemano por puntaje y todos están desde el inicio, nunca llega alguien con más puntaje *después* de que otro empezó. Pero igual la palabra aplica porque describe la regla: el docente que está eligiendo no puede ser interrumpido hasta que confirme o se cumpla su $\tau$. (Ojo: el tope $\tau$ no es "apropiación" por parte de otro docente, es un límite de tiempo del propio turno.)

---

## 7. Distribución log-normal

Una variable es **log-normal** si su **logaritmo** sigue una distribución normal. Dicho más práctico: es una distribución para cosas que **no pueden ser negativas** y que tienen **cola larga a la derecha** (muchos valores chicos, pocos valores muy grandes).

Compará con la normal (campana simétrica): si usaras una normal para "tiempo de elección" con media 2 min, podría darte tiempos negativos (absurdo) y sería simétrica (tanta gente tardando 0 min como 4 min), cuando en la realidad la mayoría resuelve rápido y **unos pocos se demoran muchísimo**.

Con tu ejemplo, para media $m = 2$ min:
- La mitad resuelve en menos de **1,45 min** (la mediana es menor que la media, típico de la asimetría).
- Casi nadie pasa de 10 min.

Con media $m = 8$ min (docente desorientado): mediana 5,81 min, y cerca del 25 % pasa los 10 min. Esos "pocos que se demoran mucho" son exactamente los que te interesan para justificar el tope $\tau$.

**Dato técnico útil:** el parámetro $\mu_{\text{LN}} = \ln(m) - \sigma^2/2$ de tu sección 4.3 sirve para *calibrar* la distribución de modo que su **media** sea exactamente $m$. Sin ese ajuste, la media de la log-normal no sería la que vos querés.

---

## 8. Suavización exponencial simple

Es una forma de **mantener un promedio que se va actualizando con cada dato nuevo, dándole más peso a lo reciente**. La fórmula de tu informe:

$$\hat{S}_{\text{nuevo}} = \alpha \cdot S_{\text{obs}} + (1 - \alpha) \cdot \hat{S}_{\text{anterior}}$$

Con $\alpha = 0{,}20$ significa: *"mi nueva estimación es 20 % lo que acabo de observar y 80 % lo que ya creía"*.

**Ejemplo numérico** (arranca en $\hat{S}_0 = 3{,}0$ min):

| Turno | Duración observada | Cálculo | Nueva estimación |
| :-: | :-: | :-- | :-: |
| 1 | 2,0 | 0,2·2,0 + 0,8·3,0 | 2,80 |
| 2 | 1,5 | 0,2·1,5 + 0,8·2,80 | 2,54 |
| 3 | 8,0 | 0,2·8,0 + 0,8·2,54 | 3,63 |

Un turno largo (8 min) sube la estimación, pero **no la dispara de golpe**: se suaviza. Así el estimador de horario no se vuelve loco con un solo caso atípico, pero tampoco ignora que la asamblea se está volviendo más lenta.

**¿Por qué no un promedio común?** Porque en la asamblea los tiempos **cambian**: al principio la gente resuelve en 2 min y después, cuando se agotan las escuelas, tardan 8. Un promedio de todo el día reaccionaría muy lento; la suavización exponencial "olvida" gradualmente lo viejo y se adapta.

**Para qué se usa:** para estimar $E[S_j]$, el tiempo esperado de cada docente que está adelante, y con eso calcular a qué hora le va a tocar a cada uno y mandarle el aviso de "prepárese, su turno es en 10 minutos".

---

## Para cerrar: cómo se conectan todas las piezas

1. **Log-normal** genera los tiempos de elección (con cola larga realista).
2. **FEL** hace avanzar el reloj de la simulación evento a evento.
3. **Prioridad no apropiativa** define quién es llamado y que nadie interrumpe a nadie.
4. **Suavización exponencial** estima cuánto tardarán los que están adelante, para avisar el horario.
5. **Monte Carlo** estima qué escuelas seguirán libres cuando le toque al docente.
6. **Réplicas (30)** repiten todo con distintas semillas para tener promedios e intervalos de confianza.
7. **Análisis de sensibilidad** verifica que las conclusiones no dependan de un solo supuesto.
8. **Sin warm-up** en la asamblea porque el arranque "con todos esperando" es parte de lo que medís.

Si querés, el próximo paso puede ser que te haga preguntas tipo defensa oral sobre estos temas para practicar cómo explicarlos con tus palabras, o profundizar en alguno (por ejemplo, la log-normal con cuentas, o cómo se calcula el intervalo de confianza con la t de Student).

---

> **Fecha:**
> 2026-11-08.
> **Persona:**
> Emiliano
>
> **Titulo:**
> Qué muestra cada uno de los 4 gráficos y cómo explicarlos fácil
>
> **Asunto:**
> Explicación en criollo y paso a paso de las 4 figuras de `graficos/salida/`: qué significa cada línea, caja o barra, y qué aprendimos de los datos.

**Respuesta:**

Si miramos los 4 gráficos juntos sin apuro, cuentan una historia re clara de lo que pasó cuando corrimos la simulación. Te explico uno por uno qué es cada dibujito que aparece y qué nos quiso decir el experimento:

---

## Figura 1: ¿Cuánto dura todo el acto en E1, E2 y E3? (`fig1_boxplot_duracion_escenarios.png`)

**Cómo se lee el dibujo:**
- **Los dos ejes verticales:** el de la izquierda marca cuántas horas dura la asamblea (desde que arranca a las 8:00 hs hasta que se cubre la vacante 100), y el de la derecha muestra **exactamente lo mismo pasado a minutos**, para no tener que andar multiplicando por 60 mentalmente.
- **Cada puntito suelto:** es una de las **30 simulaciones** que corrimos (como simular 30 actos públicos distintos con distinto azar).
- **La caja pintada:** encierra a la mitad del medio de esas 30 corridas (sacando las muy rápidas y las muy lentas). La **rayita negra del medio** es la mediana (el valor justo del centro), y los **palitos arriba y abajo (bigotes)** llegan hasta la corrida más larga y la más corta.
- **El rombo al costado de cada caja:** muestra el **promedio** con unas barritas que indican nuestro margen de confianza del 95 % (usando la $t$ de Student porque tenemos $n = 30$).

**Qué nos sorprendió al verlo:**
- Nosotros pensábamos que en **E2** (naranja, donde solo pusimos un reloj de 10 minutos máximo por persona) la caja iba a bajar un montón respecto a **E1** (gris, como se hace hoy sin límite). Y mirá: **quedaron casi pegadas a la misma altura** ($9,02\text{ h}$ vs. $8,98\text{ h}$, o sea $541,1$ vs. $538,8\text{ min}$). ¿Por qué pasó eso? Porque si alguien llega a su turno sin saber qué escuelas quedan y le cortás a los 10 minutos, igual perdiste esos 10 minutos, no cubriste ningún cargo y tenés que llamar al siguiente.
- Recién en **E3** (verde, cuando antes de su turno ya le recomendás 3 escuelas compatibles cerca de su casa) toda la caja cae en bloque a **$7,67\text{ h}$ ($460,0\text{ min}$)**. Eso es **1 hora y 21 minutos menos ($-15,0\,\%$)** en promedio.

---

## Figura 2: ¿Qué pasa si cambiamos el límite $\tau$ de 6 a 15 minutos? (`fig2_sensibilidad_ventana_tau.png`)

Acá probamos qué cambia si en vez de cortar el turno a los 10 minutos lo cortamos antes (**6 u 8 min**) o damos más margen (**12 o 15 min**), manteniendo 1 sola mesa.

### Gráfico (a) — ¿Cuánto espera la gente?
- **La línea punteada gris (`260,5 min`):** es lo que espera en promedio alguien atendido en el sistema actual (E1). Como E1 no tiene reloj límite, queda plana.
- **La línea naranja (E2):** queda **todo el tiempo arriba de E1** (arranca en $332,3\text{ min}$ con $\tau = 6$ y baja recién a $296,8\text{ min}$ con $\tau = 15$). Muestra que cortar turnos sin recomendador hace que la gente atendida espere **más** que hoy, porque muchos pasan a la cola de reintentos y suman espera hasta el final del acto.
- **La línea verde (E3):** va bajando a medida que das un poquito más de margen. En $\tau = 10$ empata con E1 ($263,6\text{ min}$), y con **12 o 15 minutos** ya pasa **por debajo** de E1 ($254,0$ y $246,7\text{ min}$).
- **La línea azul punteada arriba:** mide la espera promedio contando a **los 300 convocados** (también a los que se quedan esperando hasta el cierre sin alcanzar cargo). Se mantiene bastante pareja entre **$355$ y $359\text{ min}$**, igual casi 1 hora menos que E1 y E2 ($\approx 416\text{–}421\text{ min}$).
- **El recuadro azul:** te señala dónde estuvo el mejor número de E3 ($\tau = 15\text{ min}$, con $451,3\text{ min}$ de duración total, prácticamente empatado con $\tau = 12$ en $452,8\text{ min}$).

### Gráfico (b) — ¿Cuánta gente cae a reintentos y arriesga su mérito?
- **La línea roja punteada abajo (`8,0 %`):** es el **piso imposible de bajar** en el simulador, porque supusimos que al 8 % de los docentes se les corta internet o no atiende justo cuando toca, le des 6 o 15 minutos.
- **Las curvas naranja (E2) y verde (E3):** muestran qué porcentaje de llamados termina derivado a reintentos. El problema es que como la cola de reintentos recién se atiende al final del acto, cuando la vacante de su especialidad ya la tomó otro con menor puntaje, **cada punto acá representa docentes perjudicados en su orden de mérito**.
- Si te apurás demasiado poniendo **$\tau = 6\text{ min}$**, mandás a **$27,6\,\%$ en E2** y **$22,8\,\%$ en E3** a reintentos. Si en E3 ampliás a **$\tau = 12$ o $15\text{ min}$**, casi todos cierran bien su elección y los reintentos bajan hasta **`9,9 %`**, pegaditos al 8 % de caídas de red.

**Qué entendimos mirando los dos gráficos juntos:** poner una ventana muy corta ($\tau = 6\text{ o }8$) **no hace más rápida la asamblea y encima castiga a muchísimos docentes en su mérito**. Conviene usar **E3 con $\tau = 12$ a $15$ minutos**: dura igual o un poquito menos, baja la espera de atendidos por debajo de E1 y casi no desplaza a nadie por reloj.

---

## Figura 3: ¿Cuánto ayuda poner 2 o 3 mesas en paralelo ($c = 1, 2, 3$)? (`fig3_sensibilidad_comisiones_c.png`)

Muestra tres grupos de barras (gris = E1, naranja = E2, verde = E3) cuando atendés con **1, 2 o 3 comisiones al mismo tiempo** ($\tau = 10\text{ min}$).

- **En (a) — Duración total en horas:** la **línea azul punteada en `4,0 h`** marca lo que sería resolver todo en **un solo turno de mañana** (por ejemplo, de 8:00 a 12:00 hs).
  - Con **1 mesa**, todos tardan entre $7,67$ y $9,02\text{ h}$ (todo el día).
  - Con **2 mesas**, E1 ($4,58\text{ h}$) y E2 ($4,50\text{ h}$) todavía se pasan de las 4 horas; **E3 ($3,85\text{ h} = 231,3\text{ min}$)** es el único que logra terminar toda la asamblea dentro de la mañana.
  - Con **3 mesas**, E3 baja a **$2,58\text{ h}$** ($154,9\text{ min}$).
- **En (b) — Espera promedio de los 300 convocados:** pasa de $359 \to 179 \to 119\text{ min}$ en E3 (contra $416 \to 209 \to 140\text{ min}$ en E1).

**Algo re interesante para conectar con lo que vimos en clase:** cuando verificamos $M/M/2$ en la Sección 5.1, pasar de 1 a 2 servidores bajó la espera **16 veces** porque el sistema quedaba vacío la mitad del tiempo ($P_0 = 0,50$). En cambio acá pasa de $7,67\text{ h}$ a $3,85\text{ h}$ (baja **a la mitad**, $1/c$), porque los 300 docentes ya están esperando desde las 8:00 y las mesas no frenan un segundo ($P_0 = 0$) hasta adjudicar los 100 cargos. Igual, E3 siempre conserva su ~15–17 % de ventaja.

---

## Figura 4: ¿Qué pasa si pocos usan el recomendador, y sirvió Monte Carlo? (`fig4_adopcion_recomendador_y_montecarlo.png`)

### Gráfico (a) — "¿Y si los docentes no le hacen caso al recomendador?" ($p_{\text{rec}}$)
- Como en nuestro caso base supusimos que el **70 %** acepta guiarse por las 3 sugerencias cuando ya se quedaron sin sus opciones iniciales, acá probamos qué pasa si no lo usa nadie (**0 %, que equivale a E2**), o si lo usa el **30 %, 50 %, 70 % o 90 %**.
- Las **dos líneas rectas de arriba** son lo que tardan E1 (`541,1 min`) y E2 (`538,8 min`).
- Mirá cómo bajan la línea verde (duración) y la azul (espera): **incluso en el escenario pesimista donde apenas el 30 % acepta las recomendaciones**, el acto ya baja a **`502,5 min`** (casi 39 min menos que hoy). Y si lo adopta el 90 %, baja a **`430,3 min`** (`7,17 h`, más de 1 hora y 50 min de ahorro). Esto muestra que nuestra conclusión **es robusta**: no depende de que todo el mundo haga caso.

### Gráfico (b) — "¿Aportó algo simular con Monte Carlo, o alcanzaba con mirar qué estaba libre en ese minuto?"
- Las barras miden el **error ($MSE$)** al predecir 10 minutos antes si una escuela va a llegar con vacante libre cuando te toque pasar: **cuanto más baja la barra, más confiable es el aviso**.
- **Sin Monte Carlo ($R_{\text{MC}} = 0$, foto estática):** simplemente asume que lo que está libre en este segundo va a seguir libre en 10 minutos. En el promedio general el error es $0,0511$, pero mirá la **barra naranja alta ("vacantes disputadas")**: justo en las escuelas peleadas que están por elegir los 2 a 5 colegas que tenés adelante, el error salta a **`0,3550`** (falla un montón).
- **Con Monte Carlo ($R_{\text{MC}} = 200$ pasadas):** el error general baja a **`0,0147` ($-71,3\,\%$)** y en las vacantes peleadas se desploma a **`0,1006` ($-71,7\,\%$)**.
- **El dato honesto del recuadro (`p_rec = 0,70`):** si comparamos E3 con y sin Monte Carlo dejando igual el recomendador, vimos que **el grueso del ahorro de tiempo ($538,8 \to 461,0\text{ min}$) lo logra tener listas precargadas + recomendador** (Monte Carlo solo recorta `-0,98 min`, que no es significativo en tiempo). Donde **sí** hace una diferencia real Monte Carlo es en avisar con mucha más precisión qué vacantes de verdad llegan libres (`-71 %` de error) y mejorar levemente pero con significancia estadística la satisfacción con el cargo elegido ($0,584 \to 0,586$, $p = 0,023$).

---

> **Fecha:**
> 2026-11-08.
> **Persona:**
> Emiliano
>
> **Titulo:**
> ¿De dónde sale `gl = 29` en la distribución t de Student?
>
> **Asunto:**
> Explicación simple de qué son los grados de libertad (`gl = 29`), por qué es `30 - 1` tanto en los intervalos de confianza como en las pruebas pareadas entre escenarios, y para qué se usa `2,0452`.

**Respuesta:**

**`gl`** significa **grados de libertad** (*degrees of freedom*). En criollo, es **cuántos datos "libres" tenés de verdad después de haber usado la muestra para calcular el promedio**.

### Ejemplo fácil con 3 notas
Imaginate que rendiste 3 parciales y te dicen: *"tu promedio fue 7"*.
- El primer parcial te lo podés inventar libre: pongamos **6**.
- El segundo también es libre: pongamos **8**.
- ¿El tercero puede ser cualquiera? **No**, porque para que el promedio siga dando 7, el tercero *obligatoriamente* tiene que ser **7** ($6 + 8 + 7 = 21$, dividido 3 da 7).

Tenías $n = 3$ notas, pero una vez que fijaste el promedio solo pudiste elegir **2** números libremente (`3 - 1 = 2` grados de libertad).

### Cómo aplica en nuestro trabajo (`n = 30`, `gl = 29`)
1. **En los intervalos de confianza de cada escenario (Sección 6.1 y 6.3):** como corrimos **30 simulaciones independientes** ($n = 30$) y usamos esos mismos 30 resultados para estimar tanto la media $\bar{X}$ como el desvío estándar $s$ (`src/metricas.py`), se "gasta" 1 grado de libertad al fijar la media. Entonces queda:
   $$\text{gl} = n - 1 = 30 - 1 = 29$$
2. **En las pruebas t pareadas (Sección 6.3.1):** como comparamos E1 vs. E2 o E2 vs. E3 **réplica a réplica** (usando la misma semilla en cada par), restamos cada par y armamos **30 diferencias** ($D_1, D_2, \dots, D_{30}$). Al calcular el promedio de esas 30 diferencias, de nuevo queda $\text{gl} = 30 - 1 = 29$.

### ¿Y de dónde sale el `2,0452`?
Como no conocemos el desvío estándar "real y exacto" del universo (solo lo estimamos con $s$ sobre 30 corridas), en lugar de usar el famoso `1,96` de la distribución Normal usamos la tabla de **$t$ de Student** con $\text{gl} = 29$ y 95 % de confianza ($2,5\,\%$ en cada cola). Ese valor en tabla da **$2,0452$**, que ensancha apenitas el margen de error para ser honestos con esa incertidumbre extra de la muestra finita.

---

> **Fecha:**
> 2026-11-08.
> **Persona:**
> Emiliano
>
> **Titulo:**
> ¿De dónde sale el "satisfacción de adjudicación ($p = 0,023$)" de Monte Carlo?
>
> **Asunto:**
> Explicación simple de cómo se mide la satisfacción, de qué comparación sale exactamente ese $p = 0,023$, y por qué una diferencia chica (`0,584` vs. `0,586`) igual da estadísticamente significativa.

**Respuesta:**

Ese **$p = 0,023$** sale de la prueba de **ablación de Monte Carlo** (`E3 sin MC` vs. `E3 con MC`), o sea, el experimento donde dejamos todo igual en E3 (`p_rec = 0,70`, $\tau = 10\text{ min}$) y lo único que prendemos o apagamos es el pronóstico Monte Carlo (`R_MC = 0` vs. `R_MC = 200`, en `src/correr_experimentos.py` y guardado en `data/resultados_experimentos.json`).

### 1. Primero: ¿cómo medimos la "satisfacción"?
En `src/simulation.py`, cada uno de los 100 docentes que logra adjudicar recibe una nota de **0 a 1** según en qué puesto de su ranking real de 10 escuelas (`ranking_real_10`) quedó la escuela que agarró:
- Puesto 1 (su escuela ideal) = **`1,00`**
- Puesto 2 = **`0,90`** ... bajando de `0,10` en `0,10` hasta el puesto 10 = **`0,10`**
- Si agarró una escuela que ni estaba en su Top 10 = **`0,05`**

Después promediamos esos 100 puntajes por asamblea.

### 2. ¿Qué comparamos para sacar `p = 0,023`?
Corrimos las **mismas 30 semillas** (`gl = 29`) dos veces en E3:
- **E3 sin Monte Carlo (`R_MC = 0`):** el recomendador ordena las 3 sugerencias mirando solo lo que está libre *en ese instante* (foto estática). Dio satisfacción promedio **`0,584`** (`0,58428`).
- **E3 con Monte Carlo (`R_MC = 200`):** multiplica el puntaje de cada escuela por la probabilidad $\theta$ de que siga libre dentro de 10 minutos (`src/recomendador.py`). Dio **`0,586`** (`0,58575`).

Cuando hacés la **prueba *t* pareada** entre las 30 réplicas con y sin MC (`src/metricas.py`), da:
- $t = -2,41$ con $\text{gl} = 29$
- **$p = 0,02257 \approx 0,023$** (como $0,023 < 0,05$, la diferencia es **estadísticamente significativa**).

### 3. ¿Cómo puede ser significativa una diferencia tan chiquita (`0,584` → `0,586`)?
Porque **comparamos las mismas 30 corridas semilla por semilla** (*Common Random Numbers*). Como no hay ruido aleatorio extra entre los dos lotes, el test detecta que **en casi todas las asambleas pasa lo mismo**: sin MC, el recomendador a veces mete en el Top 3 una escuela "linda" cuya última vacante justo la agarra un colega que pasa antes; con MC, la filtra antes y deja otra alternativa mejor ubicada que el docente sí alcanza a tomar. Es una ganancia chica en magnitud (`+0,0015`), pero súper consistente en las 30 réplicas.

*(Ojo para no mezclarlo en la defensa: si comparás **E1 vs. E3**, ahí la satisfacción da $0,590$ vs. $0,586$ con **$p = 0,120$**, o sea, **empate estadístico** con el sistema actual ahorrando 81 minutos. Ese $p = 0,023$ mide específicamente el plus que agrega Monte Carlo dentro de E3).*

---
