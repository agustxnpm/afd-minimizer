"""
Tests para la clase AFD
Prueba todas las funciones implementadas de forma clara y detallada
"""
import unittest
import sys
import os

# Agregar el directorio src al path para poder importar
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.afd import AFD


class TestAFD(unittest.TestCase):
    """Tests para la clase AFD"""
    
    def setUp(self):
        """
        Se ejecuta antes de cada test.
        Crea AFDs de ejemplo para usar en las pruebas.
        """
        # AFD simple que acepta cadenas que terminan en 'b'
        self.afd_simple = AFD(
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
        
        # AFD incompleto (le faltan transiciones)
        self.afd_incompleto = AFD(
            estados={'q0', 'q1', 'q2'},
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q0', 'b'): 'q2',
                # Faltan transiciones desde q1 y q2
            },
            estado_inicial='q0',
            estados_finales={'q2'}
        )
        
        # AFD con estados inalcanzables
        self.afd_con_inalcanzables = AFD(
            estados={'q0', 'q1', 'q2', 'q3'},  # q3 es inalcanzable
            alfabeto={'a', 'b'},
            transiciones={
                ('q0', 'a'): 'q1',
                ('q0', 'b'): 'q2',
                ('q1', 'a'): 'q1',
                ('q1', 'b'): 'q2',
                ('q2', 'a'): 'q1',
                ('q2', 'b'): 'q2',
                # q3 no es alcanzable desde q0
                ('q3', 'a'): 'q3',
                ('q3', 'b'): 'q3'
            },
            estado_inicial='q0',
            estados_finales={'q2'}
        )
    
    def test_constructor(self):
        """Test del constructor __init__"""
        print("\n=== Test Constructor ===")
        
        # Verificar que los atributos se asignan correctamente
        self.assertEqual(self.afd_simple.estados, {'q0', 'q1'})
        self.assertEqual(self.afd_simple.alfabeto, {'a', 'b'})
        self.assertEqual(self.afd_simple.estado_inicial, 'q0')
        self.assertEqual(self.afd_simple.estados_finales, {'q1'})
        self.assertEqual(len(self.afd_simple.transiciones), 4)
        
        print("✅ Constructor funciona correctamente")
    
    def test_es_completo(self):
        """Test de la función es_completo"""
        print("\n=== Test es_completo ===")
        
        # El AFD simple debe ser completo
        self.assertTrue(self.afd_simple.es_completo())
        print("✅ AFD completo detectado correctamente")
        
        # El AFD incompleto debe retornar False
        self.assertFalse(self.afd_incompleto.es_completo())
        print("✅ AFD incompleto detectado correctamente")
        
        # Crear AFD vacío para edge case
        afd_vacio = AFD(set(), set(), {}, '', set())
        self.assertTrue(afd_vacio.es_completo())  # Vacío es completo trivialmente
        print("✅ AFD vacío manejado correctamente")
    
    def test_procesar_cadena(self):
        """Test de la función procesar_cadena"""
        print("\n=== Test procesar_cadena ===")
        
        # Cadenas que deben ser aceptadas (terminan en 'b')
        cadenas_aceptadas = ["b", "ab", "aab", "abb", "aabb", "bab"]
        for cadena in cadenas_aceptadas:
            resultado = self.afd_simple.procesar_cadena(cadena)
            self.assertTrue(resultado, f"Cadena '{cadena}' debería ser aceptada")
            print(f"✅ Cadena '{cadena}' aceptada correctamente")
        
        # Cadenas que deben ser rechazadas (terminan en 'a' o vacía)
        cadenas_rechazadas = ["", "a", "aa", "ba", "aba", "abba"]
        for cadena in cadenas_rechazadas:
            resultado = self.afd_simple.procesar_cadena(cadena)
            self.assertFalse(resultado, f"Cadena '{cadena}' debería ser rechazada")
            print(f"✅ Cadena '{cadena}' rechazada correctamente")
        
        # Test con símbolos no válidos
        self.assertFalse(self.afd_simple.procesar_cadena("abc"))  # 'c' no está en alfabeto
        print("✅ Símbolo inválido rechazado correctamente")
    
    def test_obtener_estados_alcanzables(self):
        """Test de la función obtener_estados_alcanzables"""
        print("\n=== Test obtener_estados_alcanzables ===")
        
        # AFD simple: todos los estados son alcanzables
        alcanzables_simple = self.afd_simple.obtener_estados_alcanzables()
        self.assertEqual(alcanzables_simple, {'q0', 'q1'})
        print(f"✅ Estados alcanzables AFD simple: {alcanzables_simple}")
        
        # AFD incompleto: algunos estados pueden no ser alcanzables por transiciones faltantes
        alcanzables_incompleto = self.afd_incompleto.obtener_estados_alcanzables()
        # Desde q0 puedes llegar a q1 y q2, pero no hay transiciones desde q1 ni q2
        self.assertIn('q0', alcanzables_incompleto)  # Siempre incluye estado inicial
        print(f"✅ Estados alcanzables AFD incompleto: {alcanzables_incompleto}")
        
        # AFD con inalcanzables: q3 no debe estar en el resultado
        alcanzables_con_inalcanzables = self.afd_con_inalcanzables.obtener_estados_alcanzables()
        self.assertEqual(alcanzables_con_inalcanzables, {'q0', 'q1', 'q2'})
        self.assertNotIn('q3', alcanzables_con_inalcanzables)
        print(f"✅ Estados alcanzables (sin q3): {alcanzables_con_inalcanzables}")
    
    def test_to_dict(self):
        """Test de la función to_dict"""
        print("\n=== Test to_dict ===")
        
        resultado = self.afd_simple.to_dict()
        
        # Verificar estructura del diccionario
        self.assertIn("tipo", resultado)
        self.assertIn("estados", resultado)
        self.assertIn("alfabeto", resultado)
        self.assertIn("transiciones", resultado)
        self.assertIn("estado_inicial", resultado)
        self.assertIn("estados_finales", resultado)
        
        # Verificar valores
        self.assertEqual(resultado["tipo"], "AFD")
        self.assertEqual(set(resultado["estados"]), {'q0', 'q1'})
        self.assertEqual(set(resultado["alfabeto"]), {'a', 'b'})
        self.assertEqual(resultado["estado_inicial"], 'q0')
        self.assertEqual(set(resultado["estados_finales"]), {'q1'})
        
        # Verificar transiciones
        self.assertEqual(len(resultado["transiciones"]), 4)
        for trans in resultado["transiciones"]:
            self.assertIn("origen", trans)
            self.assertIn("simbolo", trans)
            self.assertIn("destino", trans)
        
        print("✅ Serialización to_dict funciona correctamente")
        print(f"   Estructura generada: {list(resultado.keys())}")
    
    def test_from_dict(self):
        """Test de la función from_dict"""
        print("\n=== Test from_dict ===")
        
        # Crear diccionario de prueba
        data = {
            "tipo": "AFD",
            "estados": ["q0", "q1", "q2"],
            "alfabeto": ["a", "b"],
            "transiciones": [
                {"origen": "q0", "simbolo": "a", "destino": "q1"},
                {"origen": "q0", "simbolo": "b", "destino": "q2"},
                {"origen": "q1", "simbolo": "a", "destino": "q1"},
                {"origen": "q1", "simbolo": "b", "destino": "q2"},
                {"origen": "q2", "simbolo": "a", "destino": "q1"},
                {"origen": "q2", "simbolo": "b", "destino": "q2"}
            ],
            "estado_inicial": "q0",
            "estados_finales": ["q2"]
        }
        
        # Crear AFD desde diccionario
        afd_reconstruido = AFD.from_dict(data)
        
        # Verificar que se reconstruyó correctamente
        self.assertEqual(afd_reconstruido.estados, {'q0', 'q1', 'q2'})
        self.assertEqual(afd_reconstruido.alfabeto, {'a', 'b'})
        self.assertEqual(afd_reconstruido.estado_inicial, 'q0')
        self.assertEqual(afd_reconstruido.estados_finales, {'q2'})
        self.assertEqual(len(afd_reconstruido.transiciones), 6)
        
        # Verificar que las transiciones se reconstruyeron bien
        self.assertEqual(afd_reconstruido.transiciones[('q0', 'a')], 'q1')
        self.assertEqual(afd_reconstruido.transiciones[('q0', 'b')], 'q2')
        
        print("✅ Deserialización from_dict funciona correctamente")
    
    def test_serialization_roundtrip(self):
        """Test de serialización ida y vuelta (to_dict -> from_dict)"""
        print("\n=== Test Serialización Completa ===")
        
        # Convertir AFD a diccionario y luego de vuelta a AFD
        data = self.afd_simple.to_dict()
        afd_reconstruido = AFD.from_dict(data)
        
        # Verificar que son equivalentes
        self.assertEqual(afd_reconstruido.estados, self.afd_simple.estados)
        self.assertEqual(afd_reconstruido.alfabeto, self.afd_simple.alfabeto)
        self.assertEqual(afd_reconstruido.estado_inicial, self.afd_simple.estado_inicial)
        self.assertEqual(afd_reconstruido.estados_finales, self.afd_simple.estados_finales)
        self.assertEqual(afd_reconstruido.transiciones, self.afd_simple.transiciones)
        
        # Verificar que procesan cadenas igual
        cadenas_test = ["", "a", "b", "ab", "ba", "aab", "abb"]
        for cadena in cadenas_test:
            resultado_original = self.afd_simple.procesar_cadena(cadena)
            resultado_reconstruido = afd_reconstruido.procesar_cadena(cadena)
            self.assertEqual(resultado_original, resultado_reconstruido,
                           f"Diferencia en procesamiento de '{cadena}'")
        
        print("✅ Serialización ida y vuelta funciona perfectamente")
    
    def test_str_repr(self):
        """Test de las funciones __str__ y __repr__"""
        print("\n=== Test __str__ y __repr__ ===")
        
        # Test __str__
        str_result = str(self.afd_simple)
        self.assertIn("AFD", str_result)
        self.assertIn("estados=2", str_result)
        print(f"✅ __str__: {str_result}")
        
        # Test __repr__
        repr_result = repr(self.afd_simple)
        self.assertIn("AFD", repr_result)
        self.assertIn("estados=", repr_result)
        self.assertIn("alfabeto=", repr_result)
        print(f"✅ __repr__: {repr_result}")


def ejecutar_tests():
    """Función para ejecutar todos los tests con salida detallada"""
    print("🧪 EJECUTANDO TESTS PARA LA CLASE AFD")
    print("=" * 50)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAFD)
    
    # Ejecutar tests con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Resumen final
    print("\n" + "=" * 50)
    if resultado.wasSuccessful():
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print(f"   Total ejecutados: {resultado.testsRun}")
        print("   La clase AFD está funcionando correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print(f"   Errores: {len(resultado.errors)}")
        print(f"   Fallos: {len(resultado.failures)}")
    
    return resultado.wasSuccessful()


if __name__ == "__main__":
    # Ejecutar tests cuando se ejecuta el archivo directamente
    ejecutar_tests()
