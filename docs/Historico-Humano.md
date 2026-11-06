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
