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
			self.press(Button.X, wait=1.5) # open menu
			self.press(Button.A, wait=2) # select map
			self.press(Button.A, duration=1) # you want to teleport here?
			self.press(Button.A, wait=4) # sure!

			# walk to daycare and get an egg
			self.press(Direction.DOWN, duration=0.05, wait=0.5)
			self.press(Direction.DOWN, duration=0.8)
			self.press(Direction.LEFT, duration=0.2)
			self.press(Button.A, duration=1) # talk to her "I have an egg for you, do you want it?"
			self.press(Button.A, wait=4) # yes I do
			self.press(Button.A, wait=3) # you got it
			self.press(Button.A, duration=1) # Put egg on your team
			self.press(Button.A, wait=2) # please select the slot!
			self.press(Direction.DOWN) # select correct pokemon slot
			self.press(Button.A)
			self.pressRep(Button.B, 6, duration=0.5, interval=0.5, wait=1)

			# begin the spin
			self.press(Direction.RIGHT, duration=1)
			self.hold([Direction.RIGHT, Direction.R_LEFT])
			for i in range(65):
				print('wait for ' + str(i))
				self.wait(1)

			print('egg hatching')
			self.holdEnd([Direction.RIGHT, Direction.R_LEFT])

			# egg hatched?
			self.press(Button.A, wait=16) # Oh
			self.press(Button.A, wait=4) # "Pokemon" hatched from the egg