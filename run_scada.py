#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher para el Sistema SCADA optimizado para 1920x1080
Este script asegura que la aplicación se ejecute con la configuración correcta
"""

import sys
import platform

def configurar_entorno():
    """Configurar el entorno para ejecución óptima"""
    print("🚀 Iniciando Sistema SCADA...")
    print(f"💻 Sistema: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Verificar resolución recomendada
    try:
        if platform.system() == "Windows":
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            print(f"📺 Resolución detectada: {screen_width}x{screen_height}")
            
            if screen_width >= 1920 and screen_height >= 1080:
                print("✅ Resolución óptima detectada")
            else:
                print("⚠️ Resolución menor a 1920x1080 - La interfaz podría no mostrarse completamente")
                
    except Exception as e:
        print(f"⚠️ No se pudo detectar la resolución: {e}")

def main():
    """Función principal"""
    configurar_entorno()
    
    # Importar y ejecutar la aplicación
    try:
        from automation_control import ClasificadoraModerna
        
        print("🏭 Cargando Sistema SCADA...")
        app = ClasificadoraModerna()
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✅ Sistema SCADA iniciado correctamente")
        print("📱 Interfaz optimizada para 1920x1080")
        print("🎮 ¡Listo para operar!")
        
        app.run()
        
    except ImportError as e:
        print(f"❌ Error al importar la aplicación: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()