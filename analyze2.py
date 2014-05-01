#coding:utf-8
import sys
import wave
import numpy as np
import scipy.fftpack
import matplotlib
matplotlib.use('WXAgg')
from pylab import *
import matplotlib.pyplot as plt
Part = 0.5
Thes = 1.5
Sample = 5
Range = 2

def gcd(x,y):
	a = max(x,y)
	b = min(x,y)
	if a % b == 0:
		return b
	else:
		return gcd(b,a%b)

def check(data,d):
	if len(data) == 0:
		return False
	for e in data:
		nr = near(e,d)
		if nr-e > Range or nr-e < -Range:
			return False
	return True

def near(x,y):
	a = int(x/y) * y
	b = a + y
	return a if x-a < b-x else b

def analyze(data,fs):
	top = []
	length = int(len(data) * Part)
	for i in range(1,length):
		if data[i] > data[i-1] and data[i] > data[i+1]:
			top.append((data[i],i))
	top.sort()
	top.reverse()
	top = [v for (k,v) in top]
	N = min(Sample, len(top))
	print top[0:N],
	for d in range(length,4,-1):
		if check(top[0:N],d):
			return d
	return 0

def Fft(data,fs):
	data = [x / 32768.0 for x in data]
	X = np.fft.fft(data)
	Power = [c.real ** 2 + c.imag ** 2 for c in X]
	Y = np.fft.ifft(Power)
	Y = [c.real for c in Y]
	print analyze(Y,fs)
	return Y

wf = wave.open("data/voice.wav" , "r" )
fs = wf.getframerate()  # サンプリング周波数
x = wf.readframes(wf.getnframes())
x = frombuffer(x,dtype="int16")
x = [e / 32768.0 for e in x]
wf.close()

fig = plt.figure()
sp1 = fig.add_subplot(211)
sp2 = fig.add_subplot(212)

print len(x)
print fs

start = 0    # サンプリングする開始位置
N = 1000   # FFTのサンプル数
SHIFT = 1000  # 窓関数をずらすサンプル数

def update(idleevent):
    global start
    sp1.cla()  # クリア
    sp1.plot(range(start, start+N), x[start:start+N])
    sp1.axis([start, start+N, -1.0,1.0])
    sp1.set_xlabel("time [sample]")
    sp1.set_ylabel("Wave")

    sp2.cla()
    sp2.plot(Fft(x[start:start+N],8000)[0:400])
    sp2.set_xlabel("time [sample]")
    sp2.set_ylabel("Self Relation")

    fig.canvas.draw_idle()
    start += SHIFT  # 窓関数をかける範囲をずらす
    if start + N > len(x):
        sys.exit()

import wx
wx.EVT_IDLE(wx.GetApp(), update)
plt.show()
