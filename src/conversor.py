"""
Clase para convertir AFND a AFD
"""
from typing import Dict, Set, List, Tuple
try:
    from .afd import AFD
    from .afnd import AFND
except ImportError:
    from afd import AFD
    from afnd import AFND


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
            
        Raises:
            ValueError: Si el conjunto de estados está vacío
        """
        # Si el conjunto está vacío, lanzar error
        if not conjunto_estados:
            raise ValueError("No se puede generar nombre para conjunto de estados vacío")
        
        # Ordenar los estados alfabéticamente y unir con guiones bajos
        estados_ordenados = sorted(conjunto_estados)
        return "_".join(estados_ordenados)
    
    def clausura_epsilon_conjunto(self, estados: Set[str]) -> Set[str]:
        """
        Calcula la clausura epsilon (lambda) de un conjunto de estados
        
        Esta función es fundamental en el algoritmo de construcción de subconjuntos,
        ya que determina todos los estados alcanzables sin consumir símbolos de entrada.
        
        Args:
            estados: Conjunto de estados del AFND. Puede estar vacío.
            
        Returns:
            Conjunto de estados que incluye el conjunto original más todos los estados
            alcanzables mediante transiciones lambda (ε-transiciones).
            
        Raises:
            ValueError: Si algún estado en el conjunto no existe en el AFND.
            TypeError: Si el argumento no es un conjunto de strings.
            
        Examples:
            >>> afnd = AFND(...)
            >>> conversor = ConversorAFND(afnd)
            >>> clausura = conversor.clausura_epsilon_conjunto({'q0'})
            # Retorna {'q0'} si no hay transiciones lambda desde q0
        """
        # Validación de tipo
        if not isinstance(estados, set):
            raise TypeError("El argumento 'estados' debe ser un conjunto (set)")
        
        # Validación de contenido: todos deben ser strings
        if not all(isinstance(estado, str) for estado in estados):
            raise TypeError("Todos los estados deben ser strings")
        
        # Validación: todos los estados deben existir en el AFND
        estados_invalidos = estados - self.afnd.estados
        if estados_invalidos:
            raise ValueError(f"Estados no válidos en el AFND: {estados_invalidos}")
        
        # Si el conjunto está vacío, retornar vacío (caso válido)
        if not estados:
            return set()
        
        # Calcular clausura usando la función existente de AFND
        return self.afnd.clausura_lambda(estados)
    
    def mover(self, estados: Set[str], simbolo: str) -> Set[str]:
        """
        Calcula el conjunto de estados alcanzables desde un conjunto de estados
        con un símbolo específico (función 'mover' del algoritmo de subconjuntos).
        
        Para cada estado en el conjunto origen, encuentra todos los estados destino
        alcanzables mediante transiciones con el símbolo dado. No incluye clausura epsilon.
        
        Args:
            estados: Conjunto de estados origen del AFND. No puede estar vacío.
            simbolo: Símbolo de transición del alfabeto.
            
        Returns:
            Conjunto de estados destino alcanzables directamente con el símbolo.
            Puede estar vacío si no hay transiciones.
            
        Raises:
            TypeError: Si los argumentos no tienen el tipo correcto.
            ValueError: Si algún estado no existe en el AFND o el símbolo no está en el alfabeto.
            
        Examples:
            >>> afnd = AFND(..., transiciones={('q0', 'a'): {'q1', 'q2'}})
            >>> conversor = ConversorAFND(afnd)
            >>> mover = conversor.mover({'q0'}, 'a')  # {'q1', 'q2'}
        """
        # Validación de tipos
        if not isinstance(estados, set):
            raise TypeError("El argumento 'estados' debe ser un conjunto (set)")
        if not isinstance(simbolo, str):
            raise TypeError("El argumento 'simbolo' debe ser un string")
        
        # Validación de contenido
        if not all(isinstance(estado, str) for estado in estados):
            raise TypeError("Todos los estados deben ser strings")
        
        # Validación de dominio
        if simbolo not in self.afnd.alfabeto:
            raise ValueError(f"Símbolo '{simbolo}' no pertenece al alfabeto del AFND")
        
        estados_invalidos = estados - self.afnd.estados
        if estados_invalidos:
            raise ValueError(f"Estados no válidos en el AFND: {estados_invalidos}")
        
        # Validación de lógica
        if not estados:
            raise ValueError("El conjunto de estados origen no puede estar vacío")
        
        # Calcular el conjunto de estados destino
        destinos = set()
        for estado in estados:
            # Buscar transiciones desde este estado con el símbolo dado
            clave_transicion = (estado, simbolo)
            if clave_transicion in self.afnd.transiciones:
                # Agregar todos los estados destino (maneja no-determinismo)
                destinos.update(self.afnd.transiciones[clave_transicion])
        
        return destinos
    
    def convertir_a_afd(self) -> AFD:
        """
        Convierte el AFND a AFD usando el algoritmo de construcción de subconjuntos.
        
        Este método implementa el algoritmo clásico de Rabin-Scott para eliminar
        el no-determinismo de un AFND, creando un AFD equivalente que acepta
        el mismo lenguaje.
        
        Algoritmo:
        1. Estado inicial del AFD: clausura epsilon del estado inicial del AFND
        2. Para cada estado del AFD (conjunto de estados AFND):
           - Para cada símbolo del alfabeto:
             - Calcular mover(conjunto, símbolo)
             - Calcular clausura epsilon del resultado
             - Crear nuevo estado del AFD si no existe
        3. Estados finales: conjuntos que contienen estados finales del AFND
        
        Returns:
            AFD equivalente al AFND original.
            
        Raises:
            ValueError: Si el AFND no tiene estados, alfabeto o estado inicial válido.
            
        Note:
            La complejidad temporal es O(2^n * |alfabeto| * |transiciones|),
            donde n es el número de estados del AFND.
        """
        # Validaciones previas
        if not self.afnd.estados:
            raise ValueError("El AFND debe tener al menos un estado")
        if not self.afnd.alfabeto:
            raise ValueError("El AFND debe tener alfabeto no vacío")
        if self.afnd.estado_inicial not in self.afnd.estados:
            raise ValueError(f"Estado inicial '{self.afnd.estado_inicial}' no existe en los estados del AFND")
        
        # Limpiar estado interno
        self.estados_afd = {}
        self.contador_estados = 0
        
        # Paso 1: Calcular estado inicial del AFD
        estado_inicial_afnd = self.clausura_epsilon_conjunto({self.afnd.estado_inicial})
        estado_inicial_afd = self.generar_nombre_estado(frozenset(estado_inicial_afnd))
        self.estados_afd[frozenset(estado_inicial_afnd)] = estado_inicial_afd
        
        # Cola de estados por procesar (conjuntos de estados AFND)
        por_procesar = [frozenset(estado_inicial_afnd)]
        procesados = set()
        
        # Diccionario para construir transiciones del AFD: (estado_afd, simbolo) -> estado_afd_destino
        transiciones_afd = {}
        
        # Paso 2: Construir todos los estados del AFD
        while por_procesar:
            conjunto_actual = por_procesar.pop(0)
            
            # Evitar procesar el mismo conjunto múltiples veces
            if conjunto_actual in procesados:
                continue
            procesados.add(conjunto_actual)
            
            estado_afd_actual = self.estados_afd[conjunto_actual]
            
            # Para cada símbolo del alfabeto
            for simbolo in self.afnd.alfabeto:
                # Calcular mover(conjunto_actual, simbolo)
                estados_mover = self.mover(set(conjunto_actual), simbolo)
                
                # Calcular clausura epsilon del resultado
                conjunto_destino = frozenset(self.clausura_epsilon_conjunto(estados_mover))
                
                # Si el conjunto destino no está vacío o es nuevo
                if conjunto_destino not in self.estados_afd:
                    if conjunto_destino:  # Solo crear estado si no está vacío
                        nombre_destino = self.generar_nombre_estado(conjunto_destino)
                        self.estados_afd[conjunto_destino] = nombre_destino
                        por_procesar.append(conjunto_destino)
                    else:
                        # Conjunto vacío: no crear estado, pero registrar transición a estado pozo
                        # Para simplificar, omitimos transiciones a vacío (el AFD será completo)
                        continue
                
                # Registrar transición del AFD
                if conjunto_destino:
                    estado_afd_destino = self.estados_afd[conjunto_destino]
                    transiciones_afd[(estado_afd_actual, simbolo)] = estado_afd_destino
        
        # Paso 3: Determinar estados finales del AFD
        estados_finales_afd = set()
        for conjunto, nombre_estado in self.estados_afd.items():
            # Si el conjunto contiene al menos un estado final del AFND
            if conjunto & self.afnd.estados_finales:
                estados_finales_afd.add(nombre_estado)
        
        # Paso 4: Crear y retornar el AFD
        # Convertir transiciones a formato esperado por AFD
        transiciones_afd_dict = {}
        for (estado_origen, simbolo), estado_destino in transiciones_afd.items():
            if (estado_origen, simbolo) not in transiciones_afd_dict:
                transiciones_afd_dict[(estado_origen, simbolo)] = estado_destino
        
        # Crear conjunto de estados del AFD
        estados_afd_final = set(self.estados_afd.values())
        
        return AFD(
            estados=estados_afd_final,
            alfabeto=self.afnd.alfabeto.copy(),
            transiciones=transiciones_afd_dict,
            estado_inicial=estado_inicial_afd,
            estados_finales=estados_finales_afd
        )
    
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
            "tiene_epsilon": self.afnd.tiene_transiciones_lambda()
        }
