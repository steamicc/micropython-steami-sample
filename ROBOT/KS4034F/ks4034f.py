"""
Bibliothèque MicroPython pour le robot Keyestudio KS4034F
Portage de la bibliothèque MakeCode originale
"""

from machine import I2C
from pyb import Pin, Timer
from time import sleep_us, sleep_ms, ticks_us, ticks_diff


class MotorPosition:
    """Position des moteurs sur le robot"""
    UPPER_LEFT = 0
    LOWER_LEFT = 1
    UPPER_RIGHT = 2
    LOWER_RIGHT = 3


class MotorDirection:
    """Direction de rotation des moteurs"""
    FORWARD = 0
    BACK = 1


class LineTrackingSensor:
    """Position des capteurs de suivi de ligne"""
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class LedCount:
    """Identifiants des LEDs colorées"""
    LEFT = 0x09
    RIGHT = 0x0A


class LedState:
    """États des LEDs"""
    ON = 4095
    OFF = 0


class Colors:
    """Couleurs prédéfinies (RGB en format 24-bit)"""
    RED = 0xFF0000
    ORANGE = 0xFFA500
    YELLOW = 0xFFFF00
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    INDIGO = 0x4B0082
    VIOLET = 0x8A2BE2
    PURPLE = 0xFF00FF
    WHITE = 0xFFFFFF
    BLACK = 0x000000


