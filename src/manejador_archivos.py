"""
Clase para manejar la lectura y escritura de archivos JSON de autómatas
"""
import json
import os
from typing import Dict, Union, List
from .afd import AFD
from .afnd import AFND


class ManejadorArchivos:
    """
    Se encarga de la lectura y escritura de autómatas en formato JSON
    """
    
    @staticmethod
    def leer_automata(ruta_archivo: str) -> Union[AFD, AFND]:
        """
        Lee un autómata desde un archivo JSON
        
        Args:
            ruta_archivo: Ruta al archivo JSON
            
        Returns:
            Instancia de AFD o AFND según el tipo especificado en el archivo
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el archivo no es un JSON válido
            ValueError: Si el formato del autómata no es válido
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe")
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                data = json.load(archivo)
            
            # Validar estructura básica
            ManejadorArchivos._validar_estructura_json(data)
            
            # Crear autómata según el tipo
            tipo = data.get("tipo", "AFD")
            if tipo == "AFD":
                return AFD.from_dict(data)
            elif tipo == "AFND":
                return AFND.from_dict(data)
            else:
                raise ValueError(f"Tipo de autómata no soportado: {tipo}")
                
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error al parsear JSON: {e}")
    
    @staticmethod
    def escribir_automata(automata: Union[AFD, AFND], ruta_archivo: str, 
                         incluir_metadatos: bool = True) -> None:
        """
        Escribe un autómata a un archivo JSON
        
        Args:
            automata: Instancia de AFD o AFND a escribir
            ruta_archivo: Ruta donde escribir el archivo
            incluir_metadatos: Si incluir metadatos adicionales en el JSON
            
        Raises:
            OSError: Si hay problemas de escritura del archivo
        """
        try:
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)
            
            # Convertir autómata a diccionario
            data = automata.to_dict()
            
            # Agregar metadatos si se solicita
            if incluir_metadatos:
                data["metadatos"] = ManejadorArchivos._generar_metadatos(automata)
            
            # Escribir archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(data, archivo, indent=2, ensure_ascii=False)
                
        except OSError as e:
            raise OSError(f"Error al escribir archivo {ruta_archivo}: {e}")
    
    @staticmethod
    def _validar_estructura_json(data: Dict) -> None:
        """
        Valida que el JSON tenga la estructura mínima requerida
        
        Args:
            data: Diccionario con los datos del JSON
            
        Raises:
            ValueError: Si la estructura no es válida
        """
        campos_requeridos = ["estados", "alfabeto", "transiciones", 
                           "estado_inicial", "estados_finales"]
        
        for campo in campos_requeridos:
            if campo not in data:
                raise ValueError(f"Campo requerido '{campo}' no encontrado en el JSON")
        
        # Validaciones adicionales
        if not isinstance(data["estados"], list):
            raise ValueError("El campo 'estados' debe ser una lista")
        
        if not isinstance(data["alfabeto"], list):
            raise ValueError("El campo 'alfabeto' debe ser una lista")
        
        if not isinstance(data["transiciones"], list):
            raise ValueError("El campo 'transiciones' debe ser una lista")
        
        if not isinstance(data["estados_finales"], list):
            raise ValueError("El campo 'estados_finales' debe ser una lista")
    
    @staticmethod
    def _generar_metadatos(automata: Union[AFD, AFND]) -> Dict:
        """
        Genera metadatos para incluir en el archivo JSON
        
        Args:
            automata: Instancia del autómata
            
        Returns:
            Diccionario con metadatos
        """
        from datetime import datetime
        
        return {
            "fecha_creacion": datetime.now().isoformat(),
            "version": "1.0",
            "estadisticas": {
                "num_estados": len(automata.estados),
                "num_simbolos": len(automata.alfabeto),
                "num_transiciones": len(automata.transiciones),
                "es_completo": automata.es_completo() if hasattr(automata, 'es_completo') else None
            }
        }
    
    @staticmethod
    def validar_archivo_automata(ruta_archivo: str) -> Dict:
        """
        Valida un archivo de autómata sin cargarlo completamente
        
        Args:
            ruta_archivo: Ruta al archivo a validar
            
        Returns:
            Diccionario con información de validación
        """
        resultado = {
            "es_valido": False,
            "errores": [],
            "advertencias": [],
            "tipo": None,
            "estadisticas": {}
        }
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                data = json.load(archivo)
            
            # Validar estructura
            ManejadorArchivos._validar_estructura_json(data)
            
            # Determinar tipo
            resultado["tipo"] = data.get("tipo", "AFD")
            
            # Calcular estadísticas básicas
            resultado["estadisticas"] = {
                "num_estados": len(data["estados"]),
                "num_simbolos": len(data["alfabeto"]),
                "num_transiciones": len(data["transiciones"])
            }
            
            resultado["es_valido"] = True
            
        except FileNotFoundError:
            resultado["errores"].append("Archivo no encontrado")
        except json.JSONDecodeError as e:
            resultado["errores"].append(f"JSON inválido: {e}")
        except ValueError as e:
            resultado["errores"].append(f"Estructura inválida: {e}")
        except Exception as e:
            resultado["errores"].append(f"Error inesperado: {e}")
        
        return resultado
    
    @staticmethod
    def listar_automatas_en_directorio(directorio: str) -> List[Dict]:
        """
        Lista todos los archivos de autómatas válidos en un directorio
        
        Args:
            directorio: Directorio a explorar
            
        Returns:
            Lista de diccionarios con información de cada autómata encontrado
        """
        automatas = []
        
        if not os.path.exists(directorio):
            return automatas
        
        for archivo in os.listdir(directorio):
            if archivo.endswith('.json'):
                ruta_completa = os.path.join(directorio, archivo)
                validacion = ManejadorArchivos.validar_archivo_automata(ruta_completa)
                
                if validacion["es_valido"]:
                    automatas.append({
                        "nombre_archivo": archivo,
                        "ruta_completa": ruta_completa,
                        "tipo": validacion["tipo"],
                        "estadisticas": validacion["estadisticas"]
                    })
        
        return automatas
