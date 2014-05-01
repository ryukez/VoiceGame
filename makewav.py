#coding: utf-8
import wave
import struct
import numpy as np
import pyaudio
from pylab import *
Part = 0.2

def Init(fs,length):
	return [0]*(length*fs)

def AddSineWave (data, A, f0, fs, s = 0, start = 0.0, end = 600.0):
	# 振幅A,周波数f0,サンプリング数fs,基本位置sのサイン波を[start,end)に加算
	length = len(data)
	start = int(start*fs)
	end = min(int(end*fs),length)
	for n in range(start, end):
		y = A * np.sin(2 * np.pi * f0 * (n - s) / fs) + data[n]
		if y > 32767:  y = 32767
		if y < -32767: y = -32767
		data[n] = y
	return data

def Convert(data):
	data = struct.pack("h" * len(data), *data)
	return data

def RConvert(buf):
	data = frombuffer(buf,dtype="int16")
	return data

def Play (data, fs, bit = 16):
	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paInt16,
					channels=1,
					rate=int(fs),
					output= True)
	chunk = 1024
	sp = 0
	buffer = data[sp:sp+chunk]
	while buffer != '':
		stream.write(buffer)
		sp = sp + chunk
		buffer = data[sp:sp+chunk]
	stream.close()
	p.terminate()

def Save(filename,data,fs,bit = 16):
	data = Convert(data)
	f = wave.open(filename,"w")
	f.setparams((1,bit/8,fs,len(data),"NONE","not compressed"))
	f.writeframes(data)
	f.close()

def Load(filename):
	f = wave.open(filename,"r")
	buf = f.readframes(f.getnframes())
	return RConvert(buf)
	
def Show(data):
	plot(data)
	show()

def Analyze(data):
	inter = 0
	value = 0
	length = int(len(data) * Part)
	for i in range(2,length):
		pos = i
		res = 0
		cnt = 0
		while pos < length:
			res += data[pos]
			cnt += 1
			pos += i
		if float(res) / cnt > value:
			inter = i
			value = float(res) / cnt
	return inter

def Fft(data):
	data = [x / 32768.0 for x in data]
	X = np.fft.fft(data)
	Power = [c.real ** 2 + c.imag ** 2 for c in X]
	Y = np.fft.ifft(Power)
	Y = [c.real for c in Y]
	plot(Y[0:100])
	show()
	return Analyze(Y)

if __name__ == "__main__" :
#	freqList = [262, 294, 330, 349, 392, 440, 494, 523]  # ドレミファソラシド
#	data = Init(8000,2)
#	data = AddSineWave(data, 1000, 30, 8000.0)
#	data = AddSineWave(data, 2000, 50, 8000.0, 30)
#	data = AddSineWave(data, 1500, 80, 8000.0)
#	Save("data/sound.wav",data,8000)
	data = Load("data/voice.wav")
	start = 12000
	N = 1000
	fs = 8000
#	window = np.hamming(N)
#	X = np.fft.fft(window*data[start:start+N])
#	window = np.hamming(N)
	freqList = np.fft.fftfreq(N, d=1.0/fs)
#	Y = [c.real ** 2 + c.imag ** 2 for c in Y]
#	subplot(312)
#	plot(freqList[0:1000],PowerSpectrum[0:1000])
#	axis([0,fs/2,0,100])
	print Fft(data[start:start+N])
