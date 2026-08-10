"""Erzeugt die PWA-App-Icons (reine Standardbibliothek, kein Pillow noetig).

Motiv: Aufhaengepunkt, Pendelfaden und Scheibe.

Aufruf einmalig:  python _make_icons.py
"""

import math
import struct
import zlib

BG = (11, 15, 20)
TEAL = (79, 209, 197)
TEAL_D = (18, 122, 114)
DIM = (34, 48, 63)


def mix(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


def pixel(fx, fy):
    """fx, fy in [0,1) - liefert RGB."""
    x = fx - 0.5
    y = fy - 0.5

    # Aufhaengepunkt oben
    px, py = 0.0, -0.30
    if math.hypot(x - px, y - py) < 0.035:
        return mix(BG, TEAL, 0.55)

    # Scheibe unten rechts (ausgelenktes Pendel)
    bx, by = 0.17, 0.20
    r = math.hypot(x - bx, y - by)
    if r < 0.235:
        # weicher Verlauf mit Glanzpunkt oben links
        t = math.hypot(x - bx + 0.09, y - by + 0.09) / 0.42
        return mix(TEAL, TEAL_D, min(1.0, max(0.0, t)))

    # Faden vom Aufhaengepunkt zur Scheibe
    dx, dy = bx - px, by - py
    ll = dx * dx + dy * dy
    s = ((x - px) * dx + (y - py) * dy) / ll
    if 0.0 <= s <= 1.0:
        d = math.hypot(x - (px + s * dx), y - (py + s * dy))
        if d < 0.012:
            return mix(BG, TEAL, 0.45)

    # Schwingungsbogen (gestrichelt)
    rr = math.hypot(x - px, y - py)
    if 0.505 < rr < 0.53:
        ang = math.atan2(x - px, y - py)
        if (int(abs(ang) / 0.13) % 2) == 0 and abs(ang) < 1.15:
            return DIM

    return BG


def write_png(path, size):
    rows = bytearray()
    for y in range(size):
        rows.append(0)  # Filter-Byte
        for x in range(size):
            r, g, b = pixel((x + 0.5) / size, (y + 0.5) / size)
            rows += bytes((r, g, b, 255))

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(bytes(rows), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as fh:
        fh.write(png)
    print('erzeugt:', path)


if __name__ == '__main__':
    write_png('icon-180.png', 180)
    write_png('icon-192.png', 192)
    write_png('icon-512.png', 512)
