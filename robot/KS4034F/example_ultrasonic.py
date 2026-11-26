"""
Exemple d'utilisation du capteur ultrason
Évitement d'obstacles simple
"""

from ks4034f import KS4034F, LedCount, LedState
from time import sleep

# Initialiser le robot
robot = KS4034F()

# Distance de sécurité en cm
SAFE_DISTANCE = 20

print("Démonstration évitement d'obstacles")
print(f"Distance de sécurité: {SAFE_DISTANCE} cm")
print("Appuyez sur Ctrl+C pour arrêter\n")

try:
    while True:
        # Mesurer la distance
        distance = robot.read_ultrasonic()
        print(f"Distance: {distance} cm", end="")

        if distance < SAFE_DISTANCE and distance > 0:
            # Obstacle proche - alerter et éviter
            print(" - OBSTACLE!")

            # Allumer les LEDs en rouge (alerte)
            robot.set_led(LedCount.LEFT, LedState.ON)
            robot.set_led(LedCount.RIGHT, LedState.ON)

            # Arrêter
            robot.stop()
            sleep(0.3)

            # Reculer
            print("  -> Reculer...")
            robot.move_backward(40)
            sleep(0.5)

            # Tourner à droite pour éviter
            print("  -> Tourner...")
            robot.turn_right(50)
            sleep(0.7)

            # Éteindre les LEDs
            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.OFF)

        else:
            # Voie libre - avancer
            print(" - OK")
            robot.move_forward(35)

        sleep(0.2)

except KeyboardInterrupt:
    print("\n\nArrêt demandé par l'utilisateur")

finally:
    # Éteindre les LEDs et arrêter le robot
    robot.set_led(LedCount.LEFT, LedState.OFF)
    robot.set_led(LedCount.RIGHT, LedState.OFF)
    robot.cleanup()
    print("Robot arrêté proprement")
