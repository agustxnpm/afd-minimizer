# AFD Minimizer

Un sistema completo para la minimización de Autómatas Finitos Determinísticos (AFD) y conversión de Autómatas Finitos No Determinísticos (AFND) a AFD.

## Características

- ✅ **Representación de AFD y AFND**: Clases completas para manejar ambos tipos de autómatas
- ✅ **Conversión AFND → AFD**: Algoritmo de construcción de subconjuntos
- ✅ **Minimización de AFD**: Algoritmo de partición para minimizar estados
- ✅ **Lectura/Escritura JSON**: Manejo completo de archivos en formato JSON
- ✅ **Validación**: Validación de estructura y propiedades de autómatas
- ✅ **Estadísticas**: Información detallada del proceso de minimización

## Estructura del Proyecto

```
afd-minimizer/
├── src/
│   ├── __init__.py
│   ├── afd.py                    # Clase AFD
│   ├── afnd.py                   # Clase AFND  
│   ├── minimizador.py            # Minimización de AFD
│   ├── conversor.py              # Conversión AFND → AFD
│   ├── manejador_archivos.py     # Lectura/escritura JSON
│   └── minimizador_principal.py  # Coordinador principal
├── ejemplos/
│   ├── automata_ejemplo.json     # Ejemplo de AFD
│   └── afnd_ejemplo.json         # Ejemplo de AFND
├── main.py                       # Ejemplos de uso
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
from src.minimizador_principal import MinimizadorPrincipal

minimizador = MinimizadorPrincipal()

# Procesar autómata completo: cargar → convertir → minimizar → guardar
resultado = minimizador.procesar_automata_completo(
    ruta_entrada="ejemplos/automata_ejemplo.json",
    ruta_salida="salida/automata_minimizado.json"
)

if resultado["exito"]:
    print("✅ Minimización completada")
    print(f"Reducción de estados: {resultado['estadisticas']['reduccion']['estados']}")
```

### Uso Individual de Clases
```python
from src.afd import AFD
from src.minimizador import MinimizadorAFD
from src.manejador_archivos import ManejadorArchivos

# Cargar AFD desde archivo
afd = ManejadorArchivos.leer_automata("ejemplos/automata_ejemplo.json")

# Minimizar
minimizador = MinimizadorAFD(afd)
afd_minimizado = minimizador.minimizar()

# Guardar resultado
ManejadorArchivos.escribir_automata(afd_minimizado, "salida/resultado.json")
```

### Creación Manual de Autómatas
```python
from src.afd import AFD

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
```

## Requisitos

- Python 3.8+
- Typing support

## Instalación

```bash
git clone <repository-url>
cd afd-minimizer
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# .venv\Scripts\activate   # En Windows
```

## Ejecutar Ejemplos

```bash
python main.py
```

## Desarrollo

El proyecto está estructurado con el principio de responsabilidad única:

- **AFD/AFND**: Representación de autómatas
- **MinimizadorAFD**: Lógica de minimización
- **ConversorAFND**: Conversión AFND → AFD  
- **ManejadorArchivos**: I/O de archivos JSON
- **MinimizadorPrincipal**: Coordinación de operaciones

## TODO

- [ ] Implementar algoritmos de minimización
- [ ] Implementar conversión AFND → AFD
- [ ] Agregar validaciones completas
- [ ] Implementar procesamiento de cadenas
- [ ] Agregar visualización gráfica
- [ ] Tests unitarios
- [ ] Documentación API completa
