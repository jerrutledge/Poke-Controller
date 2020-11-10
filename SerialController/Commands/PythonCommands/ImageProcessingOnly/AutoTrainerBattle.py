#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.Reset import ResetGame
from Commands.Keys import KeyPress, Button, Direction, Stick
import json

# Battle through trainers by setting up with Swords Dance/X-Attack
# Spams the pokemon's slot 1 attack. Assumes swords dance is in slot 2
class AutoTrainerBattle(ImageProcPythonCommand, ResetGame):
	NAME = 'Auto Trainer Battle'

	def __init__(self, cam):
		super().__init__(cam)
		self.use_swords_dance = True
		self.times_set_up = 1
		self.pokemonMoves = {}

		try:
			with open('moves.json') as move_data:
				self.pokemonMoves = json.load(move_data)
		except:
			print("Couldn't load moves file.")

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
			if "Please select a Battle" in text or "Would you like to choose" in text:
				for _ in range(3):
					self.pressRep(Button.A, 2)
					self.press(Direction.DOWN)
				self.press(Button.A)
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
	
	# determine the best attacking move - returns a number from 1 to 4.
	def bestAttack(self, givenPokemon=None, turn=2):
		move_lr = [920, 152]
		pp_lr = [1155, 25]
		dynamaxed = False

		tb = [
			{
				"top": 437,
				"bottom": 225
			},
			{
				"top": 508,
				"bottom": 159
			},
			{
				"top": 574,
				"bottom": 88
			},
			{
				"top": 645,
				"bottom": 22
			},
		]
		attack_text = []

		attack_text.append(self.getText(tb[0]["top"], tb[0]["bottom"], move_lr[0], move_lr[1]))
		attack_text.append(self.getText(tb[1]["top"], tb[1]["bottom"], move_lr[0], move_lr[1]))
		attack_text.append(self.getText(tb[2]["top"], tb[2]["bottom"], move_lr[0], move_lr[1]))
		attack_text.append(self.getText(tb[3]["top"], tb[3]["bottom"], move_lr[0], move_lr[1]))

		# if we are already dynamaxed, move text appears in white
		# OCR processing must invert the image to get a proper reading
		if ("Max" in attack_text[0] or "Max" in attack_text[1] or 
				"Max" in attack_text[2] or "Max" in attack_text[3]):
			dynamaxed = True
			attack_text.clear()
			attack_text.append(self.getText(tb[0]["top"], tb[0]["bottom"], move_lr[0], 
					move_lr[1], inverse=True))
			attack_text.append(self.getText(tb[1]["top"], tb[1]["bottom"], move_lr[0], 
					move_lr[1], inverse=True))
			attack_text.append(self.getText(tb[2]["top"], tb[2]["bottom"], move_lr[0], 
					move_lr[1], inverse=True))
			attack_text.append(self.getText(tb[3]["top"], tb[3]["bottom"], move_lr[0], 
					move_lr[1], inverse=True))


		# determine whether we can dynamax
		dynamax = False
		if dynamaxed:
			print("Turn "+str(turn)+": currently Dynamaxed")
		else:
			dynamax = self.isContainTemplate("dynamax.png")
			if dynamax:
				print("Turn "+str(turn)+": Dynamax Detected!")
			else:
				if self.isContainTemplate("dynamax-not-ready.png"):
					print("Turn "+str(turn)+": Dynamax not ready yet!")
				else:
					print("Turn "+str(turn)+": Dynamax impossible")
		
		attacks = []
		for i in range(4):
			effectiveness = 0
			status = False
			cur_pp = 0
			name = " ".join(attack_text[i].split())
			cur_move = None
			if givenPokemon and givenPokemon["moves"]:
				cur_move = givenPokemon["moves"][i]
			else:
				for move in self.pokemonMoves:
					if move in name:
						cur_move = self.pokemonMoves[move]
						print("Identified "+cur_move["moveName"])
						cur_move["move_number"] = i
						break
			if cur_move:
				name = cur_move["moveName"]
			else:
				print("Couldn't identify move '" + name + "'")
			# determine pp value
			cur_pp = -1
			for j in range(3):
				pp_text = self.getText(tb[i]["top"]+6, tb[i]["bottom"]+6, 
						pp_lr[0], pp_lr[1], inverse=True)
				pp_text = "".join(pp_text.split())
				try:
					cur_pp = int(pp_text.split("/")[0])
				except (ValueError, IndexError) as e:
					print(str(e) + ": "+name+" PP unknown")
					cur_pp = -1
				if cur_pp == -1:
					print("OCR Fail. PP = "+pp_text+"")
				else:
					break
			if cur_move:
				cur_move["PP"] = cur_pp
			# determine through OCR whether the move is super effective or not
			if cur_pp <= 0:
				effectiveness = -1 # no pp - never select this move
			elif cur_move and cur_move["useless"]:
				effectiveness = 0
			elif ("Super effective" in attack_text[i] or \
					("Super e" in attack_text[i]) or \
					("Super" in attack_text[i] and "Max" in attack_text[i])):
				effectiveness = 3
			elif ("Not very effective" in attack_text[i]):
				effectiveness = 1
			elif ("Effective" in attack_text[i]):
				effectiveness = 2
			elif ("No effect" in attack_text[i]):
				effectiveness = -1 # move has no effect - never select this move
			else:
				# sometimes, pokemon have less than 4 moves
				# if the OCR doesn't see a long enough string, it's not a move
				if len("".join(attack_text[i].strip())) <= 3:
					effectiveness = -2
				else:
					# this is probably a status move
					status = True
			# multiply the effectiveness of the move by what we know about game state
			if (not (dynamax or dynamaxed)) and cur_move and cur_move["oneUse"]:
				if turn == 1:
					effectiveness = 50000
				else:
					effectiveness = 0
			elif cur_move and effectiveness > 0:
				# apply STAB
				if givenPokemon and cur_move["moveType"] in givenPokemon["types"]:
					effectiveness = int(effectiveness * 1.5)
				# put in relative value of attack stat
				if givenPokemon and "stats" in givenPokemon:
					if cur_move["moveCategory"] == "Physical":
						effectiveness *= givenPokemon["stats"][1]
					if cur_move["moveCategory"] == "Special":
						effectiveness *= givenPokemon["stats"][3]
				# Is it a max move
				if dynamax or dynamaxed:
					effectiveness *= int(cur_move["maxMovePower"])
					cur_move["effectiveness"] = int(effectiveness)
				else:
					accuracy = min(cur_move["accuracy"], 100) / 100
					accuracy = accuracy * cur_move["averageEffectiveness"]
					effectiveness *= cur_move["power"] * accuracy / cur_move["turnsTaken"]
				# if there are two moves of equal power, we slightly prefer the one with more pp
				if cur_pp < 5:
					effectiveness -= 5 - cur_pp
			# append what we know about the move to our array
			if cur_move:
				cur_move["effectiveness"] = effectiveness
				attacks.append(cur_move)
			else:
				attacks.append({
					"moveName": name,
					"move_number": i,
					"effectiveness": effectiveness,
					"status_move": status,
					"PP": cur_pp,
				})
			print(name+" effectiveness: "+str(effectiveness))

		attacks.sort(key=lambda attack: attack["effectiveness"], reverse=True)

		best_attack = attacks[0]

		return best_attack, attacks, dynamax
		
class testMoveSelector(AutoTrainerBattle):
	NAME = 'Test Move Selector'
	def do(self):
		for i in range(50):
			print("TRY #"+str(i))
			self.bestAttack()
			self.wait(0.5)

