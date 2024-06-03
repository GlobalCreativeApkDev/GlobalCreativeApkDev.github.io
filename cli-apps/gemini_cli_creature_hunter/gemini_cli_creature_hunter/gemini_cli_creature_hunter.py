"""
This file contains code for the game "Gemini CLI Creature Hunter".
Author: GlobalCreativeApkDev
"""


# Game version: 1


# Importing necessary libraries


import sys
import time
import uuid
import pickle
import copy
import google.generativeai as gemini
import random
import os
from dotenv import load_dotenv
from functools import reduce

from mpmath import mp, mpf
from tabulate import tabulate

mp.pretty = True


# Creating static variables to be used throughout the game.


LETTERS: str = "abcdefghijklmnopqrstuvwxyz"
ELEMENT_CHART: list = [
    ["ATTACKING\nELEMENT", "TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
     "PURE",
     "LEGEND", "PRIMAL", "WIND"],
    ["DOUBLE\nDAMAGE", "ELECTRIC\nDARK", "NATURE\nICE", "FLAME\nWAR", "SEA\nLIGHT", "SEA\nMETAL", "NATURE\nWAR",
     "TERRA\nICE", "METAL\nLIGHT", "ELECTRIC\nDARK", "TERRA\nFLAME", "LEGEND", "PRIMAL", "PURE", "WIND"],
    ["HALF\nDAMAGE", "METAL\nWAR", "SEA\nWAR", "NATURE\nELECTRIC", "FLAME\nICE", "TERRA\nLIGHT", "FLAME\nMETAL",
     "ELECTRIC\nDARK", "TERRA", "NATURE", "SEA\nICE", "PRIMAL", "PURE", "LEGEND", "N/A"],
    ["NORMAL\nDAMAGE", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER",
     "OTHER",
     "OTHER", "OTHER", "OTHER"]
]


# Creating static functions to be used in this game.


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def list_to_string(a_list: list) -> str:
    res: str = "["  # initial value
    for i in range(len(a_list)):
        if i == len(a_list) - 1:
            res += str(a_list[i])
        else:
            res += str(a_list[i]) + ", "

    return res + "]"


def tabulate_element_chart() -> str:
    return str(tabulate(ELEMENT_CHART, headers='firstrow', tablefmt='fancy_grid'))


def generate_random_name() -> str:
    res: str = ""  # initial value
    name_length: int = random.randint(3, 25)
    for i in range(name_length):
        res += LETTERS[random.randint(0, len(LETTERS) - 1)]

    return res.capitalize()


def generate_random_legendary_creature(element):
    # type: (str) -> LegendaryCreature
    name: str = generate_random_name()
    max_hp: mpf = mpf(random.randint(45000, 55000))
    max_magic_points: mpf = mpf(random.randint(45000, 55000))
    attack_power: mpf = mpf(random.randint(8500, 9500))
    defense: mpf = mpf(random.randint(8500, 9500))
    attack_speed: mpf = mpf(random.randint(100, 125))
    skills: list = []  # initial value
    num_attack_skills: int = 0  # initial value
    num_heal_skills: int = 0  # initial value
    for i in range(4):
        if random.random() < 0.5:
            # Generating attack skill
            num_attack_skills += 1
            new_skill: Skill = Skill("ATTACK SKILL #" + str(num_attack_skills), "An attack skill.",
                                     "ATTACK", num_attack_skills * mpf("0.01") * random.randint(350, 450),
                                     mpf("0"), mpf("10") ** (num_attack_skills * random.randint(2, 4)))
            skills.append(new_skill)
        else:
            # Generating heal skill
            num_heal_skills += 1
            new_skill: Skill = Skill("HEAL SKILL #" + str(num_heal_skills), "A heal skill", "HEAL",
                                     mpf("0"), mpf("10") ** (num_attack_skills * random.randint(1, 3)),
                                     mpf("10") ** (num_attack_skills * random.randint(2, 4)))
            skills.append(new_skill)

    awaken_bonus: AwakenBonus = AwakenBonus(mpf(random.randint(115, 135)), mpf(random.randint(115, 135)),
                                            mpf(random.randint(115, 135)), mpf(random.randint(115, 135)),
                                            mpf(random.randint(0, 15)),
                                            mpf(0.01 * random.randint(0, 15)), mpf(0.01 * random.randint(0, 15)))
    new_legendary_creature: LegendaryCreature = LegendaryCreature(name, element, max_hp, max_magic_points,
                                                                  attack_power, defense, attack_speed, skills,
                                                                  awaken_bonus)
    return new_legendary_creature


def triangular(n: int) -> int:
    return int(n * (n - 1) / 2)


def mpf_sum_of_list(a_list: list) -> mpf:
    return mpf(str(sum(mpf(str(elem)) for elem in a_list if is_number(str(elem)))))


def mpf_product_of_list(a_list: list) -> mpf:
    return mpf(reduce(lambda x, y: mpf(x) * mpf(y) if is_number(x) and
                                                      is_number(y) else mpf(x) if is_number(x) and not is_number(
        y) else mpf(y) if is_number(y) and not is_number(x) else 1, a_list, 1))


def get_elemental_damage_multiplier(element1: str, element2: str) -> mpf:
    if element1 == "TERRA":
        return mpf("2") if element2 in ["ELECTRIC, DARK"] else mpf("0.5") if element2 in ["METAL", "WAR"] else mpf("1")
    elif element1 == "FLAME":
        return mpf("2") if element2 in ["NATURE", "ICE"] else mpf("0.5") if element2 in ["SEA", "WAR"] else mpf("1")
    elif element1 == "SEA":
        return mpf("2") if element2 in ["FLAME", "WAR"] else mpf("0.5") if element2 in ["NATURE", "ELECTRIC"] else \
            mpf("1")
    elif element1 == "NATURE":
        return mpf("2") if element2 in ["SEA", "LIGHT"] else mpf("0.5") if element2 in ["FLAME", "ICE"] else mpf("1")
    elif element1 == "ELECTRIC":
        return mpf("2") if element2 in ["SEA", "METAL"] else mpf("0.5") if element2 in ["TERRA", "LIGHT"] else mpf("1")
    elif element1 == "ICE":
        return mpf("2") if element2 in ["NATURE", "WAR"] else mpf("0.5") if element2 in ["FLAME", "METAL"] else mpf("1")
    elif element1 == "METAL":
        return mpf("2") if element2 in ["TERRA", "ICE"] else mpf("0.5") if element2 in ["ELECTRIC", "DARK"] else \
            mpf("1")
    elif element1 == "DARK":
        return mpf("2") if element2 in ["METAL", "LIGHT"] else mpf("0.5") if element2 == "TERRA" else mpf("1")
    elif element1 == "LIGHT":
        return mpf("2") if element2 in ["ELECTRIC", "DARK"] else mpf("0.5") if element2 == "NATURE" else mpf("1")
    elif element1 == "WAR":
        return mpf("2") if element2 in ["TERRA", "FLAME"] else mpf("0.5") if element2 in ["SEA", "ICE"] else mpf("1")
    elif element1 == "PURE":
        return mpf("2") if element2 == "LEGEND" else mpf("0.5") if element2 == "PRIMAL" else mpf("1")
    elif element1 == "LEGEND":
        return mpf("2") if element2 == "PRIMAL" else mpf("0.5") if element2 == "PURE" else mpf("1")
    elif element1 == "PRIMAL":
        return mpf("2") if element2 == "PURE" else mpf("0.5") if element2 == "LEGEND" else mpf("1")
    elif element1 == "WIND":
        return mpf("2") if element2 == "WIND" else mpf("1")
    else:
        return mpf("1")


def load_game_data(file_name):
    # type: (str) -> SavedGameData
    return pickle.load(open(file_name, "rb"))


def save_game_data(game_data, file_name):
    # type: (SavedGameData, str) -> None
    pickle.dump(game_data, open(file_name, "wb"))


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating necessary classes


###########################################
# ADVENTURE MODE
###########################################


class Action:
    """
    This class contains attributes of an action which can be carried out during battles.
    """

    POSSIBLE_NAMES: list = ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]

    def execute(self, user, target, skill_to_use=None):
        # type: (LegendaryCreature, LegendaryCreature, Skill or None) -> bool
        if self.name == "NORMAL ATTACK":
            if user == target:
                return False

            is_crit: bool = random.random() < user.crit_rate
            crit_factor: mpf = user.crit_damage if is_crit else mpf("1")
            raw_damage: mpf = user.attack_power * crit_factor - target.defense
            damage_multiplier_by_element: mpf = get_elemental_damage_multiplier(user.element, target.element)
            raw_damage *= damage_multiplier_by_element
            damage: mpf = raw_damage if raw_damage > mpf("0") else mpf("0")
            target.curr_hp -= damage
            print(str(user.name) + " dealt " + str(damage) + " damage on " + str(target.name) + "!")
            return True

        elif self.name == "NORMAL HEAL":
            if user != target:
                return False

            heal_amount: mpf = 0.05 * user.max_hp
            user.curr_hp += heal_amount
            if user.curr_hp >= user.max_hp:
                user.curr_hp = user.max_hp

            return True

        elif self.name == "USE SKILL":
            if isinstance(skill_to_use, Skill):
                if skill_to_use.skill_type == "HEAL":
                    user.curr_hp += skill_to_use.heal_amount
                    if user.curr_hp >= user.max_hp:
                        user.curr_hp = user.max_hp
                elif skill_to_use.skill_type == "ATTACK":
                    is_crit: bool = random.random() < user.crit_rate
                    crit_factor: mpf = user.crit_damage if is_crit else mpf("1")
                    raw_damage: mpf = user.attack_power * skill_to_use.damage_multiplier * crit_factor - target.defense
                    damage_multiplier_by_element: mpf = get_elemental_damage_multiplier(user.element, target.element)
                    raw_damage *= damage_multiplier_by_element
                    damage: mpf = raw_damage if raw_damage > mpf("0") else mpf("0")
                    target.curr_hp -= damage
                    print(str(user.name) + " dealt " + str(damage) + " damage on " + str(target.name) + "!")
                return True
            return False
        return False


    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Action
        return copy.deepcopy(self)


class AwakenBonus:
    """
    This class contains attributes of the bonus gained for awakening a legendary creature.
    """

    def __init__(self, max_hp_percentage_up, max_magic_points_percentage_up, attack_power_percentage_up,
                 defense_percentage_up, attack_speed_up, crit_rate_up, crit_damage_up):
        # type: (mpf, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        self.max_hp_percentage_up: mpf = max_hp_percentage_up
        self.max_magic_points_percentage_up: mpf = max_magic_points_percentage_up
        self.attack_power_percentage_up: mpf = attack_power_percentage_up
        self.defense_percentage_up: mpf = defense_percentage_up
        self.attack_speed_up: mpf = attack_speed_up
        self.crit_rate_up: mpf = crit_rate_up
        self.crit_damage_up: mpf = crit_damage_up

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> AwakenBonus
        return copy.deepcopy(self)


class Battle:
    """
    This class contains attributes of a battle in this game.
    """

    def __init__(self, trainer1):
        # type: (Trainer) -> None
        self.trainer1: Trainer = trainer1
        self.whose_turn: LegendaryCreature or None = None
        self.winner: BattleTeam or None = None
        self.reward: Reward = Reward()  # initial value

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Battle
        return copy.deepcopy(self)


