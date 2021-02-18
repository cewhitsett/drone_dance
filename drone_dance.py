""" 
  Code adapted from https://github.com/aubio/aubio/blob/master/python/demos/demo_tapthebeat.py

  To run,

  python drone_dance.py <filename.wav>

"""

import sys
import time
import pyaudio
import aubio
import numpy as np

from tello import Tello

win_s = 1024                # fft size
hop_s = win_s // 2          # hop size

# parse command line arguments
if len(sys.argv) < 2:
    print("Usage: %s <filename> [samplerate]" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]

samplerate = 0
if len( sys.argv ) > 2: samplerate = int(sys.argv[2])


drone = Tello()
drone.send_command("command")
drone.send_command("takeoff")
# create aubio source
a_source = aubio.source(filename, samplerate, hop_s)
samplerate = a_source.samplerate

# create aubio tempo detection
a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)

# create a simple click sound
click = 0.7 * np.sin(2. * np.pi * np.arange(hop_s) / hop_s * samplerate / 3000.)

WAIT_LENGTH = 6

waited = 0
index = 0
direct = "cw"

commands = [
  "forward 30"
  "cw 90",
  "ccw 90",
  "ccw 90",
  "cw 90",
  "flip r",
  "flip l",
  "land"
]
# pyaudio callback
def pyaudio_callback(_in_data, _frame_count, _time_info, _status):
    global waited, direct, index
    samples, read = a_source()
    is_beat = a_tempo(samples)
    if is_beat:
        # Uncomment the next line to hear the click on suspected beats
        # samples += click 
        waited += 1
        if waited == WAIT_LENGTH:
          waited = 0
          if commands[index] != "skip":
            drone.send_command(commands[index])
          index = (index + 1) % len(commands)

    audiobuf = samples.tobytes()
    if read < hop_s:
        return (audiobuf, pyaudio.paComplete)
    return (audiobuf, pyaudio.paContinue)

# create pyaudio stream with frames_per_buffer=hop_s and format=paFloat32
p = pyaudio.PyAudio()
pyaudio_format = pyaudio.paFloat32
frames_per_buffer = hop_s
n_channels = 1
stream = p.open(format=pyaudio_format, channels=n_channels, rate=samplerate,
        output=True, frames_per_buffer=frames_per_buffer,
        stream_callback=pyaudio_callback)

# start pyaudio stream
stream.start_stream()

try:
  # wait for stream to finish
  while stream.is_active():
      time.sleep(0.1)
except:
  # Really only should throw on someone suffocated the program.
  drone.send_command("land")

drone.send_command("land")
# stop pyaudio stream
stream.stop_stream()
stream.close()
# close pyaudio
p.terminate()
