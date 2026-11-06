# Resumen de clase: Investigación Operativa 2 (2026)
**Temas:** Consigna del trabajo final · Panorama de la asignatura · Introducción a las metaheurísticas (TSP y algoritmo genético)

> **Criterios aplicados a este resumen**
> - **Orden:** cronológico, según se dieron los temas en la clase.
> - **Libertad de completado: moderada.** Se corrigieron errores evidentes de dictado y de tipeo (términos técnicos). No se agregó contenido que no estuviera dicho o insinuado en la clase. Los términos corregidos están listados al final.
> - **Tono:** las opiniones, anécdotas y recomendaciones del profesor se presentan en recuadros **📝 Nota del profesor/a**, en registro académico neutro.
> - **Ejemplos:** donde la clase dio un ejemplo, se usa ese. Donde no lo hubo, se agrega un ejemplo breve marcado como *(ejemplo ilustrativo, no dicho en clase)*.

---

## 1. Aspectos administrativos y de calendario

### 1.1. Contexto de la evaluación
- Existe un **trabajo final** que también sirve para **mejorar la nota del parcial**.
- Las **notas del parcial** se entregan **la semana siguiente** a esta clase.
- Si el promedio entre parcial y trabajo final no alcanza el **promedio de aprobación**, habrá una instancia de **recuperatorio**. Por eso el trabajo final se entrega con anticipación a la fecha de cierre de regularidades.

### 1.2. Fechas mencionadas

| Hecho | Fecha / plazo dicho en clase |
|---|---|
| Plazo estimado para hacer el trabajo | Entre 10 y 15 días, según la fecha de entrega de regularidades |
| Fecha cargada en la plataforma | Alrededor del **10 de noviembre** (modificable) |
| Fecha límite probable | Hasta el **15 de noviembre** |
| Entrega de regularidades | Entre el **15 y el 20 de noviembre** |
| Entrega de notas del parcial | La semana siguiente a la clase |
| Próxima clase | "El otro jueves" (se continúa con metaheurísticas) |

Si hay mucha gente atrasada, se podrían dar unos días más.

### 1.3. Pasos inmediatos a seguir
1. Ingresar al **enlace a la planilla** compartida (publicada en la plataforma, en la sección *"Trabajo final de Investigación Operativa 2, 2026"*).
2. Cargar el **número de grupo** y sus integrantes. La planilla se edita en forma simultánea, por lo que conviene coordinarse para no pisarse.
3. Completar las demás columnas de la propuesta inicial (ver sección 3.5).

> **📝 Nota del profesor/a**
> El profesor indicó que, en general, el desempeño en los parciales es bueno, aunque algunas personas deberían hacer un esfuerzo adicional en el trabajo final.

---

## 2. Panorama de la asignatura (programa 2026)

El programa tiene **5 unidades**. Estado al día de la clase:

| Unidades | Estado |
|---|---|
| Primeras 3 (incluye Teoría de Colas) | Vistas completamente |
| Pronósticos | **No vista** todavía |
| Metaheurísticas | **No vista**; se inicia en esta clase |

### 2.1. Teoría de colas: estado y alcance
- Falta ver un par de modelos, pero la parte teórica **está prácticamente agotada**.
- Los modelos de colas se justifican a partir de la **transición desde las cadenas de Markov** hacia los modelos de colas (explicación dada la clase anterior).
- Los modelos más complejos (p. ej. el **modelo de servicio de máquinas** o un **modelo muy general** presente en el libro de Taha y otros textos) siguen siendo **fórmulas para calcular las mismas medidas** ya vistas:
  - **Longitud de cola**
  - **Clientes en el sistema**
  - **Tiempo de espera en cola**
  - **Tiempo de espera en el sistema**
- Lo que resta es **hacer los ejercicios del trabajo práctico**.
- El aspecto más interesante que se destacó son las **limitaciones de estos modelos**.

