#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractclassmethod
from time import sleep
import threading
import cv2
from .Keys import KeyPress, Button, Hat, Direction, Stick
from . import CommandBase
import pytesseract
from pprint import pprint

# the class For notifying stop signal is sent from Main window
class StopThread(Exception):
	pass

# Python command
class PythonCommand(CommandBase.Command):
	def __init__(self):
		super(PythonCommand, self).__init__()
		self.keys = None
		self.thread = None
		self.alive = True
		self.postProcess = None

	@abstractclassmethod
	def do(self):
		pass

	def do_safe(self, ser):
		if self.keys is None:
			self.keys = KeyPress(ser)

		try:
			if self.alive:
				self.do()
				self.finish()
		except StopThread:
			print('-- finished successfully. --')
		except:
			if self.keys is None:
				self.keys = KeyPress(ser)
			print('-- ERROR - please check log --')
			import traceback
			traceback.print_exc()
			self.keys.end()
			self.alive = False

	def start(self, ser, postProcess=None):
		self.alive = True
		self.postProcess = postProcess
		if not self.thread:
			self.thread = threading.Thread(target=self.do_safe, args=(ser,))
			self.thread.start()

	def end(self, ser):
		self.sendStopRequest()

	def sendStopRequest(self):
		if self.checkIfAlive(): # try if we can stop now
			self.alive = False
			print('-- sent a stop request. --')

	# NOTE: Use this function if you want to get out from a command loop by yourself
	def finish(self):
		self.alive = False
		self.end(self.keys.ser)

	# press button at duration times(s)
	def press(self, buttons, duration=0.1, wait=0.1):
		self.keys.input(buttons)
		self.wait(duration)
		self.keys.inputEnd(buttons)
		self.wait(wait)
		self.checkIfAlive()

	# press button at duration times(s) repeatedly
	def pressRep(self, buttons, repeat, duration=0.1, interval=0.1, wait=0.1):
		for i in range(0, repeat):
			self.press(buttons, duration, 0 if i == repeat - 1 else interval)
		self.wait(wait)

	# add hold buttons
	def hold(self, buttons, wait=0.1):
		self.keys.hold(buttons)
		self.wait(wait)

	# release holding buttons
	def holdEnd(self, buttons):
		self.keys.holdEnd(buttons)
		self.checkIfAlive()

	# do nothing at wait time(s)
	def wait(self, wait):
		sleep(wait)
		self.checkIfAlive()

	def checkIfAlive(self):
		if not self.alive:
			self.keys.end()
			self.keys = None
			self.thread = None

			if not self.postProcess is None:
				self.postProcess()
				self.postProcess = None

			# raise exception for exit working thread
			raise StopThread('exit successfully')
		else:
			return True

	# Use time glitch
	# Controls the system time and get every-other-day bonus without any punishments
	def timeLeap(self, is_go_back=True):
		self.press(Button.HOME, wait=1)
		self.press(Direction.DOWN)
		self.press(Direction.RIGHT)
		self.press(Direction.RIGHT)
		self.press(Direction.RIGHT)
		self.press(Direction.RIGHT)
		self.press(Button.A, wait=1.5) # System Settings
		self.press(Direction.DOWN, duration=2, wait=0.5)

		self.press(Button.A, wait=0.3) # System Settings > System
		self.press(Direction.DOWN)
		self.press(Direction.DOWN)
		self.press(Direction.DOWN)
		self.press(Direction.DOWN, wait=0.3)
		self.press(Button.A, wait=0.2) # Date and Time
		self.press(Direction.DOWN, duration=0.7, wait=0.2)

		# increment and decrement
		if is_go_back:
			self.press(Button.A, wait=0.2)
			self.press(Direction.UP, wait=0.2) # Increment a year
			self.press(Direction.RIGHT, duration=1.5)
			self.press(Button.A, wait=0.5)

			self.press(Button.A, wait=0.2)
			self.press(Direction.LEFT, duration=1.5)
			self.press(Direction.DOWN, wait=0.2) # Decrement a year
			self.press(Direction.RIGHT, duration=1.5)
			self.press(Button.A, wait=0.5)

		# use only increment
		# for use of faster time leap
		else:
			self.press(Button.A, wait=0.2)
			self.press(Direction.RIGHT)
			self.press(Direction.RIGHT)
			self.press(Direction.UP, wait=0.2) # increment a day
			self.press(Direction.RIGHT, duration=1)
			self.press(Button.A, wait=0.5)

		self.press(Button.HOME, wait=1)
		self.press(Button.HOME, wait=1)

