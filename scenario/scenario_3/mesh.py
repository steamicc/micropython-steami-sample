"""Message format shared by the peripherals and the relays of scenario 3.

A legacy BLE advertisement holds at most 31 bytes, so a message is packed in
binary rather than in JSON:

    Flags                       3 bytes
    Complete Local Name        11 bytes  ("STeaMi-P1")
    Manufacturer Specific Data 10 bytes  (length, type, company ID, message)
                               --------
                               24 bytes

The message itself is 6 bytes, XOR-encrypted with KEY:

    src   uint8  index of the sender in NODES
    dst   uint8  index of the receiver in NODES
    seq   uint8  sequence number of the sender, 0-255 then wraps
    hop   uint8  number of relays the message went through
    value int16  the distance in mm, little-endian
"""

import struct

NODES = (
    "STeaMi-P1",
    "STeaMi-P2",
    "STeaMi-P3",
    "STeaMi-R1",
    "STeaMi-R2",
    "STeaMi-R3",
)

KEY = 0x5A  # Shared XOR key: hides the data, but is not real encryption
COMPANY_ID = 0xFFFF  # Reserved by the Bluetooth SIG for tests and prototypes
MAX_HOPS = 3  # A relay drops a message that already went through 3 relays

_MESSAGE = "<BBBBh"


def xor_encrypt(data):
    """XOR every byte with KEY. Applying it twice gives back the data."""
    return bytes(b ^ KEY for b in data)


def encode(name, src, dst, seq, hop, value):
    """Return the advertising payload of a message advertised by node name.

    src is the node that created the message: a relay forwards it under its
    own name, but keeps src, so that the others can recognise a duplicate.
    """
    message = struct.pack(
        _MESSAGE, NODES.index(src), NODES.index(dst), seq & 0xFF, hop, value
    )
    man_data = struct.pack("<H", COMPANY_ID) + xor_encrypt(message)
    name = name.encode()
    payload = bytearray()
    payload += bytes((2, 0x01, 0x06))  # Flags: LE General Discoverable
    payload += bytes((len(name) + 1, 0x09)) + name
    payload += bytes((len(man_data) + 1, 0xFF)) + man_data
    return payload


def decode(adv_data):
    """Return (src, dst, seq, hop, value) from an advertising payload, or None."""
    if not adv_data:  # aioble gives None for a result without advertising data
        return None
    i = 0
    while i + 1 < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        if adv_data[i + 1] == 0xFF:
            man_data = bytes(adv_data[i + 2 : i + 1 + length])
            if len(man_data) != 8 or struct.unpack("<H", man_data[:2])[0] != COMPANY_ID:
                return None
            src, dst, seq, hop, value = struct.unpack(_MESSAGE, xor_encrypt(man_data[2:]))
            if src >= len(NODES) or dst >= len(NODES):
                return None
            return NODES[src], NODES[dst], seq, hop, value
        i += 1 + length
    return None


def is_new(last_seq, src, seq):
    """True when seq is newer than the last one seen from src (and records it).

    Sequence numbers wrap at 256: a number up to 127 steps ahead is newer.
    """
    last = last_seq.get(src)
    if last is not None and not 0 < (seq - last) % 256 < 128:
        return False
    last_seq[src] = seq
    return True
