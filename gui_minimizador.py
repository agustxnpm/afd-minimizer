#!/usr/bin/env python3
"""
GUI Mejorada para el Minimizador de Autómatas usando Tkinter
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional, Union, Dict, Any
import pydot
from PIL import Image, ImageTk
import io
import json

import sys
import os
# Agregar el directorio src al path para importar módulos locales
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar las clases del sistema (desde src/)
from automata import Automata
from afd import AFD
from afnd import AFND


class GUIMinimizador:
    """
    Interfaz gráfica mejorada para el minimizador de autómatas
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🤖 Minimizador de Autómatas - Fundamentos Teóricos de Informática")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 700)
        
        # Configurar estilo
        self._configurar_estilo()
        
        # Instancia del coordinador principal
        self.automata_manager = Automata()

        # Variables de estado
        self.automata_original: Optional[Union[AFD, AFND]] = None
        self.automata_afd: Optional[AFD] = None
        self.automata_minimizado: Optional[AFD] = None
        self.afd_original_para_min: Optional[AFD] = None
        self.lenguaje: str = "No especificado"
        self.imagen_original: Optional[ImageTk.PhotoImage] = None
        self.imagen_afd: Optional[ImageTk.PhotoImage] = None
        self.imagen_minimizado: Optional[ImageTk.PhotoImage] = None

        # Variables para almacenar imágenes originales (sin zoom)
        self.imagen_original_pil: Optional[Image.Image] = None
        self.imagen_afd_pil: Optional[Image.Image] = None
        self.imagen_minimizado_pil: Optional[Image.Image] = None

        # Variables de zoom para cada panel
        self.zoom_original = 1.0
        self.zoom_afd = 1.0
        self.zoom_minimizado = 1.0
        self.zoom_factor = 1.1  # Factor de zoom por cada paso
        self.zoom_min = 0.1     # Zoom mínimo
        self.zoom_max = 5.0     # Zoom máximo

        # Variables de offset para pan/arrastre
        self.offset_original = {'x': 0, 'y': 0}
        self.offset_afd = {'x': 0, 'y': 0}
        self.offset_minimizado = {'x': 0, 'y': 0}
        self.drag_start = None  # Para drag-and-drop

        # Opción de operación
        self.operacion = tk.StringVar(value="afnd_afd")

        # Crear interfaz
        self._crear_widgets()
        self._configurar_layout()

    def _configurar_estilo(self):
        """Configurar el estilo visual de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Header.TFrame', background='#f0f0f0')
        style.configure('Main.TButton', font=('Segoe UI', 10))
        style.configure('Success.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Panel.TLabelframe', font=('Segoe UI', 10, 'bold'))
        style.configure('Panel.TLabelframe.Label', foreground='#2c3e50')
        
        # Configurar colores de la ventana principal
        self.root.configure(bg='#ecf0f1')

    def _crear_widgets(self):
        """Crear todos los widgets de la interfaz"""

        # Frame principal con padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # ===== SECCIÓN SUPERIOR: Controles =====
        frame_superior = ttk.Frame(main_container)
        frame_superior.pack(fill=tk.X, pady=(0, 10))

        # Frame para título y descripción
        frame_titulo = ttk.Frame(frame_superior)
        frame_titulo.pack(fill=tk.X, pady=(0, 10))
        
        titulo = ttk.Label(frame_titulo, text="🤖 Minimizador de Autómatas Finitos", 
                          font=('Segoe UI', 16, 'bold'))
        titulo.pack()
        
        descripcion = ttk.Label(frame_titulo, 
                               text="Convierte AFND a AFD y minimiza autómatas finitos determinísticos",
                               font=('Segoe UI', 10))
        descripcion.pack()
        
        self.label_lenguaje = ttk.Label(frame_titulo, text="", font=('Segoe UI', 20, 'italic'))
        self.label_lenguaje.pack()

        # Frame para selector de operación con mejor diseño
        frame_operacion = ttk.LabelFrame(frame_superior, text="📋 Seleccionar Operación", padding="10")
        frame_operacion.pack(fill=tk.X, pady=(0, 10))
        
        self.radio_afnd_afd = ttk.Radiobutton(
            frame_operacion, 
            text="Convertir AFND → AFD", 
            variable=self.operacion, 
            value="afnd_afd"
        )
        self.radio_afd_min = ttk.Radiobutton(
            frame_operacion, 
            text="Minimizar AFD → AFD mínimo", 
            variable=self.operacion, 
            value="afd_min"
        )
        self.radio_afnd_afd.pack(side=tk.LEFT, padx=20)
        self.radio_afd_min.pack(side=tk.LEFT, padx=20)

        # Frame para botones principales
        frame_botones = ttk.Frame(frame_superior)
        frame_botones.pack(fill=tk.X)
        
        # Botones con iconos simulados
        self.btn_cargar = ttk.Button(
            frame_botones, 
            text="📁 Cargar JSON", 
            command=self._cargar_archivo,
            style='Main.TButton',
            width=20
        )
        self.btn_procesar = ttk.Button(
            frame_botones, 
            text="⚙️ Procesar", 
            command=self._procesar_automata,
            state=tk.DISABLED,
            style='Success.TButton',
            width=20
        )
        self.btn_guardar = ttk.Button(
            frame_botones, 
            text="💾 Guardar Resultado", 
            command=self._guardar_resultado,
            state=tk.DISABLED,
            style='Main.TButton',
            width=20
        )
        self.btn_informe = ttk.Button(
            frame_botones, 
            text="📊 Generar Informe", 
            command=self._generar_informe,
            state=tk.DISABLED,
            style='Main.TButton',
            width=20
        )
        
        self.btn_cargar.pack(side=tk.LEFT, padx=5)
        self.btn_procesar.pack(side=tk.LEFT, padx=5)
        self.btn_guardar.pack(side=tk.LEFT, padx=5)
        self.btn_informe.pack(side=tk.LEFT, padx=5)

        # ===== SECCIÓN MEDIA: Prueba de cadenas =====
        frame_prueba = ttk.LabelFrame(main_container, text="🔍 Probar Cadenas", padding="10")
        frame_prueba.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_prueba, text="Cadena de entrada:").pack(side=tk.LEFT, padx=5)
        self.entry_cadena = ttk.Entry(frame_prueba, width=40, font=('Consolas', 10))
        self.entry_cadena.pack(side=tk.LEFT, padx=5)
        self.btn_probar = ttk.Button(
            frame_prueba, 
            text="▶️ Probar", 
            command=self._probar_cadena,
            state=tk.DISABLED
        )
        self.btn_probar.pack(side=tk.LEFT, padx=5)
        
        # Label para mostrar resultado de prueba
        self.label_resultado_prueba = ttk.Label(frame_prueba, text="", font=('Segoe UI', 10))
        self.label_resultado_prueba.pack(side=tk.LEFT, padx=20)

        # ===== SECCIÓN GRÁFICOS: Paneles de visualización =====
        self.frame_graficos = ttk.Frame(main_container)
        self.frame_graficos.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Crear tres paneles adaptativos para los gráficos
        # Los tamaños se ajustarán automáticamente
        
        # Panel Autómata Original
        self.frame_original = ttk.LabelFrame(
            self.frame_graficos, 
            text="📌 Autómata Original",
            style='Panel.TLabelframe'
        )
        self.canvas_original = tk.Canvas(
            self.frame_original, 
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2,
            width=350,
            height=200
        )
        self.canvas_original.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._mostrar_placeholder(self.canvas_original, "No hay autómata cargado")
        
        # Bindings para zoom en panel original
        self.canvas_original.bind("<MouseWheel>", lambda e: self._zoom_canvas(e, 'original'))
        self.canvas_original.bind("<Button-4>", lambda e: self._zoom_canvas(e, 'original', zoom_in=True))
        self.canvas_original.bind("<Button-5>", lambda e: self._zoom_canvas(e, 'original', zoom_in=False))

        # Bindings para drag en panel original
        self.canvas_original.bind("<ButtonPress-1>", lambda e: self._start_drag(e, 'original'))
        self.canvas_original.bind("<B1-Motion>", lambda e: self._drag(e, 'original'))

        # Panel AFD Convertido
        self.frame_afd = ttk.LabelFrame(
            self.frame_graficos, 
            text="🔄 AFD (Conversión)",
            style='Panel.TLabelframe'
        )
        self.canvas_afd = tk.Canvas(
            self.frame_afd, 
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2,
            width=350,
            height=200
        )
        self.canvas_afd.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._mostrar_placeholder(self.canvas_afd, "No hay conversión")
        
        # Bindings para zoom en panel AFD
        self.canvas_afd.bind("<MouseWheel>", lambda e: self._zoom_canvas(e, 'afd'))
        self.canvas_afd.bind("<Button-4>", lambda e: self._zoom_canvas(e, 'afd', zoom_in=True))
        self.canvas_afd.bind("<Button-5>", lambda e: self._zoom_canvas(e, 'afd', zoom_in=False))

        # Bindings para drag en panel AFD
        self.canvas_afd.bind("<ButtonPress-1>", lambda e: self._start_drag(e, 'afd'))
        self.canvas_afd.bind("<B1-Motion>", lambda e: self._drag(e, 'afd'))

        # Panel AFD Minimizado
        self.frame_minimizado = ttk.LabelFrame(
            self.frame_graficos, 
            text="✨ AFD Minimizado",
            style='Panel.TLabelframe'
        )
        self.canvas_minimizado = tk.Canvas(
            self.frame_minimizado, 
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2,
            width=350,
            height=200
        )
        self.canvas_minimizado.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._mostrar_placeholder(self.canvas_minimizado, "No hay minimización")
        
        # Bindings para zoom en panel minimizado
        self.canvas_minimizado.bind("<MouseWheel>", lambda e: self._zoom_canvas(e, 'minimizado'))
        self.canvas_minimizado.bind("<Button-4>", lambda e: self._zoom_canvas(e, 'minimizado', zoom_in=True))
        self.canvas_minimizado.bind("<Button-5>", lambda e: self._zoom_canvas(e, 'minimizado', zoom_in=False))

        # Bindings para drag en panel minimizado
        self.canvas_minimizado.bind("<ButtonPress-1>", lambda e: self._start_drag(e, 'minimizado'))
        self.canvas_minimizado.bind("<B1-Motion>", lambda e: self._drag(e, 'minimizado'))

        # ===== SECCIÓN INFERIOR: Consola de estado =====
        frame_consola = ttk.LabelFrame(main_container, text="📝 Consola de Estado", padding="5")
        frame_consola.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto con scrollbar
        self.texto_estado = scrolledtext.ScrolledText(
            frame_consola, 
            height=6,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white'
        )
        self.texto_estado.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje de bienvenida
        self._mostrar_estado("═" * 60 + "\n", 'header')
        self._mostrar_estado("🤖 Sistema de Minimización de Autómatas iniciado\n", 'success')
        self._mostrar_estado("═" * 60 + "\n", 'header')
        self._mostrar_estado("Esperando cargar un autómata...\n", 'info')

    def _configurar_layout(self):
        """Configurar el layout de los widgets"""
        # Los paneles de gráficos en horizontal con expansión
        self.frame_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.frame_afd.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.frame_minimizado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    def _mostrar_placeholder(self, canvas, texto):
        """Mostrar texto placeholder en un canvas"""
        canvas.delete("all")
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        canvas.create_text(
            width/2, height/2,
            text=texto,
            font=('Segoe UI', 12),
            fill='#7f8c8d',
            anchor='center'
        )

    def _cargar_archivo(self):
        """Cargar archivo JSON con autómata"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )

        if not archivo:
            return

        try:
            # Limpiar paneles
            self._limpiar_todos_paneles()
            
            # Resetear zoom del panel original
            self.zoom_original = 1.0
            self.imagen_original_pil = None
            
            # Leer JSON para extraer campo Lenguaje
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.lenguaje = data.get("Lenguaje", "No especificado")
            
            # Cargar autómata
            self.automata_original = self.automata_manager.cargar(archivo)
            
            # Validar autómata
            validacion = self.automata_manager.validar_automata(self.automata_original)
            
            # Mostrar resultados
            self._mostrar_estado(f"\n📁 Autómata cargado desde: {archivo}\n", 'success')
            self._mostrar_validacion(validacion)
            
            if validacion["es_valido"]:
                # Generar gráfico del original
                self._generar_grafico_original()
                self.btn_procesar.config(state=tk.NORMAL)
                self.btn_probar.config(state=tk.NORMAL)
                self._mostrar_estado("✅ Autómata listo para procesar\n", 'success')
                self.label_lenguaje.config(text=f"Lenguaje: {self.lenguaje}")
            else:
                self.btn_procesar.config(state=tk.DISABLED)
                self.btn_probar.config(state=tk.DISABLED)
                self._mostrar_estado("❌ Corrija los errores antes de procesar\n", 'error')
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
            self._mostrar_estado(f"❌ Error al cargar: {str(e)}\n", 'error')

    def _limpiar_todos_paneles(self):
        """Limpiar todos los paneles de visualización"""
        self._mostrar_placeholder(self.canvas_original, "No hay autómata cargado")
        self._mostrar_placeholder(self.canvas_afd, "No hay conversión")
        self._mostrar_placeholder(self.canvas_minimizado, "No hay minimización")
        self.automata_original = None
        self.automata_afd = None
        self.automata_minimizado = None
        self.lenguaje = "No especificado"
        self.label_resultado_prueba.config(text="")
        self.label_lenguaje.config(text="")
        
        # Limpiar imágenes guardadas
        self.imagen_original_pil = None
        self.imagen_afd_pil = None
        self.imagen_minimizado_pil = None
        
        # Resetear zoom
        self.zoom_original = 1.0
        self.zoom_afd = 1.0
        self.zoom_minimizado = 1.0

        # Resetear offsets
        self.offset_original = {'x': 0, 'y': 0}
        self.offset_afd = {'x': 0, 'y': 0}
        self.offset_minimizado = {'x': 0, 'y': 0}
        self.drag_start = None

    def _procesar_automata(self):
        """Procesar el autómata según la operación seleccionada"""
        if not self.automata_original:
            return

        try:
            op = self.operacion.get()
            self._mostrar_estado(f"\n⚙️ Procesando operación: {'AFND → AFD' if op == 'afnd_afd' else 'AFD → AFD mínimo'}\n", 'info')
            
            if op == "afnd_afd":
                # Limpiar resultados previos para conversión
                self.automata_afd = None
                self.automata_minimizado = None
                self._mostrar_placeholder(self.canvas_afd, "No hay conversión")
                self._mostrar_placeholder(self.canvas_minimizado, "No hay minimización")
                
                # Limpiar imágenes guardadas de resultados
                self.imagen_afd_pil = None
                self.imagen_minimizado_pil = None
                
                # Resetear zoom de los paneles resultantes
                self.zoom_afd = 1.0
                self.zoom_minimizado = 1.0
            elif op == "afd_min":
                # Limpiar solo minimización, mantener AFD convertido si existe
                self.automata_minimizado = None
                self._mostrar_placeholder(self.canvas_minimizado, "No hay minimización")
                
                # Limpiar imagen de minimización
                self.imagen_minimizado_pil = None
                
                # Resetear zoom del panel minimizado
                self.zoom_minimizado = 1.0
            
            if op == "afnd_afd":
                if not isinstance(self.automata_original, AFND):
                    self._mostrar_estado("⚠️ El autómata cargado no es un AFND.\n", 'warning')
                    messagebox.showwarning("Advertencia", "El autómata cargado no es un AFND")
                    return
                
                # Conversión AFND → AFD
                self.automata_afd = self.automata_manager.to_afd(self.automata_original)
                self._generar_grafico_afd()
                self._mostrar_estado("✅ Conversión AFND → AFD completada exitosamente.\n", 'success')
                self._mostrar_estadisticas_conversion()
                
            elif op == "afd_min":
                # Seleccionar AFD a minimizar: convertido si existe, sino el original
                afd_a_minimizar = self.automata_afd if self.automata_afd else self.automata_original
                
                if not isinstance(afd_a_minimizar, AFD):
                    self._mostrar_estado("⚠️ No hay AFD disponible para minimizar.\n", 'warning')
                    messagebox.showwarning("Advertencia", "No hay AFD disponible para minimizar")
                    return
                
                # Guardar el AFD original para estadísticas
                self.afd_original_para_min = afd_a_minimizar
                
                # Minimización AFD
                self.automata_minimizado = self.automata_manager.minimizar(afd_a_minimizar)
                self._generar_grafico_minimizado()
                self._mostrar_estado("✅ Minimización de AFD completada exitosamente.\n", 'success')
                self._mostrar_estadisticas_minimizacion()
            
            self.btn_guardar.config(state=tk.NORMAL)
            self.btn_informe.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar autómata:\n{str(e)}")
            self._mostrar_estado(f"❌ Error al procesar: {str(e)}\n", 'error')

    def _mostrar_estadisticas_conversion(self):
        """Mostrar estadísticas de la conversión AFND a AFD"""
        if self.automata_original and self.automata_afd:
            orig_estados = len(self.automata_original.estados)
            afd_estados = len(self.automata_afd.estados)
            self._mostrar_estado(f"📊 Estadísticas de conversión:\n", 'info')
            self._mostrar_estado(f"   • Estados AFND original: {orig_estados}\n")
            self._mostrar_estado(f"   • Estados AFD resultante: {afd_estados}\n")
            self._mostrar_estado(f"   • Factor de expansión: {afd_estados/orig_estados:.2f}x\n")

    def _mostrar_estadisticas_minimizacion(self):
        """Mostrar estadísticas de la minimización"""
        if self.afd_original_para_min and self.automata_minimizado:
            orig_estados = len(self.afd_original_para_min.estados)
            min_estados = len(self.automata_minimizado.estados)
            reduccion = orig_estados - min_estados
            porcentaje = (reduccion / orig_estados) * 100 if orig_estados > 0 else 0
            
            self._mostrar_estado(f"📊 Estadísticas de minimización:\n", 'info')
            self._mostrar_estado(f"   • Estados originales: {orig_estados}\n")
            self._mostrar_estado(f"   • Estados minimizados: {min_estados}\n")
            self._mostrar_estado(f"   • Reducción: {reduccion} estados ({porcentaje:.1f}%)\n")

    def _guardar_resultado(self):
        """Guardar el resultado como JSON"""
        op = self.operacion.get()
        automata_a_guardar = self.automata_afd if op == "afnd_afd" else self.automata_minimizado
        
        if not automata_a_guardar:
            return

        archivo = filedialog.asksaveasfilename(
            title="Guardar resultado",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if not archivo:
            return
            
        try:
            self.automata_manager.guardar(automata_a_guardar, archivo)
            messagebox.showinfo("Éxito", f"Resultado guardado en:\n{archivo}")
            self._mostrar_estado(f"💾 Resultado guardado en: {archivo}\n", 'success')
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            self._mostrar_estado(f"❌ Error al guardar: {str(e)}\n", 'error')

    def _generar_informe(self):
        """Generar informe detallado"""
        op = self.operacion.get()
        if not self.automata_original:
            return
        if op == "afnd_afd" and not self.automata_afd:
            return
        if op == "afd_min" and not self.automata_minimizado:
            return

        # Determinar el autómata procesado
        automata_procesado = self.automata_original if op == "afnd_afd" else self.afd_original_para_min

        archivo = filedialog.asksaveasfilename(
            title="Guardar informe",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if not archivo:
            return
            
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("     INFORME DE PROCESAMIENTO DE AUTÓMATA FINITO\n")
                f.write("=" * 70 + "\n\n")
                
                # Información del autómata original
                f.write("1. AUTÓMATA ORIGINAL\n")
                f.write("-" * 40 + "\n")
                f.write(f"   Tipo: {'AFND' if isinstance(automata_procesado, AFND) else 'AFD'}\n")
                f.write(f"   Estados: {list(automata_procesado.estados)}\n")
                f.write(f"   Alfabeto: {list(automata_procesado.alfabeto)}\n")
                f.write(f"   Estado inicial: {automata_procesado.estado_inicial}\n")
                f.write(f"   Estados finales: {list(automata_procesado.estados_finales)}\n")
                f.write(f"   Lenguaje: {self.lenguaje}\n\n")
                
                # Validación
                validacion = self.automata_manager.validar_automata(automata_procesado)
                f.write("2. VALIDACIÓN DEL AUTÓMATA ORIGINAL\n")
                f.write("-" * 40 + "\n")
                f.write(f"   Estado: {'✓ Válido' if validacion['es_valido'] else '✗ Inválido'}\n")
                
                if validacion["errores"]:
                    f.write("   Errores encontrados:\n")
                    for error in validacion["errores"]:
                        f.write(f"     • {error}\n")
                        
                if validacion["advertencias"]:
                    f.write("   Advertencias:\n")
                    for adv in validacion["advertencias"]:
                        f.write(f"     • {adv}\n")
                f.write("\n")
                
                # Proceso realizado
                f.write("3. PROCESO REALIZADO\n")
                f.write("-" * 40 + "\n")
                
                # Verificar si hay proceso completo (conversión + minimización)
                if self.automata_minimizado and self.automata_afd:
                    # Proceso completo: AFND → AFD → AFD mínimo
                    f.write("   Operaciones realizadas:\n")
                    f.write("   1. Conversión de AFND a AFD (Método: Construcción de subconjuntos)\n")
                    f.write("   2. Minimización de AFD (Método: Algoritmo k-equivalente)\n\n")
                    
                    f.write("4. AUTÓMATA INTERMEDIO (AFD)\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"   Estados: {list(self.automata_afd.estados)}\n")
                    f.write(f"   Estado inicial: {self.automata_afd.estado_inicial}\n")
                    f.write(f"   Estados finales: {list(self.automata_afd.estados_finales)}\n\n")
                    
                    f.write("5. AUTÓMATA RESULTANTE FINAL (AFD MÍNIMO)\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"   Estados: {list(self.automata_minimizado.estados)}\n")
                    f.write(f"   Estado inicial: {self.automata_minimizado.estado_inicial}\n")
                    f.write(f"   Estados finales: {list(self.automata_minimizado.estados_finales)}\n\n")
                    
                    # Estadísticas
                    f.write("6. ESTADÍSTICAS\n")
                    f.write("-" * 40 + "\n")
                    # Conversión
                    afnd_est = len(self.automata_original.estados)
                    afd_est = len(self.automata_afd.estados)
                    f.write(f"   Conversión AFND → AFD:\n")
                    f.write(f"     Estados AFND: {afnd_est}\n")
                    f.write(f"     Estados AFD: {afd_est}\n")
                    f.write(f"     Factor de expansión: {afd_est/afnd_est:.2f}x\n\n")
                    # Minimización
                    min_est = len(self.automata_minimizado.estados)
                    red = afd_est - min_est
                    porc = (red/afd_est)*100 if afd_est > 0 else 0
                    f.write(f"   Minimización AFD → AFD mínimo:\n")
                    f.write(f"     Estados AFD: {afd_est}\n")
                    f.write(f"     Estados mínimos: {min_est}\n")
                    f.write(f"     Estados eliminados: {red}\n")
                    f.write(f"     Reducción: {porc:.1f}%\n")
                    
                elif op == "afnd_afd":
                    f.write("   Operación: Conversión de AFND a AFD\n")
                    f.write("   Método: Construcción de subconjuntos\n\n")
                    f.write("4. AUTÓMATA RESULTANTE (AFD)\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"   Estados: {list(self.automata_afd.estados)}\n")
                    f.write(f"   Estado inicial: {self.automata_afd.estado_inicial}\n")
                    f.write(f"   Estados finales: {list(self.automata_afd.estados_finales)}\n\n")
                    
                    # Estadísticas
                    f.write("5. ESTADÍSTICAS\n")
                    f.write("-" * 40 + "\n")
                    orig_est = len(automata_procesado.estados)
                    res_est = len(self.automata_afd.estados)
                    f.write(f"   Estados originales: {orig_est}\n")
                    f.write(f"   Estados resultantes: {res_est}\n")
                    f.write(f"   Factor de expansión: {res_est/orig_est:.2f}x\n")
                    
                elif op == "afd_min":
                    f.write("   Operación: Minimización de AFD\n")
                    f.write("   Método: Algoritmo k-equivalente\n\n")
                    f.write("4. AUTÓMATA RESULTANTE (AFD MINIMIZADO)\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"   Estados: {list(self.automata_minimizado.estados)}\n")
                    f.write(f"   Estado inicial: {self.automata_minimizado.estado_inicial}\n")
                    f.write(f"   Estados finales: {list(self.automata_minimizado.estados_finales)}\n\n")
                    
                    # Estadísticas
                    f.write("5. ESTADÍSTICAS\n")
                    f.write("-" * 40 + "\n")
                    orig_est = len(automata_procesado.estados)
                    res_est = len(self.automata_minimizado.estados)
                    red = orig_est - res_est
                    porc = (red/orig_est)*100 if orig_est > 0 else 0
                    f.write(f"   Estados originales: {orig_est}\n")
                    f.write(f"   Estados minimizados: {res_est}\n")
                    f.write(f"   Estados eliminados: {red}\n")
                    f.write(f"   Reducción: {porc:.1f}%\n")
                
                f.write("\n" + "=" * 70 + "\n")
                f.write("                    FIN DEL INFORME\n")
                f.write("=" * 70 + "\n")
                
            messagebox.showinfo("Éxito", f"Informe generado en:\n{archivo}")
            self._mostrar_estado(f"📊 Informe generado en: {archivo}\n", 'success')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe:\n{str(e)}")
            self._mostrar_estado(f"❌ Error al generar informe: {str(e)}\n", 'error')

    def _probar_cadena(self):
        """Probar una cadena en los autómatas"""
        cadena = self.entry_cadena.get().strip()
        
        if cadena == "":
            cadena = "ε"  # Cadena vacía
            
        if not self.automata_original:
            return
            
        op = self.operacion.get()
        
        try:
            # Probar en autómata original
            orig_acepta = self.automata_original.procesar_cadena(cadena if cadena != "ε" else "")
            resultado = f"Cadena '{cadena}': Original {'✓' if orig_acepta else '✗'}"
            
            resultados = [orig_acepta]
            
            # Probar en AFD si existe
            if self.automata_afd:
                afd_acepta = self.automata_afd.procesar_cadena(cadena if cadena != "ε" else "")
                resultado += f" | AFD {'✓' if afd_acepta else '✗'}"
                resultados.append(afd_acepta)
            
            # Probar en minimizado si existe
            if self.automata_minimizado:
                min_acepta = self.automata_minimizado.procesar_cadena(cadena if cadena != "ε" else "")
                resultado += f" | Minimizado {'✓' if min_acepta else '✗'}"
                resultados.append(min_acepta)
            
            # Verificar equivalencia entre todos
            if len(resultados) > 1:
                equivalente = all(r == resultados[0] for r in resultados)
                resultado += f" | {'✓ Equivalentes' if equivalente else '✗ NO equivalentes'}"
            
            # Actualizar label de resultado
            color = 'green' if orig_acepta else 'red'
            self.label_resultado_prueba.config(text=resultado, foreground=color)
            
            self._mostrar_estado(f"🔍 Prueba: {resultado}\n", 'info')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al probar cadena:\n{str(e)}")
            self._mostrar_estado(f"❌ Error al probar cadena: {str(e)}\n", 'error')

    def _generar_grafico_original(self):
        """Generar y mostrar gráfico del autómata original"""
        if not self.automata_original:
            return
        try:
            # Generar imagen si no existe
            if self.imagen_original_pil is None:
                self.imagen_original_pil = self._crear_grafico_automata(self.automata_original)
            self._mostrar_grafico_en_canvas(self.canvas_original, self.imagen_original_pil, self.zoom_original, 'original')
        except Exception as e:
            self._mostrar_estado(f"❌ Error al generar gráfico original: {str(e)}\n", 'error')
            self._mostrar_placeholder(self.canvas_original, "Error al generar gráfico")

    def _generar_grafico_afd(self):
        """Generar y mostrar gráfico del AFD convertido"""
        if not self.automata_afd:
            return
        try:
            # Generar imagen si no existe
            if self.imagen_afd_pil is None:
                self.imagen_afd_pil = self._crear_grafico_automata(self.automata_afd)
            self._mostrar_grafico_en_canvas(self.canvas_afd, self.imagen_afd_pil, self.zoom_afd, 'afd')
        except Exception as e:
            self._mostrar_estado(f"❌ Error al generar gráfico AFD: {str(e)}\n", 'error')
            self._mostrar_placeholder(self.canvas_afd, "Error al generar gráfico")

    def _generar_grafico_minimizado(self):
        """Generar y mostrar gráfico del AFD minimizado"""
        if not self.automata_minimizado:
            return
        try:
            # Generar imagen si no existe
            if self.imagen_minimizado_pil is None:
                self.imagen_minimizado_pil = self._crear_grafico_automata(self.automata_minimizado)
            self._mostrar_grafico_en_canvas(self.canvas_minimizado, self.imagen_minimizado_pil, self.zoom_minimizado, 'minimizado')
        except Exception as e:
            self._mostrar_estado(f"❌ Error al generar gráfico minimizado: {str(e)}\n", 'error')
            self._mostrar_placeholder(self.canvas_minimizado, "Error al generar gráfico")

    def _mostrar_grafico_en_canvas(self, canvas, imagen_pil, zoom=1.0, panel='original'):
        """Mostrar un gráfico en un canvas con ajuste de tamaño y zoom"""
        # La imagen ya es un objeto PIL Image
        
        # Obtener dimensiones actuales del canvas y de la imagen
        canvas.update_idletasks()  # Asegurar que el canvas tenga sus dimensiones actualizadas
        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 350
        canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 200
        img_width, img_height = imagen_pil.size
        
        # Aplicar zoom a las dimensiones originales
        zoomed_width = int(img_width * zoom)
        zoomed_height = int(img_height * zoom)
        
        # Calcular factor de escala para ajustar la imagen al canvas
        scale_factor = 1.0  # Permitir zoom ilimitado, la imagen puede ser más grande que el canvas
        
        # Calcular dimensiones finales
        final_width = int(zoomed_width * scale_factor)
        final_height = int(zoomed_height * scale_factor)
        
        # Redimensionar la imagen siempre que haya zoom o el tamaño haya cambiado
        if zoom != 1.0 or final_width != img_width or final_height != img_height:
            # Usar BICUBIC para mejor calidad en zoom
            imagen_pil = imagen_pil.resize((final_width, final_height), Image.Resampling.BICUBIC)
        
        # Convertir a PhotoImage
        imagen_tk = ImageTk.PhotoImage(imagen_pil)
        
        # Limpiar canvas y mostrar imagen centrada con offset
        canvas.delete("all")
        offset = getattr(self, f"offset_{panel}")
        x = canvas_width // 2 + offset['x']
        y = canvas_height // 2 + offset['y']
        canvas.create_image(x, y, image=imagen_tk, anchor='center')
        
        # Guardar referencia para evitar que sea recolectada por garbage collector
        canvas.image = imagen_tk

    def _crear_imagen_prueba(self, automata):
        """Crear una imagen de prueba simple cuando pydot no está disponible"""
        from PIL import Image, ImageDraw

        # Crear imagen
        img = Image.new('RGB', (400, 300), 'white')
        draw = ImageDraw.Draw(img)

        # Dibujar elementos básicos
        # Título
        draw.text((200, 30), f"Autómata: {type(automata).__name__}", fill='black', anchor='mm')

        # Estados
        y_pos = 80
        for i, estado in enumerate(automata.estados):
            color = 'lightgreen' if estado in automata.estados_finales else 'lightblue'
            draw.rectangle([50, y_pos + i*40, 150, y_pos + i*40 + 30], fill=color, outline='black')
            draw.text((100, y_pos + i*40 + 15), str(estado), fill='black', anchor='mm')

            # Marcar estado inicial
            if estado == automata.estado_inicial:
                draw.text((30, y_pos + i*40 + 15), "→", fill='red', anchor='mm')

        # Información básica
        draw.text((250, 100), f"Estados: {len(automata.estados)}", fill='black')
        draw.text((250, 130), f"Alfabeto: {list(automata.alfabeto)}", fill='black')
        draw.text((250, 160), f"Estado inicial: {automata.estado_inicial}", fill='black')
        draw.text((250, 190), f"Estados finales: {list(automata.estados_finales)}", fill='black')

        # Devolver la imagen PIL directamente
        return img

    def _zoom_canvas(self, event, panel, zoom_in=None):
        """Manejar el zoom con la rueda del ratón"""
        
        # Determinar si es zoom in o zoom out
        if zoom_in is None:
            # Para Windows/Linux con MouseWheel
            if event.delta > 0:
                zoom_in = True
            else:
                zoom_in = False
        elif zoom_in is False:
            # Para Linux con Button-4/Button-5
            zoom_in = True if event.num == 4 else False
        
        
        # Obtener la variable de zoom correspondiente
        if panel == 'original':
            zoom_var = 'zoom_original'
            canvas = self.canvas_original
            imagen_pil = self.imagen_original_pil
        elif panel == 'afd':
            zoom_var = 'zoom_afd'
            canvas = self.canvas_afd
            imagen_pil = self.imagen_afd_pil
        elif panel == 'minimizado':
            zoom_var = 'zoom_minimizado'
            canvas = self.canvas_minimizado
            imagen_pil = self.imagen_minimizado_pil
        else:
            return
        
        # Solo hacer zoom si hay una imagen cargada
        if not imagen_pil:
            print("No hay imagen cargada para hacer zoom")
            return
        
        # Calcular nuevo zoom
        current_zoom = getattr(self, zoom_var)
        if zoom_in:
            new_zoom = min(current_zoom * self.zoom_factor, self.zoom_max)
        else:
            new_zoom = max(current_zoom / self.zoom_factor, self.zoom_min)
        
        
        # Solo actualizar si cambió significativamente
        if abs(new_zoom - current_zoom) > 0.01:
            # Calcular nuevo offset para mantener el punto bajo el cursor
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 350
            canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 200
            canvas_center_x = canvas_width // 2
            canvas_center_y = canvas_height // 2
            
            # Obtener posición del mouse relativa al canvas
            mouse_x = event.x
            mouse_y = event.y
            
            # Obtener offset actual
            current_offset = getattr(self, f"offset_{panel}")
            current_offset_x = current_offset['x']
            current_offset_y = current_offset['y']
            
            # Calcular coordenadas del punto en la imagen que está bajo el cursor
            # (relativo al centro de la imagen)
            image_x = (mouse_x - canvas_center_x - current_offset_x) / current_zoom
            image_y = (mouse_y - canvas_center_y - current_offset_y) / current_zoom
            
            # Calcular nuevo offset para que ese punto siga bajo el cursor después del zoom
            new_offset_x = mouse_x - canvas_center_x - (image_x * new_zoom)
            new_offset_y = mouse_y - canvas_center_y - (image_y * new_zoom)
            
            # Aplicar nuevo zoom y offset
            setattr(self, zoom_var, new_zoom)
            setattr(self, f"offset_{panel}", {'x': new_offset_x, 'y': new_offset_y})
            
            # Aplicar zoom a la imagen guardada
            try:
                self._mostrar_grafico_en_canvas(canvas, imagen_pil, new_zoom, panel)
                
            except Exception as e:
                self._mostrar_estado(f"❌ Error al aplicar zoom: {str(e)}\n", 'error')
                print(f"Error al aplicar zoom: {e}")
        else:
            print("Cambio de zoom muy pequeño, ignorando")

    def _start_drag(self, event, panel):
        """Iniciar el arrastre de la imagen"""
        self.drag_start = {
            'x': event.x,
            'y': event.y,
            'offset': getattr(self, f"offset_{panel}").copy(),
            'panel': panel
        }

    def _drag(self, event, panel):
        """Manejar el arrastre de la imagen"""
        if self.drag_start and self.drag_start['panel'] == panel:
            dx = event.x - self.drag_start['x']
            dy = event.y - self.drag_start['y']
            offset = self.drag_start['offset']
            new_offset = {'x': offset['x'] + dx, 'y': offset['y'] + dy}
            setattr(self, f"offset_{panel}", new_offset)
            
            # Redibujar la imagen
            imagen_pil = getattr(self, f"imagen_{panel}_pil")
            if imagen_pil:
                zoom = getattr(self, f"zoom_{panel}")
                canvas = getattr(self, f"canvas_{panel}")
                self._mostrar_grafico_en_canvas(canvas, imagen_pil, zoom, panel)

    def _crear_grafico_automata(self, automata: Union[AFD, AFND]) -> Image.Image:
        """Crear gráfico de autómata usando pydot con mejor estilo"""
        try:
            # Verificar disponibilidad de graphviz
            test_grafo = pydot.Dot()
            test_grafo.create_png()
        except Exception as e:
            # Si no hay pydot/graphviz, crear una imagen de prueba simple
            print(f"Graphviz no disponible, creando imagen de prueba: {e}")
            return self._crear_imagen_prueba(automata)

        # Código original para crear gráfico con pydot...
        grafo = pydot.Dot(
            graph_type='digraph',
            rankdir='LR',
            bgcolor='white',
            dpi='96',
            size='8,6',
            ratio='compress',
            fontname='Arial',
            fontsize='11',
            ranksep='0.5',
            nodesep='0.4'
        )
        
        # Configuración de estilo para nodos
        grafo.set_node_defaults(
            fontname='Arial',
            fontsize='10',
            style='filled',
            fillcolor='lightblue',
            penwidth='2'
        )
        
        # Configuración de estilo para aristas
        grafo.set_edge_defaults(
            fontname='Arial',
            fontsize='9',
            arrowsize='0.8'
        )

        # Agregar nodo invisible para flecha inicial
        nodo_inicio = pydot.Node('__start__', shape='none', label='', width='0', height='0')
        grafo.add_node(nodo_inicio)

        # Agregar nodos del autómata
        for estado in automata.estados:
            # Configurar estilo según tipo de estado
            if estado in automata.estados_finales:
                forma = 'doublecircle'
                fillcolor = '#90EE90'  # Verde claro
            else:
                forma = 'circle'
                fillcolor = '#ADD8E6'  # Azul claro
            
            # Color especial para estado inicial
            if estado == automata.estado_inicial:
                pencolor = 'red'
                penwidth = '3'
            else:
                pencolor = 'black'
                penwidth = '2'
            
            nodo = pydot.Node(
                str(estado),
                shape=forma,
                fillcolor=fillcolor,
                color=pencolor,
                penwidth=penwidth,
                label=str(estado)
            )
            grafo.add_node(nodo)

        # Agregar flecha al estado inicial
        arista_inicial = pydot.Edge(
            '__start__',
            str(automata.estado_inicial),
            color='red',
            penwidth='2'
        )
        grafo.add_edge(arista_inicial)

        # Agrupar transiciones por origen-destino
        transiciones_agrupadas = {}
        for (estado_origen, simbolo), destinos in automata.transiciones.items():
            if isinstance(destinos, str):
                destinos = {destinos}
            
            for destino in destinos:
                key = (estado_origen, destino)
                if key not in transiciones_agrupadas:
                    transiciones_agrupadas[key] = []
                transiciones_agrupadas[key].append(simbolo)

        # Crear aristas con etiquetas agrupadas
        for (origen, destino), simbolos in transiciones_agrupadas.items():
            # Unir símbolos con comas
            etiqueta = ', '.join(sorted(simbolos))
            
            # Estilo de arista
            if origen == destino:
                # Auto-loop
                arista = pydot.Edge(
                    str(origen),
                    str(destino),
                    label=etiqueta,
                    color='#4169E1',  # Azul real
                    fontcolor='#4169E1',
                    penwidth='1.5'
                )
            else:
                # Arista normal
                arista = pydot.Edge(
                    str(origen),
                    str(destino),
                    label=etiqueta,
                    color='#696969',  # Gris oscuro
                    fontcolor='black',
                    penwidth='1.5'
                )
            grafo.add_edge(arista)

        # Renderizar a PNG y convertir a PIL Image
        png_bytes = grafo.create_png()
        return Image.open(io.BytesIO(png_bytes))

    def _mostrar_estado(self, mensaje: str, tipo='normal'):
        """Mostrar mensaje en el área de texto con formato"""
        # Configurar tags para diferentes tipos de mensajes
        self.texto_estado.tag_config('normal', foreground='#ecf0f1')
        self.texto_estado.tag_config('success', foreground='#2ecc71', font=('Consolas', 9, 'bold'))
        self.texto_estado.tag_config('error', foreground='#e74c3c', font=('Consolas', 9, 'bold'))
        self.texto_estado.tag_config('warning', foreground='#f39c12', font=('Consolas', 9, 'bold'))
        self.texto_estado.tag_config('info', foreground='#3498db', font=('Consolas', 9, 'bold'))
        self.texto_estado.tag_config('header', foreground='#9b59b6', font=('Consolas', 9, 'bold'))
        
        # Insertar mensaje con el tag correspondiente
        self.texto_estado.insert(tk.END, mensaje, tipo)
        self.texto_estado.see(tk.END)

    def _mostrar_validacion(self, validacion: Dict[str, Any]):
        """Mostrar resultados de validación con formato mejorado"""
        self._mostrar_estado("\n📋 VALIDACIÓN DEL AUTÓMATA\n", 'header')
        self._mostrar_estado("─" * 40 + "\n", 'normal')
        
        if validacion['es_valido']:
            self._mostrar_estado("✅ Estado: VÁLIDO\n", 'success')
        else:
            self._mostrar_estado("❌ Estado: INVÁLIDO\n", 'error')

        if validacion["errores"]:
            self._mostrar_estado("\n⚠️ Errores encontrados:\n", 'error')
            for error in validacion["errores"]:
                self._mostrar_estado(f"   • {error}\n", 'normal')

        if validacion["advertencias"]:
            self._mostrar_estado("\n⚠️ Advertencias:\n", 'warning')
            for adv in validacion["advertencias"]:
                self._mostrar_estado(f"   • {adv}\n", 'normal')

        self._mostrar_estado("─" * 40 + "\n", 'normal')


def main():
    """Función principal para iniciar la aplicación"""
    # Configurar aspecto de la ventana principal
    root = tk.Tk()
    
    # Intentar configurar el ícono de la ventana (opcional)
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    # Centrar la ventana en la pantalla
    window_width = 1500
    window_height = 950
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Crear y ejecutar la aplicación
    app = GUIMinimizador(root)
    root.mainloop()


if __name__ == "__main__":
    main()