class WildBattle(Battle):
    """
    This class contains attributes of a battle against a legendary creature.
    """

    def __init__(self, trainer1, wild_legendary_creature):
        # type: (Trainer, LegendaryCreature) -> None
        Battle.__init__(self, trainer1)
        self.wild_legendary_creature: LegendaryCreature = wild_legendary_creature
        self.reward = Reward(mpf("10") ** (5 * self.wild_legendary_creature.level),
                             mpf("10") ** (5 * self.wild_legendary_creature.level - 2),
                             mpf("10") ** (5 * self.wild_legendary_creature.level))
        self.wild_legendary_creature_caught: bool = False
        self.trainer_fled: bool = False

    def get_someone_to_move(self):
        # type: () -> None
        """
        Getting a legendary creature to move and have its turn.
        :return: None
        """

        # Finding out which legendary creature moves
        full_attack_gauge_list: list = []  # initial value
        while len(full_attack_gauge_list) == 0:
            for legendary_creature in self.trainer1.battle_team.get_legendary_creatures():
                if legendary_creature.attack_gauge >= legendary_creature.FULL_ATTACK_GAUGE and legendary_creature not \
                        in full_attack_gauge_list:
                    full_attack_gauge_list.append(legendary_creature)

            if (self.wild_legendary_creature.attack_gauge >= self.wild_legendary_creature.FULL_ATTACK_GAUGE and
                    self.wild_legendary_creature not in full_attack_gauge_list):
                full_attack_gauge_list.append(self.wild_legendary_creature)

            self.tick()

        max_attack_gauge: mpf = max(legendary_creature.attack_gauge for legendary_creature in full_attack_gauge_list)
        for legendary_creature in full_attack_gauge_list:
            if legendary_creature.attack_gauge == max_attack_gauge:
                self.whose_turn = legendary_creature

    def tick(self):
        # type: () -> None
        """
        The clock ticks when battles are carried out.
        :return: None
        """

        for legendary_creature in self.trainer1.battle_team.get_legendary_creatures():
            legendary_creature.attack_gauge += legendary_creature.attack_speed * 0.07

        self.wild_legendary_creature.attack_gauge += self.wild_legendary_creature.attack_speed * 0.07


class TrainerBattle(Battle):
    """
    This class contains attributes of a battle between legendary creature trainers.
    """

    def __init__(self, trainer1, trainer2):
        # type: (Trainer, Trainer) -> None
        Battle.__init__(self, trainer1)
        self.trainer2: Trainer = trainer2
        self.reward = Reward(mpf("10") ** sum(5 * legendary_creature.level for legendary_creature in
                                              self.trainer2.battle_team.get_legendary_creatures()),
                             mpf("10") ** sum(5 * legendary_creature.level - 2 for legendary_creature in
                                              self.trainer2.battle_team.get_legendary_creatures()),
                             mpf("10") ** sum(5 * legendary_creature.level for legendary_creature in
                                              self.trainer2.battle_team.get_legendary_creatures()))

    def get_someone_to_move(self):
        # type: () -> None
        """
        Getting a legendary creature to move and have its turn.
        :return: None
        """

        # Finding out which legendary creature moves
        full_attack_gauge_list: list = []  # initial value
        while len(full_attack_gauge_list) == 0:
            for legendary_creature in self.trainer1.battle_team.get_legendary_creatures():
                if legendary_creature.attack_gauge >= legendary_creature.FULL_ATTACK_GAUGE and legendary_creature not \
                        in full_attack_gauge_list:
                    full_attack_gauge_list.append(legendary_creature)

            for legendary_creature in self.trainer2.battle_team.get_legendary_creatures():
                if legendary_creature.attack_gauge >= legendary_creature.FULL_ATTACK_GAUGE and legendary_creature not \
                        in full_attack_gauge_list:
                    full_attack_gauge_list.append(legendary_creature)

            self.tick()

        max_attack_gauge: mpf = max(legendary_creature.attack_gauge for legendary_creature in full_attack_gauge_list)
        for legendary_creature in full_attack_gauge_list:
            if legendary_creature.attack_gauge == max_attack_gauge:
                self.whose_turn = legendary_creature

    def tick(self):
        # type: () -> None
        """
        The clock ticks when battles are carried out.
        :return: None
        """

        for legendary_creature in self.trainer1.battle_team.get_legendary_creatures():
            legendary_creature.attack_gauge += legendary_creature.attack_speed * 0.07

        for legendary_creature in self.trainer2.battle_team.get_legendary_creatures():
            legendary_creature.attack_gauge += legendary_creature.attack_speed * 0.07


class City:
    """
    This class contains attributes of a city in this game.
    """

    def __init__(self, name, tiles):
        # type: (str, list) -> None
        self.name: str = name
        self.__tiles: list = tiles

    def get_tile_at(self, x, y):
        # type: (int, int) -> CityTile or None
        if x < 0 or x >= len(self.__tiles[0]) or y < 0 or y >= len(self.__tiles):
            return None
        return self.__tiles[y][x]

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

    def __str__(self):
        # type: () -> str
        res: str = str(self.name)
        all_tiles: list = []  # initial value
        for y in range(len(self.__tiles)):
            curr_tiles: list = []  # initial value
            for x in range(len(self.__tiles[y])):
                curr_tile: CityTile = self.get_tile_at(x, y)
                curr_tiles.append(str(curr_tile))

            all_tiles.append(curr_tiles)
        return res + "\n" + str(tabulate(all_tiles, headers='firstrow', tablefmt='fancy_grid'))

    def clone(self):
        # type: () -> City
        return copy.deepcopy(self)


class CityTile:
    """
    This class contains attributes of a tile in a city.
    """

    def __init__(self):
        # type: () -> None
        self.__trainers: list = []  # initial value
        self.is_portal: bool = False
        self.can_encounter_wild_battles: bool = False

    def get_trainers(self):
        # type: () -> list
        return self.__trainers

    def add_trainer(self, trainer):
        # type: (Trainer) -> None
        self.__trainers.append(trainer)

    def remove_trainer(self, trainer):
        # type: (Trainer) -> bool
        if trainer in self.__trainers:
            self.__trainers.remove(trainer)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return "(" + str(type(self).__name__) + ") AND " + list_to_string([trainer.name for trainer in self.__trainers])

    def clone(self):
        # type: () -> CityTile
        return copy.deepcopy(self)


class PortalTile(CityTile):
    """
    This class contains attributes of a portal from one city to another.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)
        self.is_portal = True


class GrassTile(CityTile):
    """
    This class contains attributes of a city tile with grass where the player can encounter wild legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)
        self.can_encounter_wild_battles = True


class PavementTile(CityTile):
    """
    This class contains attributes of a tile with pavement where the player can walk safely without any distractions
    from wild legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)


###########################################
# ADVENTURE MODE
###########################################


###########################################
# INVENTORY
###########################################


class LegendaryCreatureInventory:
    """
    This class contains attributes of an inventory containing legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        self.__legendary_creatures: list = []  # initial value

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> None
        self.__legendary_creatures.append(legendary_creature)

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__legendary_creatures:
            self.__legendary_creatures.remove(legendary_creature)
            return True
        return False

    def get_legendary_creatures(self):
        # type: () -> list
        return self.__legendary_creatures

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> LegendaryCreatureInventory
        return copy.deepcopy(self)


class ItemInventory:
    """
    This class contains attributes of an inventory containing items.
    """

    def __init__(self):
        # type: () -> None
        self.__items: list = []  # initial value

    def add_item(self, item):
        # type: (Item) -> None
        self.__items.append(item)

    def remove_item(self, item):
        # type: (Item) -> bool
        if item in self.__items:
            self.__items.remove(item)
            return True
        return False

    def get_items(self):
        # type: () -> list
        return self.__items

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> ItemInventory
        return copy.deepcopy(self)


###########################################
# INVENTORY
###########################################


###########################################
# LEGENDARY CREATURE
###########################################


class BattleTeam:
    """
    This class contains attributes of a team brought to battles.
    """

    MAX_LEGENDARY_CREATURES: int = 5

    def __init__(self, legendary_creatures=None):
        # type: (list) -> None
        if legendary_creatures is None:
            legendary_creatures = []
        self.__legendary_creatures: list = legendary_creatures if len(legendary_creatures) <= \
                                                                  self.MAX_LEGENDARY_CREATURES else []

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if len(self.__legendary_creatures) < self.MAX_LEGENDARY_CREATURES:
            self.__legendary_creatures.append(legendary_creature)
            return True
        return False

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__legendary_creatures:
            self.__legendary_creatures.remove(legendary_creature)
            return True
        return False

    def get_legendary_creatures(self):
        # type: () -> list
        return self.__legendary_creatures

    def recover_all(self):
        # type: () -> None
        for legendary_creature in self.__legendary_creatures:
            legendary_creature.restore()

    def all_died(self):
        # type: () -> bool
        for legendary_creature in self.__legendary_creatures:
            if legendary_creature.get_is_alive():
                return False
        return True

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> BattleTeam
        return copy.deepcopy(self)


