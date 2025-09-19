"""
Clase para convertir AFND a AFD
"""
from typing import Dict, Set, List, Tuple
from .afd import AFD
from .afnd import AFND


class ConversorAFND:
    """
    Se encarga de convertir un AFND a AFD usando el algoritmo de construcción de subconjuntos
    """
    
    def __init__(self, afnd: AFND):
        """
        Inicializa el conversor con un AFND
        
        Args:
            afnd: Autómata Finito No Determinístico a convertir
        """
        self.afnd = afnd
        self.estados_afd = {}  # Mapeo de conjunto de estados AFND -> estado AFD
        self.contador_estados = 0
    
    def generar_nombre_estado(self, conjunto_estados: frozenset) -> str:
        """
        Genera un nombre único para un conjunto de estados del AFND
        
        Args:
            conjunto_estados: Conjunto de estados del AFND
            
        Returns:
            Nombre del nuevo estado para el AFD
        """
        # TODO: Implementar lógica
        pass
    
    def clausura_epsilon_conjunto(self, estados: Set[str]) -> Set[str]:
        """
        Calcula la clausura epsilon de un conjunto de estados
        
        Args:
            estados: Conjunto de estados
            
        Returns:
            Clausura epsilon del conjunto
        """
        # TODO: Implementar lógica
        pass
    
    def mover(self, estados: Set[str], simbolo: str) -> Set[str]:
        """
        Calcula el conjunto de estados alcanzables desde un conjunto de estados
        con un símbolo específico
        
        Args:
            estados: Conjunto de estados origen
            simbolo: Símbolo de transición
            
        Returns:
            Conjunto de estados destino
        """
        # TODO: Implementar lógica
        pass
    
    def convertir_a_afd(self) -> AFD:
        """
        Convierte el AFND a AFD usando el algoritmo de construcción de subconjuntos
        
        Returns:
            AFD equivalente al AFND
        """
        # TODO: Implementar algoritmo de construcción de subconjuntos
        pass
    
    def obtener_estadisticas_conversion(self) -> Dict:
        """
        Obtiene estadísticas del proceso de conversión
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "estados_afnd": len(self.afnd.estados),
            "estados_afd": len(self.estados_afd),
            "factor_expansion": len(self.estados_afd) / len(self.afnd.estados) if len(self.afnd.estados) > 0 else 0,
            "tiene_epsilon": self.afnd.tiene_transiciones_epsilon()
        }
