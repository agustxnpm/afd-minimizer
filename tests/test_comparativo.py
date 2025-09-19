"""
Tests comparativos entre nuestra implementación y automata-lib
Verifica que nuestros algoritmos producen los mismos resultados que la librería estándar
"""
import unittest
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from afd import AFD
from afnd import AFND

# Importar automata-lib
try:
    from automata.fa.dfa import DFA
    from automata.fa.nfa import NFA
    AUTOMATA_LIB_DISPONIBLE = True
except ImportError:
    AUTOMATA_LIB_DISPONIBLE = False
    print("⚠️ automata-lib no está disponible. Instálala con: pip install automata-lib")


@unittest.skipUnless(AUTOMATA_LIB_DISPONIBLE, "automata-lib no está disponible")
class TestComparativoAutomataLib(unittest.TestCase):
    """Tests comparativos con automata-lib"""
    
    def setUp(self):
        """Configurar AFDs para comparar"""
        
        # AFD que acepta cadenas que terminan en 'b'
        self.mi_afd_termina_b = AFD(
            estados={'q0', 'q1'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q0',
                ('q0', 'b'): 'q1',
                ('q1', 'a'): 'q0',
                ('q1', 'b'): 'q1'
            },
            estado_inicial='q0',
            estados_finales={'q1'}
        )
        
        # Mismo AFD usando automata-lib
        self.automata_lib_termina_b = DFA(
            states={'q0', 'q1'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': 'q0', 'b': 'q1'},
                'q1': {'a': 'q0', 'b': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        
        # AFD más complejo: acepta cadenas con número par de 'a's
        self.mi_afd_par_as = AFD(
            estados={'q0', 'q1'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',  # par -> impar
                ('q0', 'b'): 'q0',  # par -> par  
                ('q1', 'a'): 'q0',  # impar -> par
                ('q1', 'b'): 'q1'   # impar -> impar
            },
            estado_inicial='q0',
            estados_finales={'q0'}  # q0 = número par de 'a's
        )
        
        # Mismo AFD en automata-lib
        self.automata_lib_par_as = DFA(
            states={'q0', 'q1'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': 'q1', 'b': 'q0'},
                'q1': {'a': 'q0', 'b': 'q1'}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        
        # Conjunto de cadenas de prueba
        self.cadenas_prueba = [
            "",           # cadena vacía
            "a",          # un símbolo
            "b",
            "aa",         # dos símbolos
            "ab", 
            "ba",
            "bb",
            "aaa",        # tres símbolos
            "aab",
            "aba", 
            "abb",
            "baa",
            "bab",
            "bba", 
            "bbb",
            "aaaa",       # cuatro símbolos
            "abab",
            "baba",
            "bbbb",
            "aaaaa",      # cinco símbolos
            "ababa",
            "babab",
            "bbbbb"
        ]
    
    def test_procesar_cadena_termina_b(self):
        """Comparar procesamiento de cadenas - AFD que termina en 'b'"""
        print("\n=== Test Comparativo: AFD termina en 'b' ===")
        
        diferencias = []
        
        for cadena in self.cadenas_prueba:
            # Resultado de nuestra implementación
            mi_resultado = self.mi_afd_termina_b.procesar_cadena(cadena)
            
            # Resultado de automata-lib
            lib_resultado = self.automata_lib_termina_b.accepts_input(cadena)
            
            # Comparar resultados
            if mi_resultado != lib_resultado:
                diferencias.append(f"'{cadena}': Mi={mi_resultado}, Lib={lib_resultado}")
            else:
                print(f"✅ '{cadena}' -> {mi_resultado} (coinciden)")
        
        # Verificar que no hay diferencias
        self.assertEqual(len(diferencias), 0, 
                        f"Diferencias encontradas: {diferencias}")
        
        print(f"🎉 Todas las {len(self.cadenas_prueba)} cadenas procesadas coinciden")
    
    def test_procesar_cadena_par_as(self):
        """Comparar procesamiento de cadenas - AFD número par de 'a's"""
        print("\n=== Test Comparativo: AFD número par de 'a's ===")
        
        diferencias = []
        
        for cadena in self.cadenas_prueba:
            # Resultado de nuestra implementación
            mi_resultado = self.mi_afd_par_as.procesar_cadena(cadena)
            
            # Resultado de automata-lib
            lib_resultado = self.automata_lib_par_as.accepts_input(cadena)
            
            # Comparar resultados
            if mi_resultado != lib_resultado:
                diferencias.append(f"'{cadena}': Mi={mi_resultado}, Lib={lib_resultado}")
            else:
                print(f"✅ '{cadena}' -> {mi_resultado} (coinciden)")
        
        # Verificar que no hay diferencias
        self.assertEqual(len(diferencias), 0, 
                        f"Diferencias encontradas: {diferencias}")
        
        print(f"🎉 Todas las {len(self.cadenas_prueba)} cadenas procesadas coinciden")
    
    def test_estados_alcanzables_comparativo(self):
        """Comparar estados alcanzables con automata-lib"""
        print("\n=== Test Comparativo: Estados alcanzables ===")
        
        # Nuestros estados alcanzables
        mis_alcanzables = self.mi_afd_termina_b.obtener_estados_alcanzables()
        
        # automata-lib no tiene método directo, pero podemos verificar
        # que todos los estados están realmente alcanzables
        lib_todos_estados = set(self.automata_lib_termina_b.states)
        
        # Para automata-lib, verificar si cada estado es alcanzable
        # procesando cadenas que lleven a cada estado
        lib_alcanzables = set()
        lib_alcanzables.add(self.automata_lib_termina_b.initial_state)  # Estado inicial siempre alcanzable
        
        # Probar diferentes cadenas para ver qué estados alcanza
        cadenas_exploracion = ["", "a", "b", "aa", "ab", "ba", "bb", "aaa", "aab", "aba", "abb"]
        for cadena in cadenas_exploracion:
            try:
                estado_final = self._obtener_estado_final_automata_lib(self.automata_lib_termina_b, cadena)
                lib_alcanzables.add(estado_final)
            except:
                pass  # Cadena inválida o error
        
        print(f"Mis estados alcanzables: {mis_alcanzables}")
        print(f"Estados alcanzables (lib): {lib_alcanzables}")
        
        # Verificar que coinciden
        self.assertEqual(mis_alcanzables, lib_alcanzables)
        print("✅ Estados alcanzables coinciden")
    
    def test_es_completo_comparativo(self):
        """Comparar si el AFD es completo"""
        print("\n=== Test Comparativo: AFD completo ===")
        
        # Nuestro resultado
        mi_completo = self.mi_afd_termina_b.es_completo()
        
        # automata-lib: verificar si el DFA está completamente definido
        lib_completo = self._verificar_completitud_automata_lib(self.automata_lib_termina_b)
        
        print(f"Mi implementación - es completo: {mi_completo}")
        print(f"Verificación lib - es completo: {lib_completo}")
        
        self.assertEqual(mi_completo, lib_completo)
        print("✅ Verificación de completitud coincide")
    
    def test_minimizacion_preparacion(self):
        """Test preparatorio para minimización (cuando la implementes)"""
        print("\n=== Test Comparativo: Preparación minimización ===")
        
        # Crear un AFD con estados redundantes
        afd_redundante = AFD(
            estados={'q0', 'q1', 'q2', 'q3'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q0', 'b'): 'q2',
                ('q1', 'a'): 'q3',
                ('q1', 'b'): 'q3',
                ('q2', 'a'): 'q3',
                ('q2', 'b'): 'q3',
                ('q3', 'a'): 'q3',
                ('q3', 'b'): 'q3'
            },
            estado_inicial='q0',
            estados_finales={'q3'}
        )
        
        # Crear equivalente en automata-lib
        lib_redundante = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': 'q1', 'b': 'q2'},
                'q1': {'a': 'q3', 'b': 'q3'},
                'q2': {'a': 'q3', 'b': 'q3'},
                'q3': {'a': 'q3', 'b': 'q3'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        
        # Verificar que procesan cadenas igual ANTES de minimizar
        cadenas_test = ["aa", "ab", "ba", "bb", "aaa", "bbb"]
        for cadena in cadenas_test:
            mi_resultado = afd_redundante.procesar_cadena(cadena)
            lib_resultado = lib_redundante.accepts_input(cadena)
            self.assertEqual(mi_resultado, lib_resultado, 
                           f"Diferencia en '{cadena}' antes de minimizar")
        
        print("✅ AFD redundante procesa igual que automata-lib")
        
        # TODO: Cuando implementes minimización, agregar:
        # afd_minimizado = minimizar(afd_redundante)
        # lib_minimizado = lib_redundante.minify()
        # # Comparar que ambos minimizan al mismo número de estados
    
    def _obtener_estado_final_automata_lib(self, dfa, cadena):
        """Función auxiliar para obtener el estado final tras procesar una cadena"""
        estado_actual = dfa.initial_state
        for simbolo in cadena:
            if simbolo in dfa.input_symbols:
                estado_actual = dfa.transitions[estado_actual][simbolo]
            else:
                raise ValueError(f"Símbolo {simbolo} no válido")
        return estado_actual
    
    def _verificar_completitud_automata_lib(self, dfa):
        """Función auxiliar para verificar si un DFA de automata-lib es completo"""
        for estado in dfa.states:
            for simbolo in dfa.input_symbols:
                if estado not in dfa.transitions or simbolo not in dfa.transitions[estado]:
                    return False
        return True
    
    def _alcanzables_automata_lib(self, automaton):
        """
        Calcula los estados alcanzables de un DFA o NFA de automata-lib manualmente (BFS).
        """
        visitados = set()
        por_visitar = [automaton.initial_state]
        while por_visitar:
            actual = por_visitar.pop()
            if actual not in visitados:
                visitados.add(actual)
                transiciones = automaton.transitions.get(actual, {})
                for destinos in transiciones.values():
                    # Para DFA, destinos es un string; para NFA, es un set
                    if isinstance(destinos, set):
                        for d in destinos:
                            if d not in visitados:
                                por_visitar.append(d)
                    else:
                        if destinos not in visitados:
                            por_visitar.append(destinos)
        return visitados

    def test_casos_extremos_comparativo(self):
        """Test de casos extremos comparativo"""
        print("\n=== Test Comparativo: Casos extremos ===")
        
        casos_extremos = [
            "",           # cadena vacía
            "a" * 100,    # cadena muy larga de 'a's
            "b" * 100,    # cadena muy larga de 'b's
            "ab" * 50,    # patrón repetido
            "ba" * 50,    # patrón repetido alternativo
        ]
        
        for cadena in casos_extremos:
            # Test en AFD termina en 'b'
            mi_resultado = self.mi_afd_termina_b.procesar_cadena(cadena)
            lib_resultado = self.automata_lib_termina_b.accepts_input(cadena)
            self.assertEqual(mi_resultado, lib_resultado, 
                           f"Diferencia en caso extremo '{cadena[:10]}...'")
            
            # Test en AFD número par de 'a's
            mi_resultado2 = self.mi_afd_par_as.procesar_cadena(cadena)
            lib_resultado2 = self.automata_lib_par_as.accepts_input(cadena)
            self.assertEqual(mi_resultado2, lib_resultado2, 
                           f"Diferencia en caso extremo '{cadena[:10]}...' (par 'a's)")
        
        print("✅ Todos los casos extremos coinciden")
    
    def test_estados_inalcanzables_comparativo(self):
        """
        Compara los estados inalcanzables entre la implementación propia y automata-lib (DFA y NFA)
        """
        print("\n=== Test Comparativo: Estados inalcanzables ===")
        
        # AFD de ejemplo COMPLETO (con estado pozo)
        afd = AFD(
            estados={'q0', 'q1', 'q2', 'q3', 'qx'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q0', 'b'): 'qx',
                ('q1', 'a'): 'qx',
                ('q1', 'b'): 'q2',
                ('q2', 'a'): 'q3',
                ('q2', 'b'): 'qx',
                ('q3', 'a'): 'qx',
                ('q3', 'b'): 'q0',
                ('qx', 'a'): 'qx',
                ('qx', 'b'): 'qx',
            },
            estado_inicial='q0',
            estados_finales={'q2'}
        )
        # Automata-lib DFA equivalente
        dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'qx'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': 'q1', 'b': 'qx'},
                'q1': {'a': 'qx', 'b': 'q2'},
                'q2': {'a': 'q3', 'b': 'qx'},
                'q3': {'a': 'qx', 'b': 'q0'},
                'qx': {'a': 'qx', 'b': 'qx'},
            },
            initial_state='q0',
            final_states={'q2'}
        )
        # Estados alcanzables (propio)
        propios = afd.obtener_estados_alcanzables()
        # Estados inalcanzables (propio)
        propios_inalcanzables = afd.estados - propios
        # Estados alcanzables (automata-lib, calculado manualmente)
        lib_alcanzables = self._alcanzables_automata_lib(dfa)
        lib_inalcanzables = set(dfa.states) - lib_alcanzables
        self.assertEqual(propios_inalcanzables, lib_inalcanzables)

        # NFA de ejemplo (sin lambda, verificamos solo nuestra implementación)
        afnd = AFND(
            estados={'p0', 'p1', 'p2', 'p3'},
            alfabeto={'a', 'b'},
            transiciones={
                ('p0', 'a'): {'p1'},
                ('p1', 'a'): {'p2'},
                ('p2', 'b'): {'p3'},
            },
            estado_inicial='p0',
            estados_finales={'p3'}
        )
        propios_afnd = afnd.obtener_estados_alcanzables()
        # Verificamos que encuentra todos los estados alcanzables
        self.assertEqual(propios_afnd, {'p0', 'p1', 'p2', 'p3'})
        # Estados inalcanzables (ninguno en este caso)
        propios_inalcanzables_afnd = afnd.estados - propios_afnd
        self.assertEqual(propios_inalcanzables_afnd, set())

def ejecutar_tests_comparativos():
    """Función para ejecutar tests comparativos"""
    if not AUTOMATA_LIB_DISPONIBLE:
        print("❌ No se puede ejecutar tests comparativos: automata-lib no disponible")
        print("   Instala con: pip install automata-lib")
        return False
    
    print("🔬 EJECUTANDO TESTS COMPARATIVOS CON AUTOMATA-LIB")
    print("=" * 60)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestComparativoAutomataLib)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Resumen
    print("\n" + "=" * 60)
    if resultado.wasSuccessful():
        print("🎉 ¡TODOS LOS TESTS COMPARATIVOS PASARON!")
        print("   Tu implementación funciona igual que automata-lib")
        print("   ✅ Algoritmos verificados contra librería estándar")
    else:
        print("❌ ALGUNOS TESTS COMPARATIVOS FALLARON")
        print(f"   Errores: {len(resultado.errors)}")
        print(f"   Fallos: {len(resultado.failures)}")
        print("   🔍 Revisa las diferencias reportadas arriba")
    
    return resultado.wasSuccessful()


if __name__ == "__main__":
    ejecutar_tests_comparativos()
