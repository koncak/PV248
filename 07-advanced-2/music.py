import math
import numpy as np

names = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Bes', 'B']


def find_note(frequency, base):
    c = base * pow(2, -21 / 12)
    n = 12 * (math.log2(frequency/c))

    octave = int(n // 12)
    pitch = int(n % 12)

    cents, _ = math.modf(n)
    cents = int(cents * 100)
    print(cents)

    # cents = int(100 * (n % 1))
    if cents < 0:
        pitch += 1

    if cents <= -50:
        pitch -= 1
        cents += 100

    if cents >= 50:
        pitch += 1
        cents = 100 - cents

    if pitch >= 12:
        pitch -= 12
        octave += 1

    print(pitch, octave)
    out = names[pitch]

    if octave >= 0:
        out = out.lower() + ("’" * octave)

    else:
        octave += 1
        out = out + (',' * -octave)

    return out, cents


def peak_print(range, notes):
    """

    :param range: tuple, from where to where are peaks valid
    :param notes: list of tuples, up to threee notes with cents (note, cents)
    :return:
    """
