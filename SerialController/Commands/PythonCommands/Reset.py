#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

# reset the game
class ResetGame(PythonCommand):

	def __init__(self):
		super().__init__()

	def resetGame(self, wait_for_load=True):
		self.wait(0.3)
		self.press(Button.HOME, wait=1)
		self.press(Button.X, wait=0.5)
		self.pressRep(Button.A, 25, wait=16)
		self.pressRep(Button.A, 6, interval=0.5)
		# wait extra time for the game to load in and take control of the character
		# if executing this before taking some other action, set to True
		if wait_for_load:
			self.wait(8)

# reset the game
class Reset(ResetGame):
	NAME = "Reset"

	def __init__(self):
		super().__init__()

	def do(self):
		# we're resetting manually, finish the program after pressing A on title
		self.resetGame(wait_for_load=False)