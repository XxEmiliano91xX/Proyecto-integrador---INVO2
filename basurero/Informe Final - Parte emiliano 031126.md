# 

# Universidad Católica de Salta

## Facultad de Ingeniería

# Sistema de turnos dinámicos para las asignaciones docentes en Salta

**Carrera:** Ingeniería en Informática  
**Asignatura:** Investigacion Operativa II  
**Profesor Titular:**   
**Profesor Auxiliar:**   
**Integrantes y DNI:**

* Emiliano Javier Aguirre, 45.770.631  
* Pablo Celaya, 45.115.839

**LO QUE ESTA EN AMARRILLO ES EL ENCABEZADO TENTATIVO**

ÍNDICE                                                          

\[Tabla de contenido automática de Word\]

RESUMEN                                                         

\[Problema, propuesta, método (simulación \+ metaheurística), resultado principal. 150-250 palabras. Se escribe al final.\]

Palabras clave: teoría de colas, prioridad no apropiativa, simulación de eventos discretos, metaheurísticas, asignaciones docentes

1\. INTRODUCCIÓN                                                 

   1.1. Contexto: las asambleas de designación docente en Salta

   1.2. Planteo del problema

        \[Proceso secuencial, bloqueo de la línea, incertidumbre del docente, desconexiones\]

   1.3. Objetivos

        1.3.1. Objetivo general

        1.3.2. Objetivos específicos

   1.4. Alcance y limitaciones

        \[Qué entra y qué no: sin aplicación real, documentos ya validados\]

   1.5. Organización del informe

Tarea 3/11 (Emi)

# Marco teorico

## **2\. Teoría de colas**

### **2.1 Elementos de un sistema de colas**

Los actores principales de una situación de colas son el cliente y el servidor. Los clientes llegan a una instalación de servicio desde una fuente; al llegar pueden ser atendidos de inmediato o esperar en una cola si la instalación está ocupada. Cuando el servidor termina, toma al siguiente cliente de la cola; si la cola está vacía, queda ocioso hasta que llegue uno nuevo. El sistema comprende tanto a quienes esperan como a quienes están siendo atendidos.

Desde el análisis de colas, la llegada de los clientes se representa con el tiempo entre llegadas sucesivas y el servicio con el tiempo de servicio por cliente. Ambos pueden ser probabilísticos (por ejemplo, la operación de una dependencia oficial) o determinísticos (por ejemplo, los turnos de una entrevista de trabajo o de una cita médica). El tamaño de la cola puede ser finito (como el área intermedia entre dos máquinas sucesivas) o, a todos los fines prácticos, infinito.

La disciplina de la cola es el orden en que se selecciona a los clientes. La más común es primero en llegar, primero en ser atendido (FCFS, o PLPS en las presentaciones). Otras son último en llegar, primero en ser atendido (LCFS) y servicio en orden aleatorio (SIRO). También se puede seleccionar según un orden de prioridad, como los trabajos urgentes de un taller, que se procesan antes que los regulares. Por último, el comportamiento de los clientes influye en el análisis: pueden cambiarse a una cola más corta, desistir de hacer cola por la demora anticipada o salirse de ella por haber esperado demasiado.

### **2.2 Distribución exponencial y proceso de Poisson**

En la mayoría de las situaciones de colas las llegadas ocurren al azar: la ocurrencia de un evento (una llegada o una terminación de servicio) es independiente del tiempo transcurrido desde el evento anterior. Los tiempos aleatorios entre llegadas y de servicio se describen con una distribución de probabilidad, habitualmente la exponencial con parámetro λ:

* Densidad: f(t) \= λ·e^(−λt), para t ≥ 0  
* Distribución acumulada: F(t) \= P{T ≤ t} \= 1 − e^(−λt), y por lo tanto P{T \> t} \= e^(−λt)  
* Media y varianza: E\[T\] \= 1/λ ; V(T) \= 1/λ²

La exponencial tiene tres propiedades que sostienen casi todos los modelos siguientes:

