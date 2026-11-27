from pins import *
import time

# Nombre de mesures par test
N_MEASURES = 10

# --- Fonction de mesure moyenne ---
def measure_average(n=N_MEASURES, action_before=None, action_after=None):
    values = []
    if action_before:
        action_before()
        sleep(2)  # temps de stabilisation

    for _ in range(n):
        val = BATTERY.current()  # lecture courant (mA)
        values.append(val)
        sleep(0.5)

    if action_after:
        action_after()

    return sum(values) / len(values) if values else 0

# --- Génération d’un son ---
def tone(pin, freq, duration_ms):
    if freq == 0:
        time.sleep_ms(duration_ms)
        return
    period_us = int(1_000_000 / freq)
    half_period = period_us // 2
    end_time = time.ticks_add(time.ticks_us(), duration_ms * 1000)
    while time.ticks_diff(end_time, time.ticks_us()) > 0:
        pin.on()
        time.sleep_us(half_period)
        pin.off()
        time.sleep_us(half_period)

# --- Mesure de consommation du buzzer ---
def measure_buzzer(freq, duration_ms):
    def buzzer_on():
        tone(SPEAKER, freq, duration_ms)  # génère un son
    def buzzer_off():
        SPEAKER.off()

    return measure_average(action_before=buzzer_on, action_after=buzzer_off)

# --- Boucle principale ---
def run_buzzer_tests():
    freqs = [200, 500, 1000, 2000, 4000]   # fréquences Hz à tester
    durations = [200, 500, 1000]           # durées en ms

    print("==== Mesure consommation buzzer ====")

    # Mesure témoin (buzzer éteint)
    current_temoin = measure_average()
    print(f"Conso témoin (buzzer OFF): {current_temoin:.2f} mA")

    for f in freqs:
        for d in durations:
            current = measure_buzzer(f, d)
            print(f"Freq: {f} Hz | Duree: {d} ms | Conso: {current:.2f} mA | Diff: {current - current_temoin:.2f} mA")

            # Affichage OLED
            SCREEN.clear()
            show_lines([
                f"Freq : {f}Hz",
                f"Duree: {d}ms",
                f"Conso: {current:.1f}mA",
                f"Diff : {current - current_temoin:.1f}mA",
            ])
            SCREEN.show()
            sleep(2)

            # Effacer l'écran avant le test suivant
            SCREEN.clear()
            SCREEN.show()
            sleep(1)


    print("==== Fin des mesures ====")

# Lance les tests
run_buzzer_tests()
