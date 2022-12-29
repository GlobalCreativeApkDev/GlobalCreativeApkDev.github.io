"""
This file contains code for the game "Life Simulation".
Author: GlobalCreativeApkDev
The game "Life Simulation" is inspired by Torn RPG (https://www.torn.com/), Stardew Valley
(https://www.stardewvalley.net/), and Pokemon games.
"""

# Game version: 1


# Importing necessary libraries
import sys
import uuid
import pickle
import copy
import random
from datetime import datetime, timedelta
import os
from functools import reduce

import mpmath
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


# Creating static functions to be used throughout the game.


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def tabulate_element_chart() -> str:
    return str(tabulate(ELEMENT_CHART, headers='firstrow', tablefmt='fancy_grid'))


def generate_random_name() -> str:
    res: str = ""  # initial value
    name_length: int = random.randint(5, 20)
    for i in range(name_length):
        res += LETTERS[random.randint(0, len(LETTERS) - 1)]

    return res.capitalize()


def get_index_of_element(a_list: list, elem: object) -> int:
    for i in range(len(a_list)):
        if a_list[i] == elem:
            return i

    return -1


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


def resistance_accuracy_rule(accuracy: mpf, resistance: mpf) -> mpf:
    if resistance - accuracy <= mpf("0.15"):
        return mpf("0.15")
    else:
        return resistance - accuracy


def load_game_data(file_name):
    # type: (str) -> Game
    return pickle.load(open(file_name, "rb"))


def save_game_data(game_data, file_name):
    # type: (Game, str) -> None
    pickle.dump(game_data, open(file_name, "wb"))


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating necessary classes to be used throughout the game.


###########################################
# MINIGAMES
###########################################


class Minigame:
    """
    This class contains attributes of a minigame in this game.
    """

    POSSIBLE_NAMES: list = ["BOX EATS PLANTS", "MATCH WORD PUZZLE", "MATCH-3 GAME"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]
        self.already_played: bool = False

    def reset(self):
        # type: () -> bool
        time_now: datetime = datetime.now()
        if self.already_played and time_now.hour > 0:
            self.already_played = False
            return True
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
        # type: () -> Minigame
        return copy.deepcopy(self)


###########################################
# MINIGAMES
###########################################


###########################################
# BOX EATS PLANTS
###########################################


class BoxEatsPlantsBoard:
    """
    This class contains attributes of a board in the game "Box Eats Plants".
    """

    BOARD_WIDTH: int = 10
    BOARD_HEIGHT: int = 10

    def __init__(self):
        # type: () -> None
        self.__tiles: list = []  # initial value
        for i in range(self.BOARD_HEIGHT):
            new: list = []  # initial value
            for j in range(self.BOARD_WIDTH):
                new.append(BoxEatsPlantsTile())

            self.__tiles.append(new)

    def num_plants(self):
        # type: () -> int
        plants: int = 0  # initial value
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                curr_tile: BoxEatsPlantsTile = self.get_tile_at(x, y)
                if isinstance(curr_tile.plant, Plant):
                    plants += 1

        return plants

    def num_rocks(self):
        # type: () -> int
        rocks: int = 0  # initial value
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                curr_tile: BoxEatsPlantsTile = self.get_tile_at(x, y)
                if isinstance(curr_tile.rock, Rock):
                    rocks += 1

        return rocks

    def num_boxes(self):
        # type: () -> int
        boxes: int = 0  # initial value
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                curr_tile: BoxEatsPlantsTile = self.get_tile_at(x, y)
                if isinstance(curr_tile.box, Box):
                    boxes += 1

        return boxes

    def spawn_plant(self):
        # type: () -> Plant
        plant_x: int = random.randint(0, self.BOARD_WIDTH - 1)
        plant_y: int = random.randint(0, self.BOARD_HEIGHT - 1)
        plant_tile: BoxEatsPlantsTile = self.__tiles[plant_y][plant_x]
        while plant_tile.plant is not None:
            plant_x = random.randint(0, self.BOARD_WIDTH - 1)
            plant_y = random.randint(0, self.BOARD_HEIGHT - 1)
            plant_tile = self.__tiles[plant_y][plant_x]

        plant: Plant = Plant(plant_x, plant_y)
        plant_tile.add_plant(plant)
        return plant

    def spawn_rock(self):
        # type: () -> Rock
        rock_x: int = random.randint(0, self.BOARD_WIDTH - 1)
        rock_y: int = random.randint(0, self.BOARD_HEIGHT - 1)
        rock_tile: BoxEatsPlantsTile = self.__tiles[rock_y][rock_x]
        while rock_tile.rock is not None:
            rock_x = random.randint(0, self.BOARD_WIDTH - 1)
            rock_y = random.randint(0, self.BOARD_HEIGHT - 1)
            rock_tile = self.__tiles[rock_y][rock_x]

        rock: Rock = Rock(rock_x, rock_y)
        rock_tile.add_rock(rock)
        return rock

    def spawn_box(self):
        # type: () -> Box
        box_x: int = random.randint(0, self.BOARD_WIDTH - 1)
        box_y: int = random.randint(0, self.BOARD_HEIGHT - 1)
        box_tile: BoxEatsPlantsTile = self.__tiles[box_y][box_x]
        while box_tile.plant is not None or box_tile.rock is not None:
            box_x = random.randint(0, self.BOARD_WIDTH - 1)
            box_y = random.randint(0, self.BOARD_HEIGHT - 1)
            box_tile = self.__tiles[box_y][box_x]
        box: Box = Box(box_x, box_y)
        box_tile.add_box(box)
        return box

    def get_tile_at(self, x, y):
        # type: (int, int) -> BoxEatsPlantsTile or None
        if x < 0 or x >= self.BOARD_WIDTH or y < 0 or y >= self.BOARD_HEIGHT:
            return None
        return self.__tiles[y][x]

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

    def __str__(self):
        # type: () -> str
        return str(tabulate(self.__tiles, tablefmt='fancy_grid'))

    def clone(self):
        # type: () -> BoxEatsPlantsBoard
        return copy.deepcopy(self)


