# MicroPython STeaMi Sample

A collection of MicroPython sample scripts for the **STeaMi** board (STM32WB55). These examples show LED control, button input, BLE communication, battery consumption measurement, small games and multi-board scenarios, for STEAM education and embedded experimentation.

Driver-specific examples (sensors, OLED screen, D-PAD, etc.) live next to their driver in [micropython-steami-lib](https://github.com/steamicc/micropython-steami-lib/tree/main/lib), in each `lib/<driver>/examples/` folder.

---

## 📁 Project Structure

```
micropython-steami-sample/
│
├── basic/      # Basic peripherals (PWM, servo)
├── battery/    # Power consumption measurements with the fuel gauge
├── ble/        # Bluetooth Low Energy communication
├── button/     # Button input examples
├── demo/       # Combined demo (menu, sensors, screen, BLE)
├── game/       # Mini games (dino, snake, tic-tac-toe)
├── led/        # LED control
├── robot/      # Keyestudio KS4034F robot car
└── scenario/   # Multi-board BLE scenarios (peripherals and relays)
```

Each example is a folder containing a `main.py` script and the helper modules it imports (`pins.py`, etc.). Some groups (`battery/`, `scenario/scenario_3/`) share a `pins.py` in their parent folder: copy it next to `main.py` (or mount the parent folder) before running the example.

---

## ✅ Requirements

* **Hardware**: STeaMi board
* **Firmware**: the STeaMi MicroPython firmware, which includes the drivers from micropython-steami-lib and `aioble`
* **Tooling**: [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) (official MicroPython tool)

---

## 🚀 Quick Start with `mpremote`

1. **Install mpremote** if not already installed:

   ```bash
   pip install mpremote
   ```

2. **Connect your board** via USB and verify it's detected:

   ```bash
   mpremote connect list
   ```

3. **Run an example without copying it**. Mounting the example folder makes its helper modules (`pins.py`, etc.) importable:

   ```bash
   cd led/blink
   mpremote mount . run main.py
   ```

4. **Or install it so that it runs on boot**:

   ```bash
   cd led/blink
   mpremote cp *.py :
   mpremote reset
   ```

5. **Open a REPL (optional)**:

   ```bash
   mpremote
   ```

   Then press `Ctrl+C` to stop current execution or `Ctrl+D` to soft reset.

---

## 🧪 Examples

* `led/blink/` — basic LED blink
* `button/set_led_on/` — toggle the RGB LEDs with the A, B and MENU buttons
* `basic/PWM/Servo_Sweep/` — sweep a servo motor with PWM
* `ble/beacon/` to `ble/trilateration/` — BLE localization path, from a beacon to indoor positioning (see `ble/README.md`)
* `ble/STeaMi_adv/` — share distance readings between boards through BLE advertising
* `ble/STeaMi_talk/` — central and peripheral exchanging data over a BLE connection
* `game/dinoSteam/` — a simple endless runner game
* `battery/` — measure the current drawn by each peripheral
* `scenario/` — multi-board BLE mesh scenarios
