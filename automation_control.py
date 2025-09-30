import customtkinter as ctk
from tkinter import messagebox
import serial
import time
import threading
from datetime import datetime
import random

# Configuración del tema
ctk.set_appearance_mode("dark")  # Modo oscuro
ctk.set_default_color_theme("blue")  # Tema azul

class ClasificadoraModerna:
    def __init__(self):
        # Ventana principal
        self.root = ctk.CTk()
        self.root.title("🏭 SISTEMA SCADA - Clasificadora Industrial")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')  # Maximizar en Windows
        # Alternativa para sistemas Unix: self.root.attributes('-zoomed', True)
        self.root.resizable(True, True)  # Permitir redimensionar
        self.root.minsize(1600, 900)  # Tamaño mínimo
        
        # Variables del sistema
        self.ser = None
        self.hardware_conectado = False
        self.modo_actual = "Objetos Pequeños"
        self.sistema_activo = False
        self.objetos_clasificados = {"pequeños": 0, "grandes": 0}
        
        # Variables para simulación
        self.simulacion_activa = False
        self.thread_simulacion = None
        
        # Variables para gráficos
        self.historial_produccion = []
        self.max_historial = 20
        
        self.start_time = time.time()
        
        # Crear interfaz primero (rápido)
        self.crear_interfaz()
        
        # Mostrar ventana inmediatamente
        self.root.update()
        
        # Ejecutar tareas pesadas en segundo plano después de mostrar la UI
        self.root.after(100, self.inicializar_sistema_async)
    
    def inicializar_sistema_async(self):
        """Inicializar componentes pesados después de mostrar la UI"""
        # Mostrar mensaje de inicialización
        self.log_mensaje("🔄 Inicializando sistema...")
        
        # Conectar hardware en un hilo separado para no bloquear la UI
        threading.Thread(target=self.conectar_hardware_async, daemon=True).start()
        
        # Iniciar monitoreo con delay para no sobrecargar al inicio
        self.root.after(500, self.iniciar_monitoreo)
        
        self.log_mensaje("✅ Sistema inicializado")
    
    def conectar_hardware_async(self):
        """Conectar hardware de forma asíncrona"""
        try:
            self.conectar_hardware()
        except Exception as e:
            self.root.after(0, lambda error=str(e): self.log_mensaje(f"❌ Error en inicialización: {error}"))
    
    def crear_interfaz(self):
        # Header principal
        self.crear_header_moderno()
        
        # Container principal sin scroll
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Panel superior - Estado y Control
        self.crear_panel_superior()
        
        # Panel medio - Estadísticas y KPIs
        self.crear_panel_estadisticas()
        
        # Panel inferior - Log y Control avanzado
        self.crear_panel_inferior()
    
    def crear_header_moderno(self):
        # Frame del header
        header_frame = ctk.CTkFrame(self.root, height=70, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = ctk.CTkLabel(header_frame, 
                                  text="⚙️ SISTEMA SCADA", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left", padx=25, pady=15)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(header_frame, 
                                     text="Clasificadora Industrial de Objetos", 
                                     font=ctk.CTkFont(size=12),
                                     text_color="gray70")
        subtitle_label.pack(side="left", padx=(10, 0), pady=15)
        
        # Indicador de estado general
        self.status_frame = ctk.CTkFrame(header_frame, width=200, height=50)
        self.status_frame.pack(side="right", padx=30, pady=15)
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.status_frame, 
                                        text="🟡 SISTEMA STANDBY", 
                                        font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(expand=True)
    
    def crear_panel_superior(self):
        # Container del panel superior
        top_container = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=250)
        top_container.pack(fill="x", pady=(0, 15))
        top_container.pack_propagate(False)
        
        # Panel de estado (izquierda)
        estado_frame = ctk.CTkFrame(top_container)
        estado_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(estado_frame, 
                    text="🔧 ESTADO DEL SISTEMA", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Indicadores de estado
        self.crear_indicadores_estado(estado_frame)
        
        # Panel de control (centro)
        control_frame = ctk.CTkFrame(top_container)
        control_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(control_frame, 
                    text="🎮 PANEL DE CONTROL", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.crear_controles_principales(control_frame)
        
        # Panel KPI (derecha)
        kpi_frame = ctk.CTkFrame(top_container)
        kpi_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(kpi_frame, 
                    text="📊 KPI TIEMPO REAL", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.crear_kpis_modernos(kpi_frame)
    
    def crear_indicadores_estado(self, parent):
        # Conexión
        conn_frame = ctk.CTkFrame(parent, height=40)
        conn_frame.pack(fill="x", padx=15, pady=8)
        conn_frame.pack_propagate(False)
        
        ctk.CTkLabel(conn_frame, text="CONEXIÓN HARDWARE", 
                    font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10, pady=10)
        
        self.label_conexion = ctk.CTkLabel(conn_frame, text="DESCONECTADO", 
                                         font=ctk.CTkFont(size=11, weight="bold"),
                                         text_color="red")
        self.label_conexion.pack(side="right", padx=10, pady=10)
        
        # Modo actual
        modo_frame = ctk.CTkFrame(parent, height=40)
        modo_frame.pack(fill="x", padx=15, pady=8)
        modo_frame.pack_propagate(False)
        
        ctk.CTkLabel(modo_frame, text="MODO ACTIVO", 
                    font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10, pady=10)
        
        self.label_modo = ctk.CTkLabel(modo_frame, text="Objetos Pequeños", 
                                     font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#1f6aa5")
        self.label_modo.pack(side="right", padx=10, pady=10)
        
        # Estado actuador
        servo_frame = ctk.CTkFrame(parent, height=40)
        servo_frame.pack(fill="x", padx=15, pady=8)
        servo_frame.pack_propagate(False)
        
        ctk.CTkLabel(servo_frame, text="ACTUADOR", 
                    font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10, pady=10)
        
        self.label_servo = ctk.CTkLabel(servo_frame, text="REPOSO", 
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color="gray50")
        self.label_servo.pack(side="right", padx=10, pady=10)
    
    def crear_controles_principales(self, parent):
        # Botón principal - Cambiar modo
        self.btn_modo = ctk.CTkButton(parent, 
                                     text="⚡ CAMBIAR MODO DE CLASIFICACIÓN", 
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     height=50,
                                     command=self.cambiar_modo)
        self.btn_modo.pack(fill="x", padx=15, pady=10)
        
        # Botón reconectar
        self.btn_reconectar = ctk.CTkButton(parent, 
                                          text="🔌 RECONECTAR HARDWARE", 
                                          font=ctk.CTkFont(size=12),
                                          height=40,
                                          fg_color="#e74c3c",
                                          hover_color="#c0392b",
                                          command=self.conectar_hardware)
        self.btn_reconectar.pack(fill="x", padx=15, pady=5)
        
        # Separador
        separator = ctk.CTkFrame(parent, height=2)
        separator.pack(fill="x", padx=20, pady=15)
        
        # Sección simulación
        ctk.CTkLabel(parent, text="🎮 SIMULACIÓN", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 5))
        
        self.btn_simular = ctk.CTkButton(parent, 
                                       text="▶️ INICIAR SIMULACIÓN", 
                                       font=ctk.CTkFont(size=12),
                                       height=40,
                                       fg_color="#27ae60",
                                       hover_color="#229954",
                                       command=self.toggle_simulacion)
        self.btn_simular.pack(fill="x", padx=15, pady=5)
        
        self.btn_reset = ctk.CTkButton(parent, 
                                     text="🔄 RESET ESTADÍSTICAS", 
                                     font=ctk.CTkFont(size=12),
                                     height=35,
                                     fg_color="#f39c12",
                                     hover_color="#e67e22",
                                     command=self.reset_estadisticas)
        self.btn_reset.pack(fill="x", padx=15, pady=5)
    
    def crear_kpis_modernos(self, parent):
        # Throughput
        throughput_frame = ctk.CTkFrame(parent, height=80)
        throughput_frame.pack(fill="x", padx=15, pady=12)
        throughput_frame.pack_propagate(False)
        
        ctk.CTkLabel(throughput_frame, text="THROUGHPUT", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(12, 4))
        self.label_throughput = ctk.CTkLabel(throughput_frame, text="0.0 obj/min", 
                                           font=ctk.CTkFont(size=18, weight="bold"),
                                           text_color="#27ae60")
        self.label_throughput.pack(pady=(0, 12))
        
        # Tiempo online
        uptime_frame = ctk.CTkFrame(parent, height=80)
        uptime_frame.pack(fill="x", padx=15, pady=12)
        uptime_frame.pack_propagate(False)
        
        ctk.CTkLabel(uptime_frame, text="TIEMPO ONLINE", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(12, 4))
        self.label_uptime = ctk.CTkLabel(uptime_frame, text="00:00:00", 
                                       font=ctk.CTkFont(size=18, weight="bold"),
                                       text_color="#3498db")
        self.label_uptime.pack(pady=(0, 12))
    
    def crear_panel_estadisticas(self):
        # Container de estadísticas
        stats_container = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=180)
        stats_container.pack(fill="x", pady=(0, 15))
        stats_container.pack_propagate(False)
        
        # Título
        ctk.CTkLabel(stats_container, 
                    text="📈 ESTADÍSTICAS DE PRODUCCIÓN", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))
        
        # Frame de las tarjetas de estadísticas
        cards_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        cards_frame.pack(fill="x")
        
        # Tarjeta objetos pequeños
        small_card = ctk.CTkFrame(cards_frame)
        small_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(small_card, text="🔹 OBJETOS PEQUEÑOS", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.label_pequeños = ctk.CTkLabel(small_card, text="0", 
                                         font=ctk.CTkFont(size=36, weight="bold"),
                                         text_color="#3498db")
        self.label_pequeños.pack(pady=10)
        
        # Tarjeta objetos grandes
        large_card = ctk.CTkFrame(cards_frame)
        large_card.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(large_card, text="🔸 OBJETOS GRANDES", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.label_grandes = ctk.CTkLabel(large_card, text="0", 
                                        font=ctk.CTkFont(size=36, weight="bold"),
                                        text_color="#e67e22")
        self.label_grandes.pack(pady=10)
        
        # Tarjeta total
        total_card = ctk.CTkFrame(cards_frame, fg_color="#27ae60")
        total_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(total_card, text="📊 TOTAL PROCESADOS", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white").pack(pady=10)
        
        self.label_total = ctk.CTkLabel(total_card, text="0", 
                                      font=ctk.CTkFont(size=40, weight="bold"),
                                      text_color="white")
        self.label_total.pack(pady=10)
    
    def crear_panel_inferior(self):
        # Container inferior con altura fija
        bottom_container = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=320)
        bottom_container.pack(fill="x", expand=False)
        bottom_container.pack_propagate(False)
        
        # Panel de log (izquierda - más ancho)
        log_frame = ctk.CTkFrame(bottom_container)
        log_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Header del log con botón limpiar
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent", height=40)
        log_header.pack(fill="x", padx=10, pady=5)
        log_header.pack_propagate(False)
        
        ctk.CTkLabel(log_header, text="📝 LOG DEL SISTEMA", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", pady=8)
        
        clear_btn = ctk.CTkButton(log_header, text="🗑️ Limpiar", 
                                 width=70, height=25,
                                 font=ctk.CTkFont(size=9),
                                 fg_color="#f39c12",
                                 hover_color="#e67e22",
                                 command=self.limpiar_log)
        clear_btn.pack(side="right", pady=8)
        
        # Área de texto del log
        self.text_log = ctk.CTkTextbox(log_frame, 
                                      height=280,
                                      font=ctk.CTkFont(family="Consolas", size=9),
                                      fg_color="#1a1a1a",
                                      text_color="#00ff88")
        self.text_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Panel de control avanzado (derecha - más compacto)
        advanced_frame = ctk.CTkFrame(bottom_container, width=280)
        advanced_frame.pack(side="right", fill="y", padx=(10, 0))
        advanced_frame.pack_propagate(False)
        
        ctk.CTkLabel(advanced_frame, text="⚙️ CONTROL AVANZADO", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(pady=8)
        
        # Switch para modo automático
        self.auto_switch = ctk.CTkSwitch(advanced_frame, text="Modo Automático",
                                        font=ctk.CTkFont(size=11))
        self.auto_switch.pack(pady=8, padx=15)
        
        # Slider para velocidad de simulación
        ctk.CTkLabel(advanced_frame, text="Velocidad Simulación", 
                    font=ctk.CTkFont(size=10)).pack(pady=(8, 0))
        
        self.speed_slider = ctk.CTkSlider(advanced_frame, from_=1, to=10, 
                                         number_of_steps=9, height=16,
                                         command=self.cambiar_velocidad_sim)
        self.speed_slider.set(5)
        self.speed_slider.pack(pady=5, padx=15)
        
        self.speed_label = ctk.CTkLabel(advanced_frame, text="5x", 
                                       font=ctk.CTkFont(size=10))
        self.speed_label.pack()
        
        # Progress bar para mostrar actividad
        ctk.CTkLabel(advanced_frame, text="Actividad del Sistema", 
                    font=ctk.CTkFont(size=10)).pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(advanced_frame, height=16)
        self.progress_bar.pack(pady=5, padx=15)
        self.progress_bar.set(0)
        
        # Información adicional del sistema
        info_frame = ctk.CTkFrame(advanced_frame)
        info_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(info_frame, text="💻 SISTEMA", 
                    font=ctk.CTkFont(size=9, weight="bold")).pack(pady=2)
        ctk.CTkLabel(info_frame, text="1920x1080 Optimizado", 
                    font=ctk.CTkFont(size=8),
                    text_color="gray60").pack()
    
    def cambiar_velocidad_sim(self, value):
        self.speed_label.configure(text=f"{int(value)}x")
    
    def limpiar_log(self):
        self.text_log.delete("0.0", "end")
        self.log_mensaje("📝 Log limpiado")
    
    def log_mensaje(self, mensaje):
        timestamp = datetime.now().strftime("%H:%M:%S")
        mensaje_completo = f"[{timestamp}] {mensaje}\n"
        
        self.text_log.insert("end", mensaje_completo)
        self.text_log.see("end")
        
        # Mantener solo las últimas 100 líneas
        content = self.text_log.get("0.0", "end")
        lines = content.split('\n')
        if len(lines) > 100:
            # Mantener solo las últimas 100 líneas
            new_content = '\n'.join(lines[-100:])
            self.text_log.delete("0.0", "end")
            self.text_log.insert("0.0", new_content)
        
        # Actualizar indicador de estado
        if "Error" in mensaje or "❌" in mensaje:
            self.status_label.configure(text="🔴 SISTEMA ERROR", text_color="red")
        elif "✅" in mensaje or "conectado" in mensaje.lower():
            self.status_label.configure(text="🟢 SISTEMA ACTIVO", text_color="green")
        else:
            self.status_label.configure(text="🟡 SISTEMA OPERANDO", text_color="#f39c12")
    
    def conectar_hardware(self):
        puertos = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]
        
        self.root.after(0, lambda: self.log_mensaje("🔍 Buscando hardware..."))
        
        for puerto in puertos:
            try:
                # Actualizar estado en la UI mientras busca
                self.root.after(0, lambda p=puerto: self.log_mensaje(f"🔍 Probando {p}..."))
                
                # Timeout más corto para respuesta más rápida
                self.ser = serial.Serial(puerto, 9600, timeout=0.5)
                time.sleep(1)  # Reducido de 2 a 1 segundo
                
                self.ser.write(b"C\n")
                time.sleep(0.3)  # Reducido de 0.5 a 0.3 segundos
                if self.ser.in_waiting > 0:
                    respuesta = self.ser.readline().decode().strip()
                    if "Modo cambiado" in respuesta:
                        self.hardware_conectado = True
                        self.root.after(0, lambda: self.label_conexion.configure(text="CONECTADO", text_color="green"))
                        self.root.after(0, lambda: self.log_mensaje(f"✅ Hardware conectado en {puerto}"))
                        self.root.after(0, lambda: self.btn_reconectar.configure(fg_color="#27ae60", text='✅ CONECTADO'))
                        return
                self.ser.close()
            except Exception:
                continue
        
        self.hardware_conectado = False
        self.root.after(0, lambda: self.label_conexion.configure(text="MODO SIMULACIÓN", text_color="#f39c12"))
        self.root.after(0, lambda: self.log_mensaje("⚠️ Hardware no detectado - Modo simulación activo"))
        self.root.after(0, lambda: self.btn_reconectar.configure(fg_color="#e74c3c", text='🔌 RECONECTAR'))
    
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
                
                if "Objetos Pequeños" in respuesta:
                    self.modo_actual = "Objetos Pequeños"
                    self.label_modo.configure(text="Objetos Pequeños", text_color="#3498db")
                elif "Objetos Grandes" in respuesta:
                    self.modo_actual = "Objetos Grandes"
                    self.label_modo.configure(text="Objetos Grandes", text_color="#e67e22")
                    
            except Exception as e:
                self.log_mensaje(f"❌ Error al cambiar modo: {e}")
        else:
            if self.modo_actual == "Objetos Pequeños":
                self.modo_actual = "Objetos Grandes"
                self.label_modo.configure(text="Objetos Grandes", text_color="#e67e22")
                self.log_mensaje("⚡ Objetos Grandes ACTIVADO - Clasificando objetos GRANDES")
                self.btn_modo.configure(text="⚡ CAMBIAR A Objetos Pequeños")
            else:
                self.modo_actual = "Objetos Pequeños"
                self.label_modo.configure(text="Objetos Pequeños", text_color="#3498db")
                self.log_mensaje("⚡ Objetos Pequeños ACTIVADO - Clasificando objetos PEQUEÑOS")
                self.btn_modo.configure(text="⚡ CAMBIAR A Objetos Grandes")
    
    def toggle_simulacion(self):
        if not self.simulacion_activa:
            self.simulacion_activa = True
            self.btn_simular.configure(text="⏹️ DETENER SIMULACIÓN", fg_color="#e74c3c")
            self.thread_simulacion = threading.Thread(target=self.ejecutar_simulacion, daemon=True)
            self.thread_simulacion.start()
            self.log_mensaje("🎮 Simulación iniciada")
        else:
            self.simulacion_activa = False
            self.btn_simular.configure(text="▶️ INICIAR SIMULACIÓN", fg_color="#27ae60")
            self.log_mensaje("⏹️ Simulación detenida")
    
    def ejecutar_simulacion(self):
        while self.simulacion_activa:
            # Usar velocidad del slider
            velocidad = self.speed_slider.get()
            delay = max(0.5, 8 - velocidad)
            time.sleep(random.uniform(delay/2, delay))
            
            if not self.simulacion_activa:
                break
                
            if self.modo_actual == "Objetos Pequeños":
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
        
        # Actualizar progress bar
        self.progress_bar.set(random.uniform(0.3, 1.0))
        self.root.after(1000, lambda: self.progress_bar.set(0))
    
    def simular_servo_activacion(self):
        self.label_servo.configure(text="ACTIVO", text_color="#27ae60")
        self.log_mensaje("⚙️ ACTUADOR ACTIVADO - Filtrando objeto...")
        
        def restaurar_servo():
            self.label_servo.configure(text="REPOSO", text_color="gray50")
            self.log_mensaje("⚙️ Actuador en REPOSO")
        
        self.root.after(2000, restaurar_servo)
    
    def iniciar_monitoreo(self):
        """Monitorear mensajes del hardware y actualizar KPIs"""
        if self.hardware_conectado and self.ser:
            try:
                while self.ser.in_waiting > 0:
                    mensaje = self.ser.readline().decode().strip()
                    if mensaje:
                        self.procesar_mensaje_arduino(mensaje)
            except Exception:
                pass
        
        # Actualizar KPIs
        self.actualizar_kpis()
        
        # Programar próxima verificación
        self.root.after(100, self.iniciar_monitoreo)
    
    def actualizar_kpis(self):
        """Actualizar los indicadores KPI"""
        try:
            # Throughput
            total = self.objetos_clasificados["pequeños"] + self.objetos_clasificados["grandes"]
            elapsed_time = time.time() - self.start_time
            throughput = (total / max(elapsed_time/60, 1))
            self.label_throughput.configure(text=f"{throughput:.1f} obj/min")
            
            # Tiempo online
            uptime = int(elapsed_time)
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            self.label_uptime.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
        except Exception:
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
            self.label_servo.configure(text="ACTIVO", text_color="#27ae60")
        elif "Servo regresó a REPOSO" in mensaje:
            self.label_servo.configure(text="REPOSO", text_color="gray50")
        elif "Objetos Pequeños" in mensaje:
            self.modo_actual = "Objetos Pequeños"
            self.label_modo.configure(text="Objetos Pequeños", text_color="#3498db")
        elif "Objetos Grandes" in mensaje:
            self.modo_actual = "Objetos Grandes"
            self.label_modo.configure(text="Objetos Grandes", text_color="#e67e22")
    
    def actualizar_estadisticas(self):
        self.label_pequeños.configure(text=str(self.objetos_clasificados["pequeños"]))
        self.label_grandes.configure(text=str(self.objetos_clasificados["grandes"]))
        total = self.objetos_clasificados["pequeños"] + self.objetos_clasificados["grandes"]
        self.label_total.configure(text=str(total))
    
    def reset_estadisticas(self):
        respuesta = messagebox.askyesno("Confirmar Reset", 
                                      "¿Está seguro de resetear todas las estadísticas?")
        if respuesta:
            self.objetos_clasificados = {"pequeños": 0, "grandes": 0}
            self.historial_produccion = []
            self.actualizar_estadisticas()
            self.log_mensaje("🔄 Estadísticas reseteadas")
    
    def run(self):
        """Iniciar la aplicación"""
        # Mostrar la ventana primero
        self.root.deiconify()  # Asegurar que la ventana esté visible
        
        # Mensajes de bienvenida después de un breve delay
        self.root.after(200, lambda: self.log_mensaje("🚀 SISTEMA SCADA INICIADO"))
        self.root.after(300, lambda: self.log_mensaje("💡 Modo simulación disponible si no hay hardware"))
        self.root.after(400, lambda: self.log_mensaje("⚡ Sistema listo para operar"))
        
        # Iniciar el loop principal
        self.root.mainloop()
    
    def on_closing(self):
        if self.simulacion_activa:
            self.simulacion_activa = False
        if self.hardware_conectado and self.ser:
            self.ser.close()
        self.root.destroy()

if __name__ == "__main__":
    app = ClasificadoraModerna()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()