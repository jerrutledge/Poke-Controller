#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.OfflineDateGlitch.OfflineDateGlitchBase import OfflineDateGlitchCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

# Perform the Day skip glitch n times
# ***must be started on the 1st of a 31-day month***
class AdvanceFrameBy(OfflineDateGlitchCommand):
	NAME = 'Advance Frame By N'

	def __init__(self, cam):
		super().__init__(cam)
		self.use_rank = True
		self.n = 9

	def do(self):
		for i in range(1, self.n):
			self.wait(1)

			if ((i-1)%30 == 0) and (i != 1):
				# this skip will put the day back to one
				print("setting date to beginning of month...")
				self.changeDay(False)

			print("advancing frame " + str(i) + "...")

			self.enterRaidDen()
			self.pressRep(Button.A, 2, duration=0.5, interval=0.5, wait=2.6)
			self.press(Button.B, duration=0.3, wait=0.5)
			self.changeDay(False)
			self.press(Button.A, wait=3.5)

			print("now on frame: " + str(i+1))

		self.finish()


# resets until finding a n star raid on the nth frame
class FindNStar(OfflineDateGlitchCommand):
	NAME = 'Find N-Star Raid'

	def __init__(self, cam):
		super().__init__(cam)
		# reset and n are intended for finding shiny pokemon on particular frames:
		# 1. save on n frames before our intended shiny frame
		# 2. advance n frames to our shiny frame
		# 3. check if the pokemon is the right pokemon (e.g. is it G-Max Charizard?)
		# 4. reset - taking us back n frames to try again
		self.reset = False
		self.n = 0
		# a list of acceptable pokemon (as there may be more than one)
		self.combinations = [
		{
			"stars": 5,
			"name": "Alakazam",
			"ability": "Magic Guard",
			"types": ["PSYCHIC", "None"],
		},
		]
		self.debug = True

	def do(self):
		self.FindRaid(reset=self.reset, skip_num=self.n, combinations=self.combinations)

	def FindRaid(self, reset=False, skip_num=4, combinations=[]):
		if reset:
			self.resetGame(wait_for_load=True)
		else:
			# assume that the current raid is not the desired raid and begin by advancing the date
			self.raidLeap()
		while True:
			if reset:
				for i in range(1, skip_num):
					self.wait(0.5)

					print("advancing frame " + str(i) + "...")
					self.advanceFrame()

			self.wait(0.2)
			self.enterRaidDen()
			self.wait(self.stream_delay)

			#check stars
			stars = self.getStars()
			print("stars: "+str(stars))

			#check type
			types = self.getTypes(100, 75)
			print("types: " + str(types))
			if (types == [] or stars > 5 or stars < 1):
				# we probably failed to enter the den in time for the stream delay
				# just try again
				if reset:
					self.resetGame(wait_for_load=True)
				continue

			for combo in combinations:
				if combo["types"] == types and combo["stars"] == stars:
					# we don't need to check name and ability if we aren't resetting
					if not reset:
						print("Found a potential match for:" )
						self.press(Button.B, wait=2)
						self.save()
						result = self.battle(True, combo["name"],
								desired_ability=combo["ability"])
						if not result:
							# if we've entered the battle, we need to reset 
							# and also make sure we don't check the same frame twice
							self.resetGame(wait_for_load=True)
							break
					print("Pokemon found!! "+str(combo))
					return True

			print("not a match...")
			if reset:
				self.resetGame(wait_for_load=True)
			else:
				self.raidLeap()


class HostMaxRaidBattles(FindNStar):
	NAME = 'HOST MAX RAID'

	def __init__(self, cam):
		super().__init__(cam)
		self.n = 7
		self.reset = True
		self.desired_num_of_stars = 3
		self.desired_pokemon = ""
		# desired ability function assumes your lead has trace
		self.desired_ability = ""
		self.match_type = False
		self.desired_first_type = ""
		self.desired_second_type = ""
		self.debug = True

	def do(self):
		while True:
			self.FindRaid(reset=True, num_stars=self.desired_num_of_stars,
				ability=self.desired_ability, match_type=self.match_type,
				desired_first_type=self.desired_first_type,
				desired_second_type=self.desired_second_type, skip_num=self.n)
			# after finding the raid, go online
			self.press(Button.B, wait=2)
			self.press(Button.Y, wait=2)
			self.press(Button.PLUS, wait=10)
			self.pressRep(Button.B, 2, interval=0.5, wait=3)
			text = self.getText()
			num_players = 1
			while num_players < 4:
				# enter the raid den and invite others
				print("beginning search for players...")
				self.enterRaidDen()
				self.press(Button.A)
				for i in range(180):
					if "Searching..." in text:
						self.wait(1)
					else:
						# no "Searching...", 4 players found
						num_players = 4
						break
					if i > 160:
						print("could not find 4 players. exiting...")
						self.press(Button.B, duration=0.5, wait=0.5)
						self.press(Button.A, wait=3)
						break
					text = self.getText(debug=self.debug)
			print("found a full party. entering raid")
			self.press(Direction.UP)
			self.pressRep(Button.A, 3, interval=0.5)
			self.battle(catch=False)



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
		self.move_num = 1
		self.catch = True

	def do(self):
		self.battle(dynamax = self.dynamax, move_num=self.move_num, catch=self.catch)