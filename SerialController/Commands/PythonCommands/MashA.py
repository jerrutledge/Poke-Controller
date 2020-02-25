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
