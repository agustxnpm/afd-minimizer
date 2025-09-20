"""
Clase principal para coordinar todas las operaciones del minimizador
"""
from typing import Dict, Optional, Union, List
from .afd import AFD
from .afnd import AFND
from .minimizador import MinimizadorAFD
from .conversor import ConversorAFND
from .manejador_archivos import ManejadorArchivos


class Automata:
    """
    Clase principal que coordina todas las operaciones del sistema
    """
    
    def __init__(self):
        """Inicializa el minimizador principal"""
        self.automata_actual = None
        self.historial_operaciones = []
    
    def cargar(self, ruta_archivo: str) -> Union[AFD, AFND]:
        """
        Carga un autómata desde un archivo JSON
        
        Args:
            ruta_archivo: Ruta al archivo JSON
            
        Returns:
            Autómata cargado (AFD o AFND)
        """
        automata = ManejadorArchivos.leer_automata(ruta_archivo)
        self.automata_actual = automata
        self._agregar_operacion("cargar", f"Cargado desde {ruta_archivo}")
        return automata
    
    def guardar(self, automata: Union[AFD, AFND], 
                                   ruta_archivo: str, 
                                   incluir_metadatos: bool = True) -> None:
        """
        Guarda un autómata en un archivo JSON
        
        Args:
            automata: Autómata a guardar
            ruta_archivo: Ruta donde guardar
            incluir_metadatos: Si incluir metadatos
        """
        ManejadorArchivos.escribir_automata(automata, ruta_archivo, incluir_metadatos)
        self._agregar_operacion("guardar", f"Guardado en {ruta_archivo}")
    
    def to_afd(self, afnd: AFND) -> AFD:
        """
        Convierte un AFND a AFD
        
        Args:
            afnd: AFND a convertir
            
        Returns:
            AFD equivalente
        """
        conversor = ConversorAFND(afnd)
        afd = conversor.convertir_a_afd()
        self._agregar_operacion("conversion", "AFND convertido a AFD")
        return afd
    
    def minimizar(self, afd: AFD) -> AFD:
        """
        Minimiza un AFD
        
        Args:
            afd: AFD a minimizar
            
        Returns:
            AFD minimizado
        """
        minimizador = MinimizadorAFD(afd)
        afd_minimizado = minimizador.minimizar()
        estadisticas = minimizador.obtener_estadisticas_minimizacion()
        self._agregar_operacion("minimizacion", f"AFD minimizado: {estadisticas}")
        return afd_minimizado
    
    def procesar_automata_completo(self, ruta_entrada: str, 
                                  ruta_salida: str,
                                  forzar_conversion: bool = False) -> Dict:
        """
        Procesa un autómata completo: carga, convierte si es necesario, minimiza y guarda
        
        Args:
            ruta_entrada: Archivo de entrada
            ruta_salida: Archivo de salida
            forzar_conversion: Si forzar conversión de AFD a AFD (para limpieza)
            
        Returns:
            Diccionario con estadísticas del proceso completo
        """
        resultado = {
            "exito": False,
            "operaciones_realizadas": [],
            "estadisticas": {},
            "errores": []
        }
        
        try:
            # 1. Cargar autómata
            automata_original = self.cargar_automata_desde_archivo(ruta_entrada)
            resultado["operaciones_realizadas"].append("carga")
            
            # 2. Convertir a AFD si es necesario
            if isinstance(automata_original, AFND):
                afd = self.convertir_afnd_a_afd(automata_original)
                resultado["operaciones_realizadas"].append("conversion")
            else:
                afd = automata_original
            
            # 3. Minimizar AFD
            afd_minimizado = self.minimizar_afd(afd)
            resultado["operaciones_realizadas"].append("minimizacion")
            
            # 4. Guardar resultado
            self.guardar_automata_en_archivo(afd_minimizado, ruta_salida)
            resultado["operaciones_realizadas"].append("guardado")
            
            # 5. Generar estadísticas
            resultado["estadisticas"] = self._generar_estadisticas_proceso(
                automata_original, afd_minimizado
            )
            
            resultado["exito"] = True
            
        except Exception as e:
            resultado["errores"].append(str(e))
        
        return resultado
    
    def validar_automata(self, automata: Union[AFD, AFND]) -> Dict:
        """
        Valida un autómata y retorna información sobre su validez
        
        Args:
            automata: Autómata a validar
            
        Returns:
            Diccionario con información de validación
        """
        from .afd import AFD
        from .afnd import AFND
        
        validacion = {
            "es_valido": True,
            "errores": [],
            "advertencias": [],
            "propiedades": {}
        }
        
        # Determinar tipo de autómata
        es_afd = isinstance(automata, AFD)
        tipo_automata = "AFD" if es_afd else "AFND"
        
        # 1. Validar estados básicos
        if not automata.estados:
            validacion["errores"].append("El autómata no tiene estados")
            validacion["es_valido"] = False
            return validacion
        
        # 2. Validar estado inicial
        if automata.estado_inicial not in automata.estados:
            validacion["errores"].append(f"El estado inicial '{automata.estado_inicial}' no está en el conjunto de estados")
            validacion["es_valido"] = False
        
        # 3. Validar estados finales
        estados_finales_invalidos = automata.estados_finales - automata.estados
        if estados_finales_invalidos:
            validacion["errores"].append(f"Los siguientes estados finales no existen: {estados_finales_invalidos}")
            validacion["es_valido"] = False
        
        # 4. Validar alfabeto
        if not automata.alfabeto:
            validacion["advertencias"].append("El autómata no tiene símbolos en el alfabeto")
        
        # 5. Validar transiciones
        transiciones_invalidas = []
        estados_origen_en_transiciones = set()
        estados_destino_en_transiciones = set()
        
        for clave_transicion, destinos in automata.transiciones.items():
            if not isinstance(clave_transicion, tuple) or len(clave_transicion) != 2:
                transiciones_invalidas.append(f"Formato inválido de clave de transición: {clave_transicion}")
                continue
                
            estado_origen, simbolo = clave_transicion
            
            # Verificar estado origen
            if estado_origen not in automata.estados:
                transiciones_invalidas.append(f"Estado origen '{estado_origen}' no existe en la transición {clave_transicion}")
            
            # Verificar símbolo
            if simbolo not in automata.alfabeto:
                transiciones_invalidas.append(f"Símbolo '{simbolo}' no está en el alfabeto en la transición {clave_transicion}")
            
            # Verificar destinos
            if es_afd:
                # Para AFD, destino debe ser un solo estado
                if not isinstance(destinos, str):
                    transiciones_invalidas.append(f"AFD debe tener un solo estado destino en {clave_transicion}, encontrado: {destinos}")
                elif destinos not in automata.estados:
                    transiciones_invalidas.append(f"Estado destino '{destinos}' no existe en la transición {clave_transicion}")
                else:
                    estados_destino_en_transiciones.add(destinos)
            else:
                # Para AFND, destinos deben ser un conjunto
                if not isinstance(destinos, set):
                    transiciones_invalidas.append(f"AFND debe tener un conjunto de estados destino en {clave_transicion}, encontrado: {destinos}")
                else:
                    estados_invalidos = destinos - automata.estados
                    if estados_invalidos:
                        transiciones_invalidas.append(f"Estados destino inválidos en {clave_transicion}: {estados_invalidos}")
                    estados_destino_en_transiciones.update(destinos)
            
            estados_origen_en_transiciones.add(estado_origen)
        
        if transiciones_invalidas:
            validacion["errores"].extend(transiciones_invalidas)
            validacion["es_valido"] = False
        
        # 6. Verificar completitud (solo para AFD)
        if es_afd:
            transiciones_faltantes = []
            for estado in automata.estados:
                for simbolo in automata.alfabeto:
                    if (estado, simbolo) not in automata.transiciones:
                        transiciones_faltantes.append(f"Transición faltante: ({estado}, {simbolo})")
            
            if transiciones_faltantes:
                validacion["errores"].extend(transiciones_faltantes)
                validacion["es_valido"] = False
        
        # 7. Verificar determinismo (para AFND)
        elif not es_afd:
            transiciones_no_deterministas = []
            for clave_transicion, destinos in automata.transiciones.items():
                if isinstance(destinos, set) and len(destinos) > 1:
                    transiciones_no_deterministas.append(f"Transición no determinista: {clave_transicion} -> {destinos}")
            
            if transiciones_no_deterministas:
                validacion["propiedades"]["es_deterministico"] = False
                validacion["advertencias"].append("El AFND tiene transiciones no deterministas")
            else:
                validacion["propiedades"]["es_deterministico"] = True
        
        # 8. Verificar estados inalcanzables (advertencia)
        estados_alcanzables = self._encontrar_estados_alcanzables(automata)
        estados_inalcanzables = automata.estados - estados_alcanzables
        
        if estados_inalcanzables:
            validacion["advertencias"].append(f"Estados inalcanzables: {estados_inalcanzables}")
            validacion["propiedades"]["estados_inalcanzables"] = list(estados_inalcanzables)
        
        # 9. Propiedades adicionales
        validacion["propiedades"].update({
            "tipo": tipo_automata,
            "num_estados": len(automata.estados),
            "num_simbolos": len(automata.alfabeto),
            "num_transiciones": len(automata.transiciones),
            "num_estados_finales": len(automata.estados_finales),
            "estados_alcanzables": len(estados_alcanzables),
            "tiene_estados_finales": len(automata.estados_finales) > 0
        })
        
        return validacion
    
    def _encontrar_estados_alcanzables(self, automata: Union[AFD, AFND]) -> set:
        """
        Encuentra todos los estados alcanzables desde el estado inicial
        
        Args:
            automata: Autómata a analizar
            
        Returns:
            Conjunto de estados alcanzables
        """
        from collections import deque
        
        alcanzables = set()
        cola = deque([automata.estado_inicial])
        alcanzables.add(automata.estado_inicial)
        
        while cola:
            estado_actual = cola.popleft()
            
            # Explorar transiciones desde el estado actual
            for simbolo in automata.alfabeto:
                clave = (estado_actual, simbolo)
                if clave in automata.transiciones:
                    destinos = automata.transiciones[clave]
                    
                    if isinstance(destinos, str):
                        # AFD
                        destinos = {destinos}
                    
                    for destino in destinos:
                        if destino not in alcanzables:
                            alcanzables.add(destino)
                            cola.append(destino)
        
        return alcanzables
    
    def obtener_estadisticas_automata(self, automata: Union[AFD, AFND]) -> Dict:
        """
        Obtiene estadísticas detalladas de un autómata
        
        Args:
            automata: Autómata a analizar
            
        Returns:
            Diccionario con estadísticas
        """
        estadisticas = {
            "tipo": "AFD" if isinstance(automata, AFD) else "AFND",
            "num_estados": len(automata.estados),
            "num_simbolos": len(automata.alfabeto),
            "num_transiciones": len(automata.transiciones),
            "estados_finales": len(automata.estados_finales),
            "alfabeto": list(automata.alfabeto),
            "densidad_transiciones": 0.0  # Se calculará
        }
        
        # Calcular densidad de transiciones
        max_transiciones = len(automata.estados) * len(automata.alfabeto)
        if max_transiciones > 0:
            estadisticas["densidad_transiciones"] = len(automata.transiciones) / max_transiciones
        
        return estadisticas
    
    def _agregar_operacion(self, tipo: str, descripcion: str) -> None:
        """
        Agrega una operación al historial
        
        Args:
            tipo: Tipo de operación
            descripcion: Descripción de la operación
        """
        from datetime import datetime
        
        self.historial_operaciones.append({
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            "descripcion": descripcion
        })
    
    def _generar_estadisticas_proceso(self, automata_original: Union[AFD, AFND], 
                                    automata_final: AFD) -> Dict:
        """
        Genera estadísticas del proceso completo
        
        Args:
            automata_original: Autómata original
            automata_final: Autómata final (minimizado)
            
        Returns:
            Diccionario con estadísticas
        """
        stats_original = self.obtener_estadisticas_automata(automata_original)
        stats_final = self.obtener_estadisticas_automata(automata_final)
        
        return {
            "original": stats_original,
            "final": stats_final,
            "reduccion": {
                "estados": stats_original["num_estados"] - stats_final["num_estados"],
                "transiciones": stats_original["num_transiciones"] - stats_final["num_transiciones"],
                "porcentaje_reduccion_estados": (
                    (stats_original["num_estados"] - stats_final["num_estados"]) / 
                    stats_original["num_estados"] * 100
                ) if stats_original["num_estados"] > 0 else 0
            }
        }
    
    def obtener_historial(self) -> List[Dict]:
        """
        Obtiene el historial de operaciones
        
        Returns:
            Lista con el historial de operaciones
        """
        return self.historial_operaciones.copy()
    
    def limpiar_historial(self) -> None:
        """Limpia el historial de operaciones"""
        self.historial_operaciones.clear()
