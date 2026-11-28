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

* **Hardware**: STeaMi board, any release (V1a, V1b or V1c)
* **Firmware**: the STeaMi MicroPython firmware **v0.31.0 or later** (`steami-micropython-firmware-vX.Y.Z.hex`) from the [micropython-steami-lib releases](https://github.com/steamicc/micropython-steami-lib/releases); the latest is [v0.31.3](https://github.com/steamicc/micropython-steami-lib/releases/tag/v0.31.3). It includes the drivers, the `steami` layer (with `steami.Screen`) and `aioble`.
* **Tooling**: [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) (official MicroPython tool)

The examples that draw on the screen space their text with `SCREEN.text_height()`, which first ships in [v0.31.0](https://github.com/steamicc/micropython-steami-lib/releases/tag/v0.31.0). On v0.30.x they stop with `AttributeError: text_height`; before v0.30.0, `steami.Screen` does not exist yet and `from steami import Screen` fails with an `ImportError`.

> [!WARNING]
> Firmware v0.31.0 moves the MicroPython filesystem: on a board coming from an older firmware, the first boot reformats it and every file stored on the board is lost. Copy your files off the board before updating.

### Hardware releases

The examples read the sensors through the [`steami` layer](https://github.com/steamicc/micropython-steami-lib/tree/main/lib/steami), which detects the board release and picks the right chip: temperature and humidity come from the WSEN-HIDS on a V1a/V1b and from the BME280 on a V1c. A sensor missing on the board (for example the APDS-9960 light sensor on a V1c) reads as 0 or `nan`, with a one-time `[STeaMi] ... (E20)` message on the console.

The examples draw through `steami.Screen`, which offers the drawing API of [`steami_screen`](https://github.com/steamicc/micropython-steami-lib/tree/main/lib/steami_screen) and picks the screen of the release:

| Release | Screen |
| --- | --- |
| V1a, V1b | SSD1327 OLED, 128x128, 16 grey levels |
| V1c | GC9A01 round TFT, 240x240, 16-colour palette |

The layouts are designed for 128 px and scaled on the 240 px screen, and the text stays inside the circle of the V1c. Create the screen and call `SCREEN.begin()` at the start of the program, before the BLE imports: it allocates the frame buffer in one block.

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
