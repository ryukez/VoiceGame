#coding:utf-8
import sys
import wave
import numpy as np
import scipy.fftpack
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

wf = wave.open("data/violin.wav" , "r" )
fs = wf.getframerate()  # サンプリング周波数
x = wf.readframes(wf.getnframes())
x = np.frombuffer(x, dtype= "int16") / 32768.0  # -1 - +1に正規化
wf.close()

fig = plt.figure()
sp1 = fig.add_subplot(211)
sp2 = fig.add_subplot(212)

print len(x)
print fs

start = 0    # サンプリングする開始位置
N = 8192   # FFTのサンプル数
SHIFT = 2048  # 窓関数をずらすサンプル数

hammingWindow = np.hamming(N)
freqList = np.fft.fftfreq(N, d=1.0/fs)  # 周波数軸の値を計算

def update(idleevent):
    global start

    windowedData = hammingWindow * x[start:start+N]  # 切り出した波形データ（窓関数あり）
    X = np.fft.fft(windowedData)  # FFT
    amplitudeSpectrum = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in X]  # 振幅スペクトル
    unit=fs/N
    s=0
    p=0
    while p*unit<1000:
        s+=amplitudeSpectrum[p]
        p+=1
    p=0
    average=0
    while p*unit<1000:
        average+=p*unit*(amplitudeSpectrum[p]/s)
        p+=1
    print average
    # 波形を更新
    sp1.cla()  # クリア
    sp1.plot(range(start, start+N), x[start:start+N])
    sp1.axis([start, start+N, -1.0, 1.0])
    sp1.set_xlabel("time [sample]")
    sp1.set_ylabel("amplitude")

    # 振幅スペクトルを描画
    sp2.cla()
    sp2.plot(freqList, amplitudeSpectrum, marker= 'o', linestyle='-')
    sp2.axis([0, 500, 0, 100])
    sp2.set_xlabel("frequency [Hz]")
    sp2.set_ylabel("amplitude spectrum")

    fig.canvas.draw_idle()
    start += SHIFT  # 窓関数をかける範囲をずらす
    if start + N > len(x):
        sys.exit()

import wx
wx.EVT_IDLE(wx.GetApp(), update)
plt.show()
