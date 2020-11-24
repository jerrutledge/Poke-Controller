#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NewType
from Commands.PythonCommandBase import (
    PythonCommand,
    pokemonTypes,
    ImageProcPythonCommand,
)
from Commands.PythonCommands.ImageProcessingOnly.AutoTrainerBattle import (
    AutoTrainerBattle,
)
from Commands.Keys import KeyPress, Button, Direction, Stick
import re
import json
import math

# Battle through trainers by setting up with Swords Dance/X-Attack
# Spams the Pokémon's slot 1 attack. Assumes swords dance is in slot 2
class AutoDynamaxAdventure(AutoTrainerBattle):
    NAME = "Auto Dynamax Adventure"

    def __init__(self, cam):
        super().__init__(cam)
        self.keep_non_shiny_legend = False
        self.current_hp = 0
        self.max_hp = 0
        self.lowest_pp = 30
        self.boss_types = []
        self.turn_num = 0
        self.next_pokemon = ""
        self.nextPokemonRating = 0
        self.pokemonData = None
        self.currentPokemon = None
        self.currentPokemonRating = 600
        self.catchTopPokemon = True

        with open("pokemon-data.json") as poke_data:
            self.pokemonData = json.load(poke_data)

    def do(self):
        while True:
            # reset the variables
            self.current_hp = 0
            self.max_hp = 0
            self.lowest_pp = 30
            self.turn_num = 0
            self.next_pokemon = None
            self.nextPokemonRating = 0
            self.currentPokemon = None
            self.currentPokemonRating = 600
            if not self.catchTopPokemon:
                self.boss_types = []

            # yes, I'd like to go on an adventure
            self.pressRep(Button.A, 3, duration=0.5, interval=0.3, wait=0.5)
            if self.catchTopPokemon:
                # yes, I'm looking for a particular pokemon
                self.pressRep(Button.A, 3, duration=0.5, interval=0.3, wait=0.5)
            else:
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
                pokemon_options.append(
                    " ".join(self.getText(205, -240, 620, -850, inverse=True).split())
                )
                pokemon_abilities.append(
                    " ".join(self.getText(240, -270, 620, -850, inverse=True).split())
                )
                pokemon_options.append(
                    " ".join(self.getText(395, -430, 620, -850).split())
                )
                pokemon_abilities.append(
                    " ".join(self.getText(430, -460, 620, -850).split())
                )
                pokemon_options.append(
                    " ".join(self.getText(580, -615, 620, -850).split())
                )
                pokemon_abilities.append(
                    " ".join(self.getText(615, -645, 620, -850).split())
                )
                print(pokemon_options)
                print(pokemon_abilities)
                for pokemon in pokemon_options:
                    if pokemon in self.pokemonData:
                        if pokemon + " (2)" in self.pokemonData:
                            i = pokemon_options.index(pokemon)
                            ability = self.pokemonData[pokemon]["ability"]
                            if ability != pokemon_abilities[i]:
                                name = pokemon + " (2)"
                                v = self.pokemonRate(self.pokemonData[name])
                                values.append(v)
                                continue
                        v = self.pokemonRate(self.pokemonData[pokemon])
                        values.append(v)
                    else:
                        print("couldn't find " + pokemon)
                        values.append(0)
                print(values)
                if max(values) > 0:
                    choice = values.index(max(values))
                    print(
                        "Choosing pokemon #"
                        + str(choice + 1)
                        + ", "
                        + pokemon_options[choice]
                    )
                    self.pressRep(Direction.DOWN, choice)
                    self.currentPokemon = self.pokemonData[pokemon_options[choice]]
                    self.initializeCurrentPokemon()
                else:
                    print(
                        "OCR Fail: Max value: "
                        + str(max(values))
                        + ". Choose pokemon 1"
                    )
            self.press(Button.A)

            # start adventuring until it's over
            result = self.maxAdventureCycle()

            # check to make sure we didn't fail the first battle
            if not result:
                # just start again
                continue

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
                poke_name = " ".join(poke_name.split())
                if poke_name not in catches:
                    catches.append(poke_name)
                    suffix = " " + poke_name
                    if self.isContainTemplate("shiny_mark.png"):
                        print("SHINY!!! Pokemon #" + str(i + 1))
                        shinies.append(i)
                        suffix += " SHINY"
                    suffix += " (" + str(i) + ")"
                    self.camera.saveCapture(suffix=suffix)
                    self.press(Direction.DOWN, wait=0.5)
                else:
                    break
            # exit from pokemon summary
            self.press(Button.B, wait=2.5)
            print("Options: " + str(catches))
            if len(shinies) > 1:
                print("wow 2+ shinies!!! Gotta stop")
                break
            elif len(shinies) == 1 and shinies[0] == 3 and self.catchTopPokemon:
                print("Found desired shiny " + catches[3])
                break
            elif len(shinies) > 0:
                print("found a shiny in slot " + str(shinies[0] + 1))
                self.press(Direction.UP, duration=2, wait=0.2)
                self.pressRep(Direction.DOWN, shinies[0], interval=0.2)
                self.pressRep(Button.A, 3, interval=0.3)
            else:
                print("Not selecting any Pokemon...")
                self.press(Button.B, duration=0.9, wait=0.5)
                self.press(Button.A)
            self.pressRep(Button.B, 2, duration=0.5, interval=0.5)
            self.press(Button.A)
            if self.catchTopPokemon:
                self.press(Button.B)
                self.pressRep(Button.A, 20, duration=0.3, interval=0.3)
                self.pressRep(Button.B, 20, duration=0.3, interval=0.3)
            else:
                self.pressRep(Button.B, 30, interval=0.4)

    def maxAdventureCycle(self):
        for _ in range(10000):
            text = self.getText()
            text = " ".join(text.split())

            # double check the textbox in the lower part of the screen
            small_text = self.getText(
                top=-130, bottom=30, left=50, right=50, inverse=False, debug=False
            )
            small_text = " ".join(small_text.split())
            if len(text) < len(small_text):
                text = small_text

            # update our current HP, if possible
            hp_text = (self.getText(664, 24, 72, -222)).strip()
            result = re.search("^(\d+\/\d+)$", hp_text)
            if result is None:
                result = re.search("(\d+\/\d+)", small_text)
            if result is not None:
                hp_text = result.group(1)
                hp_int = hp_text.split("/")
                new_hp = int(hp_int[0])
                new_max_hp = int(hp_int[1])
                if new_max_hp < 100 or new_hp > new_max_hp:
                    # don't update hp
                    new_max_hp = 0
                elif not (new_hp == self.current_hp) or not (new_max_hp == self.max_hp):
                    print("Update HP: " + str(hp_int[0]) + "/" + str(hp_int[1]))
                    self.current_hp = new_hp
                    self.max_hp = new_max_hp
                else:
                    text += " HP_TXT=" + str(hp_text)

            # update the game state via text
            boss_text_regex = re.search("There’s a strong (.*)-type reaction", text)
            next_pokemon_regex = re.search(
                "^([A-Za-z \-.]*) is weak! Throw a Pok", text
            )
            cur_pokemon_regex = re.search("Go! (.*)!", text)
            if boss_text_regex is not None:
                if boss_text_regex.group(1).upper() in pokemonTypes:
                    bossType = boss_text_regex.group(1).upper()
                    if len(self.boss_types) == 0 or bossType not in self.boss_types:
                        self.boss_types = [bossType]
                    elif len(bossType) == 1:
                        self.boss_types.append(bossType)
                    print("Boss type:", self.boss_types)
                    self.wait(2)
                    continue
                else:
                    print("Boss type? No...")
            elif next_pokemon_regex is not None:
                next_pokemon_text = next_pokemon_regex.group(1).strip(" ")
                print("TEXT next pokemon: " + text)
                if next_pokemon_text in self.pokemonData:
                    self.next_pokemon = self.pokemonData[next_pokemon_text]
                    print(next_pokemon_text + " - " + str(self.next_pokemon["types"]))
                    self.nextPokemonRating = self.pokemonRate(self.next_pokemon)
                    self.wait(1.9)
                    text = "Catch"
                else:
                    print("couldn't identify pokemon '" + next_pokemon_text + "'")
            elif cur_pokemon_regex is not None:
                cur_pokemon_text = cur_pokemon_regex.group(1)
                print("TEXT sending out pokemon: " + text)
                if cur_pokemon_text in self.pokemonData:
                    # check to make sure we're not overwriting our current data
                    if (
                        self.currentPokemon
                        and cur_pokemon_text == self.currentPokemon["name"]
                    ):
                        print("Current pokemon is already " + cur_pokemon_text)
                        continue
                    self.currentPokemon = self.pokemonData[cur_pokemon_text]
                    self.initializeCurrentPokemon()
                    print(cur_pokemon_text + " - " + str(self.currentPokemon["types"]))
                    self.wait(3)
                    continue
                else:
                    print("couldn't identify pokemon '" + cur_pokemon_text + "'")

            # work out what action to take based on the text
            if "Catch" in text:
                print(text + " -- Catching Pokémon...")
                # since we know the battle is over now, the next battle will start on turn 1
                self.turn_num = 1
                self.pressRep(Button.A, 10)
                # instead of waiting, calculate
                if not self.currentPokemon:
                    self.wait(5)
                    continue
                self.currentPokemonRating = self.pokemonRate(
                    self.currentPokemon, rateHP=True
                )
            elif self.isContainTemplate("cheer_icon.png"):
                print("Cheer Icon - cheering on!")
                self.pressRep(Button.A, 3)
                self.wait(2)
            elif self.isContainTemplate("battle_icon.png"):
                print("Battle Icon - selecting move")
                self.press(Button.A, wait=0.2)
                # center the cursor on the first move
                self.press(Direction.RIGHT, duration=0.8)  # deselect dynamax
                self.hold(Direction.UP)
                # determine the best move via OCR
                if self.currentPokemon is not None:
                    # if we know them, provide attacks
                    best_attack, attacks, dynamax = self.bestAttack(
                        givenPokemon=self.currentPokemon, turn=self.turn_num
                    )
                else:
                    best_attack, attacks, dynamax = self.bestAttack(turn=self.turn_num)
                self.holdEnd(Direction.UP)
                self.wait(0.06)  # we have to wait for the hold end to be written
                print(
                    "Choose move#"
                    + str(best_attack["move_number"] + 1)
                    + ": "
                    + best_attack["moveName"]
                )
                # move up from the bottom in case there are less than 4 moves
                self.pressRep(Direction.UP, (4 - best_attack["move_number"]) % 4)
                if dynamax:
                    self.press(Direction.LEFT)
                self.pressRep(Button.A, 7, interval=0.1)
                # in case we are targeting ourselves for some reason
                self.press(Direction.UP)
                self.pressRep(Button.A, 6)
                self.press(Direction.RIGHT)
                self.pressRep(Button.A, 6)
                self.press(Direction.UP)
                self.pressRep(Button.A, 6)
                # update our lowest pp number
                self.lowest_pp = min(best_attack["PP"] - 1, self.lowest_pp)
                if self.turn_num:
                    self.turn_num += 1
                self.wait(1)
            elif "hold one item" in text:
                print("Item offered! Choosing item")
                self.pressRep(Button.A, 10, interval=0.5)
            elif "Which path would you like to take" in text:
                print("Choosing path? TEXT:" + text)
                self.pressRep(Button.A, 3, wait=2)
            elif (
                "Are you interested in swapping your current" in text
                or "One Trainer can choose to put the Pokémon" in text
            ):
                print("New Pokémon offer! TEXT:" + text)
                change_pokemon = False
                temp_old_val = 100
                temp_new_val = 100
                if self.next_pokemon is None or self.currentPokemon is None:
                    # if there is an OCR fail or otherwise the pokemon is unknown
                    temp_old_val = self.pokemonRate(rateHP=True)
                    temp_new_val = self.pokemonRate(rateHP=False)
                else:
                    # do math to see whether the new pokemon should be taken
                    temp_old_val = self.currentPokemonRating
                    temp_new_val = self.nextPokemonRating
                if temp_old_val < temp_new_val:
                    print(
                        "Accepting new Pokémon (Value: "
                        + str(temp_new_val)
                        + " > "
                        + str(temp_old_val)
                        + ")"
                    )
                    self.press(Button.A)
                    self.current_hp = 100
                    self.max_hp = 100
                    self.lowest_pp = 30
                    self.currentPokemon = self.next_pokemon
                    if self.currentPokemon is not None:
                        self.initializeCurrentPokemon()
                        print("new pokemon " + self.currentPokemon["name"])
                else:
                    print(
                        "Rejecting new Pokémon (Value: "
                        + str(temp_new_val)
                        + " < "
                        + str(temp_old_val)
                        + ")"
                    )
                    self.press(Button.B)
                self.next_pokemon = None
                self.wait(6)
            elif "Caught" in text or " @ confim @ quit" in text:
                if self.catchTopPokemon and self.next_pokemon:
                    print("Boss identified as " + self.next_pokemon["name"])
                    self.boss_types = self.next_pokemon["types"]
                print("Final screen TEXT: " + text)
                return True
            elif "Oh, that’s a bit of a letdown, isn’t it?" in text:
                print("Wow. We lost the very first battle.")
                self.pressRep(Button.B, 10, interval=0.3)
                return False
            else:
                print("TEXT: " + text)
            self.wait(0.2)
        print("Reached the end of 10000 - this shouldn't happen.")

    # when you get a new pokemon, update PP information
    def initializeCurrentPokemon(self):
        self.lowest_pp = 30
        i = 0
        for move in self.currentPokemon["moves"]:
            move["PP"] = int(move["maxPP"])
            move["move_number"] = i
            self.lowest_pp = min(move["PP"], self.lowest_pp)
            i += 1
        self.currentPokemonRating = self.pokemonRate(self.currentPokemon)

    def pokemonRate(self, pokemon=None, rateHP=False):
        hp_modifier = 1
        val = 600
        if pokemon:
            val = pokemon["value"]
        if len(self.boss_types) and pokemon:
            typad = 0
            suffix = ""
            if self.boss_types[0] in pokemon["offensiveAdvantages"]:
                typad += 100
                suffix += "+supermove1"
            if (
                len(self.boss_types) == 2
                and self.boss_types[1] in pokemon["offensiveAdvantages"]
            ):
                typad += 100
                suffix += "+supermove2"
            dmatch = pokemon["defensiveMatchups"]
            defense = dmatch[self.boss_types[0]]
            if len(self.boss_types) == 2:
                defense = min(defense, dmatch[self.boss_types[1]])
            typad += 100 / defense
            suffix += ""
            print(pokemon["name"], "type advantage =", typad, suffix)
            val += typad
        if rateHP:
            hp_modifier = (8 + 2 * (self.current_hp / max(1, self.max_hp))) / 10 + 0.06
            suffix = "(" + str(self.current_hp) + "/" + str(self.max_hp) + ")"
            print("HP modifier =", hp_modifier, suffix)
            val = math.floor(hp_modifier * val)
            if self.lowest_pp < 3:
                val = max(val * 0.5, 550)
        return val