class LegendaryCreature:
    """
    This class contains attributes of a legendary creature in this game.
    """

    MIN_CRIT_RATE: mpf = mpf("0.15")
    MAX_CRIT_RATE: mpf = mpf("1")
    MIN_CRIT_DAMAGE: mpf = mpf("1.5")
    MIN_ATTACK_GAUGE: mpf = mpf("0")
    FULL_ATTACK_GAUGE: mpf = mpf("1")
    POTENTIAL_ELEMENTS: list = ["TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
                                "PURE", "LEGEND", "PRIMAL", "WIND", "BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM",
                                "SOUL"]

    def __init__(self, name, element, max_hp, max_magic_points, attack_power, defense, attack_speed, skills,
                 awaken_bonus):
        # type: (str, mpf, str, mpf, mpf, mpf, mpf, list, AwakenBonus) -> None
        self.name: str = name
        self.element: str = element if element in self.POTENTIAL_ELEMENTS else self.POTENTIAL_ELEMENTS[0]
        self.level: int = 1
        self.exp: mpf = mpf("0")
        self.required_exp: mpf = mpf("1e6")
        self.curr_hp: mpf = max_hp
        self.max_hp: mpf = max_hp
        self.curr_magic_points: mpf = max_magic_points
        self.max_magic_points: mpf = max_magic_points
        self.attack_power: mpf = attack_power
        self.defense: mpf = defense
        self.attack_speed: mpf = attack_speed
        self.__skills: list = skills
        self.awaken_bonus: AwakenBonus = awaken_bonus
        self.crit_rate: mpf = self.MIN_CRIT_RATE
        self.crit_damage: mpf = self.MIN_CRIT_DAMAGE
        self.__runes: dict = {}  # initial value
        self.attack_gauge: mpf = self.MIN_ATTACK_GAUGE
        self.has_awakened: bool = False
        self.corresponding_team: BattleTeam or None = None  # initial value

    def awaken(self):
        # type: () -> bool
        if not self.has_awakened:
            self.name = "AWAKENED " + str(self.name)
            self.max_hp *= 1 + self.awaken_bonus.max_hp_percentage_up / 100
            self.max_magic_points *= 1 + self.awaken_bonus.max_magic_points_percentage_up / 100
            self.attack_power *= 1 + self.awaken_bonus.attack_power_percentage_up / 100
            self.defense *= 1 + self.awaken_bonus.defense_percentage_up / 100
            self.attack_speed += self.awaken_bonus.attack_speed_up
            self.crit_rate += self.awaken_bonus.crit_rate_up
            if self.crit_rate > self.MAX_CRIT_RATE:
                self.crit_rate = self.MAX_CRIT_RATE

            self.crit_damage += self.awaken_bonus.crit_damage_up
            self.restore()
            self.has_awakened = True
            return True
        return False

    def restore(self):
        # type: () -> None
        self.curr_magic_points = self.max_magic_points
        self.curr_hp = self.max_hp

    def get_skills(self):
        # type: () -> list
        return self.__skills

    def get_runes(self):
        # type: () -> dict
        return self.__runes

    def get_is_alive(self):
        # type: () -> bool
        return self.curr_hp > 0

    def recover_magic_points(self):
        # type: () -> None
        self.curr_magic_points += self.max_magic_points / 12
        if self.curr_magic_points >= self.max_magic_points:
            self.curr_magic_points = self.max_magic_points

    def place_rune(self, rune):
        # type: (Rune) -> bool
        if rune.already_placed:
            return False

        if rune.slot_number in self.__runes.keys():
            self.remove_rune(rune.slot_number)

        self.__runes[rune.slot_number] = rune
        self.max_hp *= 1 + (rune.max_hp_percentage_up / 100)
        self.max_magic_points *= 1 + (rune.max_magic_points_percentage_up / 100)
        self.attack_power *= 1 + (rune.attack_power_percentage_up / 100)
        self.defense *= 1 + (rune.stat_increase.defense_percentage_up / 100)
        self.attack_speed += rune.attack_speed_up
        self.crit_rate += rune.crit_rate_up
        if self.crit_rate > self.MAX_CRIT_RATE:
            self.crit_rate = self.MAX_CRIT_RATE

        self.crit_damage += rune.crit_damage_up
        self.restore()
        rune.already_placed = True
        return True

    def level_up(self):
        # type: () -> None
        while self.exp >= self.required_exp:
            self.level += 1
            self.required_exp *= mpf("10") ** self.level
            temp_runes: dict = self.__runes
            for slot_number in self.__runes.keys():
                self.remove_rune(slot_number)

            self.attack_power *= triangular(self.level)
            self.max_hp *= triangular(self.level)
            self.player_gold_per_second *= triangular(self.level)
            self.max_magic_points *= triangular(self.level)
            self.defense *= triangular(self.level)
            self.attack_speed += 2
            for rune in temp_runes.values():
                self.place_rune(rune)

            self.restore()

    def level_up_rune(self, slot_number):
        # type: (int) -> bool
        if slot_number not in self.__runes.keys():
            return False

        current_rune: Rune = self.__runes[slot_number]
        self.remove_rune(slot_number)
        success: bool = current_rune.level_up()
        self.place_rune(current_rune)
        return success

    def remove_rune(self, slot_number):
        # type: (int) -> bool
        if slot_number in self.__runes.keys():
            # Remove the rune at slot number 'slot_number'
            current_rune: Rune = self.__runes[slot_number]
            self.max_hp /= 1 + (current_rune.max_hp_percentage_up / 100)
            self.max_magic_points /= 1 + (current_rune.max_magic_points_percentage_up / 100)
            self.attack_power /= 1 + (current_rune.attack_power_percentage_up / 100)
            self.defense /= 1 + (current_rune.defense_percentage_up / 100)
            self.attack_speed -= current_rune.attack_speed_up
            self.crit_rate -= current_rune.crit_rate_up
            if self.crit_rate <= self.MIN_CRIT_RATE:
                self.crit_rate = self.MIN_CRIT_RATE

            self.crit_damage -= current_rune.crit_damage_up
            if self.crit_damage <= self.MIN_CRIT_DAMAGE:
                self.crit_damage = self.MIN_CRIT_DAMAGE

            self.restore()
            self.__runes.pop(current_rune.slot_number)
            current_rune.already_placed = False
            return True
        return False

    def have_turn(self, other, skill, action_name):
        # type: (LegendaryCreature, Skill or None, str) -> bool
        self.attack_gauge = self.MIN_ATTACK_GAUGE
        if action_name == "NORMAL ATTACK":
            self.normal_attack(other)
        elif action_name == "NORMAL HEAL":
            self.normal_heal(other)
        elif action_name == "USE SKILL" and isinstance(skill, Skill):
            self.use_skill(other, skill)
        else:
            return False

        return True

    def normal_attack(self, other):
        # type: (LegendaryCreature) -> None
        action: Action = Action("NORMAL ATTACK")
        action.execute(self, other)

    def normal_heal(self, other):
        # type: (LegendaryCreature) -> None
        action: Action = Action("NORMAL HEAL")
        action.execute(self, other)

    def use_skill(self, other, active_skill):
        # type: (LegendaryCreature, Skill) -> bool
        if active_skill not in self.__skills:
            return False

        if self.curr_magic_points < active_skill.magic_points_cost:
            print("Not enough magic points!")
            return False

        action: Action = Action("USE SKILL")
        action.execute(self, other, active_skill)
        self.curr_magic_points -= active_skill.magic_points_cost
        return True

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> LegendaryCreature
        return copy.deepcopy(self)


class Skill:
    """
    This class contains attributes of a skill legendary creatures have.
    """

    POSSIBLE_SKILL_TYPES: list = ["ATTACK", "HEAL"]

    def __init__(self, name, description, skill_type, damage_multiplier, heal_amount, magic_points_cost):
        # type: (str, str, str, mpf, mpf, mpf) -> None
        self.name: str = name
        self.level: int = 1
        self.description: str = description
        self.skill_type: str = skill_type if skill_type in self.POSSIBLE_SKILL_TYPES else self.POSSIBLE_SKILL_TYPES[0]
        self.damage_multiplier: mpf = damage_multiplier if self.skill_type == "ATTACK" else mpf("0")
        self.heal_amount: mpf = heal_amount if self.skill_type == "HEAL" else mpf("0")
        self.magic_points_cost: mpf = magic_points_cost

    def level_up(self):
        # type: () -> None
        self.damage_multiplier *= mpf("1.25") * self.level
        self.heal_amount *= mpf("1.25") * self.level
        self.level += 1

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Skill
        return copy.deepcopy(self)


###########################################
# LEGENDARY CREATURE
###########################################


###########################################
# ITEM
###########################################


class Item:
    """
    This class contains attributes of an item in this game.
    """

    def __init__(self, name, description, gold_cost):
        # type: (str, str, mpf) -> None
        self.name: str = name
        self.description: str = description
        self.gold_cost: mpf = gold_cost
        self.sell_gold_gain: mpf = gold_cost / 5

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Item
        return copy.deepcopy(self)


class Ball(Item):
    """
    This class contains attributes of a ball used to catch a legendary creature.
    """

    MIN_CATCH_SUCCESS_RATE: mpf = mpf("0.15")
    MAX_CATCH_SUCCESS_RATE: mpf = mpf("1")

    def __init__(self, name, description, gold_cost, catch_success_rate):
        # type: (str, str, mpf, mpf) -> None
        Item.__init__(self, name, description, gold_cost)
        self.catch_success_rate: mpf = catch_success_rate if (self.MIN_CATCH_SUCCESS_RATE <= catch_success_rate <=
                                                        self.MAX_CATCH_SUCCESS_RATE) else self.MIN_CATCH_SUCCESS_RATE


class Rune(Item):
    """
    This class contains attributes of a rune used to strengthen legendary creatures.
    """

    MIN_SLOT_NUMBER: int = 1
    MAX_SLOT_NUMBER: int = 6
    MIN_RATING: int = 1
    MAX_RATING: int = 6
    MAX_CRIT_RATE_UP: mpf = mpf("0.85")

    def __init__(self, name, description, gold_cost, rating, slot_number, max_magic_points_percentage_up,
                 max_hp_percentage_up, attack_power_percentage_up, defense_percentage_up, attack_speed_up,
                 crit_rate_up, crit_damage_up):
        # type: (str, str, mpf, int, int, mpf, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        Item.__init__(self, name, description, gold_cost)
        self.rating: int = rating if self.MIN_RATING <= rating <= self.MAX_RATING else self.MIN_RATING
        self.slot_number: int = slot_number if self.MIN_SLOT_NUMBER <= slot_number <= self.MAX_SLOT_NUMBER \
            else self.MIN_SLOT_NUMBER
        self.max_magic_points_percentage_up: mpf = max_magic_points_percentage_up
        self.max_hp_percentage_up: mpf = max_hp_percentage_up
        self.attack_power_percentage_up: mpf = attack_power_percentage_up
        self.defense_percentage_up: mpf = defense_percentage_up
        self.attack_speed_up: mpf = attack_speed_up
        self.crit_rate_up: mpf = crit_rate_up if mpf("0") <= crit_rate_up <= self.MAX_CRIT_RATE_UP else mpf("0")
        self.crit_damage_up: mpf = crit_damage_up
        self.level: int = 1
        self.level_up_gold_cost: mpf = gold_cost
        self.level_up_success_rate: mpf = mpf("1")
        self.already_placed: bool = False  # initial value

    def level_up(self):
        # type: () -> bool
        # Check whether levelling up is successful or not
        if random.random() > self.level_up_success_rate:
            return False

        # Increase the level of the rune
        self.level += 1

        # Update the cost and success rate of levelling up the rune
        self.level_up_gold_cost *= mpf("10") ** (self.level + self.rating)
        self.level_up_success_rate *= mpf("0.95")

        # Increase stats
        self.stat_increase.max_hp_percentage_up += self.rating
        self.stat_increase.max_magic_points_percentage_up += self.rating
        self.stat_increase.attack_percentage_up += self.rating
        self.stat_increase.defense_percentage_up += self.rating
        self.stat_increase.attack_speed_up += 2 * self.rating
        self.stat_increase.crit_rate_up += 0.01 * self.rating
        self.stat_increase.crit_damage_up += 0.05 * self.rating
        self.stat_increase.resistance_up += 0.01 * self.rating
        self.stat_increase.accuracy_up += 0.01 * self.rating
        return True


class AwakenShard(Item):
    """
    This class contains attributes of an awaken shard to immediately awaken a legendary creature.
    """

    def __init__(self, name, description, gold_cost, legendary_creature_element):
        # type: (str, str, mpf, str) -> None
        Item.__init__(self, name, description, gold_cost)
        self.legendary_creature_element: str = legendary_creature_element


class EXPShard(Item):
    """
    This class contains attributes of an EXP shard to increase the EXP of a legendary creature.
    """

    def __init__(self, name, description, gold_cost, exp_granted):
        # type: (str, str, mpf, mpf) -> None
        Item.__init__(self, name, description, gold_cost)
        self.exp_granted: mpf = exp_granted


class LevelUpShard(Item):
    """
    This class contains attributes of a shard used to immediately level up a legendary creature.
    """

    def __init__(self, name, description, gold_cost):
        # type: (str, str, mpf) -> None
        Item.__init__(self, name, description, gold_cost)


class SkillLevelUpShard(Item):
    """
    This class contains attributes of a skill level up shard to immediately increase the level of a
    skill possessed by a legendary creature.
    """

    def __init__(self, name, description, gold_cost):
        # type: (str, str, mpf) -> None
        Item.__init__(self, name, description, gold_cost)


###########################################
# ITEM
###########################################


###########################################
# GENERAL
###########################################


