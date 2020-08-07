#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

class PokeScan(ImageProcPythonCommand):
	NAME = 'PokeScan'

	def __init__(self, cam):
		super().__init__(cam)
		self.file_name = "pokemon_scan_2.txt"
		self.n = 3000

	def do(self):
		file = open(self.file_name, "w")
		for i in range(self.n):
			print(" ================= getting pokemon #"+str(i+1))
			self.wait(self.stream_delay)
			pokemon = str(i+1) + ": "
			number = self.getText(500, 150, 950, 1, digits=True, inverse=True)
			print("NUMBER = "+str(number))
			pokemon += "number=("+str(number)+") "
			screen_read = self.getText()
			print(screen_read)
			pokemon += screen_read.replace("\n", "\t")
			pokemon += "\n"
			file.write(pokemon)
			self.press(Button.R, wait=2)
		file.close()