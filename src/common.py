from random import randint
from dataclasses import dataclass
from dataclasses import field

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
    reroll_values: list[int] = field(default_factory=list)

    def get_value(self) -> int:
        value = 0
        for _ in range(self.n):
            result = randint(1, self.faces)
            if result in self.reroll_values:
                result = randint(1, self.faces)
            value += result
        return value

    def get_max(self) -> int:
        return self.n * self.faces

    def get_min(self) -> int:
        return self.n
