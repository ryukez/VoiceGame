#!/usr/bin/env python
# encoding: utf-8
import sys
import os
import time
import numpy as np
import pyaudio
import pygame
import random
import time
import math
import traceback
from pygame.locals import *
#-----デバッグ定数-----
Debug = False

#-----システム定数-----
Size = (800,600)
X = Size[0]
Y = Size[1]
PX = 150
MAXWIDTH = 5
MAXJUMP = 1.8
PreSize = 8
Screen = pygame.display.set_mode((Size[0],Size[1]+40))
Clock = pygame.time.Clock()
Scale = 2
EPS = 2
unit = 20

#-----音声処理定数-----
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8192
CHUNK = 1024
FUNIT = 1024
SHIFT = 1024
TURN = 30
Part = 0.2
Sample = 1
Range = 2
Volume = 0.4
tune = {"A": 0,"A#": 1,"B": 2,"C": 3,"C#": 4,"D": 5,"D#": 6,"E": 7,"F": 8,"F#": 9,"G": 10,"G#": 11}

#画像読み込み
title = pygame.transform.scale(pygame.image.load("data/white.jpg").convert(),(Size[0],Size[1]+40))
back = pygame.transform.scale(pygame.image.load("data/white.jpg").convert(),Size)
wall = pygame.transform.scale(pygame.image.load("data/wall.png").convert_alpha(),(unit,unit))
plane = pygame.transform.scale(pygame.image.load("data/plane.png").convert_alpha(),(unit,unit))
menu = pygame.transform.scale(pygame.image.load("data/gameover.png").convert_alpha(),Size)
supporter = pygame.transform.scale(pygame.image.load("data/supporter.png").convert_alpha(),Size)
circle = pygame.transform.scale(pygame.image.load("data/point.png").convert_alpha(),(unit,unit))


#色定義
RED = (255,0,0)
GREEN = (39,203,81)
BLUE = (123,48,255)
WHITE = (255,255,255)
BLACK = (0,0,0)

class Game():
	highscore = 0
	def __init__(self):
		pygame.init()
	
	#-----デバッグ関連-----
		self.dbstr = ""
		self.dbstr2 = ""
		
	#-----システム関連-----
		self.scene = 0
		self.cnt = 0
		self.select = 0
		self.mode = 0
		self.pitch = 0
		self.sfont = pygame.font.SysFont("Comic Sans MS",50)
		self.font = pygame.font.Font("data/MSGOTHIC.TTF",35)
		self.midfont = pygame.font.Font("data/MSGOTHIC.TTF",60)
		self.bigfont = pygame.font.Font("data/MSGOTHIC.TTF",100)
#		self.read_note("data/note.txt")

	#-----音声関連-----
		self.start = 0
		self.pa = pyaudio.PyAudio()
		self.data = []
		self.recording = pyaudio.paContinue

	def play_init(self):
		self.todraw = []
		self.point = []
		self.lyric = []
		self.pos1 = 0
		self.pos2 = 0
		self.pos3 = 0
		self.freq = 5 * unit
		self.x = 0
		self.y = Y/2
		self.a = 0
		self.v = 0
		self.nxt = 0
		self.ypre = Y/2
		self.ynxt = Y/2
		self.preHz = [0] * PreSize
		self.precount = 0
		self.presum = 0
		if self.mode == 0:
			self.read_note("data/note.txt")

#デバッグ用
	def debug(self,string):
		self.dbstr = string

#音声解析部分
	def gcd(self,x,y):
		a = max(x,y)
		b = min(x,y)
		if a % b == 0:
			return b
		else:
			return self.gcd(b,a%b)
	
	def judge(self,data,d):
		if len(data) == 0:
			return False
		for e in data:
			nr = self.near(e,d)
			if nr-e > Range or nr-e < -Range:
				return False
		return True
	
	def near(self,x,y):
		a = int(x/y) * y
		b = a + y
		return a if x-a < b-x else b
	
	def analyze(self,data,fs):
		top = []
		length = int(len(data) * Part)
		for i in range(1,length):
			if data[i] > data[i-1] and data[i] > data[i+1]:
				top.append((data[i],i))
		top.sort()
		top.reverse()
		top = [v for (k,v) in top]
