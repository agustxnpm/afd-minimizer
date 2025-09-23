# AFD Minimizer

Un sistema completo para la minimización de Autómatas Finitos Determinísticos (AFD) y conversión de Autómatas Finitos No Determinísticos (AFND) a AFD.

## Características

- ✅ **Representación de AFD y AFND**: Clases completas para manejar ambos tipos de autómatas
- ✅ **Conversión AFND → AFD**: Algoritmo de construcción de subconjuntos
- ✅ **Minimización de AFD**: Algoritmo de partición para minimizar estados
- ✅ **Lectura/Escritura JSON**: Manejo completo de archivos en formato JSON
- ✅ **Validación**: Validación de estructura y propiedades de autómatas
- ✅ **Estadísticas**: Información detallada del proceso de minimización
- ✅ **Interfaz Gráfica**: GUI completa con visualización de autómatas
- ✅ **Tests Unitarios**: Cobertura completa de tests
- ✅ **Procesamiento Completo**: Pipeline automático de carga → conversión → minimización → guardado

## Estructura del Proyecto

```
afd-minimizer/
├── src/
│   ├── __init__.py
│   ├── afd.py                    # Clase AFD
│   ├── afnd.py                   # Clase AFND
│   ├── automata.py               # Coordinador principal
│   ├── minimizador.py            # Minimización de AFD
│   ├── conversor.py              # Conversión AFND → AFD
│   └── manejador_archivos.py     # Lectura/escritura JSON
├── tests/
│   ├── __init__.py
│   ├── test_afd.py               # Tests para AFD
│   ├── test_conversor.py         # Tests para conversión
│   ├── test_minimizador.py       # Tests para minimización
│   └── test_comparativo.py       # Tests comparativos
├── ejemplos/
│   ├── AFND1.json                # Ejemplo de AFND
│   ├── AFND2.json                # Ejemplo de AFND
│   └── AFND3.json                # Ejemplo de AFND
├── gui_minimizador.py            # Interfaz gráfica
├── ejecutar_tests.py             # Script para ejecutar tests
└── README.md
```

## Formato JSON de Entrada/Salida

### AFD
```json
{
  "tipo": "AFD",
  "estados": ["q0", "q1", "q2"],
  "alfabeto": ["a", "b"],
  "transiciones": [
    {
      "origen": "q0",
      "simbolo": "a", 
      "destino": "q1"
    }
  ],
  "estado_inicial": "q0",
  "estados_finales": ["q2"]
}
```

### AFND
```json
{
  "tipo": "AFND",
  "estados": ["p0", "p1", "p2"],
  "alfabeto": ["a", "b"],
  "transiciones": [
    {
      "origen": "p0",
      "simbolo": "a",
      "destino": "p1"
    },
    {
      "origen": "p0", 
      "simbolo": "a",
      "destino": "p2"
    }
  ],
  "estado_inicial": "p0",
  "estados_finales": ["p2"]
}
```

## Uso Básico

### Proceso Completo (Recomendado)
```python
from src.automata import Automata

minimizador = Automata()

# Procesar autómata completo: cargar → convertir → minimizar → guardar
resultado = minimizador.procesar_automata_completo(
    ruta_entrada="ejemplos/AFND1.json",
    ruta_salida="salida/automata_minimizado.json"
)

if resultado["exito"]:
    print("✅ Minimización completada")
    print(f"Operaciones realizadas: {resultado['operaciones_realizadas']}")
    print(f"Estadísticas: {resultado['estadisticas']}")
else:
    print("❌ Error en el proceso:")
    for error in resultado["errores"]:
        print(f"  - {error}")
```

### Uso Individual de Clases
```python
from src.automata import Automata
from src.afd import AFD
from src.afnd import AFND

# Crear instancia del coordinador
automata_manager = Automata()

# Cargar autómata desde archivo
afd = automata_manager.cargar("ejemplos/AFND1.json")

# Minimizar AFD
afd_minimizado = automata_manager.minimizar_afd(afd)

# Guardar resultado
automata_manager.guardar(afd_minimizado, "salida/resultado.json")
```

### Creación Manual de Autómatas
```python
from src.afd import AFD
from src.afnd import AFND

# Crear AFD programáticamente
estados = {'q0', 'q1', 'q2'}
alfabeto = {'a', 'b'}
transiciones = {
    ('q0', 'a'): 'q1',
    ('q0', 'b'): 'q2',
    ('q1', 'a'): 'q1',
    ('q1', 'b'): 'q2',
    ('q2', 'a'): 'q1', 
    ('q2', 'b'): 'q2'
}

afd = AFD(estados, alfabeto, transiciones, 'q0', {'q2'})

# Crear AFND programáticamente
estados_afnd = {'p0', 'p1', 'p2'}
transiciones_afnd = {
    ('p0', 'a'): {'p1', 'p2'},  # Transición no determinística
    ('p0', 'b'): {'p0'},
    ('p1', 'a'): {'p2'},
    ('p2', 'b'): {'p2'}
}

afnd = AFND(estados_afnd, alfabeto, transiciones_afnd, 'p0', {'p2'})
```

## Requisitos

- Python 3.8+
- PIL (Pillow) para la interfaz gráfica
- pydot y graphviz para visualización de autómatas

## Instalación

```bash
git clone <repository-url>
cd afd-minimizer
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# .venv\Scripts\activate   # En Windows
pip install -r requirements.txt
```

**Nota**: La dependencia `automata-lib` es opcional y solo se requiere para los tests comparativos.

## Ejecutar Aplicación

### Interfaz Gráfica
```bash
python gui_minimizador.py
```

### Ejecutar Tests
```bash
python ejecutar_tests.py
```

## Interfaz Gráfica

La aplicación incluye una interfaz gráfica completa que permite:

- Cargar autómatas desde archivos JSON
- Visualizar autómatas con diagramas interactivos
- Aplicar conversión AFND → AFD
- Minimizar AFD automáticamente
- Ver estadísticas detalladas
- Guardar resultados
- Zoom y navegación en los diagramas

Para iniciar la GUI:
```bash
python gui_minimizador.py
```

## Tests

El proyecto incluye tests unitarios completos:

- **Tests básicos**: Validación de clases AFD, AFND, minimización y conversión
- **Tests comparativos**: Comparación con la librería `automata-lib` (opcional)

Para ejecutar todos los tests:
```bash
python ejecutar_tests.py
```

Para instalar la dependencia opcional para tests comparativos:
```bash
pip install automata-lib
```

## Desarrollo

El proyecto está estructurado con el principio de responsabilidad única:

- **AFD/AFND**: Representación de autómatas
- **MinimizadorAFD**: Lógica de minimización
- **ConversorAFND**: Conversión AFND → AFD  
- **ManejadorArchivos**: I/O de archivos JSON
- **Automata**: Coordinación de operaciones
- **GUIMinimizador**: Interfaz gráfica
