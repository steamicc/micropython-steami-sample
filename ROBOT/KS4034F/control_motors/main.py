"""
Exemple simplifié utilisant la bibliothèque KS4034F
Test de tous les moteurs individuellement
"""

from ks4034f import KS4034F, MotorPosition, MotorDirection
from time import sleep

# Initialiser le robot
robot = KS4034F()

print("Test des 4 moteurs du robot KS4034F")

# Test moteur Avant-Droit (M1)
print("\n1. Test Moteur Avant-Droit (UPPER_RIGHT)")
robot.motor(MotorPosition.UPPER_RIGHT, MotorDirection.FORWARD, 25)
sleep(1)
robot.motor(MotorPosition.UPPER_RIGHT, MotorDirection.BACK, 25)
sleep(1)
robot.stop()

# Test moteur Avant-Gauche (M2)
print("\n2. Test Moteur Avant-Gauche (UPPER_LEFT)")
robot.motor(MotorPosition.UPPER_LEFT, MotorDirection.FORWARD, 25)
sleep(1)
robot.motor(MotorPosition.UPPER_LEFT, MotorDirection.BACK, 25)
sleep(1)
robot.stop()

# Test moteur Arrière-Droit (M3)
print("\n3. Test Moteur Arrière-Droit (LOWER_RIGHT)")
robot.motor(MotorPosition.LOWER_RIGHT, MotorDirection.FORWARD, 25)
sleep(1)
robot.motor(MotorPosition.LOWER_RIGHT, MotorDirection.BACK, 25)
sleep(1)
robot.stop()

# Test moteur Arrière-Gauche (M4)
print("\n4. Test Moteur Arrière-Gauche (LOWER_LEFT)")
robot.motor(MotorPosition.LOWER_LEFT, MotorDirection.FORWARD, 25)
sleep(1)
robot.motor(MotorPosition.LOWER_LEFT, MotorDirection.BACK, 25)
sleep(1)

robot.stop()
print("\nTest terminé - Tous les moteurs arrêtés")

robot.cleanup()