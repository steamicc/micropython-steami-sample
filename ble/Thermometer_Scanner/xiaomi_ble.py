"""Decode the BLE advertising of Xiaomi LYWSD03MMC thermo-hygrometers.

Runs on MicroPython (STeaMi board) and on CPython. Formats of the pvvx
firmware (https://github.com/pvvx/ATC_MiThermometer): "custom" (pvvx),
"atc1441" and unencrypted BTHome v2. The original Xiaomi firmware (MiBeacon,
encrypted) is only reported.
"""

import math
import struct

UUID_ENV = 0x181A  # pvvx and atc1441
UUID_BTHOME = 0xFCD2
UUID_MIBEACON = 0xFE95

# BTHome v2: data size of each object, by object id
_BTHOME_SIZES = {
    0x00: 1, 0x01: 1, 0x02: 2, 0x03: 2, 0x04: 3, 0x05: 3, 0x06: 2, 0x07: 2,
    0x08: 2, 0x09: 1, 0x0A: 3, 0x0B: 3, 0x0C: 2, 0x0D: 2, 0x0E: 2, 0x0F: 1,
    0x10: 1, 0x11: 1, 0x12: 2, 0x13: 2, 0x14: 2, 0x2E: 1, 0x2F: 1, 0x3A: 1,
    0x3F: 2, 0x40: 2, 0x41: 2, 0x42: 3, 0x43: 2, 0x44: 2, 0x45: 2, 0x46: 1,
    0x47: 2, 0x48: 2, 0x49: 2, 0x4A: 2, 0x4B: 3, 0x4C: 4, 0x4D: 4, 0x4E: 4,
    0x4F: 4, 0x50: 4, 0x51: 2, 0x52: 2,
}
for _i in range(0x15, 0x2E):  # binary sensors
    _BTHOME_SIZES.setdefault(_i, 1)


def _mac(octets):
    return ":".join("{:02X}".format(b) for b in octets)


def _service_data(frame):
    """Service data (AD type 0x16) of an advertising frame: list of (uuid, data)."""
    found = []
    i = 0
    while i + 1 < len(frame):
        length = frame[i]
        if length == 0 or i + 1 + length > len(frame):
            break
        if frame[i + 1] == 0x16 and length >= 3:
            uuid = frame[i + 2] | (frame[i + 3] << 8)
            found.append((uuid, bytes(frame[i + 4 : i + 1 + length])))
        i += 1 + length
    return found


def _pvvx(d):
    t, h, mv, percent = struct.unpack("<hHHB", d[6:13])
    return {"format": "pvvx", "mac": _mac(d[5 - i] for i in range(6)), "temperature": t / 100,
            "humidity": h / 100, "battery": percent, "voltage": mv / 1000}


def _atc1441(d):
    t, h, percent, mv = struct.unpack(">hBBH", d[6:12])
    return {"format": "atc1441", "mac": _mac(d[0:6]), "temperature": t / 10,
            "humidity": float(h), "battery": percent, "voltage": mv / 1000}


def _bthome(d):
    if not d or d[0] & 0x01:  # empty or encrypted
        return None
    m = {"format": "bthome", "mac": None, "temperature": None, "humidity": None,
         "battery": None, "voltage": None}
    i = 1
    while i < len(d):
        oid = d[i]
        size = _BTHOME_SIZES.get(oid)
        if size is None or i + 1 + size > len(d):
            break  # unknown or truncated object: keep what came before
        v = d[i + 1 : i + 1 + size]
        if oid == 0x01:
            m["battery"] = v[0]
        elif oid == 0x02:
            m["temperature"] = struct.unpack("<h", v)[0] / 100
        elif oid == 0x45:
            m["temperature"] = struct.unpack("<h", v)[0] / 10
        elif oid == 0x03:
            m["humidity"] = struct.unpack("<H", v)[0] / 100
        elif oid == 0x2E:
            m["humidity"] = float(v[0])
        elif oid == 0x0C:
            m["voltage"] = struct.unpack("<H", v)[0] / 1000
        i += 1 + size
    if m["temperature"] is None and m["humidity"] is None:
        return None
    return m


def decode(frame):
    """Readings of an advertising frame, or None if it is not a readable thermometer.

    Returns a dict: format, mac (None for BTHome: use the BLE address),
    temperature (°C), humidity (% RH), battery (%), voltage (V).
    """
    for uuid, d in _service_data(frame or b""):
        if uuid == UUID_ENV and len(d) >= 15:
            return _pvvx(d)
        if uuid == UUID_ENV and len(d) >= 13:
            return _atc1441(d)
        if uuid == UUID_BTHOME:
            m = _bthome(d)
            if m:
                return m
        if uuid == UUID_MIBEACON:
            return {"format": "mibeacon"}
    return None


def _saturation_pressure(t):
    """Saturation vapour pressure (hPa) at t °C, Magnus formula (Sonntag 1990)."""
    return 6.112 * math.exp(17.62 * t / (243.12 + t))


def humidity_at(t_ref, h_ref, t_target):
    """Relative humidity (%) of the reference air brought to t_target °C.

    The amount of water vapour does not change; only the saturation pressure
    follows the temperature. Used to compare the humidity of a board that
    warms up with a reference left at room temperature. None if a reading is
    missing.
    """
    for v in (t_ref, h_ref, t_target):
        if v is None or math.isnan(v):
            return None
    return h_ref * _saturation_pressure(t_ref) / _saturation_pressure(t_target)
