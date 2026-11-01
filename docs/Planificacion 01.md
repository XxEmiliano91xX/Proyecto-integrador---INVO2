# Resumen de planificación: Trabajo Final de Investigación Operativa II

**Tema:** Sistema de turnos dinámicos para las asignaciones docentes en Salta
**Integrantes:** Pablo y Emiliano
**Fecha de entrega:** martes 10/11
**Días que NO contamos:** 02/11, 04/11, 05/11 (exposición de redes y parciales) y 09/11 (colchón de contingencia)

---

## 1. Idea del proyecto

Hoy las asambleas de designación docente de la Junta Calificadora de Salta son estrictamente secuenciales: se llama a los docentes por puntaje, uno por uno, y la decisión del docente *N* bloquea al docente *N+1*. Los docentes no saben cuándo les toca, algunos deciden en 30 segundos y otros en 10 minutos, y si alguien no responde se frena toda la línea.

Nuestra propuesta es reemplazar la espera ciega por un sistema de turnos con estimación de horario y ventanas de decisión:

1. Los docentes suben sus documentos oficiales, se aprueban y quedan en estado **disponible**.
2. Cada docente precarga una lista de escuelas de su interés.
3. El día de la asignación hay una **cola principal ordenada por puntaje**.
4. El sistema **estima a qué hora le toca** a cada docente y le avisa **10 minutos antes** ("Prepárese").
5. Cuando le toca, tiene una **ventana de tiempo máxima (τ)** para elegir un cargo según su grado y especialidad.
6. Si no elige a tiempo, pasa a una **cola de reintentos** de menor prioridad, así no demora al resto.

## 2. Alcance

**Entra en el trabajo:**
- Contexto del proceso real en Salta y definición formal del problema.
- Marco teórico: colas con prioridad no apropiativa, colas de reintento (feedback), metaheurísticas, simulación de eventos discretos.
- Formulación matemática del sistema.
- Simulador en Python con 3 escenarios comparables.
- Metaheurística para optimizar la asignación o las tandas.
- Resultados, análisis de sensibilidad, conclusiones y recomendaciones para la Junta.

**No entra:**
- Desarrollo de una aplicación real (sin front, sin base de datos productiva).
- Validación de documentos oficiales (se asume que los docentes ya están validados).

## 3. Modelo (a alto nivel)

```
[Docentes validados (LOM)]
          │
          ▼
 COLA PRINCIPAL (prioridad no apropiativa, por puntaje)
          │
          ├─► Estimador de horario E[T_k] + aviso (T - 10 min)
          ▼
 VENTANILLA DE ELECCIÓN (slot máximo τ)
          │
   ┌──────┴──────────────┐
   ▼                     ▼
[Elige en t ≤ τ]   [Timeout o ausente]
   │                     │
   ▼                     ▼
[Cargo asignado]   COLA DE REINTENTOS (baja prioridad)
```

**Teoría de colas**
- Disciplina de servicio: prioridad **no apropiativa** por puntaje.
- Tiempo de servicio truncado: `S = min(T_eleccion, τ)`.
- Reintentos: quien excede τ pasa a una cola de segunda vuelta.

**Estimación de horario**
- `E[T_k] = T_inicio + Σ_{j=1}^{k-1} E[S_j]`
- Se recalcula en tiempo real cada vez que un docente termina antes o pasa a reintentos.
- Alerta cuando `E[T_k] − T_actual ≤ 10 min`.

**Metaheurística**
- Matching docentes-cargos que maximiza la satisfacción de preferencias (cercanía, turno) respetando el orden de mérito, y/o partición de cargos en comisiones simultáneas para minimizar el makespan.
- Candidatos: Algoritmo Genético o Búsqueda Tabú.

**Simulación (eventos discretos, Python)**
- Entrada de referencia: 300 docentes, 100 cargos.
- Tiempos de decisión log-normales (la mayoría ~1 min, pocos muy largos).
- Probabilidad de desconexión o falla técnica: `p = 0.08`.
- Mínimo 30 réplicas por escenario.

| Escenario | Descripción |
|---|---|
| **E1 (base)** | Procedimiento tradicional: cola simple sin límite de tiempo |
| **E2** | Ventana τ + estimador de alerta + cola de reintentos |
| **E3** | Modelo integrado: E2 + pre-asignación por preferencias con la metaheurística |

**Métricas:** `W_q`, `L_q`, tiempo total de la jornada, tasa de atención, cargos cubiertos.

## 4. Contrato conceptual de notación

Para no escribir cosas contradictorias el martes, estos nombres quedan fijos (a confirmar en los primeros 20 minutos del 03/11):

| Símbolo | Significado |
|---|---|
| `P_i` | Puntaje del docente *i* |
| `τ` | Ventana máxima de decisión (tiempo límite de servicio) |
| `c` | Cantidad de comisiones / canales de atención simultáneos |
| `M` | Máximo de escuelas que cada docente puede precargar |
| `S_j` | Tiempo de servicio del docente *j* (`min(T_eleccion, τ)`) |
| `E[T_k]` | Horario estimado de atención del docente en la posición *k* |
| `p` | Probabilidad de desconexión o falla técnica |
| `W_q`, `L_q` | Tiempo medio de espera en cola y largo medio de cola |

