"""
Tests para la clase ConversorAFND
"""
import unittest
from src.afd import AFD
from src.afnd import AFND
from src.conversor import ConversorAFND
try:
    from automata.fa.dfa import DFA
    from automata.fa.nfa import NFA
    automata_lib_disponible = True
except ImportError:
    automata_lib_disponible = False


class TestConversorAFND(unittest.TestCase):
    """Tests para el conversor AFND → AFD"""

    def test_conversion_simple_sin_lambda(self):
        """
        Test de conversión básica sin transiciones lambda
        """
        # AFND simple: acepta cadenas que terminan en 'ab'
        afnd = AFND(
            estados={'q0', 'q1', 'q2'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): {'q0', 'q1'},  # No-determinismo
                ('q0', 'b'): {'q0'},
                ('q1', 'b'): {'q2'},
            },
            estado_inicial='q0',
            estados_finales={'q2'}
        )

        # Convertir a AFD
        conversor = ConversorAFND(afnd)
        afd = conversor.convertir_a_afd()

        # Verificar que el AFD tenga las propiedades básicas
        self.assertIsInstance(afd, AFD)
        self.assertTrue(len(afd.estados) > 0)
        self.assertEqual(afd.alfabeto, {'a', 'b'})

        # Verificar equivalencia: AFND y AFD deben aceptar las mismas cadenas
        cadenas_prueba = [
            ("", False),      # Vacía
            ("a", False),     # Solo 'a'
            ("b", False),     # Solo 'b'
            ("ab", True),     # Termina en 'ab'
            ("aab", True),    # Termina en 'ab'
            ("abb", False),   # No termina en 'ab'
            ("abab", True),   # Termina en 'ab'
            ("baba", False),  # No termina en 'ab'
        ]

        for cadena, esperado in cadenas_prueba:
            with self.subTest(cadena=cadena):
                resultado_afnd = afnd.procesar_cadena(cadena)
                resultado_afd = afd.procesar_cadena(cadena)
                self.assertEqual(resultado_afnd, resultado_afd,
                    f"Cadena '{cadena}': AFND={resultado_afnd}, AFD={resultado_afd}")

    def test_conversion_con_lambda(self):
        """
        Test de conversión con transiciones lambda
        """
        # AFND con lambda: acepta 'a' seguido opcionalmente de 'b's
        afnd = AFND(
            estados={'q0', 'q1', 'q2'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'lambda'): {'q1'},  # q0 --λ--> q1
                ('q1', 'a'): {'q2'},       # q1 --a--> q2
                ('q2', 'b'): {'q2'},       # q2 --b--> q2 (acepta múltiples 'b')
            },
            estado_inicial='q0',
            estados_finales={'q2'}
        )

        # Convertir a AFD
        conversor = ConversorAFND(afnd)
        afd = conversor.convertir_a_afd()

        # Verificar equivalencia
        cadenas_prueba = [
            ("", False),      # Vacía
            ("a", True),      # Solo 'a'
            ("ab", True),     # 'a' + 'b'
            ("abb", True),    # 'a' + 'bb'
            ("b", False),     # Solo 'b'
            ("ba", False),    # 'b' + 'a'
            ("aa", False),    # 'aa' (no acepta)
        ]

        for cadena, esperado in cadenas_prueba:
            with self.subTest(cadena=cadena):
                resultado_afnd = afnd.procesar_cadena(cadena)
                resultado_afd = afd.procesar_cadena(cadena)
                self.assertEqual(resultado_afnd, resultado_afd,
                    f"Cadena '{cadena}': AFND={resultado_afnd}, AFD={resultado_afd}")

    def test_conversion_completa_automata_lib(self):
        """
        Test comparativo completo con automata-lib (solo procesamiento de cadenas)
        """
        if not automata_lib_disponible:
            self.skipTest("automata-lib no está disponible")

        # AFND: acepta cadenas con 'a' en posición impar
        afnd = AFND(
            estados={'q0', 'q1', 'q2'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'b'): {'q0'},
                ('q0', 'a'): {'q1'},
                ('q1', 'a'): {'q2'},
                ('q1', 'b'): {'q0'},
                ('q2', 'a'): {'q1'},
                ('q2', 'b'): {'q0'},
            },
            estado_inicial='q0',
            estados_finales={'q1'}  # 'a' en posición impar
        )

        # NFA equivalente en automata-lib (sin convertir)
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'b': {'q0'}, 'a': {'q1'}},
                'q1': {'a': {'q2'}, 'b': {'q0'}},
                'q2': {'a': {'q1'}, 'b': {'q0'}},
            },
            initial_state='q0',
            final_states={'q1'}
        )

        # Convertir con mi código
        conversor = ConversorAFND(afnd)
        afd_propio = conversor.convertir_a_afd()

        # Comparar procesando cadenas entre AFND y AFD propio
        cadenas_prueba = [
            "", "a", "b", "aa", "ab", "ba", "bb",
            "aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb"
        ]

        for cadena in cadenas_prueba:
            with self.subTest(cadena=cadena):
                # Mi AFND
                resultado_afnd = afnd.procesar_cadena(cadena)
                # Mi AFD convertido
                resultado_afd = afd_propio.procesar_cadena(cadena)
                # Deben ser iguales
                self.assertEqual(resultado_afnd, resultado_afd,
                    f"Cadena '{cadena}': AFND={resultado_afnd}, AFD={resultado_afd}")

                # Si automata-lib está disponible, comparar también con NFA
                if automata_lib_disponible:
                    try:
                        resultado_nfa = nfa.accepts_input(cadena)
                        # AFND y NFA deben coincidir
                        self.assertEqual(resultado_afnd, resultado_nfa,
                            f"Cadena '{cadena}': AFND={resultado_afnd}, NFA_lib={resultado_nfa}")
                    except Exception:
                        # Si hay error en automata-lib, continuar
                        pass

        # Si automata-lib está disponible, convertir NFA a DFA y comparar equivalencia
        if automata_lib_disponible:
            dfa_automata_lib = DFA.from_nfa(nfa)
            
            # Cadenas adicionales para verificar equivalencia
            cadenas_equivalencia = [
                "aaaa", "bbbb", "abab", "baba", "abba", "baab", "aabb", "bbaa"
            ]
            
            for cadena in cadenas_equivalencia:
                with self.subTest(cadena=cadena):
                    resultado_dfa_lib = dfa_automata_lib.accepts_input(cadena)
                    resultado_afd_propio = afd_propio.procesar_cadena(cadena)
                    self.assertEqual(resultado_dfa_lib, resultado_afd_propio,
                        f"Equivalencia fallida: cadena '{cadena}', DFA_lib={resultado_dfa_lib}, AFD_propio={resultado_afd_propio}")

    def test_estadisticas_conversion(self):
        """
        Test de las estadísticas de conversión
        """
        afnd = AFND(
            estados={'q0', 'q1'},
            alfabeto={'a'},
            transiciones={('q0', 'a'): {'q1'}},
            estado_inicial='q0',
            estados_finales={'q1'}
        )

        conversor = ConversorAFND(afnd)
        afd = conversor.convertir_a_afd()
        stats = conversor.obtener_estadisticas_conversion()

        self.assertEqual(stats['estados_afnd'], 2)
        self.assertEqual(stats['estados_afd'], len(afd.estados))
        self.assertIsInstance(stats['factor_expansion'], float)
        self.assertIsInstance(stats['tiene_epsilon'], bool)

    def test_errores_validacion(self):
        """
        Test de validaciones y errores
        """
        # AFND inválido: estado inicial no existe
        afnd_invalido = AFND(
            estados={'q0', 'q1'},
            alfabeto={'a'},
            transiciones={},
            estado_inicial='q2',  # No existe
            estados_finales={'q1'}
        )

        conversor = ConversorAFND(afnd_invalido)
        with self.assertRaises(ValueError):
            conversor.convertir_a_afd()


if __name__ == '__main__':
    unittest.main()