1. **Es estrictamente decreciente.** Valores pequeños, cercanos a cero, son bastante probables. Por ejemplo, P{0 ≤ T ≤ ½·(1/λ)} \= 0,393, mayor que P{½·(1/λ) ≤ T ≤ 3/2·(1/λ)} \= 0,383, aunque ambos intervalos tienen la misma longitud.  
2. **Falta de memoria.** Describe un fenómeno totalmente aleatorio: P{T \> t \+ Δt \| T \> Δt} \= P{T \> t}. La probabilidad de que el próximo evento ocurra dentro de un intervalo depende solo de ese intervalo y no del tiempo que ya pasó desde el último evento.  
3. **Relación con la distribución de Poisson.** Si los tiempos entre eventos son exponenciales con parámetro λ, la cantidad de eventos X(t) en un período t tiene distribución de Poisson: P{X(t) \= n} \= (λt)^n · e^(−λt) / n\!, con media E\[X(t)\] \= λt.

|  | Exponencial | Poisson |
| ----- | ----- | ----- |
| Variable aleatoria | Tiempo entre llegadas sucesivas, t | Cantidad de llegadas n en un período T |
| Valor medio | 1/λ unidades de tiempo | λT llegadas durante T |
| P{sin llegadas en un período A} | P{t \> A} \= e^(−λA) | p₀(A) \= e^(−λA) |

Ejemplo de la cátedra: con un tiempo medio entre llegadas de 20 minutos, λ \= 1/20 por minuto; la media de la exponencial es 20 minutos y, en un período de T \= 60 minutos, la media de Poisson es λT \= 3 llegadas.

### **2.3 Proceso de nacimiento y muerte**

La mayoría de los modelos elementales de colas suponen que las entradas y las salidas ocurren según un proceso de nacimiento y muerte: un nacimiento es la llegada de un cliente y una muerte es la salida del cliente servido. El estado del sistema en el tiempo t es N(t), la cantidad de clientes en el sistema. Se definen λₙ, la tasa de llegadas, y μₙ, la tasa de salidas cuando hay n clientes en el sistema. Los supuestos son:

* Dado N(t) \= n, el tiempo hasta el próximo nacimiento es exponencial con parámetro λₙ (n \= 0, 1, 2, …).  
* Dado N(t) \= n, el tiempo hasta la próxima muerte es exponencial con parámetro μₙ (n \= 1, 2, …).  
* Ambas variables aleatorias son mutuamente independientes. La próxima transición es n → n+1 o n → n−1, según cuál de las dos variables sea menor.

El proceso de nacimiento y muerte es un tipo especial de cadena de Markov de tiempo continuo, es decir, un proceso en el que la probabilidad de lo que ocurra a continuación depende solo del estado actual (propiedad de Markov). Los modelos de colas representables así son mucho más manejables analíticamente que cualquier otro.

En estado estable, para cada estado n la tasa media de entrada es igual a la tasa media de salida (ecuación de balance):

* Estado 0: μ₁P₁ \= λ₀P₀  
* Estado n ≥ 1: λₙ₋₁Pₙ₋₁ \+ μₙ₊₁Pₙ₊₁ \= (λₙ \+ μₙ)Pₙ

Resolviendo recursivamente en función de P₀ se obtiene Pₙ \= Cₙ·P₀, donde

Cₙ \= (λₙ₋₁·λₙ₋₂·…·λ₀) / (μₙ·μₙ₋₁·…·μ₁) para n ≥ 1, y C₀ \= 1\.

Como las probabilidades deben sumar 1, P₀ \= (Σₙ Cₙ)⁻¹.

### **2.4 Estado estacionario y estado transitorio**

Los modelos analíticos de la cátedra describen el comportamiento a largo plazo o de estado estable, alcanzado después de que el sistema estuvo operando un tiempo suficientemente largo. Se contrapone al comportamiento transitorio (o de calentamiento) que prevalece al inicio de la operación, durante el cual la distribución de probabilidad del estado cambia con el tiempo hasta converger a la distribución estacionaria. Las presentaciones señalan dos razones para no analizar el régimen transitorio: su complejidad analítica (los resultados existentes son demasiado complicados para tener buen uso práctico) y el hecho de que la mayoría de las situaciones de colas se estudian en condiciones de estado estable.

Un sistema solo alcanza el estado estable si las llegadas no superan la capacidad de servicio. En el modelo de un servidor, si λ ≥ μ la suma que define P₀ diverge, la cola crece sin límite y la solución deja de ser válida.

