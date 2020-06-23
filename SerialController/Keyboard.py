#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pynput.keyboard import Key, Listener
from Commands.Keys import KeyPress, Button, Direction, Stick

# This handles keyboard interactions
class Keyboard:
	def __init__(self):
		self.listener = Listener(
			on_press=self.on_press,
			on_release=self.on_release)
	
	def listen(self):
		self.listener.start()
	
	def stop(self):
		self.listener.stop()
	
	def on_press(self, key):
		try:
			print('alphanumeric key {0} pressed'.format(key.char))
		except AttributeError:
			print('special key {0} pressed'.format(key))

	def on_release(self, key):
		print('{0} released'.format(key))

# This regards a keyboard inputs as Switch controller
class SwitchKeyboardController(Keyboard):
	def __init__(self, keyPress):
		super(SwitchKeyboardController, self).__init__()
		self.key = keyPress
		self.holding = []
		self.holdingDir = []

		self.key_map = {
			'y': Button.Y,
			'b': Button.B,
			'x': Button.X,
			'a': Button.A,
			'l': Button.L,
			'r': Button.R,
			'k': Button.ZL,
			'e': Button.ZR,
			'm': Button.MINUS,
			'p': Button.PLUS,
			'q': Button.LCLICK,
			'w': Button.RCLICK,
			'h': Button.HOME,
			'c': Button.CAPTURE,
			Key.up: Direction.UP,
			Key.right: Direction.RIGHT,
			Key.down: Direction.DOWN,
			Key.left: Direction.LEFT,
		}

		self.current_direction = None

	def on_press(self, key):

		if key is None:
			print('unknown key has input')

		try:
			if self.key_map[key.char] in self.holding:
				return

			for k in self.key_map.keys():
				if key.char == k:
					self.holding.append(self.key_map[key.char])
					# every time we input something to the key module
					# we pass along all the inputs we are currently holding
					self.key.input(self.holding + ([self.current_direction] \
						if self.current_direction != None else []))
		
		# for special keys
		except AttributeError:
			if key in self.holdingDir:
				return

			for k in self.key_map.keys():
				if key == k:
					self.holdingDir.append(key)
					if self.inputDir(self.holdingDir):
						self.key.input(self.holding + [self.current_direction])

	def on_release(self, key):

		if key is None:
			print('unknown key has released')

		try:
			if self.key_map[key.char] in self.holding:
				self.holding.remove(self.key_map[key.char])
				self.key.inputEnd(self.key_map[key.char])
		
		except AttributeError:
			if key in self.holdingDir:
				self.holdingDir.remove(key)
				if self.inputDir(self.holdingDir):
					self.key.input(self.holding + [self.current_direction])
	
	# this function will update the self.current_direction variable
	# it will return true if the direction needs to be updated
	def inputDir(self, dirs):
		# first, let's clean the input
		# accept the last two non-opposing arrow key inputs
		valid_dirs = []
		for i in range(1, len(dirs) + 1):
			if dirs[-i] == Key.up and (Key.down not in valid_dirs):
				valid_dirs.append(Key.up)
			if dirs[-i] == Key.down and (Key.up not in valid_dirs):
				valid_dirs.append(Key.down)
			if dirs[-i] == Key.left and (Key.right not in valid_dirs):
				valid_dirs.append(Key.left)
			if dirs[-i] == Key.right and (Key.left not in valid_dirs):
				valid_dirs.append(Key.right)

		if len(valid_dirs) == 0:
			# stop holding the current direction
			if not self.current_direction == None:
				self.key.inputEnd(self.current_direction)
			self.current_direction = None
			return False

		new_direction = None
		if len(valid_dirs) == 1:
			new_direction = self.key_map[valid_dirs[0]]
		elif len(valid_dirs) > 1:
			if Key.up in valid_dirs:
				if Key.right in valid_dirs:	new_direction = Direction.UP_RIGHT
				elif Key.left in valid_dirs:	new_direction = Direction.UP_LEFT
			elif Key.down in valid_dirs:
				if Key.left in valid_dirs:	new_direction = Direction.DOWN_LEFT
				elif Key.right in valid_dirs:	new_direction = Direction.DOWN_RIGHT

		if new_direction == None:
			print('error: could not determine direction from key input. valid_dirs=' \
				+ str(valid_dirs))
			return False
		elif new_direction == self.current_direction:
			return False
		self.current_direction = new_direction
		return True