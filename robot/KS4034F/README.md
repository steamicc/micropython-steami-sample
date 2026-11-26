# Bibliothèque MicroPython pour Keyestudio KS4034F

Portage MicroPython de la bibliothèque MakeCode pour le robot Keyestudio KS4034F.

## Installation

Copiez le fichier `ks4034f.py` sur votre carte micro:bit ou autre carte compatible MicroPython.

## Utilisation de base

```python
from ks4034f import KS4034F, MotorDirection, MotorPosition

# Initialiser le robot
robot = KS4034F()

# Avancer à 50% de vitesse
robot.move_forward(50)

# Reculer
robot.move_backward(50)

# Tourner à gauche
robot.turn_left(50)

# Tourner à droite
robot.turn_right(50)

# Arrêter
robot.stop()
```

## Caractéristiques

### Contrôle des moteurs

#### Moteurs individuels
```python
from ks4034f import MotorPosition, MotorDirection

# Contrôler un moteur spécifique
robot.motor(MotorPosition.UPPER_LEFT, MotorDirection.FORWARD, 50)
robot.motor(MotorPosition.LOWER_RIGHT, MotorDirection.BACK, 75)
```

Positions disponibles:
- `MotorPosition.UPPER_LEFT` - Moteur avant-gauche (M2)
- `MotorPosition.LOWER_LEFT` - Moteur arrière-gauche (M4)
- `MotorPosition.UPPER_RIGHT` - Moteur avant-droit (M1)
- `MotorPosition.LOWER_RIGHT` - Moteur arrière-droit (M3)

#### Mouvements de base
```python
# Tous les mouvements acceptent une vitesse de 0 à 100%
robot.move_forward(50)    # Avancer
robot.move_backward(50)   # Reculer
robot.turn_left(50)       # Tourner à gauche sur place
robot.turn_right(50)      # Tourner à droite sur place
robot.stop()              # Arrêter tous les moteurs
```

### LEDs colorées

```python
from ks4034f import LedCount, LedState

# Allumer/éteindre les LEDs
robot.set_led(LedCount.LEFT, LedState.ON)
robot.set_led(LedCount.RIGHT, LedState.OFF)
```

### Servo moteur

```python
# Définir l'angle du servo (-90 à 90 degrés)
robot.set_servo_angle(0)    # Centre
robot.set_servo_angle(90)   # Droite
robot.set_servo_angle(-90)  # Gauche
```

### Capteur ultrason

```python
# Mesurer la distance en centimètres
distance = robot.read_ultrasonic()
print(f"Distance: {distance} cm")
```

### Capteurs de suivi de ligne

```python
from ks4034f import LineTrackingSensor

# Lire les capteurs (0 = ligne noire, 1 = blanc)
left = robot.read_line_sensor(LineTrackingSensor.LEFT)
center = robot.read_line_sensor(LineTrackingSensor.CENTER)
right = robot.read_line_sensor(LineTrackingSensor.RIGHT)
```

## Exemples

### Évitement d'obstacles

```python
from ks4034f import KS4034F
from time import sleep

robot = KS4034F()

while True:
    distance = robot.read_ultrasonic()

    if distance < 20 and distance > 0:
        # Obstacle détecté
        robot.move_backward(40)
        sleep(0.5)
        robot.turn_right(50)
        sleep(0.8)
    else:
        # Voie libre
        robot.move_forward(40)

    sleep(0.1)
```

### Suivi de ligne

```python
from ks4034f import KS4034F, LineTrackingSensor
from time import sleep

robot = KS4034F()

while True:
    left = robot.read_line_sensor(LineTrackingSensor.LEFT)
    center = robot.read_line_sensor(LineTrackingSensor.CENTER)
    right = robot.read_line_sensor(LineTrackingSensor.RIGHT)

    if center == 0:
        # Ligne au centre
        robot.move_forward(30)
    elif left == 0:
        # Ligne à gauche
        robot.turn_left(25)
    elif right == 0:
        # Ligne à droite
        robot.turn_right(25)
    else:
        # Pas de ligne
        robot.stop()

    sleep(0.1)
```

### Scanner ultrason

```python
from ks4034f import KS4034F
from time import sleep

robot = KS4034F()

# Scanner de -90° à 90°
for angle in range(-90, 91, 10):
    robot.set_servo_angle(angle)
    sleep(0.2)
    distance = robot.read_ultrasonic()
    print(f"Angle {angle}°: {distance} cm")

# Retour au centre
robot.set_servo_angle(0)
```

## Configuration personnalisée

Si votre câblage est différent, vous pouvez personnaliser les pins :

```python
robot = KS4034F(
    i2c_bus=3,              # Bus I2C
    servo_pin=14,           # Pin du servo
    trig_pin=15,            # Pin trigger ultrason
    echo_pin=16,            # Pin echo ultrason
    line_left_pin=3,        # Pin capteur gauche
    line_center_pin=4,      # Pin capteur centre
    line_right_pin=10       # Pin capteur droit
)
```

## Architecture technique

### Communication I2C

Le robot utilise un contrôleur STC15 à l'adresse I2C `0x30` pour contrôler les moteurs et LEDs.

#### Registres des moteurs

| Moteur | Position | Registre A | Registre B |
|--------|----------|------------|------------|
| M1 | Avant-droit | 0x01 | 0x02 |
| M2 | Avant-gauche | 0x03 | 0x04 |
| M3 | Arrière-droit | 0x05 | 0x06 |
| M4 | Arrière-gauche | 0x07 | 0x08 |

#### Registres des LEDs

| LED | Registre |
|-----|----------|
| Gauche | 0x09 |
| Droite | 0x0A |

### Pins par défaut

| Fonction | Pin |
|----------|-----|
| Servo | 14 |
| Ultrason Trigger | 15 |
| Ultrason Echo | 16 |
| Ligne Gauche | 3 |
| Ligne Centre | 4 |
| Ligne Droite | 10 |

## Nettoyage

Toujours appeler `cleanup()` à la fin pour arrêter les moteurs et libérer les ressources :

```python
try:
    robot.move_forward(50)
    # ... votre code ...
finally:
    robot.cleanup()
```

## Fichiers d'exemples

- [example_complete.py](example_complete.py) - Exemples complets de toutes les fonctionnalités
- [control_motors/main.py](control_motors/main.py) - Test simple des moteurs

## Différences avec la version MakeCode

1. **Syntaxe Python** : Utilisation de méthodes au lieu de fonctions globales
2. **Énumérations** : Utilisation de classes pour les constantes au lieu d'enums TypeScript
3. **Gestion des ressources** : Méthode `cleanup()` pour libérer les ressources
4. **Flexibilité** : Configuration des pins personnalisable à l'initialisation

## Licence

Portage basé sur la bibliothèque MakeCode originale de Keyestudio.
