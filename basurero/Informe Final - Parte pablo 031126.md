Tarea 3/11 (Pablo)

# Desarrollo (continuación)

## **5\. Escenario 3: recomendación de escuelas y aviso anticipado**

### **5.1 El problema: cuando las escuelas preferidas ya no están**

En la precarga cada docente indica hasta M escuelas en orden de preferencia. El día de la asamblea, cuando le toca elegir, puede pasar que varias o todas ya hayan sido tomadas por docentes de mayor puntaje. En ese caso, en el procedimiento actual (y también en E2), la docente tiene que recorrer el listado completo de vacantes y decidir en el momento. Ese es el caso que más alarga el tiempo de servicio y el que más riesgo tiene de superar la ventana τ y terminar en la cola de reintentos.

El Escenario 3 agrega dos ayudas sobre E2, sin modificar el orden de mérito: la cola sigue ordenada por puntaje Pᵢ y cada docente sigue eligiendo libremente.

1. **Oferta en el momento del turno.** Cuando le toca, el sistema le muestra primero las escuelas de su lista que todavía tienen un cargo compatible libre. Si no queda ninguna, le muestra las k \= 3 escuelas libres más parecidas a lo que ella buscaba (sección 5.3).
2. **Aviso anticipado.** Junto con el aviso “Prepárese” (sección 3.4), el sistema le informa cuáles de sus escuelas probablemente ya no estén cuando le toque y cuáles son sus mejores alternativas (sección 5.4). Así llega a la ventanilla con la decisión pensada.

La asignación de cada docente, por orden de puntaje, a la primera escuela libre de su lista es la regla que hoy aplica la asamblea y es la que respeta exactamente el orden de mérito (en la literatura de asignación se llama dictadura serial; Abdulkadiroğlu y Sönmez, 1998). Por eso no hace falta optimizar la asignación en sí: lo que se busca mejorar es **cuánto tarda cada docente en decidir**, y con ello la espera de todos los que vienen detrás.

### **5.2 Filtro por criterios de reserva**

Además de su lista de escuelas, en la precarga la docente declara criterios de reserva:

* Rᵢ: distancia máxima que acepta desde su domicilio, en kilómetros.
* Tᵢ: turnos que acepta (mañana, tarde, noche).
* Si acepta escuelas rurales.

Una escuela libre j es **candidata** para la docente i si tiene un cargo libre compatible con su nivel y especialidad y además cumple sus criterios de reserva: dᵢⱼ ≤ Rᵢ, algún cargo libre de j tiene un turno en Tᵢ, y j no es rural o ella acepta rurales. Las escuelas que no pasan el filtro no se le recomiendan nunca. Este filtro no adivina nada: aplica lo que la propia docente declaró.

### **5.3 Puntaje de recomendación**

Entre las escuelas candidatas se recomiendan las que obtienen mayor puntaje:

Puntajeᵢⱼ \= w\_d·Dᵢⱼ \+ w\_t·Tᵢⱼ \+ w\_c·Cᵢⱼ

con w\_d \+ w\_t \+ w\_c \= 1. Cada término toma valores entre 0 y 1:

* **Cercanía**, Dᵢⱼ \= 1 − dᵢⱼ/Rᵢ, donde dᵢⱼ es la distancia del domicilio de la docente a la escuela j. Vale 1 si la escuela está en su domicilio y 0 si está en el límite que aceptó. Es, en la práctica, el factor que más pesa en la elección de un cargo.
* **Parecido con su propia lista**, Tᵢⱼ: proporción de características que la escuela j comparte con las escuelas que la docente eligió. Se usan el turno, el tipo (urbana o rural) y la zona. Por ejemplo, si sus cinco escuelas son de turno mañana y de zona sur, una escuela libre de turno mañana y zona sur tiene Tᵢⱼ \= 1.
* **Coincidencia con otras docentes** (filtrado colaborativo), Cᵢⱼ: mide si las docentes con gustos parecidos también eligieron la escuela j. Con Lₖ la lista de la docente k:

  Cᵢⱼ \= Σₖ≠ᵢ \|Lₖ ∩ Lᵢ\|·\[j ∈ Lₖ\] / Σₖ≠ᵢ \|Lₖ ∩ Lᵢ\|

  Cada docente k “vota” por las escuelas de su lista con un peso igual a la cantidad de escuelas que comparte con i. Si muchas docentes que pusieron las mismas escuelas que i también pusieron la escuela j, entonces Cᵢⱼ es alto. Se calcula con las listas de la jornada, que el sistema ya conoce desde la precarga.

Como valores iniciales se proponen w\_d \= 0,5, w\_t \= 0,2 y w\_c \= 0,3.

### **5.4 Pronóstico de disponibilidad y aviso anticipado**

