import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import time
import threading
from datetime import datetime
import random

class ClasificadoraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SCADA - Sistema de Clasificación Industrial")
        self.root.geometry("1200x800")
        
        # Colores del tema industrial
        self.colors = {
            'bg_primary': '#1a1a1a',      # Negro principal
            'bg_secondary': '#2d2d2d',    # Gris oscuro
            'bg_tertiary': '#3a3a3a',     # Gris medio
            'accent_blue': '#00a8ff',     # Azul industrial
            'accent_orange': '#ff6b35',   # Naranja industrial
            'accent_green': '#00ff88',    # Verde industrial
            'text_primary': '#ffffff',    # Blanco
            'text_secondary': '#cccccc',  # Gris claro
            'warning': '#ffaa00',         # Amarillo advertencia
            'danger': '#ff4757',          # Rojo peligro
            'success': '#2ed573',         # Verde éxito
            'info': '#3742fa'             # Azul información
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Variables del sistema
        self.ser = None
        self.hardware_conectado = False
        self.modo_actual = "MODO 1"
        self.sistema_activo = False
        self.objetos_clasificados = {"pequeños": 0, "grandes": 0}
        
        # Variables para simulación
        self.simulacion_activa = False
        self.thread_simulacion = None
        
        # Variables para gráficos
        self.historial_produccion = []
        self.max_historial = 20
        
        self.configurar_estilos()
        self.crear_interfaz()
        self.conectar_hardware()
        self.iniciar_monitoreo()
        self.actualizar_graficos()
    
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos personalizados
        style.configure('Industrial.TLabelframe', 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       relief='raised')
        
        style.configure('Industrial.TLabelframe.Label',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['accent_blue'],
                       font=('Arial', 10, 'bold'))
    
    def crear_interfaz(self):
        # Header con título y estado general
        self.crear_header()
        
        # Container principal
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel superior (estado y controles)
        top_panel = tk.Frame(main_container, bg=self.colors['bg_primary'])
        top_panel.pack(fill='x', pady=(0, 10))
        
        self.crear_panel_estado_avanzado(top_panel)
        self.crear_panel_control_moderno(top_panel)
        self.crear_panel_kpi(top_panel)
        
        # Panel medio (gráficos y estadísticas)
        middle_panel = tk.Frame(main_container, bg=self.colors['bg_primary'])
        middle_panel.pack(fill='x', pady=(0, 10))
        
        self.crear_panel_graficos(middle_panel)
        self.crear_panel_estadisticas_avanzado(middle_panel)
        
        # Panel inferior (log y alertas)
        bottom_panel = tk.Frame(main_container, bg=self.colors['bg_primary'])
        bottom_panel.pack(fill='both', expand=True)
        
        self.crear_panel_log_moderno(bottom_panel)
        self.crear_panel_alertas(bottom_panel)
    
    def crear_header(self):
        header = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=80)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo y título
        title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_frame.pack(side='left', fill='y', padx=20)
        
        title_label = tk.Label(title_frame, text="⚙️ SISTEMA SCADA", 
                              font=('Arial', 20, 'bold'), 
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['accent_blue'])
        title_label.pack(anchor='w', pady=10)
        
        subtitle_label = tk.Label(title_frame, text="Clasificadora Industrial de Objetos", 
                                 font=('Arial', 12), 
                                 bg=self.colors['bg_secondary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor='w')
        
        # Estado general del sistema
        status_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        status_frame.pack(side='right', fill='y', padx=20)
        
        self.status_indicator = tk.Label(status_frame, text="●", 
                                        font=('Arial', 30), 
                                        bg=self.colors['bg_secondary'], 
                                        fg=self.colors['warning'])
        self.status_indicator.pack(side='right', padx=10, pady=15)
        
        status_text = tk.Label(status_frame, text="SISTEMA\nSTANDBY", 
                              font=('Arial', 11, 'bold'), 
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'],
                              justify='center')
        status_text.pack(side='right', pady=20)
    
    def crear_panel_estado_avanzado(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Título del panel
        title = tk.Label(frame, text="🔧 ESTADO DEL SISTEMA", 
                        font=('Arial', 12, 'bold'), 
                        bg=self.colors['bg_secondary'], 
                        fg=self.colors['accent_orange'])
        title.pack(pady=10)
        
        # Grid de indicadores
        indicators_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        indicators_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Conexión Hardware
        conn_frame = tk.Frame(indicators_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        conn_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=2)
        indicators_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(conn_frame, text="CONEXIÓN", font=('Arial', 9, 'bold'), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack(side='left', padx=10, pady=5)
        
        self.label_conexion = tk.Label(conn_frame, text="DESCONECTADO", 
                                     font=('Arial', 9, 'bold'), 
                                     bg=self.colors['bg_tertiary'], fg=self.colors['danger'])
        self.label_conexion.pack(side='right', padx=10, pady=5)
        
        # Modo actual
        modo_frame = tk.Frame(indicators_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        modo_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=2)
        
        tk.Label(modo_frame, text="MODO ACTIVO", font=('Arial', 9, 'bold'), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack(side='left', padx=10, pady=5)
        
        self.label_modo = tk.Label(modo_frame, text="MODO 1", 
                                 font=('Arial', 9, 'bold'), 
                                 bg=self.colors['bg_tertiary'], fg=self.colors['accent_blue'])
        self.label_modo.pack(side='right', padx=10, pady=5)
        
        # Estado servo
        servo_frame = tk.Frame(indicators_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        servo_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=2)
        
        tk.Label(servo_frame, text="ACTUADOR", font=('Arial', 9, 'bold'), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack(side='left', padx=10, pady=5)
        
        self.label_servo = tk.Label(servo_frame, text="REPOSO", 
                                  font=('Arial', 9, 'bold'), 
                                  bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'])
        self.label_servo.pack(side='right', padx=10, pady=5)
    
    def crear_panel_control_moderno(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Título del panel
        title = tk.Label(frame, text="🎮 PANEL DE CONTROL", 
                        font=('Arial', 12, 'bold'), 
                        bg=self.colors['bg_secondary'], 
                        fg=self.colors['accent_green'])
        title.pack(pady=10)
        
        controls_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        controls_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Botón cambiar modo (grande y prominente)
        self.btn_modo = tk.Button(controls_frame, text="⚡ CAMBIAR MODO", 
                                font=('Arial', 11, 'bold'), 
                                bg=self.colors['info'], 
                                fg='white',
                                relief='raised', bd=3,
                                command=self.cambiar_modo, 
                                cursor='hand2',
                                height=2)
        self.btn_modo.pack(fill='x', pady=5)
        
        # Botón reconectar
        self.btn_reconectar = tk.Button(controls_frame, text="🔌 RECONECTAR", 
                                      font=('Arial', 10), 
                                      bg=self.colors['danger'], 
                                      fg='white',
                                      command=self.conectar_hardware, 
                                      cursor='hand2')
        self.btn_reconectar.pack(fill='x', pady=2)
        
        # Separador visual
        separator = tk.Frame(controls_frame, height=2, bg=self.colors['accent_orange'])
        separator.pack(fill='x', pady=10)
        
        # Controles de simulación
        sim_label = tk.Label(controls_frame, text="SIMULACIÓN", 
                           font=('Arial', 9, 'bold'), 
                           bg=self.colors['bg_secondary'], 
                           fg=self.colors['text_secondary'])
        sim_label.pack(pady=(5, 2))
        
        self.btn_simular = tk.Button(controls_frame, text="▶️ INICIAR SIM", 
                                   font=('Arial', 9), 
                                   bg=self.colors['success'], 
                                   fg='white',
                                   command=self.toggle_simulacion, 
                                   cursor='hand2')
        self.btn_simular.pack(fill='x', pady=2)
        
        self.btn_reset = tk.Button(controls_frame, text="🔄 RESET", 
                                 font=('Arial', 9), 
                                 bg=self.colors['warning'], 
                                 fg='white',
                                 command=self.reset_estadisticas, 
                                 cursor='hand2')
        self.btn_reset.pack(fill='x', pady=2)
    
    def crear_panel_kpi(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        title = tk.Label(frame, text="📊 KPI TIEMPO REAL", 
                        font=('Arial', 12, 'bold'), 
                        bg=self.colors['bg_secondary'], 
                        fg=self.colors['accent_orange'])
        title.pack(pady=10)
        
        kpi_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        kpi_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Throughput
        throughput_frame = tk.Frame(kpi_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        throughput_frame.pack(fill='x', pady=3)
        
        tk.Label(throughput_frame, text="THROUGHPUT", font=('Arial', 8, 'bold'), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack()
        self.label_throughput = tk.Label(throughput_frame, text="0 obj/min", 
                                       font=('Arial', 12, 'bold'), 
                                       bg=self.colors['bg_tertiary'], fg=self.colors['accent_green'])
        self.label_throughput.pack()
        
        # Tiempo online
        uptime_frame = tk.Frame(kpi_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        uptime_frame.pack(fill='x', pady=3)
        
        tk.Label(uptime_frame, text="TIEMPO ONLINE", font=('Arial', 8, 'bold'), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack()
        self.label_uptime = tk.Label(uptime_frame, text="00:00:00", 
                                   font=('Arial', 11, 'bold'), 
                                   bg=self.colors['bg_tertiary'], fg=self.colors['accent_blue'])
        self.label_uptime.pack()
        
        # Eficiencia
        efficiency_frame = tk.Frame(kpi_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        efficiency_frame.pack(fill='x', pady=3)
        
        tk.Label(efficiency_frame, text="EFICIENCIA", font=('Arial', 8, 'bold'), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack()
        self.label_efficiency = tk.Label(efficiency_frame, text="100%", 
                                       font=('Arial', 12, 'bold'), 
                                       bg=self.colors['bg_tertiary'], fg=self.colors['success'])
        self.label_efficiency.pack()
    
    def crear_panel_graficos(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        title = tk.Label(frame, text="📈 PRODUCCIÓN EN TIEMPO REAL", 
                        font=('Arial', 12, 'bold'), 
                        bg=self.colors['bg_secondary'], 
                        fg=self.colors['accent_blue'])
        title.pack(pady=5)
        
        # Canvas para gráfico simple
        self.canvas_grafico = tk.Canvas(frame, height=120, 
                                      bg=self.colors['bg_tertiary'], 
                                      highlightthickness=0)
        self.canvas_grafico.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Leyenda
        legend_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        legend_frame.pack(fill='x', padx=10, pady=2)
        
        tk.Label(legend_frame, text="● Pequeños", font=('Arial', 8), 
                bg=self.colors['bg_secondary'], fg=self.colors['accent_blue']).pack(side='left', padx=5)
        tk.Label(legend_frame, text="● Grandes", font=('Arial', 8), 
                bg=self.colors['bg_secondary'], fg=self.colors['accent_orange']).pack(side='left', padx=5)
    
    def crear_panel_estadisticas_avanzado(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        title = tk.Label(frame, text="🎯 ESTADÍSTICAS DETALLADAS", 
                        font=('Arial', 12, 'bold'), 
                        bg=self.colors['bg_secondary'], 
                        fg=self.colors['accent_green'])
        title.pack(pady=5)
        
        stats_container = tk.Frame(frame, bg=self.colors['bg_secondary'])
        stats_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Objetos pequeños
        small_frame = tk.Frame(stats_container, bg=self.colors['bg_tertiary'], relief='raised', bd=2)
        small_frame.pack(fill='x', pady=3)
        
        tk.Label(small_frame, text="🔹 OBJETOS PEQUEÑOS", 
                font=('Arial', 10, 'bold'), 
                bg=self.colors['bg_tertiary'], 
                fg=self.colors['text_primary']).pack(pady=2)
        
        self.label_pequeños = tk.Label(small_frame, text="0", 
                                     font=('Arial', 24, 'bold'), 
                                     bg=self.colors['bg_tertiary'], 
                                     fg=self.colors['accent_blue'])
        self.label_pequeños.pack(pady=5)
        
        # Objetos grandes
        large_frame = tk.Frame(stats_container, bg=self.colors['bg_tertiary'], relief='raised', bd=2)
        large_frame.pack(fill='x', pady=3)
        
        tk.Label(large_frame, text="🔸 OBJETOS GRANDES", 
                font=('Arial', 10, 'bold'), 
                bg=self.colors['bg_tertiary'], 
                fg=self.colors['text_primary']).pack(pady=2)
        
        self.label_grandes = tk.Label(large_frame, text="0", 
                                    font=('Arial', 24, 'bold'), 
                                    bg=self.colors['bg_tertiary'], 
                                    fg=self.colors['accent_orange'])
        self.label_grandes.pack(pady=5)
        
        # Total
        total_frame = tk.Frame(stats_container, bg=self.colors['accent_green'], relief='raised', bd=2)
        total_frame.pack(fill='x', pady=3)
        
        tk.Label(total_frame, text="📊 TOTAL PROCESADOS", 
                font=('Arial', 10, 'bold'), 
                bg=self.colors['accent_green'], 
                fg='white').pack(pady=2)
        
        self.label_total = tk.Label(total_frame, text="0", 
                                  font=('Arial', 28, 'bold'), 
                                  bg=self.colors['accent_green'], 
                                  fg='white')
        self.label_total.pack(pady=5)
    
    def crear_panel_log_moderno(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        title_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        title_frame.pack(fill='x', pady=5)
        
        tk.Label(title_frame, text="📝 LOG DEL SISTEMA", 
                font=('Arial', 12, 'bold'), 
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary']).pack(side='left', padx=10)
        
        # Botón limpiar log
        clear_btn = tk.Button(title_frame, text="🗑️ Limpiar", 
                             font=('Arial', 8), 
                             bg=self.colors['warning'], 
                             fg='white',
                             command=self.limpiar_log, 
                             cursor='hand2')
        clear_btn.pack(side='right', padx=10)
        
        self.text_log = scrolledtext.ScrolledText(frame, 
                                                height=15, 
                                                font=('Consolas', 9), 
                                                bg='#000000', 
                                                fg=self.colors['accent_green'],
                                                insertbackground=self.colors['accent_green'],
                                                selectbackground=self.colors['accent_blue'])
        self.text_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    
    def crear_panel_alertas(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        title = tk.Label(frame, text="⚠️ CENTRO DE ALERTAS", 
                        font=('Arial', 12, 'bold'), 
                        bg=self.colors['bg_secondary'], 
                        fg=self.colors['warning'])
        title.pack(pady=5)
        
        # Área de alertas
        self.alerts_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        self.alerts_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Alerta por defecto
        default_alert = tk.Frame(self.alerts_frame, bg=self.colors['bg_tertiary'], relief='sunken', bd=1)
        default_alert.pack(fill='x', pady=2)
        
        tk.Label(default_alert, text="ℹ️ Sistema iniciado correctamente", 
                font=('Arial', 9), 
                bg=self.colors['bg_tertiary'], 
                fg=self.colors['text_secondary']).pack(pady=5, padx=10)
    
    def limpiar_log(self):
        self.text_log.delete(1.0, tk.END)
        self.log_mensaje("📝 Log limpiado", self.colors['warning'])
    
    def actualizar_graficos(self):
        """Actualizar el gráfico de producción"""
        try:
            self.canvas_grafico.delete("all")
            
            if len(self.historial_produccion) > 1:
                width = self.canvas_grafico.winfo_width()
                height = self.canvas_grafico.winfo_height()
                
                if width > 1 and height > 1:
                    # Dibujar grid
                    for i in range(0, width, 50):
                        self.canvas_grafico.create_line(i, 0, i, height, 
                                                      fill=self.colors['bg_primary'], width=1)
                    for i in range(0, height, 20):
                        self.canvas_grafico.create_line(0, i, width, i, 
                                                      fill=self.colors['bg_primary'], width=1)
                    
                    # Dibujar datos
                    if len(self.historial_produccion) > 0:
                        max_val = max([p + g for p, g in self.historial_produccion]) or 1
                        step_x = width / (self.max_historial - 1)
                        
                        # Línea de pequeños
                        points_small = []
                        for i, (small, large) in enumerate(self.historial_produccion):
                            x = i * step_x
                            y = height - (small / max_val * height * 0.8)
                            points_small.extend([x, y])
                        
                        if len(points_small) > 2:
                            self.canvas_grafico.create_line(points_small, 
                                                          fill=self.colors['accent_blue'], 
                                                          width=2, smooth=True)
                        
                        # Línea de grandes
                        points_large = []
                        for i, (small, large) in enumerate(self.historial_produccion):
                            x = i * step_x
                            y = height - (large / max_val * height * 0.8)
                            points_large.extend([x, y])
                        
                        if len(points_large) > 2:
                            self.canvas_grafico.create_line(points_large, 
                                                          fill=self.colors['accent_orange'], 
                                                          width=2, smooth=True)
        except:
            pass
        
        # Programar próxima actualización
        self.root.after(2000, self.actualizar_graficos)
    
    def log_mensaje(self, mensaje, color=None):
        if color is None:
            color = self.colors['accent_green']
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        mensaje_completo = f"[{timestamp}] {mensaje}\n"
        
        self.text_log.insert('end', mensaje_completo)
        self.text_log.see('end')
        
        # Mantener solo las últimas 100 líneas
        lines = self.text_log.get('1.0', 'end').split('\n')
        if len(lines) > 100:
            self.text_log.delete('1.0', '2.0')
        
        # Actualizar indicador de estado
        if "Error" in mensaje or "❌" in mensaje:
            self.status_indicator.config(fg=self.colors['danger'])
        elif "✅" in mensaje or "conectado" in mensaje.lower():
            self.status_indicator.config(fg=self.colors['success'])
        else:
            self.status_indicator.config(fg=self.colors['warning'])
    
    def conectar_hardware(self):
        puertos = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]
        
        for puerto in puertos:
            try:
                self.ser = serial.Serial(puerto, 9600, timeout=1)
                time.sleep(2)
                
                self.ser.write(b"C\n")
                time.sleep(0.5)
                if self.ser.in_waiting > 0:
                    respuesta = self.ser.readline().decode().strip()
                    if "Modo cambiado" in respuesta:
                        self.hardware_conectado = True
                        self.label_conexion.config(text="CONECTADO", fg=self.colors['success'])
                        self.log_mensaje(f"✅ Hardware conectado en {puerto}")
                        self.btn_reconectar.config(bg=self.colors['success'], text='✅ CONECTADO')
                        self.status_indicator.config(fg=self.colors['success'])
                        return
                self.ser.close()
            except:
                continue
        
        self.hardware_conectado = False
        self.label_conexion.config(text="SIM MODE", fg=self.colors['warning'])
        self.log_mensaje("⚠️ Hardware no detectado - Modo simulación activo")
        self.btn_reconectar.config(bg=self.colors['danger'], text='🔌 RECONECTAR')
    
    def cambiar_modo(self):
        if self.hardware_conectado:
            try:
                self.ser.write(b"C\n")
                time.sleep(0.1)
                respuesta = ""
                while self.ser.in_waiting > 0:
                    linea = self.ser.readline().decode().strip()
                    if linea:
                        respuesta = linea
                        self.log_mensaje(f"Arduino: {linea}")
                
                if "MODO 1" in respuesta:
                    self.modo_actual = "MODO 1"
                    self.label_modo.config(text="MODO 1", fg=self.colors['accent_blue'])
                elif "MODO 2" in respuesta:
                    self.modo_actual = "MODO 2"
                    self.label_modo.config(text="MODO 2", fg=self.colors['accent_orange'])
                    
            except Exception as e:
                self.log_mensaje(f"❌ Error al cambiar modo: {e}")
        else:
            if self.modo_actual == "MODO 1":
                self.modo_actual = "MODO 2"
                self.label_modo.config(text="MODO 2", fg=self.colors['accent_orange'])
                self.log_mensaje("⚡ MODO 2 ACTIVADO - Clasificando objetos GRANDES")
            else:
                self.modo_actual = "MODO 1"
                self.label_modo.config(text="MODO 1", fg=self.colors['accent_blue'])
                self.log_mensaje("⚡ MODO 1 ACTIVADO - Clasificando objetos PEQUEÑOS")
    
    def toggle_simulacion(self):
        if not self.simulacion_activa:
            self.simulacion_activa = True
            self.btn_simular.config(text="⏹️ DETENER", bg=self.colors['danger'])
            self.thread_simulacion = threading.Thread(target=self.ejecutar_simulacion, daemon=True)
            self.thread_simulacion.start()
            self.log_mensaje("🎮 Simulación iniciada")
            self.status_indicator.config(fg=self.colors['success'])
        else:
            self.simulacion_activa = False
            self.btn_simular.config(text="▶️ INICIAR SIM", bg=self.colors['success'])
            self.log_mensaje("⏹️ Simulación detenida")
    
    def ejecutar_simulacion(self):
        while self.simulacion_activa:
            time.sleep(random.uniform(3, 8))
            if not self.simulacion_activa:
                break
                
            if self.modo_actual == "MODO 1":
                if random.random() < 0.8:
                    self.simular_clasificacion("pequeño")
            else:
                if random.random() < 0.7:
                    self.simular_clasificacion("grande")
    
    def simular_clasificacion(self, tipo):
        if tipo == "pequeño":
            self.objetos_clasificados["pequeños"] += 1
            self.log_mensaje("🔹 Objeto CLASIFICADO: PEQUEÑO")
        else:
            self.objetos_clasificados["grandes"] += 1
            self.log_mensaje("🔸 Objeto CLASIFICADO: GRANDE")
        
        self.root.after(0, self.simular_servo_activacion)
        self.actualizar_estadisticas()
        
        # Actualizar historial para gráficos
        self.historial_produccion.append((self.objetos_clasificados["pequeños"], 
                                         self.objetos_clasificados["grandes"]))
        if len(self.historial_produccion) > self.max_historial:
            self.historial_produccion.pop(0)
    
    def simular_servo_activacion(self):
        self.label_servo.config(text="ACTIVO", fg=self.colors['success'])
        self.log_mensaje("⚙️ ACTUADOR ACTIVADO - Filtrando objeto...")
        
        def restaurar_servo():
            self.label_servo.config(text="REPOSO", fg=self.colors['text_secondary'])
            self.log_mensaje("⚙️ Actuador en REPOSO")
        
        self.root.after(2000, restaurar_servo)
    
    def iniciar_monitoreo(self):
        """Monitorear mensajes del hardware si está conectado"""
        if self.hardware_conectado and self.ser:
            try:
                while self.ser.in_waiting > 0:
                    mensaje = self.ser.readline().decode().strip()
                    if mensaje:
                        self.procesar_mensaje_arduino(mensaje)
            except:
                pass
        
        # Actualizar KPIs
        self.actualizar_kpis()
        
        # Programar próxima verificación
        self.root.after(100, self.iniciar_monitoreo)
    
    def actualizar_kpis(self):
        """Actualizar los indicadores KPI"""
        try:
            # Throughput simulado
            total = self.objetos_clasificados["pequeños"] + self.objetos_clasificados["grandes"]
            if hasattr(self, 'start_time'):
                elapsed_time = time.time() - self.start_time
                throughput = (total / max(elapsed_time/60, 1))  # objetos por minuto
                self.label_throughput.config(text=f"{throughput:.1f} obj/min")
            else:
                self.start_time = time.time()
                self.label_throughput.config(text="0.0 obj/min")
            
            # Tiempo online
            if hasattr(self, 'start_time'):
                uptime = int(time.time() - self.start_time)
                hours = uptime // 3600
                minutes = (uptime % 3600) // 60
                seconds = uptime % 60
                self.label_uptime.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Eficiencia (simulada)
            efficiency = random.randint(95, 100) if self.simulacion_activa or self.hardware_conectado else 100
            self.label_efficiency.config(text=f"{efficiency}%")
            
        except:
            pass
    
    def procesar_mensaje_arduino(self, mensaje):
        self.log_mensaje(f"Arduino: {mensaje}")
        
        if "PEQUEÑO" in mensaje:
            self.objetos_clasificados["pequeños"] += 1
            self.actualizar_estadisticas()
        elif "GRANDE" in mensaje:
            self.objetos_clasificados["grandes"] += 1
            self.actualizar_estadisticas()
        elif "Servo ACTIVADO" in mensaje:
            self.label_servo.config(text="ACTIVO", fg=self.colors['success'])
        elif "Servo regresó a REPOSO" in mensaje:
            self.label_servo.config(text="REPOSO", fg=self.colors['text_secondary'])
        elif "MODO 1" in mensaje:
            self.modo_actual = "MODO 1"
            self.label_modo.config(text="MODO 1", fg=self.colors['accent_blue'])
        elif "MODO 2" in mensaje:
            self.modo_actual = "MODO 2"
            self.label_modo.config(text="MODO 2", fg=self.colors['accent_orange'])
    
    def actualizar_estadisticas(self):
        self.label_pequeños.config(text=str(self.objetos_clasificados["pequeños"]))
        self.label_grandes.config(text=str(self.objetos_clasificados["grandes"]))
        total = self.objetos_clasificados["pequeños"] + self.objetos_clasificados["grandes"]
        self.label_total.config(text=str(total))
        
        # Actualizar historial para gráficos
        self.historial_produccion.append((self.objetos_clasificados["pequeños"], 
                                         self.objetos_clasificados["grandes"]))
        if len(self.historial_produccion) > self.max_historial:
            self.historial_produccion.pop(0)
    
    def reset_estadisticas(self):
        respuesta = messagebox.askyesno("Confirmar Reset", 
                                      "¿Está seguro de resetear todas las estadísticas?")
        if respuesta:
            self.objetos_clasificados = {"pequeños": 0, "grandes": 0}
            self.historial_produccion = []
            self.actualizar_estadisticas()
            self.log_mensaje("🔄 Estadísticas reseteadas", self.colors['warning'])
    
    def on_closing(self):
        if self.simulacion_activa:
            self.simulacion_activa = False
        if self.hardware_conectado and self.ser:
            self.ser.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClasificadoraGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Mensaje de bienvenida
    app.log_mensaje("🚀 SISTEMA SCADA INICIADO")
    app.log_mensaje("💡 Modo simulación disponible si no hay hardware")
    app.log_mensaje("⚡ Sistema listo para operar")
    
    root.mainloop()