"""
Exemple de scanner avec servo et capteur ultrason
Le robot scanne son environnement et trouve le chemin le plus dégagé
"""

from ks4034f import KS4034F, LedCount, LedState
from time import sleep

# Initialiser le robot
robot = KS4034F()

# Paramètres de scan
SCAN_ANGLES = [-90, -60, -30, 0, 30, 60, 90]
MIN_SAFE_DISTANCE = 30  # cm

print("Démonstration scanner ultrason")
print("Le robot scanne son environnement et évite les obstacles")
print("Appuyez sur Ctrl+C pour arrêter\n")


def scan_environment():
    """
    Scanne l'environnement et retourne les distances à chaque angle
    Returns: dict {angle: distance}
    """
    distances = {}

    print("\n--- Scan en cours ---")
    for angle in SCAN_ANGLES:
        robot.set_servo_angle(angle)
        sleep(0.3)  # Attendre que le servo se positionne

        distance = robot.read_ultrasonic()
        distances[angle] = distance

        # Visualisation simple
        bars = "=" * min(distance // 2, 50)
        print(f"  {angle:4d}°: {distance:3d}cm {bars}")

    # Retour au centre
    robot.set_servo_angle(0)
    sleep(0.3)

    return distances


def find_best_direction(distances):
    """
    Trouve la meilleure direction (la plus dégagée)
    Returns: angle de la meilleure direction
    """
    # Trouver l'angle avec la plus grande distance
    best_angle = max(distances, key=distances.get)
    best_distance = distances[best_angle]

    print(f"\nMeilleure direction: {best_angle}° ({best_distance}cm)")

    return best_angle, best_distance


def turn_to_angle(target_angle):
    """
    Tourne le robot vers l'angle cible
    """
    if target_angle < -10:
        # Tourner à gauche
        print(f"Tourner à gauche vers {target_angle}°")
        turn_time = abs(target_angle) / 90  # Proportion de 90°
        robot.turn_left(50)
        sleep(turn_time)
        robot.stop()

    elif target_angle > 10:
        # Tourner à droite
        print(f"Tourner à droite vers {target_angle}°")
        turn_time = abs(target_angle) / 90
        robot.turn_right(50)
        sleep(turn_time)
        robot.stop()

    else:
        # Continuer tout droit
        print("Continuer tout droit")


try:
    # Clignoter les LEDs pour indiquer le démarrage
    for _ in range(3):
        robot.set_led(LedCount.LEFT, LedState.ON)
        robot.set_led(LedCount.RIGHT, LedState.ON)
        sleep(0.2)
        robot.set_led(LedCount.LEFT, LedState.OFF)
        robot.set_led(LedCount.RIGHT, LedState.OFF)
        sleep(0.2)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'='*50}")
        print(f"Cycle {cycle}")
        print(f"{'='*50}")

        # Scanner l'environnement
        distances = scan_environment()

        # Trouver la meilleure direction
        best_angle, best_distance = find_best_direction(distances)

        # Décider de l'action
        if best_distance < MIN_SAFE_DISTANCE:
            # Tout est bloqué - reculer et rescanner
            print(f"\nObstacles partout (< {MIN_SAFE_DISTANCE}cm)")
            print("Action: Reculer et tourner")

            robot.set_led(LedCount.LEFT, LedState.ON)
            robot.set_led(LedCount.RIGHT, LedState.ON)

            robot.move_backward(40)
            sleep(1)
            robot.turn_right(50)
            sleep(1)
            robot.stop()

            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.OFF)

        else:
            # Voie dégagée - tourner vers la meilleure direction et avancer
            print(f"\nVoie dégagée à {best_angle}°")

            # Indiquer la direction avec les LEDs
            if best_angle < 0:
                robot.set_led(LedCount.LEFT, LedState.ON)
                robot.set_led(LedCount.RIGHT, LedState.OFF)
            elif best_angle > 0:
                robot.set_led(LedCount.LEFT, LedState.OFF)
                robot.set_led(LedCount.RIGHT, LedState.ON)
            else:
                robot.set_led(LedCount.LEFT, LedState.OFF)
                robot.set_led(LedCount.RIGHT, LedState.OFF)

            # Tourner vers la meilleure direction
            turn_to_angle(best_angle)

            # Avancer
            print("Action: Avancer")
            robot.move_forward(40)
            sleep(2)
            robot.stop()

            robot.set_led(LedCount.LEFT, LedState.OFF)
            robot.set_led(LedCount.RIGHT, LedState.OFF)

        sleep(0.5)

except KeyboardInterrupt:
    print("\n\nArrêt demandé par l'utilisateur")

finally:
    # Retourner le servo au centre et tout éteindre
    robot.set_servo_angle(0)
    robot.set_led(LedCount.LEFT, LedState.OFF)
    robot.set_led(LedCount.RIGHT, LedState.OFF)
    robot.cleanup()
    print("Robot arrêté proprement")
