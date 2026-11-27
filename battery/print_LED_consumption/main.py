from pins import *   # Pour accéder à BATTERY.current()

# --- Paramètres ---
N_MEASURES = 10

# --- Fonction de mesure ---
def measure_average(n=N_MEASURES, action_before=None, action_after=None):
    values = []
    if action_before:
        action_before()
        sleep(2)  # stabilisation
    for _ in range(n):
        val = BATTERY.current()  # mesure courant
        values.append(val)
        sleep(1)
    if action_after:
        action_after()
    return sum(values)/len(values) if values else 0

# --- Mesures pour LEDs ---
def measure_leds(leds, names):
    # Préparation actions
    def leds_on():
        for led in leds:
            led.on()
    def leds_off():
        for led in leds:
            led.off()
    # Mesure avec LEDs allumées
    curr_on = measure_average(action_before=leds_on, action_after=leds_off)
    return curr_on

# --- Boucle principale ---
while True:
    SCREEN.clear() # Effacer l'écran
    SCREEN.show() # Mettre à jour l'écran

    sleep(1)  # Pause avant mesures

    # Mesure témoin (LEDs éteintes)
    curr_temoin = measure_average()

    # LED Rouge
    curr_red = measure_leds([LED_RED], ["Rouge"])
    # LED Verte
    curr_green = measure_leds([LED_GREEN], ["Vert"])
    # LED Bleue
    curr_blue = measure_leds([LED_BLUE], ["Bleu"])
    # Rouge + Verte
    curr_rg = measure_leds([LED_RED, LED_GREEN], ["Rouge","Vert"])
    # Rouge + Bleue
    curr_rb = measure_leds([LED_RED, LED_BLUE], ["Rouge","Bleu"])
    # Verte + Bleue
    curr_gb = measure_leds([LED_GREEN, LED_BLUE], ["Vert","Bleu"])
    # Toutes LEDs
    curr_all = measure_leds([LED_RED, LED_GREEN, LED_BLUE], ["Rouge","Vert","Bleu"])

    # Affichage résultats
    SCREEN.clear()
    show_lines([
        f"T : {curr_temoin:.1f} mA",
        f"R : {curr_red:.1f} mA",
        f"V : {curr_green:.1f} mA",
        f"B : {curr_blue:.1f} mA",
        f"R+V : {curr_rg:.1f} mA",
        f"R+B : {curr_rb:.1f} mA",
        f"V+B : {curr_gb:.1f} mA",
        f"All : {curr_all:.1f} mA",
    ])
    SCREEN.show()

    print("========== Resultats ==========")
    print(f"Temoin : {curr_temoin:.2f} mA")
    print(f"Rouge: {curr_red:.2f} mA soit {curr_red - curr_temoin:.2f} mA d'ecart avec temoin")
    print(f"Vert : {curr_green:.2f} mA soit {curr_green - curr_temoin:.2f} mA d'ecart avec temoin")
    print(f"Bleu : {curr_blue:.2f} mA soit {curr_blue - curr_temoin:.2f} mA d'ecart avec temoin")
    print(f"Rouge + Vert: {curr_rg:.2f} mA soit {curr_rg - curr_temoin:.2f} mA d'ecart avec temoin")
    print(f"Rouge + Bleu: {curr_rb:.2f} mA soit {curr_rb - curr_temoin:.2f} mA d'ecart avec temoin")
    print(f"Vert + Bleu : {curr_gb:.2f} mA soit {curr_gb - curr_temoin:.2f} mA d'ecart avec temoin")
    print(f"Toutes LEDs: {curr_all:.2f} mA soit {curr_all - curr_temoin:.2f} mA d'ecart avec temoin")

    sleep(10)  # délai avant relance des mesures
