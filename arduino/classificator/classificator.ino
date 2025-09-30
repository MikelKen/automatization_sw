# arduino_interface.py
import serial
import threading
import time

class ArduinoInterface:
    """
    Clase para controlar el modo del Arduino y monitorizar su salida serie.
    Uso:
      ai = ArduinoInterface("COM3", 9600)
      ai.start_monitor(callback=my_callback)   # imprime en consola y llama callback(line)
      ai.change_mode()                         # envía señal C para alternar modo
      ai.stop_monitor()
    """
    def __init__(self, port: str, baud: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self._ser = None
        self._monitor_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def _open(self):
        if self._ser and self._ser.is_open:
            return
        self._ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        # esperar un poco para que el Arduino reinicie
        time.sleep(2)
        # limpiar buffer inicial
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

    def change_mode(self):
        """Envía la señal para alternar el modo (C\\n)."""
        with self._lock:
            try:
                if not self._ser or not self._ser.is_open:
                    self._open()
                self._ser.write(b"C\n")
                # opcional: leer respuesta inmediata si existe
                # resp = self._ser.readline().decode(errors='ignore').strip()
                # return resp
            except Exception as e:
                raise RuntimeError(f"No se pudo enviar comando: {e}")

    def start_monitor(self, callback=None, print_to_console=True):
        """
        Inicia monitor serie en background.
        callback: función opcional que se llamará con cada línea recibida (str).
        print_to_console: si True imprime cada línea (como monitor serie).
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            return  # ya está corriendo

        self._stop_event.clear()
        try:
            self._open()
        except Exception as e:
            raise RuntimeError(f"No se pudo abrir puerto serie {self.port}: {e}")

        def _reader():
            try:
                while not self._stop_event.is_set():
                    try:
                        line = self._ser.readline()
                        if not line:
                            continue
                        try:
                            text = line.decode('utf-8', errors='ignore').rstrip('\r\n')
                        except:
                            text = repr(line)
                        if print_to_console:
                            print(text)
                        if callback:
                            try:
                                callback(text)
                            except Exception as cb_e:
                                # no dejar que una excepción en el callback termine el thread
                                print("Error en callback:", cb_e)
                    except serial.SerialException as se:
                        print("SerialException en lectura:", se)
                        break
                    except Exception as e:
                        print("Error inesperado en monitor serial:", e)
                        break
            finally:
                # cerrar puerto al terminar
                try:
                    if self._ser and self._ser.is_open:
                        self._ser.close()
                except:
                    pass

        self._monitor_thread = threading.Thread(target=_reader, daemon=True)
        self._monitor_thread.start()

    def stop_monitor(self, wait=True):
        """Señala al thread que pare y cierra el puerto. wait=True bloquea hasta que termine."""
        self._stop_event.set()
        if wait and self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        # asegurar cierre del puerto
        with self._lock:
            try:
                if self._ser and self._ser.is_open:
                    self._ser.close()
            except:
                pass

    def is_monitoring(self):
        return self._monitor_thread is not None and self._monitor_thread.is_alive()
