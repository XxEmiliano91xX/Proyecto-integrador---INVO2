# Plan de Acción - Pablo (Martes 03/11/2026)

## [Goal Description]
Ejecutar la jornada del **Martes 03/11** de acuerdo con la [Planificacion 01.md](file:///c:/Users/gato4/Desktop/UCASAL%2026/2DO%20semestre/INVO%202/4%20Proyecto%20integrador/Proyecto/docs/Planificacion%2001.md) y en sincronía con el avance ya plasmado por Emiliano en [docs/Informe Final - Parte emiliano 031126.md](file:///c:/Users/gato4/Desktop/UCASAL%2026/2DO%20semestre/INVO%202/4%20Proyecto%20integrador/Proyecto/docs/Informe%20Final%20-%20Parte%20emiliano%20031126.md).

Emiliano ya completó los capítulos de **Teoría de Colas**, **Formulación del Sistema de Espera** y **Fundamentos de Simulación**, dejando cerrada la notación, los supuestos de reintentos y la interfaz de integración. A Pablo le corresponde redactar el **Marco Teórico y Formulación de Metaheurísticas** (Capítulo 5 del informe), diseñar formalmente las estructuras de datos (`docentes.csv`, `cargos.csv`) y definir la función de aptitud y el contrato de salida para el Escenario 3.

---

## Estado Actual y Acuerdos Consolidados (Post-Lectura Emiliano)

> [!NOTE]
> **Puntos ya resueltos y congelados por Emiliano en el informe:**
> - **Notación fijada (Secc. 3.6):** $P_i$ (puntaje), $\tau$ (ventana máxima, reservada exclusivamente para colas), $c$ (canales/comisiones), $M$ (máximo de preferencias), $S_j$ (servicio), $p = 0.08$ (desconexión), $W_q, L_q$.
> - **Reintentos:** 1 sola ronda de reintento; quien pasa conserva su puntaje original en la cola secundaria.
> - **Distribución de decisión:** Log-normal con media en `tiempo_decision_medio`. Se debe fijar el desvío estándar común $\sigma$.
> - **Puntos específicos solicitados a Pablo (Secc. 3.7):**
>   1. Definir formalmente la estructura de `data/cargos.csv` para la asignación por grado/especialidad y conteo de vacantes cubiertas.
>   2. Formular la función de aptitud de la metaheurística (satisfacción de preferencias ponderada por orden de mérito).
>   3. Definir cómo la pre-asignación de E3 reduce el tiempo de decisión del docente (e.g., de ~1-3 min a ~15-30 seg para confirmación).
>   4. Entregar el contrato formal del archivo `data/cronograma_optimizado.json` para que Emiliano lo consuma el viernes 06/11.

---

## Decisiones Técnicas Adoptadas para Metaheurísticas

1. **Metaheurística:** **Algoritmo Genético (AG)**.
   - *Justificación:* Problema de asignación combinatoria multiobjetivo con restricciones duras (capacidad de vacantes de cargos) y blandas (preferencias de escuelas vs. orden de mérito).
2. **Representación / Codificación:**
   - Vector de asignación de longitud $N$ (donde el gen $i$ indica el `id_cargo` asignado al docente $i$, o $0$ si queda vacante/espera).
3. **Función de Aptitud (Fitness):**
   $$f(x) = \sum_{i=1}^{N} \Big[ \text{Satisfacción}(i, \text{cargo}_i) \cdot w(P_i) \Big] - \text{PenalizaciónInfactibilidad}(x)$$
   donde el peso $w(P_i)$ prioriza el cumplimiento de las preferencias de los docentes con mayor puntaje $P_i$.
4. **Impacto en Escenario 3 (Simulación):**
   - Si un docente recibe una oferta pre-calculada en E3 que coincide con su 1ª preferencia, su tiempo de decisión se modela como $\sim \text{LogNormal}(\mu_{\text{rápido}} = 20\text{ s})$, reduciendo drásticamente $W_q$ y el tiempo total de la asamblea.

---

## Tareas de Pablo para Hoy (Martes 03/11)

### Fase 1: Redacción del Marco Teórico de Metaheurísticas (Sección 5 del Informe)
Redactar en el informe (Word / Markdown):
- **5.1 Introducción y Justificación:** Complejidad del problema de matching docente-cargo ($M^N$), limitaciones de métodos exactos y pertinencia del enfoque metaheurístico.
- **5.2 Algoritmos Genéticos:** Fundamentos teóricos (Holland, Goldberg), analogía biológica, ciclo del AG (población inicial, evaluación, selección, cruce, mutación, reemplazo).
- **5.3 Codificación y Espacio de Búsqueda:** Representación cromosómica y manejo de restricciones (máximo 1 docente por vacante).
- **5.4 Operadores Genéticos:**
  - Selección: Torneo binario o ruleta ponderada.
  - Cruce: Operador preservador de asignaciones (e.g., Two-Point Crossover con reparación o Uniform Crossover).
  - Mutación: Swap de cargos entre docentes compatibles o reasignación a cargo vacante ($p_m \approx 0.05$).
  - Elitismo: Conservación del mejor 5% de soluciones.
- **5.5 Formulación Matemática de la Función de Aptitud:** Definición explícita de la función multiobjetivo y penalizaciones.
- **5.6 Criterios de Parada y Parámetros:** Generaciones máximas ($G_{max}$, usando $G$ para no colisionar con $\tau$), tamaño de población ($N_{pop}$), tasa de convergencia.

> [!NOTE]
> **Estado 03/11 21:07:** Fases 1 y 2 redactadas en [docs/Informe Final - Parte pablo 031126.md](docs/Informe%20Final%20-%20Parte%20pablo%20031126.md) (secciones 5 y 6). Cambio respecto del plan: se usa **permutación + decodificador** en lugar de vector de cargos (toda solución es factible). Pendiente: Fase 3 (pegar en el Word) y validar propuestas con Emiliano (tabla 6.5).

### Fase 2: Especificación y Contrato de Datos (para el Viernes 06/11)
- [x] **Definir `data/docentes.csv`:**
  - Columnas: `id,puntaje,tiempo_decision_medio,preferencias,grado,especialidad`
  - Formato `preferencias`: lista de IDs de escuela o cargos ordenados por prioridad (ej: `ESC101;ESC204;ESC105`).
- [x] **Definir `data/cargos.csv`:**
  - Columnas: `id_cargo,escuela,turno,grado,especialidad,vacantes`
- [x] **Definir `data/cronograma_optimizado.json`:**
  - Esquema JSON con la pre-asignación óptima para el Escenario 3 (mapeo `id_docente` $\to$ `id_cargo_sugerido`).
- [x] **Fijar parámetro $\sigma$:** propuesto $\sigma = 0.8$ (cola larga: P{T > 3 min} ≈ 4 % con media 1 min). Falta confirmarlo con Emiliano.

### Fase 3: Integración del Documento
- [ ] Acoplar la sección redactada al documento principal junto a las secciones 1, 2, 3 y 4 de Emiliano, asegurando consistencia de estilo y referencias bibliográficas (citando a Goldberg, Holland, y literatura de asignación docente).

---

## Verification Plan

### Manual Verification
- [ ] **Control de Notación:** Validar que ninguna variable de metaheurísticas use $\tau$ (usar $G_{max}$, $t_{gen}$, etc.).
- [ ] **Alineación con Sección 3.7 de Emiliano:** Asegurar que las variables de `cargos.csv` y el comportamiento de E3 respondan exactamente a lo que el simulador espera leer el viernes.
- [ ] **Criterios de Evaluación:** Verificar cumplimiento de las pautas de la cátedra para Metaheurísticas ([Sección 2.3 y 11 de Trabajo_Final_IO2_2026.md](file:///c:/Users/gato4/Desktop/UCASAL%2026/2DO%20semestre/INVO%202/4%20Proyecto%20integrador/Proyecto/docs/Trabajo_Final_IO2_2026.md)).
