"""
Exemple de suivi de ligne
Le robot suit une ligne noire sur fond blanc
"""

from ks4034f import KS4034F, LineTrackingSensor, LedCount, LedState
from time import sleep

# Initialiser le robot
robot = KS4034F()

# Vitesses
FORWARD_SPEED = 30
TURN_SPEED = 25

print("Démonstration suivi de ligne")
print("Le robot suit une ligne noire")
print("Appuyez sur Ctrl+C pour arrêter\n")

try:
    # Allumer les LEDs pour indiquer que le programme est actif
    robot.set_led(LedCount.LEFT, LedState.ON)
    robot.set_led(LedCount.RIGHT, LedState.ON)
    sleep(0.5)
    robot.set_led(LedCount.LEFT, LedState.OFF)
    robot.set_led(LedCount.RIGHT, LedState.OFF)

    while True:
        # Lire les trois capteurs
        left = robot.read_line_sensor(LineTrackingSensor.LEFT)
        center = robot.read_line_sensor(LineTrackingSensor.CENTER)
        right = robot.read_line_sensor(LineTrackingSensor.RIGHT)

        # Afficher l'état des capteurs (0 = noir, 1 = blanc)
        print(f"L:{left} C:{center} R:{right}", end=" -> ")

        # Logique de suivi de ligne
        # 0 = ligne noire détectée, 1 = blanc

        if center == 0:
            # Ligne au centre - aller tout droit
            print("Tout droit")
            robot.move_forward(FORWARD_SPEED)
            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.OFF)

        elif left == 0 and center == 1 and right == 1:
            # Ligne à gauche - corriger à gauche
            print("Correction à gauche")
            robot.turn_left(TURN_SPEED)
            robot.set_led(LedCount.LEFT, LedState.ON)
            robot.set_led(LedCount.RIGHT, LedState.OFF)

        elif right == 0 and center == 1 and left == 1:
            # Ligne à droite - corriger à droite
            print("Correction à droite")
            robot.turn_right(TURN_SPEED)
            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.ON)

        elif left == 0 and center == 0:
            # Ligne à gauche et au centre - virage serré à gauche
            print("Virage à gauche")
            robot.turn_left(TURN_SPEED + 5)
            robot.set_led(LedCount.LEFT, LedState.ON)
            robot.set_led(LedCount.RIGHT, LedState.OFF)

        elif right == 0 and center == 0:
            # Ligne à droite et au centre - virage serré à droite
            print("Virage à droite")
            robot.turn_right(TURN_SPEED + 5)
            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.ON)

        elif left == 0 and right == 0:
            # Ligne des deux côtés - peut être un croisement ou une fin
            print("Intersection ou fin")
            robot.move_forward(FORWARD_SPEED)
            robot.set_led(LedCount.LEFT, LedState.ON)
            robot.set_led(LedCount.RIGHT, LedState.ON)

        else:
            # Aucune ligne détectée - arrêter
            print("Ligne perdue - Arrêt")
            robot.stop()
            robot.set_led(LedCount.LEFT, LedState.ON)
            robot.set_led(LedCount.RIGHT, LedState.ON)
            sleep(0.5)
            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.OFF)
            sleep(0.5)

        sleep(0.05)  # Petit délai pour la stabilité

except KeyboardInterrupt:
    print("\n\nArrêt demandé par l'utilisateur")

finally:
    # Éteindre les LEDs et arrêter le robot
    robot.set_led(LedCount.LEFT, LedState.OFF)
    robot.set_led(LedCount.RIGHT, LedState.OFF)
    robot.cleanup()
    print("Robot arrêté proprement")