Cuando la docente que está en la posición k recibe el aviso “Prepárese”, el sistema estima la probabilidad θᵢⱼ de que cada escuela j de su lista siga teniendo un cargo compatible libre cuando le toque. Para eso **simula hacia adelante** el turno de las docentes que la preceden, partiendo del estado actual de la jornada:

1. Se toma el estado actual: cargos libres y docentes que todavía están antes que ella en la cola.
2. Se recorren esas docentes en orden. Cada una se desconecta con probabilidad p (y no toma cargo); si no, toma la primera escuela libre de su lista y, si no le queda ninguna, la primera recomendada según la sección 5.3.
3. Se registra qué escuelas de la lista de i siguen libres al llegar a su turno.
4. Se repite R \= 200 veces y θᵢⱼ es la proporción de repeticiones en que la escuela j sigue libre.

El aviso incluye las escuelas de su lista con su probabilidad de seguir libres y, si todas tienen θᵢⱼ \< 0,5, las tres alternativas candidatas con mayor valor de Puntajeᵢⱼ·θᵢⱼ, es decir, las que combinan parecido y probabilidad de estar disponibles. Por ejemplo:

> “Le toca en aproximadamente 10 minutos. ESC03 y ESC11 probablemente ya no estén disponibles (probabilidad de seguir libres: 8 % y 12 %). Alternativas probables: ESC20, ESC07, ESC15.”

Este pronóstico usa la misma lógica que el simulador de la sección 4, pero con una regla de elección simplificada y desde el estado actual de la jornada. Como se recalcula con cada aviso, incorpora los cargos ya tomados y los docentes que pasaron a reintentos.

### **5.5 Efecto sobre el tiempo de servicio**

El tiempo de decisión depende de la situación en la que la docente llega a la ventanilla. Sea mᵢ su tiempo medio de decisión personal (columna `tiempo_decision_medio`):

| Caso | Situación | Media del tiempo de decisión | E2 | E3 |
| :---- | :---- | :---- | :---- | :---- |
| A | Al menos una escuela de su lista sigue libre | mᵢ | Sí | Sí |
| B | Ninguna libre, acepta una de las 3 recomendadas | 2·mᵢ | — | Con probabilidad p\_rec |
| C | Ninguna libre, recorre todo el listado | 4·mᵢ | Siempre | Con probabilidad 1 − p\_rec |

En todos los casos el tiempo de decisión es log-normal y el servicio sigue truncado en τ: S \= min(T\_elección, τ). Se mantienen la desconexión con probabilidad p y la cola de reintentos de E2. La comparación E2 frente a E3 mide entonces cuánto se reduce la espera al convertir parte de los casos C en casos B. Valor inicial propuesto: p\_rec \= 0,7.

### **5.6 Validación del recomendador**

Como no hay datos reales de elecciones, se usa una prueba con datos sintéticos. Para cada docente se genera una lista “verdadera” de 10 escuelas en orden de preferencia. Se le dan al sistema solo las primeras M \= 5, se marcan como tomadas y se le pide que recomiende 3 escuelas. La medida es el **acierto en el top 3**: la proporción de docentes para las que al menos una de las tres recomendaciones está entre las 5 escuelas ocultas de su lista verdadera. Se compara con dos referencias simples:

* recomendar 3 escuelas candidatas al azar;
* recomendar las 3 escuelas candidatas más cercanas a su domicilio.

El recomendador combinado tiene que superar a ambas referencias para que tenga sentido usarlo. También se informa el acierto de cada término por separado (solo cercanía, solo parecido, solo coincidencia), para mostrar qué aporta cada uno.

### **5.7 Calibración de los pesos (a decidir)**

Los pesos w\_d, w\_t y w\_c pueden ajustarse para maximizar el acierto en el top 3 de la sección 5.6. Si se quiere incluir una metaheurística, este es un uso posible: templado simulado o búsqueda tabú sobre los pesos, con el acierto como función objetivo. Con solo tres pesos que suman 1, una búsqueda en grilla (probar todas las combinaciones de a 0,1) también resuelve el problema, por lo que la metaheurística sería un complemento y no una necesidad. **Pendiente de decisión del grupo.**

## **6\. Datos**

### **6.1 Origen y generación**

No hay datos públicos individuales de las asambleas, por lo que la instancia se genera con supuestos explícitos y una semilla fija para que sea reproducible. Las coordenadas se expresan en kilómetros sobre un plano de 20 × 20 km, como aproximación a la ciudad de Salta, y las distancias son euclídeas.