> `τ` se reserva **solo** para la ventana de decisión. Si la metaheurística necesita un límite propio (por ejemplo de tiempo de cómputo), usa otro símbolo.

## 5. Formato del dataset `docentes.csv`

Lo genera Pablo (datos sintéticos) en los primeros 15 minutos del viernes 06/11.

| Columna | Descripción |
|---|---|
| `id` | Identificador del docente |
| `puntaje` | Puntaje del Listado de Orden de Mérito |
| `tiempo_decision_medio` | Media de la distribución de tiempo de decisión |
| `preferencias` | Escuelas de interés (hasta `M`) |

La metaheurística (Pablo) entrega su salida en un archivo simple (`cronograma_optimizado.json` o `.csv`) que el simulador (Emiliano) consume para el Escenario 3.

## 6. Estructura del repositorio

Emiliano la copia y adapta de la configuración usada en Compiladores.

```
/docs        Fuente del informe y diagramas conceptuales
/src         Código modularizado (simulation.py, metaheuristic.py, utils.py)
/data        Instancias sintéticas (docentes, cargos vacantes)
/notebooks   Visualizaciones y gráficos de resultados
requirements.txt
README.md
.gitignore   (para Python)
```

## 7. Cronograma

| Fecha | Día | Foco | Pablo | Emiliano |
|---|---|---|---|---|
| 01/11 | Domingo | Setup y planificación | Planificación del informe (alcance, objetivos, estructura) | Documento Word en Drive (portada, estilos de la cátedra) y repo de GitHub copiando la config de Compiladores |
| 02/11 | Lunes | *No se cuenta* | — | — |
| 03/11 | Martes | Marco teórico y formulación (en paralelo) | Metaheurísticas, instancia de datos y función de aptitud (fitness) | Teoría de colas, formulación del sistema de espera y fundamentos de simulación |
| 04/11 | Miércoles | *No se cuenta* | — | — |
| 05/11 | Jueves | *No se cuenta* (parcial de Sistemas 3) | — | — |
| 06/11 | Viernes | Programación (en paralelo) | Dataset sintético, algoritmo de optimización y su salida JSON/CSV | Motor de simulación, Escenarios 1 y 2 |
| 07/11 | Sábado | Resultados y conclusiones | Experimentos, análisis del Escenario 3 y discusión general | Análisis del Escenario 1 vs 2 (efecto de τ y saturación de reintentos) |
| 08/11 | Domingo | Revisión cruzada | Revisa lo de Emiliano | Revisa lo de Pablo |
| 09/11 | Lunes | *Contingencia* | — | — |
| 10/11 | Martes | Cierre y entrega | Verificación final | Verificación final |

## 8. Reglas para trabajar en paralelo

**Martes 03/11**
- Primeros 20 minutos juntos para cerrar el contrato de notación, la función objetivo formal y los datos de entrada.
- Después cada uno escribe su sección en el mismo Word, sin pisarse.

**Viernes 06/11**
- Primeros 15 minutos: fijar el formato de `docentes.csv`.
- Emiliano **no espera** a Pablo: programa primero E1 y E2, que no dependen de la metaheurística.
- Última hora del día: integración. Se conecta la salida de Pablo al simulador para correr E3.

**Sábado 07/11**
- Mañana: correr las simulaciones (mínimo 30 réplicas por escenario), exportar CSV y generar gráficos (histogramas de espera, boxplots de tiempo total, tablas de media y desvío de `W_q`).
- Tarde: cada uno redacta su parte y juntos las conclusiones y recomendaciones para la Junta.
- No se redactan resultados sin números a mano, por eso el código debe quedar cerrado el viernes.

**Domingo 08/11**
- Revisión cruzada de texto.
- Control técnico: que las variables del marco teórico coincidan con los nombres del código y con los ejes de los gráficos.

## 9. Preguntas abiertas / pendientes

- [ ] Valor de `τ` para el caso base (la idea inicial usa 3 minutos).
- [ ] Valor de `M` (máximo de escuelas precargadas por docente).
- [ ] Cantidad de comisiones `c` en el Escenario 3.
- [ ] Metaheurística: ¿Algoritmo Genético o Búsqueda Tabú? ¿Matching de preferencias, partición en comisiones, o ambos?
- [ ] ¿Un docente enviado a reintentos conserva su puntaje original dentro de la cola de segunda vuelta?
- [ ] ¿Cuántas rondas de reintento se permiten antes de dar por perdido el turno?
- [ ] ¿Agregamos `grado` y `especialidad` al dataset de docentes y creamos un `cargos.csv`? (Hoy solo están `id`, `puntaje`, `tiempo_decision_medio` y `preferencias`.)
- [ ] Pautas y rúbrica formal de la cátedra (formato, numeración, extensión) para cargarlas en el Word.
- [ ] Nombre del repositorio y convención de ramas y commits.
- [ ] Confirmar el reparto del martes y el viernes (quedó como "bueno, vemos").
