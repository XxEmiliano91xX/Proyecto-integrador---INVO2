UNIVERSIDAD CATÓLICA DE SALTA

Facultad de Ingeniería · Ingeniería en Informática

TRABAJO FINAL INTEGRADOR
Investigación Operativa II

Carrera
Modalidad
Integrantes

Ingeniería en Informática
Individual o grupal
Máximo 3 estudiantes por grupo

1. Propósito del trabajo

El Trabajo Final Integrador tiene como objetivo que los estudiantes profundicen, apliquen e
integren los conceptos, modelos, algoritmos y herramientas desarrollados en la asignatura
a partir de la Unidad de Teoría de Colas.

El trabajo podrá desarrollarse bajo una de las siguientes modalidades:

Modalidad A – Aplicación práctica

Desarrollo de una aplicación basada en uno o más modelos de Investigación Operativa
para analizar y resolver un problema concreto.

Modalidad B – Monografía de investigación

Estudio sistemático y fundamentado de un tema relacionado con los contenidos de la
asignatura, incluyendo revisión bibliográfica, análisis crítico, comparación de enfoques y,
cuando resulte pertinente, ejemplos o experimentos computacionales.

En ambas modalidades deberá existir una relación explícita con al menos uno de los
contenidos:

• Teoría de Colas.

• Pronósticos.

• Metaheurísticas.

También podrán desarrollarse trabajos que integren contenidos de diferentes unidades.

Investigación Operativa II · Trabajo Final Integrador · 2026

2. Áreas temáticas

2.1. Teoría de Colas

• Procesos de Poisson.

• Distribución exponencial.

• Procesos nacimiento–muerte.

• Cadenas de Markov aplicadas a sistemas de espera.

• Probabilidades de estado estacionario.

• Ley de Little.

• Medidas de desempeño: L, Lq, W, Wq, utilización, probabilidad de espera y probabilidad

de bloqueo.

• Modelo M/M/1.

• Modelos M/M/c.

• Sistemas con capacidad finita.

• Sistemas con población finita.

• Modelo de reparación o servicio a máquinas.

• Redes de colas.

• Comparación entre soluciones analíticas y simulación.

• Dimensionamiento de servidores.

• Análisis de capacidad.

• Aplicaciones a sistemas informáticos y de comunicaciones.

Posibles campos de aplicación

• Servidores web, servicios cloud y centros de cómputos.

• Routers, redes y sistemas de comunicaciones.

• Procesamiento de trabajos y sistemas informáticos.

• Atención bancaria, hospitales y call centers.

• Logística, líneas de producción y transporte.

• Sistemas de reparación y servicios públicos.

2.2. Pronósticos

• Promedio móvil.

• Promedio móvil ponderado.

• Suavización exponencial.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Regresión.

• Análisis de series temporales.

• Selección de parámetros.

• Medición del error de pronóstico.

• Comparación de métodos.

• Validación con datos históricos.

• Utilización del pronóstico en procesos de decisión.

Podrán utilizarse, entre otras, las siguientes medidas de error:

𝑀𝐴𝐸,   𝑀𝑆𝐸,   𝑅𝑀𝑆𝐸,   𝑀𝐴𝑃𝐸

Posibles aplicaciones

• Demanda de productos y ventas.

• Cantidad de usuarios de un sistema.

• Tráfico de red y uso de infraestructura informática.

• Consumo energético.

• Demanda hospitalaria e incidentes.

• Planificación de capacidad.

2.3. Metaheurísticas

• Búsqueda tabú.

• Templado simulado.

• Algoritmos genéticos.

• Comparación entre metaheurísticas.

• Diseño de funciones objetivo.

• Codificación de soluciones.

• Generación de vecindades.

• Mecanismos de exploración y explotación.

• Selección, cruce y mutación.

• Criterios de parada.

• Análisis de convergencia.

• Calibración de parámetros.

Problemas posibles

• Scheduling y asignación de recursos.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Ruteo y Traveling Salesman Problem.

• Planificación y distribución.

• Optimización de redes.

• Selección de configuraciones.

• Ubicación de instalaciones.

• Optimización de capacidad.

• Problemas combinatorios.

