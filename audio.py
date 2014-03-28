#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import time
import numpy as np
import pyaudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RANK = 1000
TURN = 10

class Spectrum(object):
	def analyze(self,data):
		rdata = []
		for e in data:
			rdata.append(abs(e))
		rdata.sort()
		return rdata[len(rdata)-RANK]
	def __init__(self):
		self.pa = pyaudio.PyAudio()
		self.cnt = 0
		self.data = []
	def fft(self, samples):
		win = np.hanning(len(samples))
		#フーリエ解析
		res = np.fft.fftshift(np.fft.fft(win*samples))
		freq = np.fft.fftfreq(len(samples), d=self.RATE**-1)
		return zip(freq, 20*np.log10(np.abs(res))) 
	def callback(self, in_data, frame_count, time_info, status):
		self.data.extend(np.frombuffer(''.join(in_data),dtype="int16"))
		self.cnt = (self.cnt + 1) % TURN
		if self.cnt % TURN == TURN - 1:
			print self.analyze(self.data)
			self.data = []
		return (in_data, self.recording)
	def record(self):
		self.recording = pyaudio.paContinue
		stream = self.pa.open(
			format = FORMAT,
			channels = CHANNELS,
			rate = RATE,
			input = True,
			output = False,
			frames_per_buffer = CHUNK,
			stream_callback = self.callback)
		stream.start_stream()
if __name__ == '__main__':
	spe = Spectrum()
	spe.record()
