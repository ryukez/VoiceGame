import sys
import os
import time
import numpy as np
import pyaudio
import pygame
import random
import time
import math
from pygame.locals import *
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 512
RANK = 500
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
	f = open("data/noise.txt","w")
	for e in record.data:
		f.write(str(e)+'\n')
	f.close()

if __name__ == '__main__': main()