### **2.5 Medidas de desempeño y fórmula de Little**

A partir de las probabilidades Pₙ se obtienen las medidas de desempeño del sistema, con c servidores:

* L: cantidad esperada de clientes en el sistema, L \= Σ n·Pₙ  
* Lq: cantidad esperada de clientes en la cola, Lq \= Σ (n − c)·Pₙ, sumando desde n \= c+1  
* W: tiempo esperado de espera en el sistema  
* Wq: tiempo esperado de espera en la cola

La fórmula de Little las vincula: L \= λef·W y Lq \= λef·Wq, donde λef es la tasa efectiva de llegadas al sistema. Es igual a λ cuando todos los clientes que llegan se unen al sistema; si algunos no pueden hacerlo porque el sistema está lleno, λ \= λef \+ λperdido y por lo tanto λef \< λ. Además, el tiempo en el sistema es el tiempo en cola más el tiempo de servicio:

W \= Wq \+ 1/μ ; L \= Lq \+ λef/μ

La cantidad promedio de servidores ocupados es L − Lq \= λef/μ, y la utilización de la instalación es esa cantidad dividida por c.

### **2.6 Notación de Kendall**

Las características de una cola se resumen con la notación de Kendall (1953), (a/b/c):(d/e/f), donde:

* a: distribución de las llegadas  
* b: distribución de las salidas (tiempo de servicio)  
* c: cantidad de servidores en paralelo (1, 2, …, ∞)  
* d: disciplina de la cola  
* e: cantidad máxima admisible en el sistema (finita o infinita)  
* f: tamaño de la fuente (finito o infinito)

Para a y b los símbolos estándar son M (Markov: llegadas de Poisson o tiempos exponenciales), D (tiempo constante), Eₖ (Erlang), GI (distribución general del tiempo entre llegadas) y G (distribución general del tiempo de servicio). Para d se usan PLPS (FCFS), ULPS (LCFS), SEOA (servicio en orden aleatorio) y DG (disciplina general).

### **2.7 Modelos de un servidor**

**Modelo (M/M/1):(DG/∞/∞).** Con λₙ \= λ y μₙ \= μ, y ρ \= λ/μ \< 1, las probabilidades de estado estable son Pₙ \= (1 − ρ)·ρⁿ y las medidas de desempeño resultan:

* L \= ρ/(1 − ρ) \= λ/(μ − λ)  
* Lq \= ρ²/(1 − ρ) \= λ²/\[μ(μ − λ)\]  
* W \= 1/(μ − λ)  
* Wq \= λ/\[μ(μ − λ)\]

Además, la distribución del tiempo de espera en el sistema con disciplina FCFS es P{W \> t} \= e^(−μ(1−ρ)t). Ejemplo de la cátedra (lavadero de autos): con λ \= 4 autos por hora y un tiempo medio de lavado de 10 minutos (μ \= 6 por hora), ρ \= 2/3, P₀ \= 0,333, L \= 2, Lq \= 1,333, W \= 0,5 hora y Wq \= 0,333 hora.

**Modelo (M/M/1):(DG/K/∞), con capacidad finita.** Si el sistema admite como máximo K clientes, λₙ \= λ para n \< K y λₙ \= 0 para n ≥ K. Entonces Pₙ \= (1 − ρ)ρⁿ / (1 − ρ^(K+1)) para ρ ≠ 1 (y 1/(K+1) si ρ \= 1), con n \= 0, 1, …, K, y

* L \= ρ/(1 − ρ) − (K \+ 1)ρ^(K+1) / (1 − ρ^(K+1)) ; Lq \= L − (1 − P₀)  
* λperdido \= λ·P\_K ; λef \= λ(1 − P\_K)  
* W \= L/λef ; Wq \= Lq/λef

Ejemplo de la cátedra: el mismo lavadero con cuatro lugares de espera (K \= 5\) tiene λef \= 3,80752 y W \= 0,3736 hora (unos 22 minutos, contra 30 minutos sin límite), a costa de perder aproximadamente el 4,8 % de los clientes potenciales (P₅ \= 0,04812). Es un ejemplo de compromiso entre espera y clientes que no se atienden.

### **2.8 Modelos de múltiples servidores**

