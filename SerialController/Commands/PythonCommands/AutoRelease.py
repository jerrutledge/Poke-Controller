#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick
import re

JUDGEMENT_STRINGS = ["No good", "Decent", "Pretty good", \
				"Very good", "Fantastic", "Best"]

# auto releasing pokemons
# accepted IVs can be:
# 1. an array of literal judge values (i.e. ["Best", "No Good", etc.]) 
# 		where "*" = any value
# 2. ["N*"] meaning any permutation of N or more "Best" values where N
#		is a positive interger between 1 and 6
class AutoRelease(ImageProcPythonCommand):
	NAME = 'Release N Boxes'

	def __init__(self, cam):
		super().__init__(cam)
		self.row = 5
		self.col = 6
		self.cam = cam

		# release a number of boxes in a row
		self.boxes = 1
		self.ocr_fails = 0
		self.shinies = 0
		self.accepted_ivs = [
				['Best', 'Best', 'Best', 'Best', 'Best', 'Best'],
				['Best', 'Best', 'Best', '*', 'Best', 'Best'],
				['Best', 'Best', 'Best', 'Best', 'Best', '*'],
				['Best', 'Best', 'Best', 'Best', 'Best', 'No good'],
				['Best', 'No good', 'Best', 'Best', 'Best', 'Best'],
				['5*']
				]

	def do(self):
		if self.boxes > 1:
			print("Releasing " + str(self.boxes) + " boxes...")
		self.wait(0.5)

		for box in range(self.boxes):
			if self.boxes > 1:
				print("Releasing box #" + str(box + 1))
			self.ReleaseBox(accepted_ivs = self.accepted_ivs)

			# Go to next Box
			if box < (self.boxes - 1):
				self.press(Button.B, wait=2)
				self.press(Button.R, wait=3)
				self.press(Button.R, wait=0.2+self.stream_delay)

		# Return from pokemon box
		print("Released all boxes. OCR Fails: "+str(self.ocr_fails))
		if self.shinies > 0:
			print("SHINY POKEMON: "+str(self.shinies))
		self.press(Button.B, wait=2)
		self.press(Button.B, wait=2)
		self.press(Button.B, wait=1.5)

	def Release(self):
		self.press(Button.A, wait=0.4)
		self.press(Direction.UP, wait=0.1)
		self.press(Direction.UP, wait=0.1)
		self.press(Button.A, wait=1)
		self.press(Direction.UP, wait=0.1)
		self.press(Button.A, wait=1.4)
		self.press(Button.A)

	# marks with a red diamond, the sixth symbol
	def MarkPerfect(self):
		self.press(Button.A, wait=0.4)
		self.press(Direction.DOWN, wait=0.1)
		self.press(Direction.DOWN, wait=0.1)
		self.press(Direction.DOWN, wait=0.1)
		self.press(Button.A, wait=0.7)
		self.press(Direction.LEFT)
		self.press(Button.A, wait=0.2)
		self.press(Button.A, duration=0.2)
		self.press(Button.B, wait=0.2)

	def ReleaseBox(self, accepted_ivs=[['Best', 'Best', 'Best', 'Best', 'Best', 'Best']]):
		if self.cam.isOpened():
			# make sure we are viewing stats and not the pokemon model
			# usually the box automatically opens to the stats unless the top left 
			# Pokemon in the open box is an Egg?
			text = self.getText(20, -63, 878, 5)
			if not ("lv." in text or "Lv." in text or "Egg" in text):
				print('no lv. or egg in top: '+text)
				self.press(Button.PLUS, wait=self.stream_delay)
		shiny_count = 0
		for i in range(self.row):
			for j in range(self.col):
				if not self.cam.isOpened():
					self.Release()
				else:
					shiny = self.AssessPokemon(accepted_ivs)
					shiny_count += shiny

				if not j == self.col - 1:
					if i % 2 == 0:	self.press(Direction.RIGHT, wait=0.2)
					else:			self.press(Direction.LEFT, wait=0.2)
			if i < (self.row - 1):
				self.press(Direction.DOWN, wait=0.2)
		return shiny_count

	# Use OCR to assess the pokemon
	def AssessPokemon(self, accepted_ivs):
		# delay for video feed to update
		self.wait(self.stream_delay)
		shiny = False
		if self.isContainTemplate('status.png', threshold=0.7):
			shiny = self.isContainTemplate('shiny_mark.png', threshold=0.9)
			if shiny:
				print("SHINY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			# make sure the judge view is open
			text = self.getText(-30, 1, -300, 1)
			if "Judge" in text:
				print("Switching to judge view: " + text)
				self.press(Button.PLUS, wait=self.stream_delay)
			# use OCR to check for perfect ivs
			stats = []
			ocr_fail = True
			ivs_are_acceptable = False
			# there is a small chance the OCR will fail
			# therefore we check a max three times, breaking
			# if the format is correct
			for k in range(3):
				text = self.getText(135, 350, 990, 1)
				stats = text.split('\n')
				# remove all entries that aren't judge strings
				stats = [x for x in stats if x in JUDGEMENT_STRINGS]
				print("stat reading="+str(stats)+"; ")
				if len(stats) == 6 and set(stats).issubset(JUDGEMENT_STRINGS):
					# ocr has read correct format!
					ocr_fail = False
					break
				if k == 2:
					print("OCR fail")
			if ocr_fail:
				print("OCR Fail, moving on...")
				self.ocr_fails += 1
			elif stats in accepted_ivs:
				ivs_are_acceptable = True
			else:
				for iv_array in accepted_ivs:
					# e.g. ["5*"]
					if len(iv_array) == 1 and isinstance(iv_array[0], str):
						match = re.search(r"^(\d)\*$", iv_array[0])
						if match:
							num_of_bests = int(match.group(1))
							print("checking for "+str(num_of_bests)+" Bests based on string "+
									iv_array[0] + " found: "+str(stats.count("Best")))
							if stats.count("Best") >= num_of_bests:
								ivs_are_acceptable = True
								break
					# e.g. ['Best', 'Best', 'Best', '*', 'Best', 'Best']
					elif len(iv_array) == 6:
						matching_array = []
						for i in range(6):
							if iv_array[i] == "*":
								matching_array.append(stats[i])
							else:
								matching_array.append(iv_array[i])
						if stats == matching_array:
							ivs_are_acceptable = True
							break

			if ivs_are_acceptable:
				# mark a perfect IV pokemon
				has_perfect_ivs = stats == ['Best', 'Best', 'Best',
						'Best', 'Best', 'Best']
				if has_perfect_ivs:
					print("Perfect IVs!")
					self.MarkPerfect()
			# if not shiny and non-acccpeted IVs, release
			elif not shiny:
				# Release a pokemon
				self.Release()
		else:
			text = self.getText(1, -70, 870, 1)
			if "Egg" in text:
				print("This is an Egg, skipping...")
			else:
				print("No Pokemon, skipping...")

		return 1 if shiny else 0