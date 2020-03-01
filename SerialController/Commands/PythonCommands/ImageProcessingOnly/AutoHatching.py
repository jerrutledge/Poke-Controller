#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.AutoRelease import AutoRelease
from Commands.Keys import KeyPress, Button, Direction, Stick

# auto egg hatching using image recognition
# the goal being to hatch several eggs at once
# 自動卵孵化(キャプボあり)
# assumptions:
# 1. In bridge field
# 2. Your party contains only one pokemon
# 3. Nickname choosing is turned off
# 4. Send pokemon to box is manual
# 5. The current and next (max_box) boxes are empty
class AutoHatching(AutoRelease):
	NAME = 'Auto Hatch'

	def __init__(self, cam):
		super().__init__(cam)
		self.cam = cam
		self.party_num = 1
		self.hatched_num = 0
		self.hatched_box_num = 0
		self.max_boxes = 16
		self.release_boxes = False

	def do(self):
		print("party_num: " + str(self.party_num))
		print("hatched_num: " + str(self.hatched_num))
		print("hatched_box_num: " + str(self.hatched_box_num))

		# set menu cursor to map
		self.press(Button.X, wait=1) # open menu
		self.press(Direction.LEFT, duration=1)
		self.press(Direction.DOWN, duration=0.5)
		self.press(Button.B, wait=1)

		for i in range(0, self.max_boxes):
			while self.hatched_box_num < 30:
				print('hatched box num : ' + str(self.hatched_box_num))

				# step one: fill up the party
				if self.party_num < 6:
					print('mode: fill party')
					self.getNewEgg()

					self.press(Direction.RIGHT, duration=1)
					self.hold([Direction.RIGHT, Direction.R_LEFT])
					# turn round and round
					for time in range(15):
						print('wait for ' + str(time))
						self.wait(1)
						self.hatchEgg()
					self.holdEnd([Direction.RIGHT, Direction.R_LEFT])

				# if there's hatched pokemon in your party, 
				# check if there's a new egg
				elif self.hatched_num > self.hatched_box_num:
					print('mode: add to full party')
					self.getNewEgg()
					self.press(Direction.RIGHT, duration=1)
					self.hold([Direction.RIGHT, Direction.R_LEFT])
					for time in range(15):
						print('wait for ' + str(time))
						self.wait(1)
						if self.hatchEgg() or time == 14:
							self.holdEnd([Direction.RIGHT, Direction.R_LEFT])
							break

				# otherwise wait until an egg hatches
				else:
					self.hold([Direction.RIGHT, Direction.R_LEFT])
					time = 0
					while not self.hatchEgg():
						print('wait for hatch... (' + str(time) + ')')
						time += 1
						self.wait(1)
					self.holdEnd([Direction.RIGHT, Direction.R_LEFT])

			self.wait(self.stream_delay)
			self.hatchEgg()
			print("Box full, releasing...")
			# release current box
			self.press(Button.X, wait=1)
			self.press(Direction.UP) # set cursor to party
			self.press(Button.A, wait=2)
			self.press(Button.R, wait=3)
			if self.release_boxes:
				self.ReleaseBox()
			self.hatched_box_num = 0;
			self.hatched_num -= 30;

			# open next box
			self.press(Button.R, wait=0.5)
			self.press(Button.B, wait=2)
			self.press(Button.B, wait=2)
			self.press(Direction.DOWN, wait=0.2) # set cursor to map
			self.press(Button.B, wait=1.5)

	def getNewEgg(self):
		self.flyToNursery()


		self.press(Button.A, duration=0.4, wait=self.stream_delay)
		egg_text = "Egg!"
		screen_text = self.getText(top=-130, bottom=30, left=250, right=250)
		if not egg_text in screen_text:
			print('egg not found')
			self.pressRep(Button.B, 10)
			# ensure sucessful arrival at nursery
			if not "Nursery" in screen_text:
				print("did not arrive at nursery: "+screen_text)
				self.flyToNursery()
			return False
		print('egg found')
		if self.party_num < 6:
			# just accept egg into party
			self.press(Button.A, wait=1)
			self.press(Button.A, wait=1)
			self.press(Button.A, wait=2)
			self.pressRep(Button.B, 16)
			self.party_num += 1
			print('party_num: ' + str(self.party_num))
		else:
			# substitute a hatched pokemon for the new egg
			pokemon_to_replace = 2 + (self.hatched_box_num % 5)
			print('replacing pokemon in position '+str(pokemon_to_replace))
			self.press(Button.A, wait=3)
			self.press(Button.A, wait=2)
			self.press(Button.A, duration=1, wait=0.3)
			self.press(Button.A, wait=2.5)
			self.pressRep(Direction.DOWN, pokemon_to_replace - 1) # select correct slot
			self.press(Button.A)
			self.pressRep(Button.B, 20)
			self.hatched_box_num += 1
		return True

	# check if an egg was hatched or if a battle has started
	# return true if there has been some interruption 
	def hatchEgg(self):
		message = self.getText(top=-130, bottom=30, left=250, right=250, 
				inverse=False, debug=False)
		if "Oh?" in message:
			print('egg hatching')
			self.press(Button.B, wait=14)
			self.pressRep(Button.B, 15, wait=2)
			self.hatched_num += 1
			return True
		elif "encountered" in message or "appeared" in message \
				or "Go" in message or "wild" in message:
			self.battle()
			return True
		elif self.isContainTemplate('battle_icon.png'):
			self.battle()
			return True
		else:
			return False

	def flyToNursery(self):
		self.hatchEgg()
		for i in range(5):
			self.press(Button.X, wait=(self.stream_delay + 0.5))
			text=self.getText()
			if not "OPTIONS" in text:
				if self.hatchEgg():
					continue
				else:
					print("Double-checking that menu is open")
					self.wait(0.5)
					text = self.getText(debug=True)
					if not "OPTIONS" in text:
						print("menu is not open...")
						if "Ball" in text:
							print("trying to catch for some reason?")
							self.pressRep(Button.B, 3, interval=0.5, wait=0.5)
							self.battle()
							return
						continue
			self.pressRep(Button.A, 20, wait=2) # fly to bridge field

			# walk to daycare and get an egg
			self.press(Direction.DOWN, duration=0.05, wait=0.5)
			self.press(Direction.DOWN, duration=0.8)
			self.press(Direction.LEFT, duration=0.2, wait=self.stream_delay)
			if self.hatchEgg():
				continue
			else:
				return
		print("Unexpected fatal error: cannot fly to nursery")
		self.finish()

	def battle(self):
		print("IN BATTLE")
		text = self.getText()
		while True:
			if self.isContainTemplate('battle_icon.png'):
				print("battle icon detected, making move")
				self.pressRep(Button.A, 5, interval=0.5, wait=0.5)
				self.wait(5)
				continue
			text = self.getText()
			if "Exp." in text or "learn" in text or "forget" in text:
				print("BATTLE HAS ENDED")
				self.pressRep(Button.A, 6, interval=0.5, wait=0.5)
				break
			self.wait(5)
		while "learn" in text or "forgot" in text or "move" in text or \
				"Level" in text or "Category" in text:
			self.pressRep(Button.A, 8, interval=0.5)
			self.wait(self.stream_delay)
			text = self.getText()
		print("Battle screen cleared...")