**Modelo M/M/c.** Todos los tiempos entre llegadas son independientes y exponenciales, los tiempos de servicio son independientes y exponenciales, y hay c servidores idénticos (las presentaciones usan la letra s para esta cantidad). Es un caso especial del proceso de nacimiento y muerte con λₙ \= λ y μₙ \= n·μ para n ≤ c, y μₙ \= c·μ para n ≥ c. Los factores son:

* Cₙ \= (λ/μ)ⁿ / n\! para n \= 0, 1, …, c  
* Cₙ \= (λ/μ)ⁿ / (c\!·c^(n−c)) para n ≥ c

Si λ \< cμ, es decir, ρ \= λ/(cμ) \< 1, entonces

P₀ \= 1 / \[ Σ\_{n=0}^{c−1} (λ/μ)ⁿ/n\! \+ ((λ/μ)^c / c\!) · 1/(1 − ρ) \]

Lq \= P₀·(λ/μ)^c·ρ / \[c\!·(1 − ρ)²\] ; Wq \= Lq/λ ; W \= Wq \+ 1/μ ; L \= Lq \+ λ/μ

La probabilidad de esperar más de t en cola es P{Wq \> t} \= (1 − P{Wq \= 0})·e^(−cμ(1−ρ)t).

Ejemplo de la cátedra (sala de urgencias del Hospital San Bernardo): con λ \= 2 pacientes por hora y μ \= 3 por hora, un solo médico (c \= 1\) da ρ \= 2/3, Lq \= 4/3 y Wq \= 2/3 hora, y el 66,7 % de los pacientes debe esperar. Con un segundo médico (c \= 2\) resultan ρ \= 1/3, P₀ \= 1/2, Lq \= 1/12 y Wq \= 1/24 hora (unos 2,5 minutos), y solo espera el 16,7 %. Es decir, duplicar los servidores reduce la espera media en cola 16 veces, mucho más que proporcionalmente, un efecto que se vuelve a observar al evaluar varias comisiones simultáneas.

**Modelo M/M/c/K, con cola finita.** La capacidad de la cola es K − c y la única modificación es λₙ \= λ para n \< K y λₙ \= 0 para n ≥ K. Los clientes que llegan con la cola llena se pierden. Para c ≤ K:

* Cₙ \= (λ/μ)ⁿ/n\! para n ≤ c ; Cₙ \= (λ/μ)ⁿ/(c\!·c^(n−c)) para c ≤ n ≤ K ; Cₙ \= 0 para n \> K  
* P₀ \= 1 / \[ Σ\_{n=0}^{c} (λ/μ)ⁿ/n\! \+ ((λ/μ)^c / c\!) · Σ\_{n=c+1}^{K} (λ/(cμ))^(n−c) \]

Ejemplo de la cátedra (compañía de taxis): con c \= 4 taxis, K \= 10, λ \= 16 y μ \= 5 por hora, se obtiene λef \= 15,42815, Lq \= 1,15421, Wq \= 0,07481 hora y W \= 0,27481 hora.

**Antecedente de aplicación.** Las presentaciones citan el caso de KeyCorp (Kotha, Barnum y Bowen, Interfaces 26(1), 1996), donde el modelo M/M/c fue la herramienta clave para reducir el tiempo de espera de los clientes de sus sucursales. Con los datos de tiempo de servicio, el modelo indicó cuánto personal hacía falta; la reducción del tiempo medio de servicio (de 246 a 115 segundos) y una programación optimizada del personal permitieron que el 96 % de los clientes esperara menos de 5 minutos, con ahorros cercanos a 20 millones de dólares anuales.

### **2.9 Alcance y limitaciones de los modelos analíticos**

Todos los modelos anteriores comparten supuestos fuertes: llegadas de Poisson y servicios exponenciales, tasas que dependen a lo sumo de la cantidad de clientes en el sistema, servidores idénticos, una fuente de clientes infinita o una capacidad fija, y análisis en estado estable. En clase se destacó que, una vez que se conocen las fórmulas, lo realmente interesante son las limitaciones de estos modelos. Esas limitaciones son la razón por la cual el sistema de turnos propuesto se evalúa por simulación y no directamente con las fórmulas de esta sección (ver sección 3).

## **3\. Formulación del sistema de espera de las asignaciones docentes**

### **3.1 Correspondencia con los elementos de una cola**