> **📝 Nota del profesor/a**
> El profesor consideró que la explicación de cómo se llega a los modelos generales y al de servicio de máquinas es similar y poco atractiva. Anunció que, con el tiempo restante, se seguirán viendo contenidos, incluido pronósticos, que considera una unidad importante por su vínculo con el análisis de datos.

---

## 3. El trabajo final

### 3.1. Formato general
- Se puede hacer **de forma individual o en grupo de hasta 3 personas**.
- Se desarrolla a partir de **una o más unidades** de la parte final de la materia: **Teoría de colas, Pronósticos o Metaheurísticas** (también se pueden **combinar**).
- Hay **dos modalidades**, elegibles según preferencia (programar o investigar y escribir).

### 3.2. Modalidades

| | **Aplicación práctica** | **Monografía de investigación** |
|---|---|---|
| **Qué es** | Uso de una aplicación basada en uno o más modelos de Investigación Operativa para resolver un **problema concreto**. | Escrito que consiste en **revisión bibliográfica, análisis crítico, comparación de enfoques**, con algunos ejemplos o experimentos computacionales. |
| **Se construye un modelo** | **Sí** | **No**; se escribe sobre investigación ya existente en el campo. |
| **Implementación computacional** | **Obligatoria** (por ser práctica) | **Opcional**, sin necesidad de gran extensión. |
| **Componente propio** | Estado del arte reducido | **Estado del arte** más desarrollado y **análisis crítico** |
| **Ejemplo dado en clase** | Estudio de colas en una **estación de servicio con dos surtidores**: se arma el modelo, se sacan conclusiones y se implementa, por ejemplo, en un **notebook de Python** basado en el que mostró el profesor. | Reseña de lo investigado sobre un tema de las tres unidades. |

La profundidad de la aplicación práctica depende de **los datos disponibles y del tiempo**.

> **📝 Nota del profesor/a**
> El profesor aplica este esquema de dos modalidades en casi todas sus asignaturas porque da más versatilidad y flexibilidad. Hay personas a quienes les gusta programar o generar modelos en código y otras que prefieren investigar y escribir una monografía.

### 3.3. Sugerencias de temas por unidad

#### Teoría de colas
- Proceso de Poisson, cadenas de Markov y temas ya vistos.
- **Dimensionamiento de servidores:** variar la cantidad de servidores para encontrar la mejor. Puede hacerse de forma **automática** (el programa va cambiando la cantidad y se queda con la mejor).
  - Hay que considerar el **costo**: agregar un servidor mejora el sistema pero tiene un costo. En clase se vio poco costeo.
- Aplicaciones: servicios en la nube, centros de cómputo, etc.
- *Ejemplo dado en clase:* un servidor en la nube con *n* clientes, que puede atender, por ejemplo, **tres clientes por unidad de tiempo**. El esquema puede ser muy sencillo.
- Se pueden buscar ejemplos en la web para guiarse.

#### Pronósticos
- Tiene gran solapamiento con **machine learning** y muchos algoritmos para analizar **series temporales**.
- Técnicas sencillas: **promedio móvil, promedio ponderado, suavizado exponencial**. También hay técnicas más complejas que los libros de Investigación Operativa suelen no cubrir, pero que se pueden investigar.
- Aplicaciones: **demanda general, consumo energético**, y cualquier serie de tiempo (p. ej. el **valor del dólar**).
- *Ejemplo dado en clase:* una tesis del año anterior, dirigida por el profesor, que pronosticaba el **valor futuro del dólar** con un algoritmo de machine learning aplicado a la serie histórica. Comparaba una **red neuronal** con otros modelos como **árboles de decisión**.

