from pins import *
from time import sleep
from steami_screen import WHITE

def show_text():
        SCREEN.clear()
        SCREEN.text("Consommation:", "CENTER")
        SCREEN.show()

def measure_average(n, action_before=None, action_after=None):
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

# Nombre de mesures pour la consommation
N_MEASURES = 10

while True:
    SCREEN.clear()
    SCREEN.show()
    print("=== Mesure de consommation d'energie ===")

    # 1. Mesure écran éteint (rétroéclairage actif mais aucun pixel allumé)
    avg_off = measure_average(N_MEASURES, action_before=lambda: (SCREEN.clear(), SCREEN.show()))
    print("1. Moyenne consommation ecran vide : {:.2f} mA".format(avg_off))

    # 2. Mesure écran avec texte affiché
    avg_text = measure_average(N_MEASURES, action_before=show_text)
    print("2. Moyenne consommation ecran avec texte : {:.2f} mA".format(avg_text))

    # 3. Mesure écran plein (tous pixels allumés)
    avg_full = measure_average(N_MEASURES, action_before=lambda: (SCREEN.clear(WHITE), SCREEN.show()))
    print("3. Moyenne consommation plein ecran : {:.2f} mA".format(avg_full))

    # Affichage des résultats sur l'écran
    SCREEN.clear()
    show_lines([
        "Moyennes:",
        "pour {} mesures".format(N_MEASURES),
        "Off : {:.1f} mA".format(avg_off),
        "Texte : {:.1f} mA".format(avg_text),
        "Full : {:.1f} mA".format(avg_full),
    ], gap=6)
    SCREEN.show()

    print("========================================")
    sleep(15)  # pause avant nouvelle série de mesures