TEMPLATE_PATH = "./Template/"
class ImageProcPythonCommand(PythonCommand):
	def __init__(self, cam):
		super(ImageProcPythonCommand, self).__init__()
		self.camera = cam
		self.stream_delay = 1.4

	# Judge if current screenshot contains an image using template matching
	# It's recommended that you use gray_scale option unless the template color wouldn't be cared for performace
	# 現在のスクリーンショットと指定した画像のテンプレートマッチングを行います
	# 色の違いを考慮しないのであればパフォーマンスの点からuse_grayをTrueにしてグレースケール画像を使うことを推奨します
	def isContainTemplate(self, template_path, threshold=0.7, use_gray=True, show_value=False):
		src = self.camera.readFrame()
		src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) if use_gray else src

		template = cv2.imread(TEMPLATE_PATH+template_path, cv2.IMREAD_GRAYSCALE if use_gray else cv2.IMREAD_COLOR)
		w, h = template.shape[1], template.shape[0]

		method = cv2.TM_CCOEFF_NORMED
		res = cv2.matchTemplate(src, template, method)
		_, max_val, _, max_loc = cv2.minMaxLoc(res)

		if show_value:
			print(template_path + ' ZNCC value: ' + str(max_val))

		if max_val > threshold:
			if use_gray:
				src = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)

			top_left = max_loc
			bottom_right = (top_left[0] + w, top_left[1] + h)
			cv2.rectangle(src, top_left, bottom_right, (255, 0, 255), 2)
			return True
		else:
			return False

	# read text (from the specified part of the screen)
	# debug = True will print the text and save a screenshot
	def getText(self, top=1, bottom=1, left=1, right=1, digits=False, 
			inverse=False, threshold = 0, debug=False):
		frame = self.camera.readFrame()
		# gray and apply crop/threshold/inverse
		src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		crop = not (left==1 and top==1 and right==1 and bottom==1)
		if crop:
			src = src[top:-bottom, left:-right]
		if inverse:
			src = cv2.bitwise_not(src)
		if threshold > 1:
			src = cv2.threshold(src, threshold, 255, cv2.THRESH_OTSU)[1]


		# Output OCR of selected area
		# Define config parameters.
		# '-l eng'  for using the English language
		# '--oem 1' for using LSTM OCR Engine
		if digits:
			config = ('-l eng digits')
		else:
			config = ('-l eng --oem 1 --psm 3')
		text = pytesseract.image_to_string(src, config=config)

		if debug:
			print("OCR Reading:")
			print(text)
			if crop:
				self.camera.saveCapture(top, bottom, left, right)
		return text

	# Get interframe difference binarized image
	# フレーム間差分により2値化された画像を取得
	def getInterframeDiff(self, frame1, frame2, frame3, threshold):
		diff1 = cv2.absdiff(frame1, frame2)
		diff2 = cv2.absdiff(frame2, frame3)

		diff = cv2.bitwise_and(diff1, diff2)

		# binarize
		img_th = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]

		# remove noise
		mask = cv2.medianBlur(img_th, 3)
		return mask

	# detect number of stars
	def getStars(self, output_photo=False):
		src = self.camera.readFrame()
		# crop and gray
		src = (cv2.cvtColor(src, cv2.COLOR_BGR2GRAY))[1:100, 1:550]
		_, base_img = cv2.threshold(src, 190, 255, cv2.THRESH_BINARY)
		contours, _ = cv2.findContours(base_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		# draw contours & print, if enabled
		if output_photo:
			for c in contours:
				approx = cv2.approxPolyDP(c,0.05*cv2.arcLength(c, True), True)
				cv2.drawContours(base_img, [approx], 0, (160, 0, 0), 2)
			dt_now = datetime.datetime.now()
			fileName = dt_now.strftime('%Y-%m-%d_%H-%M-%S')+".png"
			cv2.imwrite(fileName, base_img)

		return len(contours)