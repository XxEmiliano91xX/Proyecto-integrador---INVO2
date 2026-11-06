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
   * 2.2. Modelos analíticos clásicos como banco de pruebas de validación
   * 2.3. Limitaciones de los modelos analíticos frente al problema de asignación docente
   * 2.4. Colas con prioridad no apropiativa, servicio truncado y reintentos
   * 2.5. Fundamentos de simulación de eventos discretos
   * 2.6. Asignación por orden de mérito y sistemas de recomendación
4. [3. Metodología y formulación del modelo](#3-metodología-y-formulación-del-modelo)
   * 3.1. Correspondencia con los elementos de una cola
   * 3.2. Escenario base (E1): cola secuencial sin límite de tiempo
   * 3.3. Escenario E2: ventana τ, servicio truncado y cola de reintentos
   * 3.4. Estimador dinámico de horario y aviso previo
   * 3.5. Escenario E3: recomendación de escuelas y aviso anticipado de disponibilidad
   * 3.6. Métricas de desempeño
   * 3.7. Resumen de notación y convenciones
5. [4. Datos e implementación computacional](#4-datos-e-implementación-computacional)
   * 4.1. Origen de los datos: fuentes oficiales y generación sintética
   * 4.2. Formato de los archivos de datos
   * 4.3. Parametrización de la distribución log-normal
   * 4.4. Arquitectura modular e interfaz con el simulador
6. [5. Verificación, validación y diseño experimental](#5-verificación-validación-y-diseño-experimental)
   * 5.1. Validación analítica del motor de simulación
   * 5.2. Validación y calibración del recomendador de escuelas
   * 5.3. Diseño experimental y análisis de sensibilidad
7. [6. Resultados y análisis](#6-resultados-y-análisis)
8. [7. Discusión](#7-discusión)
9. [8. Conclusiones](#8-conclusiones)
10. [9. Referencias bibliográficas](#9-referencias-bibliográficas)

---

## RESUMEN

En la Provincia de Salta, la cobertura de cargos docentes interinos y suplentes a cargo de la Junta Calificadora de Méritos y Disciplina se realiza mediante actos públicos estrictamente secuenciales regidos por el puntaje del Cuadro de Orden de Mérito. En este esquema, cada aspirante bloquea la atención de quienes le siguen mientras consulta las vacantes remanentes y toma su decisión, lo que genera extensas jornadas de espera, incertidumbre sobre el horario de atención y demoras acumulativas ante indecisiones o fallas de conexión. En este trabajo se formula y evalúa mediante simulación de eventos discretos en Python un sistema alternativo de turnos dinámicos estructurado en tres escenarios comparables sobre una instancia representativa del Departamento Capital (300 docentes, 100 cargos y 40 establecimientos). El Escenario 1 reproduce el procedimiento secuencial actual; el Escenario 2 incorpora una ventana máxima de decisión (τ = 10 minutos), un estimador dinámico de horario con alerta previa y una cola secundaria de reintentos no apropiativa; y el Escenario 3 añade la precarga de preferencias junto con un módulo de recomendación híbrida (filtrado por restricciones geográficas y de turno, similitud de atributos y filtrado colaborativo) acoplado a un pronóstico de disponibilidad mediante simulación Monte Carlo hacia adelante. *[PENDIENTE CORRIDA 07/11: agregar una oración final con las reducciones porcentuales de Wq y duración total de jornada obtenidas en las 30 réplicas entre E1, E2 y E3]*.

**Palabras clave:** teoría de colas, prioridad no apropiativa, simulación de eventos discretos, cola de reintentos, sistemas de recomendación, designaciones docentes.

---

## 1. INTRODUCCIÓN

### 1.1. Contexto: el sistema educativo y las designaciones docentes en Salta

El sistema educativo de la Provincia de Salta comprende más de 2.300 unidades educativas de gestión estatal y privada y supera los 450.000 alumnos matriculados en todos sus niveles y modalidades, de los cuales más de 350.000 corresponden a los niveles obligatorios Inicial, Primario y Secundario (Ministerio de Educación, Cultura, Ciencia y Tecnología de Salta [MECCyT], 2024). Desde el punto de vista demográfico y territorial, el Censo Nacional de Población, Hogares y Viviendas 2022 registró en la provincia 1.441.351 habitantes, concentrando en el Departamento Capital 627.704 habitantes —el 43,5 % de la población provincial— dentro de una superficie de 1.722 km² (Instituto Nacional de Estadística y Censos [INDEC], 2023). Esta concentración poblacional convierte a las convocatorias de cobertura de cargos del área metropolitana de Salta en operativos masivos, particularmente al inicio del ciclo lectivo entre febrero y marzo.

En el plano institucional, el ingreso a la docencia y la cobertura de cargos interinos y suplentes se rigen por la Ley Provincial N.° 6.830 (*Estatuto del Educador*, promulgada originalmente por Decreto N.° 60/95 y modificada por las Leyes N.° 7.189 y N.° 8.325). Sus artículos 10 y 12 encomiendan a la Junta Calificadora de Méritos y Disciplina —organizada en salas para los niveles Inicial y Primario y para el Nivel Secundario y sus modalidades, con sede central en calle Caseros 975 de la ciudad de Salta— el estudio de los legajos del personal docente y la elaboración pública de las nóminas de aspirantes por estricto orden de mérito (Gobierno de la Provincia de Salta, 1995). La calificación numérica de cada docente se determina anualmente conforme a la Resolución Ministerial N.° 1.851/08 (*Régimen de Valoración de Antecedentes para la Carrera Docente*), que pondera título, antigüedad, capacitaciones, desempeño y residencia para emitir los cuadros provisorios, sustanciar el período de tachas (reclamos) y publicar las denominadas *tirillas* definitivas de puntaje en el portal oficial *Edusalta* (Ministerio de Educación de la Provincia de Salta, 2008).

Una vez cerrados los cuadros definitivos, la adjudicación efectiva de vacantes en escuelas públicas se ejecuta mediante actos públicos de designación coordinados por la Secretaría de Gestión Educativa y las Direcciones Generales de Nivel, ya sea en sedes presenciales (como escuelas cabecera o dependencias ministeriales) o a través de instancias virtuales implementadas desde la emergencia sanitaria. En ambos formatos, el procedimiento respeta una regla invariable: se convoca a los aspirantes en orden decreciente de puntaje y cada docente elige un cargo compatible entre las vacantes que continúan libres en ese instante.

### 1.2. Planteamiento del problema

Si bien el llamado secuencial por orden de mérito garantiza transparencia e imparcialidad legal, su instrumentación operativa presenta cuatro cuellos de botella propios de un sistema de espera de canal único sin acotamiento de servicio:

1. **Bloqueo de cabecera de línea (*head-of-line blocking*).** El proceso es estrictamente secuencial: el docente ubicado en la posición *k + 1* del listado no puede iniciar su elección hasta que el docente en la posición *k* concluya la suya. Un único participante indeciso frena a la totalidad de la fila restante.
2. **Alta asimetría en los tiempos de decisión.** Quienes encabezan el listado suelen encontrar disponible su escuela deseada y resuelven su elección en menos de dos minutos. En cambio, a medida que avanza la asamblea y las vacantes céntricas o de turno preferido se agotan, muchos docentes llegan a la ventanilla descubriendo en ese mismo momento que ninguna de las escuelas que tenían previstas sigue libre. Deben entonces examinar sobre la marcha la planilla completa de vacantes remanentes —evaluando barrios, distancias de traslado y turnos—, lo que multiplica su tiempo de deliberación.
3. **Incertidumbre horaria y espera improductiva.** Al no existir una estimación dinámica de horarios, cientos de docentes deben permanecer presentes o conectados frente a la pantalla durante varias horas sin saber si serán llamados en diez minutos o tres horas más tarde.
4. **Fricción por ausencias o fallas técnicas.** En modalidades remotas o híbridas, las caídas de conectividad o la falta de respuesta al llamado obligan a repetir verificaciones de protocolo antes de dar por ausente al postulante, sumando tiempo muerto al proceso o generando reclamos posteriores si la desconexión fue involuntaria.

El problema que aborda este trabajo consiste en diseñar, formular matemáticamente y evaluar mediante simulación computacional un esquema de gestión de turnos que reduzca el tiempo medio de espera en cola y la duración total de la jornada de designación, sin alterar la prioridad legal otorgada por el puntaje de mérito.

### 1.3. Objetivos

#### 1.3.1. Objetivo general

Formular, implementar y evaluar mediante simulación de eventos discretos un sistema de turnos dinámicos con ventana máxima de atención, cola de reintentos y recomendación anticipada de vacantes para optimizar los tiempos de espera y de jornada en las asambleas de designación docente de la Provincia de Salta, preservando el orden de mérito vigente.

#### 1.3.2. Objetivos específicos

1. Modelar el acto público de designación docente bajo el enfoque de la teoría de colas, identificando las propiedades estructurales (fuente finita, horizonte transitorio de una jornada, prioridad no apropiativa, truncamiento de servicio y realimentación) que justifican el empleo de simulación de eventos discretos.
2. Verificar y validar el motor computacional de eventos discretos en Python contrastando sus salidas en régimen estacionario contra las soluciones analíticas exactas de los modelos M/M/1 y M/M/c de la cátedra.
3. Diseñar un mecanismo de precarga de preferencias, filtrado por restricciones de reserva, recomendación híbrida de escuelas alternativas y pronóstico de disponibilidad por simulación Monte Carlo que reduzca la deliberación del docente cuyas opciones iniciales ya fueron adjudicadas.
4. Comparar estadísticamente tres escenarios operativos —procedimiento tradicional (E1), sistema con ventana de tiempo y cola de reintentos (E2), y sistema integrado con recomendación y aviso anticipado (E3)— junto con un análisis de sensibilidad sobre el tamaño de ventana τ y la cantidad de comisiones simultáneas *c*.
5. Formular recomendaciones operativas concretas para la Junta Calificadora de Méritos y Disciplina a partir de las métricas obtenidas.

### 1.4. Alcance y limitaciones

El estudio abarca la formulación conceptual y matemática del sistema de espera y recomendación, el diseño de una instancia de datos anclada en establecimientos reales del Departamento Capital y microdatos sintéticos reproducibles de aspirantes, la implementación computacional del simulador y del recomendador en Python, su validación analítica y el análisis estadístico de escenarios.

Quedan fuera del alcance de este trabajo:
* El desarrollo de una aplicación web o móvil de producción (interfaz gráfica de usuario, autenticación, pasarelas de notificación o base de datos transaccional).
* La etapa administrativa previa de valoración de antecedentes, carga de documentación probatoria y resolución de tachas, asumiéndose como dato de entrada el Cuadro de Orden de Mérito definitivo ya publicado por la Junta Calificadora.
* El régimen específico de designación por horas cátedra fraccionadas del Nivel Secundario, concentrándose el modelado en cargos completos (maestro de grado, maestro de nivel inicial y cargos equivalentes) donde cada vacante representa una unidad indivisible.

### 1.5. Organización del informe

El resto del documento se estructura del siguiente modo. La sección 2 desarrolla el marco teórico estrictamente necesario para fundamentar el modelo: elementos de colas, ley de Little, modelos analíticos de referencia para validación, prioridad no apropiativa, simulación de eventos discretos y fundamentos de recomendación y asignación. La sección 3 formula la metodología matemática de los tres escenarios, el estimador horario y las métricas de desempeño. La sección 4 detalla los datos geográficos de Salta Capital, la generación sintética y la arquitectura modular en Python. La sección 5 expone la verificación analítica y el diseño experimental. Las secciones 6, 7 y 8 presentan los resultados, la discusión de supuestos y las conclusiones del trabajo.

---

## 2. MARCO TEÓRICO

### 2.1. Elementos de un sistema de colas y Ley de Little

Un sistema de colas se define formalmente mediante una fuente de clientes que solicitan atención a una o más instalaciones de servicio (servidores). Si los servidores se encuentran ocupados al momento de un arribo, los clientes forman una línea de espera gobernada por una disciplina de selección (Hillier y Lieberman, 2015, cap. 17; Rivadera, 2026a).

En la notación estándar de Kendall (1953), ampliada a *(a/b/c):(d/e/f)*, se identifican: la distribución del tiempo entre arribos (*a*), la distribución del tiempo de servicio (*b*), el número de servidores paralelos (*c*), la disciplina de la cola (*d*), la capacidad del sistema (*e*) y el tamaño de la población fuente (*f*). Cuando el arribo de clientes ocurre a tasa media $\lambda$ y la tasa media de atención por servidor es $\mu$, el factor de utilización de una instalación con $c$ canales idénticos se define como:

$$\rho = \frac{\lambda}{c \mu}$$

Bajo condiciones de conservación de flujo en estado estacionario ($\rho < 1$), las medidas cuantitativas fundamentales de desempeño son la cantidad media de clientes en el sistema ($L$) y en la cola ($L_q$), y el tiempo medio de permanencia en el sistema ($W$) y de espera en la cola ($W_q$). Estas variables se encuentran unívocamente vinculadas mediante la **Ley de Little** (Little, 1961):

$$L = \lambda W \quad ; \quad L_q = \lambda W_q$$

$$W = W_q + \frac{1}{\mu} \quad ; \quad L = L_q + \frac{\lambda}{\mu}$$

En sistemas con horizonte de tiempo finito (como una jornada de asignación cerrada de duración $T_{\text{total}}$), la identidad de Little adopta la forma temporal exacta:

$$L_q = \frac{1}{T_{\text{total}}} \sum_{j} W_{q, j}$$

expresión que se emplea en este trabajo como invariante matemático para verificar la coherencia estadística del simulador computacional en cada réplica.

### 2.2. Modelos analíticos clásicos como banco de pruebas de validación

Los modelos markovianos clásicos suponen arribos regidos por un proceso de Poisson con tiempos entre llegadas exponenciales de parámetro $\lambda$ (densidad $f(t) = \lambda e^{-\lambda t}$) y tiempos de servicio independientes igualmente exponenciales con parámetro $\mu$. 

En este proyecto, las soluciones analíticas de estado estable no se emplean para modelar la asamblea docente (dadas las restricciones analizadas en 2.3), sino como un **banco de pruebas formal de verificación** para certificar que el motor de simulación de eventos discretos programa y procesa las colas sin desvíos sistemáticos (Rivadera, 2026b, 2026c):

1. **Modelo $M/M/1$ (un servidor, capacidad y fuente infinitas):**
   $$L_q = \frac{\lambda^2}{\mu(\mu - \lambda)} = \frac{\rho^2}{1 - \rho} \quad ; \quad W_q = \frac{\lambda}{\mu(\mu - \lambda)} = \frac{\rho}{\mu(1 - \rho)}$$
   Para $\lambda = 4$ y $\mu = 6$ clientes/hora ($\rho = 2/3$), los valores teóricos exactos son $L_q = 1,3333$ clientes y $W_q = 0,3333$ horas (20 minutos).
2. **Modelo $M/M/c$ (múltiples servidores en paralelo):**
   Con $c$ servidores y $\rho = \lambda / (c\mu) < 1$, la probabilidad de sistema vacío $P_0$ y la longitud media en cola vienen dadas por las fórmulas de Erlang-C:
   $$P_0 = \left[ \sum_{n=0}^{c-1} \frac{(\lambda/\mu)^n}{n!} + \frac{(\lambda/\mu)^c}{c!} \cdot \frac{1}{1 - \rho} \right]^{-1}$$
   $$L_q = \frac{P_0 (\lambda/\mu)^c \rho}{c! (1 - \rho)^2} \quad ; \quad W_q = \frac{L_q}{\lambda}$$
   Para $\lambda = 2$ y $\mu = 3$ clientes/hora, la solución exacta arroja para $c = 1$ una espera $W_q = 0,6667$ horas (40 minutos), mientras que duplicar los servidores a $c = 2$ reduce la espera a $W_q = 0,0417$ horas (2,5 minutos), verificando la marcada no linealidad de la congestión frente a la capacidad de atención.

### 2.3. Limitaciones de los modelos analíticos frente al problema de asignación docente

Si bien los modelos $M/M/1$ y $M/M/c$ constituyen pilares de la investigación operativa, sus hipótesis estructurales resultan incompatibles con la realidad de una asamblea de designación docente:

* **Régimen transitorio vs. estado estable:** Las fórmulas analíticas exigen que el sistema opere en régimen permanente ($t \to \infty$). Una asamblea docente es un proceso estrictamente transitorio (*terminating system*): comienza a una hora fija con un padrón cerrado y concluye cuando se atiende al último postulante o se agotan las vacantes.
* **Fuente finita y arribo simultáneo:** No existe una tasa externa constante de llegadas $\lambda$. Los $N = 300$ aspirantes están convocados desde el inicio de la jornada en una lista predeterminada.
* **Distribución del tiempo de servicio y truncamiento:** El tiempo de deliberación humana no es exponencial; presenta alta asimetría positiva modelable mediante distribuciones log-normales con cola derecha pesada. Además, la incorporación de un límite administrativo $\tau$ trunca el servicio en $S = \min(T, \tau)$, rompiendo la propiedad de falta de memoria.
* **Disciplina de prioridad no apropiativa y realimentación:** El orden de llamado responde estrictamente al puntaje de mérito $P_i$, y los aspirantes que no concretan su elección en la ventana $\tau$ reingresan a una cola secundaria de reintentos.

Estas discrepancias matemáticas invalidan el cálculo mediante fórmulas analíticas cerradas y fundamentan la necesidad metodológica de recurrir a la **simulación computacional de eventos discretos** (Law, 2015, cap. 1; Taha, 2017, cap. 19).

### 2.4. Colas con prioridad no apropiativa, servicio truncado y reintentos

Cuando los clientes poseen diferentes niveles de prioridad, la disciplina puede ser apropiativa (*preemptive*, si la llegada de un cliente preferente interrumpe el servicio en curso) o **no apropiativa (*non-preemptive*)**, donde el cliente que ya inició su atención la concluye sin interrupción y la prioridad solo determina el orden de extracción de la cola de espera (Cobham, 1954; Hillier y Lieberman, 2015). En las asambleas docentes, la prioridad por puntaje de mérito $P_i$ es no apropiativa: un docente con mayor puntaje no puede desalojar a quien ya se encuentra decidiendo frente a la autoridad.

A su vez, limitar la permanencia en ventanilla a un umbral $\tau$ convierte al tiempo de servicio en una variable aleatoria truncada:

$$S = \min(T_{\text{elección}}, \tau)$$

En caso de superar el umbral ($T_{\text{elección}} > \tau$) o registrarse una contingencia de conexión, el cliente no abandona el sistema sino que es derivado a una **cola de reintentos con realimentación (*feedback queue*)**. Esta cola secundaria se procesa con menor jerarquía que la principal, pero conservando internamente la prioridad no apropiativa por puntaje, impidiendo que demoras extremas penalicen a aspirantes que aguardan su primer turno.

### 2.5. Fundamentos de simulación de eventos discretos

Un modelo de **simulación de eventos discretos (SED)** representa la trayectoria temporal de un sistema cuyo estado evoluciona exclusivamente mediante cambios instantáneos en puntos discretos del tiempo (Banks et al., 2010; Law, 2015). El algoritmo opera bajo el mecanismo de **avance al próximo evento (*next-event time advance*)**, gestionado a través de una lista de eventos futuros (FEL, *Future Event List*), estructurada computacionalmente como una cola de prioridad basada en montículos binarios (*heapq*).

En una simulación de horizonte finito (*terminating simulation*), el comportamiento estocástico de interés está gobernado por las condiciones iniciales de la jornada y no admite el descarte de períodos de calentamiento (*warm-up*). Debido a la autocorrelación temporal existente entre los turnos consecutivos de una misma asamblea, las esperas individuales no pueden tratarse como observaciones independientes. El protocolo riguroso exige realizar $R_{\text{rep}} \ge 30$ **réplicas independientes** inicializadas con semillas disjuntas del generador pseudoaleatorio, permitiendo estimar el valor esperado de cada métrica $\bar{X}$ y su intervalo de confianza al nivel $1 - \alpha$ mediante la distribución $t$ de Student:

$$\bar{X} \pm t_{R_{\text{rep}} - 1 \, ; \, 1 - \alpha/2} \cdot \frac{s}{\sqrt{R_{\text{rep}}}}$$

### 2.6. Asignación por orden de mérito y sistemas de recomendación

Desde la perspectiva del diseño de mecanismos de mercado (*market design*), el procedimiento tradicional de designación docente donde los aspirantes son ordenados de mayor a menor puntaje y eligen sucesivamente entre las vacantes remanentes se formaliza como una **dictadura serial (*serial dictatorship*)** (Abdulkadiroğlu y Sönmez, 1998; Combe, Tercieux y Terrier, 2022). Este mecanismo ostenta propiedades matemáticas óptimas: es **eficiente en el sentido de Pareto**, **a prueba de manipulación estratégica (*strategy-proof*)** y garantiza la **ausencia de reclamos justificados de mérito** (ningún docente de menor puntaje accede a una vacante pretendida por un docente de mayor puntaje si este último era elegible para ella).

Dado que el orden de mérito legal establecido por la Ley Provincial N.° 6.830 no debe ser modificado, la optimización operativa del sistema no consiste en reordenar la nómina mediante algoritmos de emparejamiento forzoso, sino en **disminuir la incertidumbre y el tiempo de deliberación** de los aspirantes cuando sus opciones iniciales resultan agotadas. Para ello, se articulan tres paradigmas de **sistemas de recomendación híbridos** (Ricci, Rokach y Shapira, 2015):
1. **Filtrado basado en restricciones (*constraint-based*):** excluye taxativamente cargos que violen límites de distancia geodésica $R_i$, incompatibilidad de turno o ámbito rural no aceptado.
2. **Filtrado basado en contenido (*content-based*):** calcula la similitud entre las características objetivas de las escuelas vacantes (área geográfica, turno predominante, tipo) y las preferencias históricas declaradas por el docente.
3. **Filtrado colaborativo basado en vecindario (*collaborative filtering*):** pondera la popularidad de una escuela entre aspirantes que comparten patrones de elección fuertemente correlacionados en sus listas de precarga.

---

## 3. METODOLOGÍA Y FORMULACIÓN DEL MODELO

### 3.1. Correspondencia con los elementos de una cola

El acto público de designación docente se traduce al marco de la sección 2.1 conforme a la siguiente correspondencia:

| Elemento de teoría de colas | Correspondencia en el sistema de asignaciones docentes |
| :--- | :--- |
| **Cliente** | Docente habilitado en el Cuadro de Orden de Mérito definitivo |
| **Fuente de entrada** | Finita y cerrada: *N* docentes (*N* = 300 en la instancia base) presentes o convocados desde el inicio; no existe arribo externo de Poisson |
| **Servidor** | Comisión o ventanilla digital/presencial de adjudicación (*c* = 1 en la comparación base de E1, E2 y E3; *c* ∈ {2, 3} en sensibilidad) |
| **Tiempo de servicio** | Tiempo efectivo empleado en el turno, dependiente de la distribución log-normal de deliberación T_elección y de la política del escenario |
| **Colas** | Cola principal ordenada por puntaje Pᵢ y (en E2 y E3) cola secundaria de reintentos |
| **Disciplina de atención** | Prioridad no apropiativa estricta según puntaje Pᵢ dentro de cada cola, teniendo prelación absoluta la cola principal sobre la de reintentos |
| **Capacidad del sistema** | Finita, acotada superiormente por los *N* docentes empadronados |
| **Contingencias del cliente** | Desconexión o ausencia temporal al llamado con probabilidad *p* = 0,08, más truncamiento administrativo al cumplirse la ventana τ en E2 y E3 |

El proceso opera además acoplado a un **inventario compartido finito de vacantes**: la asamblea concluye en cuanto se atiende al último docente pendiente o se agota la totalidad de los cargos disponibles, lo que ocurra primero. En la notación de Kendall (sección 2.1), el sistema corresponde a un esquema transitorio con fuente finita y disciplina de prioridad con realimentación, carente de solución analítica exacta.

### 3.2. Escenario base (E1): cola secuencial sin límite de tiempo

El Escenario 1 modela el procedimiento tradicional sin acotamiento por turno. Se convoca a los docentes uno por uno en orden decreciente de puntaje Pᵢ sobre *c* = 1 comisión, y quien toma servicio dispone del tiempo completo requerido para decidir:

$$S_j = T_{\text{elección}, j}$$

Si el docente llamado no responde por ausencia o desconexión técnica (evento de probabilidad *p* = 0,08), la mesa ejecuta los llamados reglamentarios de verificación durante un tiempo fijo de protocolo $T_{\text{aus}} = 5$ minutos antes de declararlo ausente y avanzar al siguiente postulante, perdiendo aquel su oportunidad en el acto.

Para quienes permanecen en espera, el docente ubicado en la posición *k* aguarda la suma acumulada de servicios previos, $W_{q, k} = \sum_{j=1}^{k-1} S_j$. Cuando las vacantes preferidas por los docentes intermedios y finales comienzan a agotarse, su media de deliberación se cuadruplica respecto de su media basal $m_i$ (pasando de ~2 minutos a ~8 minutos con cola pesada log-normal, como se detalla en la sección 3.5.4). En consecuencia, unas pocas deliberaciones de 15 o 25 minutos se propagan íntegramente como demora acumulada sobre todos los postulantes subsiguientes.

### 3.3. Escenario E2: ventana τ, servicio truncado y cola de reintentos

El Escenario 2 introduce un límite máximo de permanencia en ventanilla igual a **τ = 10 minutos**, de modo que el tiempo efectivo de servicio por intento queda truncado en:

$$S = \min(T_{\text{elección}}, \tau)$$

Si el docente confirma un cargo en un tiempo $t \le \tau$, la adjudicación queda firme, se descuenta la vacante y el docente egresa del sistema. Si, en cambio, vence la ventana $\tau$ sin decisión ($T_{\text{elección}} > \tau$) o se registra una desconexión/ausencia al llamado (en cuyo caso el turno se da por vencido al agotarse la ventana o tras el tiempo de verificación acotado a $\tau$), el docente no bloquea al resto de la nómina: es derivado a una **cola secundaria de reintentos** de menor prioridad.

Las reglas operativas de la cola de reintentos son:
1. Se atiende recién cuando la cola principal queda vacía (siempre que aún resten cargos libres), evitando perjudicar a docentes que todavía no tuvieron su primera oportunidad.
2. Dentro de la cola secundaria los postulantes conservan su puntaje original $P_i$ (prioridad no apropiativa por mérito).
3. Se admite como máximo **una ronda de reintento** por docente; si en esta segunda instancia vuelve a superar $\tau$ o permanece desconectado, egresa definitivamente sin asignación.

A título ilustrativo con una distribución exponencial de media $1/\mu = 6$ minutos para un docente cuyas opciones iniciales ya fueron tomadas, con ventana $\tau = 10$ minutos y probabilidad de desconexión $p = 0,08$ (asumiendo que una desconexión insume el tope $\tau$), la probabilidad de exceder la ventana estando conectado es $P\{T > \tau\} = e^{-10/6} \approx 0,189$, el tiempo medio truncado es $E[\min(T, \tau)] = (1 - e^{-10/6})/\mu \approx 4,87$ minutos, y la fracción derivada a reintentos en ese segmento crítico resulta:

$$q = p + (1 - p) \cdot P\{T > \tau\} \approx 0,08 + 0,92 \cdot 0,189 = 0,254 \quad ; \quad E[S] = p \cdot \tau + (1 - p) \cdot E[\min(T, \tau)] \approx 5,28 \text{ min}$$

Por el contrario, para un docente con opciones vigentes y media basal de 2 minutos, $P\{T > 10\} = e^{-5} \approx 0,0067$, por lo que prácticamente ningún postulante decidido es desplazado por el reloj. El tope $\tau$ poda selectivamente la cola derecha extrema de los tiempos de servicio para proteger la espera global de la asamblea.

### 3.4. Estimador dinámico de horario y aviso previo

Dado que el orden de llamado es conocido desde la apertura, en cualquier instante $t_{\text{actual}}$ el sistema estima el horario esperado de inicio de atención del docente ubicado en la posición pendiente *k* como:

$$E[T_k] = t_{\text{actual}} + \frac{1}{c} \cdot \left[ E[S_{\text{restante}}] + \sum_{j=1}^{k-1} E[S_j] \right]$$

donde $E[S_{\text{restante}}]$ corresponde al tiempo remanente esperado del servicio en curso y $E[S_j]$ es la duración esperada truncada de cada postulante que precede a *k* en la fila. El estimador es **reactivo en tiempo real**: cada vez que un docente concreta su elección antes de lo previsto o pasa a la cola de reintentos, su término esperado desaparece de la suma y se actualizan instantáneamente los horarios proyectados de quienes restan. Cuando se verifica la condición:

$$E[T_k] - t_{\text{actual}} \le 10 \text{ minutos}$$

el sistema emite la notificación automática *«Prepárese: su turno se estima en 10 minutos»*, eliminando la espera ciega frente al dispositivo.

### 3.5. Escenario E3: recomendación de escuelas y aviso anticipado de disponibilidad

Mientras que E2 acota el daño de las deliberaciones extensas cortándolas en $\tau$, el Escenario 3 ataca la causa de raíz de esas demoras: el desconcierto del docente que llega a la ventanilla cuando las hasta *M* = 5 escuelas que había preseleccionado ya fueron tomadas. Sin alterar el orden de mérito $P_i$ ni imponer asignaciones forzosas (preservando las propiedades de la dictadura serial descriptas en la sección 2.6), E3 incorpora una etapa previa de precarga y dos asistencias informativas en línea.

#### 3.5.1. Filtro por criterios de reserva declarados

Durante la precarga previa a la asamblea, además de ordenar hasta *M* = 5 escuelas preferidas (lista $L_i$), el docente *i* declara tres criterios explícitos de reserva:

* **$R_i$**: distancia máxima aceptable desde su domicilio hasta el establecimiento (en km).
* **$\text{Turnos}_i$**: subconjunto de turnos que puede desempeñar ({mañana, tarde, noche}).
* **$\text{Rural}_i \in \{0, 1\}$**: indicador de si acepta cargos en establecimientos de ámbito rural.

En un estado dado de la asamblea, una escuela *j* pertenece al conjunto de **candidatas factibles** $K_i(\text{estado})$ del docente *i* si y solo si: (a) posee al menos una vacante libre compatible con el nivel y la especialidad del docente, (b) la distancia geodésica domicilio-escuela verifica $d_{ij} \le R_i$, (c) alguna de esas vacantes compatibles pertenece a $\text{Turnos}_i$, y (d) la escuela es urbana o bien $\text{Rural}_i = 1$. Ninguna escuela fuera de $K_i$ se sugiere jamás al postulante.

#### 3.5.2. Puntaje híbrido de recomendación

Para ordenar las escuelas candidatas $j \in K_i(\text{estado})$ que no integraban la lista original $L_i$, se calcula el puntaje normalizado en $[0, 1]$:

$$\text{Puntaje}_{ij} = w_d \cdot D_{ij} + w_t \cdot T_{ij} + w_c \cdot C_{ij} \quad , \quad \text{con } w_d + w_t + w_c = 1 \quad \text{y} \quad w_d, w_t, w_c \ge 0$$

donde cada componente captura una dimensión distinta de preferencia:

1. **Cercanía geográfica ($D_{ij}$):**
   $$D_{ij} = 1 - \frac{d_{ij}}{R_i}$$
   Toma el valor 1 cuando la escuela coincide con el domicilio del docente y decrece linealmente hasta 0 en el radio máximo tolerado $R_i$.
2. **Similitud de contenido con la propia lista ($T_{ij}$):** proporción ponderada de atributos institucionales (turno predominante, zona barrial y ámbito urbano/rural) que la escuela *j* comparte con el perfil medio de las escuelas incluidas originalmente en $L_i$. Si las cinco escuelas elegidas por el docente pertenecen a zona sur y turno mañana, una candidata libre con ambos rasgos alcanza $T_{ij} = 1$.
3. **Coincidencia colaborativa entre pares ($C_{ij}$):** mide la frecuencia con que otros docentes con gustos afines eligieron la escuela *j* en sus propias precargas:
   $$C_{ij} = \frac{\sum_{k \ne i} |L_k \cap L_i| \cdot I(j \in L_k)}{\sum_{k \ne i} |L_k \cap L_i|}$$
   donde $I(j \in L_k)$ vale 1 si $j$ figura en $L_k$ y 0 en caso contrario. Cada colega *k* «vota» por las escuelas de su lista con un peso proporcional a la cantidad de establecimientos en común con *i*.

Los pesos de referencia iniciales son $w_d = 0,5$, $w_t = 0,2$ y $w_c = 0,3$, sujetos a la calibración sistemática de la sección 5.2. Al iniciarse el turno de un docente sin vacantes libres en $L_i$, la pantalla le destaca en primer término las $k_{\text{rec}} = 3$ escuelas candidatas con mayor puntaje.

#### 3.5.3. Pronóstico de disponibilidad mediante simulación Monte Carlo hacia adelante

En el instante en que el estimador de la sección 3.4 dispara el aviso *«Prepárese»* (10 minutos antes del turno previsto del docente *i*), quedan por delante relativamente pocos postulantes en la fila activa, pero sus elecciones determinarán si las escuelas de $L_i$ llegan libres o agotadas. Para anticipar ese escenario, el sistema ejecuta en segundo plano $R_{\text{MC}} = 200$ micro-simulaciones Monte Carlo rápidas partiendo de una copia exacta del estado vigente (vacantes libres actuales y subcola de docentes que preceden a *i*):

1. Se recorren secuencialmente los docentes previos a *i* en orden de turno.
2. En cada réplica interna, cada predecesor sufre desconexión/timeout sin tomar cargo con su probabilidad efectiva, o bien adjudica la primera escuela con vacante compatible disponible en su lista $L_h$; si ninguna sigue libre, toma con probabilidad $p_{\text{rec}}$ la primera alternativa de su ranking de recomendación (o elige entre el resto de compatibles).
3. Al alcanzar la posición de *i*, se registra para cada escuela $j$ si conserva al menos una vacante compatible libre.
4. Promediando sobre las $R_{\text{MC}} = 200$ trayectorias se obtiene el estimador $\theta_{ij} \in [0, 1]$ de la probabilidad de disponibilidad de cada establecimiento *j* al momento del turno de *i*.

El mensaje enviado al docente informa las probabilidades $\theta_{ij}$ de sus escuelas preseleccionadas y, cuando todas verifican $\theta_{ij} < 0,50$, adjunta preventivamente las tres candidatas externas que maximizan el **valor esperado de utilidad disponible**, $\text{Puntaje}_{ij} \cdot \theta_{ij}$. De este modo, el postulante dispone de los 10 minutos previos a su llamado para evaluar opciones concretas y altamente factibles antes de ingresar a la ventanilla.

#### 3.5.4. Modelo unificado del tiempo de decisión por casos

Para reflejar de manera consistente el vínculo entre disponibilidad de vacantes y demora humana a través de los tres escenarios, sea $m_i$ la media basal de decisión propia del docente *i* cuando encuentra opciones previstas disponibles. La media efectiva $\mu_{\text{eff}}(i)$ de su distribución log-normal de deliberación al ser atendido depende de la situación observada en ventanilla según tres regímenes:

| Régimen | Situación al iniciar el turno del docente *i* | Media log-normal | Ocurrencia en E1 y E2 | Ocurrencia en E3 |
| :---: | :--- | :---: | :--- | :--- |
| **Caso A** | Al menos una escuela de su lista $L_i$ conserva vacante compatible libre | **$1 \cdot m_i$** | Cuando $L_i$ tiene vacante libre (en E1 implícitamente las opciones que el docente traía en mente) | Cuando $L_i$ tiene vacante libre |
| **Caso B** | $L_i$ agotada, pero el docente decide guiado por las $k_{\text{rec}} = 3$ recomendaciones y el preaviso | **$2 \cdot m_i$** | No aplica (no existe sistema de recomendación ni preaviso) | Con probabilidad **$p_{\text{rec}} = 0,70$** (si $K_i \ne \emptyset$) |
| **Caso C** | $L_i$ agotada y el docente inspecciona manualmente el padrón remanente completo | **$4 \cdot m_i$** | Siempre que $L_i$ se encuentre agotada | Con probabilidad **$1 - p_{\text{rec}} = 0,30$** (o si $K_i = \emptyset$) |

Esta formulación asegura una comparación limpia y auditable: E1 carece de ventana $\tau$ y opera solo bajo los Casos A y C; E2 agrega la ventana $\tau = 10$ minutos, el aviso horario y la cola de reintentos sobre los mismos Casos A y C; y E3 mantiene intacta la mecánica de colas de E2, midiendo exactamente cuánto disminuyen $W_q$, $L_q$, los pases a reintentos y la duración de jornada cuando el 70 % de las búsquedas a ciegas (Caso C, media $4 \cdot m_i$) se transforman en elecciones asistidas y preavisadas (Caso B, media $2 \cdot m_i$).

### 3.6. Métricas de desempeño

En cada réplica de simulación se relevan seis indicadores principales:

1. **Tiempo medio de espera en cola ($W_q$):** promedio en minutos, sobre los docentes atendidos, del lapso transcurrido desde la apertura de la asamblea hasta el inicio efectivo de su atención (incluyendo la espera adicional de quienes pasan por la cola de reintentos).
2. **Longitud media de la cola ($L_q$):** promedio ponderado en el tiempo de la cantidad total de docentes aguardando turno durante la jornada:
   $$L_q = \frac{1}{T_{\text{total}}} \int_0^{T_{\text{total}}} N_{\text{cola}}(t) \, dt = \frac{\sum_j W_{q, j}}{T_{\text{total}}}$$
   Esta identidad constituye la versión exacta en horizonte finito de la fórmula de Little (sección 2.1) y se emplea como control interno de coherencia en cada corrida.
3. **Duración total de la jornada ($T_{\text{total}}$):** instante en minutos en que finaliza el último servicio del acto público (por agotamiento de cargos o fin de ambas colas).
4. **Proporción de derivación a reintentos:** fracción de docentes de la cola principal cuyo primer intento culmina por vencimiento de $\tau$ o desconexión.
5. **Tasa de cobertura de vacantes:** porcentaje de los cargos ofrecidos que resultan efectivamente adjudicados al cierre de la jornada.
6. **Satisfacción media de los adjudicatarios:** utilidad promedio alcanzada por los docentes que obtuvieron cargo (midiendo pertenencia y posición en $L_i$ o $\text{Puntaje}_{ij}$ alcanzado).

### 3.7. Resumen de notación y convenciones

| Símbolo | Significado y unidades | Valor de referencia |
| :---: | :--- | :---: |
| *N* | Cantidad total de docentes convocados en el orden de mérito | 300 docentes |
| *V_tot* | Cantidad total de vacantes de cargos ofrecidas en la asamblea | 100 vacantes |
| *E_tot* | Cantidad de establecimientos educativos en el padrón de la instancia | 40 escuelas |
| $P_i$ | Puntaje oficial del docente *i* en el Cuadro de Orden de Mérito | [20,00 ; 100,00] |
| $\tau$ | Ventana máxima de decisión por intento en E2 y E3 (reservado exclusivamente a este uso) | 10 min (sensib.: 8, 15) |
| *c* | Cantidad de comisiones o ventanillas de atención simultáneas | 1 (sensib.: 2, 3) |
| *M* | Cantidad máxima de escuelas precargadas en la lista $L_i$ | 5 escuelas |
| $m_i$ | Media basal de decisión del docente *i* en Caso A | [1,0 ; 3,0] min |
| $\sigma$ | Parámetro común de dispersión de la normal subyacente en la distribución log-normal | 0,8 |
| $S_j$ | Tiempo efectivo de servicio del intento *j*, $S_j = \min(T_{\text{elección}}, \tau)$ | minutos |
| *p* | Probabilidad de desconexión o falla de respuesta por turno | 0,08 |
| $T_{\text{aus}}$ | Tiempo de protocolo para declarar ausente a un desconectado en E1 | 5,0 min |
| $k_{\text{rec}}$ | Cantidad de escuelas alternativas sugeridas por el recomendador en E3 | 3 escuelas |
| $p_{\text{rec}}$ | Probabilidad de decidir dentro del conjunto recomendado en E3 (Caso B vs. C) | 0,70 |
| $w_d, w_t, w_c$ | Pesos de cercanía, contenido y filtrado colaborativo en $\text{Puntaje}_{ij}$ | 0,5 ; 0,2 ; 0,3 |
| $R_{\text{MC}}$ | Cantidad de micro-simulaciones Monte Carlo para estimar $\theta_{ij}$ en el preaviso | 200 corridas |
| $R_{\text{rep}}$ | Cantidad de réplicas independientes de jornada completa por escenario | 30 réplicas |
| $W_q, L_q$ | Tiempo medio de espera en cola (min) y cantidad media de docentes en cola | métricas de salida |
| $\lambda, \mu, \rho, P_0$ | Tasas, utilización y probabilidad de estado vacío en modelos analíticos de prueba | validación |

---

## 4. DATOS E IMPLEMENTACIÓN COMPUTACIONAL

### 4.1. Origen de los datos: fuentes oficiales y generación sintética

De acuerdo con los criterios metodológicos de la asignatura, resulta indispensable distinguir qué variables provienen de registros públicos verificables y cuáles requieren generación sintética justificada debido a reserva legal o inexistencia de medición previa:

1. **Infraestructura escolar real (`data/escuelas.csv`).** La localización geográfica, denominación, código jurisdiccional, ámbito (urbano o rural) y oferta de niveles de los establecimientos educativos de la Provincia de Salta son datos públicos contenidos en el **Padrón Oficial de Establecimientos Educativos** (Base Nacional Homologada de la Red Federal de Información Educativa y portal *Edusalta*, MECCyT, 2024). Para construir la instancia representativa se seleccionan **40 establecimientos reales de gestión estatal del Departamento Capital**, abarcando escuelas históricas del micro y macrocentro salteño —tales como la Escuela N.° 4.001 *Juan Bautista Alberdi* (Caseros 1150), la Escuela N.° 4.002 *Mariano Cabezón* y la Escuela N.° 4.017 *Domingo Faustino Sarmiento* (Alvarado 427)— junto con establecimientos de los barrios de zonas norte, sur, este, oeste y parajes periurbanos/rurales del municipio y su entorno en el Valle de Lerma. A partir de sus coordenadas geográficas reales (latitud $\phi$ y longitud $\lambda_{\text{geo}}$ en grados decimales), las distancias $d_{ij}$ en kilómetros se calculan de forma exacta mediante la fórmula geodésica de Haversine sobre radio terrestre medio $R_T = 6.371$ km.
2. **Vacantes ofrecidas (`data/cargos.csv`).** Si bien las planillas de vacantes se exhiben en cada convocatoria anual, su detalle histórico desagregado no se publica como serie abierta estandarizada. Se genera por ello un lote de **100 cargos vacantes** distribuidos sobre las 40 escuelas reales, respetando la oferta de niveles (Inicial, Primario y Secundario) y turnos habituales (mañana, tarde y, en menor proporción, vespertino/noche), con mayor concentración relativa de vacantes libres en zonas periféricas, tal como ocurre empíricamente tras los movimientos previos de traslado docente.
3. **Padrón de aspirantes y preferencias (`data/docentes.csv`).** Aunque los Cuadros de Orden de Mérito son públicos para consulta nominal por DNI en *Edusalta*, los domicilios particulares de los docentes están protegidos por normativa de datos personales, y ni las listas previas de escuelas deseadas ni los tiempos individuales de deliberación existen hoy como registro porque forman parte de las innovaciones propuestas en este proyecto. En consecuencia, los **300 docentes** de la instancia se generan de forma sintética con semilla pseudoaleatoria fija (`semilla = 2026`), bajo supuestos explícitos coherentes con la geografía de Salta Capital:
   * **Puntajes $P_i$:** valores estrictamente distintos en el rango [20,00 ; 100,00] conforme a la escala de dos decimales de la Resolución Ministerial N.° 1.851/08, distribuidos con asimetría moderada (mayor densidad de aspirantes noveles e intermedios entre 25 y 65 puntos y cola superior de docentes con alta antigüedad y postítulos).
   * **Domicilios:** coordenadas sorteadas dentro de la mancha residencial del Departamento Capital siguiendo su gradiente real de densidad poblacional (INDEC, 2023).
   * **Tiempos medios basales $m_i$:** distribución uniforme continua en [1,0 ; 3,0] minutos para el Caso A.
   * **Criterios de reserva:** radio máximo $R_i \sim U(5, 15)$ km para zonas urbanas (ampliado hasta 25 km si acepta ámbito rural, condición asignada al 30 % del padrón) y uno o dos turnos aceptados.
   * **Lista verdadera de preferencias (10 escuelas):** para cada docente se muestrean sin reposición 10 escuelas compatibles con probabilidad proporcional a una utilidad latente función decreciente de la distancia domicilio-escuela y creciente con la centralidad del establecimiento y la coincidencia de turno. Las primeras *M* = 5 conforman la columna `preferencias` visible para el sistema; las posiciones 6 a 10 se reservan en `preferencias_ocultas` exclusivamente para auditar la precisión del recomendador fuera de muestra (sección 5.2).

### 4.2. Formato de los archivos de datos

**`data/escuelas.csv`**

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `id_escuela` | texto | Identificador interno (`ESC01` a `ESC40`) |
| `cue_anexo` | texto | Código Único de Establecimiento oficial (cuando corresponde al padrón nacional) |
| `nombre` | texto | Denominación oficial del establecimiento en Salta Capital |
| `latitud`, `longitud` | decimal | Coordenadas geográficas reales (WGS84) |
| `zona` | texto | `centro`, `norte`, `sur`, `este`, `oeste` o `periurbana` |
| `tipo` | texto | `urbana` o `rural` |

**`data/cargos.csv`**

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `id_cargo` | texto | Identificador de la oferta (`C001` a `C100`) |
| `id_escuela` | texto | Clave foránea hacia `escuelas.csv` |
| `nivel` | texto | `inicial`, `primario` o `secundario` |
| `especialidad` | texto | `maestro_jardín`, `maestro_grado`, `matemática`, `lengua`, `inglés`, `educación_física` |
| `turno` | texto | `mañana`, `tarde` o `noche` |
| `vacantes` | entero | Cantidad de puestos idénticos del registro (por defecto 1) |

**`data/docentes.csv`**

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `id` | texto | Identificador del postulante (`D001` a `D300`) |
| `puntaje` | decimal | Puntaje oficial $P_i$ en el Cuadro de Orden de Mérito |
| `tiempo_decision_medio` | decimal | Media basal $m_i$ en minutos (Caso A) |
| `nivel` | texto | Nivel educativo habilitado |
| `especialidad` | texto | Especialidad habilitada (define compatibilidad exacta con `cargos.csv`) |
| `latitud`, `longitud` | decimal | Domicilio del docente dentro del Departamento Capital |
| `preferencias` | texto | Lista $L_i$ de hasta *M* = 5 `id_escuela` ordenados por prioridad, separados por `;` |
| `radio_max_km` | decimal | Distancia máxima aceptada $R_i$ en kilómetros |
| `turnos` | texto | Turnos aceptados separados por `;` |
| `acepta_rural` | entero | `1` si acepta escuelas rurales, `0` en caso contrario |
| `preferencias_ocultas` | texto | Escuelas 6 a 10 de su ranking verdadero (uso exclusivo de validación en sección 5.2; ignorada por el simulador) |

### 4.3. Parametrización de la distribución log-normal

Si una variable aleatoria positiva $T$ sigue una distribución log-normal con esperanza deseada *m* (donde $m \in \{m_i, 2 \cdot m_i, 4 \cdot m_i\}$ según el régimen A, B o C de la sección 3.5.4) y parámetro de forma $\sigma$ en la escala logarítmica, los parámetros de la distribución normal subyacente $\ln(T) \sim N(\mu_{\text{LN}}, \sigma^2)$ se determinan de forma unívoca mediante:

$$\mu_{\text{LN}} = \ln(m) - \frac{\sigma^2}{2}$$

Se emplea el subíndice `LN` para evitar cualquier ambigüedad con la tasa de servicio $\mu$ de la teoría de colas. Se fija **$\sigma = 0,8$** como parámetro común en `src/utils.py`. Esta elección reproduce una asimetría derecha realista: para un docente en Caso A con $m = 2$ minutos, la mediana de decisión es $\exp(\mu_{\text{LN}}) \approx 1,45$ minutos y apenas el 1,3 % supera los 10 minutos; en cambio, para un docente desorientado en Caso C con $m = 8$ minutos, la mediana asciende a 5,81 minutos y cerca del 35 % excedería la barrera de 10 minutos si no existiera ventana ni asistencia.

### 4.4. Arquitectura modular e interfaz con el simulador

A diferencia de una optimización estática fuera de línea, las recomendaciones y probabilidades de disponibilidad en E3 evolucionan dinámicamente a medida que se ocupan las vacantes durante la jornada. Por ello, la implementación en Python 3 se organiza en módulos desacoplados bajo el directorio `src/`:

* **`src/utils.py`**: constantes globales compartidas ($\sigma = 0,8$, fórmula geodésica de Haversine, generadores log-normales y exponenciales con control de semillas `numpy.random.Generator` independientes).
* **`src/generar_datos.py`**: construcción reproducible de `escuelas.csv`, `cargos.csv` y `docentes.csv`.
* **`src/recomendador.py`**: encapsula la lógica del Escenario 3 y expone tres funciones puras consumidas por el motor de eventos:
  * `candidatas(docente, estado)` → filtra las escuelas con vacantes compatibles libres según $R_i$, $\text{Turnos}_i$ y $\text{Rural}_i$ (sección 3.5.1).
  * `recomendar(docente, estado, k=3)` → calcula $\text{Puntaje}_{ij}$ y retorna las *k* mejores alternativas (sección 3.5.2).
  * `pronosticar(docente, estado, R_MC=200)` → ejecuta la simulación Monte Carlo hacia adelante y devuelve el vector $\theta_{ij}$ junto con las sugerencias preventivas para el aviso de 10 minutos (sección 3.5.3).
* **`src/simulation.py`**: motor de simulación de eventos discretos basado en una cola de prioridad (`heapq`) para la FEL, que implementa tanto el modo estacionario abierto (para validación de referencia) como el modo de jornada finita para E1, E2 y E3. En el inicio de servicio de un docente en E2 o E3 agenda dos eventos competitivos —fin de elección en `t + T_elección` y vencimiento de ventana en `t + τ`—, ejecutando el menor y cancelando el restante.
* **`notebooks/experimentos.ipynb`**: ejecución reproducible de validaciones, corridas de escenarios, cálculo de intervalos de confianza y generación de gráficos y tablas.

---

## 5. VERIFICACIÓN, VALIDACIÓN Y DISEÑO EXPERIMENTAL

### 5.1. Validación analítica del motor de simulación

Antes de activar la prioridad por puntaje, el truncamiento en $\tau$ y la cola de reintentos, se verifica y valida que el núcleo de eventos discretos (`src/simulation.py`) reproduzca sin sesgo las soluciones analíticas exactas de los modelos markovianos clásicos vistos en la sección 2.2 (Rivadera, 2026b, 2026c). Configurando llegadas de Poisson, servicios exponenciales y disciplina FCFS sobre corridas largas (100.000 clientes atendidos tras descartar los primeros 10.000 como período de calentamiento; Law, 2015), las medias muestrales del simulador deben contener los siguientes valores teóricos dentro de sus intervalos de confianza al 95 %:

| Modelo de prueba | Parámetros de tasa | Indicadores teóricos exactos de referencia |
| :--- | :--- | :--- |
| **M/M/1** | $\lambda = 4$ /h, $\mu = 6$ /h | $\rho = 0,6667$ ; $L = 2,0000$ ; $L_q = 1,3333$ ; $W = 0,5000$ h ; $W_q = 0,3333$ h |
| **M/M/c ($c=1$ vs. $c=2$)** | $\lambda = 2$ /h, $\mu = 3$ /h | $c = 1$: $W_q = 0,6667$ h (40 min) $\quad ; \quad c = 2$: $W_q = 0,0417$ h (2,5 min) |

De forma complementaria, sobre las corridas de horizonte finito (E1, E2 y E3) se verifican tres invariantes determinísticos en cada réplica: (1) cumplimiento exacto de la identidad finita de Little $L_q = (\sum W_{q, j})/T_{\text{total}}$; (2) conservación estricta de vacantes (ningún cargo supera sus vacantes declaradas ni se adjudica a un docente de nivel o especialidad incompatibles); y (3) respeto del orden de mérito en la cola principal (los inicios de primer servicio son estrictamente monótonos decrecientes en $P_i$).

### 5.2. Validación y calibración del recomendador de escuelas

Para evaluar objetivamente la calidad del recomendador antes de acoplarlo al simulador, se ejecuta un experimento de validación cruzada sobre las preferencias ocultas de los *N* = 300 docentes:

1. Se entrega al algoritmo únicamente la lista visible $L_i$ (primeras 5 escuelas), ocultando las posiciones 6 a 10 (`preferencias_ocultas`).
2. Se marcan las 5 escuelas de $L_i$ como agotadas y se solicita a `recomendar(docente, estado, k=3)` que proponga 3 establecimientos entre los restantes.
3. Se contabiliza la **tasa de acierto en el top 3 (*Hit Rate@3*)**: proporción de docentes para quienes al menos una de las 3 escuelas recomendadas pertenece a sus 5 preferencias verdaderas ocultas.

El método híbrido propuesto se contrasta contra cuatro configuraciones base y de ablación:
* **Azar factible:** elegir 3 escuelas al azar dentro del filtro de reserva $K_i$.
* **Solo cercanía:** $w_d = 1, w_t = 0, w_c = 0$.
* **Solo contenido:** $w_d = 0, w_t = 1, w_c = 0$.
* **Solo colaborativo:** $w_d = 0, w_t = 0, w_c = 1$.
* **Híbrido calibrado:** combinación $(w_d, w_t, w_c)$ óptima sobre el símplex $w_d + w_t + w_c = 1$.

Dado que el vector de pesos reside en un símplex bidimensional de solo tres variables continuas, discretizarlo con paso 0,05 arroja únicamente $(21 \times 22)/2 = 231$ combinaciones, lo que permite hallar el óptimo exacto de la grilla en fracciones de segundo sin necesidad de emplear una metaheurística (reservándose los métodos metaheurísticos para extensiones complejas con decenas de atributos ponderados o calibración conjunta con el simulador; Taha, 2017, cap. 10).

### 5.3. Diseño experimental y análisis de sensibilidad

La experimentación principal compara sistemáticamente los tres escenarios bajo idénticas entradas (`docentes.csv`, `escuelas.csv`, `cargos.csv`) y números aleatorios comunes (*common random numbers*) por réplica para reducir la varianza de las diferencias pareadas (Law, 2015, cap. 11), ejecutando **$R_{\text{rep}} = 30$ réplicas independientes** por configuración:

* **Experimento 1 — Comparación central de escenarios ($c = 1, \tau = 10$ min):** E1 (secuencial sin límite) vs. E2 (ventana $\tau$ + alerta + cola de reintentos) vs. E3 (E2 + recomendador híbrido + pronóstico Monte Carlo en el aviso previo).
* **Experimento 2 — Sensibilidad respecto de la ventana máxima $\tau$ (en E2 y E3, con $c = 1$):** evaluación de $\tau \in \{6, 8, 10, 12, 15\}$ minutos para cuantificar el compromiso entre recorte de esperas en la cola principal y volumen de docentes derivados a la cola secundaria de reintentos.
* **Experimento 3 — Sensibilidad respecto de la cantidad de comisiones simultáneas *c* (en E2 y E3, con $\tau = 10$ min):** evaluación de $c \in \{1, 2, 3\}$ comisiones operando en paralelo sobre el padrón compartido de vacantes (verificando el efecto no lineal de reducción de espera análogo al observado en el modelo $M/M/c$ de la sección 2.2 y su impacto sobre eventuales colisiones de disponibilidad).

---

## 6. RESULTADOS Y ANÁLISIS

> *[SECCIÓN PENDIENTE DE EJECUCIÓN COMPUTACIONAL — VIERNES 06/11 Y SÁBADO 07/11]*
> *Conforme al cronograma del proyecto, las tablas e indicadores siguientes se completarán exclusivamente con las salidas numéricas verificadas de las 30 réplicas por escenario generadas desde `notebooks/experimentos.ipynb`.*

### 6.1. Resultados de la validación analítica del simulador

| Modelo de prueba | Métrica | Valor teórico exacto | Media simulada (IC 95 %) | Error relativo (%) |
| :--- | :---: | :---: | :---: | :---: |
| $M/M/1$ ($\lambda=4, \mu=6$) | $W_q$ (h) | 0,3333 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/1$ ($\lambda=4, \mu=6$) | $L_q$ (clientes) | 1,3333 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/2$ ($\lambda=2, \mu=3$) | $W_q$ (h) | 0,0417 | *[Pendiente corrida]* | *[Pendiente]* |
| $M/M/2$ ($\lambda=2, \mu=3$) | $P_0$ | 0,5000 | *[Pendiente corrida]* | *[Pendiente]* |

### 6.2. Desempeño y calibración del recomendador (Hit Rate@3)

| Configuración del recomendador | Pesos ($w_d ; w_t ; w_c$) | Hit Rate@3 (%) | Mejora vs. azar |
| :--- | :---: | :---: | :---: |
| Selección aleatoria dentro del filtro $K_i$ | — | *[Pendiente]* | — |
| Solo cercanía geográfica | (1,00 ; 0,00 ; 0,00) | *[Pendiente]* | *[Pendiente]* |
| Solo similitud de contenido | (0,00 ; 1,00 ; 0,00) | *[Pendiente]* | *[Pendiente]* |
| Solo filtrado colaborativo | (0,00 ; 0,00 ; 1,00) | *[Pendiente]* | *[Pendiente]* |
| Híbrido calibrado | *[Óptimo en grilla]* | *[Pendiente]* | *[Pendiente]* |

### 6.3. Comparación principal entre escenarios (E1, E2 y E3 — 30 réplicas)

| Métrica de desempeño (Media ± IC 95 %) | E1 (Tradicional) | E2 (Ventana $\tau$ + Reintentos) | E3 (E2 + Recomendación y Preaviso) |
| :--- | :---: | :---: | :---: |
| Tiempo medio de espera en cola, $W_q$ (min) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Largo medio de cola, $L_q$ (docentes) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Duración total de la jornada, $T_{\text{total}}$ (min / h) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Derivación a cola de reintentos (%) | No aplica | *[Pendiente]* | *[Pendiente]* |
| Cargos vacantes cubiertos (%) | *[Pendiente]* | *[Pendiente]* | *[Pendiente]* |
| Error absoluto medio del estimador horario (min) | No aplica | *[Pendiente]* | *[Pendiente]* |

### 6.4. Análisis de sensibilidad sobre $\tau$ y *c*

*[Espacio reservado para insertar las figuras generadas por el notebook: (Figura 1) Boxplot de $T_{\text{total}}$ por escenario; (Figura 2) Curva de compromiso $W_q$ vs. tasa de reintentos al variar $\tau \in \{6, 8, 10, 12, 15\}$ min; (Figura 3) Reducción de $T_{\text{total}}$ y $W_q$ para $c \in \{1, 2, 3\}$ comisiones simultáneas, junto con su interpretación cuantitativa.]*

---

## 7. DISCUSIÓN

### 7.1. Implicancias operativas para la Junta Calificadora de Salta

El diseño modelado aborda el problema de congestión de las asambleas docentes distinguiendo dos dimensiones que suelen confundirse en la discusión administrativa: la **regla jurídica de prioridad** y la **organización del flujo de atención**. Respetar de forma irrestricta el puntaje de la Resolución Ministerial N.° 1.851/08 y de la Ley N.° 6.830 exige mantener el orden de adjudicación por mérito (dictadura serial), pero no obliga a sostener esperas ciegas ni tiempos de deliberación ilimitados en ventanilla.

La articulación entre los escenarios E2 y E3 muestra que ambas intervenciones cumplen funciones complementarias:
* La **ventana $\tau$ y la cola de reintentos (E2)** operan como un mecanismo de contención estructural: impiden que una falla técnica de conectividad o una indecisión aislada bloquee a centenares de docentes posteriores, sin despojar de su derecho al postulante afectado, quien conserva su puntaje relativo en la ronda complementaria.
* La **recomendación híbrida con pronóstico Monte Carlo en el preaviso (E3)** actúa preventivamente sobre el tiempo de servicio antes de que el reloj $\tau$ deba intervenir, suministrando información filtrada por distancia, turno y afinidad justo cuando las opciones originales del docente están próximas a agotarse.

### 7.2. Supuestos críticos y limitaciones del estudio

La interpretación de los resultados debe contemplar las limitaciones inherentes a los supuestos adoptados:

1. **Microdatos de preferencias y tiempos de decisión sintéticos.** Si bien la red espacial de establecimientos se apoya en escuelas reales del Departamento Capital y el marco institucional reproduce la normativa salteña, las listas individuales de preferencias, los radios tolerados y los factores multiplicadores de demora ($1 \cdot m_i$, $2 \cdot m_i$ y $4 \cdot m_i$, junto con $p_{\text{rec}} = 0,70$) son parámetros modelados. En una prueba piloto real de la Secretaría de Gestión Educativa, estos valores podrían estimarse directamente a partir de registros de tiempo de sesión (*logs* de plataforma).
2. **Cargos indivisibles frente a bloques de horas cátedra.** El modelo asume que cada docente toma a lo sumo un cargo unitario, supuesto fiel para los niveles Inicial y Primario. En el Nivel Secundario, donde un profesor suele combinar varios paquetes de horas cátedra compatibles en distintos colegios sin superposición horaria, la decisión individual se vuelve un problema combinatorio de armado de horario personal que requeriría extender tanto el filtro de restricciones como la distribución de servicio.
3. **Concurrencia en múltiples comisiones ($c > 1$).** Cuando dos o más comisiones atienden simultáneamente un mismo cuadro de mérito (análisis de sensibilidad con $c \in \{2, 3\}$), puede ocurrir que el docente de puntaje $k + 1$ elija un segundo antes que el de puntaje $k$ si este último delibera más tiempo dentro de su ventana $\tau$. En la práctica administrativa, las comisiones paralelas resultan totalmente libres de colisión de mérito cuando particionan el padrón por nivel o especialidad independiente (por ejemplo, una comisión para Nivel Inicial, otra para Maestro de Grado y otra para Educación Física), mientras que sobre una misma especialidad exigen un bloqueo temporal de vacante o aceptar dicha concurrencia dentro del margen de la ventana.

### 7.3. Posibles extensiones futuras

A partir de la plataforma de simulación construida se abren tres líneas directas de continuación:
* **Estimación econométrica de preferencias con datos históricos:** disponer de actas reales de designación permitiría ajustar un modelo logit multinomial o logit mixto de elección discreta sobre distancias, turnos y características barriales en reemplazo de los pesos lineales propuestos.
* **Optimización vía simulación con metaheurísticas:** cuando se desee dimensionar simultáneamente la asignación de personal administrativo a múltiples salas/especialidades, las franjas horarias de citación escalonada y umbrales $\tau$ diferenciados por especialidad sujetas a un presupuesto operativo fijo, el espacio combinatorio resultante justifica acoplar una búsqueda tabú o un algoritmo genético sobre las salidas del simulador (Law, 2015, cap. 12; Taha, 2017, cap. 10).
* **Extensión a horas cátedra del Nivel Secundario:** incorporar restricciones de compatibilidad horaria entre bloques y tiempos de traslado entre establecimientos dentro de un mismo turno.

---

## 8. CONCLUSIONES

1. Se formuló un modelo integral de colas y simulación de eventos discretos adaptado a la operatoria real de las asambleas de designación docente regidas por la Junta Calificadora de Méritos y Disciplina de Salta, capturando explícitamente las propiedades que invalidan las fórmulas analíticas estacionarias clásicas: población finita presente al inicio, horizonte cerrado de jornada única, prioridad no apropiativa por mérito, truncamiento de servicio en ventana $\tau$ y realimentación mediante cola secundaria de reintentos.
2. Se demostró conceptualmente que, bajo vigencia estricta del orden de mérito legal (Ley N.° 6.830 y Resolución Ministerial N.° 1.851/08), la regla de adjudicación secuencial equivale a una dictadura serial eficiente y libre de reclamos de prioridad, por lo que la mejora operativa genuina no reside en alterar externamente quién recibe cada cargo, sino en acotar los bloqueos extremos (E2) y reducir el tiempo de deliberación mediante información anticipada y recomendaciones filtradas en tiempo real (E3).
3. Se diseñó una arquitectura reproducible en Python que articula datos geográficos reales de establecimientos de Salta Capital con generación sintética controlada de aspirantes, verificable frente a modelos analíticos exactos de teoría de colas ($M/M/1$ y $M/M/c$) y auditable en su componente de recomendación mediante validación sobre preferencias ocultas.
4. *[PENDIENTE CORRIDA 07/11: incorporar dos puntos finales con las conclusiones cuantitativas sobre (a) la reducción de Wq y T_total lograda por E2 y E3 frente a E1 y (b) el valor recomendado de τ y c para la Junta Calificadora según el análisis de sensibilidad]*.

---

## 9. REFERENCIAS BIBLIOGRÁFICAS

* Abdulkadiroğlu, A., y Sönmez, T. (1998). Random serial dictatorship and the core from random endowments in house allocation problems. *Econometrica*, 66(3), 689–701. https://doi.org/10.2307/2998580
* Banks, J., Carson, J. S., II, Nelson, B. L., y Nicol, D. M. (2010). *Discrete-Event System Simulation* (5.ª ed.). Pearson.
* Cobham, A. (1954). Priority assignment in waiting line problems. *Journal of the Operations Research Society of America*, 2(1), 70–76. https://doi.org/10.1287/opre.2.1.70
* Combe, J., Tercieux, O., y Terrier, C. (2022). The design of teacher assignment: Theory and evidence. *The Review of Economic Studies*, 89(6), 3154–3222. https://doi.org/10.1093/restud/rdac006
* Gobierno de la Provincia de Salta (1995). *Ley Provincial N.° 6.830: Estatuto del Educador* (y modificatorias Leyes N.° 7.189 y N.° 8.325). Boletín Oficial de la Provincia de Salta. https://www.edusalta.gov.ar
* Hillier, F. S., y Lieberman, G. J. (2015). *Introducción a la investigación de operaciones* (10.ª ed.). McGraw-Hill Education.
* Instituto Nacional de Estadística y Censos [INDEC] (2023). *Censo Nacional de Población, Hogares y Viviendas 2022: Resultados definitivos*. República Argentina. https://censo.gob.ar
* Kendall, D. G. (1953). Stochastic processes occurring in the theory of queues and their analysis by the method of the imbedded Markov chain. *The Annals of Mathematical Statistics*, 24(3), 338–354. https://doi.org/10.1214/aoms/1177728975
* Law, A. M. (1980). Statistical analysis of the output data from terminating simulations. *Naval Research Logistics Quarterly*, 27(1), 131–143. https://doi.org/10.1002/nav.3800270113
* Law, A. M. (2015). *Simulation Modeling and Analysis* (5.ª ed.). McGraw-Hill Education.
* Little, J. D. C. (1961). A proof for the queuing formula: L = λW. *Operations Research*, 9(3), 383–387. https://doi.org/10.1287/opre.9.3.383
* Ministerio de Educación de la Provincia de Salta (2008). *Resolución Ministerial N.° 1.851/08: Régimen de Valoración de Antecedentes para la Carrera Docente*. Portal oficial *Edusalta*. https://www.edusalta.gov.ar
* Ministerio de Educación, Cultura, Ciencia y Tecnología de la Provincia de Salta [MECCyT] (2024). *Información Estadística Educativa y Padrón Oficial de Establecimientos Educativos (Relevamiento Anual)*. Secretaría de Planeamiento Educativo y Desarrollo Profesional Docente, *Edusalta*. https://www.edusalta.gov.ar
* Ricci, F., Rokach, L., y Shapira, B. (Eds.) (2015). *Recommender Systems Handbook* (2.ª ed.). Springer. https://doi.org/10.1007/978-1-4899-7637-6
* Rivadera, G. R. (2026a). *Teoría de Colas (Primera Parte): Introducción – Procesos de Nacimiento y Muerte* [Material de cátedra]. Investigación Operativa II, Facultad de Ingeniería, Universidad Católica de Salta (UCASAL).
* Rivadera, G. R. (2026b). *Teoría de Colas (Segunda Parte): Notación y modelos de un servidor* [Material de cátedra]. Investigación Operativa II, Facultad de Ingeniería, Universidad Católica de Salta (UCASAL).
* Rivadera, G. R. (2026c). *Teoría de Colas (Tercera Parte): Notación y modelos de múltiples servidores* [Material de cátedra]. Investigación Operativa II, Facultad de Ingeniería, Universidad Católica de Salta (UCASAL).
* Taha, H. A. (2017). *Investigación de operaciones* (10.ª ed.). Pearson Educación.