class KS4034F:
    """
    Classe principale pour contrôler le robot Keyestudio KS4034F
    """

    STC15_ADDRESS = 0x30  # Adresse I2C du contrôleur

    # Mapping des registres des moteurs
    MOTOR_REGISTERS = {
        MotorPosition.UPPER_RIGHT: (0x01, 0x02),   # M1A, M1B
        MotorPosition.UPPER_LEFT: (0x03, 0x04),    # M2A, M2B
        MotorPosition.LOWER_RIGHT: (0x05, 0x06),   # M3A, M3B
        MotorPosition.LOWER_LEFT: (0x07, 0x08)     # M4A, M4B
    }

    def __init__(self, i2c_bus=3, servo_pin="P0", trig_pin="P15", echo_pin="P16",
                 line_left_pin="P3", line_center_pin="P4", line_right_pin="P10"):
        """
        Initialise le robot KS4034F

        Args:
            i2c_bus: Numéro du bus I2C (par défaut 3)
            servo_pin: Pin du servo moteur (par défaut 14)
            trig_pin: Pin trigger du capteur ultrason (par défaut 15)
            echo_pin: Pin echo du capteur ultrason (par défaut 16)
            line_left_pin: Pin du capteur de ligne gauche (par défaut 3)
            line_center_pin: Pin du capteur de ligne central (par défaut 4)
            line_right_pin: Pin du capteur de ligne droit (par défaut 10)
        """
        # Initialisation I2C
        self.i2c = I2C(i2c_bus)

        # Initialisation du servo avec Timer (pour STM32)
        self.servo_pin = servo_pin
        # pyb.Pin nécessite le mode OUT_PP pour PWM
        self.servo_pin_obj = Pin(servo_pin, Pin.OUT_PP)
        # Sur STM32, on utilise pyb.Timer pour PWM
        self.servo_timer = None
        self.servo_channel = None

        # Initialisation capteur ultrason
        self.trig = Pin(trig_pin, Pin.OUT_PP)
        self.echo = Pin(echo_pin, Pin.IN)
        self.last_ultrasonic_time = 0

        # Initialisation capteurs de ligne
        self.line_sensors = {
            LineTrackingSensor.LEFT: Pin(line_left_pin, Pin.IN),
            LineTrackingSensor.CENTER: Pin(line_center_pin, Pin.IN),
            LineTrackingSensor.RIGHT: Pin(line_right_pin, Pin.IN)
        }

    def _i2c_write(self, reg, value):
        """
        Écrit une valeur dans un registre I2C

        Args:
            reg: Registre à écrire
            value: Valeur à écrire (0-255)
        """
        buf = bytearray([reg, value])
        self.i2c.writeto(self.STC15_ADDRESS, buf)

    def motor(self, position, direction, speed):
        """
        Contrôle un moteur individuel

        Args:
            position: Position du moteur (MotorPosition.UPPER_LEFT, etc.)
            direction: Direction (MotorDirection.FORWARD ou BACK)
            speed: Vitesse en pourcentage (0-100)
        """
        # Convertir le pourcentage en valeur 0-255
        speed_value = int((speed / 100) * 255)
        speed_value = max(0, min(255, speed_value))  # Limiter entre 0 et 255

        # Récupérer les registres du moteur
        reg_a, reg_b = self.MOTOR_REGISTERS[position]

        # Définir la direction
        if direction == MotorDirection.FORWARD:
            if position in [MotorPosition.UPPER_RIGHT, MotorPosition.LOWER_RIGHT]:
                # Moteurs droits (M1 et M3)
                self._i2c_write(reg_a, speed_value)
                self._i2c_write(reg_b, 0)
            else:
                # Moteurs gauches (M2 et M4)
                self._i2c_write(reg_a, 0)
                self._i2c_write(reg_b, speed_value)
        else:  # BACK
            if position in [MotorPosition.UPPER_RIGHT, MotorPosition.LOWER_RIGHT]:
                # Moteurs droits (M1 et M3)
                self._i2c_write(reg_a, 0)
                self._i2c_write(reg_b, speed_value)
            else:
                # Moteurs gauches (M2 et M4)
                self._i2c_write(reg_a, speed_value)
                self._i2c_write(reg_b, 0)

    def stop(self):
        """Arrête tous les moteurs"""
        for reg_a, reg_b in self.MOTOR_REGISTERS.values():
            self._i2c_write(reg_a, 0)
            self._i2c_write(reg_b, 0)

    def move_forward(self, speed):
        """
        Avance tout droit

        Args:
            speed: Vitesse en pourcentage (0-100)
        """
        self.motor(MotorPosition.UPPER_LEFT, MotorDirection.FORWARD, speed)
        self.motor(MotorPosition.LOWER_LEFT, MotorDirection.FORWARD, speed)
        self.motor(MotorPosition.UPPER_RIGHT, MotorDirection.FORWARD, speed)
        self.motor(MotorPosition.LOWER_RIGHT, MotorDirection.FORWARD, speed)

    def move_backward(self, speed):
        """
        Recule tout droit

        Args:
            speed: Vitesse en pourcentage (0-100)
        """
        self.motor(MotorPosition.UPPER_LEFT, MotorDirection.BACK, speed)
        self.motor(MotorPosition.LOWER_LEFT, MotorDirection.BACK, speed)
        self.motor(MotorPosition.UPPER_RIGHT, MotorDirection.BACK, speed)
        self.motor(MotorPosition.LOWER_RIGHT, MotorDirection.BACK, speed)

    def turn_left(self, speed):
        """
        Tourne à gauche (rotation sur place)

        Args:
            speed: Vitesse en pourcentage (0-100)
        """
        self.motor(MotorPosition.UPPER_LEFT, MotorDirection.BACK, speed)
        self.motor(MotorPosition.LOWER_LEFT, MotorDirection.BACK, speed)
        self.motor(MotorPosition.UPPER_RIGHT, MotorDirection.FORWARD, speed)
        self.motor(MotorPosition.LOWER_RIGHT, MotorDirection.FORWARD, speed)

    def turn_right(self, speed):
        """
        Tourne à droite (rotation sur place)

        Args:
            speed: Vitesse en pourcentage (0-100)
        """
        self.motor(MotorPosition.UPPER_LEFT, MotorDirection.FORWARD, speed)
        self.motor(MotorPosition.LOWER_LEFT, MotorDirection.FORWARD, speed)
        self.motor(MotorPosition.UPPER_RIGHT, MotorDirection.BACK, speed)
        self.motor(MotorPosition.LOWER_RIGHT, MotorDirection.BACK, speed)

    def set_led(self, led, state):
        """
        Contrôle les LEDs colorées

        Args:
            led: LED à contrôler (LedCount.LEFT ou RIGHT)
            state: État de la LED (LedState.ON ou OFF)
        """
        self._i2c_write(led, state)

    def set_servo_angle(self, angle):
        """
        Définit l'angle du servo moteur

        Args:
            angle: Angle en degrés (-90 à 90)

        Note:
            Sur certaines cartes comme la STEAMI, la pin P14 (PB14) ne supporte pas le PWM.
            Le servo ne sera pas fonctionnel dans ce cas.
        """
        # Marquer comme tenté si c'est la première fois
        if self.servo_timer is None and self.servo_channel is None:
            print(f"Tentative d'initialisation du servo sur {self.servo_pin}...")

            # Essayer différents timers jusqu'à en trouver un qui fonctionne
            success = False
            for timer_id in [1, 2, 3, 4, 5, 8, 12, 15, 16, 17]:
                if success:
                    break

                try:
                    print(f"  Essai Timer {timer_id}...")
                    test_timer = Timer(timer_id, freq=50)

                    # Essayer différents canaux
                    for channel_id in [1, 2, 3, 4]:
                        try:
                            print(f"    Essai Canal {channel_id}...", end=" ")
                            test_channel = test_timer.channel(
                                channel_id,
                                Timer.PWM,
                                pin=self.servo_pin_obj
                            )
                            # Succès !
                            self.servo_timer = test_timer
                            self.servo_channel = test_channel
                            print(f"OK!")
                            print(f"✓ Servo initialisé: Timer {timer_id}, Canal {channel_id}")
                            success = True
                            break
                        except Exception as e:
                            # Ce canal ne fonctionne pas, continuer
                            print(f"Échec ({type(e).__name__}: {e})")

                    if not success:
                        # Aucun canal n'a fonctionné, libérer le timer
                        test_timer.deinit()

                except Exception as e:
                    # Ce timer n'existe pas ou n'est pas disponible
                    print(f"  Timer {timer_id} non disponible ({type(e).__name__})")
                    continue

            if not success:
                # Marquer comme indisponible (utiliser False au lieu de None)
                self.servo_timer = False
                self.servo_channel = False
                print(f"✗ ATTENTION: La pin {self.servo_pin} ne supporte pas le PWM")
                print("  Le servo moteur ne sera pas fonctionnel.")
                print("  Si vous avez besoin du servo, reconnectez-le sur une pin PWM")
                print("  (PA_0/P0, PA_1/P1, PA_2/P2, PA_8/P11 selon la carte)")
                return

        # Si le servo n'est pas disponible, ne rien faire
        if self.servo_channel is False:
            return

        angle = max(-90, min(90, angle))  # Limiter entre -90 et 90

        # Convertir l'angle en largeur d'impulsion
        # Servo standard: 1ms (-90°) à 2ms (+90°) avec signal 50Hz (20ms période)
        pulse_width_ms = 1.5 + (angle / 90.0) * 0.5  # 1ms à 2ms
        duty_percent = (pulse_width_ms / 20.0) * 100  # Convertir en %

        # Appliquer le duty cycle
        try:
            self.servo_channel.pulse_width_percent(int(duty_percent))
        except Exception as e:
            print(f"Erreur lors du contrôle du servo: {e}")

    def read_line_sensor(self, sensor):
        """
        Lit un capteur de suivi de ligne

        Args:
            sensor: Capteur à lire (LineTrackingSensor.LEFT, CENTER, ou RIGHT)

        Returns:
            0 si ligne noire détectée, 1 sinon
        """
        return self.line_sensors[sensor].value()

    def read_ultrasonic(self):
        """
        Lit la distance du capteur ultrason

        Returns:
            Distance en centimètres (0 si erreur)
        """
        # Envoyer une impulsion trigger
        self.trig.value(0)
        sleep_us(2)
        self.trig.value(1)
        sleep_us(10)
        self.trig.value(0)

        # Mesurer le temps de l'écho (timeout 35ms = ~6m)
        timeout = 35000
        start = ticks_us()

        # Attendre que l'écho passe à HIGH
        while self.echo.value() == 0:
            if ticks_diff(ticks_us(), start) > timeout:
                # Utiliser la dernière valeur valide si disponible
                if self.last_ultrasonic_time != 0:
                    return round(self.last_ultrasonic_time / 58)
                return 0

        pulse_start = ticks_us()

        # Attendre que l'écho passe à LOW
        while self.echo.value() == 1:
            if ticks_diff(ticks_us(), pulse_start) > timeout:
                if self.last_ultrasonic_time != 0:
                    return round(self.last_ultrasonic_time / 58)
                return 0

        pulse_end = ticks_us()
        pulse_duration = ticks_diff(pulse_end, pulse_start)

        # Sauvegarder pour la prochaine fois
        if pulse_duration > 0:
            self.last_ultrasonic_time = pulse_duration

        # Calculer la distance en cm (vitesse du son: 343 m/s)
        # distance = (temps * vitesse du son) / 2
        # temps en microsecondes, donc distance en cm = temps / 58
        distance = round(pulse_duration / 58)

        return distance

    def cleanup(self):
        """Nettoie les ressources (arrête les moteurs et le servo)"""
        self.stop()
        if self.servo_timer is not None and self.servo_timer is not False:
            try:
                self.servo_timer.deinit()
            except:
                pass
