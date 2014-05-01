import sys
import os
import time
import numpy as np
import pyaudio
import struct
import pygame
import random
import time
import math
import wave
from pygame.locals import *
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 8000
RANK = 100
TURN = 5

class Record():
	def __init__(self):
		self.data = []
		self.cnt = 0
	def callback(self,in_data, frame_count, time_info, status):
		self.data.extend(np.frombuffer(''.join(in_data),dtype="int16"))
		self.cnt+=1
		if self.cnt == TURN:
			return (in_data, pyaudio.paComplete)
		else:
			return (in_data, pyaudio.paContinue)

def main():
	record=Record()
	pa=pyaudio.PyAudio()
	stream = pa.open(
		format = FORMAT,
		channels = CHANNELS,
		rate = RATE,
		input = True,
		output = False,
		frames_per_buffer = CHUNK,
		stream_callback = record.callback)
	stream.start_stream()
	while True:
		if record.cnt == TURN:
			break
	buf = struct.pack("h" * len(record.data),*record.data)
	f = wave.open("data/voice.wav","w")
	f.setparams((1,2,RATE,len(buf),"NONE","not compressed"))
	f.writeframes(buf)
	f.close()

if __name__ == '__main__': main()

