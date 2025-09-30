#include <Servo.h>
Servo miServo;

// Pines de entradas para la detección
const int SENSOR1 = 2;
const int SENSOR2 = 3;

// Pines para el switch de modo
const int pinModo = 13;   // Pin central del switch
const int pinPull = 12;   // Pin lateral usado con pull-up interno

// Servo
const int pinServo = 4;
const int anguloReposo = 0;
const int anguloActivo = 45;

// Variables para detectar cambios
bool ultimoModo = HIGH;

void setup() {
  pinMode(SENSOR1, INPUT_PULLUP);
  pinMode(SENSOR2, INPUT_PULLUP);

  // Configuración del switch
  pinMode(pinModo, INPUT);       // Pin central lee el estado
  pinMode(pinPull, INPUT_PULLUP);// Pin 12 siempre en pull-up

  miServo.attach(pinServo);
  miServo.write(anguloReposo);

  Serial.begin(9600);
  Serial.println("Sistema iniciado...");
}

void loop() {
  bool modo = digitalRead(pinModo);

  // Detectar si cambió el modo
  if (modo != ultimoModo) {
    if (modo == HIGH) {
      Serial.println("Modo cambiado: MODO 1 (Filtrar objetos pequeños).");
    } else {
      Serial.println("Modo cambiado: MODO 2 (Filtrar objetos grandes).");
    }
    ultimoModo = modo;
  }

  if (modo == HIGH) {
    // ------- MODO 1: SENSOR1 en LOW y SENSOR2 en HIGH ------
    if (digitalRead(SENSOR1) == LOW && digitalRead(SENSOR2) == HIGH) {
      Serial.println("SENSOR 1 ACTIVO. (Objeto Pequeño)");
      activarServo();
    } else if (digitalRead(SENSOR2) == LOW) {
      Serial.println("SENSOR 2 ACTIVO, pero no se FILTRAN objetos grandes en este modo.");
    }
  } else {
    // ------- MODO 2: se necesitan los dos SENSORES en LOW ------
    if (digitalRead(SENSOR1) == LOW && digitalRead(SENSOR2) == LOW) {
      Serial.println("SENSOR 1 y 2 ACTIVOS. (Objeto Grande)");
      activarServo();
    }
  }
}

// Función para mover el servo
void activarServo() {
  Serial.println("Servo ACTIVADO... Filtrando...");
  miServo.write(anguloActivo);
  delay(2000);    //Tiempo que se mantiene activo el servo FILTRANDO.
  miServo.write(anguloReposo);
  delay(500);
  Serial.println("Servo regresó a REPOSO...");
}