* 300 docentes y 100 cargos en 40 escuelas.
* Puntajes uniformes entre 20 y 100, sin repetidos.
* tiempo\_decision\_medio uniforme entre 1 y 3 minutos.
* Domicilios distribuidos al azar en el plano y escuelas con mayor densidad en el centro.
* Lista verdadera de 10 escuelas por docente: se eligen con mayor probabilidad las más cercanas a su domicilio y las más populares (céntricas), y con su turno preferido. Las primeras M \= 5 forman la columna `preferencias`.
* Rᵢ uniforme entre 5 y 15 km; uno o dos turnos aceptados; el 30 % acepta escuelas rurales.
* Niveles y especialidades con proporciones similares en docentes y cargos.

### **6.2 Formato de los archivos**

**data/docentes.csv**

| Columna | Tipo | Descripción |
| :---- | :---- | :---- |
| id | texto | Identificador (D001, …) |
| puntaje | decimal | Puntaje Pᵢ del Listado de Orden de Mérito |
| tiempo\_decision\_medio | decimal | mᵢ, en minutos |
| preferencias | texto | Hasta M escuelas en orden, separadas por punto y coma (ESC03;ESC11;ESC07) |
| nivel | texto | inicial, primario o secundario |
| especialidad | texto | maestro\_grado, matematica, lengua, ingles, … |
| x, y | decimal | Domicilio, en km |
| radio\_max\_km | decimal | Rᵢ |
| turnos | texto | Turnos aceptados (manana;tarde) |
| acepta\_rural | 0 / 1 | Si acepta escuelas rurales |
| preferencias\_ocultas | texto | Escuelas 6 a 10 de la lista verdadera. Solo se usa para validar el recomendador; el simulador no la lee |

**data/escuelas.csv**

| Columna | Tipo | Descripción |
| :---- | :---- | :---- |
| id\_escuela | texto | ESC01, … |
| x, y | decimal | Ubicación, en km |
| zona | texto | centro, norte, sur, este, oeste |
| tipo | texto | urbana o rural |

**data/cargos.csv**

| Columna | Tipo | Descripción |
| :---- | :---- | :---- |
| id\_cargo | texto | C001, … |
| escuela | texto | id\_escuela |
| nivel | texto | Mismos valores que en docentes.csv |
| especialidad | texto | Mismos valores que en docentes.csv |
| turno | texto | manana, tarde o noche |
| vacantes | entero | Por defecto 1 |

### **6.3 Interfaz con el simulador**

El recomendador no produce un archivo previo, porque las recomendaciones dependen de qué cargos están libres en cada momento. Se entrega como un módulo, `src/recomendador.py`, que el simulador llama durante la jornada:

| Función | Qué hace | Cuándo la llama el simulador |
| :---- | :---- | :---- |
| `candidatas(docente, estado)` | Escuelas libres que pasan el filtro de la sección 5.2 | Al iniciar el servicio |
| `recomendar(docente, estado, k=3)` | Las k candidatas con mayor puntaje (sección 5.3) | Al iniciar el servicio, si no queda ninguna escuela de su lista |
| `pronosticar(docente, estado, R=200)` | θᵢⱼ de sus escuelas y alternativas para el aviso (sección 5.4) | Al emitir el aviso “Prepárese” |

`estado` contiene los cargos libres y la cola actual. El parámetro σ de la log-normal se define una sola vez en `src/utils.py`.

### **6.4 Valores propuestos para las preguntas abiertas**

| Parámetro | Propuesta |
| :---- | :---- |
| τ (caso base) | 10 minutos; 15 minutos como análisis de sensibilidad. Reemplaza el valor ilustrativo de 3 minutos de la sección 3.3 |
| M | 5 escuelas |
| c | 1 en E1, E2 y E3; c \= 2 y 3 como sensibilidad (con mᵢ entre 1 y 3 minutos, una sola comisión puede superar las 8 horas de jornada) |
| σ de la log-normal | 0,8 |
| p\_rec | 0,7 |
| k (recomendaciones) | 3 |
| R (repeticiones del pronóstico) | 200 |
| Pesos w\_d, w\_t, w\_c | 0,5 ; 0,2 ; 0,3 |
| Reintentos | Una ronda, conservando el puntaje (supuesto de la sección 3.3) |

## **Fuentes (secciones 5 y 6\)**

* Abdulkadiroğlu, A. y Sönmez, T. (1998). Random serial dictatorship and the core from random endowments in house allocation problems. *Econometrica*, 66(3), 689-701.
* Ricci, F., Rokach, L. y Shapira, B. (Eds.) (2015). *Recommender Systems Handbook* (2.ª ed.). Springer. (Filtrado basado en contenido y filtrado colaborativo.)
* Law, A. M. (2015). *Simulation Modeling and Analysis* (5.ª ed.). McGraw-Hill. (Simulación Monte Carlo; ya citado en la sección 4.)
