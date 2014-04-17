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
from pygame.locals import *
Size = (800,600)
X = Size[0]
Y = Size[1]
K = 15.0
PX = 200
Range = 100
MAXWIDTH = 5
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8192
CHUNK = 2048
SHIFT = 512
RANK = 5
TURN = 5
Screen = pygame.display.set_mode(Size)
Clock = pygame.time.Clock()
Scale = 2
EPS = 5
unit = 20
back = pygame.transform.scale(pygame.image.load("data/back.jpg").convert(),Size)
wall = pygame.transform.scale(pygame.image.load("data/wall.jpg").convert(),(unit,unit))
plane = pygame.transform.scale(pygame.image.load("data/plane.png").convert_alpha(),(unit,unit))
menu = pygame.transform.scale(pygame.image.load("data/gameover.png").convert_alpha(),Size)
RED = (255,0,0)
GREEN = (39,203,81)
BLUE = (123,48,255)
WHITE = (255,255,255)
BLACK = (0,0,0)

class Game():
	highscore = 0
	noise = []
	def __init__(self):
		pygame.init()
		self.todraw = []
		self.pos1 = 0
		self.pos2 = 0
		self.x = 0
		self.y = Y/2
		self.a = 0
		self.v = 0
		self.freq = 10 * unit
		self.nxt = 0
		self.ypre = Y/2
		self.ynxt = Y/2
		self.dbstr = ""
		self.dbstr2 = ""
		self.start = 0
		self.font = pygame.font.Font(None,35)
		self.midfont = pygame.font.Font(None,60)
		self.bigfont = pygame.font.Font(None,100)
		self.pa = pyaudio.PyAudio()
		self.data = []
		self.recording = pyaudio.paContinue
		self.scene = 1
		self.cnt = 0
		self.select = 0
		self.freqList = []
#音声解析部分
	def limit(self,x,a,b):
		if x<a: return a
		elif x<=b: return x
		else: return b
	def evaluate(self,val):
		p = float(val) / 1000 - 20
		if p == 0:
			return 0
		else:
			return - (p / abs(p)) * math.log(abs(p)**2,2) / 100;
	def analyze(self,data):
		rdata = []
		for e in data:
			rdata.append(abs(e))
		rdata.sort()
		return self.evaluate(rdata[len(rdata)-len(rdata)/RANK])
	def s_analyze(self,data):
		rdata = []
		for e in data:
			rdata.append(abs(e))
		rdata.sort()
		return rdata[len(rdata)-RANK]
	def h_analyze(self,data):
		pos = 0
		for i in range(0,len(data)):
			if data[i] > data[pos]:
				pos = i
			if self.freqList[i] > 3000:
				break
		return pos
	def fft(self, data):
#		for i in range(0,len(data)):
#			data[i]-=self.noise[i]
		data = [c/32768.0 for c in data]
		window = np.hamming(len(data))
		self.freqList = np.fft.fftfreq(len(data),d=1.0/RATE)
		result=np.fft.fft(window*data)
		unit=RATE/len(data)
		result=[np.sqrt(c.real**2 + c.imag**2) for c in result]
		h = self.h_analyze(result)
		return self.freqList[h]
#		print self.h_analyze(result) / self.s_analyze(data)
	def callback(self, in_data, frame_count, time_info, status):
		next = np.frombuffer(''.join(in_data),dtype="int16")
		if self.start+CHUNK >= len(self.data):
			self.data.extend(next)
		return (in_data, self.recording)
	def debug(self,string):
		self.dbstr = string
	def gameover(self):
		if self.cnt <= 60:
			self.cnt+=1
	def update(self):
		if self.scene == 1:
			if not self.check():
				self.cnt = 0
				self.scene = 2
			self.make_wall()
			while self.pos1 < len(self.todraw) and self.todraw[self.pos1][0] + unit < self.x:
				self.pos1+=1
			while self.pos2 < len(self.todraw) and self.todraw[self.pos2][0] + unit < self.x + PX:
				self.pos2+=1
			while len(self.data) - self.start >= CHUNK:
