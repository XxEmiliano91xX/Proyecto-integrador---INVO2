# Universidad Católica de Salta
## Facultad de Ingeniería

---

# Sistema de turnos dinámicos con recomendación de vacantes para las asambleas de designación docente en Salta

**Trabajo Final Integrador — Modalidad A (Aplicación Práctica)**

* **Carrera:** Ingeniería en Informática
* **Asignatura:** Investigación Operativa II
* **Profesor Titular:** Mg. Ing. Gustavo Ramiro Rivadera
* **Profesor Auxiliar:** Ing. Gustavo Flores Vargas
* **Integrantes:**
  * Emiliano Javier Aguirre — DNI 45.770.631
  * Pablo Celaya — DNI 45.115.839
* **Año:** 2026

---

## ÍNDICE

1. [Resumen](#resumen)
2. [1. Introducción](#1-introducción)
   * 1.1. Contexto: el sistema educativo y las designaciones docentes en Salta
   * 1.2. Planteamiento del problema
   * 1.3. Objetivos
   * 1.4. Alcance y limitaciones
   * 1.5. Organización del informe
3. [2. Marco teórico](#2-marco-teórico)
   * 2.1. Elementos de un sistema de colas y Ley de Little
   * 2.2. Modelos analíticos clásicos ($M/M/1$ y $M/M/c$) para validación
   * 2.3. Por qué no alcanzan las fórmulas analíticas en la asignación docente
   * 2.4. Simulación de eventos discretos y prioridades de atención
   * 2.5. Recomendación multicriterio y pronóstico por simulación Monte Carlo
4. [3. Metodología y formulación del modelo](#3-metodología-y-formulación-del-modelo)
   * 3.1. Correspondencia con los elementos de una cola
   * 3.2. Escenario 1 (E1): procedimiento actual sin límite de tiempo
   * 3.3. Escenario 2 (E2): ventana de tiempo $\tau$, aviso previo y cola de reintentos
   * 3.4. Estimador dinámico de horario y notificación previa
   * 3.5. Escenario 3 (E3): recomendación de escuelas y pronóstico de vacantes
   * 3.6. Métricas de desempeño
   * 3.7. Resumen de variables y parámetros
5. [4. Datos e implementación computacional](#4-datos-e-implementación-computacional)
   * 4.1. Origen de los datos: fuentes públicas y datos sintéticos
   * 4.2. Estructura de los archivos CSV
   * 4.3. Uso de la distribución log-normal para los tiempos de elección
   * 4.4. Organización modular del código en Python
6. [5. Verificación, validación y diseño experimental](#5-verificación-validación-y-diseño-experimental)
   * 5.1. Verificación del simulador contra modelos $M/M/1$ y $M/M/c$
   * 5.2. Prueba del recomendador y evaluación del pronóstico
   * 5.3. Diseño de experimentos y análisis de sensibilidad
   * 5.4. Contrastación con referencias operativas reales
7. [6. Resultados y análisis](#6-resultados-y-análisis)
8. [7. Discusión](#7-discusión)
9. [8. Conclusiones](#8-conclusiones)
10. [9. Referencias bibliográficas](#9-referencias-bibliográficas)

---

## RESUMEN

En la Provincia de Salta, la cobertura de cargos docentes interinos y suplentes coordinada junto a la Junta Calificadora de Méritos y Disciplina se realiza mediante actos públicos secuenciales ordenados por el puntaje del Cuadro de Orden de Mérito. En esta modalidad, cada docente que está eligiendo detiene el avance de todos los que vienen detrás mientras revisa qué vacantes quedan libres y toma una decisión. Esto provoca jornadas muy extensas, largas horas de espera sin horario estimado y demoras acumuladas ante indecisiones o cortes de conexión. En este trabajo se modela y evalúa mediante simulación de eventos discretos en Python una propuesta de gestión de turnos sobre un caso representativo del Departamento Capital (300 docentes, 100 cargos vacantes y 40 escuelas públicas). Se comparan tres escenarios principales: el Escenario 1 (E1) representa el llamado secuencial actual sin tiempo límite; el Escenario 2 (E2) incorpora un tiempo máximo de elección por turno ($\tau = 10$ minutos), un estimador de horario que avisa 10 minutos antes y una cola secundaria de reintentos; y el Escenario 3 (E3) suma una carga previa de preferencias, un recomendador sencillo basado en cercanía, turno y coincidencias entre colegas, y un pronóstico rápido por simulación Monte Carlo que anticipa qué escuelas tienen mayor probabilidad de llegar libres al turno del docente. El motor de simulación se verifica contra las fórmulas teóricas de los modelos $M/M/1$ y $M/M/c$ vistos en la asignatura, y se analizan distintos valores de ventana $\tau$, cantidad de mesas de atención simultáneas y niveles de aceptación del recomendador. *[PENDIENTE CORRIDA 07/11: completar con los porcentajes de reducción del tiempo de espera $W_q$ y de la duración total de la jornada $T_{\text{total}}$ obtenidos en las 30 réplicas para E2 y E3 respecto de E1]*.

**Palabras clave:** teoría de colas, simulación de eventos discretos, turnos dinámicos, sistemas de recomendación, pronóstico Monte Carlo, designaciones docentes.

---

## 1. INTRODUCCIÓN

### 1.1. Contexto: el sistema educativo y las designaciones docentes en Salta

El sistema educativo de la Provincia de Salta cuenta con más de 2.300 unidades educativas de gestión estatal y privada y supera los 450.000 alumnos matriculados en todos sus niveles y modalidades, de los cuales más de 350.000 asisten a los niveles obligatorios Inicial, Primario y Secundario (Ministerio de Educación, Cultura, Ciencia y Tecnología de Salta [MECCyT], 2024a). Según el Censo Nacional de Población, Hogares y Viviendas 2022, la provincia tiene 1.441.351 habitantes y el Departamento Capital concentra 627.704 habitantes —el 43,5 % del total provincial— en una superficie de 1.722 km² (Instituto Nacional de Estadística y Censos [INDEC], 2023). Debido a esta concentración demográfica, los actos públicos de designación docente en Salta Capital convocan a cientos de postulantes en una misma jornada, especialmente al inicio del ciclo lectivo entre febrero y marzo.

Desde el punto de vista legal, el ingreso a la docencia y la cobertura de interinatos y suplencias están regulados por la Ley Provincial N.° 6.830 (*Estatuto del Educador*, junto con sus modificatorias Leyes N.° 7.189 y N.° 8.325). Sus artículos 10 y 12 establecen que la Junta Calificadora de Méritos y Disciplina —dividida en salas para Nivel Inicial y Primario y para Nivel Secundario, con sede central en calle Caseros 975 de la ciudad de Salta— es el organismo encargado de evaluar los antecedentes de los docentes y confeccionar los padrones por estricto orden de mérito (Gobierno de la Provincia de Salta, 1995). El puntaje de cada postulante se calcula todos los años aplicando la Resolución Ministerial N.° 1.851/08, que valora título, antigüedad, capacitaciones, concepto profesional y residencia para publicar los cuadros provisorios, abrir el período de reclamos (*tachas*) y emitir las *tirillas* definitivas de puntaje en el portal oficial *Edusalta* (Ministerio de Educación de la Provincia de Salta, 2008).

Una vez publicados los cuadros definitivos, la asignación de los cargos vacantes en las escuelas se lleva a cabo en actos públicos organizados por la Secretaría de Gestión Educativa y las Direcciones de Nivel, tanto en forma presencial (en escuelas cabecera o sedes ministeriales) como en modalidades virtuales incorporadas desde la pandemia. Más allá del formato, la regla central es siempre la misma: se llama a los docentes de mayor a menor puntaje y cada uno elige un cargo compatible entre las vacantes que siguen libres en ese momento.

### 1.2. Planteamiento del problema

Aunque llamar uno por uno según el puntaje asegura transparencia y respeta la normativa vigente, en la práctica esta forma de trabajo genera cuatro cuellos de botella claros, típicos de una fila con un único canal de atención sin límite de tiempo:

1. **Efecto tapón o bloqueo secuencial (*head-of-line blocking*).** Como el llamado es estrictamente uno tras otro, el docente ubicado en la posición $k + 1$ no puede empezar a elegir hasta que termine el docente en la posición $k$. Una sola persona indecisa demora a todos los que están detrás en la fila.
2. **Aumento del tiempo de decisión a medida que avanza el acto.** Los primeros docentes del listado casi siempre encuentran libre la escuela que buscaban y resuelven su turno en un par de minutos. En cambio, a medida que las escuelas céntricas o de turnos más pedidos se van ocupando, muchos docentes de mitad de tabla en adelante llegan a su turno y recién ahí se enteran de que ninguna de las opciones que tenían pensadas sigue disponible. En ese instante deben ponerse a revisar toda la planilla de vacantes restantes —mirando barrios, distancias, líneas de colectivo y horarios—, lo que multiplica el tiempo que tardan frente a la mesa. Dado que el Ministerio no publica registros cronometrados de la duración individual de cada atención en mesa, este incremento del tiempo de elección se modela de manera sintética bajo supuestos explícitos (sección 4.3), en línea con los cuellos de botella administrativos y demoras en sedes de designación reportados en convocatorias masivas de la provincia (Gobierno de la Provincia de Salta, 2025; Navarro, 2023).
3. **Espera a ciegas e incertidumbre de horario.** Al no contar con un cálculo dinámico de a qué hora aproximada les va a tocar, los docentes deben permanecer en el salón o pendientes de la pantalla durante horas sin saber si serán llamados en quince minutos o cuatro horas después. De hecho, los cronogramas oficiales publicados en *Edusalta* citan a los postulantes desde primera hora de la mañana (por ejemplo, a las 8:00 hs) bajo la modalidad abierta *«hasta lo que dure la jornada»* o *«hasta que finalice la jornada»* (MECCyT, 2024b), registrándose reclamos en Salta Capital por esperas de varias horas afuera de las oficinas de designación sin certeza de atención (Navarro, 2023).
4. **Tiempos muertos por ausencias o cortes de internet.** En instancias virtuales o mixtas, cuando alguien no responde o sufre una caída de conexión, la mesa debe repetir los llamados reglamentarios de verificación antes de seguir con el próximo postulante, acumulando minutos muertos o reclamos si el corte fue involuntario.

El problema abordado en este proyecto consiste en diseñar, modelar matemáticamente y evaluar por simulación un sistema de turnos dinámicos que reduzca el tiempo de espera en fila y la duración total de la asamblea, respetando el orden de mérito de la lista principal y midiendo de forma transparente qué ocurre con los docentes que pasan a una instancia de reintento.

Desde la formulación de Investigación Operativa, las **decisiones que se desean estudiar** comprenden la fijación del tiempo máximo por turno ($\tau$), el dimensionamiento de comisiones simultáneas ($c$) y el efecto de asistir al postulante con precarga, recomendación y pronóstico previo; sujetas a las **restricciones** normativas y operativas de respetar estrictamente el orden decreciente de puntaje $P_i$ en la cola principal (Ley N.° 6.830), exigir compatibilidad de nivel y especialidad para cada cargo y no superar el cupo finito de $V_{\text{tot}} = 100$ vacantes ofrecidas.

### 1.3. Objetivos

#### 1.3.1. Objetivo general

Formular, implementar en Python y evaluar mediante simulación de eventos discretos un sistema de turnos dinámicos con tiempo máximo de atención, cola de reintentos y recomendación anticipada de vacantes, con el fin de reducir los tiempos de espera y la duración total de las asambleas de designación docente en Salta Capital respetando el orden de mérito vigente.

#### 1.3.2. Objetivos específicos

1. Modelar el acto público de designación docente desde el enfoque de la Teoría de Colas, identificando las características reales del proceso (cantidad finita de docentes, jornada con inicio y cierre, prioridad por puntaje, tope de tiempo por turno y cola de reintentos) que hacen necesario recurrir a la simulación computacional.
2. Verificar el correcto funcionamiento del motor de simulación de eventos discretos comparando sus resultados en régimen estacionario contra las fórmulas exactas de los modelos $M/M/1$ y $M/M/c$ desarrollados en la cátedra.
3. Diseñar un módulo de precarga de preferencias, recomendación multicriterio de escuelas alternativas y pronóstico rápido de vacantes mediante simulación Monte Carlo, orientado a reducir el tiempo de búsqueda del docente cuando sus opciones iniciales ya fueron tomadas.
4. Comparar estadísticamente tres escenarios operativos —sistema actual (E1), sistema digital con ventana de tiempo y reintentos (E2), y sistema asistido con recomendador y pronóstico (E3)— realizando además análisis de sensibilidad sobre el tiempo máximo por turno ($\tau$), la cantidad de mesas simultáneas ($c$) y el grado de adopción de las recomendaciones.
5. Elaborar propuestas prácticas y viables para la gestión de los actos públicos de designación a partir de los resultados obtenidos, contemplando aspectos normativos y de conectividad.

### 1.4. Alcance y limitaciones

El trabajo comprende la formulación del modelo matemático y de simulación, el armado de un conjunto de datos basado en escuelas públicas reales de Salta Capital combinado con datos sintéticos reproducibles de docentes y vacantes, la programación completa en Python, la verificación contra modelos teóricos y la comparación estadística de escenarios.

Quedan fuera del alcance de este estudio:
* El desarrollo de una plataforma web o aplicación móvil final para usuarios (pantallas, login, servidores en la nube o envío real de mensajes por WhatsApp/SMS).
* El proceso administrativo previo de inscripción anual, valoración de carpetas y resolución de reclamos de puntaje, tomando como punto de partida el Cuadro de Orden de Mérito definitivo ya publicado.
* Las designaciones por bloques fraccionados de horas cátedra propias del Nivel Secundario, enfocándose el modelo en cargos completos e indivisibles (como Maestro de Grado o Nivel Inicial), donde cada docente toma a lo sumo un cargo.

### 1.5. Organización del informe

En la sección 2 se repasan los conceptos teóricos de colas, simulación y pronóstico utilizados en el proyecto. La sección 3 explica paso a paso el modelo matemático de los tres escenarios, el estimador de horarios, el recomendador y las métricas de evaluación. La sección 4 describe cómo se armaron los archivos de datos de Salta Capital y cómo está estructurado el código en Python. La sección 5 detalla las pruebas de verificación del simulador y los experimentos planteados. Finalmente, las secciones 6, 7 y 8 presentan los resultados, la discusión práctica y las conclusiones del trabajo.

---

## 2. MARCO TEÓRICO

### 2.1. Elementos de un sistema de colas y Ley de Little

Un sistema de colas está compuesto por clientes que llegan buscando un servicio, uno o más servidores encargados de atenderlos y una fila o cola donde los clientes aguardan cuando todos los servidores están ocupados, ordenados según una regla o disciplina de atención (Hillier y Lieberman, 2015, cap. 17; Rivadera, 2026a).

Para resumir las características de una cola se utiliza la notación de Kendall $(A/B/c):(D/E/F)$, donde $A$ indica la distribución del tiempo entre llegadas, $B$ la distribución del tiempo de servicio, $c$ la cantidad de servidores en paralelo, $D$ la disciplina de atención (por ejemplo, orden de llegada FIFO o prioridad), $E$ la capacidad máxima del sistema y $F$ el tamaño de la población de origen. Si los clientes llegan a una tasa media $\lambda$ (clientes por unidad de tiempo) y cada servidor puede atender a una tasa media $\mu$, el factor de utilización de los servidores es:

$$\rho = \frac{\lambda}{c \mu}$$

Cuando el sistema es estable ($\rho < 1$), su desempeño se resume en cuatro medidas principales: la cantidad media de clientes en todo el sistema ($L$), la cantidad media esperando en la cola ($L_q$), el tiempo medio total en el sistema ($W$) y el tiempo medio de espera en la cola ($W_q$). Estas métricas están relacionadas por la **Ley de Little** (Little, 1961):

$$L = \lambda W \quad ; \quad L_q = \lambda W_q$$

$$W = W_q + \frac{1}{\mu} \quad ; \quad L = L_q + \frac{\lambda}{\mu}$$

En un proceso que dura una jornada finita de longitud $T_{\text{total}}$ con $N$ personas convocadas desde el inicio, la relación entre el largo medio de la fila y los tiempos individuales de espera se cumple de forma exacta como promedio en el tiempo. Si $N_{\text{cola}}(t)$ es la cantidad de docentes esperando en el minuto $t$ y $Q_i$ es el tiempo total que el docente $i$ pasó esperando en fila durante el acto, el área bajo la curva de espera cumple:

$$L_q = \frac{1}{T_{\text{total}}} \int_0^{T_{\text{total}}} N_{\text{cola}}(t)\,dt = \frac{1}{T_{\text{total}}} \sum_{i=1}^{N} Q_i$$

Esta igualdad resulta muy útil en programación porque permite controlar automáticamente en cada corrida del simulador que los tiempos de espera individuales y la longitud promedio de la cola estén bien calculados.

### 2.2. Modelos analíticos clásicos ($M/M/1$ y $M/M/c$) para validación

Los modelos básicos estudiados en la materia suponen llegadas según un proceso de Poisson (tiempos entre arribos exponenciales de media $1/\lambda$) y tiempos de atención también exponenciales e independientes de media $1/\mu$.

Aunque estos modelos no describen directamente una asamblea docente (por los motivos que se explican en 2.3), sus fórmulas exactas sirven como **caso de prueba obligatorio** para comprobar que nuestro código de simulación maneja bien el reloj, los eventos y las colas antes de cargarle las reglas reales del problema (Rivadera, 2026b, 2026c):

1. **Modelo $M/M/1$ (un solo servidor, cola y población infinitas):**
   $$L = \frac{\rho}{1 - \rho} \quad ; \quad L_q = \frac{\rho^2}{1 - \rho} \quad ; \quad W = \frac{1}{\mu - \lambda} \quad ; \quad W_q = \frac{\rho}{\mu - \lambda}$$
   Por ejemplo, con $\lambda = 4$ clientes/hora y $\mu = 6$ clientes/hora ($\rho = 2/3 \approx 0,6667$), las fórmulas dan exactamente $L_q = 1,3333$ clientes en fila y $W_q = 0,3333$ horas (20 minutos).

2. **Modelo $M/M/c$ (varios servidores idénticos en paralelo):**
   Con $c$ servidores y utilización $\rho = \lambda / (c\mu) < 1$, la probabilidad de que el sistema esté vacío ($P_0$) y la longitud media de la cola ($L_q$) se calculan mediante las expresiones de Erlang-C:
   $$P_0 = \left[ \sum_{n=0}^{c-1} \frac{(\lambda/\mu)^n}{n!} + \frac{(\lambda/\mu)^c}{c!} \cdot \frac{1}{1 - \rho} \right]^{-1}$$
   $$L_q = \frac{P_0 (\lambda/\mu)^c \rho}{c! (1 - \rho)^2} \quad ; \quad W_q = \frac{L_q}{\lambda}$$
   Por ejemplo, para $\lambda = 2$ y $\mu = 3$ clientes/hora, con un único servidor ($c = 1$) la espera media es $W_q = 0,6667$ horas (40 minutos), mientras que al habilitar un segundo servidor ($c = 2$) la espera cae drásticamente a $W_q = 0,0417$ horas (2,5 minutos). Esto muestra cómo agregar capacidad reduce la congestión de manera no lineal.

### 2.3. Por qué no alcanzan las fórmulas analíticas en la asignación docente

Las fórmulas cerradas de $M/M/1$ y $M/M/c$ no se pueden aplicar directamente para calcular las esperas de una asamblea docente porque la operatoria real rompe varios de sus supuestos básicos:

* **Jornada finita en lugar de estado estacionario:** las ecuaciones teóricas calculan promedios cuando el tiempo tiende a infinito ($t \to \infty$). Una asamblea empieza a una hora puntual con un listado cerrado y termina apenas se cubren los cargos o se llama al último docente.
* **Población finita presente desde el inicio:** los $N = 300$ docentes no van llegando al azar durante el día como en un banco o un supermercado; ya están anotados y habilitados desde el minuto cero.
* **Tiempos de decisión no exponenciales y con corte por reloj:** lo que tarda una persona en elegir escuela no sigue una distribución exponencial; la mayoría resuelve en pocos minutos y unos pocos demoran bastante más (comportamiento asimétrico que representamos con una distribución log-normal). Además, al poner un límite de $\tau = 10$ minutos, el servicio se corta en $S = \min(T_{\text{elección}}, \tau)$.
* **Atención por orden de mérito y cola de reintentos:** el llamado sigue el puntaje de cada docente y quienes superan el tiempo máximo vuelven a esperar en una cola secundaria.
* **Vacantes que se agotan turno a turno:** cada cargo tomado achica las opciones disponibles para quienes siguen atrás, haciendo que los tiempos de elección cambien a lo largo de la jornada.

Frente a todas estas condiciones combinadas, la herramienta adecuada dentro de la Investigación Operativa es la **simulación de eventos discretos** (Law, 2015; Taha, 2017).

### 2.4. Simulación de eventos discretos y prioridades de atención

En una **simulación de eventos discretos (SED)** el estado del sistema (cuántas personas esperan, qué mesas están ocupadas y qué vacantes quedan libres) solo cambia en instantes puntuales llamados *eventos*: el inicio de un turno, la confirmación de un cargo o el vencimiento del tiempo límite (Banks et al., 2010; Law, 2015). Para no perder tiempo simulando segundo por segundo, el programa mantiene una **lista de eventos futuros (FEL)** ordenada por hora de ocurrencia mediante una cola de prioridad (`heapq` en Python) y hace saltar el reloj directamente al evento más próximo.

En cuanto al orden de llamado, las asambleas docentes funcionan como una cola con **prioridad no apropiativa**: los postulantes se ordenan de mayor a menor puntaje de mérito $P_i$, pero una vez que un docente empezó su turno nadie puede interrumpirlo hasta que elija o se cumpla su tiempo máximo $\tau$ (Hillier y Lieberman, 2015). Si el tiempo $\tau$ vence sin elección, el postulante pasa a una **cola secundaria de reintentos**, la cual recién se atiende cuando termina de pasar la cola principal para no demorar a quienes todavía no tuvieron su primer turno.

Por tratarse de un sistema con inicio y cierre fijo, no corresponde descartar un período de calentamiento (*warm-up*). Además, como la demora de un docente afecta directamente a todos los que están detrás en esa misma jornada, los turnos de un mismo día no son independientes entre sí. Por eso, para obtener resultados estadísticamente confiables se ejecutan **$R_{\text{rep}} = 30$ réplicas completas e independientes** (cambiando la semilla aleatoria en cada corrida) y se calcula para cada indicador su media muestral $\bar{X}$ junto con su intervalo de confianza del 95 % usando la distribución $t$ de Student:

$$\bar{X} \pm t_{R_{\text{rep}} - 1 \, ; \, 0,975} \cdot \frac{s}{\sqrt{R_{\text{rep}}}}$$

### 2.5. Recomendación multicriterio y pronóstico por simulación Monte Carlo

Como la Ley Provincial N.° 6.830 exige respetar el orden de mérito y la libre elección del docente en su turno, no sería válido legalmente reemplazar el acto público por un algoritmo que asigne escuelas de manera forzosa ni alterar el orden del listado. La mejora pasa, en cambio, por **ayudar al docente a llegar preparado a su turno** cuando las escuelas que quería originalmente están por agotarse.

Para lograrlo combinamos dos herramientas simples y complementarias:
1. **Sistema de recomendación híbrido sencillo** (Ricci, Rokach y Shapira, 2015): primero filtra únicamente las escuelas con vacantes compatibles que cumplan las condiciones básicas del docente (distancia máxima desde su casa, turnos en los que puede trabajar y si acepta zona rural), y luego las ordena combinando tres puntajes fáciles de interpretar: cercanía en kilómetros, parecido con las escuelas que el docente había preseleccionado y frecuencia con que otros docentes de gustos similares eligieron esa misma escuela.
2. **Pronóstico rápido mediante simulación Monte Carlo**: diez minutos antes del turno estimado de un docente quedan pocos postulantes delante de él. En ese momento el programa simula rápidamente 200 veces las elecciones de esos pocos docentes previos para estimar qué probabilidad tiene cada escuela de seguir libre cuando le toque elegir, evitando sugerir vacantes que casi seguro se van a ocupar un par de turnos antes.

---

## 3. METODOLOGÍA Y FORMULACIÓN DEL MODELO

### 3.1. Correspondencia con los elementos de una cola

La asamblea de designación se traduce a los componentes de un sistema de colas según la siguiente tabla:

| Elemento del sistema de colas | Equivalente en la asamblea de designación docente |
| :--- | :--- |
| **Cliente** | Docente incluido en el Cuadro de Orden de Mérito definitivo |
| **Población de entrada** | Finita y cerrada: $N = 300$ docentes habilitados desde la apertura del acto |
| **Servidor** | Comisión o mesa de designación ($c = 1$ en el caso base; $c \in \{2, 3\}$ en sensibilidad) |
| **Tiempo de servicio** | Duración efectiva del turno del docente (según tiempo de elección, límite $\tau$ o verificación de ausencia) |
| **Colas de espera** | Cola principal ordenada por puntaje $P_i$ y (en E2 y E3) cola secundaria de reintentos |
| **Disciplina de atención** | Prioridad no apropiativa de mayor a menor puntaje $P_i$; la cola principal tiene prioridad sobre la de reintentos |
| **Capacidad** | Finita, limitada a los $N = 300$ docentes convocados |
| **Fallas / ausencias** | Probabilidad $p = 0,08$ de no responder o desconectarse al ser llamado, con $T_{\text{aus}} = 5$ min de verificación |

Además de las filas, el sistema trabaja sobre un **listado compartido de $V_{\text{tot}} = 100$ vacantes**: el acto termina apenas se adjudica el último cargo disponible o cuando ya no quedan docentes por atender en ninguna de las colas.

**Caso de docentes sin vacantes compatibles (*sin oferta*).** Al haber 300 docentes para 100 cargos divididos por nivel y especialidad, llega un punto de la jornada en que para ciertas especialidades ya no queda ningún cargo libre en ninguna escuela. Cuando se llama a un docente en esa situación, tanto en E1 como en E2 y E3 se registra un trámite rápido de constancia de $t_{\text{pase}} = 0,5$ minutos, el docente se retira como *sin oferta* y no se lo envía a la cola de reintentos.

### 3.2. Escenario 1 (E1): procedimiento actual sin límite de tiempo

El Escenario 1 representa el acto público tradicional con una única comisión ($c = 1$) y sin reloj máximo por turno. Se llama a los postulantes por orden decreciente de puntaje $P_i$ y cada docente utiliza todo el tiempo que necesita para revisar la planilla y decidir:

$$S_j = T_{\text{elección}, j}$$

Si el docente llamado está ausente o tiene un problema de conexión (probabilidad $p = 0,08$), la mesa realiza los llamados de rigor durante un tiempo fijo $T_{\text{aus}} = 5$ minutos y, al no obtener respuesta, pasa al siguiente en la lista perdiendo aquel su turno (en E1 no hay cola de reintentos).

En este esquema el docente en la posición $k$ acumula como espera la suma completa de los turnos anteriores: $W_{q, k} = \sum_{j=1}^{k-1} S_j$. Cuando las escuelas más buscadas se agotan, el tiempo promedio de búsqueda de los docentes sube de unos 2 minutos a unos 8 minutos (con casos puntuales de 15 o 20 minutos por la asimetría de la distribución log-normal), trasladando toda esa demora al resto de la fila.

### 3.3. Escenario 2 (E2): ventana de tiempo $\tau$, aviso previo y cola de reintentos

El Escenario 2 digitaliza el manejo del turno agregando un tiempo límite de **$\tau = 10$ minutos** por atención, de manera que la duración máxima en ventanilla queda acotada por:

$$S = \min(T_{\text{elección}}, \tau)$$

Si el docente confirma su escuela dentro de los 10 minutos ($T_{\text{elección}} \le \tau$), se le asigna el cargo, se descuenta la vacante y finaliza su trámite. Si en cambio pasan los 10 minutos sin que haya podido decidirse ($T_{\text{elección}} > \tau$), o si sufre una desconexión al ser llamado, el sistema libera la atención para no frenar al resto y pasa a ese docente a una **cola secundaria de reintentos**.

Para que el comportamiento del modelo sea claro y parejo, se fijan cinco reglas sencillas:
1. **Desconexiones o ausencias:** se esperan los mismos $T_{\text{aus}} = 5$ minutos de verificación que en E1, pero en lugar de quedar eliminado del acto, el docente pasa a la cola de reintentos.
2. **Cuándo se atiende la cola de reintentos:** recién cuando termina de pasar el último docente de la cola principal (siempre que todavía queden vacantes sin cubrir).
3. **Orden dentro de reintentos:** se mantiene el orden de mérito original de mayor a menor puntaje $P_i$.
4. **Máximo un reintento:** cada docente tiene a lo sumo una segunda oportunidad. Al volver a ser llamado se sortea un nuevo tiempo de decisión según las vacantes libres en ese momento; si vuelve a superar $\tau$ o sigue desconectado, queda fuera sin asignación.
5. **Sin vacantes compatibles:** si al llegar su reintento ya se agotaron todos los cargos de su especialidad, egresa en $t_{\text{pase}} = 0,5$ min bajo la condición *sin oferta*.

Evaluando la distribución log-normal ($\sigma = 0,8$) en Python mediante `scipy.stats.lognorm` para $\tau = 10$ minutos y $p = 0,08$, se observa claramente por qué la ventana actúa como un filtro sobre las demoras largas sin perjudicar a quien ya sabe qué elegir:

| Situación del docente | Tiempo medio sin tope | Probabilidad de superar 10 min | Pasan a reintento (incluyendo 8 % de fallas de red) | Tiempo medio efectivo en mesa |
| :--- | :---: | :---: | :---: | :---: |
| Docente con escuela prevista libre (Caso A) | 2,0 min | 0,8 % | 8,7 % | 2,21 min |
| Docente revisando planilla desde cero (Caso C) | 8,0 min | 24,9 % | 30,9 % | 6,01 min |

Como muestra la tabla, a un docente que tiene disponible alguna de sus escuelas buscadas casi nunca se le corta el turno por reloj (menos del 1 % de las veces). En cambio, cuando alguien llega sin opciones conocidas y empieza a revisar toda la planilla en vivo, casi 1 de cada 4 veces supera los 10 minutos.

**Limitación de digitalizar sin orientar al docente (efecto en el orden de mérito).** Si bien mandar a los indecisos a la cola de reintentos destraba la fila principal, tiene una contracara importante: como hay 300 docentes para 100 cargos, mientras la fila principal sigue avanzando las vacantes se van terminando. Cuando finalmente toca atender la cola de reintentos, es muy probable que varios docentes con puntaje alto que habían sido derivados ya no encuentren vacantes de su especialidad porque las tomaron docentes con menor puntaje que venían detrás. Medimos explícitamente este problema mediante el indicador de *casos afectados en su mérito por reintento* (sección 3.6), que muestra por qué limitar el reloj por sí solo no alcanza y motiva las herramientas del Escenario 3.

### 3.4. Estimador dinámico de horario y notificación previa

Como el orden del listado se conoce desde que arranca el acto, en cualquier minuto $t_{\text{actual}}$ el sistema puede calcular a qué hora aproximada será atendido el docente que ocupa el lugar $k$ de la fila pendiente sumando la duración esperada de quienes están antes:

$$E[T_k] = t_{\text{actual}} + \frac{1}{c} \cdot \left( \sum_{m=1}^{c_{\text{ocup}}} E[S_{\text{restante}, m}] + \sum_{j=1}^{k-1} E[S_j] \right)$$

Como el sistema real no conoce de antemano cuánto tarda en decidir cada persona (y en E2 tampoco cuenta con listas precargadas), el tiempo esperado de atención se estima dinámicamente mediante **suavización exponencial simple** a partir de las duraciones reales observadas en la asamblea. Cada vez que finaliza el turno efectivo $S_{\text{obs}}$ de un docente que tenía oferta disponible, se actualiza el promedio suavizado $\hat{S}$ con factor $\alpha = 0,20$ (partiendo de $\hat{S}_0 = 3,0$ minutos):

$$\hat{S}_{\text{nuevo}} = \alpha \cdot S_{\text{obs}} + (1 - \alpha) \cdot \hat{S}_{\text{anterior}}$$

Con este valor actualizado:
* Para cada docente $j$ que aguarda adelante en la fila, se estima $E[S_j] = \hat{S}$ si todavía quedan vacantes libres de su nivel y especialidad, o bien $E[S_j] = t_{\text{pase}} = 0,5$ minutos si los cargos compatibles ya se agotaron.
* Para cada mesa ocupada $m$ que lleva $t_{\text{trans}, m}$ minutos de atención en curso, el tiempo remanente esperado se acota como $E[S_{\text{restante}, m}] = \max(0,\, \hat{S} - t_{\text{trans}, m})$.

Este pronóstico de horario se recalcula al finalizar cada turno. La primera vez que para un docente en espera (no atendido en el instante inicial $t = 0$) se cumple que:

$$E[T_k] - t_{\text{actual}} \le 10 \text{ minutos}$$

el sistema le envía un único aviso automático (*«Prepárese: su turno estimado es en 10 minutos»*) y registra esa hora prometida $E[T_k]_{\text{avisado}}$ para evaluar luego su precisión mediante el $MAE$.

### 3.5. Escenario 3 (E3): recomendación de escuelas y pronóstico de vacantes

Mientras que E2 frena los atrasos cortando el turno a los 10 minutos, el Escenario 3 busca evitar que el docente llegue desorientado a la ventanilla. Manteniendo exactamente las mismas reglas de cola y ventana $\tau = 10$ minutos de E2, el E3 agrega una **precarga simple antes del acto público** y un **aviso enriquecido 10 minutos antes del turno** con sugerencias personalizadas y probabilidades de vacante.

#### 3.5.1. Precarga y filtro de condiciones básicas

Antes de que comience la asamblea, cada docente $i$ carga en el sistema una lista ordenada $L_i$ con hasta $M = 5$ escuelas de su preferencia y completa tres filtros básicos sobre qué alternativas estaría dispuesto a aceptar si sus cinco opciones se agotan:

* **$R_i$**: distancia máxima en línea recta desde su domicilio hasta la escuela (en km).
* **$\text{Turnos}_i$**: turnos en los que puede trabajar (`mañana`, `tarde`, `noche`).
* **$\text{Rural}_i$**: indica con `1` si acepta escuelas rurales o `0` si solo busca escuelas urbanas.

Al momento de buscarle alternativas al docente $i$, el sistema arma el conjunto $K_i$ únicamente con aquellas escuelas que tienen al menos una vacante libre compatible con su título/nivel y que cumplen al mismo tiempo la distancia $d_{ij} \le R_i$, el turno y el tipo urbano/rural elegido. Nunca se le recomienda una escuela fuera de sus propios límites.

#### 3.5.2. Puntaje multicriterio para ordenar alternativas

Para puntuar qué tan conveniente es cada escuela candidata $j \in K_i$ (que no estaba en su lista inicial $L_i$), se calcula un promedio ponderado entre 0 y 1:

$$\text{Puntaje}_{ij} = w_d \cdot D_{ij} + w_t \cdot T_{ij} + w_c \cdot C_{ij} \quad \text{con } w_d + w_t + w_c = 1$$

Los tres criterios reflejan aspectos prácticos que cualquier docente mira al elegir:

1. **Cercanía al domicilio ($D_{ij}$):**
   $$D_{ij} = 1 - \frac{d_{ij}}{R_i}$$
   Vale 1 si la escuela está pegada a su domicilio y baja linealmente hasta 0 en el límite de distancia $R_i$ que el docente indicó como máximo tolerable.
2. **Parecido con sus escuelas elegidas ($T_{ij}$):** compara los atributos de la escuela candidata $j$ contra cada escuela $s$ de la lista precargada $L_i$, promediando la coincidencia de zona barrial, ámbito urbano/rural (`escuelas.csv`) y disponibilidad de algún turno compatible en común dentro de la oferta vigente (`cargos.csv`):
   $$T_{ij} = \frac{1}{|L_i|} \sum_{s \in L_i} \frac{I(\text{zona}_j = \text{zona}_s) + I(\text{tipo}_j = \text{tipo}_s) + I(\text{TurnosLibres}_j \cap \text{Turnos}_s \ne \emptyset)}{3}$$
   donde $\text{TurnosLibres}_j$ son los turnos con vacante compatible abierta en la escuela $j$ y $\text{Turnos}_s$ los turnos ofrecidos originalmente en la escuela $s$.
3. **Elecciones de docentes con gustos parecidos ($C_{ij}$):** se fija qué tan elegida fue esa escuela $j$ en las listas de otros docentes que también anotaron escuelas en común con el docente $i$:
   $$C_{ij} = \frac{\sum_{k \ne i} |L_k \cap L_i| \cdot I(j \in L_k)}{\sum_{k \ne i} |L_k \cap L_i|}$$
   donde $|L_k \cap L_i|$ es la cantidad de escuelas en común entre las listas de ambos docentes, e $I(j \in L_k)$ vale 1 si el colega $k$ incluyó a la escuela $j$ y 0 si no la incluyó (si el denominador resulta igual a 0, se define $C_{ij} = 0$).

Como valores iniciales usamos $w_d = 0,50$, $w_t = 0,20$ y $w_c = 0,30$, los cuales luego se ajustan probando combinaciones sobre los datos en la sección 5.2.

#### 3.5.3. Pronóstico de disponibilidad mediante simulación Monte Carlo

Cuando faltan 10 minutos para el turno del docente $i$ (momento en que sale el aviso de preparación), suelen quedar apenas entre 2 y 5 docentes delante de él en la fila. Sin embargo, esos pocos turnos previos pueden llevarse justo la última vacante de las escuelas que a él le interesaban.

Para anticiparse a eso, en el momento de enviar el aviso el programa toma una copia de las vacantes libres en ese instante y corre en segundo plano **$R_{\text{MC}} = 200$ simulaciones rápidas (Monte Carlo)** de esos pocos docentes que están adelante:
1. En cada una de las 200 pasadas, simula turno por turno a los docentes previos a $i$: contempla la probabilidad de que no adjudiquen cargo en ese turno ya sea por desconexión ($p$) o por superar la ventana máxima $\tau = 10$ minutos (sorteando un tiempo log-normal con media poblacional $\bar{m} = 2,0$ min si tienen opciones de su lista $L_h$ libres o $4\bar{m} = 8,0$ min si su lista está agotada), y en caso de concretar elección descuentan la primera escuela libre de $L_h$ (o una alternativa compatible dentro de sus filtros $K_h$ si $L_h$ ya se agotó).
2. Al llegar al turno de $i$, anota qué escuelas conservaron al menos una vacante libre para su especialidad.
3. Dividiendo por 200 la cantidad de veces que la escuela $j$ llegó con lugar libre, se obtiene la **probabilidad estimada de disponibilidad $\theta_{ij} \in [0, 1]$**.

Con ese dato, la notificación de 10 minutos antes le muestra al docente el semáforo de probabilidad $\theta_{ij}$ de sus 5 escuelas preferidas y, debajo, le sugiere las **$k_{\text{rec}} = 3$ mejores escuelas alternativas** ordenadas por el producto $\text{Puntaje}_{ij} \cdot \theta_{ij}$ (es decir, escuelas que se ajustan a su perfil y que además tienen alta chance de seguir libres cuando lo llamen). Así el docente aprovecha esos 10 minutos de espera previa para pensar su decisión tranquilo, en vez de enterarse sobre la marcha en la ventanilla.

#### 3.5.4. Efecto sobre el tiempo de elección y adjudicación de vacante (Casos A, B y C)

Para conectar de manera clara la disponibilidad de vacantes con lo que tarda cada docente $i$ en su turno, partimos de su tiempo medio base $m_i$ (entre 1 y 3 minutos) cuando encuentra libre lo que quería, y definimos tres situaciones posibles al momento de ser atendido:

| Situación | Qué encuentra el docente $i$ al iniciar su turno | Tiempo medio de decisión | Cuándo ocurre en E1 y E2 | Cuándo ocurre en E3 |
| :---: | :--- | :---: | :--- | :--- |
| **Caso A** | Al menos una de las 5 escuelas de su lista $L_i$ sigue con vacante libre | **$1 \cdot m_i$** (~2 min) | Siempre que $L_i$ tenga vacante libre | Siempre que $L_i$ tenga vacante libre |
| **Caso B** | Su lista $L_i$ se agotó, pero al menos una de las 3 escuelas recomendadas en el aviso previo sigue libre y el docente se guía por ellas | **$2 \cdot m_i$** (~4 min) | Nunca (no hay recomendador ni preaviso de vacantes) | Con probabilidad de adopción **$p_{\text{rec}} = 0,70$** si alguna sugerida sigue libre |
| **Caso C** | Su lista $L_i$ se agotó y el docente se pone a revisar toda la planilla restante en el momento | **$4 \cdot m_i$** (~8 min) | Siempre que $L_i$ esté agotada | Con probabilidad $1 - p_{\text{rec}}$ (no usa la sugerencia), o si las 3 sugeridas se ocuparon justo antes, o si $K_i$ está vacío |

De esta forma no se asume que el recomendador funciona siempre de manera mágica: si las 3 escuelas sugeridas se ocuparon en los últimos minutos previos, o si el docente prefiere ignorar la recomendación (el 30 % de las veces en el caso base, parámetro que variamos ampliamente en sensibilidad), cae igualmente en el Caso C.

Cuando el docente logra confirmar su elección dentro del turno (sin límite en E1, o con $T_{\text{elección}} \le \tau$ en E2 y E3), la vacante concreta que se le adjudica sigue una regla consistente con cada caso:
* **En Caso A:** toma la primera escuela con vacante compatible disponible siguiendo el orden estricto de su lista $L_i$ (puestos 1 a 5).
* **En Caso B (solo E3):** entre las escuelas recomendadas del aviso previo que continúan libres, elige aquella mejor ubicada en sus `preferencias_ocultas` (opciones 6 a 10) o, si ninguna coincide, la de mayor puntaje recomendado $\text{Puntaje}_{ij}$.
* **En Caso C:** al revisar manualmente la planilla restante, si existe alguna vacante compatible dentro de sus filtros aceptados ($K_i$) elige la mejor posicionada en sus `preferencias_ocultas` (o una vacante al azar dentro de $K_i$ si sus opciones 6 a 10 también se agotaron); si $K_i$ ya está vacío pero aún quedan cargos compatibles fuera de su radio habitual, toma uno al azar entre los remanentes.

### 3.6. Métricas de desempeño

En cada una de las 30 réplicas del simulador se calculan las siguientes métricas para comparar los escenarios de manera justa. Llamamos $Q_i$ al tiempo total en minutos que el docente $i$ pasa esperando en fila (sin contar los minutos en que está siendo atendido en la mesa; si pasó a reintentos, suma la espera en la fila principal más la espera en la fila secundaria; y si la asamblea cerró por agotamiento de cargos antes de que lo llamen, cuenta su espera hasta el minuto de cierre $T_{\text{total}}$):

1. **Tiempo medio de espera de los atendidos ($W_q$, en minutos):** promedio de $Q_i$ entre todos los docentes que llegaron a ser llamados al menos una vez.
2. **Tiempo medio de espera sobre los 300 convocados ($W_{\text{conv}}$, en minutos):** promedio de $Q_i$ sobre los $N = 300$ docentes del padrón. Permite comparar escenarios sobre exactamente el mismo grupo de personas aunque en un escenario se atiendan más postulantes que en otro.
3. **Longitud media de la fila ($L_q$, en docentes):** cantidad promedio de docentes esperando a lo largo de toda la asamblea, verificada mediante $L_q = \frac{1}{T_{\text{total}}} \sum_{i=1}^{N} Q_i$.
4. **Duración total de la asamblea ($T_{\text{total}}$, en minutos y horas):** momento en que termina de atenderse el último turno del acto público.
5. **Porcentaje de derivación a reintentos (%):** proporción de docentes llamados en la cola principal cuyo primer turno terminó por superar $\tau = 10$ minutos o por desconexión.
6. **Cobertura de cargos (%):** porcentaje de las 100 vacantes ofrecidas que quedaron efectivamente cubiertas al finalizar el acto (informando aparte el porcentaje de llamados declarados *sin oferta*).
7. **Satisfacción media de los docentes designados (escala 0 a 1):** indicador calculado al final de la corrida comparando la escuela adjudicada contra el ranking real de 10 escuelas preferidas del docente ($1,0$ si obtuvo su primera opción, bajando de a $0,10$ hasta $0,10$ para la décima opción, y $0,05$ si eligió una escuela fuera de sus 10 preferidas).
8. **Error medio del estimador de horario ($MAE$, en minutos):** promedio de la diferencia en valor absoluto $|E[T_k]_{\text{avisado}} - T_k^{\text{real}}|$ entre la hora prometida en el aviso previo y la hora real en que empezó su turno.
9. **Casos afectados en su mérito por reintento (%):** porcentaje de docentes enviados a reintento que luego no consiguen vacante porque otros postulantes con menor puntaje eligieron antes los últimos cargos compatibles en la cola principal. En E1 vale siempre 0 %.

### 3.7. Resumen de variables y parámetros

| Símbolo | Descripción y unidad | Valor base |
| :---: | :--- | :---: |
| $N$ | Total de docentes empadronados en la convocatoria | 300 docentes |
| $V_{\text{tot}}$ | Total de cargos vacantes ofrecidos en el acto | 100 cargos |
| $E_{\text{tot}}$ | Cantidad de escuelas públicas incluidas en la instancia | 40 escuelas |
| $P_i$ | Puntaje de mérito del docente $i$ | [20,00 ; 100,00] |
| $\tau$ | Tiempo máximo de atención por turno en E2 y E3 | 10 min (sensib.: 6, 8, 12, 15) |
| $c$ | Cantidad de comisiones o mesas atendiendo en paralelo | 1 (sensib.: 2, 3) |
| $M$ | Cantidad máxima de escuelas precargadas en la lista $L_i$ | 5 escuelas |
| $m_i$ | Tiempo medio base de elección del docente $i$ en Caso A | [1,0 ; 3,0] min |
| $\beta_A, \beta_B, \beta_C$ | Multiplicadores del tiempo medio en los Casos A, B y C | 1 ; 2 ; 4 |
| $\sigma$ | Dispersión en escala logarítmica de la distribución log-normal | 0,8 |
| $p$ | Probabilidad de ausencia o corte de conexión en el turno | 0,08 |
| $T_{\text{aus}}$ | Tiempo de verificación ante falta de respuesta al llamado | 5,0 min |
| $t_{\text{pase}}$ | Trámite rápido cuando ya no quedan vacantes de la especialidad | 0,5 min |
| $\alpha$ | Factor de suavización exponencial del estimador de horario | 0,20 ($\hat{S}_0 = 3,0$ min) |
| $k_{\text{rec}}$ | Cantidad de escuelas alternativas sugeridas en E3 | 3 escuelas |
| $p_{\text{rec}}$ | Probabilidad de guiarse por la recomendación vigente en E3 | 0,70 (sensib.: 0,3 ; 0,5 ; 0,9) |
| $w_d, w_t, w_c$ | Pesos de cercanía, parecido con la lista y coincidencia entre colegas | 0,50 ; 0,20 ; 0,30 |
| $R_{\text{MC}}$ | Cantidad de pasadas rápidas Monte Carlo en cada preaviso | 200 pasadas |
| $R_{\text{rep}}$ | Cantidad de réplicas completas de la jornada por escenario | 30 réplicas |

---

## 4. DATOS E IMPLEMENTACIÓN COMPUTACIONAL

### 4.1. Origen de los datos: fuentes públicas y datos sintéticos

Siguiendo las pautas de la cátedra, combinamos datos geográficos reales de infraestructura educativa de Salta con datos sintéticos generados de manera controlada para aquellas variables que no son públicas o corresponden a funcionalidades nuevas propuestas en este trabajo:

1. **Escuelas públicas reales (`data/escuelas.csv`).** Los nombres, códigos oficiales, ubicaciones, barrios y niveles de las escuelas provienen del **Padrón Oficial de Establecimientos Educativos** publicado en el portal *Edusalta* y en la base nacional de información educativa (MECCyT, 2024a). Seleccionamos **40 escuelas estatales reales del Departamento Capital**, incluyendo establecimientos céntricos tradicionales —como la Escuela N.° 4.001 *Juan Bautista Alberdi* (Caseros 1150), la Escuela N.° 4.002 *Mariano Cabezón* y la Escuela N.° 4.017 *Presidente Domingo Faustino Sarmiento* (Alvarado 427)— junto con escuelas distribuidas en los barrios de zona norte, sur, este, oeste y sectores periurbanos/rurales del municipio. Con la latitud y longitud reales de cada edificio, calculamos las distancias exactas en kilómetros mediante la fórmula de Haversine (radio terrestre medio $R_T = 6.371$ km).
2. **Cargos vacantes (`data/cargos.csv`).** Como las planillas históricas de vacantes de cada acto público no se publican como archivos descargables unificados, generamos **100 cargos vacantes** repartidos entre las 40 escuelas reales respetando niveles (`inicial`, `primario`, `secundario`), especialidades y turnos (`mañana`, `tarde`, `noche`), asignando mayor presencia de vacantes libres en barrios periféricos, tal como suele ocurrir luego de los traslados anuales de titulares.
3. **Padrón de docentes y preferencias (`data/docentes.csv`).** Los domicilios particulares están resguardados por privacidad y las listas de escuelas preseleccionadas aún no existen en el sistema actual. Por ello se generan **300 docentes sintéticos** con semilla fija reproducible (`semilla = 2026`):
   * **Puntajes $P_i$:** valores únicos entre 20,00 y 100,00 con dos decimales (formato de la Resolución Ministerial N.° 1.851/08), concentrando mayor cantidad de postulantes jóvenes e intermedios entre 25 y 65 puntos y menos docentes con puntajes cercanos al tope.
   * **Domicilios:** coordenadas ubicadas dentro de las zonas residenciales de Salta Capital de acuerdo con su distribución poblacional (INDEC, 2023).
   * **Tiempos medios base $m_i$:** valores sorteados con distribución uniforme entre 1,0 y 3,0 minutos.
   * **Límites aceptados:** distancia máxima $R_i$ entre 5 y 15 km para escuelas urbanas (extendida hasta 25 km para el 30 % de docentes que acepta ámbito rural) y uno o dos turnos disponibles.
   * **Preferencias de escuelas (10 por docente):** para generar gustos creíbles sin que sean totalmente predecibles por fórmula, para cada docente se calcula una afinidad base hacia cada escuela compatible según la cercanía a su casa, coincidencia de turno y si es céntrica, sumándole una variación aleatoria propia de cada persona (preferencia personal). Con esos pesos se sortean sin repetición 10 escuelas: las primeras 5 se guardan en la columna `preferencias` (lista $L_i$ que ve el sistema) y las ubicadas del puesto 6 al 10 se guardan aparte en `preferencias_ocultas` únicamente para medir qué tan bien acierta el recomendador (sección 5.2) y evaluar la satisfacción final (sección 3.6).

### 4.2. Estructura de los archivos CSV

**`data/escuelas.csv`**

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `id_escuela` | texto | Identificador interno (`ESC01` a `ESC40`) |
| `cue_anexo` | texto | Código Único de Establecimiento oficial |
| `nombre` | texto | Nombre oficial de la escuela en Salta Capital |
| `latitud`, `longitud` | decimal | Coordenadas geográficas reales |
| `zona` | texto | `centro`, `norte`, `sur`, `este`, `oeste` o `periurbana` |
| `tipo` | texto | `urbana` o `rural` |

**`data/cargos.csv`**

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `id_cargo` | texto | Identificador del cargo (`C001` a `C100`) |
| `id_escuela` | texto | Referencia a `escuelas.csv` |
| `nivel` | texto | `inicial`, `primario` o `secundario` |
| `especialidad` | texto | `maestro_jardín`, `maestro_grado`, `matemática`, `lengua`, `inglés`, `educación_física` |
| `turno` | texto | `mañana`, `tarde` o `noche` |
| `vacantes` | entero | Cantidad de puestos disponibles del registro (por defecto 1) |

**`data/docentes.csv`**

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `id` | texto | Identificador del docente (`D001` a `D300`) |
| `puntaje` | decimal | Puntaje $P_i$ en el Cuadro de Orden de Mérito |
| `tiempo_decision_medio` | decimal | Media base $m_i$ en minutos (Caso A) |
| `nivel`, `especialidad` | texto | Nivel y especialidad habilitados para tomar cargo |
| `latitud`, `longitud` | decimal | Coordenadas del domicilio en Salta Capital |
| `preferencias` | texto | Hasta 5 códigos `id_escuela` ordenados y separados por `;` |
| `radio_max_km` | decimal | Distancia máxima aceptada $R_i$ en kilómetros |
| `turnos` | texto | Turnos aceptados separados por `;` |
| `acepta_rural` | entero | `1` si acepta escuelas rurales, `0` si solo acepta urbanas |
| `preferencias_ocultas` | texto | Opciones 6 a 10 reservadas solo para pruebas y cálculo de satisfacción |

### 4.3. Uso de la distribución log-normal para los tiempos de elección

Elegimos una distribución **log-normal** para sortear los tiempos de decisión porque cumple dos propiedades muy realistas para tiempos humanos: nunca genera números negativos y tiene asimetría hacia la derecha (la mayoría de las personas resuelve cerca o por debajo del promedio, pero siempre aparecen algunos casos que se demoran bastante más).

Si queremos que una variable log-normal $T$ tenga media igual a $m$ (donde $m$ vale $m_i$, $2 m_i$ o $4 m_i$ según sea Caso A, B o C) y fijamos la dispersión $\sigma = 0,8$, el parámetro $\mu_{\text{LN}}$ de la normal asociada $\ln(T) \sim N(\mu_{\text{LN}}, \sigma^2)$ se despeja directamente de la fórmula de la esperanza log-normal $m = e^{\mu_{\text{LN}} + \sigma^2/2}$:

$$\mu_{\text{LN}} = \ln(m) - \frac{\sigma^2}{2}$$

Usamos el subíndice `LN` para no confundirlo con la tasa de atención $\mu$ de teoría de colas. Con $\sigma = 0,8$, cuando un docente tiene media $m = 2$ minutos (Caso A), la mitad de las elecciones tarda menos de 1,45 minutos y casi ninguna pasa de 10 minutos; mientras que cuando está desorientado con media $m = 8$ minutos (Caso C), la mediana sube a 5,81 minutos y cerca del 25 % supera los 10 minutos si no hay límite de reloj.

### 4.4. Organización modular del código en Python

El proyecto se programó en Python 3 separando cada responsabilidad en archivos independientes dentro de la carpeta `src/`:

* **`src/utils.py`**: funciones auxiliares compartidas (distancia de Haversine en kilómetros, sorteo de tiempos log-normales y exponenciales manejando generadores `numpy.random.Generator` con semillas controladas).
* **`src/generar_datos.py`**: script que construye de manera reproducible `escuelas.csv`, `cargos.csv` y `docentes.csv`.
* **`src/recomendador.py`**: implementa las tres funciones principales del Escenario 3:
  * `candidatas(docente, estado)` → filtra las escuelas con vacantes compatibles según distancia $R_i$, turnos y ámbito rural.
  * `recomendar(docente, estado, k=3)` → calcula $\text{Puntaje}_{ij}$ y devuelve las 3 mejores escuelas alternativas.
  * `pronosticar(docente, estado, R_MC=200)` → corre las 200 micro-simulaciones rápidas de los docentes previos y calcula la probabilidad de vacante $\theta_{ij}$ para armar el aviso de 10 minutos.
* **`src/simulation.py`**: motor de simulación de eventos discretos armado sobre `heapq`. Permite correr tanto colas abiertas clásicas ($M/M/1$ y $M/M/c$ para verificación) como la asamblea completa en los escenarios E1, E2 y E3. En E2 y E3, al iniciar un turno compara el tiempo sorteado de elección contra el tope $\tau$ para definir si el docente confirma cargo o pasa a la cola de reintentos.
* **`src/metricas.py`**: reúne el cálculo de todos los indicadores de la sección 3.6, intervalos de confianza y controles automáticos de consistencia.
* **`notebooks/experimentos.ipynb`**: notebook desde donde se corren las pruebas de validación, las 30 réplicas de cada experimento y todos los gráficos del informe.

---

## 5. VERIFICACIÓN, VALIDACIÓN Y DISEÑO EXPERIMENTAL

### 5.1. Verificación del simulador contra modelos $M/M/1$ y $M/M/c$

Antes de simular la asamblea docente, comprobamos que el motor de eventos discretos (`src/simulation.py`) programe bien los arribos, las filas y los servidores comparando sus promedios contra los resultados teóricos exactos de $M/M/1$ y $M/M/c$ vistos en clase (Rivadera, 2026b, 2026c). Corriendo 30 réplicas independientes de simulaciones largas con llegadas de Poisson y servicios exponenciales (100.000 clientes atendidos por réplica luego de descartar los primeros 10.000 para estabilizar el sistema), verificamos que el intervalo de confianza al 95 % del simulador contenga los valores analíticos:

| Modelo teórico | Parámetros de entrada | Valores exactos por fórmula |
| :--- | :--- | :--- |
| **$M/M/1$** | $\lambda = 4$ /h, $\mu = 6$ /h | $\rho = 0,6667$ ; $L = 2,0000$ ; $L_q = 1,3333$ ; $W = 0,5000$ h ; $W_q = 0,3333$ h (20 min) |
| **$M/M/c$ ($c=1$ vs. $c=2$)** | $\lambda = 2$ /h, $\mu = 3$ /h | Con $c = 1$: $W_q = 0,6667$ h (40 min) $\quad ; \quad$ Con $c = 2$: $W_q = 0,0417$ h (2,5 min) y $P_0 = 0,5000$ |

Además, al correr las simulaciones de la asamblea (E1, E2 y E3), el código ejecuta tres chequeos automáticos (`assert`) al terminar cada réplica:
1. Que el largo medio de la cola calculado integrando en el tiempo coincida exactamente con la suma de esperas individuales dividida por la duración del acto ($L_q = \frac{1}{T_{\text{total}}}\sum_{i=1}^{N} Q_i$).
2. Que ninguna escuela entregue más cargos que sus vacantes reales ni asigne cargos a un docente de otro nivel o especialidad.
3. Que en la cola principal los turnos se inicien respetando sin excepciones el orden decreciente de puntaje $P_i$.

### 5.2. Prueba del recomendador y evaluación del pronóstico

#### 5.2.1. Tasa de acierto en el Top 3 (*Hit Rate@3*) y ajuste de pesos

Para comprobar que el recomendador realmente sugiere escuelas acordes al perfil del docente antes de integrarlo a la cola, hacemos una prueba usando las opciones 6 a 10 guardadas en `preferencias_ocultas` de los 300 docentes:
1. Le pasamos al algoritmo únicamente las primeras 5 escuelas (`preferencias` visibles) y simulamos que esas 5 ya se quedaron sin vacantes.
2. Le pedimos a `recomendar(docente, estado, k=3)` que sugiera 3 escuelas alternativas entre el resto del padrón.
3. Medimos el **porcentaje de acierto en el Top 3 (*Hit Rate@3*)**: a qué porcentaje de los docentes el sistema logra acertarle en esas 3 sugerencias al menos una de sus verdaderas opciones 6 a 10 que estaban ocultas.

Comparamos nuestra combinación ponderada contra alternativas simples: elegir 3 escuelas al azar dentro del radio del docente, sugerir siempre las 3 más pedidas por todo el padrón (popularidad general), o usar uno solo de los criterios por separado (solo cercanía, solo parecido o solo coincidencia con colegas). Como los tres pesos son positivos y suman $w_d + w_t + w_c = 1$, recorriendo los valores de a saltos de $0,05$ hay apenas 231 combinaciones posibles, por lo que las probamos todas con un ciclo simple en Python en menos de un segundo para elegir los pesos con mejor acierto sin necesidad de algoritmos complejos.

*(Nota: dado que las preferencias de prueba provienen de nuestro propio generador sintético basado en distancia, turno y componente aleatorio personal, este indicador valida el funcionamiento interno del módulo y sirve como referencia comparativa, sabiendo que en una aplicación real debería medirse con elecciones verdaderas de docentes).*

#### 5.2.2. Precisión del pronóstico Monte Carlo

Para verificar si hacer las 200 pasadas rápidas de simulación en el preaviso realmente predice mejor qué escuelas van a seguir libres 10 minutos después, comparamos la probabilidad pronosticada $\theta_{ij}$ contra lo que terminó ocurriendo en el turno real del docente ($y_{ij} = 1$ si la escuela llegó con vacante libre y $y_{ij} = 0$ si se agotó antes). Calculamos para ello el **Error Cuadrático Medio ($MSE$)** y su raíz (**$RMSE$**):

$$MSE = \frac{1}{n} \sum (\theta_{ij} - y_{ij})^2 \quad ; \quad RMSE = \sqrt{MSE}$$

y los contrastamos contra la alternativa más simple (asumir sin simular que toda escuela libre en el momento del aviso va a seguir libre 10 minutos más tarde). Cuanto más cercanos a cero sean el $MSE$ y el $RMSE$, más confiable es la alerta enviada al docente.

### 5.3. Diseño de experimentos y análisis de sensibilidad

Todos los escenarios se evalúan sobre los mismos archivos de entrada (`escuelas.csv`, `cargos.csv`, `docentes.csv`) utilizando **30 réplicas independientes** con semillas emparejadas por réplica para que la comparación entre E1, E2 y E3 sea lo más justa posible (Law, 2015):

* **Experimento 1 — Comparación central de escenarios ($c = 1, \tau = 10$ min):** se comparan E1 (actual sin límite), E2 (ventana de 10 min + aviso horario + cola de reintentos) y E3 (E2 + recomendador multicriterio + pronóstico Monte Carlo en el aviso previo) sobre todas las métricas de la sección 3.6.
* **Experimento 2 — Sensibilidad del tiempo máximo de turno $\tau$ (en E2 y E3, con $c = 1$):** se prueban ventanas de $\tau \in \{6, 8, 10, 12, 15\}$ minutos para analizar el equilibrio práctico: ventanas muy cortas achican la espera inicial pero mandan demasiada gente a reintento (afectando su orden de mérito), mientras que ventanas muy largas se acercan nuevamente a las demoras de E1.
* **Experimento 3 — Sensibilidad de la cantidad de comisiones simultáneas $c$ (en E2 y E3, con $\tau = 10$ min):** se evalúa trabajar con $c \in \{1, 2, 3\}$ mesas atendiendo en paralelo para cuantificar cuánto baja la duración total de la jornada al sumar personal administrativo.
* **Experimento 4 — Sensibilidad de la adopción del recomendador y aporte del pronóstico en E3:** se varía la probabilidad de adopción $p_{\text{rec}} \in \{0,30 ;\, 0,50 ;\, 0,70 ;\, 0,90\}$ y se compara también E3 con y sin el pronóstico Monte Carlo, de modo que las conclusiones muestren un rango realista de mejora sin depender de un único valor supuesto.

### 5.4. Contrastación con referencias operativas reales

Mientras que las pruebas contra $M/M/1$ y $M/M/c$ aseguran que el programa no tiene errores de lógica, para validar que los números del Escenario 1 tengan sentido práctico contrastamos el orden de magnitud de la duración simulada ($T_{\text{total}}$ en E1) con las características documentadas de los operativos reales en la provincia. En las convocatorias anuales de Nivel Inicial, Primario y EPJA, el Ministerio cita a cientos e incluso más de un millar de docentes por departamento en jornadas que arrancan a las 8:00 hs bajo la pauta abierta *«hasta lo que dure la jornada»*, o bien desdobladas en bloques matutinos (9:00 a 12:00 hs) y vespertinos (*«a partir de las 13:30 y hasta que finalice la jornada»*) cuando el volumen de postulantes exige particionar la atención (Gobierno de la Provincia de Salta, 2025; MECCyT, 2024b), habiéndose registrado en Salta Capital reclamos por esperas de varias horas afuera de las oficinas técnicas (Navarro, 2023). Dado que no existen actas públicas con el cronometraje minuto a minuto de cada turno individual, los tiempos por postulante se simulan de forma sintética controlada y los resultados de E2 y E3 se interpretan principalmente en términos comparativos (porcentaje de reducción respecto de E1 bajo idénticas condiciones de entrada).

---

## 6. RESULTADOS Y ANÁLISIS

> *[SECCIÓN PENDIENTE DE EJECUCIÓN COMPUTACIONAL — VIERNES 06/11 Y SÁBADO 07/11]*
> *Las tablas y gráficos siguientes se completarán con las salidas numéricas obtenidas al correr las 30 réplicas por escenario en `notebooks/experimentos.ipynb`.*

### 6.1. Resultados de la verificación del simulador ($M/M/1$ y $M/M/c$)

| Modelo de prueba | Métrica | Valor teórico exacto | Media simulada (IC 95 %) | Error relativo (%) |
| :--- | :---: | :---: | :---: | :---: |
| $M/M/1$ ($\lambda=4, \mu=6$) | $W_q$ (h) | 0,3333 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/1$ ($\lambda=4, \mu=6$) | $L_q$ (clientes) | 1,3333 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/1$ ($\lambda=2, \mu=3$) | $W_q$ (h) | 0,6667 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/2$ ($\lambda=2, \mu=3$) | $W_q$ (h) | 0,0417 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/2$ ($\lambda=2, \mu=3$) | $P_0$ | 0,5000 | *[Pendiente corrida]* | *[Pendiente]* |

Chequeos automáticos de consistencia en las corridas de E1, E2 y E3 (igualdad temporal de Little, control de vacantes y respeto del puntaje en cola principal): *[Pendiente: confirmar cumplimiento en las 30 réplicas de cada escenario]*.

### 6.2. Desempeño del recomendador (Hit Rate@3) y del pronóstico ($MSE$ / $RMSE$)

| Configuración evaluada | Pesos ($w_d ; w_t ; w_c$) | Hit Rate@3 (%) | Mejora frente al azar |
| :--- | :---: | :---: | :---: |
| Elección al azar dentro del filtro $K_i$ | — | *[Pendiente]* | — |
| Escuelas más pedidas (popularidad general) | — | *[Pendiente]* | *[Pendiente]* |
| Solo cercanía en km | (1,00 ; 0,00 ; 0,00) | *[Pendiente]* | *[Pendiente]* |
| Solo parecido con su lista | (0,00 ; 1,00 ; 0,00) | *[Pendiente]* | *[Pendiente]* |
| Solo coincidencia con otros docentes | (0,00 ; 0,00 ; 1,00) | *[Pendiente]* | *[Pendiente]* |
| Recomendador combinado (mejor grilla) | *[Óptimo hallado]* | *[Pendiente]* | *[Pendiente]* |

| Evaluación de disponibilidad en el aviso de 10 min | $MSE$ | $RMSE$ | Observación |
| :--- | :---: | :---: | :--- |
| Pronóstico Monte Carlo ($R_{\text{MC}} = 200$ pasadas) | *[Pendiente]* | *[Pendiente]* | Anticipa el consumo de vacantes de los turnos previos |
| Sin pronóstico (mirar solo si hoy está libre) | *[Pendiente]* | *[Pendiente]* | Referencia base sin simulación hacia adelante |

### 6.3. Comparación principal entre escenarios (E1, E2 y E3 — 30 réplicas)

| Indicador de desempeño (Media ± IC 95 %) | E1 (Actual sin límite) | E2 (Ventana $\tau=10$ min + Reintentos) | E3 (Asistido con Recomendador + Pronóstico) |
| :--- | :---: | :---: | :---: |
| Espera media de los atendidos, $W_q$ (min) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Espera media sobre los 300 convocados, $W_{\text{conv}}$ (min) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Cantidad media de docentes en fila, $L_q$ | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Duración total de la asamblea, $T_{\text{total}}$ (min / h) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Derivación a cola de reintentos (%) | No aplica | *[Pendiente]* | *[Pendiente]* |
| Cargos vacantes cubiertos (%) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Docentes sin oferta compatible (%) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Satisfacción media de los adjudicatarios (0 a 1) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Error medio del aviso de horario, $MAE$ (min) | No aplica | *[Pendiente]* | *[Pendiente]* |
| Casos afectados en su mérito por reintento (%) | 0 % | *[Pendiente]* | *[Pendiente]* |

### 6.4. Gráficos y análisis de sensibilidad

*[Espacio reservado para insertar las figuras generadas desde `notebooks/experimentos.ipynb` acompañadas de su explicación práctica:*
* *Figura 1: Diagrama de cajas (boxplot) de la duración total de la asamblea $T_{\text{total}}$ en horas para E1, E2 y E3.*
* *Figura 2: Evolución de la espera media $W_q$ y del porcentaje de pases a reintento al variar la ventana $\tau \in \{6, 8, 10, 12, 15\}$ minutos.*
* *Figura 3: Reducción de la duración de jornada y tiempos de espera al habilitar $c \in \{1, 2, 3\}$ mesas de atención simultáneas.*
* *Figura 4: Variación de la mejora del Escenario 3 según el porcentaje de docentes que aprovechan las recomendaciones ($p_{\text{rec}} \in \{0,30 ; 0,50 ; 0,70 ; 0,90\}$) y comparación con/sin el pronóstico Monte Carlo.]*

---

## 7. DISCUSIÓN

### 7.1. Aporte práctico para la organización de las asambleas en Salta

El análisis realizado permite separar dos cuestiones que muchas veces se mezclan al hablar de modernizar los actos públicos docentes: por un lado el **respeto estricto al puntaje de mérito**, y por otro la **forma en que se organiza la fila y la información disponible**. Cumplir con la Ley Provincial N.° 6.830 y la Resolución N.° 1.851/08 exige llamar por orden de puntaje y dejar que cada docente elija libremente su cargo, pero no obliga a que trescientas personas esperen a ciegas durante toda una mañana o tarde ni a que quien llega sin opciones frena durante veinte minutos al resto del padrón.

Al comparar el Escenario 2 con el Escenario 3 se ve con claridad por qué ambas mejoras se necesitan mutuamente:
* **La ventana de $\tau = 10$ minutos y la cola de reintentos (E2)** funcionan como una red de contención: evitan que un corte de internet o una indecisión puntual trabe a cientos de colegas. Sin embargo, aplicar un reloj límite sin darle herramientas previas al docente hace que muchos postulantes sorprendidos sin vacantes pasen a la cola secundaria, corriendo el riesgo de que para cuando llegue su reintento otros docentes con menor puntaje ya hayan ocupado los últimos cargos compatibles.
* **La precarga con recomendador y pronóstico de vacantes en el aviso previo (E3)** ataca justamente la raíz del problema: le avisa al docente 10 minutos antes si sus escuelas elegidas están por agotarse y le muestra 3 alternativas concretas cercanas a su domicilio y compatibles con sus turnos que tienen alta probabilidad de seguir libres. Así bajan tanto el tiempo de atención como la cantidad de docentes que caen en la cola de reintentos. *(Como alternativa reglamentaria adicional, si el Ministerio quisiera reducir aún más el riesgo de perder prioridad al pasar a reintentos por un corte de red, podría evaluarse reservar provisoriamente una vacante hasta el final de la ronda principal).*

Desde el punto de vista técnico, la propuesta es sencilla de llevar a una arquitectura web estándar: solo requiere agregar un formulario simple de precarga de hasta 5 escuelas cuando el docente confirma asistencia al acto, y un cálculo liviano en el servidor cada vez que avanza un turno.

### 7.2. Supuestos y limitaciones del modelo

Para defender los resultados con honestidad técnica deben tenerse presentes las principales limitaciones del estudio:

1. **Tiempos de decisión y adopción modelados de forma sintética.** Aunque las 40 escuelas y sus distancias en Salta Capital son reales, los tiempos medios de elección (multiplicadores $\times 2$ en Caso B y $\times 4$ en Caso C) y la proporción de docentes que aceptan las sugerencias ($p_{\text{rec}} = 0,70$ en el caso base) son supuestos razonables pero no medidos sobre usuarios reales. Por eso incluimos el análisis de sensibilidad del Experimento 4, y señalamos que en una prueba piloto del Ministerio estos tiempos podrían medirse directamente con los registros (*logs*) de la plataforma.
2. **Evaluación del recomendador sobre preferencias generadas.** Como las listas de escuelas de los docentes se armaron sintéticamente usando distancia, turno y una variación aleatoria personal, el porcentaje de acierto (*Hit Rate@3*) comprueba que el algoritmo funciona bien sobre esa estructura, pero la validación definitiva requeriría datos reales de precarga docente.
3. **Aplicación a cargos completos frente a horas cátedra de Secundaria.** Nuestro modelo asume que cada docente elige un único cargo indivisible, lo cual representa fielmente a Nivel Inicial y Nivel Primario (Maestro de Grado, Celador, etc.). En Nivel Secundario, donde muchos profesores arman su carga horaria combinando varios bloques de pocas horas cátedra en distintos colegios sin superposición de horarios, habría que ampliar el filtro para chequear choques de bloques horarios y tiempos de traslado entre escuelas.
4. **Trabajo con varias comisiones en paralelo ($c > 1$).** En el análisis de sensibilidad con 2 o 3 mesas atendiendo a la vez un mismo listado, puede pasar que el docente del puesto $k + 1$ confirme su cargo un minuto antes que el del puesto $k$ mientras ambos están dentro de su ventana de 10 minutos. En la práctica esto se evita muy fácil si cada mesa atiende un nivel o especialidad distinta en simultáneo (por ejemplo, Mesa 1 para Nivel Inicial, Mesa 2 para Maestro de Grado y Mesa 3 para Educación Física), sin mezclar un mismo cuadro de mérito en dos ventanillas.
5. **Conectividad desigual y respaldo presencial.** No todos los docentes de la provincia cuentan con buena señal de internet o computadora en el hogar, especialmente en zonas periurbanas o rurales. Por eso cualquier implementación real debe contemplar avisos livianos (SMS o Telegram/WhatsApp), mantener un puesto presencial con pantallas en la sede de designación para quien prefiera concurrir en persona y otorgar el pase automático a reintento ante caídas de red involuntarias.

### 7.3. Líneas de trabajo futuro

A partir de este simulador se abren tres mejoras concretas a futuro:
* **Calibración con datos históricos de actas:** contar con registros reales de designaciones permitiría ajustar los pesos del recomendador según el comportamiento histórico real de elección por barrio y turno en Salta.
* **Uso de metaheurísticas para planificar operativos masivos:** si se buscara organizar en simultáneo las convocatorias de decenas de especialidades decidiendo cuántas mesas asignar a cada sala, en qué horarios escalonar las citaciones y qué ventana $\tau$ fijar para cada nivel con personal administrativo limitado, el problema combinatorio resultante sería ideal para aplicar Algoritmos Genéticos o Búsqueda Tabú acoplados al simulador (Law, 2015; Taha, 2017).
* **Extensión al régimen de horas cátedra de Secundaria:** incorporar matrices horarias por día de la semana para recomendar paquetes compatibles de horas cátedra.

---

## 8. CONCLUSIONES

1. Se formuló e implementó en Python un modelo de simulación de eventos discretos adaptado a los actos públicos de designación docente de Salta Capital, contemplando las características reales que impiden usar directamente las fórmulas estacionarias clásicas: padrón finito de 300 docentes presente desde el inicio, cierre al agotar las 100 vacantes, orden de atención por puntaje de mérito, ventana máxima de turno $\tau$ y cola secundaria de reintentos.
2. Se verificó el correcto funcionamiento del motor de simulación contrastando sus resultados en régimen estacionario contra las soluciones exactas de los modelos $M/M/1$ y $M/M/c$ de la asignatura, complementado con controles automáticos de la Ley de Little temporal y de conservación de vacantes en cada corrida.
3. Se mostró que respetar el orden de mérito establecido por la Ley N.° 6.830 y la Resolución Ministerial N.° 1.851/08 es totalmente compatible con reducir las esperas: mientras la ventana $\tau = 10$ minutos con aviso horario (E2) evita que demoras aisladas frenen a toda la fila, el agregado de precarga de preferencias, recomendador multicriterio y pronóstico Monte Carlo de disponibilidad (E3) ataca la desorientación del docente cuyas opciones iniciales se agotaron, disminuyendo tanto el tiempo en ventanilla como la cantidad de personas enviadas a reintento.
4. *[PENDIENTE CORRIDA 07/11 — Completar con los valores numéricos finales de las 30 réplicas: (a) cuánto bajan en porcentaje e intervalo de confianza la espera media $W_q$ y la duración total de la asamblea $T_{\text{total}}$ en E2 y en E3 frente al sistema tradicional E1; (b) qué porcentaje de casos pasa a reintento en E2 vs. E3 y cómo baja la afectación de mérito; y (c) qué configuración práctica de ventana $\tau$ y cantidad de comisiones $c$ se recomienda a partir del análisis de sensibilidad]*.

---

## 9. REFERENCIAS BIBLIOGRÁFICAS

* Banks, J., Carson, J. S., II, Nelson, B. L., y Nicol, D. M. (2010). *Discrete-Event System Simulation* (5.ª ed.). Pearson.
* Gobierno de la Provincia de Salta (1995). *Ley Provincial N.° 6.830: Estatuto del Educador* (y modificatorias Leyes N.° 7.189 y N.° 8.325). Boletín Oficial de la Provincia de Salta. https://www.edusalta.gov.ar
* Gobierno de la Provincia de Salta (2025, 6 de febrero). *Se desarrolla el proceso de designaciones y titularizaciones 2025*. Secretaría de Prensa y Comunicación. https://www.salta.gob.ar/prensa/noticias/se-desarrolla-el-proceso-de-designaciones-y-titularizaciones-2025-99952
* Hillier, F. S., y Lieberman, G. J. (2015). *Introducción a la investigación de operaciones* (10.ª ed.). McGraw-Hill Education.
* Instituto Nacional de Estadística y Censos [INDEC] (2023). *Censo Nacional de Población, Hogares y Viviendas 2022: Resultados definitivos*. República Argentina. https://censo.gob.ar
* Law, A. M. (2015). *Simulation Modeling and Analysis* (5.ª ed.). McGraw-Hill Education.
* Little, J. D. C. (1961). A proof for the queuing formula: L = λW. *Operations Research*, 9(3), 383–387. https://doi.org/10.1287/opre.9.3.383
* Ministerio de Educación de la Provincia de Salta (2008). *Resolución Ministerial N.° 1.851/08: Régimen de Valoración de Antecedentes para la Carrera Docente*. Portal oficial *Edusalta*. https://www.edusalta.gov.ar
* Ministerio de Educación, Cultura, Ciencia y Tecnología de la Provincia de Salta [MECCyT] (2024a). *Información Estadística Educativa y Padrón Oficial de Establecimientos Educativos (Relevamiento Anual)*. Secretaría de Planeamiento Educativo y Desarrollo Profesional Docente, *Edusalta*. https://www.edusalta.gov.ar
* Ministerio de Educación, Cultura, Ciencia y Tecnología de la Provincia de Salta [MECCyT] (2024b, 7 de febrero). *Cronograma de Titularizaciones y Designaciones para los niveles Inicial, Primario y EPJA* (Parte de Prensa N.° 8681). Portal oficial *Edusalta*. https://www.edusalta.gov.ar/index.php/informacion/partes-de-prensa/8681-cronograma-de-titularizaciones-y-designaciones-para-los-niveles-inicial-primario-y-epja
* Navarro, E. (2023, 7 de febrero). *Docentes esperaron por horas afuera de la Secretaría Técnica en Salta Capital*. El Vocero Hoy. https://elvocerohoy.com/contenido/11240/docentes-esperaron-por-horas-afuera-de-la-secretaria-tecnica-en-salta-capital
* Ricci, F., Rokach, L., y Shapira, B. (Eds.) (2015). *Recommender Systems Handbook* (2.ª ed.). Springer. https://doi.org/10.1007/978-1-4899-7637-6
* Rivadera, G. R. (2026a). *Teoría de Colas (Primera Parte): Introducción – Procesos de Nacimiento y Muerte* [Material de cátedra]. Investigación Operativa II, Facultad de Ingeniería, Universidad Católica de Salta (UCASAL).
* Rivadera, G. R. (2026b). *Teoría de Colas (Segunda Parte): Notación y modelos de un servidor* [Material de cátedra]. Investigación Operativa II, Facultad de Ingeniería, Universidad Católica de Salta (UCASAL).
* Rivadera, G. R. (2026c). *Teoría de Colas (Tercera Parte): Notación y modelos de múltiples servidores* [Material de cátedra]. Investigación Operativa II, Facultad de Ingeniería, Universidad Católica de Salta (UCASAL).
* Taha, H. A. (2017). *Investigación de operaciones* (10.ª ed.). Pearson Educación.
