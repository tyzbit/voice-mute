#!/usr/bin/env python
## Need to run this first: pactl load-module module-pipe-source source_name=virtmic

import webrtcvad, alsaaudio, time, audioop, sys, os, time

sample_rate = 16000
frame_duration = 10
period_size = 160

# Open the device in nonblocking capture mode. The last argument could
# just as well have been zero for blocking mode. Then we could have
# left out the sleep call in the bottom of the loop
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)

# Set attributes: Mono, 16000 Hz, 16 bit little endian samples
inp.setchannels(1)
inp.setrate(sample_rate)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# The period size controls the internal number of frames per period.
# The significance of this parameter is documented in the ALSA api.
# For our purposes, it is suficcient to know that reads from the device
# will return this many frames. Each frame being 2 bytes long.
# This means that the reads below will return either 320 bytes of data
# or 0 bytes of data. The latter is possible because we are in nonblocking
# mode.
inp.setperiodsize(period_size)

def main(args):
    data_samples = []
    moving_window = int(args[1])
    vad = webrtcvad.Vad(int(args[0]))
    while True:
        # Read data from device
        l,data = inp.read()
        if l:
            padded = data.ljust(period_size * 2, '\0')
            is_speech = vad.is_speech(padded, sample_rate)
            if is_speech:
                if len(data_samples) >= moving_window:
                    data_samples.pop(0)
                data_samples.append(1)
            else:
                if len(data_samples) >= moving_window:
                    data_samples.pop(0)
                data_samples.append(0)
            moving_average = sum(data_samples) / float(len(data_samples))
            print 'Moving Average: %s' % moving_average
        time.sleep(.001)

if __name__ == '__main__':
    main(sys.argv[1:])