#### Metaheurísticas
- Existen muchísimos algoritmos; cada uno es "un mundo en sí mismo", aunque hay **familias** que usan técnicas parecidas.
- Los **algoritmos genéticos** se usan mucho actualmente, incluso combinados con redes neuronales.
- Aplicaciones posibles: **scheduling, asignación de recursos, planificación y distribución, optimización de redes, ubicación de instalaciones, ruteo**.
- Caso destacado: **ruteo / agente viajero** (ver sección 5).
- Ejemplos de algoritmos mencionados: **colonia de hormigas** (*Ant Colony Optimization*, metaheurística probabilística de inteligencia de enjambre), **colonia de abejas** (*Bee Colony*), **algoritmos genéticos**, **búsqueda tabú**, **recocido simulado**.
- Las redes neuronales también se catalogan como metaheurísticas.
- *Ejemplo de tesis dado en clase:* una tesis donde se hacía un tipo de **ruteo** aplicando un algoritmo metaheurístico.

#### Trabajos integrados
- Se pueden **mezclar dos técnicas**; no es obligatorio.
- *Ejemplo dado en clase:* usar **metaheurísticas para hacer pronósticos**.

> **📝 Nota del profesor/a**
> El profesor manifestó preferencia personal por las metaheurísticas, que le parecen "súper interesantes" y "divertidas". Sostuvo que pronósticos es más fácil de entender y que las metaheurísticas son algo más complejas. Aclaró que cualquiera de los tres temas es válido y que no hay inconveniente con la elección. Señaló además que este tipo de contenido difícilmente se vea de forma concreta en otras materias (en Sistemas Inteligentes se ven redes neuronales, pero esto es más amplio). Dijo que podría ir dando algunas pistas sobre metaheurísticas en las clases restantes.

### 3.4. Estructura sugerida del informe
La estructura es **parecida a la de una tesis** (orientativa; no tiene que ser exactamente igual).

| Sección | Aplicación práctica | Monografía |
|---|---|---|
| Planteo del problema / tema | Sí | Sí |
| Modelo conceptual | Sí | — |
| **Implementación computacional** | **Sí** (obligatoria) | Opcional |
| **Estado del arte** | Reducido | **Sí**, más desarrollado |
| **Análisis crítico** | — | **Sí** |
| Conclusiones | Sí | Sí |

- **Longitud:** orientativa; la cantidad de páginas no tiene que ser exacta.
- **Bibliografía:** debe ser **accesible** (que el profesor pueda verificarla) y con **sustento** (paper u otra fuente respaldatoria).
- **Presentación oral:** sólo si alcanza el tiempo (se estaba terminando el cuatrimestre). Podría haber una clase de presentación de grupos con preguntas.

### 3.5. Propuesta inicial (columnas de la planilla)
La planilla pide, entre otras cosas:
1. **Número de grupo** e integrantes
2. **Título provisorio**
3. **Modalidad:** aplicación práctica o monografía
4. **Unidades:** se puede marcar **una o varias** (por ejemplo Colas + Metaheurísticas)
5. **Problema o tema** (el significado de cada columna está explicado en la consigna)

No es necesario tener todo claro de entrada, pero cuanto antes se defina, mejor.

### 3.6. Uso de inteligencia artificial
**Está permitido.** Condiciones y recomendaciones dadas:
- Es útil para **buscar ideas iniciales** rápidamente, **delegar programación**, **revisar redacción** o evaluar qué está bien y qué mal.
- Hay que **revisar todo** lo generado.
- Debe haber **la mayor cantidad posible de aporte propio** y **originalidad**.
- **No se aceptan contenidos cuya autoría y validez los integrantes no puedan explicar** durante una posible defensa o en preguntas por mail.
- Si el trabajo es **demasiado evidentemente generado por IA, se nota**.

### 3.7. Vínculo con el examen final
- El examen final es **escrito**.
- El profesor puede **hacer preguntas puntuales sobre el trabajo final** en la instancia de examen, o consultar por mail si tiene dudas sobre algún trabajo.

---

## 4. Metaheurísticas: panorama general

