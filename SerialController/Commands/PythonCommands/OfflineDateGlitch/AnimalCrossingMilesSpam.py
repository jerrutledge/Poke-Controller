#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.OfflineDateGlitch.OfflineDateGlitchBase import OfflineDateGlitchCommand
from Commands.Keys import KeyPress, Button, Direction, Stick
import math
from datetime import datetime
import turnips

# Check the nook terminal, fast forward a day, repeat
# assumes your house is to the right of the town hall
class ACNH_Infinite_Miles(OfflineDateGlitchCommand):
	NAME = 'ACNH Infinite Miles'

	def __init__(self, cam):
		super().__init__(cam)

	def do(self):
		self.acnh_reset()
		while True:
			print("walking to Nook terminal...")
			self.press(Direction.DOWN, duration=3.8)
			self.press(Direction.LEFT, duration=0.6)
			self.press(Direction.DOWN, duration=0.4)
			self.press(Direction.LEFT, duration=0.7)
			self.press(Direction.UP, duration=0.8)
			self.press(Button.A)
			self.wait(9.5)
			self.press(Direction.UP, duration=0.4)
			self.press(Direction.RIGHT, duration=1)
			self.press(Button.A)
			self.pressRep(Button.B, 5, wait=0.5)
			self.wait(self.stream_delay)
			text = self.getText(-248, 70, 258, 258)
			if "Nook" in text and "Stop," in text:
				print("collecting miles... ")
				self.pressRep(Button.B, 15, interval=0.5)

				print("advancing date and resetting...")
				self.changeDay(False)
				self.acnh_reset()
			else:
				print("Nook terminal was not reached. resetting...")
				print("error text: "+text)
				self.pressRep(Button.B, 5, interval = 0.5)
				self.acnh_reset(wait_for_Isabelle=False)

	def acnh_reset(self, wait_for_Isabelle=True):
		self.press(Button.MINUS)
		self.pressRep(Button.B, 3, interval=0.5, wait=0.8)
		# select yes, save and quit
		self.press(Button.A)
		self.pressRep(Button.B, 20, interval=0.5)
		print("waiting for title screen to load...")
		if wait_for_Isabelle:
			self.wait(20)
		else:
			self.wait(16)
		# dismiss the title screen asap
		self.pressRep(Button.A, 36, interval=0.5)
		if wait_for_Isabelle:
			print("waiting for Isabelle to start talking...")
			for i in range(25):
				self.wait(0.5)
				text_box_string = self.getText(-248, 70, 258, 258)
				if "everyone!" in text_box_string:
					print("Isabelle's greeting detected!")
					break
				print("try #" + str(i) + " text: " + text_box_string.replace("\n", ""))
			self.pressRep(Button.B, 36, interval=0.5)
			self.wait(8)
		else:
			self.wait(12)

class ACNH_Open_Mail(OfflineDateGlitchCommand):
	NAME = 'ACNH Open Mail'

	def __init__(self, cam):
		super().__init__(cam)
		self.open_presents = True

	def do(self):
		while True:
			if self.open_presents:
				self.press(Button.A, wait=0.9)
				self.press(Button.A, wait=0.9)
			self.press(Button.A, wait=0.9)
			self.press(Button.MINUS, wait=0.3)
			self.press(Direction.UP, wait=0.3)
			self.press(Button.A, wait=0.9)

