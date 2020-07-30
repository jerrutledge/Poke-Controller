#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick
import cv2
import time

# using RankBattle glitch
# Infinity getting berries
# 無限きのみ(ランクマッチ, 画像認識任意)
class InfinityBerry(ImageProcPythonCommand):
	NAME = 'Infinity Berry'

	def __init__(self, cam):
		super().__init__(cam)
		self.cam = cam

	def do(self):
		# If camera is not opened, then pick 1 and timeleap (never "Shake it more")
		if not self.cam.isOpened():
			while True:
				self.press(Button.A, wait=0.5)
				self.press(Button.B, wait=0.5)
				self.press(Button.A, wait=0.5) # yes
				# exit dialogue
				self.pressRep(Button.B, 15, interval=0.5)

				# Time glitch
				self.timeLeap()

		else:
			while True:
				# talk to tree
				self.press(Button.A, duration=0.5)
				while True:
					text = self.getNextText()
					if "It's a tree" in text:
						print("1 - Shaking tree")
						# two possible states: 
						# 1. A down arrow that indicates the dialogue can be advanced
						# 2. A (Yes/No) menu
						self.press(Button.A, duration=0.3)
						self.press(Button.A)
						# if we press A twice quickly it covers both cases:
						# 1. Brings up the menu and selects yes
						# 2. Selects yes and the second input is eaten by the animation
						self.wait(4) # wait for the shaking animation to finish
					if "nothing" in text:
						print("Tree is currently empty. Advancing the date...")
						self.press(Button.B, wait=0.5)
						break
					if "fell from the tree" in text:
						print('2 - Something fell: '+text)
					if "fallen to the ground" in text:
						if self.isContinue():
							print('3 - Continue shaking tree')
							self.press(Button.A, wait=4)
							continue
						else:
							print('4 - Collect berries and advance the date')
							self.pressRep(Button.B, 10, interval=0.5)
							break

				# Time glitch
				self.timeLeap()

	def isContinue(self, check_interval=0.1, check_duration=2):
		check_time = 0
		zero_count = 0
		height_half = int(self.camera.capture_size[1] / 2)

		frame1 = cv2.cvtColor(self.camera.readFrame()[0:height_half-1, :], cv2.COLOR_BGR2GRAY)
		time.sleep(check_interval / 3)
		frame2 = cv2.cvtColor(self.camera.readFrame()[0:height_half-1, :], cv2.COLOR_BGR2GRAY)
		time.sleep(check_interval / 3)
		frame3 = cv2.cvtColor(self.camera.readFrame()[0:height_half-1, :], cv2.COLOR_BGR2GRAY)

		while check_time < check_duration:
			mask = self.getInterframeDiff(frame1, frame2, frame3, 15)
			zero_count += cv2.countNonZero(mask)

			frame1 = frame2
			frame2 = frame3
			time.sleep(check_interval)
			frame3 = cv2.cvtColor(self.camera.readFrame()[0:height_half-1, :], cv2.COLOR_BGR2GRAY)

			check_time += check_interval

		print('InfinityBerry.isContinue: zero_count=' + str(zero_count))

		# zero count threshold is heuristic value... weather: sunny
		return True if zero_count < 9000 else False

	# advances the dialogue by one box and returns the next text
	def getNextText(self):
		self.press(Button.A, duration=0.5)
		self.wait(self.stream_delay)
		return self.getText(top=-130, bottom=30, left=50, right=50)