### 4.1. Punto de partida: tipos de solución
Al optimizar un problema (visto en Investigación Operativa 1 con el **método simplex**) existen:
- **Soluciones factibles:** cumplen las restricciones, pero **no son óptimas**.
- **Solución óptima:** la mejor posible, que es lo que normalmente se busca.

### 4.2. Cuándo no sirve buscar el óptimo exacto
- Para muchos problemas **existe un algoritmo que da la solución óptima**.
- Pero cuando el problema es **muy complejo y con una cantidad muy grande de datos**, esos algoritmos se vuelven **imprácticos por el tiempo de espera** (tema de la **teoría de la complejidad computacional**).
- En ese caso se recurre a **algoritmos aproximados**: no se busca la solución exacta, sino **una solución buena**.
- Una solución es "buena" porque es **la mejor de un conjunto de soluciones exploradas** por uno o varios algoritmos. Puede que coincida con la óptima o no.

*Ejemplo ilustrativo, no dicho en clase:* si un algoritmo exacto tarda años en un mapa grande y uno aproximado entrega en segundos una ruta un poco más larga que la óptima, la ruta aproximada suele ser la única utilizable en la práctica.

### 4.3. Definiciones clave

| Concepto | Definición según la clase |
|---|---|
| **Heurística** | Usa **información adicional disponible en cada paso** del algoritmo para mejorar la solución. |
| **Metaheurística** | En general **no usa esa información**; es una **exploración con alguna técnica** que va **descartando soluciones peores** que otras ya encontradas. Se la describe como una receta general. |
| **Característica de las metaheurísticas** | Son **aproximaciones robustas que no garantizan el óptimo**, pero **escapan de los óptimos locales** (soluciones que no son las mejores globalmente). |

Según el profesor, esa es **"la única diferencia"** entre heurística y metaheurística.

---

## 5. El problema del agente viajero (TSP)

### 5.1. Enunciado
**Problema del agente viajero** (en inglés *Traveling Salesman Problem*, TSP): encontrar la **ruta más corta posible** que **visite cada ciudad de un conjunto exactamente una vez y regrese a la ciudad de origen**.

- Es un **problema combinatorio**: para asegurar que una ruta es la más corta hay que **explorar todas las combinaciones**.
- Es un **ciclo** (se vuelve al origen), no un tramo de grafo. Matemáticamente corresponde a un **camino/ciclo hamiltoniano** y **no es tan fácil como la ruta más corta** entre dos puntos (algoritmos exactos vistos en la parte de grafos).

*Ejemplo ilustrativo, no dicho en clase:* un repartidor que debe pasar por 5 ciudades, partir de una y volver a ella, buscando el menor recorrido total.

### 5.2. Por qué se complica
- Al **agregar ciudades** la cantidad de combinaciones **crece mucho**.
- Para **4 a ~50 ciudades** el problema es **tratable** de forma exacta; con más, el tiempo se vuelve excesivo y probablemente el algoritmo no termine.
- **Programación lineal:** se puede plantear con variables por ciudad, pero la **matriz resultante es enorme**. Con 100 ciudades, es una matriz de 100 × 100, "una barbaridad". Por eso no es buena idea.

### 5.3. Algoritmos exactos
- El TSP exacto **no se resuelve con simplex** (el profesor se corrigió en clase): se plantea como **programación lineal entera**, que es distinta de la lineal continua vista en IO1 y **no se vio** en la materia.
- Algoritmos mencionados:
  - **Branch and Bound (B&B)**: algoritmo en forma de **árbol** que va **descartando soluciones peores**.
  - **Plano de corte** (derivado de B&B, muy parecido).
- Ambos son **tremendamente lentos**: para el TSP con muchos datos pueden demorar **miles de años**.

### 5.4. Referencia bibliográfica
- **Libro de Taha, 10.ª edición:** tiene **un capítulo dedicado exclusivamente al TSP**, con algoritmos exactos, heurísticas y metaheurísticas.
  - Explica **tres metaheurísticas**: **búsqueda tabú** (bastante sencilla), **recocido simulado** (*simulated annealing*) y **algoritmo genético**.
  - Taja también tiene **otro capítulo sobre programación heurística**, con explicación general y aplicación al TSP.
