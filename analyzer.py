#coding:utf-8
import sys
import wave
import numpy as np
import scipy.fftpack
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
Range = 10
Thes = Range * 2 / 10
PowerThes = 3
MAX = 10
Part = 0.2
def InputFromFile():
	data = []
	f = open("data/noise2.txt","r")
	for line in f.readlines():
		data.append(eval(line))
	f.close()
	return data

def isTop(data,pos,top):
	greater = 0
	if data[pos] < PowerThes:
		return 0
	for r in range(-Range,Range+1):
		if pos+r >= 0 and pos+r < len(data)/2 and data[pos+r] > data[pos]:
			greater+=1
	return 1 if greater <= Thes else 0

def search(data,pos,top):
	ans = pos
	for r in range(-Range,Range+1):
		if pos+r >= 0 and pos+r < len(data)/2 and data[pos+r] > data[ans]:
			ans = pos+r
	return isTop(data,ans,top)

def subst(list1,list2):
	ret = []
	for i in range(0,len(list1)):
		ret.append(list1[i]-list2[i])
	return ret

def h_analyze(data,pre):
	pos = 0
	for i in range(0,len(data)/2):
		if data[i] > data[pos]:
			pos = i
	top = pos
	if data[top] < PowerThes:
		return pre
	ans = 1
	ansval = 0
	for d in range(1,MAX+1):
		inter = top / d
		if freqList[inter] < 100:
			continue
		pos = inter
		res = 0
		while pos < len(data)/2:
			res += search(data,pos,data[top])
			pos += inter
		if res > ansval:
			ans = d
			ansval = res
	return top / ans

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

#wf = wave.open("data/violin.wav" , "r" )
#fs = wf.getframerate()  # サンプリング周波数
fs = 2048.0
#x = wf.readframes(wf.getnframes())
x = InputFromFile()  # -1 - +1に正規化
print len(x)
x = [e / 32768.0 for e in x]
#wf.close()

fig = plt.figure()
sp1 = fig.add_subplot(211)
sp2 = fig.add_subplot(212)

print len(x)
print fs

start = 0    # サンプリングする開始位置
N = 2048   # FFTのサンプル数
SHIFT = 256  # 窓関数をずらすサンプル数

hammingWindow = np.hamming(N)
freqList = np.fft.fftfreq(N, d=1.0/fs)  # 周波数軸の値を計算
preSpectrum = [0] * N
preHz = 0

def update(idleevent):
    global start
    global preSpectrum
    global preHz
    windowedData = hammingWindow * x[start:start+N]  # 切り出した波形データ（窓関数あり）
    X = np.fft.fft(windowedData)  # FFT
    amplitudeSpectrum = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in X]  # 振幅スペクトル
    preHz=h_analyze(subst(amplitudeSpectrum,preSpectrum),preHz)
#    print freqList[preHz]
    preSpectrum = amplitudeSpectrum
    unit=fs/N
    # 波形を更新
    sp1.cla()  # クリア
    sp1.plot(range(start, start+N), x[start:start+N])
    sp1.axis([start, start+N, -1.0, 1.0])
    sp1.set_xlabel("time [sample]")
    sp1.set_ylabel("amplitude")

    # 振幅スペクトルを描画
    sp2.cla()
    sp2.plot(freqList, amplitudeSpectrum, marker= 'o', linestyle='-')
    sp2.axis([0, 3000, 0, 50])
    sp2.set_xlabel("frequency [Hz]")
    sp2.set_ylabel("amplitude spectrum")

    fig.canvas.draw_idle()
    start += SHIFT  # 窓関数をかける範囲をずらす
    if start + N > len(x):
        sys.exit()

import wx
wx.EVT_IDLE(wx.GetApp(), update)
plt.show()
