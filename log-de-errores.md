# Log de Errores

Historial de errores reportados, diagnósticos y soluciones aplicadas.

---


## 2026-11-03 21:51 — E3 mal planteado: τ = 3 min tomado como decidido y metaheurística sin justificación

**Descripción:** En la primera versión de la parte de Pablo y en la explicación simple se presentó τ = 3 minutos como valor definido por Emiliano, cuando en su sección 3.3 es solo un valor ilustrativo, y es poco realista para elegir entre varias escuelas (Pablo propone 10 a 15 minutos). Además, el E3 se planteó como un algoritmo genético para pre-asignar cargos, pero si se respeta el orden de mérito la solución óptima es directa (asignar por puntaje la primera escuela libre de cada lista, dictadura serial), así que la metaheurística no estaba justificada.

**Solución:** Se reescribieron las secciones 5 y 6 de `docs/Informe Final - Parte pablo 031126.md`. El E3 pasa a ser: oferta en el momento del turno + recomendación de alternativas (filtro por criterios de reserva + puntaje de cercanía, parecido y filtrado colaborativo) + aviso anticipado con pronóstico de disponibilidad por simulación hacia adelante. τ propuesto: 10 min (15 min como sensibilidad). La metaheurística queda como opción para calibrar los pesos del recomendador, pendiente de decisión. Aprendizaje: no presentar valores ilustrativos como decisiones y justificar cada técnica antes de proponerla.
