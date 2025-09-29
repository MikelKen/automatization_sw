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
        self.root.title("Sistema de Control - Banda Clasificadora de Objetos")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables del sistema
        self.ser = None
        self.hardware_conectado = False
        self.modo_actual = "MODO 1"  # MODO 1 = Pequeños, MODO 2 = Grandes
        self.sistema_activo = False
        self.objetos_clasificados = {"pequeños": 0, "grandes": 0}
        
        # Variables para simulación
        self.simulacion_activa = False
        self.thread_simulacion = None
        
        self.crear_interfaz()
        self.conectar_hardware()
        self.iniciar_monitoreo()
    
    def crear_interfaz(self):
        # Título principal
        titulo = tk.Label(self.root, text="🏭 SISTEMA DE CLASIFICACIÓN DE OBJETOS", 
                         font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        titulo.pack(pady=10)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Panel de estado (izquierda)
        self.crear_panel_estado(main_frame)
        
        # Panel de control (centro)
        self.crear_panel_control(main_frame)
        
        # Panel de estadísticas (derecha)
        self.crear_panel_estadisticas(main_frame)
        
        # Panel de registro (abajo)
        self.crear_panel_registro(main_frame)
    
    def crear_panel_estado(self, parent):
        estado_frame = tk.LabelFrame(parent, text="Estado del Sistema", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0')
        estado_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew', ipadx=10, ipady=10)
        
        # Estado de conexión
        tk.Label(estado_frame, text="Conexión Hardware:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.label_conexion = tk.Label(estado_frame, text="❌ Desconectado", 
                                     font=('Arial', 10), fg='red', bg='#f0f0f0')
        self.label_conexion.pack(anchor='w', pady=(0,10))
        
        # Modo actual
        tk.Label(estado_frame, text="Modo de Clasificación:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.label_modo = tk.Label(estado_frame, text="🔵 MODO 1 (Objetos Pequeños)", 
                                 font=('Arial', 10), fg='blue', bg='#f0f0f0')
        self.label_modo.pack(anchor='w', pady=(0,10))
        
        # Estado del servo
        tk.Label(estado_frame, text="Estado Servo:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.label_servo = tk.Label(estado_frame, text="⚪ Reposo", 
                                  font=('Arial', 10), fg='gray', bg='#f0f0f0')
        self.label_servo.pack(anchor='w')
    
    def crear_panel_control(self, parent):
        control_frame = tk.LabelFrame(parent, text="Panel de Control", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        control_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew', ipadx=10, ipady=10)
        
        # Botón cambiar modo
        self.btn_modo = tk.Button(control_frame, text="🔄 Cambiar Modo de Clasificación", 
                                font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                                command=self.cambiar_modo, cursor='hand2')
        self.btn_modo.pack(pady=10, padx=20, fill='x')
        
        # Botón reconectar
        self.btn_reconectar = tk.Button(control_frame, text="🔌 Reconectar Hardware", 
                                      font=('Arial', 11), bg='#e74c3c', fg='white',
                                      command=self.conectar_hardware, cursor='hand2')
        self.btn_reconectar.pack(pady=5, padx=20, fill='x')
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Simulación
        tk.Label(control_frame, text="Simulación (sin hardware):", 
               font=('Arial', 10, 'bold'), bg='#f0f0f0').pack()
        
        self.btn_simular = tk.Button(control_frame, text="🎮 Iniciar Simulación", 
                                   font=('Arial', 10), bg='#27ae60', fg='white',
                                   command=self.toggle_simulacion, cursor='hand2')
        self.btn_simular.pack(pady=5, padx=20, fill='x')
        
        # Reset estadísticas
        self.btn_reset = tk.Button(control_frame, text="🔄 Resetear Estadísticas", 
                                 font=('Arial', 10), bg='#f39c12', fg='white',
                                 command=self.reset_estadisticas, cursor='hand2')
        self.btn_reset.pack(pady=5, padx=20, fill='x')
    
    def crear_panel_estadisticas(self, parent):
        stats_frame = tk.LabelFrame(parent, text="Estadísticas", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0')
        stats_frame.grid(row=0, column=2, padx=5, pady=5, sticky='nsew', ipadx=10, ipady=10)
        
        # Objetos pequeños
        tk.Label(stats_frame, text="🔸 Objetos Pequeños:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.label_pequeños = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), 
                                     fg='#3498db', bg='#f0f0f0')
        self.label_pequeños.pack(anchor='w', pady=(0,10))
        
        # Objetos grandes
        tk.Label(stats_frame, text="🔹 Objetos Grandes:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.label_grandes = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), 
                                    fg='#e74c3c', bg='#f0f0f0')
        self.label_grandes.pack(anchor='w', pady=(0,10))
        
        # Total
        tk.Label(stats_frame, text="📊 Total Procesados:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.label_total = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), 
                                  fg='#27ae60', bg='#f0f0f0')
        self.label_total.pack(anchor='w')
    
    def crear_panel_registro(self, parent):
        registro_frame = tk.LabelFrame(parent, text="Registro de Actividad", 
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0')
        registro_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        
        self.text_log = scrolledtext.ScrolledText(registro_frame, height=12, width=90, 
                                                font=('Courier', 9), bg='#2c3e50', fg='#ecf0f1')
        self.text_log.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurar el grid
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)
    
    def log_mensaje(self, mensaje, color='white'):
        timestamp = datetime.now().strftime("%H:%M:%S")
        mensaje_completo = f"[{timestamp}] {mensaje}\n"
        self.text_log.insert('end', mensaje_completo)
        self.text_log.see('end')
        
        # Mantener solo las últimas 100 líneas
        lines = self.text_log.get('1.0', 'end').split('\n')
        if len(lines) > 100:
            self.text_log.delete('1.0', '2.0')
    
    def conectar_hardware(self):
        puertos = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]  # Agregar más si es necesario
        
        for puerto in puertos:
            try:
                self.ser = serial.Serial(puerto, 9600, timeout=1)
                time.sleep(2)  # Esperar reset de Arduino
                
                # Verificar si Arduino responde
                self.ser.write(b"C\n")
                time.sleep(0.5)
                if self.ser.in_waiting > 0:
                    respuesta = self.ser.readline().decode().strip()
                    if "Modo cambiado" in respuesta:
                        self.hardware_conectado = True
                        self.label_conexion.config(text=f"✅ Conectado ({puerto})", fg='green')
                        self.log_mensaje(f"✅ Hardware conectado en {puerto}")
                        self.btn_reconectar.config(bg='#27ae60', text='🔌 Hardware Conectado')
                        return
                self.ser.close()
            except:
                continue
        
        # No se pudo conectar
        self.hardware_conectado = False
        self.label_conexion.config(text="❌ Modo Simulación", fg='orange')
        self.log_mensaje("⚠️ Hardware no detectado - Usando modo simulación")
        self.btn_reconectar.config(bg='#e74c3c', text='🔌 Reconectar Hardware')
    
    def cambiar_modo(self):
        if self.hardware_conectado:
            try:
                self.ser.write(b"C\n")
                time.sleep(0.1)
                # Leer respuesta
                respuesta = ""
                while self.ser.in_waiting > 0:
                    linea = self.ser.readline().decode().strip()
                    if linea:
                        respuesta = linea
                        self.log_mensaje(f"Arduino: {linea}")
                
                # Actualizar modo local
                if "MODO 1" in respuesta:
                    self.modo_actual = "MODO 1"
                    self.label_modo.config(text="🔵 MODO 1 (Objetos Pequeños)", fg='blue')
                elif "MODO 2" in respuesta:
                    self.modo_actual = "MODO 2"
                    self.label_modo.config(text="🔴 MODO 2 (Objetos Grandes)", fg='red')
                    
            except Exception as e:
                self.log_mensaje(f"❌ Error al cambiar modo: {e}")
        else:
            # Simulación del cambio de modo
            if self.modo_actual == "MODO 1":
                self.modo_actual = "MODO 2"
                self.label_modo.config(text="🔴 MODO 2 (Objetos Grandes)", fg='red')
                self.log_mensaje("🔄 Modo cambiado: MODO 2 (Clasificar objetos GRANDES)")
            else:
                self.modo_actual = "MODO 1"
                self.label_modo.config(text="🔵 MODO 1 (Objetos Pequeños)", fg='blue')
                self.log_mensaje("🔄 Modo cambiado: MODO 1 (Clasificar objetos PEQUEÑOS)")
    
    def toggle_simulacion(self):
        if not self.simulacion_activa:
            self.simulacion_activa = True
            self.btn_simular.config(text="⏹️ Detener Simulación", bg='#e74c3c')
            self.thread_simulacion = threading.Thread(target=self.ejecutar_simulacion, daemon=True)
            self.thread_simulacion.start()
            self.log_mensaje("🎮 Simulación iniciada")
        else:
            self.simulacion_activa = False
            self.btn_simular.config(text="🎮 Iniciar Simulación", bg='#27ae60')
            self.log_mensaje("⏹️ Simulación detenida")
    
    def ejecutar_simulacion(self):
        while self.simulacion_activa:
            # Simular detección de objeto aleatorio cada 3-8 segundos
            time.sleep(random.uniform(3, 8))
            if not self.simulacion_activa:
                break
                
            # Simular detección según el modo
            if self.modo_actual == "MODO 1":
                # Simular objeto pequeño (80% probabilidad) o falso positivo
                if random.random() < 0.8:
                    self.simular_clasificacion("pequeño")
            else:
                # Simular objeto grande (70% probabilidad)
                if random.random() < 0.7:
                    self.simular_clasificacion("grande")
    
    def simular_clasificacion(self, tipo):
        if tipo == "pequeño":
            self.objetos_clasificados["pequeños"] += 1
            self.log_mensaje("🔸 Objeto CLASIFICADO: PEQUEÑO")
        else:
            self.objetos_clasificados["grandes"] += 1
            self.log_mensaje("🔹 Objeto CLASIFICADO: GRANDE")
        
        # Simular activación del servo
        self.root.after(0, self.simular_servo_activacion)
        self.actualizar_estadisticas()
    
    def simular_servo_activacion(self):
        self.label_servo.config(text="🟢 Filtrando...", fg='green')
        self.log_mensaje("⚙️ Servo ACTIVADO... Filtrando...")
        
        def restaurar_servo():
            self.label_servo.config(text="⚪ Reposo", fg='gray')
            self.log_mensaje("⚙️ Servo regresó a REPOSO...")
        
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
        
        # Programar próxima verificación
        self.root.after(100, self.iniciar_monitoreo)
    
    def procesar_mensaje_arduino(self, mensaje):
        self.log_mensaje(f"Arduino: {mensaje}")
        
        if "PEQUEÑO" in mensaje:
            self.objetos_clasificados["pequeños"] += 1
            self.actualizar_estadisticas()
        elif "GRANDE" in mensaje:
            self.objetos_clasificados["grandes"] += 1
            self.actualizar_estadisticas()
        elif "Servo ACTIVADO" in mensaje:
            self.label_servo.config(text="🟢 Filtrando...", fg='green')
        elif "Servo regresó a REPOSO" in mensaje:
            self.label_servo.config(text="⚪ Reposo", fg='gray')
        elif "MODO 1" in mensaje:
            self.modo_actual = "MODO 1"
            self.label_modo.config(text="🔵 MODO 1 (Objetos Pequeños)", fg='blue')
        elif "MODO 2" in mensaje:
            self.modo_actual = "MODO 2"
            self.label_modo.config(text="🔴 MODO 2 (Objetos Grandes)", fg='red')
    
    def actualizar_estadisticas(self):
        self.label_pequeños.config(text=str(self.objetos_clasificados["pequeños"]))
        self.label_grandes.config(text=str(self.objetos_clasificados["grandes"]))
        total = self.objetos_clasificados["pequeños"] + self.objetos_clasificados["grandes"]
        self.label_total.config(text=str(total))
    
    def reset_estadisticas(self):
        respuesta = messagebox.askyesno("Confirmar Reset", 
                                      "¿Está seguro de resetear todas las estadísticas?")
        if respuesta:
            self.objetos_clasificados = {"pequeños": 0, "grandes": 0}
            self.actualizar_estadisticas()
            self.log_mensaje("🔄 Estadísticas reseteadas")
    
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
    app.log_mensaje("🚀 Sistema de Clasificación iniciado")
    app.log_mensaje("💡 Si no hay hardware conectado, usa la simulación para probar")
    
    root.mainloop()

import serial, time

PORT = "COM3"   # 👈 cámbialo por tu puerto (ej. COM4, COM5 o /dev/ttyACM0 en Linux)
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # esperar a que Arduino reinicie

def send(cmd):
    ser.write((cmd + '\n').encode())
    resp = ser.readline().decode().strip()
    print("Arduino:", resp)

print("=== CONTROL DE ARDUINO ===")
print("Comandos: 1=MODE1 | 2=MODE2 | t=TOGGLE | q=Salir")

while True:
    cmd = input(">> ").strip().lower()
    if cmd == "q":
        break
    elif cmd in ["1", "2", "t"]:
        send(cmd)
    else:
        print("Comando no válido")

ser.close()