2.4. Trabajos integradores

Se valorarán especialmente propuestas que relacionen diferentes técnicas.

Pronóstico + Teoría de Colas

Pronosticar la demanda de un servicio y utilizar los resultados para dimensionar servidores.

Teoría de Colas + Metaheurísticas

Determinar mediante un algoritmo genético o templado simulado la configuración de
servidores que minimice:

𝐶𝑜𝑠𝑡𝑜 𝑡𝑜𝑡𝑎𝑙  =  𝐶𝑜𝑠𝑡𝑜 𝑑𝑒 𝑟𝑒𝑐𝑢𝑟𝑠𝑜𝑠  +  𝐶𝑜𝑠𝑡𝑜 𝑑𝑒 𝑒𝑠𝑝𝑒𝑟𝑎

Pronóstico + Metaheurísticas

Pronosticar demanda y posteriormente optimizar la asignación de recursos.

Colas + Simulación

Comparar las fórmulas analíticas de un modelo M/M/1 o M/M/c con los resultados
obtenidos mediante simulación.

3. Modalidad A – Aplicación práctica

El objetivo será formular, implementar y analizar un modelo aplicado a un problema
concreto.

3.1. Planteamiento del problema

Se deberá describir:

• Contexto.

• Problema.

• Sistema analizado.

• Objetivo.

• Restricciones.

• Variables.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Parámetros.

• Decisiones que se desean estudiar.

Deberá justificarse por qué la técnica seleccionada resulta adecuada.

3.2. Modelo conceptual y matemático

Deberá desarrollarse formalmente el modelo utilizado. Según la temática podrán incluirse:

• Estados y probabilidades.

• Tasas y distribuciones.

• Variables y parámetros.

• Restricciones y funciones objetivo.

• Ecuaciones y algoritmos.

Las expresiones utilizadas deberán ser explicadas y relacionadas con el problema
estudiado.

3.3. Datos
Deberá explicarse:

• Origen de los datos.

• Variables utilizadas.

• Proceso de limpieza.

• Supuestos.

• Transformaciones realizadas.

Los datos podrán ser reales, públicos, obtenidos de APIs, generados experimentalmente o
sintéticos.

Cuando se utilicen datos simulados deberá justificarse su generación.

El modelo deberá implementarse utilizando una herramienta apropiada. Preferentemente:

• Python.

• R.

• Jupyter Notebook / Google Colab.

• QTSPlus.

• Java Modeling Tools.

3.4. Implementación computacional

• Otras herramientas justificadas.

El código deberá ser legible y reproducible. Cuando corresponda deberá incluir funciones,
clases, parámetros, comentarios, visualizaciones y tablas de resultados.

Investigación Operativa II · Trabajo Final Integrador · 2026

3.5. Verificación y validación

Verificación

Comprobar que el algoritmo implementado representa correctamente el modelo formulado.

Validación

Comprobar que los resultados tienen sentido respecto del sistema estudiado.

Cuando exista una solución conocida o analítica se recomienda utilizarla como referencia.
Por ejemplo, una implementación de un M/M/1 puede compararse con:

𝐿  =

𝜌
1 − 𝜌

𝐿𝑞  =

𝜌²
1 − 𝜌

𝑊  =

𝑊𝑞  =

1
𝜇 − 𝜆
𝜌
𝜇 − 𝜆

3.6. Experimentación

El trabajo deberá incluir al menos tres escenarios o configuraciones diferentes.

• Diferentes tasas de llegada.

• Distinto número de servidores.

• Variación de capacidad.

• Diferentes parámetros de suavización.

• Distintos tamaños de ventana.

• Diferentes configuraciones de una metaheurística.

• Distintas políticas de asignación.

Los escenarios deberán ser comparados sistemáticamente.

3.7. Resultados

Los resultados deberán presentarse mediante:

• Tablas.

• Gráficos.

• Indicadores.

• Medidas de desempeño.

• Comparación de escenarios.

Investigación Operativa II · Trabajo Final Integrador · 2026

No será suficiente ejecutar el algoritmo. El grupo deberá interpretar los resultados y
explicar sus implicaciones para la toma de decisiones.