- Se sugiere basar un trabajo en el TSP apoyándose en ese capítulo.
- Papers: se pueden encontrar en **arXiv** y **ResearchGate**; algunos sitios, como **Springer Link**, son pagos.

> **📝 Nota del profesor/a**
> El profesor comentó que posee el libro de Taha en papel y en PDF. Mencionó que ediciones anteriores incluían un capítulo de pronósticos, ausente en esta edición, y que algunos capítulos estaban en línea (en inglés). No se confirmó con certeza (ver sección de ambigüedades).

### 5.5. Metaheurísticas que inspiran su diseño en la naturaleza
- Muchas metaheurísticas **copian procesos del mundo natural** y construyen un **modelo matemático** de ellos.
- **Recocido simulado:** su nombre extraño proviene de la **siderurgia/física** (tratamiento térmico de metales).
- **Colonia de hormigas / abejas:** se basan en la **búsqueda de comida** de esos insectos.
- **Algoritmo genético:** imita la **selección natural**.
- *Ejemplo dado en clase:* en la naturaleza hay problemas que se resuelven de forma "intuitiva" pero con cierto grado de optimalidad (búsqueda de alimento de las abejas).

---

## 6. Diseño y estructura de una metaheurística

### 6.1. Estrategias de construcción
Se mencionaron diversas estrategias en una diapositiva:
- **Construcción:** greedy, aleatoria, GRASP, entre otras.
- **Perturbación:** modificar al azar una solución para ver si mejora.

Diferencia general:
- Unas **construyen una solución paso a paso**.
- Otras la obtienen aplicando **técnicas de perturbación**: una **modificación aleatoria** de algo que representa una solución, para ver si ese cambio la mejora. Esto es común en los **algoritmos genéticos**.

### 6.2. Los tres elementos principales al aplicar una metaheurística
Se dijo que estos algoritmos son **"recetas"**; salvo que se investigue algo muy puntual, lo habitual es **usar un algoritmo ya hecho** (hormigas, genético, recocido simulado, etc.). Pero al aplicarlo hay que considerar:

| # | Elemento | Explicación | Ejemplo |
|---|---|---|---|
| 1 | **Codificación de la información** | Representar el espacio del problema en la forma que **requiere el algoritmo**. | En el TSP con un algoritmo genético hay que decidir cómo representar las ciudades y las rutas como un "gen". |
| 2 | **Función objetivo** | Medida para evaluar qué tan buena es una solución. A veces es clara y a veces no. | En el TSP: la **distancia total** del recorrido (menor es mejor). |
| 3 | **Manejo de restricciones** | Algunos algoritmos **eliminan o penalizan soluciones** para que no se reingrese a zonas del espacio ya exploradas, volviendo más eficiente la búsqueda. | Se ve mucho en la **búsqueda tabú**. |

> **📝 Nota del profesor/a**
> El profesor considera que la **codificación** es el paso **más complicado** de estos algoritmos.

### 6.3. Equilibrio entre diversificación y explotación
- **Diversificación:** explorar soluciones posibles en distintas zonas del espacio.
- **Explotación:** cuando se encuentra una solución prometedora o mucho mejor que otras, se buscan soluciones **muy cercanas a ella**.
- *Ejemplo dado en clase:* en el algoritmo genético se termina buscando soluciones cerca de los valores 7,35 o 7,25 (ver sección 7.4).

### 6.4. Clasificación de las metaheurísticas

