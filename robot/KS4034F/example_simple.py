"""
Exemple simple d'utilisation du robot KS4034F
Déplacements de base
"""

from ks4034f import KS4034F
from time import sleep

# Initialiser le robot
robot = KS4034F()

print("Démonstration simple du robot KS4034F")

try:
    # Avancer pendant 2 secondes
    print("Avancer...")
    robot.move_forward(50)
    sleep(2)

    # Arrêt
    print("Arrêt...")
    robot.stop()
    sleep(1)

    # Reculer pendant 2 secondes
    print("Reculer...")
    robot.move_backward(50)
    sleep(2)

    # Arrêt
    print("Arrêt...")
    robot.stop()
    sleep(1)

    # Tourner à gauche pendant 1 seconde
    print("Tourner à gauche...")
    robot.turn_left(50)
    sleep(1)

    # Arrêt
    print("Arrêt...")
    robot.stop()
    sleep(1)

    # Tourner à droite pendant 1 seconde
    print("Tourner à droite...")
    robot.turn_right(50)
    sleep(1)

    # Arrêt final
    print("Arrêt final...")
    robot.stop()

    print("Démonstration terminée!")

except KeyboardInterrupt:
    print("\nInterruption par l'utilisateur")

finally:
    # Toujours arrêter le robot à la fin
    robot.cleanup()
