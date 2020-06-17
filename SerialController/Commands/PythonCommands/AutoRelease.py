#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick

# auto releaseing pokemons
class AutoRelease(ImageProcPythonCommand):
	NAME = 'Release N Boxes'

	def __init__(self, cam):
		super().__init__(cam)
		self.row = 5
		self.col = 6
		self.cam = cam

		# release a number of boxes in a row
		self.boxes = 2
		self.ocr_fails = 0
		self.shinies = 0
		self.accepted_ivs = [['Best', 'Best', 'Best', 'Best', 'Best', 'Best'], \
			['Best', 'Best', 'Best', 'Best', 'Best', 'No good']]

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
				self.press(Button.R, wait=0.2)

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
			text = self.getText(400, -440, 880, -990)
			if "Ability" in text:
				self.press(Button.PLUS, wait=self.stream_delay)
			# use OCR to check for perfect ivs
			stats = []
			judgements = ["No good", "Decent", "Pretty good", \
				"Very good", "Fantastic", "Best"]
			ocr_fail = True
			# there is a small chance the OCR will fail
			# therefore we check a max three times, breaking
			# if the format is correct
			for k in range(3):
				text = self.getText(135, 350, 990, 1)
				stats = text.split('\n')
				while '' in stats:
					stats.remove('')
				print("stats="+str(stats)+"; "+(str(stats in accepted_ivs)))
				if len(stats) == 6 and set(stats).issubset(judgements):
					# ocr has read correct format!
					ocr_fail = False
					break
				if k == 2:
					print("OCR fail")
			if ocr_fail:
				print("OCR Fail, moving on...")
				self.ocr_fails += 1
			elif stats in accepted_ivs:
				# mark a perfect IV pokemon
				perfect_iv = stats == ['Best', 'Best', 'Best', \
						'Best', 'Best', 'Best']
				if perfect_iv:
					print("Perfect IVs!")
					self.MarkPerfect()
			# if not shiny and non-acccpeted IVs, release
			elif not shiny:
				# Release a pokemon
				self.Release()

		return 1 if shiny else 0