El proceso de designación se interpreta con los elementos de la sección 1.1:

| Elemento de teoría de colas | En el sistema de asignaciones |
| :---- | :---- |
| Cliente | Docente validado del Listado de Orden de Mérito |
| Fuente | Finita: n docentes (300 en la instancia de referencia), todos presentes desde el inicio de la jornada. No hay un proceso de llegadas de Poisson |
| Servidor | Ventanilla de elección (comisión). Se prevé c \= 1 en E1 y E2 y c ≥ 1 en E3 |
| Tiempo de servicio | Tiempo de decisión del docente, T\_elección (distribución log-normal) |
| Cola | Cola principal ordenada por puntaje Pᵢ y cola de reintentos de menor prioridad |
| Disciplina | Prioridad no apropiativa por puntaje: el docente que ya está decidiendo no es interrumpido por otro de mayor puntaje |
| Tamaño de la cola | Finito, acotado por la cantidad de docentes |
| Comportamiento del cliente | Desconexión o falla técnica con probabilidad p \= 0,08; además, el sistema (no el cliente) corta la espera al vencer la ventana τ |

Este sistema no coincide exactamente con ningún modelo de la sección 1: la cola es finita y cerrada (no hay llegadas aleatorias a lo largo del tiempo), el servicio está truncado y hay reintentos. Lo más cercano en la notación de Kendall es una cola con fuente finita (símbolo f) y disciplina general (DG). Las fórmulas de la sección 1 se usan por eso como referencia cualitativa y para validar el simulador, no como modelo final.

### **3.2 Escenario base (E1): cola simple sin límite de tiempo**

En el procedimiento tradicional se llama a los docentes por puntaje, uno por uno, y el servicio del docente j no tiene tope: S\_j \= T\_j. El docente en la posición k espera en cola la suma de los servicios de quienes lo preceden, Wq\_k \= Σ\_{j\<k} S\_j, de modo que si los n docentes tienen servicio de media E\[S\], el tiempo total de la jornada es n·E\[S\] y la espera media en cola es (n − 1)/2 · E\[S\]. Con n \= 300 y E\[S\] \= 1 minuto (valor ilustrativo) la jornada dura unas 5 horas y la espera media supera las 2 horas y media. Un único docente lento, o ausente, demora a toda la línea que lo sigue. El tratamiento de las desconexiones en E1, donde no hay tope de tiempo, queda por definir.

### **3.3 Escenario E2: ventana τ, servicio truncado y cola de reintentos**

En el sistema propuesto el servicio se trunca en la ventana τ:

S \= min(T\_elección, τ)

Quien no elige a tiempo, o no responde, pasa a la cola de reintentos de menor prioridad, de manera que se atiende después de la cola principal y no demora a quienes tienen mayor puntaje. Esta cola funciona como una realimentación (feedback): el cliente vuelve a entrar al sistema después de un servicio no completado. Esta estructura no está desarrollada en las presentaciones de la cátedra y aquí se define de forma conceptual.

Como referencia con una distribución para la que existen fórmulas cerradas, si T\_elección es exponencial con media 1/μ (sección 1.2), entonces P{T \> τ} \= e^(−μτ) y

E\[min(T, τ)\] \= (1 − e^(−μτ)) / μ

Si además se supone que un docente ausente consume la ventana completa, la probabilidad de pasar a reintentos y el servicio medio son

q \= p \+ (1 − p)·P{T \> τ} ; E\[S\] \= p·τ \+ (1 − p)·E\[min(T, τ)\]

Con media de 1 minuto, τ \= 3 minutos y p \= 0,08 (valores ilustrativos), P{T \> τ} \= e^(−3) ≈ 0,050, E\[min(T, τ)\] ≈ 0,95 minutos, q ≈ 12,6 % y E\[S\] ≈ 1,11 minutos. Como en el ejemplo del lavadero con capacidad finita (sección 1.7), el tope reduce la espera del resto a costa de que una fracción de clientes (aquí, el 12,6 %) no se atienda en su primera oportunidad. El modelo de simulación usa la distribución log-normal, y la exponencial queda como caso de referencia para validar.

Supuesto provisorio: mientras no se definan las preguntas abiertas del proyecto, se considera una sola ronda de reintentos y que quien pasa a ella conserva su puntaje original.