```
Metaheurísticas
├── Metaheurísticas S  (trayectoria única)
│     Se trabaja UNA misma solución para transformarla en una mejor.
└── Metaheurísticas P  (basadas en poblaciones)
      Se parte de MUCHAS soluciones a la vez.
      ├── Algoritmos evolutivos
      │     ├── Algoritmos genéticos (muy puntuales)
      │     └── Estrategias de evolución (reglas más generales)
      └── Inteligencia de enjambre (Swarm Intelligence)
            └── Hormigas, partículas, abejas
```

| Tipo | Características |
|---|---|
| **S (trayectoria única)** | Una sola solución que se va modificando para llegar a una mejor. |
| **P (poblacional)** | Un universo de soluciones. En un algoritmo genético hay **al menos dos soluciones** (los dos padres iniciales); podría haber más. |

---

## 7. Algoritmo genético aplicado al TSP (ejemplo de Taha)

El profesor usó el ejemplo de Taha para mostrar cómo funciona un algoritmo genético. Se verá en detalle con un notebook en la clase siguiente.

### 7.1. Idea general
- Imita la **selección natural**: se **cruzan individuos** durante muchas generaciones y, supuestamente, **quedan los más aptos**.
- Parece "una gran timba" porque introduce **aleatoriedad**, pero es una búsqueda guiada por la evaluación de la función objetivo.
- Es **iterativo**: en cada iteración se obtienen nuevos hijos y se evalúa cuál es mejor.

### 7.2. Etapas del algoritmo

| Etapa | Qué se hace |
|---|---|
| **1. Codificación de genes** | Se representa cada solución como un "gen". Puede ser **binaria** o **numérica**, según la bibliografía y el gusto. |
| **2. Población inicial** | Se generan soluciones iniciales. En Taha, se construye un recorrido **agregando de a un nodo no redundante** a la derecha a partir del nodo origen. |
| **3. Cruzamiento (crossover)** | De **dos padres** se obtienen **dos hijos** mediante **intercambio de genes**. Hay muchas formas de hacerlo. |
| **4. Mutación** | Con una **pequeña probabilidad** se modifica un hijo (en el TSP, **intercambiando dos ciudades de posición**). |
| **5. Evaluación** | Se calcula la **función objetivo** (distancia total) y se elige la mejor solución. |
| **6. Iteración** | Se repite el proceso varias veces. |

### 7.3. Codificación en el TSP
- **Taha** usa un **código de recorrido numérico directo**: cada ciudad tiene un número y la solución es la secuencia.
  - *Ejemplo dado en clase:* con 5 ciudades, una solución es **2, 5, 4, 3, 1**.
- **Codificación posicional (alternativa mencionada):** un **vector binario** con un 1 en las ciudades que forman parte de la ruta.
  - *Ejemplo dado en clase:* con 20 ciudades, de las cuales se visitan 10, el vector tiene 20 posiciones y 10 unos.
- En la codificación numérica **la longitud del gen no es fija**: puede haber representaciones más largas que otras (la longitud en la representación no equivale a la distancia recorrida).
- En el TSP, la codificación es directa porque el gen **es** el camino, por lo que no requiere mucho trabajo adicional.

### 7.4. Cruzamiento: paso a paso (ejemplo de Taha)
Ejemplo con **7 ciudades**:
1. Se tienen dos padres, **P1** y **P2**, cada uno una solución (recorrido que regresa al nodo de origen).
2. Se eligen **al azar dos puntos de cruce, C1 y C2, con C1 < C2**.
3. Se generan dos números aleatorios (R1 y R2) que se **transforman en valores enteros** (en el ejemplo, **3 y 5**).
4. Se **intercambian los segmentos** entre esas posiciones de P1 y P2, y se obtienen **dos hijos nuevos**.
5. Se continúa aplicando el algoritmo (mutación y evaluación).

> **Observación del profesor:** en el ejemplo, P2 termina en el nodo 5 y no contiene el 5 donde debería, por lo que **no sería estrictamente una solución válida**, "pero igual se cruza" a modo de ilustración.

