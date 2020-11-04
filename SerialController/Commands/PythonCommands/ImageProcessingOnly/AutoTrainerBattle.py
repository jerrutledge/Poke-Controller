#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.Reset import ResetGame
from Commands.Keys import KeyPress, Button, Direction, Stick

# Battle through trainers by setting up with Swords Dance/X-Attack
# Spams the pokemon's slot 1 attack. Assumes swords dance is in slot 2
class AutoTrainerBattle(ImageProcPythonCommand, ResetGame):
	NAME = 'Auto Trainer Battle'

	def __init__(self, cam):
		super().__init__(cam)
		self.use_swords_dance = True
		self.times_set_up = 1

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
	def bestAttack(self):
		attack_text = []
		attack_text.append(self.getText(top=437, bottom=225, left=920, right=152))
		attack_text.append(self.getText(508, 159, 920, 152))
		attack_text.append(self.getText(574, 88, 920, 152))
		attack_text.append(self.getText(645, 22, 920, 152))

		# if we are already dynamaxed, move text appears in white
		# OCR processing must invert the image to get a proper reading
		if ("Max" in attack_text[0] or "Max" in attack_text[1] or 
				"Max" in attack_text[2] or "Max" in attack_text[3]):
			attack_text.clear()
			attack_text.append(self.getText(437, 225, 920, 152, inverse=True))
			attack_text.append(self.getText(508, 159, 920, 152, inverse=True))
			attack_text.append(self.getText(574, 88, 920, 152, inverse=True))
			attack_text.append(self.getText(645, 22, 920, 152, inverse=True))

		pp_text = []
		pp_text.append(self.getText(top=437, bottom=225, left=1155, right=25, inverse=True))
		pp_text.append(self.getText(508, 159, 1155, 25, inverse=True))
		pp_text.append(self.getText(574, 88, 1155, 25, inverse=True))
		pp_text.append(self.getText(645, 22, 1155, 25, inverse=True))

		attacks = []
		for i in range(4):
			effectiveness = 0
			status = False
			name = " ".join(attack_text[i].split())
			try:
				cur_pp = int(pp_text[i].split("/")[0])
				max_pp = int(pp_text[i].split("/")[1])
			except ValueError:
				print("ValueError: couldn't determine PP for "+name)
				cur_pp = 0
				max_pp = 0
			if max_pp == 0:
				print("trying to read PP value again:")
				pp_text = []
				pp_text.append(self.getText(437, 225, 1155, 25, inverse=True, debug=True))
				pp_text.append(self.getText(508, 159, 1155, 25, inverse=True, debug=True))
				pp_text.append(self.getText(574, 88, 1155, 25, inverse=True, debug=True))
				pp_text.append(self.getText(645, 22, 1155, 25, inverse=True, debug=True))
				try:
					cur_pp = int(pp_text[i].split("/")[0])
					max_pp = int(pp_text[i].split("/")[1])
				except ValueError:
					print("still no OCR success, continuing...")
					cur_pp = 0
					max_pp = 0
			if cur_pp == 0:
				effectiveness = -1 # no pp - never select this move
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
			attacks.append({
				"name": name,
				"move_number": i,
				"effectiveness": effectiveness,
				"status_move": status,
				"pp_left": cur_pp,
				"max_pp": max_pp,
			})

		attacks.sort(key=lambda attack: attack["effectiveness"], reverse=True)

		best_attack = attacks[0]

		return best_attack, attacks
		


