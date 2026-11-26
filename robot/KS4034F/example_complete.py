"""
Exemple complet d'utilisation de la bibliothèque KS4034F
Démontre toutes les fonctionnalités du robot
"""

from ks4034f import (
    KS4034F,
    MotorPosition,
    MotorDirection,
    LineTrackingSensor,
    LedCount,
    LedState
)
from time import sleep


def test_motors(robot):
    """Test des moteurs individuels"""
    print("Test des moteurs individuels...")

    positions = [
        ("Avant-Gauche", MotorPosition.UPPER_LEFT),
        ("Arrière-Gauche", MotorPosition.LOWER_LEFT),
        ("Avant-Droit", MotorPosition.UPPER_RIGHT),
        ("Arrière-Droit", MotorPosition.LOWER_RIGHT)
    ]

    for name, pos in positions:
        print(f"Moteur {name} - Avant")
        robot.motor(pos, MotorDirection.FORWARD, 50)
        sleep(1)

        print(f"Moteur {name} - Arrière")
        robot.motor(pos, MotorDirection.BACK, 50)
        sleep(1)

        robot.stop()
        sleep(0.5)


def test_movements(robot):
    """Test des mouvements de base"""
    print("\nTest des mouvements de base...")

    movements = [
        ("Avancer", robot.move_forward),
        ("Reculer", robot.move_backward),
        ("Tourner à gauche", robot.turn_left),
        ("Tourner à droite", robot.turn_right)
    ]

    for name, func in movements:
        print(f"{name}...")
        func(50)
        sleep(2)
        robot.stop()
        sleep(1)


def test_leds(robot):
    """Test des LEDs colorées"""
    print("\nTest des LEDs...")

    leds = [
        ("LED Gauche", LedCount.LEFT),
        ("LED Droite", LedCount.RIGHT)
    ]

    for name, led in leds:
        print(f"{name} - ON")
        robot.set_led(led, LedState.ON)
        sleep(1)

        print(f"{name} - OFF")
        robot.set_led(led, LedState.OFF)
        sleep(0.5)

    # Allumer les deux en même temps
    print("Les deux LEDs - ON")
    robot.set_led(LedCount.LEFT, LedState.ON)
    robot.set_led(LedCount.RIGHT, LedState.ON)
    sleep(1)

    # Éteindre les deux
    print("Les deux LEDs - OFF")
    robot.set_led(LedCount.LEFT, LedState.OFF)
    robot.set_led(LedCount.RIGHT, LedState.OFF)


def test_servo(robot):
    """Test du servo moteur"""
    print("\nTest du servo...")

    angles = [-90, -45, 0, 45, 90, 0]

    for angle in angles:
        print(f"Angle: {angle}°")
        robot.set_servo_angle(angle)
        sleep(1)


def test_line_tracking(robot):
    """Test des capteurs de suivi de ligne"""
    print("\nTest des capteurs de ligne (10 lectures)...")

    sensors = [
        ("Gauche", LineTrackingSensor.LEFT),
        ("Centre", LineTrackingSensor.CENTER),
        ("Droit", LineTrackingSensor.RIGHT)
    ]

    for i in range(10):
        print(f"\nLecture {i+1}:")
        for name, sensor in sensors:
            value = robot.read_line_sensor(sensor)
            state = "Ligne noire" if value == 0 else "Blanc"
            print(f"  {name}: {state} ({value})")
        sleep(0.5)


def test_ultrasonic(robot):
    """Test du capteur ultrason"""
    print("\nTest du capteur ultrason (10 mesures)...")

    for i in range(10):
        distance = robot.read_ultrasonic()
        print(f"Distance {i+1}: {distance} cm")
        sleep(0.5)


def demo_obstacle_avoidance(robot):
    """Démonstration d'évitement d'obstacles"""
    print("\nDémonstration évitement d'obstacles (20 secondes)...")
    print("Le robot avance et évite les obstacles")

    start_time = sleep(0)  # Utiliser un compteur simple
    iterations = 0
    max_iterations = 40  # Environ 20 secondes à 0.5s par itération

    while iterations < max_iterations:
        distance = robot.read_ultrasonic()
        print(f"Distance: {distance} cm")

        if distance < 20 and distance > 0:  # Obstacle détecté
            print("Obstacle! Reculer et tourner...")
            robot.move_backward(40)
            sleep(0.5)
            robot.turn_right(50)
            sleep(0.8)
        else:
            print("Voie libre, avancer...")
            robot.move_forward(40)

        sleep(0.5)
        iterations += 1

    robot.stop()
    print("Démonstration terminée")


def demo_line_following(robot):
    """Démonstration de suivi de ligne"""
    print("\nDémonstration suivi de ligne (20 secondes)...")
    print("Le robot suit une ligne noire")

    iterations = 0
    max_iterations = 40

    while iterations < max_iterations:
        left = robot.read_line_sensor(LineTrackingSensor.LEFT)
        center = robot.read_line_sensor(LineTrackingSensor.CENTER)
        right = robot.read_line_sensor(LineTrackingSensor.RIGHT)

        print(f"Capteurs - G:{left} C:{center} D:{right}")

        if center == 0:  # Ligne au centre
            print("Ligne au centre - Avancer")
            robot.move_forward(30)
        elif left == 0:  # Ligne à gauche
            print("Ligne à gauche - Tourner à gauche")
            robot.turn_left(25)
        elif right == 0:  # Ligne à droite
            print("Ligne à droite - Tourner à droite")
            robot.turn_right(25)
        else:  # Pas de ligne détectée
            print("Pas de ligne - Arrêt")
            robot.stop()

        sleep(0.1)
        iterations += 1

    robot.stop()
    print("Démonstration terminée")


def main():
    """Programme principal"""
    print("=== Test complet du robot KS4034F ===\n")
    print("Ce fichier est conçu pour être utilisé de manière interactive.")
    print("\nPour utiliser dans le REPL:")
    print(">>> from example_complete import *")
    print(">>> robot = KS4034F()")
    print("\nPuis appelez les fonctions de test:")
    print(">>> test_motors(robot)")
    print(">>> test_movements(robot)")
    print(">>> test_leds(robot)")
    print(">>> test_servo(robot)")
    print(">>> test_line_tracking(robot)")
    print(">>> test_ultrasonic(robot)")
    print(">>> demo_obstacle_avoidance(robot)")
    print(">>> demo_line_following(robot)")
    print(">>> run_all_tests(robot)  # Tous les tests sauf démos")
    print("\nN'oubliez pas d'appeler robot.cleanup() à la fin!")
    print("\n" + "="*50)
    print("Exécution automatique: Tous les tests de base")
    print("="*50 + "\n")

    # Initialiser le robot
    robot = KS4034F()

    try:
        # Exécuter automatiquement tous les tests de base
        run_all_tests(robot)

    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur")
    except Exception as e:
        print(f"\nErreur: {e}")
        import sys
        sys.print_exception(e)
    finally:
        # Toujours nettoyer à la fin
        robot.cleanup()
        print("\nNettoyage terminé")


def run_all_tests(robot):
    """Exécute tous les tests (sans les démos)"""
    # test_motors(robot)
    # test_movements(robot)
    # test_leds(robot)
    test_servo(robot)
    # test_line_tracking(robot)
    # test_ultrasonic(robot)


# Point d'entrée
if __name__ == "__main__":
    main()
