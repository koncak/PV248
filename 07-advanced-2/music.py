import sys
import numpy as np
import wave
import struct
from math import log2, pow


def output(a1, maxs_in_windows):
    started = False
    pitches_in_windows = []
    for i in range(len(maxs_in_windows)):
        clustering_pitches = {}

        for j in range(3):
            if maxs_in_windows[i][j] != 0:
                pitch, tone = frequency_to_pitch(maxs_in_windows[i][j], a1)
                if pitch not in clustering_pitches:
                    clustering_pitches[pitch] = tone
                else:
                    if clustering_pitches[pitch] < tone:
                        clustering_pitches[pitch] = tone

        pitches_in_windows.append(clustering_pitches)

    for i in range(len(maxs_in_windows)):
        if not started:
            print("{0:.2f}".format(0.1 * i), "-", sep='', end='')
            started = True
        else:
            if len(pitches_in_windows[i - 1]) == len(pitches_in_windows[i]):
                contains_all = True
                for k, v in pitches_in_windows[i - 1].items():
                    if not (k in pitches_in_windows[i]):
                        contains_all = False

                if contains_all:
                    for k, v in pitches_in_windows[i - 1].items():
                        if k in pitches_in_windows[i]:
                            pitches_in_windows[i][k] = max(v, pitches_in_windows[i][k])
                else:
                    started = False
                    print("{0:.2f}".format(0.1 * (i + 1)), sep='', end=' ')
                    if len(pitches_in_windows[i - 1]) == 0:
                        print("no peaks")
                    else:
                        for k, v in pitches_in_windows[i - 1].items():
                            if int(v) >= 0:
                                print(k, "+", v, sep='', end=' ')
                            else:
                                print(k, v, sep='', end=' ')
                    print("\n", sep='', end='')

            else:
                started = False
                print("{0:.2f}".format(0.1 * (i + 1)), sep='', end=' ')
                if len(pitches_in_windows[i - 1]) == 0:
                    print("no peaks")
                else:
                    for k, v in pitches_in_windows[i - 1].items():
                        if int(v) >= 0:
                            print(k, "+", v, sep='', end=' ')
                        else:
                            print(k, v, sep='', end=' ')
                print("\n", sep='', end='')

    if started:
        print("{0:.2f}".format(0.1 * (i + 1)), sep='', end=' ')
        if len(pitches_in_windows[i - 1]) == 0:
            print("no peaks")
        else:
            for k, v in pitches_in_windows[i - 1].items():
                print(k, "+", v, sep='', end=' ')
        print("\n", sep='', end='')


def Nmaxelements(list1, n):
    final_list = []

    for i in range(0, n):
        max1 = 0
        index = 0

        for j in range(len(list1)):
            if list1[j] > max1:
                max1 = list1[j]
                index = j

        list1[index] = 0
        final_list.append((max1, index))

    return final_list


def frequency_to_pitch(f, a1):
    pitches = ['c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis', 'a', 'bes', 'b']
    middleC = a1 * pow(2, (-21 / 12)) * 2
    h = 12 * log2(f / middleC) #/ log2(2)

    octave_index = int(h // 12) + 1
    index = int(h % 12)
    cents = int((h % 1) * 100)

    if cents >= 50:
        index += 1
        cents = cents - 100

    if index >= 12:
        index -= 12
        octave_index += 1

    pitch = pitches[index]
    octave_char = "’"
    if octave_index < 0:
        pitch = pitch.capitalize()
        octave_char = ","

    if octave_index < 0:
        octave_index += 1

    pitch = pitch + np.abs(octave_index) * octave_char

    return str(pitch), str(cents)


def main():
    a1 = float(sys.argv[1])
    filename = sys.argv[2]
    wav = wave.open(filename, 'r')

    num_channels = wav.getnchannels()
    frame_rate = wav.getframerate()
    frames = wav.getnframes()
    raw_data = wav.readframes(frames)

    fmt = str(frames*num_channels) + "h"
    integers = struct.unpack(fmt, raw_data)
    integers = np.array(integers)

    if num_channels == 2:
        integers = [(a + b) / 2 for a, b in zip(integers[::2], integers[1::2])]

    step = frame_rate // 10
    maxs_in_windows = []
    for i in range(0, (len(integers)-frame_rate), step):

        fft_data = np.fft.rfft(integers[i:frame_rate+i])

        fft_data = np.abs(fft_data)
        peak = 20 * sum(fft_data) / len(fft_data)

        peaks = [fft_data[i] if fft_data[i] > peak else 0 for i in range(len(fft_data))]

        clusters = []
        for i in range(1, len(peaks)):
            if peaks[i-1] > peaks[i]:
                if len(clusters) > 0:
                    if clusters[-1] == 0:
                        clusters.append(peaks[i-1])
                    else:
                        clusters.append(0)
                else:
                    clusters.append(0)
            else:
                clusters.append(0)

        window_maxs = [x[1] for x in Nmaxelements(clusters, 3)]
        window_maxs.sort()
        maxs_in_windows.append(window_maxs)

    output(a1, maxs_in_windows)

    wav.close()

main()