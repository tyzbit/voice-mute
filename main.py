#!/usr/bin/env python
## Need to run this first: pactl load-module module-pipe-source source_name=virtmic

from __future__ import print_function
import webrtcvad, alsaaudio, time, audioop, sys, os, time, getopt

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


def main():
    aggressiveness = None
    buffer = None
    duration = None
    helptext = 'Usage: main.py -[-a]ggressiveness (1-3) -[-b]uffer (1-100)-[-d]uration (1-3) -[-m]ute'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ha:mb:d:",["aggressiveness=","buffer=","duration="])
    except getopt.GetoptError:
        print(helptext)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helptext)
            sys.exit()
        elif opt in ("-a", "--aggressiveness"):
            aggressiveness = int(arg)
        elif opt in ("-b", "--buffer"):
            buffer = int(arg)
        elif opt in ("-d", "--duration"):
            duration = int(arg)
        elif opt in ("-m", "--mute"):
            mute = True
    if (aggressiveness is None) or (buffer is None) or (duration is None):
        print('You must specify aggressiveness, buffer and duration')
        sys.exit(2)
    data_samples = []
    sample_rate = 16000
    period_size = (sample_rate / 100 * duration)

    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)

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

    outp = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,alsaaudio.PCM_NORMAL)

    # Set attributes: Mono, 16000 Hz, 16 bit little endian samples
    outp.setchannels(1)
    outp.setrate(sample_rate)
    outp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.
    # For our purposes, it is suficcient to know that reads from the device
    # will return this many frames. Each frame being 2 bytes long.
    # This means that the reads below will return either 320 bytes of data
    # or 0 bytes of data. The latter is possible because we are in nonblocking
    # mode.
    outp.setperiodsize(period_size)
    vad = webrtcvad.Vad(aggressiveness)

    status = '        '
    while True:
        # Read data from device
        l,data = inp.read()
        if l:
            #padded = data.ljust(period_size * 2, '\0')
            is_speech = vad.is_speech(data, sample_rate)
            if is_speech:
                if len(data_samples) >= buffer:
                    data_samples.pop(0)
                data_samples.append(1)
                status = 'Speaking'
            else:
                if len(data_samples) >= buffer:
                    data_samples.pop(0)
                data_samples.append(0)
                status = '        '
            moving_average = sum(data_samples) / float(len(data_samples))
            progress(moving_average * 100, 100, status)
            if moving_average > .8:
                ## Set the microphone to full volume
                # outp.write(data)
                pass
            else:
                ## Set the microphone to low/no volume
                # outp.write(b'\x00\x00' * period_size)
                pass
            time.sleep(duration * .01)

if __name__ == '__main__':
    main()