3.8. Conclusiones

Deberán responder a las preguntas planteadas inicialmente.

Cuando corresponda deberán formularse recomendaciones.

También deberán indicarse limitaciones, supuestos relevantes y posibles extensiones del
trabajo.

4. Modalidad B – Monografía de investigación

La monografía deberá estudiar en profundidad una problemática vinculada con Teoría de
Colas, Pronósticos, Metaheurísticas o la integración de estas técnicas.

No deberá limitarse a una compilación de definiciones. Se espera una revisión crítica y
comparativa.

4.1. Introducción

• Problemática.

• Motivación.

• Alcance.

• Objetivos.

• Preguntas de investigación.

4.2. Marco conceptual

Desarrollar los fundamentos matemáticos y computacionales necesarios.

Por ejemplo, en una monografía sobre teoría de colas podría desarrollarse la secuencia:

𝑃𝑟𝑜𝑐𝑒𝑠𝑜 𝑃𝑜𝑖𝑠𝑠𝑜𝑛   →   𝐸𝑥𝑝𝑜𝑛𝑒𝑛𝑐𝑖𝑎𝑙   →   𝑀𝑎𝑟𝑘𝑜𝑣   →   𝑁𝑎𝑐𝑖𝑚𝑖𝑒𝑛𝑡𝑜 − 𝑚𝑢𝑒𝑟𝑡𝑒

→   𝑀𝑜𝑑𝑒𝑙𝑜𝑠 𝑑𝑒 𝑐𝑜𝑙𝑎𝑠

4.3. Estado del arte

Deberán seleccionarse y analizarse trabajos académicos relevantes. Se recomienda
comparar:

• Modelos.

• Algoritmos.

• Supuestos.

• Aplicaciones.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Ventajas.

• Limitaciones.

• Resultados.

4.4. Análisis crítico

Esta sección es fundamental. El grupo deberá realizar una elaboración propia respecto de
la bibliografía estudiada.

• Cuándo resulta adecuado utilizar determinada técnica.

• Qué supuestos limitan un modelo.

• Diferencias entre enfoques.

• Costos computacionales.

• Precisión y robustez.

• Aplicabilidad.

• Tendencias actuales.

• Problemas abiertos.

4.5. Componente computacional

Siempre que resulte posible, deberá incorporarse un pequeño componente experimental,
por ejemplo:

• Notebook demostrativo.

• Implementación de un algoritmo.

• Simulación.

• Reproducción de un ejemplo de la bibliografía.

• Comparación entre dos métodos.

• Experimento con datos.

Este componente no necesita tener la extensión de la Modalidad A, pero deberá contribuir
a comprender el tema investigado.

4.6. Conclusiones

• Principales hallazgos.

• Respuesta a las preguntas iniciales.

• Ventajas y limitaciones de las técnicas estudiadas.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Posibles líneas futuras.

5. Ejemplos de temas para una monografía

Teoría de Colas

• Relación entre cadenas de Markov y teoría de colas.

• Redes de colas aplicadas a sistemas informáticos.

• Modelos de colas para cloud computing.

• Teoría de colas en redes de comunicaciones.

• Comparación M/M/1, M/M/c y modelos de capacidad finita.

• Teoría de colas y dimensionamiento de centros de datos.

• Modelos de reparación de máquinas.

• Colas con prioridades.

• Aplicaciones de teoría de colas en salud.

Pronósticos

• Comparación de métodos clásicos de pronóstico.

• Suavización exponencial y selección óptima de parámetros.

• Evaluación de métricas de error.

• Pronósticos aplicados a planificación de capacidad.

• Pronóstico de tráfico en redes informáticas.

Metaheurísticas

• Comparación entre algoritmos genéticos y templado simulado.

• Búsqueda tabú aplicada a scheduling.

• Metaheurísticas para TSP.

• Optimización mediante algoritmos genéticos.

• Metaheurísticas para asignación de recursos.

• Métodos híbridos.

• Análisis del equilibrio exploración–explotación.

6. Entregables

Informe final

Investigación Operativa II · Trabajo Final Integrador · 2026

El informe deberá contener:

1. Portada.

2. Título.

