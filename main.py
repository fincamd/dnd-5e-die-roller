"""
A simple application that simulates die throws given a string of combinations for die to roll
"""

import matplotlib.pyplot as plt

from numpy import array as np_array
from sys import argv
from argparse import ArgumentParser
from random import randint
from re import compile
from dataclasses import dataclass
from typing import Union
from functools import reduce
from itertools import chain
from tabulate import tabulate

plt.style.use('_mpl-gallery')


@dataclass
class Bonus:
    value: int = 0

    def get_value(self) -> int:
        return self.value

    def get_max(self) -> int:
        return self.value

    def get_min(self) -> int:
        return self.value


@dataclass
class DiceThrow:
    n: int = 1
    faces: int = 6

    def get_value(self) -> int:
        return sum([randint(1, self.faces) for _ in range(self.n)])

    def get_max(self) -> int:
        return self.n * self.faces

    def get_min(self) -> int:
        return self.n


@dataclass
class Attack:
    die_expression: str
    die_to_throw: list[DiceThrow]
    bonuses: list[Bonus]
    attack_modifier: int = 0
    attack_roll: int = 0
    damage_roll: int = 0
    has_advantage: bool = False
    has_disadvantage: bool = False
    force_critical_hit: bool = False

    def __str__(self):
        logs = []

        logs.append(["Attack type", self._get_attack_type()])
        logs.append(["Attack condition", self._get_attack_condition()])
        logs.append(
            ["Attack roll", f"{self.attack_roll} + {self.attack_modifier} = {self.attack_roll + self.attack_modifier} vs AC"])
        logs.append(["Damage roll", f"{self.damage_roll} points of damage"])

        return tabulate(logs, headers=["Making an attack for", self.die_expression], tablefmt="outline", colalign=("right",))

    def _get_attack_condition(self) -> str:
        if self.has_advantage:
            return "Advantage"
        elif self.has_disadvantage:
            return "Disadvantage"
        else:
            return "Normal"

    def _get_attack_type(self) -> str:
        if self.attack_roll == 20:
            return "Critical"
        elif self.attack_roll == 1:
            return "Failure"
        else:
            return "Normal"

    def _roll_atack(self) -> None:
        first_roll = DiceThrow(n=1, faces=20).get_value()
        second_roll = DiceThrow(n=1, faces=20).get_value()
        if self.force_critical_hit:
            self.attack_roll = 20
        elif self.has_advantage:
            self.attack_roll = max(first_roll, second_roll)
        elif self.has_disadvantage:
            self.attack_roll = min(first_roll, second_roll)
        else:
            self.attack_roll = first_roll

    def _roll_damage(self) -> None:
        damage_rolls = map(lambda die: die.get_value(), self.die_to_throw)
        bonuses = map(lambda die: die.get_value(), self.bonuses)
        self.damage_roll = reduce(
            lambda a, b: a + b, chain(damage_rolls, bonuses), 0)

    def get_min_damage(self):
        die_min = map(lambda die: die.get_min(), self.die_to_throw)
        bonuses_min = map(lambda die: die.get_min(), self.bonuses)
        return reduce(lambda a, b: a + b, chain(die_min, bonuses_min), 0)

    def get_max_damage(self):
        die_max = map(lambda die: die.get_max(), self.die_to_throw)
        bonuses_max = map(lambda die: die.get_max(), self.bonuses)
        return reduce(lambda a, b: a + b, chain(die_max, bonuses_max), 0)

    def make(self):
        self._roll_atack()
        self._roll_damage()
        if self.attack_roll == 1:
            self.damage_roll = 0
        elif self.attack_roll == 20:
            self.damage_roll = 2 * self.damage_roll


def draw_statistics(throw_statistics: dict) -> None:
    x = np_array(list(throw_statistics.keys()))
    y = np_array(list(throw_statistics.values()))
    fig, ax = plt.subplots()
    ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
    ax.set_xlabel("Damage roll")
    ax.set_ylabel("Number of throws")
    ax.tick_params(axis="x", labelrotation=90)
    fig.subplots_adjust(left=0.07, bottom=0.1)
    plt.xticks(x)
    plt.show()


# TODO: Change dice_amount name for something more appropriate
def check_die_syntax(dice_amount: str) -> None:
    if not compile(r"^(([1-9]\d*)d?(4|6|8|10|12|20|100)|([1-9]\d*))$").fullmatch(dice_amount):
        raise ValueError(f"Invalid die throw or value: {dice_amount}")


def parse_die_or_bonus(dice_amount: str) -> Union[Bonus, DiceThrow]:
    check_die_syntax(dice_amount)
    if "d" in dice_amount:
        n_die, die_faces = dice_amount.split("d")
        return DiceThrow(n=int(n_die), faces=int(die_faces))
    else:
        return Bonus(value=int(dice_amount))


def main(args):
    if not args.attacks:
        raise ValueError("You must provide at least one attack to make")

    # Read the die throw from console and parse them into objects
    attack_objects = []
    attacks_to_make = args.attacks
    for attack in attacks_to_make:
        die_to_throw = []
        bonuses = []

        has_advantage = False
        has_disadvantage = False
        if attack[-1] == "A":
            has_advantage = True
            attack = attack[:-1]
        if attack[-1] == "D":
            has_disadvantage = True
            attack = attack[:-1]

        for die_or_bonus in attack.split("+"):
            die_or_bonus = die_or_bonus.strip()
            die_or_bonus = parse_die_or_bonus(die_or_bonus)
            if type(die_or_bonus) == DiceThrow:
                die_to_throw.append(die_or_bonus)
            elif type(die_or_bonus) == Bonus:
                bonuses.append(die_or_bonus)

        attack_objects.append(Attack(
            die_expression=attack,
            die_to_throw=die_to_throw,
            bonuses=bonuses,
            attack_modifier=args.attack_modifier,
            has_advantage=has_advantage,
            has_disadvantage=has_disadvantage,
            force_critical_hit=args.force_critical_hit
        ))

    total_damage = 0
    for attack in attack_objects:
        attack.make()
        print(attack)
        total_damage += attack.damage_roll
    print(f"Total damage with these attacks: {total_damage} points of damage")

    if args.show_distribution:
        throws = []
        for _ in range(args.throws):
            throw = 0
            for attack in attack_objects:
                attack.make()
                throw += attack.damage_roll
            throws.append(throw)
        throw_statistics = dict.fromkeys(throws, 0)
        for value in throws:
            throw_statistics[value] += 1
        draw_statistics(throw_statistics)


if __name__ == "__main__":
    args = ArgumentParser(argv)
    args.add_argument("attacks", nargs="+",
                      help="The combination of die to throw. i.e. \"1d8+2d6+4\" // \"1d12+6\" // \"8d8+2d4+2d6+3\"")
    args.add_argument("--force-critical-hit", action="store_true", default=False, 
                      help="Whether to make all attacks force the attack roll as a critical hit")
    args.add_argument("--attack-modifier", type=int, default=0,
                      help="Specify the attack modifier of the character making the attack")
    args.add_argument("--show-distribution", action="store_true", default=False,
                      help="Specify whether to show a distribution graph")
    args.add_argument("--throws", type=int, default=10000,
                      help="Specify the number of times to repeat the die throw to calculate the distribution")

    main(args.parse_args())
