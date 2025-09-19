"""
Clase para representar un Autómata Finito No Determinístico (AFND)
"""
from typing import Dict, Set, Tuple, List, Optional
from collections import deque  # Importar deque para mejorar la eficiencia

class AFND:
    """
    Representa un Autómata Finito No Determinístico
    
    Attributes:
        estados: Conjunto de estados del autómata
        alfabeto: Alfabeto de símbolos de entrada (sin incluir epsilon)
        transiciones: Función de transición representada como diccionario
        estado_inicial: Estado inicial del autómata
        estados_finales: Conjunto de estados finales/de aceptación
    """
    
    def __init__(self, 
                 estados: Set[str], 
                 alfabeto: Set[str], 
                 transiciones: Dict[Tuple[str, str], Set[str]], 
                 estado_inicial: str, 
                 estados_finales: Set[str]):
        """
        Inicializa un AFND
        
        Args:
            estados: Conjunto de estados
            alfabeto: Alfabeto de entrada (sin epsilon)
            transiciones: Diccionario de transiciones {(estado, símbolo): conjunto_estados_destino}
            estado_inicial: Estado inicial
            estados_finales: Conjunto de estados finales
        """
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales
    
    def tiene_transiciones_lambda(self) -> bool:
        """
        Verifica si el AFND tiene transiciones lambda (λ-transiciones)
                
        Returns:
            True si tiene transiciones lambda, False en caso contrario
        """
        # Recorrer todas las transiciones
        for estado_origen, simbolo in self.transiciones:
            # Verificar si el símbolo es lambda
            if simbolo == "lambda" or simbolo == "λ" or simbolo == "":
                return True
        
        return False
    
    def clausura_lambda(self, estados: Set[str]) -> Set[str]:
        """
        Calcula la clausura lambda de un conjunto de estados
        
        La clausura lambda incluye todos los estados alcanzables
        desde los estados dados usando solo transiciones lambda.
        
        Args:
            estados: Conjunto de estados inicial
            
        Returns:
            Clausura lambda del conjunto de estados
        """
        # Crear una copia del conjunto inicial
        clausura = set(estados)
        
        # Cola de estados por procesar (usando deque para BFS eficiente)
        por_procesar = deque(estados)
        
        # Procesar hasta que no haya más estados que agregar
        while por_procesar:
            estado_actual = por_procesar.popleft()
            
            # Buscar transiciones lambda desde este estado
            for (origen, simbolo), destinos in self.transiciones.items():
                if origen == estado_actual and (simbolo == "lambda" or simbolo == "λ" or simbolo == ""):
                    # Agregar estados destino que no estén ya en la clausura
                    for destino in destinos:
                        if destino not in self.estados:
                            raise ValueError(f"El estado destino {destino} no pertenece al conjunto de estados")
                        if destino not in clausura:
                            clausura.add(destino)
                            por_procesar.append(destino)
        
        return clausura
    
    def procesar_cadena(self, cadena: str) -> bool:
        """
        Procesa una cadena y determina si es aceptada por el autómata
        
        Args:
            cadena: Cadena a procesar
            
        Returns:
            True si la cadena es aceptada, False en caso contrario
        """
        # Empezar con la clausura lambda del estado inicial
        estados_actuales = self.clausura_lambda({self.estado_inicial})
        
        # Procesar cada símbolo de la cadena
        for simbolo in cadena:
            # Verificar que el símbolo esté en el alfabeto
            if simbolo not in self.alfabeto:
                return False
            
            # Conjunto de nuevos estados después de leer el símbolo
            nuevos_estados = set()
            
            # Para cada estado actual, buscar transiciones con este símbolo
            for estado in estados_actuales:
                if (estado, simbolo) in self.transiciones:
                    # Agregar todos los estados destino
                    for dest in self.transiciones[(estado, simbolo)]:
                        if dest not in self.estados:
                            raise ValueError(f"El estado destino {dest} no pertenece al conjunto de estados")
                        nuevos_estados.add(dest)
            
            # Calcular la clausura lambda de los nuevos estados
            estados_actuales = self.clausura_lambda(nuevos_estados)
            
            # Si no hay estados actuales, la cadena es rechazada
            if not estados_actuales:
                return False
        
        # Verificar si algún estado actual es final
        for estado in estados_actuales:
            if estado in self.estados_finales:
                return True
        
        # Si llegamos aquí, no hay estados finales en el conjunto actual
        return False
    
    def obtener_estados_alcanzables(self) -> Set[str]:
        """
        Obtiene el conjunto de estados alcanzables desde el estado inicial
        siguiendo solo transiciones válidas (simulación BFS sobre configuraciones).
        
        Returns:
            Conjunto de estados alcanzables
        """
        if self.estado_inicial not in self.estados:
            raise ValueError("El estado inicial no pertenece al conjunto de estados")
        
        alcanzados = set()
        # Cola de configuraciones: (conjunto de estados actuales) usando deque para eficiencia
        cola = deque([self.clausura_lambda({self.estado_inicial})])
        
        while cola:
            estados_actuales = cola.popleft()
            
            # Agregar nuevos estados a alcanzados
            for estado in estados_actuales:
                if estado not in alcanzados:
                    alcanzados.add(estado)
            
            # Para cada símbolo del alfabeto, simular transición
            for simbolo in self.alfabeto:
                nuevos_estados = set()
                for estado in estados_actuales:
                    if (estado, simbolo) in self.transiciones:
                        for dest in self.transiciones[(estado, simbolo)]:
                            if dest not in self.estados:
                                raise ValueError(f"El estado destino {dest} no pertenece al conjunto de estados")
                            nuevos_estados.add(dest)
                
                if nuevos_estados:
                    clausura_nuevos = self.clausura_lambda(nuevos_estados)
                    # Solo agregar si hay algún estado nuevo
                    if not clausura_nuevos.issubset(alcanzados):
                        cola.append(clausura_nuevos)
        
        return alcanzados
    
    def to_dict(self) -> Dict:
        """
        Convierte el AFND a un diccionario para serialización JSON
        
        Returns:
            Diccionario con la representación del AFND
        """
        transiciones_list = []
        for (origen, simbolo), destinos in self.transiciones.items():
            for destino in destinos:
                transiciones_list.append({
                    "origen": origen,
                    "simbolo": simbolo,
                    "destino": destino
                })
        
        return {
            "tipo": "AFND",
            "estados": list(self.estados),
            "alfabeto": list(self.alfabeto),
            "transiciones": transiciones_list,
            "estado_inicial": self.estado_inicial,
            "estados_finales": list(self.estados_finales)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AFND':
        """
        Crea un AFND a partir de un diccionario (deserialización JSON)
        
        Args:
            data: Diccionario con los datos del AFND
            
        Returns:
            Instancia de AFND
        """
        estados = set(data["estados"])
        alfabeto = set(data["alfabeto"])
        estados_finales = set(data["estados_finales"])
        estado_inicial = data["estado_inicial"]
        
        # Convertir transiciones de lista a diccionario con conjuntos
        transiciones = {}
        for trans in data["transiciones"]:
            key = (trans["origen"], trans["simbolo"])
            if key not in transiciones:
                transiciones[key] = set()
            transiciones[key].add(trans["destino"])
        
        return cls(estados, alfabeto, transiciones, estado_inicial, estados_finales)
    
    def __str__(self) -> str:
        """Representación en string del AFND"""
        return f"AFND(estados={len(self.estados)}, alfabeto={self.alfabeto})"
    
    def __repr__(self) -> str:
        """Representación detallada del AFND"""
        return (f"AFND(estados={self.estados}, alfabeto={self.alfabeto}, "
                f"estado_inicial={self.estado_inicial}, estados_finales={self.estados_finales})")