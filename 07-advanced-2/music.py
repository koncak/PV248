import math
import numpy as np
import sys
import wave
import struct
from itertools import groupby
from operator import itemgetter

names = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Bes', 'B']


def find_note(frequency, base):
    c = base * pow(2, -21 / 12)
    n = 12 * (math.log2(frequency/c))

    octave = int(n // 12)
    pitch = int(n % 12)

    cents, _ = math.modf(n)
    cents = float("{0:.2f}".format(cents))
    cents = int(cents * 100)

    if cents < 0:
        pitch += 1

    if cents <= -50:
        pitch -= 1
        cents += 100

    if cents >= 50:
        pitch += 1
        cents = cents - 100

    if pitch >= 12:
        pitch -= 12
        octave += 1

    out = names[pitch]

    if octave >= 0:
        out = out.lower() + ("’" * octave)

    else:
        octave += 1
        out = out + (',' * -octave)

    return out, cents


def join_intervals(intervals, base):
    unique_peaks = set([x[0] for x in intervals])
    all_peaks = []

    for peak in unique_peaks:
        occurrence = [x[1] for x in intervals if x[0] == peak]

        for k, g in groupby(enumerate(occurrence), lambda ix: ix[0] - ix[1]):
            ranges = list(map(itemgetter(1), g))

            note = find_note(peak, base)
            if note[1] < 0:
                cents = "-"
            else:
                cents = "+"

            note_out = str(note[0] + cents + str(abs(note[1])))
            all_peaks.append((note_out, (ranges[0]/10, (ranges[-1]+1)/10), peak))

    return all_peaks


def main():
    # 0.0 - 0.7 C - 37 C + 16 g + 0
    # 0.0 - 2.3 g + 0 ------ ???
    # 0.7 - 1.1 C - 10 C + 42 g + 0
    # 1.1 - 1.9 C - 37 C + 16 g + 0
    # 1.9 - 2.3 C - 10 C + 42 g + 0

    base = int(sys.argv[1])
    filename = sys.argv[2]

    wav = wave.open(filename, 'r')

    width = wav.getsampwidth()
    frames = wav.getnframes()
    channels = wav.getnchannels()
    samples = frames * channels

    if width == 2:
        fmt = str(samples) + "h"
    else:
        raise ValueError("16 bit formats only.")
        wav.close()
        return -1

    frame_rate = wav.getframerate()
    bytes = wav.readframes(wav.getnframes())
    integers = struct.unpack(fmt, bytes)
    step = frame_rate // 10

    if channels == 2:
        integers = [(a + b) / 2 for a, b in zip(integers[::2], integers[1::2])]

    out = []
    position = 0
    for i in range(0, (len(integers)-frame_rate), step):

        fft = np.fft.rfft(integers[i:frame_rate + i])
        mean = np.mean([np.abs(x) for x in fft])

        peaks = []
        for j in range(len(fft)):
            freq = np.abs(fft[j])
            if mean*20 <= freq:
                peaks.append((freq, j))
            else:
                peaks.append((-1, -1))

        local_out = []
        for _ in range(3):
            maximum = max(peaks, key=lambda item: item[0])

            index = peaks.index(maximum)
            left = index - 1
            right = index + 2
            if index == 0:
                left = index
            if index == len(peaks):
                right = index + 1

            del peaks[left:right]
            if maximum != (-1, -1):
                local_out.append((maximum[1],))

        for x in local_out:
            out.append(x+(position,))
        position += 1

    all_peaks = join_intervals(out, base)
    if len(all_peaks) == 0:
        print("no peaks")
        return

    interval_tuples = list(set([x[1] for x in all_peaks]))
    interval_tuples = sorted(interval_tuples)

    for interval in interval_tuples:
        tones = []
        for peak in all_peaks:
            if peak[1][0] <= interval[0] and peak[1][1] >= interval[1]:
                tones.append((peak[0], peak[2]))

        tones.sort(key=lambda tup: tup[1])
        out = []
        for tone in tones:
            if tone[0] not in [o[0] for o in out]:
                out.append(tone)
        out.sort(key=lambda tup: tup[1])

        print(interval[0], "-", interval[1], end=' ')
        for tone in out:
            print(tone[0], end=' ')
        print()

    wav.close()
    return


main()
