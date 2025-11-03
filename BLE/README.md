### 🛠 BLE Timeout Issue on STeaMi

If you encounter a **timeout or failure** when calling:

```python
from bluetooth import BLE
BLE().active(True)
```

This may be due to a missing or incompatible BLE firmware on your STM32WB chip.

#### ✅ Solution:

To resolve this issue, you need to update the wireless stack of your STeaMi device. Follow these steps:

1. Visit the following website to download and update the wireless stack:  
   [Update STeaMi Wireless Stack](https://steamicc.github.io/steami-tools/webusb-wireless-stack/index.html)

2. On the site, you will find the necessary tools and instructions to update the firmware and the BLE stack on your STM32WB device.

3. Once updated, you should be able to activate BLE without any issues.

After flashing the firmware, BLE should activate without issues:

```python
>>> from bluetooth import BLE
>>> BLE().active(True)
True
```

This will fix the BLE activation timeout issue on the STeaMi board.