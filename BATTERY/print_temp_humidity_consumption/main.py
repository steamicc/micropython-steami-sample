from pins import *
from time import sleep

# Nombre de mesures pour la consommation
N_MEASURES = 5

def measure_average(n=N_MEASURES, action_before=None, action_after=None):
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
        sleep(0.5)  # délai entre mesures
    
    if action_after:
        action_after()
    
    return sum(values) / len(values) if values else 0

# Fonction pour afficher texte centré sur l'écran
def center_text(text, y):
    x = (128 - len(text)*8) // 2
    display.text(text, x, y)

# Fonctions d'accès capteur
def read_temp():
    return SENSOR.temperature()

def read_hum():
    return SENSOR.humidity()

def read_temp_hum():
    return SENSOR.temperature(), SENSOR.humidity()

# Boucle principale
while True:
    print("================================")

    # 1. Consommation capteur inactif
    curr_idle = measure_average()
    print(f"Consommation capteur OFF: {curr_idle:.2f} mA")

    sleep(1) # pause entre mesures

    # 2. Consommation capteur Température seule
    curr_temp = measure_average(action_before=read_temp)
    temp = read_temp()
    print(f"Temp: {temp:.1f}C, consommation TEMP: {curr_temp:.2f} mA")

    sleep(1) # pause entre mesures

    # 3. Consommation capteur Humidité seule
    curr_hum = measure_average(action_before=read_hum)
    hum = read_hum()
    print(f"Hum: {hum:.1f}%, consommation HUM: {curr_hum:.2f} mA")

    sleep(1) # pause entre mesures

    # 4. Consommation capteur Temp + Hum
    curr_both = measure_average(action_before=read_temp_hum)
    temp, hum = read_temp_hum()
    print(f"Temp: {temp:.1f}C, Hum: {hum:.1f}%, consommation BOTH: {curr_both:.2f} mA")

    # Affichage OLED
    display.fill(0)
    center_text("Consommation", 10)
    center_text(f"OFF : {curr_idle:.1f} mA", 30)
    center_text(f"TEMP: {curr_temp:.1f} mA", 45)
    center_text(f"HUM : {curr_hum:.1f} mA", 60)
    center_text(f"BOTH: {curr_both:.1f} mA", 75)
    center_text(f"T:{temp:.1f}C", 95)
    center_text(f"H:{hum:.1f}%", 110)
    display.show()

    # Pause avant nouvelle boucle
    sleep(5)
    display.fill(0)
    display.show()
    sleep(1)