### **3.4 Estimador de horario y aviso**

Si los docentes se atienden en orden y el docente en la posición k espera a todos los anteriores, su horario esperado de atención es

E\[T\_k\] \= T\_inicio \+ Σ\_{j=1}^{k−1} E\[S\_j\]

Es la contrapartida, para un docente concreto, del tiempo medio de espera en cola Wq de la sección 1.5: E\[T\_k\] − T\_inicio es su espera esperada en cola. El estimador se recalcula en tiempo real: cuando un docente termina antes o pasa a reintentos, su término esperado se reemplaza por el valor observado y se actualiza el horario de los que siguen. El aviso “Prepárese” se emite cuando E\[T\_k\] − T\_actual ≤ 10 minutos. Con c comisiones en paralelo el tiempo acumulado se reparte aproximadamente entre ellas, aproximación que debe contrastarse con la simulación.

### **3.5 Métricas de desempeño**

* **Wq**: tiempo medio de espera en cola de los docentes, medido en minutos desde el comienzo de la jornada hasta el inicio de su servicio.  
* **Lq**: largo medio de la cola. En una jornada finita se calcula como el promedio en el tiempo de la cantidad de docentes esperando, y vale Lq \= (Σ\_j Wq\_j) / T\_total, una versión en horizonte finito de la fórmula de Little (sección 1.5), útil para controlar la coherencia del simulador.  
* **Tiempo total de la jornada** (T\_total): desde el primer llamado hasta el último servicio.  
* **Tasa de atención**: proporción de docentes que logra completar su elección.  
* **Cargos cubiertos**: cantidad de cargos efectivamente asignados sobre el total de vacantes.

  ### **3.6 Notación y convenciones**

| Símbolo | Significado |
| :---- | :---- |
| Pᵢ | Puntaje del docente i |
| τ | Ventana máxima de decisión (tiempo límite de servicio). Se reserva solo para este uso |
| c | Cantidad de comisiones o canales de atención simultáneos (en las presentaciones, s) |
| M | Máximo de escuelas que cada docente puede precargar |
| S\_j | Tiempo de servicio del docente j, S\_j \= min(T\_elección, τ) |
| E\[T\_k\] | Horario estimado de atención del docente en la posición k |
| p | Probabilidad de desconexión o falla técnica |
| Wq, Lq | Tiempo medio de espera en cola y largo medio de cola |
| λ, μ, ρ | Tasa de llegadas, tasa de servicio y utilización ρ \= λ/(cμ) |
| K | Capacidad máxima del sistema (en una presentación se usa N) |
| Pₙ | Probabilidad de estado estable de tener n clientes en el sistema (con P mayúscula para no confundirla con p) |

Observación: en la notación de Kendall la letra M significa “Markov” (llegadas o servicios exponenciales); no debe confundirse con M, el máximo de escuelas precargadas.

### **3.7 Interfaz con la instancia de datos y con la sección de metaheurísticas**

El simulador y la metaheurística comparten datos y definiciones. Los puntos de contacto son:

* **Instancia de datos.** El simulador lee docentes.csv (id, puntaje, tiempo\_decision\_medio, preferencias). La columna tiempo\_decision\_medio es la media de la distribución de decisión; el parámetro de dispersión de la log-normal se fija en un único lugar compartido y se acuerda con quien genera la instancia, para que los datos sintéticos y el simulador usen la misma distribución. La métrica de cargos cubiertos y la asignación por grado y especialidad requieren además un archivo de cargos vacantes (cargos.csv), todavía no definido.  
* **Función de aptitud.** Si la metaheurística minimiza el tiempo total de la jornada al repartir docentes entre comisiones, la aproximación T\_total ≈ (1/c)·Σ E\[S\_j\] de esta sección sirve como estimación rápida; la evaluación final se hace siempre con el simulador. Si en cambio maximiza la satisfacción de preferencias respetando el orden de mérito, esa función pertenece a la sección de metaheurísticas y el simulador solo la reporta como métrica adicional.  
* **Escenario E3.** Se formula en la sección de metaheurísticas. El simulador consume su salida (cronograma\_optimizado.json o .csv); falta definir cómo la pre-asignación modifica el tiempo de decisión de cada docente y si la cantidad de comisiones c cambia respecto de E2.  
* **Notación.** Se usan los símbolos de la sección 2.6; en particular, τ se reserva para la ventana de decisión, y cualquier límite propio de la metaheurística (por ejemplo, de tiempo de cómputo) usa otro símbolo.

  ## **4\. Fundamentos de simulación**

  ### **4.1 Por qué simular**

