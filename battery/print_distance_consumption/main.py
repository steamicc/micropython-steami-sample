from pins import *
from time import sleep

# Nombre de mesures pour la consommation
N_MEASURES = 10

def measure_average(n=N_MEASURES, action_before=None, action_after=None):
    """
    Prend n mesures avec BATTERY.current(), fait la moyenne
    action_before: fonction optionnelle à exécuter avant la série de mesures
    action_after: fonction optionnelle à exécuter après la série de mesures
    """
    values = []
    if action_before:
        action_before()
        sleep(2)  # temps pour stabiliser

    for _ in range(n):
        val = BATTERY.current()
        values.append(val)
        sleep(1)  # délai entre mesures

    if action_after:
        action_after()

    return sum(values) / len(values) if values else 0

# Boucle principale
while True:
    # Mesure sans activer le capteur (distance non lue)
    curr_idle = measure_average()
    print("================================")
    print(f"Consommation capteur OFF: {curr_idle:.2f} mA")

    # Mesure avec le capteur actif (distance lue)
    dist = DISTANCE.read()
    curr_active = measure_average()
    print(f"Distance: {dist} mm, consommation capteur ON: {curr_active:.2f} mA")

    # Affichage sur OLED
    SCREEN.clear()
    show_lines([
        "Consommation",
        "capteur VL53L1X",
        f"OFF: {curr_idle:.1f} mA",
        f"ON : {curr_active:.1f} mA",
        f"Diff: {curr_active - curr_idle:.1f} mA",
        "Distance:",
        f"{dist} mm",
    ])
    SCREEN.show()

    sleep(5)  # délai avant la prochaine mesure
    SCREEN.clear() # effacer l'écran
    SCREEN.show() # mettre à jour l'écran
    sleep(1) # court délai avant la prochaine boucle
