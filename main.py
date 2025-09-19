"""
Ejemplo de uso del minimizador de AFD/AFND

Este archivo muestra cómo usar las diferentes clases del sistema
"""
from src.automata import Automata
from src.afd import AFD
from src.afnd import AFND


def ejemplo_uso_basico():
    """Ejemplo básico de uso del sistema"""
    
    # Crear instancia del minimizador principal
    minimizador = Automata()
    
    print("=== Ejemplo de Minimización de AFD ===")
    
    try:
        # Procesar autómata completo desde archivo
        resultado = minimizador.procesar_automata_completo(
            ruta_entrada="ejemplos/automata_ejemplo.json",
            ruta_salida="salida/automata_minimizado.json"
        )
        
        if resultado["exito"]:
            print("✅ Proceso completado exitosamente")
            print(f"Operaciones realizadas: {resultado['operaciones_realizadas']}")
            print(f"Estadísticas: {resultado['estadisticas']}")
        else:
            print("❌ Error en el proceso:")
            for error in resultado["errores"]:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def ejemplo_creacion_manual():
    """Ejemplo de creación manual de autómatas"""
    
    print("\n=== Ejemplo de Creación Manual ===")
    
    # Crear AFD de ejemplo
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
    estado_inicial = 'q0'
    estados_finales = {'q2'}
    
    # Crear instancia de AFD
    afd = AFD(estados, alfabeto, transiciones, estado_inicial, estados_finales)
    
    print(f"AFD creado: {afd}")
    print(f"Estadísticas: {afd.to_dict()}")
    
    # Crear AFND de ejemplo
    estados_afnd = {'p0', 'p1', 'p2'}
    transiciones_afnd = {
        ('p0', 'a'): {'p1', 'p2'},  # Transición no determinística
        ('p0', 'b'): {'p0'},
        ('p1', 'a'): {'p2'},
        ('p2', 'b'): {'p2'}
    }
    
    afnd = AFND(estados_afnd, alfabeto, transiciones_afnd, 'p0', {'p2'})
    print(f"\nAFND creado: {afnd}")


def ejemplo_operaciones_individuales():
    """Ejemplo de uso de operaciones individuales"""
    
    print("\n=== Ejemplo de Operaciones Individuales ===")
    
    minimizador = Automata()
    
    # Crear AFD de ejemplo con estados redundantes
    estados = {'q0', 'q1', 'q2', 'q3', 'q4'}
    alfabeto = {'a', 'b'}
    transiciones = {
        ('q0', 'a'): 'q1',
        ('q0', 'b'): 'q2',
        ('q1', 'a'): 'q3',  # q1 y q2 podrían ser equivalentes
        ('q1', 'b'): 'q4',
        ('q2', 'a'): 'q3',
        ('q2', 'b'): 'q4',
        ('q3', 'a'): 'q3',
        ('q3', 'b'): 'q3',
        ('q4', 'a'): 'q4',
        ('q4', 'b'): 'q4'
    }
    
    afd_original = AFD(estados, alfabeto, transiciones, 'q0', {'q3'})
    
    # Obtener estadísticas del autómata original
    stats_original = minimizador.obtener_estadisticas_automata(afd_original)
    print(f"Estadísticas AFD original: {stats_original}")
    
    # Minimizar AFD
    afd_minimizado = minimizador.minimizar_afd(afd_original)
    
    # Obtener estadísticas del autómata minimizado
    stats_minimizado = minimizador.obtener_estadisticas_automata(afd_minimizado)
    print(f"Estadísticas AFD minimizado: {stats_minimizado}")
    
    # Mostrar historial de operaciones
    historial = minimizador.obtener_historial()
    print("\nHistorial de operaciones:")
    for operacion in historial:
        print(f"  - {operacion['tipo']}: {operacion['descripcion']}")


if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_creacion_manual()
    ejemplo_operaciones_individuales()
    # ejemplo_uso_basico()  # Comentado porque requiere archivos de ejemplo
