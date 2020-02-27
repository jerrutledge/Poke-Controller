#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.OfflineDateGlitch.OfflineDateGlitchBase import OfflineDateGlitchCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

# Perform the Day skip glitch n times
# ***must be started on the 1st of a 31-day month***
class AdvanceFrameBy(OfflineDateGlitchCommand):
	NAME = 'Advance Frame By N'

	def __init__(self):
		super().__init__()
		self.use_rank = True
		self.n = 5

	def do(self):
		for i in range(1, self.n):
			self.wait(1)

			if ((i-1)%30 == 0) and (i != 1):
				# this skip will put the day back to one
				print("setting date to beginning of month...")
				self.changeDay(False)

			print("advancing frame " + str(i) + "...")

			self.press(Button.A, duration=0.4, wait=0.1)
			self.press(Button.A, duration=0.4, wait=0.1) # 2000W
			self.press(Button.A, wait=0.8)
			self.press(Button.A, duration=0.1, wait=3)
			self.press(Button.B, duration=0.3, wait=0.5)
			self.changeDay(False)
			self.press(Button.A, wait=5)

			print("now on frame: " + str(i+1))

		self.finish()


# resets until finding a n star raid on the nth frame
class FindNStar(OfflineDateGlitchCommand):
	NAME = 'Find N-Star Raid'

	def __init__(self, cam):
		super().__init__(cam)
		self.n = 4
		self.reset = False
		self.purple = True
		self.desired_num_of_stars = 5
		self.desired_pokemon = "Sirfetch'd"
		# desired ability function assumes your lead has trace
		self.desired_ability = "Scrappy"
		self.desired_first_type = "FIGHTING"
		self.desired_second_type = "None"
		self.debug = True

	def do(self):
		if self.reset:
			self.resetGame(wait_for_load=True)
		else:
			# assume that the current raid is not the desired raid and begin by advancing the date
			self.raidLeap()
		while True:
			if self.reset:
				for i in range(1, self.n):
					self.wait(0.5)

					print("advancing frame " + str(i) + "...")
					self.advanceFrame()

			self.enterRaidDen()
			self.wait(self.stream_delay)

			#check stars
			print("checking stars (want:"+str(self.desired_num_of_stars)+")...")
			stars = self.getStars()
			print("stars: "+str(stars))

			#check type
			pokemon_types = ["BUG", "DARK", "DRAGON", "ELECTRIC", "FAIRY", \
					"FIGHTING", "FIRE", "FLYING", "GHOST", "GRASS", "GROUND", \
					"ICE", "NORMAL", "POISON", "PSYCHIC", "ROCK", "STEEL", "WATER"]
			first_type = self.getText(100, -140, 75, -180, inverse=True)
			# there must be a first type
			for _ in range(3):
				if first_type in pokemon_types:
					break
				else:
					first_type = self.getText(100, -140, 75, -180, inverse=True)
				for current_type in pokemon_types:
					if current_type in first_type:
						first_type = current_type
						break
			print("first type: " + first_type)
			second_type = self.getText(100, -140, 217, -330, inverse=True)
			for current_type in pokemon_types:
				if current_type in second_type:
					second_type = current_type
					break
			if not second_type in pokemon_types:
				second_type = "None"
			print("second type: " + second_type)

			if stars == self.desired_num_of_stars and \
					first_type == self.desired_first_type and \
					second_type == self.desired_second_type:
				if not self.reset:
					self.press(Button.B, wait=2)
					self.save()
					result = self.battle(True, self.desired_pokemon, 
							desired_ability=self.desired_ability)
					if not result:
						self.advanceFrame(reset_and_save_game=True)
						continue
				return

			if self.reset:
				self.resetGame(wait_for_load=True)
			else:
				self.raidLeap()


# Reset Perform the Day skip glitch once & Save
class AdvanceBaseFrame(OfflineDateGlitchCommand):
	NAME = "Advance Base Frame"

	def __init__(self, cam):
		super().__init__(cam)

	def do(self):
		self.advanceFrame(reset_and_save_game=True)


# Dynamax and spam first move on first pokemon
class AutoMaxRaid(OfflineDateGlitchCommand):
	NAME = "Auto Max Raid Battle"

	def __init__(self, cam):
		super().__init__(cam)
		self.dynamax = False
		self.move_num = 3

	def do(self):
		self.battle(dynamax = self.dynamax, move_num=self.move_num)