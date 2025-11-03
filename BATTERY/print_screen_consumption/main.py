from pins import *
from time import sleep

def show_text():
        display.fill(0)
        centerText("Consommation:", 60)
        display.show()

def centerText(text, y):
    length = len(text)
    position = (128 - (length * 8)) // 2
    display.text(text, position, y)

def measure_average(n, action_before=None, action_after=None):
    """
    Prend n mesures avec fg.current_average(), fait la moyenne
    action_before: fonction optionnelle à exécuter avant la série de mesures
    action_after: fonction optionnelle à exécuter après la série de mesures
    """
    values = []
    if action_before:
        action_before()
        sleep(2)  # temps pour stabiliser
    
    for _ in range(n):
        val = fg.current_average()
        values.append(val)
        sleep(1)  # délai entre mesures
    
    if action_after:
        action_after()
    
    return sum(values) / len(values) if values else 0

# Nombre de mesures pour la consommation
N_MEASURES = 10

while True:
    display.fill(0)
    display.show()
    print("=== Mesure de consommation d'energie ===")

    # 1. Mesure écran éteint (rétroéclairage actif mais aucun pixel allumé)
    avg_off = measure_average(N_MEASURES, action_before=lambda: (display.fill(0), display.show()))
    print("1. Moyenne consommation ecran vide : {:.2f} mA".format(avg_off))

    # 2. Mesure écran avec texte affiché
    avg_text = measure_average(N_MEASURES, action_before=show_text)
    print("2. Moyenne consommation ecran avec texte : {:.2f} mA".format(avg_text))

    # 3. Mesure écran plein (tous pixels allumés)
    avg_full = measure_average(N_MEASURES, action_before=lambda: (display.fill(1), display.show()))
    print("3. Moyenne consommation plein ecran : {:.2f} mA".format(avg_full))

    # Affichage des résultats sur l'écran
    display.fill(0)
    centerText("Moyennes:", 20)
    centerText("pour {} mesures".format(N_MEASURES), 30)
    centerText("Off : {:.1f} mA".format(avg_off), 50)
    centerText("Texte : {:.1f} mA".format(avg_text), 70)
    centerText("Full : {:.1f} mA".format(avg_full), 90)
    display.show()

    print("========================================")
    sleep(15)  # pause avant nouvelle série de mesures