3. Integrantes.

4. Resumen.

5. Introducción.

6. Objetivos.

7. Marco teórico.

8. Metodología.

9. Desarrollo.

10. Resultados o análisis.

11. Discusión.

12. Conclusiones.

13. Referencias bibliográficas.

Archivos complementarios

Cuando corresponda deberán entregarse:

• Notebook .ipynb.

• Código Python o R.

• Datasets.

• Archivos de configuración.

• Modelos.

• Resultados experimentales.

El trabajo deberá poder ser reproducido a partir de los archivos entregados.

7. Presentación oral

Cada grupo deberá realizar una exposición oral.

Todos los integrantes deberán participar.

Durante la defensa podrán realizarse preguntas acerca de:

• Fundamentos teóricos.

• Formulación del problema.

• Metodología.

• Algoritmos.

• Código.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Interpretación de resultados.

• Limitaciones del modelo.

Todos los integrantes deberán demostrar conocimiento global del trabajo.

8. Extensión orientativa

Aplicación práctica
Entre 12 y 20 páginas, sin considerar anexos y código fuente.

Monografía
Entre 15 y 25 páginas, sin considerar bibliografía y anexos.

La extensión es orientativa. Se valorará la calidad del contenido por sobre la cantidad de
páginas.

9. Bibliografía

Deberán utilizarse fuentes académicas y técnicas confiables. Preferentemente:

• Libros.

• Artículos científicos.

• Actas de congresos.

• Tesis.

• Documentación técnica oficial.

Para trabajos de investigación se recomienda utilizar bibliografía reciente además de los
textos fundamentales.

Todas las referencias deberán seguir un criterio bibliográfico uniforme.

10. Uso de herramientas de Inteligencia Artificial

Las herramientas de Inteligencia Artificial podrán utilizarse como apoyo para:

• Búsqueda inicial de ideas.

• Programación.

• Depuración de código.

• Generación de visualizaciones.

• Revisión de redacción.

Sin embargo, el grupo será responsable de verificar:

• Fórmulas.

• Algoritmos.

Investigación Operativa II · Trabajo Final Integrador · 2026

• Referencias.

• Código.

• Resultados.

• Conclusiones.

No se aceptarán contenidos cuya autoría o validez los integrantes no puedan explicar
durante una posible defensa o preguntas por mail.

11. Criterios de evaluación
Ponderación
Criterio
10 %
Planteamiento y relevancia del problema
15 %
Fundamentación teórica
15 %
Formulación y metodología
20 %
Desarrollo del modelo o investigación
Experimentación / análisis crítico
20 %
Interpretación de resultados y conclusiones  10 %
10 %
Informe y presentación oral
100 %
TOTAL

Modalidad A

• Formulación correcta.

• Implementación.

• Validación.

• Diseño experimental.

• Reproducibilidad.

• Análisis de resultados.

Modalidad B

• Calidad bibliográfica.

• Organización del estado del arte.

• Profundidad conceptual.

• Comparación de alternativas.

• Análisis crítico.

• Elaboración propia.

12. Propuesta inicial

Investigación Operativa II · Trabajo Final Integrador · 2026

Antes de comenzar el trabajo definitivo, cada grupo deberá presentar una propuesta breve
que incluya:

Título provisorio

Integrantes

Máximo 3 estudiantes.

Modalidad

Aplicación práctica o Monografía de investigación.

Unidad o unidades involucradas

Teoría de Colas, Pronósticos, Metaheurísticas o una combinación de ellas.

Problema o tema

Descripción breve.

Objetivo general

Indicar qué se pretende resolver, analizar, comparar, optimizar o investigar.

Técnicas previstas

Indicar los modelos o algoritmos que se utilizarán.

Herramientas

Por ejemplo: Python, R, Google Colab, QTSPlus, Java Modeling Tools u otras.

Datos

Indicar, cuando corresponda, de dónde se obtendrán los datos.

Resultados esperados

Explicar qué producto o conocimiento se espera obtener.

La propuesta deberá ser aprobada por la cátedra antes de comenzar el desarrollo
definitivo.

Investigación Operativa II · Trabajo Final Integrador · 2026

