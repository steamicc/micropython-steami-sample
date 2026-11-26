"""
Test basique de servo moteur avec Timer PWM sur STM32
Balaye le servo de -90° à +90° et retour

Ce test permet de valider :
1. Que la pin choisie supporte le PWM
2. Quel Timer/Channel fonctionne pour cette pin
3. Le bon fonctionnement du servo moteur
"""

from pyb import Pin, Timer
from time import sleep


def angle_to_duty(angle):
    """
    Convertit un angle (-90 à 90) en duty cycle %

    Args:
        angle: Angle en degrés (-90 à 90)

    Returns:
        Duty cycle en pourcentage (5% à 10%)
    """
    # Servo standard: 1ms (-90°) à 2ms (+90°)
    # Période = 20ms (50Hz)
    # 1ms = 5%, 1.5ms = 7.5%, 2ms = 10%
    pulse_width_ms = 1.5 + (angle / 90.0) * 0.5
    duty_percent = (pulse_width_ms / 20.0) * 100
    return duty_percent


def test_servo_on_pin(pin_name, timer_id, channel_id):
    """
    Test un servo sur une pin spécifique avec un timer et canal donnés

    Args:
        pin_name: Nom de la pin (ex: "P0", "P11")
        timer_id: Numéro du timer (ex: 1, 2, 3)
        channel_id: Numéro du canal (ex: 1, 2, 3, 4)

    Returns:
        True si le test réussit, False sinon
    """
    print(f"\n{'='*50}")
    print(f"Test servo sur {pin_name} avec Timer {timer_id} Canal {channel_id}")
    print(f"{'='*50}")

    try:
        # Créer l'objet Pin en mode OUT_PP (nécessaire pour PWM)
        pin = Pin(pin_name, Pin.OUT_PP)
        print(f"✓ Pin {pin_name} créée")

        # Créer le Timer à 50Hz (fréquence standard servo)
        timer = Timer(timer_id, freq=50)
        print(f"✓ Timer {timer_id} initialisé à 50Hz")

        # Créer le canal PWM
        channel = timer.channel(channel_id, Timer.PWM, pin=pin)
        print(f"✓ Canal {channel_id} PWM créé")

        print("\nTest de balayage du servo:")
        print("Le servo va bouger de -90° à +90° puis retour")
        print("Observez le mouvement du servo\n")

        # Test: balayage de -90° à +90°
        print("Balayage vers la droite (-90° -> +90°)...")
        for angle in range(-90, 91, 10):
            duty = angle_to_duty(angle)
            channel.pulse_width_percent(int(duty))
            print(f"  Angle: {angle:4d}° (duty: {duty:.1f}%)")
            sleep(0.3)

        sleep(0.5)

        # Test: retour de +90° à -90°
        print("\nBalayage vers la gauche (+90° -> -90°)...")
        for angle in range(90, -91, -10):
            duty = angle_to_duty(angle)
            channel.pulse_width_percent(int(duty))
            print(f"  Angle: {angle:4d}° (duty: {duty:.1f}%)")
            sleep(0.3)

        # Retour au centre
        print("\nRetour au centre (0°)...")
        channel.pulse_width_percent(int(angle_to_duty(0)))
        sleep(0.5)

        print("\n✓ Test réussi!")
        print(f"  La pin {pin_name} fonctionne avec Timer {timer_id} Canal {channel_id}")

        # Nettoyage
        timer.deinit()
        return True

    except Exception as e:
        print(f"\n✗ Erreur: {type(e).__name__}: {e}")
        return False


def auto_detect_servo_pin(pin_name):
    """
    Détecte automatiquement quel Timer/Channel fonctionne pour une pin

    Args:
        pin_name: Nom de la pin à tester (ex: "P11")

    Returns:
        Tuple (timer_id, channel_id) si trouvé, None sinon
    """
    print(f"\n{'='*60}")
    print(f"Détection automatique pour la pin {pin_name}")
    print(f"{'='*60}")

    # Liste des timers et canaux à essayer
    timers_to_test = [1, 2, 3, 4, 5, 8, 12, 15, 16, 17]
    channels_to_test = [1, 2, 3, 4]

    for timer_id in timers_to_test:
        try:
            pin = Pin(pin_name, Pin.OUT_PP)
            timer = Timer(timer_id, freq=50)

            for channel_id in channels_to_test:
                try:
                    print(f"Essai: Timer {timer_id} Canal {channel_id}...", end=" ")
                    channel = timer.channel(channel_id, Timer.PWM, pin=pin)
                    print("✓ SUCCÈS!")

                    # Test trouvé, nettoyer et retourner
                    timer.deinit()
                    return (timer_id, channel_id)

                except Exception as e:
                    print(f"✗ ({type(e).__name__})")

            # Nettoyer ce timer si aucun canal n'a marché
            timer.deinit()

        except Exception as e:
            print(f"Timer {timer_id} non disponible ({type(e).__name__})")

    print(f"\n✗ Aucune configuration PWM trouvée pour {pin_name}")
    return None


# Configuration par défaut
# Modifiez ces valeurs selon votre câblage
DEFAULT_PIN = "P11"     # Pin où est connecté le servo (P11 = PA_8 = TIM1_CH1)


def main():
    """Programme principal"""
    print("="*60)
    print("Test de Servo Moteur - Balayage (Sweep)")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Pin: {DEFAULT_PIN}")

    # Méthode 1: Détection automatique
    print("\n" + "="*60)
    print("MÉTHODE 1: Détection automatique")
    print("="*60)

    result = auto_detect_servo_pin(DEFAULT_PIN)

    if result:
        timer_id, channel_id = result
        print(f"\n✓ Configuration trouvée: Timer {timer_id}, Canal {channel_id}")
        print("\nLancement du test de balayage...")
        sleep(1)
        test_servo_on_pin(DEFAULT_PIN, timer_id, channel_id)
    else:
        print(f"\n✗ La pin {DEFAULT_PIN} ne supporte pas le PWM")
        print("\nPins PWM disponibles sur STM32 (selon datasheet):")
        print("  PA_0 (P0)  - TIM2_CH1")
        print("  PA_1 (P1)  - TIM2_CH2")
        print("  PA_2 (P2)  - TIM2_CH3")
        print("  PA_8 (P11) - TIM1_CH1")
        print("  PA_9       - TIM1_CH2")
        print("  PA_10      - TIM1_CH3")
        print("\nModifiez DEFAULT_PIN dans le code pour essayer une autre pin")

    print("\n" + "="*60)
    print("Test terminé")
    print("="*60)


if __name__ == "__main__":
    main()
