"""
Tests para la clase MinimizadorAFD
"""
import unittest
from src.afd import AFD
from src.afnd import AFND
from src.conversor import ConversorAFND
from src.minimizador import MinimizadorAFD

try:
    from automata.fa.dfa import DFA
    from automata.fa.nfa import NFA
    automata_lib_disponible = True
except ImportError:
    automata_lib_disponible = False


class TestMinimizadorAFD(unittest.TestCase):
    """Tests para el minimizador de AFD"""

    def test_minimizacion_simple(self):
        """
        Test de minimización básica
        """
        # AFD con estados redundantes
        afd = AFD(
            estados={'q0', 'q1', 'q2', 'q3'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q0', 'b'): 'q2',
                ('q1', 'a'): 'q1',
                ('q1', 'b'): 'q2',
                ('q2', 'a'): 'q1',
                ('q2', 'b'): 'q2',
                ('q3', 'a'): 'q1',
                ('q3', 'b'): 'q2',  # q3 es redundante
            },
            estado_inicial='q0',
            estados_finales={'q1', 'q3'}  # q3 es equivalente a q1
        )

        minimizador = MinimizadorAFD(afd)
        afd_minimizado = minimizador.minimizar()

        # Verificar que el AFD minimizado tenga menos estados
        self.assertLess(len(afd_minimizado.estados), len(afd.estados))

        # Verificar equivalencia: ambos deben aceptar las mismas cadenas
        cadenas_prueba = ["", "a", "b", "aa", "ab", "ba", "bb"]
        for cadena in cadenas_prueba:
            resultado_original = afd.procesar_cadena(cadena)
            resultado_minimizado = afd_minimizado.procesar_cadena(cadena)
            self.assertEqual(resultado_original, resultado_minimizado,
                f"Cadena '{cadena}': Original={resultado_original}, Minimizado={resultado_minimizado}")

    def test_minimizacion_vs_automata_lib(self):
        """
        Test comparativo de minimización con automata-lib
        """
        if not automata_lib_disponible:
            self.skipTest("automata-lib no está disponible")

        # Crear un AFND simple: acepta cadenas que terminan en 'a'
        afnd = AFND(
            estados={'q0', 'q1'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): {'q1'},
                ('q0', 'b'): {'q0'},
                ('q1', 'a'): {'q1'},
                ('q1', 'b'): {'q0'},
            },
            estado_inicial='q0',
            estados_finales={'q1'}  # Termina en 'a'
        )

        # NFA equivalente en automata-lib
        nfa = NFA(
            states={'q0', 'q1'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q1'}, 'b': {'q0'}},
                'q1': {'a': {'q1'}, 'b': {'q0'}},
            },
            initial_state='q0',
            final_states={'q1'}
        )

        # Convertir y minimizar con nuestro código
        conversor = ConversorAFND(afnd)
        afd_convertido = conversor.convertir_a_afd()
        minimizador = MinimizadorAFD(afd_convertido)
        afd_minimizado_propio = minimizador.minimizar()

        # Obtener DFA minimizado de automata-lib
        dfa_minimizado_lib = DFA.from_nfa(nfa, minify=True)

        # Comparar aceptación de cadenas
        cadenas_prueba = [
            "", "a", "b", "aa", "ab", "ba", "bb"
        ]

        for cadena in cadenas_prueba:
            with self.subTest(cadena=cadena):
                resultado_propio = afd_minimizado_propio.procesar_cadena(cadena)
                resultado_lib = dfa_minimizado_lib.accepts_input(cadena)
                self.assertEqual(resultado_propio, resultado_lib,
                    f"Minimización diferente: cadena '{cadena}', Propio={resultado_propio}, Lib={resultado_lib}")

    def test_estadisticas_minimizacion(self):
        """
        Test de las estadísticas de minimización
        """
        # AFD con redundancias
        afd = AFD(
            estados={'q0', 'q1', 'q2', 'q3', 'q4'},
            alfabeto={'a'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q1', 'a'): 'q2',
                ('q2', 'a'): 'q3',
                ('q3', 'a'): 'q4',
                ('q4', 'a'): 'q4',  # Estado final absorbente
            },
            estado_inicial='q0',
            estados_finales={'q4'}
        )

        minimizador = MinimizadorAFD(afd)
        afd_minimizado = minimizador.minimizar()
        estadisticas = minimizador.obtener_estadisticas_minimizacion()

        # Verificar estadísticas
        self.assertEqual(estadisticas['estados_originales'], len(afd.estados))
        self.assertLessEqual(estadisticas['estados_minimizados'], estadisticas['estados_originales'])
        self.assertGreaterEqual(estadisticas['reduccion_porcentual'], 0.0)
        self.assertLessEqual(estadisticas['reduccion_porcentual'], 100.0)

    def test_tabla_equivalencias(self):
        """
        Test de la tabla de equivalencias
        """
        afd = AFD(
            estados={'q0', 'q1', 'q2'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q0', 'b'): 'q1',
                ('q1', 'a'): 'q2',
                ('q1', 'b'): 'q2',
                ('q2', 'a'): 'q2',
                ('q2', 'b'): 'q2',
            },
            estado_inicial='q0',
            estados_finales={'q2'}
        )

        minimizador = MinimizadorAFD(afd)
        afd_minimizado = minimizador.minimizar()
        tabla = minimizador.generar_tabla_equivalencias()

        # Verificar que todos los estados originales estén en la tabla
        for estado in afd.estados:
            self.assertIn(estado, tabla)

        # Verificar que los valores sean estados del AFD minimizado
        for estado_minimizado in tabla.values():
            self.assertIn(estado_minimizado, afd_minimizado.estados)

    def test_minimizacion_afd_completo(self):
        """
        Test de minimización de AFD completo (sin conversion previa)
        """
        # AFD que acepta cadenas con número par de 'a's
        afd = AFD(
            estados={'par', 'impar'},
            alfabeto={'a', 'b'},
            transiciones={
                ('par', 'a'): 'impar',
                ('par', 'b'): 'par',
                ('impar', 'a'): 'par',
                ('impar', 'b'): 'impar',
            },
            estado_inicial='par',
            estados_finales={'par'}
        )

        minimizador = MinimizadorAFD(afd)
        afd_minimizado = minimizador.minimizar()

        # Este AFD ya está minimizado, debería tener los mismos estados
        self.assertEqual(len(afd_minimizado.estados), len(afd.estados))

        # Verificar equivalencia
        cadenas_prueba = ["", "a", "b", "aa", "ab", "ba", "bb", "aaa", "bbb"]
        for cadena in cadenas_prueba:
            resultado_original = afd.procesar_cadena(cadena)
            resultado_minimizado = afd_minimizado.procesar_cadena(cadena)
            self.assertEqual(resultado_original, resultado_minimizado)


if __name__ == '__main__':
    unittest.main()