#		N = min(Sample, len(top))
#		print top[0:N],
#		for d in range(length,4,-1):
#			if self.judge(top[0:N],d):
#				return fs/d
		if len(top) > 0:
			return fs / top[0]
		else:
			return 0

	def volume(self,data):
		for d in data:
			if d >= Volume:
				return True
				
	def fft(self,data,fs):
		data = [x / 32768.0 for x in data]
		if not self.volume(data):
			return 0
		X = np.fft.fft(data)
		Power = [c.real ** 2 + c.imag ** 2 for c in X]
		Y = np.fft.ifft(Power)
		Y = [c.real for c in Y]
		return self.analyze(Y,fs)
		
	def callback(self, in_data, frame_count, time_info, status):
		if in_data:
			next = np.frombuffer(''.join(in_data),dtype="int16")
			if self.start+FUNIT >= len(self.data):
				self.data.extend(next)
		return (in_data, self.recording)

#ゲームオーバー処理
	def gameover(self):
		if self.cnt <= 60:
			self.cnt+=1

#毎フレームごとの処理
	def update(self):
	#-------ゲーム画面--------
		if self.scene == 1:
		#当たり判定
			if not self.check():
				self.cnt = 0
				self.scene = 2

		#壁作成部分
			if self.mode == 1:
				self.make_wall()
			while self.pos1 < len(self.todraw) and self.todraw[self.pos1][0] + unit / 2 < self.x:
				self.pos1+=1
			while self.pos2 < len(self.todraw) and self.todraw[self.pos2][0] + unit / 2 < self.x + PX:
				self.pos2+=1
			while self.pos3 < len(self.point) and self.point[self.pos3][0] + unit / 2 < self.x:
				self.pos3+=1

		#音声入力 & 座標計算
			s = 0.0
			n = 0
			while len(self.data) - self.start >= FUNIT:
				f = self.fft(self.data[self.start:self.start+FUNIT],RATE)
				s+=f
				n+=1
				self.start+=SHIFT
			if n > 0:
				ave = s / n
				if ave == 0 or ave > 1000:
					self.a = 0
				else:
					if ave < 55.0:
						ave = 55.0
					print ave
					if self.x < 100 or (float(self.presum) / (PreSize * MAXJUMP) < ave and ave < float(self.presum) * MAXJUMP / PreSize) :
						self.ynxt = Y - math.log(ave/110,2)*Y/2 - 12.5
						if self.ynxt < 0:
							self.ynxt = -100.0
						if self.ynxt > Y:
							self.ynxt = Y + 100.0
						my = (self.ynxt - self.y) / 3
						self.a = 2*(my - self.v*TURN) / (TURN*(TURN+1))
					else:
						self.a = 0
					self.presum -= self.preHz[self.precount]
					self.presum += ave
					self.preHz[self.precount] = ave
					self.precount = (self.precount + 1) % PreSize
#			self.a=0
			self.x+=2
			self.v+=self.a
			self.y+=self.v
#			self.debug(u"あ")

		#ハイスコア更新
			if self.highscore < self.x / 120.0:
				self.highscore = self.x / 120.0

	#-------ゲームオーバー画面--------
		if self.scene == 2:
			self.gameover()
		self.draw()

	#キーボード入力その他
		pressed_keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
			if self.scene == 0:
				if event.type == KEYDOWN and event.key == K_UP:
					self.select = (self.select + 2) % 3
				if event.type == KEYDOWN and event.key == K_DOWN:
					self.select = (self.select + 1) % 3
				if self.select == 0:
					if event.type == KEYDOWN and event.key == K_RETURN:
						self.scene = 1
						self.select = 0
						self.play_init()
				if self.select == 1:
					if event.type == KEYDOWN and event.key == K_LEFT :
						self.mode = (self.mode + 1) % 2
					if event.type == KEYDOWN and event.key == K_RIGHT:
						self.mode = (self.mode + 1) % 2
				if self.select == 2:
					if event.type == KEYDOWN and event.key == K_LEFT:
						self.pitch = (self.pitch + 1) % 2
					if event.type == KEYDOWN and event.key == K_RIGHT:
						self.pitch = (self.pitch + 1) % 2
			if self.scene == 2 and self.cnt > 60:
				if event.type == KEYDOWN and event.key == K_RIGHT:
					self.select = (self.select + 1) % 2
				if event.type == KEYDOWN and event.key == K_LEFT:
					self.select = (self.select + 1) % 2
				if event.type == KEYDOWN and event.key == K_RETURN:
					if self.select == 0:
						self.scene = 1
						self.play_init()
					if self.select == 1:
						self.__init__()

#壁作成関数

	def read_note(self,filename):
		f = open(filename,"r")
		for line in f.readlines():
			data = line.split(" ")
			t = tune[data[1]] + int(data[2]) * 12
			if t >= 12 and t <= 36:
				center = int(((t-12)/24.0*Y+12.5)/unit)
				self.lyric.append(unicode(data[3][:len(data[3])-1],"UTF-8"))
				self.point.append((self.nxt+X,Y-((t-12)/24.0*Y+12.5)))
				self.todraw.append((self.nxt+X,Y-(center-3)*unit,Y))
				self.todraw.append((self.nxt+X,0,Y-(center+4)*unit))
			self.nxt += self.freq*int(data[0])
			
	def make_wall(self):
		if self.x == self.nxt and not Debug :
			a=random.randint(0,Y/unit-MAXWIDTH)
