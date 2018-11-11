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


# print(find_note(10000, 440))

def peak_print(range, notes):
    """

    :param range: tuple, from where to where are peaks valid
    :param notes: list of tuples, up to threee notes with cents (note, cents)
    :return:
    """


def join_intervals(intervals, base):
    # DODGY SHIT
    out = []
    # for x in intervals:
    #     notes = find_note(x[0], 440)
    #     print(str(x[1]/10)+"-"+ str((x[1]+1)/10) + notes[0]  + str(notes[1]) )

    out = set([x[0] for x in intervals])
    for o in out:
        occurrence = [x[1] for x in intervals if x[0]==o]
        print(occurrence)
        for k, g in groupby(enumerate(occurrence), lambda ix: ix[0] - ix[1]):
            neco = list(map(itemgetter(1), g))
            print(find_note(o, 440), neco[0]/10, (neco[-1]+1)/10)
    # out.append(intervals[0])
    # for i in range(1, len(intervals)):
    #
    #     interval = intervals[i]# zatim od 1 dal
    #     if intervals[i-1][0] == interval[0]:
    #         index = out.index(intervals[i-1])
    #         del out[index]
    #         out.append(interval)
    #     else:
    #         out.append(interval)
    #
    # print(out)




join_intervals([(10000, 0), (10000, 1), (10000, 2), (10000, 3), (10000, 4), (10000, 5), (10000, 6), (10000, 7), (10000, 8), (10000, 9), (10000, 10), (10000, 11), (10000, 12), (10000, 13), (10000, 14), (10000, 15), (10000, 16), (10000, 17), (10000, 18), (10000, 19), (10000, 20), (9998, 20), (10003, 20)]
, 440)

def main():
    base = sys.argv[1]
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

    print(len(range(0, (len(integers)-frame_rate), step)))

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
            left = peaks[index - 1]
            right = peaks[index + 1]
            del peaks[index-1:index+2]
            if maximum != (-1, -1):
                local_out.append((maximum[1],))
        # print(local_out, position)
        # print(position)
        # print()
        for x in local_out:
            out.append(x+(position,))
        position += 1

    print(out)
    join_intervals(out, base)


        # if len(peaks) < 2:
        #     #neco nekam pridat?
        #     print(peaks)
        #     continue
        # for i in range(3):
        #     # co kdyz je kratsi nez 3
        #     maximum = max(peaks, key=lambda item: item[0])
        #     index = peaks.index(maximum)
        #     print(maximum, index)
        #     del peaks[index]
        #     left = peaks[index-1]  # co kdyz je prvni
        #     right = peaks[index+1]  # co kdyz je posledni
        #     print(left, right)
        #     print()
        #     if maximum[1] + 1 == right[1]:
        #         del peaks[index+1]
        #     if maximum[1] - 1 == left[1]:
        #         del peaks[index-1]

    #     mean = np.mean([np.abs(x) for x in fft])
    #     peaks = []
    #
    #     for j in range(len(fft)):
    #         freq = np.abs(fft[j])
    #         if mean*20 <= freq:
    #             peaks.append(j)
    #
    #     if len(peaks) > 0:
    #         mins.append(min(peaks))
    #         maxs.append(max(peaks))
    #
    # wav.close()
    # if len(mins) == 0:
    #     print("no peaks")
    #     return
    # else:
    #     print("low = ", min(mins), " high = ", max(maxs))
    #     return


main()