class Box:
    """
    This class contains attributes of a box in the game "Box Eats Plants".
    """

    def __init__(self, x, y):
        # type: (int, int) -> None
        self.name: str = "BOX"
        self.x: int = x
        self.y: int = y

    def move_up(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.y > 0:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_box()
            self.y -= 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_box(self)
            return True
        return False

    def move_down(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.y < board.BOARD_HEIGHT - 1:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_box()
            self.y += 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_box(self)
            return True
        return False

    def move_left(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.x > 0:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_box()
            self.x -= 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_box(self)
            return True
        return False

    def move_right(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.x < board.BOARD_WIDTH - 1:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_box()
            self.x += 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_box(self)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return str(self.name)

    def clone(self):
        # type: () -> Box
        return copy.deepcopy(self)


class Plant:
    """
    This class contains attributes of a plant in the game "Box Eats Plants".
    """

    def __init__(self, x, y):
        # type: (int, int) -> None
        self.name: str = "PLANT"
        self.x: int = x
        self.y: int = y

    def move_up(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.y > 0:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_plant()
            self.y -= 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_plant(self)
            return True
        return False

    def move_down(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.y < board.BOARD_HEIGHT - 1:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_plant()
            self.y += 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_plant(self)
            return True
        return False

    def move_left(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.x > 0:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_plant()
            self.x -= 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_plant(self)
            return True
        return False

    def move_right(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.x < board.BOARD_WIDTH - 1:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_plant()
            self.x += 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_plant(self)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return str(self.name)

    def clone(self):
        # type: () -> Plant
        return copy.deepcopy(self)


class Rock:
    """
    This class contains attributes of a rock in the game "Box Eats Plants".
    """

    def __init__(self, x, y):
        # type: (int, int) -> None
        self.name: str = "ROCK"
        self.x: int = x
        self.y: int = y

    def move_up(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.y > 0:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_rock()
            self.y -= 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_rock(self)
            return True
        return False

    def move_down(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.y < board.BOARD_HEIGHT - 1:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_rock()
            self.y += 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_rock(self)
            return True
        return False

    def move_left(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.x > 0:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_rock()
            self.x -= 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_rock(self)
            return True
        return False

    def move_right(self, board):
        # type: (BoxEatsPlantsBoard) -> bool
        if self.x < board.BOARD_WIDTH - 1:
            old_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            old_tile.remove_rock()
            self.x += 1
            new_tile: BoxEatsPlantsTile = board.get_tile_at(self.x, self.y)
            new_tile.add_rock(self)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return str(self.name)

    def clone(self):
        # type: () -> Rock
        return copy.deepcopy(self)


class BoxEatsPlantsTile:
    """
    This class contains attributes of a tile in the minigame "Box Eats Plants".
    """

    def __init__(self):
        # type: () -> None
        self.box: Box or None = None
        self.plant: Plant or None = None
        self.rock: Rock or None = None

    def add_box(self, box):
        # type: (Box) -> bool
        if self.box is None:
            self.box = box
            return True
        return False

    def remove_box(self):
        # type: () -> None
        self.box = None

    def add_plant(self, plant):
        # type: (Plant) -> bool
        if self.plant is None:
            self.plant = plant
            return True
        return False

    def remove_plant(self):
        # type: () -> None
        self.plant = None

    def add_rock(self, rock):
        # type: (Rock) -> bool
        if self.rock is None:
            self.rock = rock
            return True
        return False

    def remove_rock(self):
        # type: () -> None
        self.rock = None

    def __str__(self):
        # type: () -> str
        if self.box is None and self.plant is None and self.rock is None:
            return "NONE"
        res: str = ""  # initial value
        if isinstance(self.box, Box):
            res += str(self.box)

        if isinstance(self.plant, Plant):
            if self.box is not None:
                res += "\n" + str(self.plant)
            else:
                res += str(self.plant)

        if isinstance(self.rock, Rock):
            if self.box is not None or self.plant is not None:
                res += "\n" + str(self.rock)
            else:
                res += str(self.rock)

        return res

    def clone(self):
        # type: () -> BoxEatsPlantsTile
        return copy.deepcopy(self)


###########################################
# BOX EATS PLANTS
###########################################


###########################################
# MATCH WORD PUZZLE
###########################################


class MatchWordPuzzleBoard:
    """
    This class contains attributes of the board for the minigame "Match Word Puzzle".
    """

    BOARD_WIDTH: int = 6
    BOARD_HEIGHT: int = 4

    def __init__(self):
        # type: () -> None
        self.__tiles: list = []  # initial value
        chosen_keywords: list = []  # initial value
        chosen_keywords_tally: list = [0] * 12
        for i in range(12):
            curr_keyword: str = MatchWordPuzzleTile.POSSIBLE_KEYWORDS[random.randint(0,
                                                                                     len(MatchWordPuzzleTile.POSSIBLE_KEYWORDS) - 1)]
            while curr_keyword in chosen_keywords:
                curr_keyword = MatchWordPuzzleTile.POSSIBLE_KEYWORDS[random.randint(0,
                                                                                    len(MatchWordPuzzleTile.POSSIBLE_KEYWORDS) - 1)]

            chosen_keywords.append(curr_keyword)

        for i in range(self.BOARD_HEIGHT):
            new: list = []  # initial value
            for j in range(self.BOARD_WIDTH):
                curr_keyword: str = chosen_keywords[random.randint(0, len(chosen_keywords) - 1)]
                while chosen_keywords_tally[get_index_of_element(chosen_keywords, curr_keyword)] >= 2:
                    curr_keyword = chosen_keywords[random.randint(0, len(chosen_keywords) - 1)]

                new.append(MatchWordPuzzleTile(curr_keyword))
                chosen_keywords_tally[get_index_of_element(chosen_keywords, curr_keyword)] += 1

            self.__tiles.append(new)

    def all_opened(self):
        # type: () -> bool
        for i in range(self.BOARD_HEIGHT):
            for j in range(self.BOARD_WIDTH):
                if self.__tiles[i][j].is_closed:
                    return False

        return True

    def get_tile_at(self, x, y):
        # type: (int, int) -> MatchWordPuzzleTile or None
        if x < 0 or x >= self.BOARD_WIDTH or y < 0 or y >= self.BOARD_HEIGHT:
            return None
        return self.__tiles[y][x]

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

    def __str__(self):
        # type: () -> str
        return str(tabulate(self.__tiles, tablefmt='fancy_grid'))

    def clone(self):
        # type: () -> MatchWordPuzzleBoard
        return copy.deepcopy(self)


class MatchWordPuzzleTile:
    """
    This class contains attributes of a tile in the minigame "Match Word Puzzle".
    """

    POSSIBLE_KEYWORDS: list = ["AND", "AS", "ASSERT", "BREAK", "CLASS", "CONTINUE", "DEF", "DEL", "ELIF", "ELSE",
                               "EXCEPT", "FALSE", "FINALLY", "FOR", "FROM", "GLOBAL", "IF", "IMPORT", "IN", "IS",
                               "LAMBDA", "NONE", "NONLOCAL", "NOT", "OR", "PASS", "RAISE", "RETURN", "TRUE",
                               "TRY", "WHILE", "WITH", "YIELD"]

    def __init__(self, contents):
        # type: (str) -> None
        self.contents: str = contents if contents in self.POSSIBLE_KEYWORDS else self.POSSIBLE_KEYWORDS[0]
        self.is_closed: bool = True

    def open(self):
        # type: () -> bool
        if self.is_closed:
            self.is_closed = False
            return True
        return False

    def __str__(self):
        # type: () -> str
        return "CLOSED" if self.is_closed else str(self.contents)

    def clone(self):
        # type: () -> MatchWordPuzzleTile
        return copy.deepcopy(self)


###########################################
# MATCH WORD PUZZLE
###########################################


###########################################
# MATCH-3 GAME
###########################################


"""
Code for match-3 game is inspired by the following sources:
1. https://www.raspberrypi.com/news/make-a-columns-style-tile-matching-game-wireframe-25/
2. https://github.com/Wireframe-Magazine/Wireframe-25/blob/master/match3.py
"""


class MatchThreeBoard:
    """
    This class contains attributes of the board for the minigame "Match-3 Game".
    """

    BOARD_WIDTH: int = 10
    BOARD_HEIGHT: int = 10

    def __init__(self):
        # type: () -> None
        self.__tiles: list = [["AND"] * self.BOARD_WIDTH for k in range(self.BOARD_HEIGHT)]  # initial value
        for i in range(self.BOARD_HEIGHT):
            new: list = []  # initial value
            for j in range(self.BOARD_WIDTH):
                curr_keyword: str = MatchThreeTile.POSSIBLE_KEYWORDS[random.randint(0,
                                                                                    len(MatchThreeTile.POSSIBLE_KEYWORDS) - 1)]
                while (i > 0 and self.__tiles[i][j].contents == self.__tiles[i - 1][j].contents) or \
                        (j > 0 and self.__tiles[i][j].contents == self.__tiles[i][j - 1].contents):
                    curr_keyword = MatchThreeTile.POSSIBLE_KEYWORDS[random.randint(0,
                                                                                   len(MatchThreeTile.POSSIBLE_KEYWORDS) - 1)]

                new.append(MatchThreeTile(curr_keyword))

            self.__tiles.append(new)

        self.__matches: list = []  # initial value

    def swap_tiles(self, x1, y1, x2, y2):
        # type: (int, int, int, int) -> bool
        if self.get_tile_at(x1, y1) is None or self.get_tile_at(x2, y2) is None:
            return False

        temp: MatchThreeTile = self.__tiles[y1][x1]
        self.__tiles[y1][x1] = self.__tiles[y2][x2]
        self.__tiles[y2][x2] = temp
        return True

    def no_possible_moves(self):
        # type: () -> bool
        # Trying all possible moves and checking whether it has matches or not
        for j in range(self.BOARD_WIDTH):
            for i in range(self.BOARD_HEIGHT - 1):
                new_board: MatchThreeBoard = self.clone()
                temp: MatchThreeTile = new_board.__tiles[i][j]
                new_board.__tiles[i][j] = new_board.__tiles[i + 1][j]
                new_board.__tiles[i + 1][j] = temp
                matches: list = new_board.check_matches()
                if len(matches) > 0:
                    return False

        for i in range(self.BOARD_HEIGHT):
            for j in range(self.BOARD_WIDTH - 1):
                new_board: MatchThreeBoard = self.clone()
                temp: MatchThreeTile = new_board.__tiles[i][j]
                new_board.__tiles[i][j] = new_board.__tiles[i][j + 1]
                new_board.__tiles[i][j + 1] = temp
                matches: list = new_board.check_matches()
                if len(matches) > 0:
                    return False

        return True

    def check_matches(self):
        # type: () -> list
        self.__matches = []  # initial value
        for j in range(self.BOARD_WIDTH):
            curr_match: list = []  # initial value
            for i in range(self.BOARD_HEIGHT):
                if len(curr_match) == 0 or self.__tiles[i][j].contents == self.__tiles[i - 1][j].contents:
                    curr_match.append((i, j))
                else:
                    if len(curr_match) >= 3:
                        self.__matches.append(curr_match)
                    curr_match = [(i, j)]
            if len(curr_match) >= 3:
                self.__matches.append(curr_match)

        for i in range(self.BOARD_HEIGHT):
            curr_match: list = []  # initial value
            for j in range(self.BOARD_WIDTH):
                if len(curr_match) == 0 or self.__tiles[i][j].contents == self.__tiles[i][j - 1].contents:
                    curr_match.append((i, j))
                else:
                    if len(curr_match) >= 3:
                        self.__matches.append(curr_match)
                    curr_match = [(i, j)]
            if len(curr_match) >= 3:
                self.__matches.append(curr_match)

        return self.__matches

    def clear_matches(self):
        # type: () -> None
        for match in self.__matches:
            for position in match:
                self.__tiles[position[0]][position[1]].contents = "NONE"

        self.__matches = []

    def fill_board(self):
        # type: () -> None
        for j in range(self.BOARD_WIDTH):
            for i in range(self.BOARD_HEIGHT):
                if self.__tiles[i][j].contents == "NONE":
                    for row in range(i, 0, -1):
                        self.__tiles[row][j].contents = self.__tiles[row - 1][j].contents
                    self.__tiles[0][j].contents = MatchThreeTile.POSSIBLE_KEYWORDS[random.randint(0,
                                                                                                  len(MatchThreeTile.POSSIBLE_KEYWORDS) - 1)]
                    while self.__tiles[0][j].contents == self.__tiles[1][j].contents or (j > 0 and
                                                                                         self.__tiles[0][j].contents ==
                                                                                         self.__tiles[0][
                                                                                             j - 1].contents) or \
                            (j < self.BOARD_WIDTH - 1 and self.__tiles[0][j].contents == self.__tiles[0][
                                j + 1].contents):
                        self.__tiles[0][j].contents = MatchThreeTile.POSSIBLE_KEYWORDS[random.randint(0,
                                                                                                      len(MatchThreeTile.POSSIBLE_KEYWORDS) - 1)]

    def get_tile_at(self, x, y):
        # type: (int, int) -> MatchThreeTile or None
        if x < 0 or x >= self.BOARD_WIDTH or y < 0 or y >= self.BOARD_HEIGHT:
            return None
        return self.__tiles[y][x]

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

    def __str__(self):
        # type: () -> str
        return str(tabulate(self.__tiles, tablefmt='fancy_grid'))

    def clone(self):
        # type: () -> MatchThreeBoard
        return copy.deepcopy(self)


class MatchThreeTile:
    """
    This class contains attributes of a tile in the minigame "Match-3 Game".
    """

    POSSIBLE_KEYWORDS: list = ["AND", "AS", "ASSERT", "BREAK", "CLASS", "CONTINUE", "DEF", "DEL", "ELIF", "ELSE",
                               "EXCEPT", "FALSE", "FINALLY", "FOR", "FROM", "GLOBAL"]

    def __init__(self, contents):
        # type: (str) -> None
        self.contents: str = contents if contents in self.POSSIBLE_KEYWORDS else "NONE"

    def __str__(self):
        # type: () -> str
        return str(self.contents)

    def clone(self):
        # type: () -> MatchThreeTile
        return copy.deepcopy(self)


###########################################
# MATCH-3 GAME
###########################################


###########################################
# ADVENTURE MODE
###########################################


class CreatureBattleAction:
    """
    This class contains attributes of an action that can be carried out during creature battles.
    """

    # TODO: add methods related to creature battle action.

    POSSIBLE_NAMES: list = ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]

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
        # type: () -> CreatureBattleAction
        return copy.deepcopy(self)


class PlayerBattleAction:
    """
    This class contains attributes of an action that can be carried out during PvP battles.
    """

    # TODO: add methods related to player battle action.

    POSSIBLE_NAMES: list = ["NORMAL ATTACK", "NORMAL HEAL", "USE WEAPON"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]

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
        # type: () -> PlayerBattleAction
        return copy.deepcopy(self)


class AwakenBonus:
    """
    This class contains attributes of the bonus gained for awakening a legendary creature.
    """

    def __init__(self, max_hp_percentage_up, max_magic_points_percentage_up, attack_power_percentage_up,
                 defense_percentage_up, attack_speed_up, crit_rate_up, crit_damage_up, resistance_up,
                 accuracy_up, new_skill_gained):
        # type: (mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, Skill) -> None
        self.max_hp_percentage_up: mpf = max_hp_percentage_up
        self.max_magic_points_percentage_up: mpf = max_magic_points_percentage_up
        self.attack_power_percentage_up: mpf = attack_power_percentage_up
        self.defense_percentage_up: mpf = defense_percentage_up
        self.attack_speed_up: mpf = attack_speed_up
        self.crit_rate_up: mpf = crit_rate_up
        self.crit_damage_up: mpf = crit_damage_up
        self.resistance_up: mpf = resistance_up
        self.accuracy_up: mpf = accuracy_up
        self.new_skill_gained: Skill = new_skill_gained

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


class PVPBattle(Battle):
    """
    This class contains attributes of a battle between players.
    """

    def __init__(self, trainer1, trainer2):
        # type: (Trainer, Trainer) -> None
        Battle.__init__(self, trainer1)
        self.trainer2: Trainer = trainer2


class WildBattle(Battle):
    """
    This class contains attributes of a battle against a legendary creature.
    """

    def __init__(self, trainer1, wild_legendary_creature):
        # type: (Trainer, LegendaryCreature) -> None
        Battle.__init__(self, trainer1)
        self.wild_legendary_creature: LegendaryCreature = wild_legendary_creature


class TrainerBattle(Battle):
    """
    This class contains attributes of a battle between legendary creature trainers.
    """

    def __init__(self, trainer1, trainer2):
        # type: (Trainer, Trainer) -> None
        Battle.__init__(self, trainer1)
        self.trainer2: Trainer = trainer2


class Planet:
    """
    This class contains attributes of the planet in this game.
    """

    def __init__(self, name, cities):
        # type: (str, list) -> None
        self.name: str = name
        self.__cities: list = cities

    def get_cities(self):
        # type: () -> list
        return self.__cities

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
        # type: () -> Planet
        return copy.deepcopy(self)


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
        if y < 0 or y >= len(self.__tiles) or x < 0 or x >= len(self.__tiles[0]):
            return None
        return self.__tiles[y][x]

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

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
        # type: () -> City
        return copy.deepcopy(self)


class CityTile:
    """
    This class contains attributes of a tile in a city.
    """

    def __init__(self, portal=None):
        # type: (Portal or None) -> None
        self.portal: Portal or None = portal
        self.__game_characters: list = []  # initial value

    def get_game_characters(self):
        # type: () -> list
        return self.__game_characters

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        pass

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        pass

    def __str__(self):
        # type: () -> str
        return str(type(self).__name__) + "(NONE)"

    def clone(self):
        # type: () -> CityTile
        return copy.deepcopy(self)


class Portal:
    """
    This class contains attributes of a portal from one city to another.
    """

    def __init__(self, location_to):
        # type: (AdventureModeLocation) -> None
        self.location_to: AdventureModeLocation = location_to

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
        # type: () -> Portal
        return copy.deepcopy(self)


class WallTile(CityTile):
    """
    This class contains attributes of a city tile with a wall where the player cannot be at.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)

    def __str__(self):
        # type: () -> str
        return str(type(self).__name__) + "(WALL)"


class WaterTile(CityTile):
    """
    This class contains attributes of a city tile of a body of water where the player cannot be at.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)

    def __str__(self):
        # type: () -> str
        return str(type(self).__name__) + "(WATER)"


class GrassTile(CityTile):
    """
    This class contains attributes of a city tile with grass where the player can encounter wild legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return str(type(self).__name__) + "(GRASS)"


class PavementTile(CityTile):
    """
    This class contains attributes of a tile with pavement where the player can walk safely without any distractions
    from wild legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return str(type(self).__name__) + "(PAVEMENT)"


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
            legendary_creature_ids: list = [creature.legendary_creature_id for creature
                                            in self.__legendary_creatures]
            if legendary_creature.legendary_creature_id not in legendary_creature_ids:
                self.__legendary_creatures.append(legendary_creature)
                return True
            return False
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

    MIN_RATING: int = 1
    MAX_RATING: int = 6
    MIN_CRIT_RATE: mpf = mpf("0.15")
    MIN_CRIT_DAMAGE: mpf = mpf("1.5")
    MIN_RESISTANCE: mpf = mpf("0.15")
    MAX_RESISTANCE: mpf = mpf("1")
    MIN_ACCURACY: mpf = mpf("0")
    MAX_ACCURACY: mpf = mpf("1")
    MIN_ATTACK_GAUGE: mpf = mpf("0")
    FULL_ATTACK_GAUGE: mpf = mpf("1")
    MIN_BENEFICIAL_EFFECTS: int = 0
    MAX_BENEFICIAL_EFFECTS: int = 10
    MIN_HARMFUL_EFFECTS: int = 0
    MAX_HARMFUL_EFFECTS: int = 10
    POTENTIAL_ELEMENTS: list = ["TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
                                "PURE", "LEGEND", "PRIMAL", "WIND", "BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM",
                                "SOUL"]

    def __init__(self, name, element, rating, max_hp, max_magic_points, attack_power, defense, attack_speed,
                 skills, awaken_bonus):
        # type: (str, str, int, mpf, mpf, mpf, mpf, mpf, list, AwakenBonus) -> None
        self.legendary_creature_id: str = str(uuid.uuid1())  # generating random legendary creature ID
        self.name: str = name
        self.element: str = element if element in self.POTENTIAL_ELEMENTS else self.POTENTIAL_ELEMENTS[0]
        self.rating: int = rating if self.MIN_RATING <= rating <= self.MAX_RATING else self.MIN_RATING
        self.curr_hp: mpf = max_hp
        self.max_hp: mpf = max_hp
        self.curr_magic_points: mpf = max_magic_points
        self.max_magic_points: mpf = max_magic_points
        self.attack_power: mpf = attack_power
        self.defense: mpf = defense
        self.attack_speed: mpf = attack_speed
        self.crit_rate: mpf = self.MIN_CRIT_RATE
        self.crit_damage: mpf = self.MIN_CRIT_DAMAGE
        self.resistance: mpf = self.MIN_RESISTANCE
        self.accuracy: mpf = self.MIN_ACCURACY
        self.__beneficial_effects: list = []
        self.__harmful_effects: list = []
        self.__skills: list = skills
        self.awaken_bonus: AwakenBonus = awaken_bonus
        self.__runes: dict = {}  # initial value
        self.attack_power_percentage_up: mpf = mpf("0")
        self.attack_power_percentage_down: mpf = mpf("0")
        self.attack_speed_percentage_up: mpf = mpf("0")
        self.attack_speed_percentage_down: mpf = mpf("0")
        self.defense_percentage_up: mpf = mpf("0")
        self.defense_percentage_down: mpf = mpf("0")
        self.crit_rate_up: mpf = mpf("0")
        self.crit_damage_up: mpf = mpf("0")
        self.attack_gauge: mpf = self.MIN_ATTACK_GAUGE
        self.corresponding_team: BattleTeam = BattleTeam()

    def get_skills(self):
        # type: () -> list
        return self.__skills

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

    POSSIBLE_SKILL_TYPES: list = ["ATTACK", "HEAL", "ALLIES EFFECT", "ENEMIES EFFECT"]

    def __init__(self, name, description, skill_type, magic_points_cost, damage_multiplier,
                 beneficial_effects_to_allies, harmful_effects_to_enemies, allies_attack_gauge_up,
                 enemies_attack_gauge_down, heal_amount_to_allies):
        # type: (str, str, str, mpf, mpf, list, list, mpf, mpf, mpf) -> None
        self.name: str = name
        self.description: str = description
        self.skill_type = skill_type if skill_type in self.POSSIBLE_SKILL_TYPES else self.POSSIBLE_SKILL_TYPES[0]
        self.magic_points_cost: mpf = magic_points_cost
        self.level: int = 1
        self.damage_multiplier: mpf = damage_multiplier
        self.__beneficial_effects_to_allies: list = beneficial_effects_to_allies
        self.__harmful_effects_to_enemies: list = harmful_effects_to_enemies
        self.allies_attack_gauge_up: mpf = allies_attack_gauge_up
        self.enemies_attack_gauge_down: mpf = enemies_attack_gauge_down
        self.heal_amount_to_allies: mpf = heal_amount_to_allies

    def get_beneficial_effects_to_allies(self):
        # type: () -> list
        return self.__beneficial_effects_to_allies

    def get_harmful_effects_to_enemies(self):
        # type: () -> list
        return self.__harmful_effects_to_enemies

    def level_up(self):
        # type: () -> None
        self.level += 1
        self.damage_multiplier *= mpf("1.25")
        self.heal_amount_to_allies *= mpf("1.25")

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


class BeneficialEffect:
    """
    This class contains attributes of a beneficial effect a legendary creature has.
    """

    def __init__(self, name, is_stackable, heal_percentage_per_turn, attack_power_percentage_up,
                 attack_speed_percentage_up, defense_percentage_up, crit_rate_up, crit_damage_up):
        # type: (str, bool, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        self.name: str = name
        self.is_stackable: bool = is_stackable
        self.heal_percentage_per_turn: mpf = heal_percentage_per_turn
        self.attack_power_percentage_up: mpf = attack_power_percentage_up
        self.attack_speed_percentage_up: mpf = attack_speed_percentage_up
        self.defense_percentage_up: mpf = defense_percentage_up
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
        # type: () -> BeneficialEffect
        return copy.deepcopy(self)


class HarmfulEffect:
    """
    This class contains attributes of a harmful effect a legendary creature has.
    """

    def __init__(self, name, is_stackable, damage_percentage_per_turn, attack_power_percentage_down,
                 attack_speed_percentage_down, defense_percentage_down):
        # type: (str, bool, mpf, mpf, mpf, mpf) -> None
        self.name: str = name
        self.is_stackable: bool = is_stackable
        self.damage_percentage_per_turn: mpf = damage_percentage_per_turn
        self.attack_power_percentage_down: mpf = attack_power_percentage_down
        self.attack_speed_percentage_down: mpf = attack_speed_percentage_down
        self.defense_percentage_down: mpf = defense_percentage_down

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
        # type: () -> HarmfulEffect
        return copy.deepcopy(self)


###########################################
# LEGENDARY CREATURE
###########################################


###########################################
# ITEMS
###########################################


class ItemShop:
    """
    This class contains attributes of a shop selling items.
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


class Item:
    """
    This class contains attributes of an item in this game.
    """

    def __init__(self, name, description, dollars_cost):
        # type: (str, str, mpf) -> None
        self.name: str = name
        self.description: str = description
        self.dollars_cost: mpf = dollars_cost
        self.sell_dollars_gain: mpf = dollars_cost / 5
        self.item_type: str = "ITEM"

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


class TrainerItem(Item):
    """
    This class contains attributes of an item to be used by trainers.
    """

    def __init__(self, name, description, dollars_cost):
        # type: (str, str, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)
        self.item_type: str = "TRAINER ITEM"


class Weapon(TrainerItem):
    """
    This class contains attributes of a weapon the trainers can bring to PVP battles.
    """

    def __init__(self, name, description, dollars_cost, damage):
        # type: (str, str, mpf, mpf) -> None
        TrainerItem.__init__(self, name, description, dollars_cost)
        self.damage: mpf = damage


class Armor(TrainerItem):
    """
    This class contains attributes of an armor the trainers can bring to PVP battles.
    """

    def __init__(self, name, description, dollars_cost, armor):
        # type: (str, str, mpf, mpf) -> None
        TrainerItem.__init__(self, name, description, dollars_cost)
        self.armor: mpf = armor


class LegendaryCreatureItem(Item):
    """
    This class contains attributes of an item to be used by legendary creatures.
    """

    def __init__(self, name, description, dollars_cost):
        # type: (str, str, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)
        self.item_type: str = "LEGENDARY CREATURE ITEM"


class Egg(LegendaryCreatureItem):
    """
    This class contains attributes of an egg which can be hatched to produce a new legendary creature
    """

    POTENTIAL_ELEMENTS: list = ["TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
                                "PURE", "LEGEND", "PRIMAL", "WIND", "BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM",
                                "SOUL"]

    def __init__(self, dollars_cost, element):
        # type: (mpf, str) -> None
        LegendaryCreatureItem.__init__(self, str(element if element in self.POTENTIAL_ELEMENTS else
                                                 self.POTENTIAL_ELEMENTS[0]).upper() +
                                       " EGG", "An egg which can be hatched for legendary creatures to come out.",
                                       dollars_cost)
        self.element: str = element if element in self.POTENTIAL_ELEMENTS else self.POTENTIAL_ELEMENTS[0]


class Ball(LegendaryCreatureItem):
    """
    This class contains attributes of a ball used to catch a legendary creature.
    """

    MIN_CATCH_RATE: mpf = mpf("0.1")
    MAX_CATCH_RATE: mpf = mpf("1")

    def __init__(self, name, description, dollars_cost, catch_rate):
        # type: (str, str, mpf, mpf) -> None
        LegendaryCreatureItem.__init__(self, name, description, dollars_cost)
        self.catch_rate: mpf = catch_rate if self.MIN_CATCH_RATE <= catch_rate <= self.MAX_CATCH_RATE \
            else self.MIN_CATCH_RATE


class Rune(LegendaryCreatureItem):
    """
    This class contains attributes of a rune used to strengthen legendary creatures.
    """

    MIN_SLOT_NUMBER: int = 1
    MAX_SLOT_NUMBER: int = 6
    MIN_RATING: int = 1
    MAX_RATING: int = 6

    def __init__(self, name, description, dollars_cost, rating, slot_number):
        # type: (str, str, mpf, int, int) -> None
        LegendaryCreatureItem.__init__(self, name, description, dollars_cost)
        self.rating: int = rating if self.MIN_RATING <= rating <= self.MAX_RATING else self.MIN_RATING
        self.slot_number: int = slot_number if self.MIN_SLOT_NUMBER <= slot_number <= self.MAX_SLOT_NUMBER \
            else self.MIN_SLOT_NUMBER
        self.level: int = 1
        self.level_up_dollars_cost: mpf = dollars_cost
        self.level_up_success_rate: mpf = mpf("1")
        self.already_placed: bool = False  # initial value
        self.stat_increase: StatIncrease = self.__get_stat_increase()

    def __get_stat_increase(self):
        # type: () -> StatIncrease
        return StatIncrease(max_hp_up=mpf("10") ** (6 * self.rating),
                            max_hp_percentage_up=mpf(2 * self.rating),
                            max_magic_points_up=mpf("10") ** (6 * self.rating),
                            max_magic_points_percentage_up=mpf(2 * self.rating),
                            attack_up=mpf("10") ** (5 * self.rating),
                            attack_percentage_up=mpf(2 * self.rating),
                            defense_up=mpf("10") ** (5 * self.rating),
                            defense_percentage_up=mpf(2 * self.rating),
                            attack_speed_up=mpf(2 * self.rating),
                            crit_rate_up=mpf(0.01 * self.rating),
                            crit_damage_up=mpf(0.05 * self.rating),
                            resistance_up=mpf(0.01 * self.rating),
                            accuracy_up=mpf(0.01 * self.rating))

    def level_up(self):
        # type: () -> bool
        # Check whether levelling up is successful or not
        if random.random() > self.level_up_success_rate:
            return False

        # Increase the level of the rune
        self.level += 1

        # Update the cost and success rate of levelling up the rune
        self.level_up_dollars_cost *= mpf("10") ** (self.level + self.rating)
        self.level_up_success_rate *= mpf("0.95")

        # Increase main stat attribute
        self.stat_increase.max_hp_up += mpf("10") ** (6 * self.rating + self.level)
        self.stat_increase.max_hp_percentage_up += self.rating
        self.stat_increase.max_magic_points_up += mpf("10") ** (6 * self.rating + self.level)
        self.stat_increase.max_magic_points_percentage_up += self.rating
        self.stat_increase.attack_up += mpf("10") ** (5 * self.rating + 1)
        self.stat_increase.attack_percentage_up += self.rating
        self.stat_increase.defense_up += mpf("10") ** (5 * self.rating + 1)
        self.stat_increase.defense_percentage_up += self.rating
        self.stat_increase.attack_speed_up += 2 * self.rating
        self.stat_increase.crit_rate_up += 0.01 * self.rating
        self.stat_increase.crit_damage_up += 0.05 * self.rating
        self.stat_increase.resistance_up += 0.01 * self.rating
        self.stat_increase.accuracy_up += 0.01 * self.rating
        return True


class StatIncrease:
    """
    This class contains attributes of the increase in stats of a rune.
    """

    def __init__(self, max_hp_up=mpf("0"), max_hp_percentage_up=mpf("0"), max_magic_points_up=mpf("0"),
                 max_magic_points_percentage_up=mpf("0"), attack_up=mpf("0"), attack_percentage_up=mpf("0"),
                 defense_up=mpf("0"), defense_percentage_up=mpf("0"), attack_speed_up=mpf("0"), crit_rate_up=mpf("0"),
                 crit_damage_up=mpf("0"), resistance_up=mpf("0"), accuracy_up=mpf("0")):
        # type: (mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        self.max_hp_up: mpf = max_hp_up
        self.max_hp_percentage_up: mpf = max_hp_percentage_up
        self.max_magic_points_up: mpf = max_magic_points_up
        self.max_magic_points_percentage_up: mpf = max_magic_points_percentage_up
        self.attack_up: mpf = attack_up
        self.attack_percentage_up: mpf = attack_percentage_up
        self.defense_up: mpf = defense_up
        self.defense_percentage_up: mpf = defense_percentage_up
        self.attack_speed_up: mpf = attack_speed_up
        self.crit_rate_up: mpf = crit_rate_up
        self.crit_damage_up: mpf = crit_damage_up
        self.resistance_up: mpf = resistance_up
        self.accuracy_up: mpf = accuracy_up

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
        # type: () -> StatIncrease
        return copy.deepcopy(self)


class AwakenShard(LegendaryCreatureItem):
    """
    This class contains attributes of an awaken shard to immediately awaken a legendary creature.
    """

    def __init__(self, dollars_cost, legendary_creature_element):
        # type: (mpf, str) -> None
        LegendaryCreatureItem.__init__(self, "AWAKEN SHARD", "A shard used to immediately awaken a "
                                                             "legendary creature.", dollars_cost)
        self.legendary_creature_element: str = legendary_creature_element  # the element of the legendary creature
        # to be awakened


class EXPShard(LegendaryCreatureItem):
    """
    This class contains attributes of an EXP shard to increase the EXP of a legendary creature.
    """

    def __init__(self, dollars_cost, exp_granted):
        # type: (mpf, mpf) -> None
        LegendaryCreatureItem.__init__(self, "EXP SHARD", "A shard used to immediately increase the EXP of a "
                                                          "legendary creature.", dollars_cost)
        self.exp_granted: mpf = exp_granted


class LevelUpShard(LegendaryCreatureItem):
    """
    This class contains attributes of a shard used to immediately level up a legendary creature.
    """

    def __init__(self, dollars_cost):
        # type: (mpf) -> None
        LegendaryCreatureItem.__init__(self, "LEVEL UP SHARD", "A shard used to immediately increase the level of "
                                                               "a legendary creature.", dollars_cost)


class SkillLevelUpShard(LegendaryCreatureItem):
    """
    This class contains attributes of a skill level up shard to immediately increase the level of a
    skill possessed by a legendary creature.
    """

    def __init__(self, dollars_cost):
        # type: (mpf) -> None
        Item.__init__(self, "SKILL LEVEL UP SHARD", "A shard used to immediately increase the level of a "
                                                    "legendary creature' s skill.", dollars_cost)


###########################################
# ITEMS
###########################################


###########################################
# EXERCISE
###########################################


class ExerciseGym:
    """
    This class contains attributes of a gym where the player can improve his/her attributes.
    """

    def __init__(self, fitness_types, training_options):
        # type: (list, list) -> None
        self.name: str = "EXERCISE GYM"
        self.__fitness_types: list = fitness_types
        self.__training_options: list = training_options

    def get_training_options(self):
        # type: () -> list
        return self.__training_options

    def get_fitness_types(self):
        # type: () -> list
        return self.__fitness_types

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
        # type: () -> ExerciseGym
        return copy.deepcopy(self)


class TrainingOption:
    """
    This class contains attributes of a training option for fitness.
    """

    def __init__(self, option_name, energy_per_train):
        # type: (str, mpf) -> None
        self.option_name: str = option_name
        self.energy_per_train: mpf = energy_per_train

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
        # type: () -> TrainingOption
        return copy.deepcopy(self)


###########################################
# EXERCISE
###########################################


###########################################
# GENERAL
###########################################


class GameCharacter:
    """
    This class contains attributes of a game character in this game.
    """

    def __init__(self, name, adventure_mode_location):
        # type: (str, AdventureModeLocation) -> None
        self.game_character_id: str = str(uuid.uuid1())  # generating random game character ID
        self.name: str = name
        self.adventure_mode_location: AdventureModeLocation = adventure_mode_location

    def get_city_tile(self):
        # type: () -> CityTile or None
        if self.adventure_mode_location.city_index < 0 or self.adventure_mode_location.city_index >= \
                len(self.adventure_mode_location.planet.get_cities()) or \
                self.adventure_mode_location.planet.get_cities()[self.adventure_mode_location.city_index] \
                        [self.adventure_mode_location.city_tile_y][self.adventure_mode_location.city_tile_x] is None:
            return None
        return self.adventure_mode_location.planet.get_cities()[self.adventure_mode_location.city_index] \
            [self.adventure_mode_location.city_tile_y][self.adventure_mode_location.city_tile_x]

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
        # type: () -> GameCharacter
        return copy.deepcopy(self)


class NPC(GameCharacter):
    """
    This class contains attributes of a non-player character (NPC).
    """

    def __init__(self, name, adventure_mode_location, message):
        # type: (str, AdventureModeLocation, str) -> None
        GameCharacter.__init__(self, name, adventure_mode_location)
        self.message: str = message


class Trainer(GameCharacter):
    """
    This class contains attributes of a trainer in this game.
    """

    def __init__(self, name, adventure_mode_location):
        # type: (str, AdventureModeLocation or None) -> None
        GameCharacter.__init__(self, name, adventure_mode_location)
        self.level: int = 1
        self.exp: mpf = mpf("0")
        self.required_exp: mpf = mpf("1e6")
        self.battle_team: BattleTeam = BattleTeam()
        self.item_inventory: ItemInventory = ItemInventory()
        self.legendary_creature_inventory: LegendaryCreatureInventory = LegendaryCreatureInventory()
        self.dollars: mpf = mpf("0")
        self.energy: mpf = mpf("100")
        self.max_energy: mpf = mpf("100")
        self.energy_recharge_per_minute: mpf = mpf("1")
        self.max_hp: mpf = mpf(random.randint(120, 150))
        self.curr_hp: mpf = self.max_hp
        self.strength: mpf = mpf(random.randint(40, 50))
        self.defense: mpf = mpf(random.randint(20, 30))
        self.speed: mpf = mpf(random.randint(20, 30))
        self.dexterity: mpf = mpf(random.randint(20, 30))
        self.weapon: Weapon or None = None
        self.armor: Armor or None = None
        self.in_jail: bool = False
        self.in_hospital: bool = False

    def enter_jail(self):
        # type: () -> bool
        if not self.in_jail:
            self.in_jail = True
            return True
        return False

    def exit_jail(self):
        # type: () -> bool
        if self.in_jail:
            self.in_jail = False
            return True
        return False

    def enter_hospital(self):
        # type: () -> bool
        if not self.in_hospital:
            self.in_hospital = True
            return True
        return False

    def exit_hospital(self):
        # type: () -> bool
        if self.in_hospital:
            self.in_hospital = False
            return True
        return False

    def recharge_energy(self, seconds):
        # type: (int) -> None
        self.energy += mpf(seconds / 60)
        if self.energy >= self.max_energy:
            self.energy = self.max_energy


class AdventureModeLocation:
    """
    This class contains attributes of the location of a game character in adventure mode of this game.
    """

    def __init__(self, planet, city_index, city_tile_x, city_tile_y):
        # type: (Planet, int, int, int) -> None
        self.planet: Planet = planet
        self.city_index: int = city_index
        self.city_tile_x: int = city_tile_x
        self.city_tile_y: int = city_tile_y

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


class Jail:
    """
    This class contains attributes of the jail.
    """

    def __init__(self):
        # type: () -> None
        self.name: str = "JAIL"
        self.__game_characters: list = []  # initial value

    def get_game_characters(self):
        # type: () -> list
        return self.__game_characters

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
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
        # type: () -> Jail
        return copy.deepcopy(self)


class Hospital:
    """
    This class contains attributes of the hospital for injured game characters.
    """

    def __init__(self):
        # type: () -> None
        self.name: str = "HOSPITAL"
        self.__game_characters: list = []  # initial value

    def get_game_characters(self):
        # type: () -> list
        return self.__game_characters

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
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
        # type: () -> Hospital
        return copy.deepcopy(self)


class ResourceReward:
    """
    This class contains attributes of the resources gained for doing something.
    """

    def __init__(self, player_reward_exp=mpf("0"), player_reward_dollars=mpf("0"),
                 legendary_creature_reward_exp=mpf("0"), player_reward_items=None):
        # type: (mpf, mpf, mpf, list) -> None
        if player_reward_items is None:
            player_reward_items = []

        self.player_reward_exp: mpf = player_reward_exp
        self.player_reward_dollars: mpf = player_reward_dollars
        self.legendary_creature_reward_exp: mpf = legendary_creature_reward_exp
        self.__player_reward_items: list = player_reward_items

    def get_player_reward_items(self):
        # type: () -> list
        return self.__player_reward_items

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
        # type: () -> ResourceReward
        return copy.deepcopy(self)


class Game:
    """
    This class contains attributes of saved game data.
    """

    def __init__(self, player_data, item_shop, minigames):
        # type: (Trainer, ItemShop, list) -> None
        self.player_data: Trainer = player_data
        self.item_shop: ItemShop = item_shop
        self.__minigames: list = minigames

    def get_minigames(self):
        # type: () -> list
        return self.__minigames

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
        # type: () -> Game
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

    print("Welcome to 'Life Simulation' by 'GlobalCreativeApkDev'.")
    print("This game is an offline adventure and simulation RPG allowing the player to ")
    print("choose various real-life actions.")
    print("Below is the element chart in 'Adventure Mode' of 'Life Simulation'.\n")
    print(str(tabulate_element_chart()) + "\n")
    print("The following elements do not have any elemental strengths nor weaknesses.")
    print("This is because they are ancient world elements. In this case, these elements will always ")
    print("be dealt with normal damage.\n")
    ancient_world_elements: list = ["BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM", "SOUL"]
    for i in range(0, len(ancient_world_elements)):
        print(str(i + 1) + ". " + str(ancient_world_elements[i]))

    return 0


if __name__ == '__main__':
    main()
