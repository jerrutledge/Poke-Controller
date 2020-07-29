#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.Reset import ResetGame
from Commands.Keys import KeyPress, Button, Direction, Stick
from Commands.PythonCommands.ImageProcessingOnly.AutoTrainerBattle import AutoTrainerBattle

# use this function to reset for a unique or legendary pokemon (e.g. zacian, zamazenta)
# Unique pokemon will reset for a given nature, shininess, etc.
class UniquePokemon(AutoTrainerBattle):
	NAME = 'Reset for unique pokemon'

	def __init__(self, cam):
		super().__init__(cam)
		self.desired_traits = [
			{
				"ivs": [],
				"nature": "Adamant",
				"shiny": False,
			},
		]
		# in order to start the battle with eternatus, 
		# the player has to walk upwards into a cutscene trigger
		self.begin_by_walking_up = False
		self.num_battles = 1
		self.mashing_duration = 190

	def do(self):
		while True:
			if self.begin_by_walking_up:
				self.press(Direction.UP, duration=5)
			for _ in range(self.num_battles):
				self.autoBattle()
			print("Mashing for "+str(self.mashing_duration/2)+" seconds")
			self.pressRep(Button.A, self.mashing_duration, interval=0.5)
			# check pokemon
			self.press(Button.X, wait=1.5)
			# (this assumes the pokemon menu is in the top left corner of the menu)
			self.press(Button.A, wait=2) # open the pokemon menu 
			self.press(Direction.UP) # last pokemon in party
			self.press(Button.A, wait=0.5) # select
			self.press(Button.A, wait=3) # check summary
			self.pressRep(Direction.LEFT, 2, interval=0.5, wait=self.stream_delay)
			nature_screen_text = self.getText()
			print("Nature screen reading: \n\n" + nature_screen_text)
			for trait_set in self.desired_traits:
				if trait_set["nature"] in nature_screen_text:
					print("Desired nature '"+trait_set["nature"]+"' found!")
					return
			print("Did not find a matching set of desired traits. Resetting...")
			self.resetGame()
