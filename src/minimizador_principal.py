"""
Clase principal para coordinar todas las operaciones del minimizador
"""
from typing import Dict, Optional, Union, List
from .afd import AFD
from .afnd import AFND
from .minimizador import MinimizadorAFD
from .conversor import ConversorAFND
from .manejador_archivos import ManejadorArchivos


class MinimizadorPrincipal:
    """
    Clase principal que coordina todas las operaciones del sistema
    """
    
    def __init__(self):
        """Inicializa el minimizador principal"""
        self.automata_actual = None
        self.historial_operaciones = []
    
    def cargar_automata_desde_archivo(self, ruta_archivo: str) -> Union[AFD, AFND]:
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
    
    def guardar_automata_en_archivo(self, automata: Union[AFD, AFND], 
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
    
    def convertir_afnd_a_afd(self, afnd: AFND) -> AFD:
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
    
    def minimizar_afd(self, afd: AFD) -> AFD:
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
        validacion = {
            "es_valido": True,
            "errores": [],
            "advertencias": [],
            "propiedades": {}
        }
        
        # TODO: Implementar validaciones específicas
        # - Estados válidos
        # - Transiciones válidas
        # - Estado inicial válido
        # - Estados finales válidos
        # - Completitud (para AFD)
        # - Determinismo (para verificar si AFND es realmente determinístico)
        
        return validacion
    
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
