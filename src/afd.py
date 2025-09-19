from typing import Dict, Set, Tuple
from collections import deque  # Importar deque para mejorar la eficiencia

class AFD:
    """
    Representa un automata finito deterministico
    
    Attributes:
        estados: conjunto de estados del autómata
        alfabeto: alfabeto de símbolos de entrada
        transiciones: función de transición representada como diccionario
        estado_inicial: estado inicial del autómata
        estados_finales: conjunto de estados finales/de aceptación
    """
    
    def __init__(self, 
                 estados: Set[str], 
                 alfabeto: Set[str], 
                 transiciones: Dict[Tuple[str, str], str], 
                 estado_inicial: str, 
                 estados_finales: Set[str]):
        """
        inicializa un AFD
        
        Args:
            estados: conjunto de estados
            alfabeto: alfabeto de entrada
            transiciones: diccionario de transiciones {(estado, símbolo): estado_destino}
            estado_inicial: estado inicial
            estados_finales: conjunto de estados finales
        """
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales
    
    
    def es_completo(self) -> bool:
        """
        verifica si el autómata es completo (tiene transición para cada estado y símbolo)
        
        Returns:
            true si es completo, false en caso contrario
        """
        # para cada estado en el autómata
        for estado in self.estados:
            # para cada símbolo del alfabeto
            for simbolo in self.alfabeto:
                # verificar si existe la transición (estado, símbolo)
                transicion = (estado, simbolo)
                if transicion not in self.transiciones:
                    # si falta una transición, no es completo
                    return False
        
        return True
    
    def procesar_cadena(self, cadena: str) -> bool:
        """
        procesa una cadena y determina si es aceptada por el autómata
        
        Args:
            cadena: cadena a procesar
            
        Returns:
            true si la cadena es aceptada, false en caso contrario
        """
        # comenzar en el estado inicial
        estado_actual = self.estado_inicial
        
        # procesar cada símbolo de la cadena uno por uno
        for simbolo in cadena:
            # verificar si el símbolo está en el alfabeto
            if simbolo not in self.alfabeto:
                # si el símbolo no está en el alfabeto, rechazar
                return False
            
            # buscar la transición desde el estado actual con este símbolo
            transicion = (estado_actual, simbolo)
            
            # verificar si existe la transición
            if transicion not in self.transiciones:
                # si no hay transición definida, rechazar
                return False
            
            # ir al siguiente estado
            estado_actual = self.transiciones[transicion]
        
        # por ultimo, verificar si el estado actual es un estado final
        return estado_actual in self.estados_finales
    
    def obtener_estados_alcanzables(self) -> Set[str]:
        """
        obtiene el conjunto de estados alcanzables desde el estado inicial
        
        Returns:
            conjunto de estados alcanzables
        """
        if self.estado_inicial not in self.estados:
            raise ValueError("El estado inicial no pertenece al conjunto de estados")
        
        # conjunto para almacenar los estados visitados
        estados_alcanzables = set()
        
        # cola de estados por explorar (comienza desde estado inicial) usando deque para eficiencia
        estados_por_explorar = deque([self.estado_inicial])
        
        # mientras haya estados por explorar
        while estados_por_explorar:
            # tomar el siguiente estado de la cola (O(1) con deque)
            estado_actual = estados_por_explorar.popleft()
            
            # marcar este estado como visitado (la verificación redundante se elimina porque solo agregamos no visitados)
            if estado_actual in estados_alcanzables:
                continue  # En caso de que se agregue por error, pero no debería ocurrir
            
            estados_alcanzables.add(estado_actual)
            
            # explorar todas las transiciones desde este estado
            for simbolo in self.alfabeto:
                transicion = (estado_actual, simbolo)
                
                # si existe una transición con este símbolo
                if transicion in self.transiciones:
                    estado_destino = self.transiciones[transicion]
                    
                    # validar que el estado destino pertenece a los estados (robustez)
                    if estado_destino not in self.estados:
                        raise ValueError(f"El estado destino {estado_destino} no pertenece al conjunto de estados")
                    
                    # si el estado destino no ha sido visitado, agregarlo a la cola
                    if estado_destino not in estados_alcanzables:
                        estados_por_explorar.append(estado_destino)
                else:
                    print(f"Advertencia: No hay transición desde {estado_actual} con símbolo {simbolo}")
                    pass
        
        return estados_alcanzables
    
    def to_dict(self) -> Dict:
        """
        convierte el AFD a un diccionario para serialización JSON
        
        Returns:
            diccionario con la representación del AFD
        """
        return {
            "tipo": "AFD",
            "estados": list(self.estados),
            "alfabeto": list(self.alfabeto),
            "transiciones": [
                {
                    "origen": origen,
                    "simbolo": simbolo,
                    "destino": destino
                }
                for (origen, simbolo), destino in self.transiciones.items()
            ],
            "estado_inicial": self.estado_inicial,
            "estados_finales": list(self.estados_finales)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AFD':
        """
        crea un AFD a partir de un diccionario (deserialización JSON)
        
        Args:
            data: diccionario con los datos del AFD
            
        Returns:
            instancia de AFD
        """
        estados = set(data["estados"])
        alfabeto = set(data["alfabeto"])
        estados_finales = set(data["estados_finales"])
        estado_inicial = data["estado_inicial"]
        
        # convertir transiciones de lista a diccionario
        transiciones = {}
        for trans in data["transiciones"]:
            key = (trans["origen"], trans["simbolo"])
            transiciones[key] = trans["destino"]
        
        return cls(estados, alfabeto, transiciones, estado_inicial, estados_finales)
    
    def __str__(self) -> str:
        """Representación en string del AFD"""
        return f"AFD(estados={len(self.estados)}, alfabeto={self.alfabeto})"
    
    def __repr__(self) -> str:
        """Representación detallada del AFD"""
        return (f"AFD(estados={self.estados}, alfabeto={self.alfabeto}, "
                f"estado_inicial={self.estado_inicial}, estados_finales={self.estados_finales})")