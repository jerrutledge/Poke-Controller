#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.Reset import ResetGame
from Commands.Keys import KeyPress, Button, Direction, Stick

# Provides common functions between 
class OfflineDateGlitchCommand(ImageProcPythonCommand, ResetGame):
	def __init__(self, cam):
		super().__init__(cam)
		# in North America, the switch displays month, day, etc.
		# in other regions, day, month, etc.
		# set to true if North America
		self.day_in_second_position = True

	def changeDay(self, go_back=False, to_date=0):
		self.press(Button.HOME, wait=1)
		self.press(Direction.DOWN)
		self.press(Direction.RIGHT)
		self.press(Direction.RIGHT)
		self.press(Direction.RIGHT)
		self.press(Direction.RIGHT)
		self.press(Button.A, wait=1.5) # System Settings
		self.press(Direction.DOWN, duration=2, wait=0.5)

		self.press(Button.A, wait=0.3) # System Settings > System
		self.press(Direction.DOWN)
		self.press(Direction.DOWN)
		self.press(Direction.DOWN)
		self.press(Direction.DOWN, wait=0.3)
		self.press(Button.A, wait=0.2) # Date and Time
		self.press(Direction.DOWN, duration=0.7, wait=0.2)

		self.press(Button.A, wait=0.2) # > Set Date and Time
		if self.day_in_second_position:
			self.press(Direction.RIGHT)
		if go_back:
			self.press(Direction.DOWN, wait=0.2) # DECREMENT a day
		else:
			self.press(Direction.UP, wait=0.2) # increment a day
		self.press(Direction.RIGHT, duration=1)
		self.press(Button.A, wait=0.5)

		self.press(Button.HOME, wait=1)
		self.press(Button.HOME, wait=1)

	def save(self):
		print("saving...")
		self.press(Button.X, wait=1)
		self.press(Button.R, wait=2)
		self.press(Button.A, wait=4)

	def enterRaidDen(self):
		if self.isContainTemplate('raid_den_options.png'):
			print("already in den")
			return
		# enter the raid screen
		self.press(Button.A, duration=0.4, wait=self.stream_delay)
		# this button press either leaves you at: 
		# 1. "energy flowing out of the den"
		# 2. inside the first screen of the den
		print("in raid den yet?")
		if not self.isContainTemplate('raid_den_options.png'):
			print("not in raid den. entering")
			self.press(Button.A, duration=0.4, wait=0.1) # 2000W
			self.press(Button.A, wait=1)

	def raidLeap(self):
		self.enterRaidDen()
		self.pressRep(Button.A, 2, duration=0.5, interval=0.5, wait=2.6) # start looking for trainers
		self.press(Button.B, duration=0.4, wait=0.5)
		self.changeDay(go_back=False)
		self.press(Button.A, wait=4.5)

	def advanceFrame(self, reset_and_save_game=False, num_frames=1):
		if reset_and_save_game:
			self.resetGame()
		if num_frames <= 1:
			print("setting date back by one...")
			self.changeDay(go_back=True)
			self.wait(self.stream_delay)
			self.raidLeap()
		else:
			print("setting date to beginning of month...")
		if reset_and_save_game:
			self.save()

	def battle(self, check_pokemon=False, desired_pokemon="", dynamax=False, 
			move_num=1, desired_ability="", catch=True):
		# enter the raid den, if necessary 
		self.enterRaidDen()
		# enter the battle
		self.press(Direction.DOWN)
		self.press(Button.A, duration=0.5)
		self.press(Button.A, duration=0.5)
		self.press(Button.A, wait=11)
		# check pokemon
		if check_pokemon:
			found = False
			print("get top text:")
			for i in range(1, 40):
				print("getting text, attempt #"+str(i))
				screen_text = self.getText(inverse=True, debug=True)
				if desired_pokemon in screen_text:
					print("FOUND "+desired_pokemon+" on #"+str(i)+" TRY")
					found = True
					break
			if not found:
				print("did not find "+desired_pokemon+" :(")
				return False
		# wait for battle screen to appear
		while not self.isContainTemplate('battle_icon.png'):
			print("no battle icon...")
			self.wait(3)

		# check for desired ability by checking lead's ability after trace
		if desired_ability != "":
			self.press(Button.Y, wait=1)
			self.press(Button.A, wait=1)
			self.wait(self.stream_delay)
			for i in range(3):
				ability_text = self.getText(40, -120, 600, 1, inverse=True)
				print("ability_text: " + ability_text)
				if desired_ability in ability_text:
					print("found ability: " + desired_ability)
					break
				if i == 2:
					print("could not find ability: " + desired_ability + " :(")
					return False
				else:
					self.wait(1)

		# choose a move
		self.press(Button.A, wait=0.5)
		if dynamax:
			self.press(Direction.LEFT)
			self.press(Button.A, wait=0.5)
		for _ in range(move_num-1):
			self.press(Direction.DOWN)
		self.pressRep(Button.A, 4, interval=0.5, wait=4)

		while True:
			if self.isContainTemplate('battle_icon.png'):
				print("battle icon detected, making move")
				self.pressRep(Button.A, 5, interval=0.5, wait=0.5)
			elif "Catch" in self.getText(debug=True):
				if catch:
					print("catching...")
					self.press(Button.A, wait=0.5)
					self.press(Button.A, wait=0.5)
				else:
					print("not catching...")
					self.press(Direction.DOWN)
					self.press(Button.A, wait=0.5)
					self.press(Button.A, wait=0.5)
				break
			self.wait(3)

		# exit when the pokemon is caught
		if catch:
			for _ in range(40):
				if "caught" in self.getText(40, -120, 600, 1, inverse=True):
					print("Pokemon caught!")
					break
				elif "defeated" in self.getText(40, -120, 600, 1, inverse=True):
					print("could not catch pokemon!")
					break
				else:
					self.wait(3)

		return True

	# assuming the set date option of the switch is already open
	# this function will read the number of the date and 
	# execute the correct number of up / down presses to set the date to "day"
	def setDay(self, day=1):
		self.wait(self.stream_delay)
		date = self.getText(-300, 200, 250, -350, digits=True, inverse=True, debug=True)
		while not date.strip().isdigit():
			print("date is not digit, checking again...")
			date = self.getText(-300, 200, 250, -350, digits=True, inverse=True, debug=True)
		print("date is "+date+", desired date is "+str(day))
		date = int(date)
		if day < date:
			self.pressRep(Direction.DOWN, date - day)
		elif day > date:
			self.pressRep(Direction.UP, day - date)