class Trainer:
    """
    This class contains attributes of a trainer in this game.
    """

    def __init__(self, name):
        # type: (str) -> None
        self.player_id: str = str(uuid.uuid1())  # generating random player ID
        self.name: str = name
        self.level: int = 1
        self.exp: mpf = mpf("0")
        self.required_exp: mpf = mpf("1e6")
        self.gold: mpf = mpf("5e6")
        self.battle_team: BattleTeam = BattleTeam()
        self.item_inventory: ItemInventory = ItemInventory()
        self.legendary_creature_inventory: LegendaryCreatureInventory = LegendaryCreatureInventory()
        self.city: City or None = None  # initial value
        self.location: AdventureModeLocation = AdventureModeLocation(0, 0)

    def move_up(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_y > 0:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_trainer(self)
                self.location.tile_y -= 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_trainer(self)
                return True
            return False
        return False

    def move_down(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_y < len(self.city.get_tiles()) - 1:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_trainer(self)
                self.location.tile_y += 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_trainer(self)
                return True
            return False
        return False

    def move_left(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_x > 0:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_trainer(self)
                self.location.tile_x -= 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_trainer(self)
                return True
            return False
        return False

    def move_right(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_x < len(self.city.get_tiles()[0]) - 1:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_trainer(self)
                self.location.tile_x += 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_trainer(self)
                return True
            return False
        return False

    def claim_reward(self, reward):
        # type: (Reward) -> None
        self.exp += reward.player_reward_exp
        self.level_up()
        self.gold += reward.player_reward_gold
        for legendary_creature in self.battle_team.get_legendary_creatures():
            legendary_creature.exp += reward.legendary_creature_reward_exp
            legendary_creature.level_up()

        self.battle_team.recover_all()

    def get_city_tile(self):
        # type: () -> CityTile or None
        if isinstance(self.city, City):
            return self.city.get_tile_at(self.location.tile_x, self.location.tile_y)
        return None

    def place_rune_on_legendary_creature(self, legendary_creature, rune):
        # type: (LegendaryCreature, Rune) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures() and rune in \
                self.item_inventory.get_items():
            legendary_creature.place_rune(rune)
            return True
        return False

    def remove_rune_from_legendary_creature(self, legendary_creature, slot_number):
        # type: (LegendaryCreature, int) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            if slot_number in legendary_creature.get_runes().keys():
                legendary_creature.remove_rune(slot_number)
                return True
            return False
        return False

    def level_up(self):
        # type: () -> None
        while self.exp >= self.required_exp:
            self.level += 1
            self.required_exp *= mpf("10") ** self.level

    def purchase_item(self, item):
        # type: (Item) -> bool
        if self.gold >= item.gold_cost:
            self.gold -= item.gold_cost
            self.add_item_to_inventory(item)
            return True
        else:
            print("Not enough gold!")
            return False

    def sell_item(self, item):
        # type: (Item) -> bool
        if item in self.item_inventory.get_items():
            if isinstance(item, Rune):
                if item.already_placed:
                    return False

            self.remove_item_from_inventory(item)
            self.gold += item.sell_gold_gain
            return True
        return False

    def level_up_rune(self, rune):
        # type: (Rune) -> bool
        creature_has_rune: bool = False
        for legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            if rune in legendary_creature.get_runes().values():
                creature_has_rune = True
                if self.gold >= rune.level_up_gold_cost:
                    self.gold -= rune.level_up_gold_cost
                    return legendary_creature.level_up_rune(rune.slot_number)
                else:
                    return False
        if not creature_has_rune:
            if rune in self.item_inventory.get_items():
                if self.gold >= rune.level_up_gold_cost:
                    self.gold -= rune.level_up_gold_cost
                    return rune.level_up()
                return False
            return False
        return False

    def add_item_to_inventory(self, item):
        # type: (Item) -> None
        self.item_inventory.add_item(item)

    def remove_item_from_inventory(self, item):
        # type: (Item) -> bool
        if isinstance(item, Rune):
            for legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
                if item in legendary_creature.get_runes().values():
                    return False

        return self.item_inventory.remove_item(item)

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> None
        self.legendary_creature_inventory.add_legendary_creature(legendary_creature)

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.battle_team.get_legendary_creatures():
            return False
        return self.legendary_creature_inventory.remove_legendary_creature(legendary_creature)

    def add_legendary_creature_to_team(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            if self.battle_team.add_legendary_creature(legendary_creature):
                legendary_creature.corresponding_team = self.battle_team
                return True
            return False
        return False

    def remove_legendary_creature_from_team(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            legendary_creature.corresponding_team = None
            return self.battle_team.remove_legendary_creature(legendary_creature)
        return False

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Trainer
        return copy.deepcopy(self)


class AITrainer(Trainer):
    """
    This class contains attributes of an AI-controlled trainer in this game.
    """

    def __init__(self, name):
        # type: (str) -> None
        Trainer.__init__(self, name)


class ItemShop:
    """
    This class contains attributes of an item shop selling items.
    """

    def __init__(self, items_sold):
        # type: (list) -> None
        self.name: str = "ITEM SHOP"
        self.__items_sold: list = items_sold

    def get_items_sold(self):
        # type: () -> list
        return self.__items_sold

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> ItemShop
        return copy.deepcopy(self)


class Reward:
    """
    This class contains attributes of the reward gained for doing something in this game.
    """

    def __init__(self, player_reward_exp=mpf("0"), player_reward_gold=mpf("0"),
                 legendary_creature_reward_exp=mpf("0")):
        # type: (mpf, mpf, mpf, mpf) -> None
        self.player_reward_exp: mpf = player_reward_exp
        self.player_reward_gold: mpf = player_reward_gold
        self.legendary_creature_reward_exp: mpf = legendary_creature_reward_exp

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Reward
        return copy.deepcopy(self)


class AdventureModeLocation:
    """
    This class contains attributes of the location of a trainer in adventure mode of this game.
    """

    def __init__(self, tile_x, tile_y):
        # type: (int, int) -> None
        self.tile_x: int = tile_x
        self.tile_y: int = tile_y

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> AdventureModeLocation
        return copy.deepcopy(self)


class SavedGameData:
    """
    This class contains attributes of a saved game data.
    """

    def __init__(self, trainer_name, temperature, top_p, top_k, max_output_tokens, trainer_data):
        # type: (str, float, float, float, int, Trainer) -> None
        self.trainer_name: str = trainer_name
        self.temperature: float = temperature
        self.top_p: float = top_p
        self.top_k: float = top_k
        self.max_output_tokens: int = max_output_tokens
        self.trainer_data: Trainer = trainer_data

    def __str__(self):
        # type: () -> str
        res: str = ""  # initial value
        res += str(self.trainer_name).upper() + "\n"
        res += "Temperature: " + str(self.temperature) + "\n"
        res += "Top P: " + str(self.top_p) + "\n"
        res += "Top K: " + str(self.top_k) + "\n"
        res += "Max output tokens: " + str(self.max_output_tokens) + "\n"
        return res

    def clone(self):
        # type: () -> SavedGameData
        return copy.deepcopy(self)


###########################################
# GENERAL
###########################################


# Creating main function used to run the game.


def main() -> int:
    """
    This main function is used to run the game.
    :return: an integer
    """

    load_dotenv()
    gemini.configure(api_key=os.environ['GEMINI_API_KEY'])

    # Gemini safety settings
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    # Saved game data
    saved_game_data: SavedGameData = (SavedGameData("", 0, 0, 0,
                                                    0, Trainer("NONE")))  # initial value

    # The player's trainer name
    player_trainer_name: str = ""  # initial value

    # Gemini Generative Model
    model = gemini.GenerativeModel(model_name="gemini-1.0-pro",
                                       generation_config={"temperature": 0.9,
                                                          "top_p": 1,
                                                          "top_k": 1,
                                                          "max_output_tokens": 2048,},
                                       safety_settings=safety_settings)  # initial value

    print("Enter \"NEW GAME\" to create new saved game data.")
    print("Enter \"LOAD GAME\" to load existing saved game data.")
    action: str = input("What do you want to do? ")
    while action not in ["NEW GAME", "LOAD GAME"]:
        clear()
        print("Enter \"NEW GAME\" to create new saved game data.")
        print("Enter \"LOAD GAME\" to load existing saved game data.")
        action = input("Sorry, invalid input! What do you want to do? ")

    game_started: bool = False
    while not game_started:
        if action == "NEW GAME":
            clear()

            # Asking user input values for generation config
            temperature: str = input("Please enter temperature (0 - 1): ")
            while not is_number(temperature) or float(temperature) < 0 or float(temperature) > 1:
                temperature = input("Sorry, invalid input! Please re-enter temperature (0 - 1): ")

            float_temperature: float = float(temperature)

            top_p: str = input("Please enter Top P (0 - 1): ")
            while not is_number(top_p) or float(top_p) < 0 or float(top_p) > 1:
                top_p = input("Sorry, invalid input! Please re-enter Top P (0 - 1): ")

            float_top_p: float = float(top_p)

            top_k: str = input("Please enter Top K (at least 1): ")
            while not is_number(top_k) or int(top_k) < 1:
                top_k = input("Sorry, invalid input! Please re-enter Top K (at least 1): ")

            float_top_k: int = int(top_k)

            max_output_tokens: str = input("Please enter maximum input tokens (at least 1): ")
            while not is_number(max_output_tokens) or int(max_output_tokens) < 1:
                max_output_tokens = input("Sorry, invalid input! Please re-enter maximum input tokens (at least 1): ")

            int_max_output_tokens: int = int(max_output_tokens)

            # Set up the model
            generation_config = {
                "temperature": float_temperature,
                "top_p": float_top_p,
                "top_k": float_top_k,
                "max_output_tokens": int_max_output_tokens,
            }

            model = gemini.GenerativeModel(model_name="gemini-1.0-pro",
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)

            player_trainer_name = input("Please enter trainer name: ")
            saved_game_files: list = [f for f in os.listdir("../saved")]
            while player_trainer_name in saved_game_files:
                print("Below is a list of existing saved game files:\n")
                for i in range(len(saved_game_files)):
                    print(str(i + 1) + ". " + str(saved_game_files[i]))

                player_trainer_name = input("Sorry, trainer name " + str(player_trainer_name) + " already exists! "
                                                                        "Enter another trainer name: ")

            saved_game_data = SavedGameData(player_trainer_name, float_temperature, float_top_p, float_top_k,
                                            int_max_output_tokens, Trainer(player_trainer_name))

            # Generate 5 random legendary creatures to be placed in player trainer's battle team.
            for i in range(5):
                new_legendary_creature: LegendaryCreature = (generate_random_legendary_creature
                                                             (random.choice(LegendaryCreature.POTENTIAL_ELEMENTS)))
                saved_game_data.trainer_data.add_legendary_creature(new_legendary_creature)
                saved_game_data.trainer_data.add_legendary_creature_to_team(new_legendary_creature)

            # Generate the city where the player is at.
            city_width: int = random.randint(6, 10)
            city_height: int = random.randint(6, 10)
            city_tiles: list = []  # initial value
            portals: int = 0  # initial value
            for y in range(city_height):
                curr_row: list = []
                for x in range(city_width):
                    if x == 0 and y == 0:
                        curr_row.append(PavementTile())
                    elif portals == 0:
                        if x == city_width - 1 and y == city_height - 1:
                            portals += 1
                            curr_row.append(PortalTile())
                        else:
                            curr_tile: str = random.choice(["PORTAL", "PAVEMENT", "GRASS"])
                            if curr_tile == "PORTAL":
                                portals += 1
                                curr_row.append(PortalTile())
                            elif curr_tile == "PAVEMENT":
                                curr_row.append(PavementTile())
                            elif curr_tile == "GRASS":
                                curr_row.append(GrassTile())
                    else:
                        curr_tile: str = random.choice(["PAVEMENT", "GRASS"])
                        if curr_tile == "PAVEMENT":
                            curr_row.append(PavementTile())
                        elif curr_tile == "GRASS":
                            curr_row.append(GrassTile())

                city_tiles.append(curr_row)
            convo = model.start_chat(history=[
            ])
            convo.send_message("Please enter a good name of a fictional city (safe one word response only please)!")
            city_name: str = str(convo.last.text)
            city: City = City(city_name, city_tiles)

            # Spawn player trainer
            saved_game_data.trainer_data.city = city
            saved_game_data.trainer_data.location = AdventureModeLocation(0, 0)
            city.get_tile_at(0, 0).add_trainer(saved_game_data.trainer_data)

            # Spawn 5 to 10 random AI trainers.
            num_ai_trainers: int = random.randint(5, 10)
            for i in range(num_ai_trainers):
                tile_x: int = random.randint(0, len(city.get_tiles()[0]) - 1)
                tile_y: int = random.randint(0, len(city.get_tiles()) - 1)
                while tile_x == 0 and tile_y == 0:
                    tile_x = random.randint(0, len(city.get_tiles()[0]) - 1)
                    tile_y = random.randint(0, len(city.get_tiles()) - 1)

                time.sleep(5)
                convo.send_message("Please enter a good male/female game character name "
                                   "(safe one word response only please)! ")
                ai_trainer_name: str = str(convo.last.text)
                ai_trainer: AITrainer = AITrainer(ai_trainer_name)
                average_player_battle_creature_level: int = (sum(legendary_creature.level for legendary_creature in
                                                         saved_game_data.trainer_data.battle_team.get_legendary_creatures())
                                                             // len(saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                for j in range(5):
                    new_legendary_creature: LegendaryCreature = (generate_random_legendary_creature
                                                                 (random.choice(LegendaryCreature.POTENTIAL_ELEMENTS)))
                    while new_legendary_creature.level < average_player_battle_creature_level:
                        new_legendary_creature.exp = new_legendary_creature.required_exp
                        new_legendary_creature.level_up()

                    ai_trainer.add_legendary_creature(new_legendary_creature)
                    ai_trainer.add_legendary_creature_to_team(new_legendary_creature)

                ai_trainer.location = AdventureModeLocation(tile_x, tile_y)
                city.get_tile_at(tile_x, tile_y).add_trainer(ai_trainer)

            game_started = True
        else:
            clear()

            saved_game_files: list = [f for f in os.listdir("../saved")]
            if len(saved_game_files) == 0:
                action = "NEW GAME"

            print("Below is a list of existing saved game files:\n")
            for i in range(len(saved_game_files)):
                print(str(i + 1) + ". " + str(saved_game_files[i]))

            player_trainer_name = input("Please enter trainer name associated with saved game data you want to load: ")
            while player_trainer_name not in saved_game_files:
                clear()
                print("Below is a list of existing saved game files:\n")
                for i in range(len(saved_game_files)):
                    print(str(i + 1) + ". " + str(saved_game_files[i]))

                player_trainer_name = input("Sorry, invalid input! Please enter trainer name associated with "
                                     "saved game data you want to load: ")

            saved_game_data = load_game_data(os.path.join("../saved", player_trainer_name))

            # Set up the model
            generation_config = {
                "temperature": saved_game_data.temperature,
                "top_p": saved_game_data.top_p,
                "top_k": saved_game_data.top_k,
                "max_output_tokens": saved_game_data.max_output_tokens,
            }

            model = gemini.GenerativeModel(model_name="gemini-1.0-pro",
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)
            game_started = True

    # Start playing the game.
    while True:
        clear()
        print("Enter \"Y\" for yes.")
        print("Enter anything else for no.")
        continue_playing: str = input("Do you want to continue playing? ")
        if continue_playing != "Y":
            save_game_data(saved_game_data, os.path.join("../saved", player_trainer_name))
            return 0  # successfully saved the game

        clear()

        print("Below is the representation of the city you are currently in:\n")
        print(str(saved_game_data.trainer_data.city) + "\n")

        # Implement possible actions the player can do in the game.
        allowed: list = ["MOVE TRAINER", "PLACE RUNE", "LEVEL UP RUNE",
                         "REMOVE RUNE", "BUY ITEM", "SELL ITEM", "USE ITEM", "MANAGE BATTLE TEAM", "VIEW STATS"]
        print("Enter \"MOVE TRAINER\" to move trainer in the map.")
        print("Enter \"PLACE RUNE\" to place a rune on a legendary creature.")
        print("Enter \"LEVEL UP RUNE\" to level up a rune.")
        print("Enter \"REMOVE RUNE\" to remove a rune from a legendary creature.")
        print("Enter \"BUY ITEM\" to buy an item from the item shop.")
        print("Enter \"SELL ITEM\" to sell an item you own.")
        print("Enter \"USE ITEM\" to use an item on a legendary creature.")
        print("Enter \"MANAGE BATTLE TEAM\" to manage your battle team.")
        print("Enter \"VIEW STATS\" to view your stats.")
        action: str = input("What do you want to do? ")
        while action not in allowed:
            print("Enter \"MOVE TRAINER\" to move trainer in the map.")
            print("Enter \"PLACE RUNE\" to place a rune on a legendary creature.")
            print("Enter \"LEVEL UP RUNE\" to level up a rune.")
            print("Enter \"REMOVE RUNE\" to remove a rune from a legendary creature.")
            print("Enter \"BUY ITEM\" to buy an item from the item shop.")
            print("Enter \"SELL ITEM\" to sell an item you own.")
            print("Enter \"USE ITEM\" to use an item on a legendary creature.")
            print("Enter \"MANAGE BATTLE TEAM\" to manage your battle team.")
            print("Enter \"VIEW STATS\" to view your stats.")
            action = input("Sorry, invalid input! What do you want to do? ")

        if action == "MOVE TRAINER":
            clear()
            direction: str = input("Please enter \"UP\", \"DOWN\", \"LEFT\", or \"RIGHT\"! ")
            while direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                direction = input("Sorry, invalid input! Please enter \"UP\", \"DOWN\", \"LEFT\", or \"RIGHT\"! ")

            if direction == "UP":
                saved_game_data.trainer_data.move_up()
            elif direction == "DOWN":
                saved_game_data.trainer_data.move_down()
            elif direction == "LEFT":
                saved_game_data.trainer_data.move_left()
            elif direction == "RIGHT":
                saved_game_data.trainer_data.move_right()

            # Checking the type of tile the player lands on.
            curr_tile: CityTile = saved_game_data.trainer_data.get_city_tile()
            if isinstance(curr_tile, PortalTile):
                # Generate the city where the player is at.
                city_width: int = random.randint(6, 10)
                city_height: int = random.randint(6, 10)
                city_tiles: list = []  # initial value
                portals: int = 0  # initial value
                for y in range(city_height):
                    curr_row: list = []
                    for x in range(city_width):
                        if x == 0 and y == 0:
                            curr_row.append(PavementTile())
                        elif portals == 0:
                            if x == city_width - 1 and y == city_height - 1:
                                portals += 1
                                curr_row.append(PortalTile())
                            else:
                                curr_tile: str = random.choice(["PORTAL", "PAVEMENT", "GRASS"])
                                if curr_tile == "PORTAL":
                                    portals += 1
                                    curr_row.append(PortalTile())
                                elif curr_tile == "PAVEMENT":
                                    curr_row.append(PavementTile())
                                elif curr_tile == "GRASS":
                                    curr_row.append(GrassTile())
                        else:
                            curr_tile: str = random.choice(["PAVEMENT", "GRASS"])
                            if curr_tile == "PAVEMENT":
                                curr_row.append(PavementTile())
                            elif curr_tile == "GRASS":
                                curr_row.append(GrassTile())

                    city_tiles.append(curr_row)
                convo = model.start_chat(history=[
                ])
                convo.send_message("Please enter a good name of a fictional city (safe one word response only please)!")
                city_name: str = str(convo.last.text)
                city: City = City(city_name, city_tiles)

                # Spawn player trainer
                saved_game_data.trainer_data.city = city
                saved_game_data.trainer_data.location = AdventureModeLocation(0, 0)
                city.get_tile_at(0, 0).add_trainer(saved_game_data.trainer_data)

                # Spawn 5 to 10 random AI trainers.
                num_ai_trainers: int = random.randint(5, 10)
                for i in range(num_ai_trainers):
                    tile_x: int = random.randint(0, len(city.get_tiles()[0]) - 1)
                    tile_y: int = random.randint(0, len(city.get_tiles()) - 1)
                    while tile_x == 0 and tile_y == 0:
                        tile_x = random.randint(0, len(city.get_tiles()[0]) - 1)
                        tile_y = random.randint(0, len(city.get_tiles()) - 1)

                    time.sleep(5)
                    convo.send_message("Please enter a good male/female game character name "
                                       "(safe one word response only please)! ")
                    ai_trainer_name: str = str(convo.last.text)
                    ai_trainer: AITrainer = AITrainer(ai_trainer_name)
                    average_player_battle_creature_level: int = (sum(legendary_creature.level for legendary_creature in
                                                                     saved_game_data.trainer_data.battle_team.get_legendary_creatures())
                                                                 // len(
                                saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                    for j in range(5):
                        new_legendary_creature: LegendaryCreature = (generate_random_legendary_creature
                                                                     (random.choice(
                                                                         LegendaryCreature.POTENTIAL_ELEMENTS)))
                        while new_legendary_creature.level < average_player_battle_creature_level:
                            new_legendary_creature.exp = new_legendary_creature.required_exp
                            new_legendary_creature.level_up()

                        ai_trainer.add_legendary_creature(new_legendary_creature)
                        ai_trainer.add_legendary_creature_to_team(new_legendary_creature)

                    ai_trainer.location = AdventureModeLocation(tile_x, tile_y)
                    city.get_tile_at(tile_x, tile_y).add_trainer(ai_trainer)
            elif isinstance(curr_tile, GrassTile):
                # Determine if a wild or trainer battle occurs or not.
                wild_battle_occurs: bool = random.random() < 0.5
                if wild_battle_occurs:
                    wild_legendary_creature: LegendaryCreature = (generate_random_legendary_creature
                                                                  (random.choice(LegendaryCreature.POTENTIAL_ELEMENTS)))
                    average_player_battle_creature_level: int = (sum(legendary_creature.level for legendary_creature in
                                                                     saved_game_data.trainer_data.battle_team.get_legendary_creatures())
                                                                 // len(
                                saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                    while wild_legendary_creature.level < average_player_battle_creature_level:
                        wild_legendary_creature.exp = wild_legendary_creature.required_exp
                        wild_legendary_creature.level_up()

                    wild_battle: WildBattle = WildBattle(saved_game_data.trainer_data, wild_legendary_creature)
                    while not wild_battle.wild_legendary_creature_caught and not wild_battle.trainer_fled \
                        and wild_battle.winner is None:
                        print("Below are the current stats of your legendary creatures.\n")
                        creature_number: int = 1
                        for legendary_creature in saved_game_data.trainer_data.battle_team.get_legendary_creatures():
                            print(str(creature_number) + ". " + str(legendary_creature))
                            creature_number += 1

                        print("\n")
                        print("Below are the current stats of the wild legendary creature.\n")
                        print(wild_legendary_creature)
                        print("\n")

                        wild_battle.get_someone_to_move()
                        if wild_battle.whose_turn == wild_legendary_creature:
                            chosen_action: str = random.choice(Action.POSSIBLE_NAMES)
                            if chosen_action == "NORMAL HEAL":
                                wild_legendary_creature.have_turn(wild_legendary_creature, None, chosen_action)
                            elif chosen_action == "NORMAL ATTACK":
                                target: LegendaryCreature = (
                                    random.choice(saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                                wild_legendary_creature.have_turn(target, None, chosen_action)
                            elif chosen_action == "USE SKILL":
                                skill_to_use: Skill = random.choice(wild_legendary_creature.get_skills())
                                if skill_to_use.skill_type == "HEAL":
                                    wild_legendary_creature.have_turn(wild_legendary_creature, skill_to_use, chosen_action)
                                elif skill_to_use.skill_type == "ATTACK":
                                    target: LegendaryCreature = (
                                        random.choice(
                                            saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                                    wild_legendary_creature.have_turn(target, skill_to_use, chosen_action)
                                else:
                                    pass
                            else:
                                pass
                        else:
                            print("Enter \"NORMAL ATTACK\" for normal attack!")
                            print("Enter \"NORMAL HEAL\" for normal heal!")
                            print("Enter \"USE SKILL\" to use a skill!")
                            print("Enter \"FLEE\" to flee from the wild battle!")
                            print("Enter \"CATCH\" to catch wild legendary creature!")
                            battle_action: str = input("What do you want to do? ")
                            while battle_action not in ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL", "FLEE", "CATCH"]:
                                print("Enter \"NORMAL ATTACK\" for normal attack!")
                                print("Enter \"NORMAL HEAL\" for normal heal!")
                                print("Enter \"USE SKILL\" to use a skill!")
                                print("Enter \"FLEE\" to flee from the wild battle!")
                                print("Enter \"CATCH\" to catch wild legendary creature!")
                                battle_action = input("Sorry, invalid input! What do you want to do? ")

                            if battle_action == "NORMAL ATTACK":
                                wild_battle.whose_turn.have_turn(wild_legendary_creature, None, battle_action)
                            elif battle_action == "NORMAL HEAL":
                                wild_battle.whose_turn.have_turn(wild_battle.whose_turn, None, battle_action)
                            elif battle_action == "USE SKILL":
                                print("Below are the skills that you can use:\n")
                                skill_number: int = 1
                                for skill in wild_battle.whose_turn.get_skills():
                                    print(str(skill_number) + ". " + str(skill))
                                    skill_number += 1

                                skill_index: int = int(input("Please enter the index of the skill you want to "
                                                             "use (1 - " +
                                                             str(len(wild_battle.whose_turn.get_skills())) + "): "))
                                while skill_index < 1 or skill_index > len(wild_battle.whose_turn.get_skills()):
                                    skill_index = int(input("Sorry, invalid input! Please enter the index of the skill you want to "
                                                                 "use (1 - " +
                                                                 str(len(wild_battle.whose_turn.get_skills())) + "): "))

                                skill_to_use: Skill = wild_battle.whose_turn.get_skills()[skill_index - 1]
                                if skill_to_use.skill_type == "HEAL":
                                    wild_battle.whose_turn.have_turn(wild_battle.whose_turn, skill_to_use, battle_action)
                                elif skill_to_use.skill_type == "ATTACK":
                                    wild_battle.whose_turn.have_turn(wild_legendary_creature, skill_to_use,
                                                                     battle_action)
                                else:
                                    pass
                            elif battle_action == "FLEE":
                                flee_success: bool = random.random() < 0.75
                                if flee_success:
                                    print("You successfully fled!")
                                    wild_battle.trainer_fled = True
                                    break
                                else:
                                    print("Sorry! You can't run away!")
                            elif battle_action == "CATCH":
                                ball_objects: list = [item for item in
                                                      saved_game_data.trainer_data.item_inventory.get_items() if
                                                      isinstance(item, Ball)]
                                ball_number: int = 1
                                for ball in ball_objects:
                                    print(str(ball_number) + ". " + str(ball))
                                    ball_number += 1

                                ball_index: int = int(input("Please enter the index of the ball you want to use "
                                                            "(1 - " + str(len(ball_objects)) + "): "))
                                while ball_index < 1 or ball_index > len(ball_objects):
                                    ball_index = int(input("Sorry, invalid input! Please enter the index of the ball "
                                                           "you want to use (1 - " + str(len(ball_objects)) + "): "))

                                ball_to_use: Ball = ball_objects[ball_index - 1]
                                catch_success: bool = random.random() < ball_to_use.catch_success_rate
                                if catch_success:
                                    print("You successfully caught " + str(wild_legendary_creature.name) + "!")
                                    saved_game_data.trainer_data.add_legendary_creature(wild_legendary_creature)
                                    saved_game_data.trainer_data.add_legendary_creature_to_team(wild_legendary_creature)
                                else:
                                    print("Cannot catch " + str(wild_legendary_creature.name) + "!")
                            else:
                                pass

                        if not wild_legendary_creature.get_is_alive():
                            wild_battle.winner = wild_battle.trainer1.battle_team
                            print("You won the battle!")
                            saved_game_data.trainer_data.claim_reward(wild_battle.reward)
                            wild_battle.trainer1.battle_team.recover_all()
                            break

                        if wild_battle.trainer1.battle_team.all_died():
                            wild_battle.winner = BattleTeam([wild_legendary_creature])
                            print("You lost!")
                            wild_battle.trainer1.battle_team.recover_all()
                            break

                else:
                    if len(curr_tile.get_trainers()) > 1:
                        trainer_battle_occurs: bool = random.random() < 0.5
                        if trainer_battle_occurs:
                            other_trainer: Trainer = random.choice(curr_tile.get_trainers())
                            while other_trainer == saved_game_data.trainer_data:
                                other_trainer = random.choice(curr_tile.get_trainers())

                            trainer_battle: TrainerBattle = TrainerBattle(saved_game_data.trainer_data, other_trainer)
                            while trainer_battle.winner is None:
                                print("Below are the current stats of your legendary creatures.\n")
                                creature_number: int = 1
                                for legendary_creature in saved_game_data.trainer_data.battle_team.get_legendary_creatures():
                                    print(str(creature_number) + ". " + str(legendary_creature))
                                    creature_number += 1

                                print("Below are the current stats of your opponent's legendary creatures.\n")
                                other_creature_number: int = 1
                                for legendary_creature in trainer_battle.trainer2.battle_team.get_legendary_creatures():
                                    print(str(other_creature_number) + ". " + str(legendary_creature))
                                    other_creature_number += 1

                                trainer_battle.get_someone_to_move()
                                if trainer_battle.whose_turn in other_trainer.battle_team.get_legendary_creatures():
                                    chosen_action: str = random.choice(Action.POSSIBLE_NAMES)
                                    if chosen_action == "NORMAL HEAL":
                                        trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, None, chosen_action)
                                    elif chosen_action == "NORMAL ATTACK":
                                        target: LegendaryCreature = (
                                            random.choice(
                                                saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                                        trainer_battle.whose_turn.have_turn(target, None, chosen_action)
                                    elif chosen_action == "USE SKILL":
                                        skill_to_use: Skill = random.choice(trainer_battle.whose_turn.get_skills())
                                        if skill_to_use.skill_type == "HEAL":
                                            trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, skill_to_use, chosen_action)
                                        elif skill_to_use.skill_type == "ATTACK":
                                            target: LegendaryCreature = (
                                                random.choice(
                                                    saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                                            trainer_battle.whose_turn.have_turn(target, skill_to_use, chosen_action)
                                        else:
                                            pass
                                    else:
                                        pass
                                else:
                                    print("Enter \"NORMAL ATTACK\" for normal attack!")
                                    print("Enter \"NORMAL HEAL\" for normal heal!")
                                    print("Enter \"USE SKILL\" to use a skill!")
                                    battle_action: str = input("What do you want to do? ")
                                    while battle_action not in ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL"]:
                                        print("Enter \"NORMAL ATTACK\" for normal attack!")
                                        print("Enter \"NORMAL HEAL\" for normal heal!")
                                        print("Enter \"USE SKILL\" to use a skill!")
                                        battle_action = input("Sorry, invalid input! What do you want to do? ")

                                    if battle_action == "NORMAL ATTACK":
                                        print("Below is a list of legendary creatures you can attack:\n")
                                        creature_index: int = 1
                                        for legendary_creature in other_trainer.battle_team.get_legendary_creatures():
                                            print(str(creature_index) + ". " + str(legendary_creature))
                                            creature_index += 1

                                        target_index: int = int(input("Please enter the index of the legendary creature "
                                                                      "you want to attack (1 - " +
                                                                      str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                                      "): "))
                                        while target_index < 1 or target_index > len(other_trainer.battle_team.get_legendary_creatures()):
                                            target_index = int(
                                                input("Sorry, invalid input! Please enter the index of the legendary creature "
                                                      "you want to attack (1 - " +
                                                      str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                      "): "))

                                        target_creature: LegendaryCreature = (
                                            other_trainer.battle_team.get_legendary_creatures())[target_index - 1]
                                        trainer_battle.whose_turn.have_turn(target_creature, None, battle_action)
                                    elif battle_action == "NORMAL HEAL":
                                        trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, None, battle_action)
                                    elif battle_action == "USE SKILL":
                                        print("Below are the skills that you can use:\n")
                                        skill_number: int = 1
                                        for skill in trainer_battle.whose_turn.get_skills():
                                            print(str(skill_number) + ". " + str(skill))
                                            skill_number += 1

                                        skill_index: int = int(input("Please enter the index of the skill you want to "
                                                                     "use (1 - " +
                                                                     str(len(
                                                                         trainer_battle.whose_turn.get_skills())) + "): "))
                                        while skill_index < 1 or skill_index > len(trainer_battle.whose_turn.get_skills()):
                                            skill_index = int(input(
                                                "Sorry, invalid input! Please enter the index of the skill you want to "
                                                "use (1 - " +
                                                str(len(trainer_battle.whose_turn.get_skills())) + "): "))

                                        skill_to_use: Skill = trainer_battle.whose_turn.get_skills()[skill_index - 1]
                                        if skill_to_use.skill_type == "HEAL":
                                            trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, skill_to_use, battle_action)
                                        elif skill_to_use.skill_type == "ATTACK":
                                            print("Below is a list of legendary creatures you can attack:\n")
                                            creature_index: int = 1
                                            for legendary_creature in other_trainer.battle_team.get_legendary_creatures():
                                                print(str(creature_index) + ". " + str(legendary_creature))
                                                creature_index += 1

                                            target_index: int = int(
                                                input("Please enter the index of the legendary creature "
                                                      "you want to attack (1 - " +
                                                      str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                      "): "))
                                            while target_index < 1 or target_index > len(
                                                    other_trainer.battle_team.get_legendary_creatures()):
                                                target_index = int(
                                                    input(
                                                        "Sorry, invalid input! Please enter the index of the legendary creature "
                                                        "you want to attack (1 - " +
                                                        str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                        "): "))

                                            target_creature: LegendaryCreature = (
                                                other_trainer.battle_team.get_legendary_creatures())[target_index - 1]
                                            trainer_battle.whose_turn.have_turn(target_creature, skill_to_use, battle_action)
                                        else:
                                            pass
                                    else:
                                        pass

                                    if trainer_battle.trainer2.battle_team.all_died():
                                        trainer_battle.winner = trainer_battle.trainer1.battle_team
                                        print("You won the battle!")
                                        saved_game_data.trainer_data.claim_reward(trainer_battle.reward)
                                        trainer_battle.trainer1.battle_team.recover_all()
                                        trainer_battle.trainer2.battle_team.recover_all()
                                        break

                                    if trainer_battle.trainer1.battle_team.all_died():
                                        trainer_battle.winner = trainer_battle.trainer2.battle_team
                                        print("You lost!")
                                        trainer_battle.trainer2.claim_reward(trainer_battle.reward)
                                        trainer_battle.trainer1.battle_team.recover_all()
                                        trainer_battle.trainer2.battle_team.recover_all()
                                        break

            elif isinstance(curr_tile, PavementTile):
                # Determine if a trainer battle occurs or not.
                if len(curr_tile.get_trainers()) > 1:
                    trainer_battle_occurs: bool = random.random() < 0.5
                    if trainer_battle_occurs:
                        other_trainer: Trainer = random.choice(curr_tile.get_trainers())
                        while other_trainer == saved_game_data.trainer_data:
                            other_trainer = random.choice(curr_tile.get_trainers())

                        trainer_battle: TrainerBattle = TrainerBattle(saved_game_data.trainer_data, other_trainer)
                        while trainer_battle.winner is None:
                            print("Below are the current stats of your legendary creatures.\n")
                            creature_number: int = 1
                            for legendary_creature in saved_game_data.trainer_data.battle_team.get_legendary_creatures():
                                print(str(creature_number) + ". " + str(legendary_creature))
                                creature_number += 1

                            print("Below are the current stats of your opponent's legendary creatures.\n")
                            other_creature_number: int = 1
                            for legendary_creature in trainer_battle.trainer2.battle_team.get_legendary_creatures():
                                print(str(other_creature_number) + ". " + str(legendary_creature))
                                other_creature_number += 1

                            trainer_battle.get_someone_to_move()
                            if trainer_battle.whose_turn in other_trainer.battle_team.get_legendary_creatures():
                                chosen_action: str = random.choice(Action.POSSIBLE_NAMES)
                                if chosen_action == "NORMAL HEAL":
                                    trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, None, chosen_action)
                                elif chosen_action == "NORMAL ATTACK":
                                    target: LegendaryCreature = (
                                        random.choice(
                                            saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                                    trainer_battle.whose_turn.have_turn(target, None, chosen_action)
                                elif chosen_action == "USE SKILL":
                                    skill_to_use: Skill = random.choice(trainer_battle.whose_turn.get_skills())
                                    if skill_to_use.skill_type == "HEAL":
                                        trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, skill_to_use, chosen_action)
                                    elif skill_to_use.skill_type == "ATTACK":
                                        target: LegendaryCreature = (
                                            random.choice(
                                                saved_game_data.trainer_data.battle_team.get_legendary_creatures()))
                                        trainer_battle.whose_turn.have_turn(target, skill_to_use, chosen_action)
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                print("Enter \"NORMAL ATTACK\" for normal attack!")
                                print("Enter \"NORMAL HEAL\" for normal heal!")
                                print("Enter \"USE SKILL\" to use a skill!")
                                battle_action: str = input("What do you want to do? ")
                                while battle_action not in ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL"]:
                                    print("Enter \"NORMAL ATTACK\" for normal attack!")
                                    print("Enter \"NORMAL HEAL\" for normal heal!")
                                    print("Enter \"USE SKILL\" to use a skill!")
                                    battle_action = input("Sorry, invalid input! What do you want to do? ")

                                if battle_action == "NORMAL ATTACK":
                                    print("Below is a list of legendary creatures you can attack:\n")
                                    creature_index: int = 1
                                    for legendary_creature in other_trainer.battle_team.get_legendary_creatures():
                                        print(str(creature_index) + ". " + str(legendary_creature))
                                        creature_index += 1

                                    target_index: int = int(input("Please enter the index of the legendary creature "
                                                                  "you want to attack (1 - " +
                                                                  str(len(
                                                                      other_trainer.battle_team.get_legendary_creatures())) +
                                                                  "): "))
                                    while target_index < 1 or target_index > len(
                                            other_trainer.battle_team.get_legendary_creatures()):
                                        target_index = int(
                                            input(
                                                "Sorry, invalid input! Please enter the index of the legendary creature "
                                                "you want to attack (1 - " +
                                                str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                "): "))

                                    target_creature: LegendaryCreature = (
                                        other_trainer.battle_team.get_legendary_creatures())[target_index - 1]
                                    trainer_battle.whose_turn.have_turn(target_creature, None, battle_action)
                                elif battle_action == "NORMAL HEAL":
                                    trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, None, battle_action)
                                elif battle_action == "USE SKILL":
                                    print("Below are the skills that you can use:\n")
                                    skill_number: int = 1
                                    for skill in trainer_battle.whose_turn.get_skills():
                                        print(str(skill_number) + ". " + str(skill))
                                        skill_number += 1

                                    skill_index: int = int(input("Please enter the index of the skill you want to "
                                                                 "use (1 - " +
                                                                 str(len(
                                                                     trainer_battle.whose_turn.get_skills())) + "): "))
                                    while skill_index < 1 or skill_index > len(trainer_battle.whose_turn.get_skills()):
                                        skill_index = int(input(
                                            "Sorry, invalid input! Please enter the index of the skill you want to "
                                            "use (1 - " +
                                            str(len(trainer_battle.whose_turn.get_skills())) + "): "))

                                    skill_to_use: Skill = trainer_battle.whose_turn.get_skills()[skill_index - 1]
                                    if skill_to_use.skill_type == "HEAL":
                                        trainer_battle.whose_turn.have_turn(trainer_battle.whose_turn, skill_to_use, battle_action)
                                    elif skill_to_use.skill_type == "ATTACK":
                                        print("Below is a list of legendary creatures you can attack:\n")
                                        creature_index: int = 1
                                        for legendary_creature in other_trainer.battle_team.get_legendary_creatures():
                                            print(str(creature_index) + ". " + str(legendary_creature))
                                            creature_index += 1

                                        target_index: int = int(
                                            input("Please enter the index of the legendary creature "
                                                  "you want to attack (1 - " +
                                                  str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                  "): "))
                                        while target_index < 1 or target_index > len(
                                                other_trainer.battle_team.get_legendary_creatures()):
                                            target_index = int(
                                                input(
                                                    "Sorry, invalid input! Please enter the index of the legendary creature "
                                                    "you want to attack (1 - " +
                                                    str(len(other_trainer.battle_team.get_legendary_creatures())) +
                                                    "): "))

                                        target_creature: LegendaryCreature = (
                                            other_trainer.battle_team.get_legendary_creatures())[target_index - 1]
                                        trainer_battle.whose_turn.have_turn(target_creature, skill_to_use, battle_action)
                                    else:
                                        pass
                                else:
                                    pass

                                if trainer_battle.trainer2.battle_team.all_died():
                                    trainer_battle.winner = trainer_battle.trainer1.battle_team
                                    print("You won the battle!")
                                    saved_game_data.trainer_data.claim_reward(trainer_battle.reward)
                                    trainer_battle.trainer1.battle_team.recover_all()
                                    trainer_battle.trainer2.battle_team.recover_all()
                                    break

                                if trainer_battle.trainer1.battle_team.all_died():
                                    trainer_battle.winner = trainer_battle.trainer2.battle_team
                                    print("You lost!")
                                    trainer_battle.trainer2.claim_reward(trainer_battle.reward)
                                    trainer_battle.trainer1.battle_team.recover_all()
                                    trainer_battle.trainer2.battle_team.recover_all()
                                    break
            else:
                pass
        elif action == "PLACE RUNE":
            clear()
            runes: list = [item for item in saved_game_data.trainer_data.item_inventory.get_items() if
                           isinstance(item, Rune) and not item.already_placed]
            if len(runes) == 0:
                print("Cannot place any rune!")
            else:
                print("Below is the list of runes you can place to a legendary creature.\n")
                rune_number: int = 1  # initial value
                for rune in runes:
                    print(str(rune_number) + ". " + str(rune))
                    rune_number += 1

                rune_index: int = int(input("Please enter the index of the rune you want to place (1 - " +
                                            str(len(runes)) + "): "))
                while rune_index < 1 or rune_index > len(runes):
                    rune_index = int(input("Sorry, invalid input! Please enter the index of the rune you "
                                           "want to place (1 - " + str(len(runes)) + "): "))

                rune_to_place: Rune = runes[rune_index - 1]
                print("Below is a list of legendary creatures you can place a rune to.\n")
                creature_number: int = 1  # initial value
                for legendary_creature in saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures():
                    print(str(creature_number) + ". " + str(legendary_creature))
                    creature_number += 1

                creature_index: int = int(input("Please enter the index of the legendary creature you want to place the "
                                                "rune to (1 - " +
                                                str(len(saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures())) +
                                                "): "))
                while creature_index < 1 or creature_index > len(saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures()):
                    creature_index = int(
                        input("Sorry, invalid input! Please enter the index of the legendary creature you want to place the "
                              "rune to (1 - " +
                              str(len(
                                  saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures())) +
                              "): "))

                chosen_creature: LegendaryCreature = saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures()[creature_index - 1]
                saved_game_data.trainer_data.place_rune_on_legendary_creature(chosen_creature, rune_to_place)
        elif action == "LEVEL UP RUNE":
            clear()
            runes: list = [item for item in saved_game_data.trainer_data.item_inventory.get_items() if
                           isinstance(item, Rune)]
            if len(runes) == 0:
                print("Cannot level up any rune!")
            else:
                print("Below is the list of runes you can level up.\n")
                rune_number: int = 1  # initial value
                for rune in runes:
                    print(str(rune_number) + ". " + str(rune))
                    rune_number += 1

                rune_index: int = int(input("Please enter the index of the rune you want to level up (1 - " +
                                            str(len(runes)) + "): "))
                while rune_index < 1 or rune_index > len(runes):
                    rune_index = int(input("Sorry, invalid input! Please enter the index of the rune you "
                                           "want to level up (1 - " + str(len(runes)) + "): "))

                rune_to_level_up: Rune = runes[rune_index - 1]
                saved_game_data.trainer_data.level_up_rune(rune_to_level_up)
        elif action == "REMOVE RUNE":
            clear()
            runes: list = [item for item in saved_game_data.trainer_data.item_inventory.get_items() if
                           isinstance(item, Rune) and item.already_placed]
            if len(runes) == 0:
                print("Cannot remove any rune!")
            else:
                print("Below is the list of runes you can remove.\n")
                rune_number: int = 1  # initial value
                for rune in runes:
                    print(str(rune_number) + ". " + str(rune))
                    rune_number += 1

                rune_index: int = int(input("Please enter the index of the rune you want to remove (1 - " +
                                            str(len(runes)) + "): "))
                while rune_index < 1 or rune_index > len(runes):
                    rune_index = int(input("Sorry, invalid input! Please enter the index of the rune you "
                                           "want to remove (1 - " + str(len(runes)) + "): "))

                rune_to_remove: Rune = runes[rune_index - 1]
                corresponding_legendary_creature: LegendaryCreature = [legendary_creature for legendary_creature in
                                                                       saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures()
                                                                       if rune_to_remove in legendary_creature.get_runes().values()][0]
                saved_game_data.trainer_data.remove_rune_from_legendary_creature(corresponding_legendary_creature, rune_to_remove.slot_number)
        elif action == "BUY ITEM":
            clear()
            items_sold: list = []  # initial value
            num_items: int = random.randint(30, 50)

            # Populating the items in the item shop
            for i in range(num_items):
                item_type: str = random.choice(["BALL", "RUNE", "AWAKEN SHARD", "EXP SHARD", "LEVEL UP SHARD",
                "SKILL LEVEL UP SHARD"])
                if item_type == "BALL":
                    convo = model.start_chat(history=[
                    ])
                    convo.send_message("Please enter a good name of a ball to catch a monster like in Pokemon games "
                                       "(safe one word response only please)!")
                    ball_name: str = str(convo.last.text)
                    gold_cost: mpf = random.randint(1, 9) * mpf("10") ** random.randint(5, 10)
                    new_ball: Ball = Ball(ball_name, "A ball to catch a legendary creature.", gold_cost,
                                          mpf(random.randint(50, 100) / 100))
                    items_sold.append(new_ball)
                elif item_type == "RUNE":
                    convo = model.start_chat(history=[
                    ])
                    convo.send_message("Please enter a good name of a rune to strengthen legendary creatures "
                                       "(safe one word response only please)!")
                    rune_name: str = str(convo.last.text)
                    gold_cost: mpf = random.randint(1, 9) * mpf("10") ** random.randint(5, 10)
                    rating: int = random.randint(Rune.MIN_RATING, Rune.MAX_RATING)
                    slot_number: int = random.randint(Rune.MIN_SLOT_NUMBER, Rune.MAX_SLOT_NUMBER)
                    new_rune: Rune = Rune(rune_name, "A rune to strengthen legendary creatures.", gold_cost,
                                          rating, slot_number, rating, rating, rating, rating, rating * 2,
                                          rating * mpf("0.01"), rating * mpf("0.05"))
                    items_sold.append(new_rune)
                elif item_type == "AWAKEN SHARD":
                    new_awaken_shard: AwakenShard = AwakenShard("Awaken Shard", "A shard to immediately "
                                                                                "awaken a legendary creature.", mpf("5e7"),
                                                                random.choice(LegendaryCreature.POTENTIAL_ELEMENTS))
                    items_sold.append(new_awaken_shard)
                elif item_type == "EXP SHARD":
                    gold_cost: mpf = random.randint(1, 9) * mpf("10") ** random.randint(6, 11)
                    exp_granted: mpf = random.randint(1, 9) * mpf("10") ** random.randint(5, 10)
                    new_exp_shard: EXPShard = EXPShard("EXP Shard", "An EXP shard used to immediately increase the EXP of a legendary creature.",
                                                       gold_cost, exp_granted)
                    items_sold.append(new_exp_shard)
                elif item_type == "LEVEL UP SHARD":
                    new_level_up_shard: LevelUpShard = LevelUpShard("Level Up Shard", "A shard to immediately "
                                                                                "level up a legendary creature.", mpf("5e7"))
                    items_sold.append(new_level_up_shard)
                elif item_type == "SKILL LEVEL UP SHARD":
                    new_skill_level_up_shard: SkillLevelUpShard = SkillLevelUpShard("Skill Level Up Shard", "A shard to immediately "
                                                                                      "level up a skill a legendary creature has.",
                                                                    mpf("5e7"))
                    items_sold.append(new_skill_level_up_shard)
                else:
                    pass

            item_shop: ItemShop = ItemShop(items_sold)
            print("Below is a list of items in the item shop.\n")
            item_number: int = 1
            for item in item_shop.get_items_sold():
                print(str(item_number) + ". " + str(item))
                item_number += 1

            item_index: int = int(input("Please enter the index of the item you want to buy (1 - " +
                                        str(len(item_shop.get_items_sold())) + "): "))
            while item_index < 1 or item_index > len(item_shop.get_items_sold()):
                item_index = int(input("Sorry, invalid input! Please enter the index of the item you want to buy (1 - " +
                                            str(len(item_shop.get_items_sold())) + "): "))

            item_to_buy: Item = item_shop.get_items_sold()[item_index - 1]
            saved_game_data.trainer_data.purchase_item(item_to_buy)
        elif action == "SELL ITEM":
            clear()
            placed_runes: list = [item for item in saved_game_data.trainer_data.item_inventory.get_items()
                                  if isinstance(item, Rune) and item.already_placed]
            can_be_sold: list = [item for item in saved_game_data.trainer_data.item_inventory.get_items()
                                 if item not in placed_runes]
            if len(can_be_sold) == 0:
                print("Cannot sell any items!")
            else:
                item_number: int = 1
                print("Below is a list of items you can sell.\n")
                for item in can_be_sold:
                    print(str(item_number) + ". " + str(item))
                    item_number += 1

                item_index: int = int(input("Please enter the index of the item you want to sell (1 - "
                                            + str(len(can_be_sold)) + "): "))
                while item_index < 1 or item_index > len(can_be_sold):
                    item_index = int(input("Sorry, invalid input! Please enter the index of the item you want to sell (1 - "
                                                + str(len(can_be_sold)) + "): "))

                item_to_sell: Item = can_be_sold[item_index - 1]
                saved_game_data.trainer_data.sell_item(item_to_sell)
        elif action == "USE ITEM":
            clear()
            usable_items: list = [item for item in saved_game_data.trainer_data.item_inventory.get_items()
                                  if not isinstance(item, Rune) and not isinstance(item, Ball)]
            if len(usable_items) == 0:
                print("Cannot use any items!")
            else:
                print("Below is a list of items you can use on a legendary creature.\n")
                item_number: int = 1
                for item in usable_items:
                    print(str(item_number) + ". " + str(item))
                    item_number += 1

                item_index: int = int(input("Please enter the index of the item you want to use (1 - "
                                            + str(len(usable_items)) + "): "))
                while item_index < 1 or item_index > len(usable_items):
                    item_index = int(input("Sorry, invalid input! Please enter the index of the item you want to use (1 - "
                                           + str(len(usable_items)) + "): "))

                item_to_use: Item = usable_items[item_index - 1]
                print("Below is a list of legendary creatures you can use the item on.\n")
                creature_number: int = 1
                for legendary_creature in saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures():
                    print(str(creature_number) + ". " + str(legendary_creature))
                    creature_number += 1

                creature_index: int = int(input("Please enter the index of the legendary creature you want "
                                                "to use the item on (1 - "
                                                + str(len(saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures())) + "): "))
                while creature_index < 1 or creature_index > len(saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures()):
                    creature_index = int(input("Sorry, invalid input! Please enter the index of the legendary creature you want "
                                                    "to use the item on (1 - "
                                                    + str(
                        len(saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures())) + "): "))

                chosen_creature: LegendaryCreature = saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures()[creature_index - 1]
                if isinstance(item_to_use, AwakenShard):
                    if chosen_creature.awaken():
                        saved_game_data.trainer_data.remove_item_from_inventory(item_to_use)
                    else:
                        print(str(chosen_creature.name) + " has been awakened!")
                elif isinstance(item_to_use, LevelUpShard):
                    chosen_creature.exp = chosen_creature.required_exp
                    chosen_creature.level_up()
                elif isinstance(item_to_use, EXPShard):
                    chosen_creature.exp += item_to_use.exp_granted
                    chosen_creature.level_up()
                elif isinstance(item_to_use, SkillLevelUpShard):
                    chosen_skill: Skill = random.choice(chosen_creature.get_skills())
                    chosen_skill.level_up()
                else:
                    pass
        elif action == "MANAGE BATTLE TEAM":
            clear()
            print("Enter \"ADD LEGENDARY CREATURE\" to add legendary creature to your battle team.")
            print("Enter \"REMOVE LEGENDARY CREATURE\" to remove legendary creature from your battle team.")
            chosen_action: str = input("What do you want to do? ")
            while chosen_action not in ["ADD LEGENDARY CREATURE", "REMOVE LEGENDARY CREATURE"]:
                print("Enter \"ADD LEGENDARY CREATURE\" to add legendary creature to your battle team.")
                print("Enter \"REMOVE LEGENDARY CREATURE\" to remove legendary creature from your battle team.")
                chosen_action = input("Sorry, invalid input! What do you want to do? ")

            if chosen_action == "ADD LEGENDARY CREATURE":
                if len(saved_game_data.trainer_data.battle_team.get_legendary_creatures()) \
                    < BattleTeam.MAX_LEGENDARY_CREATURES:
                    print("Below is a list of legendary creatures you can add to the team.\n")
                    creature_number: int = 1
                    available_creatures: list = [legendary_creature for legendary_creature in
                                                 saved_game_data.trainer_data.legendary_creature_inventory.get_legendary_creatures()
                                                 if legendary_creature.corresponding_team is None]
                    for legendary_creature in available_creatures:
                        print(str(creature_number) + ". " + str(legendary_creature))
                        creature_number += 1

                    creature_index: int = int(input("Please enter the index of the legendary creature you want to add (1 - " +
                                                    str(len(available_creatures)) + "): "))
                    while creature_index < 1 or creature_index >= len(available_creatures):
                        creature_index = int(
                            input("Sorry, invalid input! Please enter the index of the legendary creature you want to add (1 - " +
                                  str(len(available_creatures)) + "): "))

                    creature_to_add: LegendaryCreature = available_creatures[creature_index - 1]
                    saved_game_data.trainer_data.add_legendary_creature_to_team(creature_to_add)
                else:
                    print("Cannot add a legendary creature to your battle team.")
            elif chosen_action == "REMOVE LEGENDARY CREATURE":
                if len(saved_game_data.trainer_data.battle_team.get_legendary_creatures()) == 0:
                    print("There are no legendary creatures you can remove from the team.")
                else:
                    print("Below is a list of legendary creatures you can remove from the team.\n")
                    creature_number: int = 1
                    for legendary_creature in saved_game_data.trainer_data.battle_team.get_legendary_creatures():
                        print(str(creature_number) + ". " + str(legendary_creature))
                        creature_number += 1

                    creature_index: int = int(
                        input("Please enter the index of the legendary creature you want to remove (1 - " +
                              str(len(saved_game_data.trainer_data.battle_team.get_legendary_creatures())) + "): "))
                    while creature_index < 1 or creature_index >= len(saved_game_data.trainer_data.battle_team.get_legendary_creatures()):
                        creature_index = int(
                            input(
                                "Sorry, invalid input! Please enter the index of the legendary creature you want to remove (1 - " +
                                str(len(saved_game_data.trainer_data.battle_team.get_legendary_creatures())) + "): "))

                    creature_to_remove: LegendaryCreature = saved_game_data.trainer_data.battle_team.get_legendary_creatures()[creature_index - 1]
                    saved_game_data.trainer_data.remove_legendary_creature_from_team(creature_to_remove)
            else:
                pass
        elif action == "VIEW STATS":
            clear()
            print("Below are your current stats.\n")
            print(saved_game_data.trainer_data)
        else:
            pass


if __name__ == "__main__":
    main()
