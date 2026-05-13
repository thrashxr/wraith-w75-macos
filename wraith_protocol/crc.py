"""CRC-16/XMODEM (polynomial 0x1021), pure Python — matches ``crcmod.predefined.mkCrcFun('xmodem')``."""

_POLYNOMIAL = 0x1021


def digest(data: bytes) -> int:
    """Return CRC-16/XMODEM over ``data`` (initial remainder 0, MSB-first)."""
    crc = 0
    for byte in data:
        crc ^= (byte & 0xFF) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ _POLYNOMIAL) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def append_crc(buf: bytearray) -> bytearray:
    """Compute CRC over ``buf[1:]`` (exclude report ID), append big-endian CRC to ``buf``."""
    if len(buf) < 2:
        raise ValueError("buffer must include report id and at least one payload byte")
    c = digest(bytes(buf[1:]))
    buf.append((c >> 8) & 0xFF)
    buf.append(c & 0xFF)
    return buf