### 7.5. Mutación
- Consiste en **mutar los genes del hijo** con una **pequeña probabilidad**.
- En el TSP, la mutación es el **intercambio de dos ciudades de posición**.
- Hace uso de la **aleatoriedad / probabilidad**.

### 7.6. Función objetivo y resultado del ejemplo
- En el TSP: **minimizar la distancia total del recorrido**.

**Expresión formal** *(escrita aquí para ordenar lo dicho verbalmente en clase; la clase no mostró una fórmula escrita)*:

$$\min Z = \sum_{i=1}^{n-1} d(c_i, c_{i+1}) + d(c_n, c_1)$$

| Elemento | Significado |
|---|---|
| **Z** | Distancia total del recorrido (función objetivo a minimizar). |
| **n** | Cantidad de ciudades. |
| **cᵢ** | Ciudad en la posición *i* del recorrido (el gen). |
| **d(cᵢ, cⱼ)** | Distancia entre dos ciudades. |
| **d(cₙ, c₁)** | Tramo de regreso a la ciudad de origen (cierra el ciclo). |

**Evolución de los hijos en las iteraciones del ejemplo** (valores citados en clase):

| Iteración | Valores de los hijos | Lectura |
|---|---|---|
| 1.ª | 7,50 y 8,10 | Se queda con el menor. |
| 2.ª | 7,35 y 8,25 | Mejora respecto de la primera. |
| 3.ª | 7,25 y 7,35 | Ambos buenos; los valores se repiten. |

Como se repiten **7,35 y 7,25**, se concluye que la distancia menor está **entre esos dos**. Eso ilustra la **explotación** (búsqueda cerca de las mejores soluciones).

### 7.7. Comparación con la solución exacta (según el ejemplo de Taha)

| Método | Solución en el ejemplo |
|---|---|
| **Algoritmo exacto** (modelado en MPL) | **1, 2, 3, 4, 1** (solución óptima) |
| **Algoritmo genético** | **1, 5, 3, 2, 4, 1** |

El profesor señaló que son **parecidas, con una pequeña diferencia**, y recalcó que estas son **soluciones aproximadas**: pueden o no alcanzar el óptimo. Taha usa el **mismo ejemplo** para comparar todos los enfoques. También mencionó que hay una **versión en Excel** del ejemplo, donde se puede ver cómo cambian los valores.

---

## 8. Cierre de la clase
- Se propuso retomar la próxima clase con **algún algoritmo puntual** o con los que queden, y mostrar un **notebook** de los tres algoritmos de Taha (**tabú, recocido simulado, genético**), si hay tiempo.
- Se compartirán las **presentaciones de metaheurísticas** (hay dos versiones) y cada persona podrá elegir cuál prefiere. Ambas explican contenidos similares, y hay **bibliografía libre** sobre el tema.

> **📝 Nota del profesor/a**
> El profesor comentó que ninguna de las dos presentaciones lo convence del todo y que más adelante hará una mezcla. Recordó que cualquiera de los tres temas (colas, pronósticos, metaheurísticas) es válido, aunque la metaheurística es la que más le gusta.

---

## 9. Puntos incompletos, ambiguos o corregidos por mí

### 9.1. Términos corregidos por errores evidentes de dictado (libertad moderada)

| En la transcripción | Interpretado como |
|---|---|
| "meteorísticas", "metabólicas", "meta heurísticas" | **Metaheurísticas** |
| "TCP" (en el contexto del agente viajero) | **TSP** (*Traveling Salesman Problem*) |
| "Taja" | **Taha** (autor de *Investigación de operaciones*) |
| "Sun Intelligence", "SWAMP" | ***Swarm Intelligence*** (inteligencia de enjambre) |
| "mi colonia optimization" | **Bee colony optimization** (colonia de abejas); la transcripción está distorsionada, pero el contexto indica abejas |
| "recocido simulado" / "simulatidad y annealing" | ***Simulated annealing*** |
| "branch and bone" | ***Branch and bound*** |
| "plano constante" | Probablemente **plano de corte** (*cutting plane*) |
| "Nodule de Python" / "nodo" | **Notebook** de Python |
| "metabólicas S y P" | **Metaheurísticas S y P** (trayectoria única y poblacionales) |
| "Polines Kirisek" (modelo muy general en el libro) | Posiblemente **Pollaczek–Khinchine**; no se pudo confirmar, la transcripción es poco clara |

