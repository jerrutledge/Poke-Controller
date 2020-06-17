#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

# Mash a button A
# A連打
class Mash_A(PythonCommand):
	NAME = 'Mash A'

	def __init__(self):
		super().__init__()

	def do(self):
		while True:
			self.press(Button.A, wait=0.1)

class direction_and_A(PythonCommand):
	NAME = "Direction & A"

	def __init__(self):
		super().__init__()
		self.repeated_direction = Direction.RIGHT
		self.second_button = False

	def do(self):
		while True:
			self.press(Button.A, wait=1.4)
			if self.second_button:
				self.wait(1)
				self.press(Button.Y, wait=1.4)
			self.press(self.repeated_direction, duration=0.3)