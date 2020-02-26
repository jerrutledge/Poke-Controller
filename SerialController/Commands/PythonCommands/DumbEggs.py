#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

# CONDITIONS:
# start in the bridge field 
# on your bike
# with a full party (the pokemon in the second slot will be replaced)
# with the default menu option being the map
# choose where new pokemon go *manually* in game settings 
class DumbEggHatcher(PythonCommand):
	NAME = "Dumb Egg Hatcher"

	def __init__(self):
		super().__init__()

	def do(self):
		while True:
			self.press(Button.X, wait=1) # open menu
			self.pressRep(Button.A, 20, wait=3) # fly to bridge field

			# walk to daycare and get an egg
			self.press(Direction.DOWN, duration=0.05, wait=0.5)
			self.press(Direction.DOWN, duration=0.8)
			self.press(Direction.LEFT, duration=0.2)
			
			self.pressRep(Button.A, 18, duration=0.3, wait=0.8) # Put egg on your team
			self.press(Direction.DOWN) # select correct pokemon slot
			self.press(Button.A)
			self.pressRep(Button.B, 10)

			# begin the spin
			self.press(Direction.RIGHT, duration=1)
			self.hold([Direction.RIGHT, Direction.R_LEFT])
			for i in range(64):
				print('wait for ' + str(i))
				self.wait(1)

			print('egg hatching')
			self.holdEnd([Direction.RIGHT, Direction.R_LEFT])
			self.press(Button.B, wait=14) # "Oh?"
			self.pressRep(Button.B, 10, wait=1)