### 9.2. Vacíos y ambigüedades del material
1. **"Fenómeno de Tanninin":** la expresión no es interpretable en la transcripción. Se interpretó, por el contexto, como una referencia a las metaheurísticas del capítulo de Taha (tabú o recocido simulado), pero **no se confirmó**.
2. **Estrategias de construcción:** de la lista dicha (greedy, aleatoria, GRASP, "BNS", "GBASE", perturbación) sólo se pudo interpretar con seguridad **greedy, aleatoria, GRASP y perturbación**. "BNS" y "GBASE" **no son interpretables** y no se explicaron.
3. **Los "dos equilibrios":** el profesor dijo que hay "dos equilibrios" y sólo desarrolló **diversificación** y **explotación**, que es el equilibrio entre ambos. No quedó claro si había un segundo equilibrio distinto.
4. **Transformación aleatoria en el cruzamiento:** el profesor mencionó que R1 y R2 se transforman "mediante esta transformación" en enteros (3 y 5), pero **la fórmula no se dictó ni se explicó**. Tampoco se aclaró bien el origen de los valores previos (44 y 72) que aparecen en la transcripción.
5. **Ejemplo de cruzamiento con padre inválido:** P2 no es una solución válida del TSP; el profesor lo reconoció. Falta saber cómo se corrige o repara esto en el algoritmo real (no se explicó).
6. **Comparación exacto vs. genético:** el óptimo es **1,2,3,4,1** (4 ciudades) mientras que el genético es **1,5,3,2,4,1** (5 ciudades). Esto sugiere que son **instancias o pasos distintos del ejemplo**, o un error al leerlas. No quedó aclarado.
7. **Unidad de los valores 7,25 / 7,35 / 7,50 / 8,10 / 8,25:** no se dijo la unidad de medida. Además, la iteración 3 no se leyó completamente.
8. **Diferencia heurística vs. metaheurística:** el profesor la presentó como una diferencia simple (uso o no de información adicional). Esto es una simplificación suya; no se desarrolló formalmente.
9. **Capítulo de pronósticos en Taha:** el profesor no estaba seguro de si la edición tenía capítulos en línea o de si se había eliminado el de pronósticos. **No confirmado.**
10. **Contradicción menor sobre las unidades vistas:** el profesor dijo que las unidades "pronóstico" y "metaheurísticas" no se habían visto, pero también que se verían sólo parcialmente "en lo que queda". No está claro cuánto contenido real se dará de pronósticos.
11. **Fecha de entrega del trabajo final:** hay **dos fechas** (10 de noviembre en la plataforma, 15 de noviembre como límite probable). **No está definida la fecha final.**
12. **Presentación oral:** no está confirmado que se realice.
13. **Modelos de colas pendientes:** el profesor dijo que faltan "un par de modelos" pero **no se dijo cuáles**.
14. **Costeo en teoría de colas:** se mencionó como factor importante, pero no se dieron fórmulas ni método.
15. **Algoritmo tabú y recocido simulado:** se nombraron, pero **no se explicaron**; sólo se dijo que el tabú limpia o penaliza soluciones. Se prometió un notebook para la próxima clase.

### 9.3. Contenido completado por mí
- La **expresión formal de la función objetivo** (sección 7.6) fue escrita por mí a partir de la descripción verbal ("suma de la distancia de todas las ciudades"). No estaba escrita en la clase.
- La etiqueta *(ejemplo ilustrativo)* indica los ejemplos que agregué yo y no se dijeron en clase.