Los modelos de la sección 1 exigen estado estable, llegadas de Poisson y servicios exponenciales, y las propias presentaciones advierten que el análisis del régimen transitorio es analíticamente complejo. El sistema propuesto incumple todo eso: es una jornada finita (un solo día, con un comienzo y un fin), la fuente es finita, el servicio está truncado en τ, hay prioridades y una cola de reintentos. Por eso se recurre a la simulación, que permite reproducir el funcionamiento del sistema evento por evento y medir las mismas variables de desempeño (Wq, Lq, tiempo total, entre otras) sin depender de las fórmulas cerradas. Los modelos analíticos siguen siendo útiles como referencia y como banco de pruebas para validar el simulador.

### **4.2 Estado y eventos**

El proceso de nacimiento y muerte de la sección 1.3 ya describe un sistema por su estado N(t) y por dos tipos de eventos: llegadas y terminaciones de servicio. En cada estado hay un tiempo aleatorio hasta el próximo evento de cada tipo, y ocurre primero el que tenga menor tiempo. Un simulador de eventos discretos usa esa misma lógica: el reloj salta de evento en evento y, en cada uno, se actualiza el estado. En el sistema de asignaciones el estado incluye el docente en servicio, el contenido de la cola principal y de la cola de reintentos, los cargos disponibles y el reloj, y los eventos son:

* inicio del servicio de un docente (llamado a elegir);  
* fin del servicio por elección antes de que venza τ;  
* vencimiento de la ventana τ (timeout);  
* desconexión o falla técnica, con probabilidad p;  
* pase a la cola de reintentos;  
* emisión del aviso, cuando E\[T\_k\] − T\_actual ≤ 10 minutos.

Esta estructura es la que describe la bibliografía de simulación de eventos discretos (Law, 2015, cap. 1; Banks et al., 2014, cap. 3; las presentaciones de la cátedra no tratan este punto). En ella los eventos son instantáneos y cambian el estado del sistema, y el reloj no avanza en pasos fijos sino que salta al instante del próximo evento (avance al próximo evento). Los componentes típicos son: las variables de estado, el reloj de simulación, la lista de eventos futuros (FEL), ordenada por instante de ocurrencia, los contadores estadísticos donde se acumulan las métricas, una rutina de inicialización y una rutina de tiempos que elige el evento más inminente. El ciclo consiste en tomar de la lista el evento más próximo, avanzar el reloj a su instante, ejecutar su lógica (actualizar el estado y programar nuevos eventos) y repetir hasta que se cumple la condición de fin de la corrida.

Un ejemplo en este sistema: al comenzar el servicio de un docente se programan dos eventos que compiten, el fin por elección en t \+ T\_elección y el vencimiento de la ventana en t \+ τ. Se ejecuta el que ocurra primero y se cancela el otro, lo que reproduce S \= min(T\_elección, τ) sin reglas adicionales. Es la misma lógica de “gana el menor de dos tiempos” de la sección 1.3.

### **4.3 Generación de tiempos aleatorios**

Las variables exponenciales se generan a partir de la distribución acumulada F(t) \= 1 − e^(−λt) de la sección 1.2: si U es uniforme en (0, 1), el valor T \= −ln(1 − U)/λ tiene distribución exponencial con media 1/λ. Un proceso de llegadas de Poisson se genera sumando tiempos entre llegadas exponenciales, y por la relación entre ambas distribuciones la cantidad de llegadas en un período T es de Poisson con media λT. Esto se usa para la validación (sección 3.5). Para el modelo propio, los tiempos de decisión son log-normales, con la media de cada docente tomada de la columna tiempo\_decision\_medio de docentes.csv, y la desconexión se genera como un evento de Bernoulli con probabilidad p \= 0,08.

### **4.4 Réplicas y régimen transitorio**

