"""
Clase para la minimización de Autómatas Finitos Determinísticos
"""
from typing import Dict, Set, List, Tuple
from collections import deque
try:
    from .afd import AFD
except ImportError:
    from afd import AFD


class MinimizadorAFD:
    """
    Se encarga de la minimización de AFDs utilizando el algoritmo de partición
    """
    
    def __init__(self, afd: AFD):
        """
        Inicializa el minimizador con un AFD
        
        Args:
            afd: Autómata Finito Determinístico a minimizar
        """
        self.afd_original = afd  # Guardar referencia al AFD original
        self.afd = afd
        self.particiones = []
        self.estados_equivalentes = {}
    
    def eliminar_estados_inalcanzables(self) -> AFD:
        """
        Elimina los estados inalcanzables del AFD
        
        Utiliza BFS para encontrar todos los estados alcanzables desde el estado inicial.
        Los estados inalcanzables no afectan el lenguaje aceptado pero aumentan innecesariamente
        el tamaño del autómata.
        
        Returns:
            Nuevo AFD sin estados inalcanzables
            
        Raises:
            ValueError: Si el estado inicial no existe en el AFD
        """
        if self.afd.estado_inicial not in self.afd.estados:
            raise ValueError(f"Estado inicial '{self.afd.estado_inicial}' no existe en los estados del AFD")
        
        # BFS para encontrar estados alcanzables
        alcanzables = set()
        cola = deque([self.afd.estado_inicial])
        alcanzables.add(self.afd.estado_inicial)
        
        while cola:
            estado_actual = cola.popleft()
            
            # Explorar todas las transiciones desde el estado actual
            for simbolo in self.afd.alfabeto:
                clave_transicion = (estado_actual, simbolo)
                if clave_transicion in self.afd.transiciones:
                    estado_destino = self.afd.transiciones[clave_transicion]
                    if estado_destino not in alcanzables:
                        alcanzables.add(estado_destino)
                        cola.append(estado_destino)
        
        # Filtrar transiciones para incluir solo estados alcanzables
        nuevas_transiciones = {}
        for estado in alcanzables:
            for simbolo in self.afd.alfabeto:
                clave_transicion = (estado, simbolo)
                if clave_transicion in self.afd.transiciones:
                    destino = self.afd.transiciones[clave_transicion]
                    if destino in alcanzables:
                        nuevas_transiciones[clave_transicion] = destino
        
        # Filtrar estados finales para incluir solo los alcanzables
        nuevos_estados_finales = self.afd.estados_finales & alcanzables
        
        # Crear y retornar el nuevo AFD
        return AFD(
            estados=alcanzables,
            alfabeto=self.afd.alfabeto,
            transiciones=nuevas_transiciones,
            estado_inicial=self.afd.estado_inicial,
            estados_finales=nuevos_estados_finales
        )
    
    def crear_particion_inicial(self) -> List[Set[str]]:
        """
        Crea la partición inicial separando estados finales de no finales
        
        Este es el primer paso del algoritmo de partición para minimización de AFD.
        Los estados finales y no finales son distinguibles porque uno acepta cadenas
        y el otro no, por lo tanto deben estar en particiones diferentes inicialmente.
        
        Returns:
            Lista de conjuntos representando la partición inicial.
            Cada conjunto contiene estados que son indistinguibles en esta etapa.
            
        Raises:
            ValueError: Si no hay estados en el AFD
        """
        if not self.afd.estados:
            raise ValueError("El AFD no tiene estados")
        
        # Separar estados finales de no finales
        estados_finales = set(self.afd.estados_finales)
        estados_no_finales = set(self.afd.estados) - estados_finales
        
        # Crear particiones: lista de conjuntos
        particiones = []
        if estados_no_finales:
            particiones.append(estados_no_finales)
        if estados_finales:
            particiones.append(estados_finales)
        
        return particiones
    
    def refinar_particiones(self) -> List[Set[str]]:
        """
        Refina las particiones hasta obtener los estados equivalentes
        
        Implementa el algoritmo de partición iterativa de Hopcroft/Moore.
        En cada iteración, divide las particiones actuales basándose en las transiciones
        con cada símbolo del alfabeto. Dos estados están en la misma partición si
        para todo símbolo van a estados en la misma partición.
        
        Returns:
            Lista de conjuntos con las particiones finales (estados equivalentes)
            
        Raises:
            ValueError: Si self.particiones no está inicializada
        """
        if not self.particiones:
            raise ValueError("Las particiones iniciales no están creadas. Llame a crear_particion_inicial() primero.")
        
        # Iterar hasta que no haya más refinamientos
        while True:
            nuevas_particiones = []
            cambio = False
            # Procesar cada partición actual
            for grupo in self.particiones:
                if len(grupo) <= 1:
                    nuevas_particiones.append(grupo)
                    continue
                firmas = {}
                for estado in grupo:
                    firma = []
                    for simbolo in self.afd.alfabeto:
                        clave = (estado, simbolo)
                        if clave in self.afd.transiciones:
                            destino = self.afd.transiciones[clave]
                            indice_particion = None
                            for i, particion in enumerate(self.particiones):
                                if destino in particion:
                                    indice_particion = i
                                    break
                            firma.append(indice_particion)
                        else:
                            firma.append(-1)
                    firma_tupla = tuple(firma)
                    if firma_tupla not in firmas:
                        firmas[firma_tupla] = set()
                    firmas[firma_tupla].add(estado)
                for subgrupo in firmas.values():
                    nuevas_particiones.append(subgrupo)
                if len(firmas) > 1:
                    cambio = True
            if not cambio:
                break
            self.particiones = nuevas_particiones
        return self.particiones
    
    def son_estados_equivalentes(self, estado1: str, estado2: str, particion: List[Set[str]]) -> bool:
        """
        Verifica si dos estados son equivalentes según una partición
        
        Dos estados son equivalentes si para todo símbolo del alfabeto,
        van a estados que están en la misma partición.
        
        Args:
            estado1: Primer estado a comparar
            estado2: Segundo estado a comparar
            particion: Partición actual del algoritmo
            
        Returns:
            True si los estados son equivalentes, False en caso contrario
            
        Raises:
            ValueError: Si alguno de los estados no existe en el AFD
        """
        if estado1 not in self.afd.estados or estado2 not in self.afd.estados:
            raise ValueError(f"Uno o ambos estados no existen en el AFD: {estado1}, {estado2}")
        
        # Si son el mismo estado, son equivalentes
        if estado1 == estado2:
            return True
        
        # Verificar que vayan a la misma partición para cada símbolo
        for simbolo in self.afd.alfabeto:
            clave1 = (estado1, simbolo)
            clave2 = (estado2, simbolo)
            destino1 = self.afd.transiciones.get(clave1, None)
            destino2 = self.afd.transiciones.get(clave2, None)
            if (destino1 is None) != (destino2 is None):
                return False
            if destino1 is not None and destino2 is not None:
                particion_destino1 = None
                particion_destino2 = None
                for i, grupo in enumerate(particion):
                    if destino1 in grupo:
                        particion_destino1 = i
                    if destino2 in grupo:
                        particion_destino2 = i
                if particion_destino1 != particion_destino2:
                    return False
        return True
    
    def construir_afd_minimizado(self) -> AFD:
        """
        Construye el AFD minimizado a partir de las particiones finales
        
        Cada partición representa un estado en el AFD minimizado. Se elige un representante
        para cada partición y se construyen las transiciones basándose en las transiciones
        de los estados originales.
        
        Returns:
            AFD minimizado con estados equivalentes fusionados
            
        Raises:
            ValueError: Si no hay particiones finales o el estado inicial no está en ninguna partición
        """
        if not self.particiones:
            raise ValueError("No hay particiones finales. Llame a refinar_particiones() primero.")
        
        # Encontrar índice de la partición que contiene el estado inicial
        particion_inicial_idx = None
        for i, particion in enumerate(self.particiones):
            if self.afd.estado_inicial in particion:
                particion_inicial_idx = i
                break
        
        if particion_inicial_idx is None:
            raise ValueError("El estado inicial no se encuentra en ninguna partición")
        
        # Crear mapeo: índice de partición -> nombre de estado
        # La partición del estado inicial será "q0"
        mapeo_particiones = {}
        nombres_estados = []
        
        # Primero agregar la partición inicial como q0
        mapeo_particiones[particion_inicial_idx] = "q0"
        nombres_estados.append("q0")
        
        # Luego agregar las demás particiones
        contador = 1
        for i, particion in enumerate(self.particiones):
            if i != particion_inicial_idx:
                nombre = f"q{contador}"
                mapeo_particiones[i] = nombre
                nombres_estados.append(nombre)
                contador += 1
        
        # Determinar estados finales: particiones que contienen estados finales originales
        estados_finales_minimizados = set()
        for i, particion in enumerate(self.particiones):
            if any(estado in self.afd.estados_finales for estado in particion):
                estados_finales_minimizados.add(mapeo_particiones[i])
        
        # Construir transiciones del AFD minimizado
        transiciones_minimizadas = {}
        for i, particion_origen in enumerate(self.particiones):
            nombre_origen = mapeo_particiones[i]
            
            # Usar el primer estado de la partición como representante para las transiciones
            representante = next(iter(particion_origen))
            
            # Construir transiciones para este estado minimizado
            for simbolo in self.afd.alfabeto:
                clave_transicion = (representante, simbolo)
                if clave_transicion in self.afd.transiciones:
                    estado_destino = self.afd.transiciones[clave_transicion]
                    
                    # Encontrar qué partición contiene el estado destino
                    particion_destino_idx = None
                    for j, particion in enumerate(self.particiones):
                        if estado_destino in particion:
                            particion_destino_idx = j
                            break
                    
                    if particion_destino_idx is not None:
                        nombre_destino = mapeo_particiones[particion_destino_idx]
                        transiciones_minimizadas[(nombre_origen, simbolo)] = nombre_destino
        
        # Crear el AFD minimizado
        return AFD(
            estados=set(nombres_estados),
            alfabeto=self.afd.alfabeto,
            transiciones=transiciones_minimizadas,
            estado_inicial="q0",  # Siempre q0 por el reordenamiento
            estados_finales=estados_finales_minimizados
        )
    
    def minimizar(self) -> AFD:
        """
        Ejecuta el proceso completo de minimización
        
        Returns:
            AFD minimizado
        """
        # 1. Eliminar estados inalcanzables
        afd_sin_inalcanzables = self.eliminar_estados_inalcanzables()
        self.afd = afd_sin_inalcanzables  # Actualizar el AFD de trabajo
        
        # 2. Crear partición inicial
        self.particiones = self.crear_particion_inicial()
        
        # 3. Refinar particiones
        self.particiones = self.refinar_particiones()
        
        # 4. Construir AFD minimizado
        afd_minimizado = self.construir_afd_minimizado()
        
        return afd_minimizado
    
    def obtener_estadisticas_minimizacion(self) -> Dict:
        """
        Obtiene estadísticas del proceso de minimización
        
        Debe llamarse después de ejecutar minimizar() para obtener estadísticas precisas.
        
        Returns:
            Diccionario con estadísticas del proceso de minimización
        """
        # Usar el AFD original para estadísticas precisas
        estados_originales = len(self.afd_original.estados)
        estados_minimizados = len(self.particiones) if self.particiones else 0
        
        # Calcular reducción
        if estados_originales > 0:
            reduccion_porcentual = ((estados_originales - estados_minimizados) / estados_originales) * 100
        else:
            reduccion_porcentual = 0.0
        
        return {
            "estados_originales": estados_originales,
            "estados_minimizados": estados_minimizados,
            "reduccion_porcentual": round(reduccion_porcentual, 2),
            "particiones_finales": len(self.particiones) if self.particiones else 0,
            "estados_finales_minimizados": sum(1 for particion in self.particiones 
                                               if any(estado in self.afd.estados_finales for estado in particion))
        }
    
    def generar_tabla_equivalencias(self) -> Dict[str, str]:
        """
        Genera una tabla que mapea cada estado original a su representante en el AFD minimizado
        
        Debe llamarse después de refinar_particiones() para tener las particiones finales.
        
        Returns:
            Diccionario que mapea estado original -> estado representante en AFD minimizado
            
        Raises:
            ValueError: Si no hay particiones finales
        """
        if not self.particiones:
            raise ValueError("No hay particiones finales. Llame a refinar_particiones() primero.")
        
        # Crear mapeo similar a construir_afd_minimizado
        # El estado "q0" será la partición que contiene el estado inicial
        particion_inicial = None
        for i, particion in enumerate(self.particiones):
            if self.afd.estado_inicial in particion:
                particion_inicial = i
                break
        
        if particion_inicial is None:
            raise ValueError("El estado inicial no se encuentra en ninguna partición")
        
        # Reordenar particiones para que la partición inicial sea q0
        particiones_ordenadas = [self.particiones[particion_inicial]] + \
                               [p for i, p in enumerate(self.particiones) if i != particion_inicial]
        
        # Crear mapeo: estado original -> nombre de estado minimizado
        tabla_equivalencias = {}
        for i, particion in enumerate(particiones_ordenadas):
            nombre_estado = f"q{i}"
            for estado_original in particion:
                tabla_equivalencias[estado_original] = nombre_estado
        
        return tabla_equivalencias
