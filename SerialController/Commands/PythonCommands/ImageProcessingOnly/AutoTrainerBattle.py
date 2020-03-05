#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.Reset import ResetGame
from Commands.Keys import KeyPress, Button, Direction, Stick

# Battle through trainers by setting up with Swords Dance/X-Attack
# Spams the pokemon's slot 1 attack. Assumes swords dance is in slot 4
class AutoTrainerBattle(ImageProcPythonCommand, ResetGame):
	NAME = 'Auto Trainer Battle'

	def __init__(self, cam):
		super().__init__(cam)
		self.exit = False
		self.use_swords_dance = False
		self.times_set_up = 1

	def do(self):
		while True:
			text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
			if "You are challenged by" in text:
				print("Entering Trainer battle...")
				if self.exit:
					return
				else:
					self.trainerBattle()
			if "Zacian appeared!" in text:
				self.captureBattle()
			self.pressRep(Button.A, 3)

	def trainerBattle(self):
		self.waitForBattleIcon()
		# if there is set up, set up
		if self.times_set_up > 0:
			print("setting up")
			if self.use_swords_dance:
				self.press(Button.A, wait=0.5)
				self.press(Direction.DOWN)
				self.press(Button.A)
				self.waitForBattleIcon()
				# now that set up is complete, choose attacking move
				self.press(Button.A, wait=0.5)
				self.press(Direction.UP)
				self.press(Button.A)
			else:
				# apply X Sp Attack in bag
				self.press(Direction.DOWN)
				self.press(Button.A, wait=1)
				self.pressRep(Direction.RIGHT, 3)
				self.pressRep(Button.A, 4)
				# select attack before continuing to spam A
		# now just spam until the battle is over
		text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
		while not "defeated" in text:
			self.pressRep(Button.A, 5, interval=0.5, wait=0.5)
			text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)

	# wait until the battle icon shows up
	def waitForBattleIcon(self):
		time = 0

		while not self.isContainTemplate('battle_icon.png'):
			print("waiting for battle icon... "+str(time))
			self.wait(1)
			time += 1

	# capture Zacian/Zamazenta with the master ball
	def captureBattle(self, ball_position=3):
		self.waitForBattleIcon()
		self.press(Button.X, wait=0.5)
		self.pressRep(Direction.RIGHT, ball_position)
		self.press(Button.A)
		text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
		while not "Exp." in text:
			self.wait(0.5)
			text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
		self.press(Button.A, wait=4)
		self.pressRep(Button.A, 2, interval=0.5, wait=1)
		self.pressRep(Direction.DOWN, 2)