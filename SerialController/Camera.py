#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import cv2
import time, datetime

class Camera:
	def __init__(self):
		self.camera = None
		self.capture_size = (1280, 720)
		self.capture_dir = "Captures"

	def openCamera(self, cameraId):
		if self.camera is not None and self.camera.isOpened():
			self.destroy()

		if os.name == 'nt':
			self.camera = cv2.VideoCapture(cameraId, cv2.CAP_DSHOW)
		else:
			self.camera = cv2.VideoCapture(cameraId)

		if not self.camera.isOpened():
			print("Camera ID " + str(cameraId) + " can't open.")
			return
		print("Camera ID " + str(cameraId) + " opened successfully")
		self.camera.set(cv2.CAP_PROP_FPS, 60)
		self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_size[0])
		self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_size[1])

	def isOpened(self):
		return self.camera.isOpened()

	def readFrame(self):
		_, self.image_bgr = self.camera.read()
		return self.image_bgr

	def saveCapture(self, top=1, bottom=1, left=1, right=1):
		src = self.image_bgr
		crop = not (top==1 and bottom==1 and left==1 and right==1)
		if crop:
			src = src[top:-bottom, left:-right]

		dt_now = datetime.datetime.now()
		suffix = ""
		if crop:
			suffix = "T"+str(top)+"B"+str(bottom)+"L"+str(left)+"R"+str(right)
		fileName = dt_now.strftime('%Y-%m-%d_%H-%M-%S')+suffix+".png"

		if not os.path.exists(self.capture_dir):
			os.makedirs(self.capture_dir)

		save_path = os.path.join(self.capture_dir, fileName)
		cv2.imwrite(save_path, src)

		print('capture succeeded: ' + save_path)
	
	def destroy(self):
		if self.camera is not None and self.camera.isOpened():
			self.camera.release()
			self.camera = None
