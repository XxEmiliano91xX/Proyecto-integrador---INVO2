# Explicación simple: tu parte (metaheurísticas) y lo que necesitás saber de Emi

---

## Parte 1: Lo justo de la parte de Emi

### El problema que estudiamos
Hoy, en las asambleas de designación docente de Salta, se llama a los docentes **uno por uno, por puntaje**. Si uno tarda 10 minutos, o no aparece, **todos los que siguen esperan**. Nadie sabe a qué hora le toca.

### Qué hizo Emi
Emi armó la parte de **colas**: estudia la asamblea como una fila de espera.

| Concepto de colas | En nuestro caso |
|---|---|
| Cliente | Docente |
| Servidor | La ventanilla (o comisión) donde se elige el cargo |
| Tiempo de servicio | Lo que tarda el docente en decidir |
| Disciplina | Por puntaje (el de más puntaje va primero) |

### Las 3 ideas clave de Emi
1. **Ventana τ (tau) = 3 minutos.** Si el docente no elige en 3 min, no frena a nadie: pasa a una **cola de reintentos** (vuelve al final, conservando su puntaje). Hay una sola ronda de reintento.
2. **Aviso "Prepárese".** El sistema calcula a qué hora le toca a cada uno y le avisa 10 minutos antes.
3. **Simulación.** Como el sistema es raro (fila finita, tope de tiempo, reintentos), las fórmulas clásicas de colas (M/M/1, M/M/c) no alcanzan. Por eso se **simula en Python**: se "juega" la asamblea miles de veces en la computadora y se miden los resultados. Las fórmulas clásicas se usan solo para comprobar que el simulador está bien programado.

### Los 3 escenarios que se comparan

| Escenario | Qué es | De quién depende |
|---|---|---|
| **E1** | Como hoy: fila simple, sin tope de tiempo | Emi |
| **E2** | Con ventana de 3 min + aviso + reintentos | Emi |
| **E3** | E2 + **a cada docente ya se le propone un cargo** | **Vos** (metaheurística) + Emi |

### Lo que se mide
- **Wq**: cuánto espera en promedio un docente.
- **Lq**: cuánta gente hay esperando en promedio.
- **Tiempo total** de la asamblea.
- **Tasa de atención** y **cargos cubiertos**.

### Símbolos que NO podés usar para otra cosa
- **τ**: solo para la ventana de 3 min.
- **p**: probabilidad de que un docente se desconecte (0,08 = 8 %).
- **c**: cantidad de comisiones.
- **M**: máximo de escuelas que puede elegir cada docente (propusimos 5).
- **Pᵢ**: puntaje del docente i.

---

## Parte 2: Metaheurísticas explicadas desde cero

### ¿Qué problema resolvés vos?
Antes de la asamblea, cada docente anotó hasta 5 escuelas que le gustan, en orden. Hay **300 docentes** y **100 cargos**. Tu trabajo es decidir **qué cargo proponerle a cada uno**, de forma que:

- Cada uno reciba una escuela **lo más arriba posible en su lista**.
- Se cubran **la mayor cantidad de cargos** posible.
- Se respete el **mérito**: alguien con más puntaje no debería quedar peor que alguien con menos.
- Solo se puede asignar un cargo que coincida con el **nivel y especialidad** del docente (un profe de matemática no va a un cargo de inglés).

Así, el día de la asamblea el docente solo dice "sí, acepto" en 20 segundos en vez de pensar 2 minutos. **Eso acelera la fila de Emi** (escenario E3).

### ¿Por qué no probar todas las combinaciones?
Porque son demasiadas. La cantidad de formas de ordenar 300 docentes es un número de **más de 600 cifras**. Ni todas las computadoras del mundo terminarían nunca.

### ¿Qué es una metaheurística?
Es una **estrategia inteligente para buscar una solución muy buena sin revisar todas**. No garantiza la mejor de todas, pero encuentra una excelente en segundos.

> **Analogía:** buscar el punto más alto de una montaña con niebla. No podés ver todo el mapa, pero podés ir probando, quedarte con lo que sube y de vez en cuando probar algo distinto por si hay una montaña más alta en otro lado.

Las dos fuerzas de toda metaheurística:
- **Explotar**: mejorar lo bueno que ya encontraste.
- **Explorar**: probar cosas nuevas para no quedarte trabado.

### El Algoritmo Genético (el que elegimos)
Imita la **evolución de las especies**: sobreviven los más aptos y tienen "hijos".

| Biología | En nuestro problema |
|---|---|
| Individuo | Una posible solución (una forma de asignar cargos) |
| Población | 100 soluciones distintas al mismo tiempo |
| Aptitud | Qué tan buena es la solución (un número) |
| Reproducción (cruce) | Mezclar dos soluciones buenas para crear una nueva |
| Mutación | Cambiar algo al azar en una solución |
| Generación | Una vuelta del ciclo |

