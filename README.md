# TP5_SIM

Simulación por eventos discretos del sistema de inscripción a exámenes
de la UNVM (TP5 de Simulación).

## El problema

Hay 5 PCs para que los alumnos se inscriban a exámenes. La inscripción
demora entre 5 y 8 minutos (uniforme) y los alumnos llegan con una
exponencial negativa de media 2'. Un técnico de sistemas hace
mantenimiento preventivo a cada PC, siempre en el mismo orden (1, 2, 3,
4, 5), sin poder alterar la secuencia. El mantenimiento tiene prioridad
sobre los alumnos pero no interrumpe una inscripción en curso, y el
técnico vuelve a hacer una ronda completa 1 hora ± 3' después de
terminar la última PC del ciclo anterior. La demora de cada
mantenimiento depende de la cantidad de archivos de la PC (1000, 1500 o
2000, equiprobables) según `dA/dt = -68 - A²/A0`, integrada
numéricamente por el método de Euler. Si un alumno llega y hay más de 6
esperando, se va y vuelve a la media hora.

Hay que determinar:

- el % de alumnos que se van para regresar más tarde,
- el tiempo ocioso promedio del técnico de mantenimiento por visita,
- el promedio de visitas por día del técnico.

El enunciado completo y la resolución manual están en
`G2_TP5_Inscripcion a examenes.xlsx` (hojas "Enunciado", "Resolucion" y
"Método de Euler").

## Estructura

- `euler.py`: `EulerSimulator`, integra numéricamente la demora de
  mantenimiento.
- `simulacion.py`: `SimulacionInscripcion`, el motor de eventos
  discretos (vector de estado, variables aleatorias, resultados
  finales). También se puede correr como script de consola.
- `params.py`: `Params`, todos los valores parametrizables del
  enunciado, con sus defaults.
- `ui/pantalla.py`: pantalla de escritorio (PyQt6) para configurar los
  parámetros, correr la simulación y ver los resultados.
- `ui/error_dialog.py`: diálogo simple para mostrar errores de
  validación de la pantalla.

## Instalación

```bash
pip install -r requirements.txt
```

## Cómo correrlo

**Pantalla (recomendado):**

```bash
python ui/pantalla.py
```

Completá los parámetros (o dejá los defaults) y presioná "Iniciar". La
tabla de la derecha muestra el vector de estado (la ventana de `i`
filas a partir del minuto `j`) y debajo aparecen los 3 resultados
finales. El botón "Exportar integración de Euler (CSV)" vuelca el
detalle paso a paso de cada integración a `euler_log.csv`, con
referencia a qué visita y PC corresponde.

**Consola (alternativa):**

```bash
python simulacion.py
```

Pide los mismos parámetros por `input()` (con defaults razonables si se
aprieta Enter) e imprime el vector de estado completo, los resultados y
exporta igual el detalle de Euler.

## Parámetros

Todos son configurables desde la pantalla o pasándolos a
`SimulacionInscripcion`/`Params`:

- **X** (`tiempo_maximo_simulacion`): minutos totales a simular.
- **N** (`iteraciones_maximas`): tope de iteraciones (máx. 100000); la
  simulación corta por lo que ocurra primero entre X y N.
- **i / j** (`filas_a_mostrar` / `minutos_desde_que_muestra`): cuántas
  filas del vector de estado mostrar, a partir de qué minuto.
- `media_llegada_alumnos`, `tiempo_minimo_inscripcion`,
  `tiempo_maximo_inscripcion`, `max_cola`, `tiempo_regreso_alumno`:
  parámetros del lado de los alumnos.
- `media_llegada_mantenimiento`, `variacion_llegada_mantenimiento`:
  frecuencia de las rondas del técnico.
- `paso_euler` (`h`): paso de la integración numérica.

## Validación de código

```bash
python -m flake8 euler.py simulacion.py params.py ui/pantalla.py ui/error_dialog.py
python -m pyright euler.py simulacion.py params.py ui/pantalla.py ui/error_dialog.py
```

Ambos deben salir limpios.
