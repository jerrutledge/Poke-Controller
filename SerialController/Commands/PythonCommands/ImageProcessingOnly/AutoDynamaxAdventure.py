#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, pokemonTypes, ImageProcPythonCommand
from Commands.PythonCommands.ImageProcessingOnly.AutoTrainerBattle import AutoTrainerBattle
from Commands.Keys import KeyPress, Button, Direction, Stick
import re

# Battle through trainers by setting up with Swords Dance/X-Attack
# Spams the Pokémon's slot 1 attack. Assumes swords dance is in slot 2
class AutoDynamaxAdventure(AutoTrainerBattle):
	NAME = 'Auto Dynamax Adventure'

	def __init__(self, cam):
		super().__init__(cam)
		self.keep_non_shiny_legend = False
		self.current_hp = 0
		self.max_hp = 0
		self.lowest_pp = 30
		self.boss_type = 'None'
		self.turn_num = 0

	def do(self):
		while True:
			# reset the variables
			self.current_hp = 0
			self.max_hp = 0
			self.lowest_pp = 30
			self.boss_type = 'None'

			# yes, I'd like to go on an adventure
			self.pressRep(Button.A, 4, duration=0.3, interval=0.4, wait=0.5)
			# no, I'm not looking for a particular pokemon
			self.pressRep(Button.B, 3, duration=0.3, interval=0.4, wait=1)
			# yes, I'd like to save the game
			self.pressRep(Button.A, 4, duration=0.3, interval=0.4, wait=2)
			# no, I don't want to invite anyone
			self.press(Direction.DOWN)
			self.press(Button.A, wait=2)
			# choose your first pokemon
			self.press(Button.A) # to dismiss text
			self.wait(self.stream_delay)
			text = self.getText()
			text = " ".join(text.split())
			print("TEXT: "+text)
			print("choose pokemon 1")
			self.press(Button.A)

			# start adventuring until it's over
			self.maxAdventureCycle()

			# view pokemon summary
			self.press(Button.A, wait=0.5)
			self.press(Direction.DOWN)
			self.press(Button.A, wait=0.8)

			# scroll
			shinies = []
			for i in range(4):
				self.wait(self.stream_delay)
				if (self.isContainTemplate("shiny_mark.png")):
					print("SHINY!!! Pokemon #" + str(i+1))
					shinies.append(i)
				self.press(Direction.DOWN, wait=0.5)
			# exit from pokemon summary
			self.press(Button.B, wait=2.3)
			if len(shinies) > 1:
				print("wow 2+ shinies!!! Gotta stop")
				break
			elif len(shinies) > 0:
				print("found a shiny in slot " + str(shinies[0] + 1))
				self.press(Direction.UP, duration=1)
				self.pressRep(Direction.DOWN, shinies[0])
				self.pressRep(Button.A, 5)
			else:
				print("Not selecting any Pokemon...")
				self.press(Button.B, duration=0.9, wait=0.5)
				self.press(Button.A)
			self.pressRep(Button.B, 5, interval=1)
			self.press(Button.A)
			self.pressRep(Button.B, 30, interval=0.4)
	
	def maxAdventureCycle(self):
		for _ in range(10000):
			text = self.getText()
			text = " ".join(text.split())
			
			# update our current HP, if possible
			hp_text = (self.getText(664, 24, 72, -222)).strip()
			if (re.search("^\d+\/\d+$", hp_text) is not None):
				print("Update HP: ("+hp_text+")")
				hp_text = hp_text.split("/")
				self.current_hp = int(hp_text[0])
				self.max_hp = int(hp_text[1])
			
			# try to determine what to do from the text
			boss_text_regex = re.search("There’s a strong (.*)-type reaction", text)
			if boss_text_regex is not None:
				if boss_text_regex.group(1).upper() in pokemonTypes:
					self.boss_type = boss_text_regex.group(1).upper()
					print("Boss type: "+self.boss_type)
				else:
					print("No...")
			if "Catch" in text:
				print(text + " -- Catching Pokémon...")
				self.pressRep(Button.A, 10)
				# break
			elif self.isContainTemplate('cheer_icon.png'):
				print("Cheer Icon - cheering on!")
				self.pressRep(Button.A, 3)
				self.wait(2)
			elif self.isContainTemplate('battle_icon.png'):
				print("Battle Icon - selecting move")
				self.press(Button.A, wait=0.2)
				# center the cursor on the first move
				self.press(Direction.RIGHT, duration=1) # deselect dynamax
				self.press(Direction.UP, duration=1)
				# determine the best move via OCR
				best_attack, attacks = self.bestAttack()
				print(attacks)
				print("Choose move#" + str(best_attack["move_number"] + 1) + ": " + best_attack["name"])
				# move up from the bottom in case there are less than 4 moves
				self.pressRep(Direction.UP, (4 - best_attack["move_number"]) % 4)
				self.press(Direction.LEFT)
				self.pressRep(Button.A, 4, interval=0.3)
				self.press(Direction.RIGHT)
				self.pressRep(Button.A, 5, interval=0.5)
				# update our lowest pp number
				self.lowest_pp = min(best_attack["pp_left"], self.lowest_pp)
			elif "Caught" in text:
				print("Final screen TEXT: " + text)
				break
			elif "hold one item" in text:
				print("Item offered! Choosing item")
				self.pressRep(Button.A, 5)
			elif "Which path would you like to take" in text:
				print("Choosing path? TEXT:" + text)
				self.pressRep(Button.A, 3, wait=2)
			elif "Are you interested in swapping your current" in text or \
					"One Trainer can choose to put the Pokémon" in text:
				print("New Pokémon offer! TEXT:" + text)
				if self.current_hp < self.max_hp/2 or self.lowest_pp < 3:
					print("Accepting new Pokémon (HP: "+str(self.current_hp)+"/"
							+str(self.max_hp)+"; PP: "+str(self.lowest_pp)+")")
					self.press(Button.A)
				else:
					print("Rejecting new Pokémon (HP: "+str(self.current_hp)+"/"
							+str(self.max_hp)+"; PP: "+str(self.lowest_pp)+")")
					self.press(Button.B)
			else:
				print("TEXT: " + text)
			self.wait(0.3)