**El ciclo:**
```
1. Crear 100 soluciones
2. Darles una nota a cada una (aptitud)
3. Repetir 300 veces:
     - Elegir a las mejores como "padres"
     - Mezclarlas para crear "hijos"
     - Cambiar algo al azar en algunos hijos
     - Quedarse con la nueva generación (guardando siempre a las 2 mejores)
4. Entregar la mejor solución encontrada
```

### ¿Cómo es una "solución" en nuestro caso?
Una solución es simplemente **una fila de docentes en cierto orden**, por ejemplo:

```
[D005, D001, D002, D010, ...]
```

Para saber qué cargo le toca a cada uno, se recorre esa fila y **a cada docente se le da la primera escuela de su lista que todavía tenga un cargo compatible libre**. Si no queda ninguna, ese docente elige normalmente el día de la asamblea.

**Ventaja:** cualquier orden produce una asignación válida. Nunca se le da un cargo a dos personas ni un cargo incompatible.

**Dato clave:** si el orden es **de mayor a menor puntaje**, se obtiene exactamente lo que hace hoy la asamblea (en la teoría se llama *dictadura serial*). Esa es nuestra **solución de referencia**.

### La nota de cada solución (función de aptitud)

```
Nota = Satisfacción + Cobertura − 5 × Injusticias
```

- **Satisfacción**: ¿qué tan arriba en su lista quedó cada docente? (vale más si es alguien con mucho puntaje).
- **Cobertura**: ¿qué porcentaje de cargos se cubrió?
- **Injusticias**: ¿cuántas veces alguien con más puntaje se quedó sin una escuela que quería y se la dieron a alguien con menos? Se resta, y con peso 5 porque el mérito importa mucho.

Ese "5" (se llama **γ**, gamma) es una perilla:
- γ **grande** → "el mérito es sagrado" → el algoritmo vuelve a la solución de hoy.
- γ **chico** → "aceptamos alguna injusticia pequeña si se cubren más cargos".

### Entonces, ¿para qué sirve si la solución de hoy ya respeta el mérito?
**Esta es la pregunta que te pueden hacer en la defensa.** Respuesta:

> El algoritmo genético nos permite **medir cuánto mérito habría que ceder para ganar en cobertura o satisfacción**. Eso le da a la Junta información para decidir su política. Además, la solución de hoy nos sirve para verificar que el algoritmo funciona: con γ muy grande, tiene que llegar a ella.

### Los operadores, en una línea cada uno
- **Selección por torneo**: se eligen 3 soluciones al azar y gana la de mejor nota.
- **Cruce de orden (OX)**: se copia un pedazo de la fila de un padre y se completa con el orden del otro padre.
- **Mutación por intercambio**: se intercambian de lugar dos docentes (preferentemente cercanos en puntaje).
- **Elitismo**: las 2 mejores soluciones pasan siempre a la siguiente generación, así nunca se empeora.

### Cuándo para
A las **300 generaciones**, o antes si pasan **50 generaciones sin mejorar**.

### Cómo comprobamos que está bien
1. Con γ muy grande debe dar la solución de hoy (cero injusticias).
2. Con un caso chico (8 docentes) se prueban todas las combinaciones a mano y el algoritmo debe encontrar la mejor.
3. Nunca debe dar más docentes que vacantes a un cargo.

### Lo que comparamos

| Config. | Qué es |
|---|---|
| AG-0 | La solución de hoy (por puntaje), sin optimizar |
| AG-1 | γ = 5: mérito muy protegido |
| AG-2 | γ = 1: equilibrio entre mérito y cobertura |
| AG-3 | AG-1 pero con más mutación (explora más) |

---

## Parte 3: Cómo se conecta tu parte con la de Emi

```
 docentes.csv + cargos.csv
            │
            ▼
   ALGORITMO GENÉTICO (vos)
            │
            ▼
 cronograma_optimizado.json  ← "a D001 proponerle C017, a D002 C044..."
            │
            ▼
   SIMULADOR E3 (Emi)
     - Si el docente acepta (85 %): decide en ~20 segundos
     - Si no acepta: decide como en E2
            │
            ▼
   Resultados: Wq, tiempo total, cargos cubiertos
```

**Lo que tenés que acordar con Emi:** 0,8 de dispersión en los tiempos de decisión (σ), 85 % de aceptación, 20 segundos de confirmación y una sola comisión en E3.

---

## Resumen en 5 frases
1. La asamblea actual es una fila lenta; Emi la estudia con teoría de colas y simulación.
2. Vos calculás de antemano qué cargo proponerle a cada docente.
3. Hay demasiadas combinaciones, así que usás un algoritmo genético que "evoluciona" soluciones.
4. Cada solución es un orden de docentes; la nota premia satisfacción y cobertura y castiga las injusticias de mérito.
5. Tu resultado (un archivo JSON) entra al simulador de Emi y acelera la fila en el escenario E3.

