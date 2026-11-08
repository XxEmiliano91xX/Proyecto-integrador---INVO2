# Log de Errores

Historial de errores reportados, diagnósticos y soluciones aplicadas.

---


## 2026-11-03 21:51 — E3 mal planteado: τ = 3 min tomado como decidido y metaheurística sin justificación

**Descripción:** En la primera versión de la parte de Pablo y en la explicación simple se presentó τ = 3 minutos como valor definido por Emiliano, cuando en su sección 3.3 es solo un valor ilustrativo, y es poco realista para elegir entre varias escuelas (Pablo propone 10 a 15 minutos). Además, el E3 se planteó como un algoritmo genético para pre-asignar cargos, pero si se respeta el orden de mérito la solución óptima es directa (asignar por puntaje la primera escuela libre de cada lista, dictadura serial), así que la metaheurística no estaba justificada.

**Solución:** Se reescribieron las secciones 5 y 6 de `docs/Informe Final - Parte pablo 031126.md`. El E3 pasa a ser: oferta en el momento del turno + recomendación de alternativas (filtro por criterios de reserva + puntaje de cercanía, parecido y filtrado colaborativo) + aviso anticipado con pronóstico de disponibilidad por simulación hacia adelante. τ propuesto: 10 min (15 min como sensibilidad). La metaheurística queda como opción para calibrar los pesos del recomendador, pendiente de decisión. Aprendizaje: no presentar valores ilustrativos como decisiones y justificar cada técnica antes de proponerla.

## 2026-11-08 11:30 — Falso positivo de división por cero (`Literal[0]` por `nonlocal`) en `src/simulation.py`

**Descripción:** El analizador estático del editor marcaba el error `Cannot divide by zero: '/' with a literal zero divisor` sobre `100.0 * llamados_sin_oferta / total_llamados` en `src/simulation.py` (línea 674). Aunque en tiempo de ejecución no fallaba (existe el resguardo `if total_llamados > 0 else 0.0` y se realizan más de 100 llamados), `llamados_sin_oferta = 0` y `total_llamados = 0` estaban inicializados como enteros literales en `simular_asamblea` y modificados únicamente vía `nonlocal` dentro de la función anidada `iniciar_turno_en_mesa`, por lo que el análisis estático infería que el divisor seguía siendo `0`.

**Solución:** Se reemplazaron ambos escalares `nonlocal` por el diccionario mutable `llamados_conteo = {"total": 0, "sin_oferta": 0}` en `src/simulation.py` (mismo patrón que `casos_conteo`), garantizando tipo `int` en lectura sin afectar la lógica ni los resultados numéricos de las réplicas. Aprendizaje: al actualizar contadores desde funciones anidadas en Python, preferir contadores en diccionario mutable evita falsos positivos de estrechamiento literal en analizadores estáticos.