#			b=random.randint(MAXWIDTH,Y/unit-a)
			self.point.append((self.x+X,(a+7/2.0)*unit))
			self.todraw.append((self.x+X,0,a*unit))
			self.todraw.append((self.x+X,(a+7)*unit,Y))
			self.nxt += self.freq

#当たり判定関数
	def check(self):
		if self.y < -unit or self.y > Y:
			return False
		for p in range(self.pos2,len(self.todraw)-1):
			if self.todraw[p][0] + unit / 2 > self.x+PX+unit:
				break
			if self.todraw[p][1] - unit + EPS < self.y and self.y < self.todraw[p][2] - EPS:
				return False
		return True

#描画系関数
	def draw(self):
	#-------タイトル画面--------
		if self.scene == 0:
			Screen.blit(title,(0,0))
			Screen.blit(self.sfont.render("Play",True,BLACK),(300,270))
			if self.mode == 0:
				Screen.blit(self.sfont.render("Song",True,BLACK),(300,350))
			if self.mode == 1:
				Screen.blit(self.sfont.render("Random",True,BLACK),(300,350))
			if self.pitch == 0:
				Screen.blit(self.sfont.render(u"±0",True,BLACK),(300,430))
			if self.pitch == 1:
				Screen.blit(self.sfont.render("+1",True,BLACK),(300,430))
			Screen.blit(plane,(200,300+self.select*80))
	#-------ゲーム画面--------
		if self.scene == 1 or self.scene == 2:
			Screen.blit(back,(0,0))
			Screen.blit(self.font.render(self.dbstr,True,BLACK),(0,0))
#			Screen.blit(self.font.render(str(self.x),True,BLACK),(0,30))
#			Screen.blit(self.font.render(str(self.highscore),True,BLACK),(0,60))
			pygame.draw.rect(Screen, (0,0,0), Rect(0,600,800,640))
			Screen.blit(supporter,(PX+150,-75))
			Screen.blit(supporter,(PX+150,525))
#			Screen.blit(supporter,(PX-600,-75))
#			Screen.blit(supporter,(PX-600,525))
			for i in range(self.pos3,len(self.point)):
				if self.point[i][0] > self.x + X:
					break		
				Screen.blit(circle,(self.point[i][0]-self.x,self.point[i][1]-unit/2))
				if self.mode == 0:
					Screen.blit(self.font.render(self.lyric[i],True,WHITE),(self.point[i][0]-self.x-5,600))
			for d in self.todraw[self.pos1:]:
				x = d[0]
				a = d[1]
				b = d[2]
				for i in range(a,b,unit):
					Screen.blit(wall,(x-self.x,i))
			Screen.blit(plane,(PX,self.y))
	#-------ゲームオーバー画面--------
		if self.scene == 2:
			if self.cnt <= 60:
				Screen.blit(menu,(0,-Y+Y/60*self.cnt))
			else:
				Screen.blit(menu,(0,0))
				Screen.blit(self.bigfont.render(str(round(self.x/120.0,2))+"s",True,WHITE),(self.pos(self.bigfont.size(str(round(self.x/120.0,2))+"s")),100))
				Screen.blit(self.midfont.render("Continue?",True,WHITE),(self.pos(self.midfont.size("Continue?")),300))
				Screen.blit(self.midfont.render(">",True,WHITE),(150+self.select*300,400))
				Screen.blit(self.midfont.render("YES",True,WHITE),(200,400))
				Screen.blit(self.midfont.render("NO",True,WHITE),(500,400))
		pygame.display.update()
	def pos(self,size):
		return (X - size[0]) / 2

def main():
	try:
	#初期化
		game = Game()
		game.stream = game.pa.open(
			format = FORMAT,
			channels = CHANNELS,
			rate = RATE,
			input = True,
			output = False,
			frames_per_buffer = CHUNK,
			stream_callback = game.callback)
		game.stream.start_stream()

	#ファイル読み込み
		f = open("data/score.txt","r")
		game.highscore = float(f.readline())
		f.close()
	#メインループ
		while True:
			Clock.tick(60)
			game.update()

	except:
		print traceback.format_exc()
		
	finally:
		f = open("data/score.txt","w")
		f.write(str(game.highscore))
		f.close()

if __name__ == '__main__': main()
