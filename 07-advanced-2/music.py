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
    cents = int(cents * 100)
    #print(cents)

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

    #print(pitch, octave)
    out = names[pitch]

    if octave >= 0:
        out = out.lower() + ("’" * octave)

    else:
        octave += 1
        out = out + (',' * -octave)

    # +1 / -1 cent, resit?
    return out, cents


#print(find_note(115, 440))

def peak_print(range, notes):
    """

    :param range: tuple, from where to where are peaks valid
    :param notes: list of tuples, up to threee notes with cents (note, cents)
    :return:
    """


def join_intervals(intervals, base):
    # DODGY SHIT
    # for x in intervals:
    #     notes = find_note(x[0], 440)
    #     print(str(x[1]/10)+"-"+ str((x[1]+1)/10) + notes[0]  + str(notes[1]) )

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
            all_peaks.append((note_out, (ranges[0]/10, (ranges[-1]+1)/10)))
    return all_peaks


# join_intervals([(10000, 0), (10000, 1), (10000, 2), (10000, 3), (10000, 4), (10000, 5), (10000, 6), (10000, 7), (10000, 8), (10000, 9), (10000, 10), (10000, 11), (10000, 12), (10000, 13), (10000, 14), (10000, 15), (10000, 16), (10000, 17), (10000, 18), (10000, 19), (10000, 20), (9998, 20), (10003, 20)]
# , 440)


def main():
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
            #doresit, kdyz je maximum na prvnim indexu a na poslednim

            index = peaks.index(maximum)
            # left = peaks[index - 1]
            # right = peaks[index + 1]
            del peaks[index-1:index+2]
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
    #interval_tuples.sort(key=lambda tup: tup[0])
    interval_tuples = sorted(interval_tuples)

    for interval in interval_tuples:
        tones = [x[0] for x in all_peaks if interval in x]
        print(interval[0], "-", interval[1], end=' ')
        for tone in tones:
            print(tone, end=' ')
        print()

    wav.close()
    return


main()