#				print self.fft(self.data[self.start:self.start+CHUNK])
				if len(self.data) - (self.start+SHIFT) >= CHUNK:
					self.start+=SHIFT
				else:
					break
			if len(self.data) > 0:
				self.a = self.analyze(self.data[self.start:]) / 5
		#		self.ynxt = float(self.s_analyze(self.data[self.start-SHIFT:])-(1<<14)) / (1<<15) * Y * Scale
		#		self.ynxt = self.limit(self.ynxt,self.ypre - Range,self.ypre + Range)
		#		self.debug(str(self.ynxt))
			self.x+=1
			self.v+=self.a
			self.y+=self.v
			self.debug(str(self.a))
			if self.highscore < self.x:
				self.highscore = self.x
		if self.scene == 2:
			self.gameover()
		self.draw()
		pressed_keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()	
			if self.scene == 2 and self.cnt > 60:
				if event.type == KEYDOWN and event.key == K_RIGHT:
					self.select = (self.select + 1) % 2
				if event.type == KEYDOWN and event.key == K_LEFT:
					self.select = (self.select + 1) % 2
				if event.type == KEYDOWN and event.key == K_RETURN:
					self.__init__()
	def make_wall(self):
		if self.x == self.nxt:
#			if random.randint(0,4)<=3:
			a=random.randint(0,Y/unit-MAXWIDTH)
			b=random.randint(MAXWIDTH,Y/unit-a)
			self.todraw.append((self.x+X,0,a*unit))
			self.todraw.append((self.x+X,(a+b)*unit,Y))
			self.nxt += self.freq
	def check(self):
		if self.y < -unit or self.y > Y:
			return False
		for p in range(self.pos2,len(self.todraw)-1):
			if self.todraw[p][0] > self.x+PX+unit:
				break
			if self.todraw[p][1] - unit + EPS < self.y and self.y < self.todraw[p][2] - EPS:
				return False
		return True
	def pos(self,size):
		return (X - size[0]) / 2
	def draw(self):
		if self.scene == 1 or self.scene == 2:
			Screen.blit(back,(0,0))
			Screen.blit(plane,(PX,self.y))
			Screen.blit(self.font.render(self.dbstr,True,BLACK),(0,0))
			Screen.blit(self.font.render(str(self.x),True,BLACK),(0,30))
			Screen.blit(self.font.render(str(self.highscore),True,BLACK),(0,60))
			for d in self.todraw[self.pos1:]:
				x = d[0]
				a = d[1]
				b = d[2]
				for i in range(a,b,unit):
					Screen.blit(wall,(x-self.x,i))
		if self.scene == 2:
			if self.cnt <= 60:
				Screen.blit(menu,(0,-Y+Y/60*self.cnt))
			else:
				Screen.blit(menu,(0,0))
				Screen.blit(self.bigfont.render(str(self.x)+"m",True,WHITE),(self.pos(self.bigfont.size(str(self.x)+"m")),100))
				Screen.blit(self.midfont.render("Continue?",True,WHITE),(self.pos(self.midfont.size("Continue?")),300))
				Screen.blit(self.midfont.render("*",True,WHITE),(150+self.select*300,400))
				Screen.blit(self.midfont.render("YES",True,WHITE),(200,400))
				Screen.blit(self.midfont.render("NO",True,WHITE),(500,400))
		pygame.display.update()

def main():
	try:
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
		f = open("data/score.txt","r")
		game.highscore = eval(f.readline())
		f.close()
		f = open("data/noise.txt","r")
		for line in f.readlines():
			game.noise.append(eval(line))
		f.close()
		while True:
			Clock.tick(60)
			game.update()
	finally:
		f = open("data/score.txt","w")
		f.write(str(game.highscore))
		f.close()

if __name__ == '__main__': main()
