#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.Reset import ResetGame
from Commands.Keys import KeyPress, Button, Direction, Stick

# Battle through trainers by setting up with Swords Dance/X-Attack
# Spams the pokemon's slot 1 attack. Assumes swords dance is in slot 2
class AutoTrainerBattle(ImageProcPythonCommand, ResetGame):
	NAME = 'Auto Trainer Battle'

	def __init__(self, cam):
		super().__init__(cam)
		self.use_swords_dance = True
		self.times_set_up = 1

	def do(self):
		print('AUTO BATTLE: use_swords_dance='+str(self.use_swords_dance)+" "+str(self.times_set_up)+' times')
		while True:
			self.autoBattle(set_up_turns=self.times_set_up)
		
	def autoBattle(self, set_up_turns=0):
		while True:
			text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
			if "You are challenged by" in text or "sent out" in text:
				print("Entering Trainer battle...")
				self.trainerBattle()
				return
			if "Zacian appeared!" in text or "Zamazenta appeared!" in text:
				self.captureBattle()
				return
			if "appeared!" in text:
				self.trainerBattle()
				return
			if "wants to learn" in text or "to forget" in text or "old move" in text:
				print("learning move? text="+text)
				self.finish()
			self.pressRep(Button.A, 3)

	def trainerBattle(self, set_up_turns=0):
		# if there is set up, set up
		if set_up_turns > 0:
			self.waitForBattleIcon()
			print("setting up "+str(set_up_turns)+" times. boost move="+\
				str(self.use_swords_dance))
			if self.use_swords_dance:
				self.press(Button.A, wait=0.5)
				self.press(Direction.DOWN)
				for i in range(set_up_turns):
					print("set up #" + str(i+1))
					# use set up move
					self.press(Button.A, wait=self.stream_delay)
					self.waitForBattleIcon()
					# enter attack menu
					self.press(Button.A, wait=0.5)
				# now that set up is complete, choose attacking move
				self.press(Direction.UP)
				self.press(Button.A)
			else:
				# apply X Sp Attack in bag
				self.press(Direction.DOWN)
				self.press(Button.A, wait=1)
				self.pressRep(Direction.RIGHT, 3)
				self.pressRep(Button.A, 4)
				# TODO: select attack before continuing to spam A
		# now just spam until the battle is over
		text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
		while not ("defeated" in text or "defeat" in text):
			self.press(Button.A)
			text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
			print("checking text: " + str(text))
			if "learn" in text or "forget" in text or "old move" in text:
				print("learning move? exiting...")
				self.finish()
			if "no energy left" in text:
				print("partner pokemon has been defeated. Choosing new pokemon.")
				self.pressRep(Button.B, 4)
				self.press(Direction.DOWN)
				self.press(Button.A)
		print("trainer has been defeated")

	# wait until the battle icon shows up
	def waitForBattleIcon(self):
		time = 0

		while not self.isContainTemplate('battle_icon.png'):
			print("waiting for battle icon... "+str(time))
			self.press(Button.B, duration=0.1, wait=0.9)
			time += 1

	# capture Zacian/Zamazenta with the master ball
	def captureBattle(self, ball_position=0):
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