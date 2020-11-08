#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, pokemonTypes, ImageProcPythonCommand
from Commands.PythonCommands.ImageProcessingOnly.AutoTrainerBattle import AutoTrainerBattle
from Commands.Keys import KeyPress, Button, Direction, Stick
import re
import json
import math

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
		self.next_pokemon = ""
		self.pokemonData = None
		self.currentPokemon = None

		with open('pokemon-data.json') as poke_data:
			self.pokemonData = json.load(poke_data)

	def do(self):
		while True:
			# reset the variables
			self.current_hp = 0
			self.max_hp = 0
			self.lowest_pp = 30
			self.boss_type = 'None'
			self.turn_num = 0
			self.next_pokemon = None
			self.currentPokemon = None

			# yes, I'd like to go on an adventure
			self.pressRep(Button.A, 3, duration=0.5, interval=0.3, wait=0.5)
			# no, I'm not looking for a particular pokemon
			self.pressRep(Button.B, 3, duration=0.5, interval=0.3, wait=0.5)
			# yes, I'd like to save the game
			self.pressRep(Button.A, 3, duration=0.5, interval=0.3, wait=2.4)
			# no, I don't want to invite anyone
			self.press(Direction.DOWN)
			self.press(Button.A, wait=1.5)
			# choose your first pokemon
			self.wait(self.stream_delay)
			if self.pokemonData is not None:
				pokemon_options = []
				pokemon_abilities = []
				values = []
				pokemon_options.append(" ".join(self.getText(205, -240, 620, -850, inverse=True).split()))
				pokemon_abilities.append(" ".join(self.getText(240, -270, 620, -850, inverse=True).split()))
				pokemon_options.append(" ".join(self.getText(395, -430, 620, -850).split()))
				pokemon_abilities.append(" ".join(self.getText(430, -460, 620, -850).split()))
				pokemon_options.append(" ".join(self.getText(580, -615, 620, -850).split()))
				pokemon_abilities.append(" ".join(self.getText(615, -645, 620, -850).split()))
				print(pokemon_options)
				print(pokemon_abilities)
				for pokemon in pokemon_options:
					if pokemon in self.pokemonData:
						values.append(self.pokemonData[pokemon]["value"])
					else:
						print("couldn't find "+pokemon)
						values.append(0)
				print(values)
				if max(values) > 0:
					choice = values.index(max(values))
					print("Choosing pokemon #" + str(choice + 1) + ", " + pokemon_options[choice])
					self.pressRep(Direction.DOWN, choice)
					self.currentPokemon = self.pokemonData[pokemon_options[choice]]
					self.initializeCurrentPokemon()
				else:
					print("OCR Fail: Max value: "+str(max(values))+". Choose pokemon 1")
			self.press(Button.A)

			# start adventuring until it's over
			self.maxAdventureCycle()

			# view pokemon summary
			self.press(Button.A, wait=0.5)
			self.press(Direction.DOWN)
			self.press(Button.A, wait=1.4)

			# scroll
			shinies = []
			catches = []
			for i in range(4):
				self.wait(self.stream_delay)
				poke_name = self.getText(30, -80, 765, -940, inverse=True)
				poke_name = " ".join(poke_name.strip())
				if poke_name not in catches:
					catches.append(poke_name)
					self.camera.saveCapture(suffix=" ("+str(i)+")")
					if (self.isContainTemplate("shiny_mark.png")):
						print("SHINY!!! Pokemon #" + str(i+1))
						shinies.append(i)
					self.press(Direction.DOWN, wait=0.5)
				else:
					break
			# exit from pokemon summary
			self.press(Button.B, wait=2.3)
			print("Options: "+str(catches))
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
			self.pressRep(Button.B, 4, interval=0.5)
			self.press(Button.A)
			self.pressRep(Button.B, 30, interval=0.4)
	
	def maxAdventureCycle(self):
		for _ in range(10000):
			text = self.getText()
			text = " ".join(text.split())

			# double check the textbox in the lower part of the screen
			small_text = self.getText(top=-130, bottom=30, left=50, right=50, 
				inverse=False, debug=False)
			small_text = " ".join(small_text.split())
			if len(text) < len(small_text):
				text = small_text
			
			# update our current HP, if possible
			hp_text = (self.getText(664, 24, 72, -222)).strip()
			if (re.search("^\d+\/\d+$", hp_text) is not None):
				hp_text = hp_text.split("/")
				new_hp = int(hp_text[0])
				new_max_hp = int(hp_text[1])
				if not (new_hp == self.current_hp) or not (new_max_hp == self.max_hp):
					print("Update HP: "+str(hp_text[0]) + "/" + str(hp_text[1]))
					self.current_hp = new_hp
					self.max_hp = new_max_hp
			
			# update the game state via text
			boss_text_regex = re.search("There’s a strong (.*)-type reaction", text)
			next_pokemon_regex = re.search("^(.*) is weak! Throw a Poké Ball now!", text)
			cur_pokemon_regex = re.search("Go! (.*)!", text)
			if boss_text_regex is not None:
				if boss_text_regex.group(1).upper() in pokemonTypes:
					self.boss_type = boss_text_regex.group(1).upper()
					print("Boss type: "+self.boss_type)
					self.wait(2)
					continue
				else:
					print("Boss type? No...")
			elif next_pokemon_regex is not None:
				next_pokemon_text = next_pokemon_regex.group(1)
				print("TEXT next pokemon: "+text)
				if next_pokemon_text in self.pokemonData:
					self.next_pokemon = self.pokemonData[next_pokemon_text]
					print(next_pokemon_text + " - " + str(self.next_pokemon["types"]))
					self.wait(2.2)
					text = "Catch"
				else:
					print("couldn't identify pokemon '"+next_pokemon_text+"'")
			elif cur_pokemon_regex is not None:
				cur_pokemon_text = cur_pokemon_regex.group(1)
				print("TEXT sending out pokemon: "+text)
				if cur_pokemon_text in self.pokemonData:
					# check to make sure we're not overwriting our current data
					if self.currentPokemon and cur_pokemon_text == self.currentPokemon["name"]:
						print("Current pokemon is already "+cur_pokemon_text)
						continue
					self.currentPokemon = self.pokemonData[cur_pokemon_text]
					self.initializeCurrentPokemon()
					print(cur_pokemon_text + " - " + str(self.currentPokemon["types"]))
					self.wait(3)
					continue
				else:
					print("couldn't identify pokemon '"+cur_pokemon_text+"'")
			
			# work out what action to take based on the text
			if "Catch" in text:
				print(text + " -- Catching Pokémon...")
				# since we know the battle is over now, the next battle will start on turn 1
				self.turn_num = 1
				self.pressRep(Button.A, 10)
				self.wait(5)
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
				if self.currentPokemon is not None:
					# if we know them, provide attacks
					best_attack, attacks, dynamax = self.bestAttack(
							givenPokemon=self.currentPokemon, turn=self.turn_num)
				else:
					best_attack, attacks, dynamax = self.bestAttack(turn=self.turn_num)
				print("Choose move#" + str(best_attack["move_number"] + 1) + ": " + best_attack["moveName"])
				# move up from the bottom in case there are less than 4 moves
				self.pressRep(Direction.UP, (4 - best_attack["move_number"]) % 4)
				if dynamax:
					self.press(Direction.LEFT)
				self.pressRep(Button.A, 6, interval=0.3)
				# in case we are targeting ourselves for some reason
				self.press(Direction.UP)
				self.pressRep(Button.A, 6, interval=0.3)
				# update our lowest pp number
				self.lowest_pp = min(best_attack["PP"] - 1, self.lowest_pp)
				if self.currentPokemon:
					self.currentPokemon["moves"][best_attack["move_number"]]["PP"] -= 1
				if self.turn_num:
					self.turn_num += 1
				self.wait(4)
			elif "Caught" in text:
				print("Final screen TEXT: " + text)
				break
			elif "hold one item" in text:
				print("Item offered! Choosing item")
				self.pressRep(Button.A, 10, interval=0.5)
			elif "Which path would you like to take" in text:
				print("Choosing path? TEXT:" + text)
				self.pressRep(Button.A, 3, wait=2)
			elif "Are you interested in swapping your current" in text or \
					"One Trainer can choose to put the Pokémon" in text:
				print("New Pokémon offer! TEXT:" + text)
				change_pokemon = False
				if self.next_pokemon is None or self.currentPokemon is None:
					# if there is an OCR fail or otherwise the pokemon is unknown
					if self.current_hp < self.max_hp/2 or self.lowest_pp < 3:
						print("Accepting new Pokémon (HP: "+str(self.current_hp)+"/"
								+str(self.max_hp)+"; PP: "+str(self.lowest_pp)+")")
						change_pokemon = True
						self.press(Button.A)
					else:
						print("Rejecting new Pokémon (HP: "+str(self.current_hp)+"/"
								+str(self.max_hp)+"; PP: "+str(self.lowest_pp)+")")
						self.press(Button.B)
				else:
					print(self.currentPokemon)
					print(self.next_pokemon)
					# do math to see whether the new pokemon should be taken
					hp_modifier = math.floor((1 + (self.current_hp / self.max_hp)) / 2)
					temp_old_val = self.currentPokemon["value"] * hp_modifier
					if self.lowest_pp < 3:
						temp_old_val = min(temp_old_val * 0.5, 400)
					temp_new_val = self.next_pokemon["value"]
					if self.boss_type:
						if self.boss_type in self.next_pokemon["offensiveAdvantages"]:
							temp_new_val = temp_new_val + 100
						if self.boss_type in self.next_pokemon["defensiveAdvantages"]:
							temp_new_val = temp_new_val + 120
						if self.boss_type in self.currentPokemon["offensiveAdvantages"]:
							temp_old_val = temp_old_val + 100
						if self.boss_type in self.currentPokemon["defensiveAdvantages"]:
							temp_old_val = temp_old_val + 120
					if temp_old_val < temp_new_val:
						print("Accepting new Pokémon (Value: "+str(temp_new_val)+" > "
								+str(temp_old_val)+")")
						self.press(Button.A)
					else:
						print("Rejecting new Pokémon (Value: "+str(temp_new_val)+" < "
								+str(temp_old_val)+")")
						self.press(Button.B)
				if change_pokemon:
					self.press(Button.A)
					self.current_hp = 100
					self.max_hp = 100
					self.lowest_pp = 30
					self.currentPokemon = self.next_pokemon
					if (self.currentPokemon is not None):
						self.initializeCurrentPokemon()
				self.next_pokemon = None
				self.wait(6)
			else:
				print("TEXT: " + text)
			self.wait(0.2)

	# when you get a new pokemon, update PP information
	def initializeCurrentPokemon(self):
		self.lowest_pp = 30
		i = 0
		for move in self.currentPokemon["moves"]:
			move["PP"] = int(move["maxPP"])
			move["move_number"] = i
			self.lowest_pp = min(move["PP"], self.lowest_pp)
			i += 1