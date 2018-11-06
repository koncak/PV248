import sys
import wave
import struct
import numpy as np


def main():
    filename = sys.argv[1]

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

    if channels == 2:
        integers = [(a + b) / 2 for a, b in zip(integers[::2], integers[1::2])]

    windows = int(len(integers) / frame_rate)

    mins = []
    maxs = []

    for i in range(windows):
        fft = np.fft.rfft(integers[i * frame_rate:i * frame_rate + frame_rate])
        mean = np.mean([np.abs(x) for x in fft])
        peaks = []

        for j in range(len(fft)):
            freq = np.abs(fft[j])
            if mean*20 <= freq:
                peaks.append(j)

        if len(peaks) > 0:
            mins.append(min(peaks))
            maxs.append(max(peaks))

    wav.close()
    if len(mins) == 0:
        print("no peaks")
        return
    else:
        print("low = ", min(mins), " high = ", max(maxs))
        return


main()