class ACNH_Turnip_Price_Seeker(ACNH_Infinite_Miles):
	NAME = 'ACNH Turnip Price Seeker'

	def __init__(self, cam):
		super().__init__(cam)
		# condition for stopping the search
		self.min_price = 610
		# if true, lowers this min price once per weekly reset
		self.adaptive_price = 5

	def do(self):
		print("Beginning to search for a turnip buying price larger than " + str(self.min_price))
		prices = {}
		weekly_times = {}
		# set the dictionary of times to use
		for day in range(6):
			# morning time
			date = datetime(2020,5,4+day,hour=8,minute=1)
			weekly_times[2 + 2*day] = date
			# afternoon time
			date = date.replace(hour=12) # set hour to 12
			weekly_times[3 + 2*day] = date
		# begin searching week by week
		while True:
			price_model = turnips.meta.MetaModel.blank()
			for time in weekly_times:
				day_of_the_week = weekly_times[time].strftime("%A %p")
				# check predicted values after the first day has been recorded
				if time > 3:
					hist = price_model.histogram()
					max_price_list = []
					for price in hist:
						max_price_list.append(max(hist[price].keys()))
					if max(max_price_list) < self.min_price:
						print("max predicted price (" + str(max_price_list) + \
							") is less than desired price (" + str(self.min_price) + ")")
						break
					if max_price_list[time - 2] < self.min_price:
						print("max price for " + day_of_the_week + " is only " + \
							str(max_price_list[time - 2]) + ", but the theoretical max is " + \
							str(max(max_price_list))+". skipping...")
						continue
					print("From histogram, theoretical max price is: " \
						+ str(max(max_price_list)))
				print("changing time to " + day_of_the_week + " (" + str(time) + ")")
				print(str(weekly_times[time]))
				self.changeDay(to_date=weekly_times[time])
				# wait for isabelle only on mornings that are not monday morning
				wait = time != 2 and not (time % 2 == 1 and time - 1 in prices.keys())
				self.acnh_reset(wait_for_Isabelle=wait)
				first_check = not (time % 2 == 1 and time - 1 in prices.keys())
				prices[time] = int(self.get_turnip_price(first_daily_check=first_check))
				price_model.fix_price(time, prices[time])
				print(day_of_the_week + " price: " + str(prices[time]))
				# check to see if the price exceeds 550
				if prices[time] > self.min_price:
					print("price larger than " + str(self.min_price) + 
						" was found! LARGE PRICE: "+str(max(prices.values())))
					self.changeDay(to_date=weekly_times[time - (time % 2)])
					print("prices: " + str(prices))
					return
			print("restarting week... week prices listed below:")
			if self.adaptive_price != 0:
				self.min_price -= self.adaptive_price
				print("lowering minimum acceptable price to: " + str(self.min_price))
			print(prices)
			prices.clear()

	def get_turnip_price(self, first_daily_check=True):
		while True:
			print("walking to shop...")
			self.press(Direction.DOWN, duration=4.6)
			self.press(Direction.RIGHT, duration=2.1)
			self.press(Direction.UP, duration=1.1)
			self.press(Button.A)
			self.wait(9.5)
			#racoons talk to you on first store entry 
			if first_daily_check:
				#dismiss raccoons
				print("Dismiss raccoons")
				self.pressRep(Button.B, 5, interval=0.5)
			else:
				print("do not wait for raccoon greeting")
			self.press(Direction.UP, duration=0.7)
			self.press(Direction.LEFT, duration=0.5)
			#talk to raccoons
			self.press(Button.A, wait=0.7)
			self.press(Button.B, duration=2.2)
			self.wait(self.stream_delay)
			#make sure the raccoons have been reached
			text = self.getText(-248, 70, 258, 258)
			if ("Yes!" in text and "course!" in text and "need?" in text) or \
					("...welcome!" in text and "today?" in text):
				print("entered store. getting turnip price... ")
				self.press(Button.B, wait=0.8)
				self.press(Direction.DOWN)
				self.press(Button.A)
				self.press(Button.B, duration=0.6)
				self.wait(self.stream_delay)
				text = self.getText(-248, 70, 258, 258)
				print("TEXT: " + text)
				price = 0
				if not ("Sundays" in text):
					# this returns an array of numbers in the given text
					prices = [int(s) for s in text.split() if s.isdigit()]
					if len(prices) > 0:
						price = prices[0]
					else:
						print("no price found :(")
				#dismiss
				self.pressRep(Button.B, 15, duration=0.3, interval=0.2)
				return price
			else:
				print("Store was not reached. resetting...")
				print("error text: "+text)
				self.pressRep(Button.B, 10, interval = 0.5)
				self.acnh_reset(wait_for_Isabelle=False)


# repeats an action over a rectangular area of the specified dimensions
class ACNH_Paint_Rectangle(ACNH_Infinite_Miles):
	NAME = 'ACNH Paint Rectangle'

	def __init__(self, cam):
		super().__init__(cam)
		self.width = 3
		self.height = 10
		self.second_button = False

	def do(self):
		print("painting a "+str(self.width)+" by "+str(self.height)+" area")
		# go right on even cycles, left on odd cycles
		horizontal_direction = Direction.RIGHT
		for y in range(self.height):
			# paint the tile below
			self.press(Button.A, wait=1.4)
			if self.second_button:
				# wait for the object to be put in pocket, then clean up
				self.wait(1)
				self.press(Button.Y, wait=1.4)
			self.press(Direction.DOWN, duration=0.2)
			# change directions
			if (y % 2 == 0):
				horizontal_direction = Direction.RIGHT
			else:
				horizontal_direction = Direction.LEFT
			self.press(horizontal_direction, duration=0.2)
			for x in range(self.width - 1):
				self.press(Button.A, wait=1.4)
				if self.second_button:
					# wait for the object to be put in pocket, then clean up
					self.wait(1)
					self.press(Button.Y, wait=1.4)
				self.press(horizontal_direction, duration=0.3)
			# face downwards for next row
			self.press(Direction.DOWN, duration=0.2)