Cada corrida del simulador es una realización de un proceso estocástico, igual que las curvas de densidad de la figura de transitorio y estado estable de las presentaciones. La bibliografía de análisis de resultados de simulación (Law, 1980; Law, 2015, cap. 9\) distingue dos tipos de simulación: de horizonte finito (terminating), cuando el propio problema define cuándo termina cada corrida, y de estado estable, cuando interesa el comportamiento a largo plazo. La jornada de asignación es del primer tipo: comienza con todos los docentes en lista y termina cuando se atendió a todos o se agotaron los cargos. No se espera que el sistema se estabilice, los resultados dependen de las condiciones iniciales y por eso no hay un período de calentamiento que descartar: las métricas se miden sobre la jornada completa.

Dentro de una misma corrida las observaciones no son independientes (la espera de un docente depende de la de quienes lo preceden), así que no se tratan como una muestra. En cambio, cada réplica independiente (distinta semilla, mismas condiciones iniciales) aporta un valor de cada métrica, y esos valores sí son independientes y con la misma distribución. Con n ≥ 30 réplicas por escenario se informan la media x̄, el desvío s y un intervalo de confianza para la media, x̄ ± t(n−1; 1−α/2)·s/√n. La comparación entre E1, E2 y E3 se hace sobre estos intervalos.

### **4.5 Validación del simulador**

Antes de usar el simulador para comparar E1, E2 y E3, se verifica que reproduce resultados analíticos conocidos de la cátedra, configurándolo con llegadas de Poisson, servicios exponenciales y disciplina FCFS:

| Caso | Resultado esperado |
| :---- | :---- |
| M/M/1, λ \= 4, μ \= 6 por hora | L \= 2 ; Lq \= 1,333 ; W \= 0,5 h ; Wq \= 0,333 h |
| M/M/c, λ \= 2, μ \= 3 por hora | c \= 1: Wq \= 2/3 h, P{Wq \> 0} \= 0,667 ; c \= 2: Wq \= 1/24 h, P{Wq \> 0} \= 0,167 |
| M/M/1/K, λ \= 4, μ \= 6, K \= 5 | λef \= 3,80752 ; W \= 0,3736 h ; P₅ \= 0,04812 |
| M/M/4/10, λ \= 16, μ \= 5 por hora | λef \= 15,42815 ; Lq \= 1,15421 ; Wq \= 0,07481 h |

Como estos valores corresponden al estado estable, a diferencia de la jornada real, la comparación debe hacerse con corridas largas, descartando el período inicial de calentamiento (sección 1.4; Law, 2015, cap. 9). Si el promedio de las réplicas coincide con el valor teórico, se puede confiar en que la lógica de eventos, colas y servidores está bien implementada antes de agregar la ventana τ, la cola de reintentos y la prioridad por puntaje.

## **Fuentes**

* Rivadera, G. R. *Teoría de Colas (Primera Parte): Introducción, procesos de nacimiento y muerte*. Investigación Operativa II, UCASAL.  
* Rivadera, G. R. *Teoría de Colas (Segunda Parte): Notación y modelos de un servidor*. Investigación Operativa II, UCASAL.  
* Rivadera, G. R. *Teoría de Colas (Tercera Parte): Notación y modelos de múltiples servidores*. Investigación Operativa II, UCASAL.  
* Kotha, S. K., Barnum, M. P. y Bowen, D. A. (1996). KeyCorp Service Excellence Management System. *Interfaces*, 26(1), 54-74 (citado en las presentaciones).  
* Resumen de clase de Investigación Operativa II (2026), sobre el trabajo final.  
* Law, A. M. (2015). *Simulation Modeling and Analysis* (5.ª ed.). McGraw-Hill. Cap. 1 (simulación de eventos discretos) y cap. 9 (análisis de resultados).  
* Banks, J., Carson, J. S., Nelson, B. L. y Nicol, D. M. (2014). *Discrete-Event System Simulation*. Pearson. Cap. 3 (principios generales).  
* Law, A. M. (1980). Statistical analysis of the output data from terminating simulations. *Naval Research Logistics Quarterly*, 27(1), 131-143.  
* Elizandro, D. y Taha, H. (2012). *Performance Evaluation of Industrial Systems: Discrete Event Simulation Using Excel/VBA* (2.ª ed.). CRC Press. Bibliografía complementaria, a verificar los capítulos antes de citar.

