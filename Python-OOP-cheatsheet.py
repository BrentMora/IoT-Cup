# ============================================================
# PYTHON OOP CHEAT SHEET (for Dart developers)
# ============================================================

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ── 1. CLASS & CONSTRUCTOR ───────────────────────────────────
# Dart:   class Animal { final String name; Animal(this.name); }
# Python: no 'final', uses __init__ instead of a named constructor

class Animal:
    # Class variable (shared across ALL instances — like Dart's static fields)
    kingdom = "Animalia"

    def __init__(self, name: str, age: int):
        # Instance variables (public by default)
        self.name = name
        self.age = age
        # "Private" variable — convention only (no true private in Python)
        # Dart uses '_name'; Python also uses '_name' (same convention!)
        self._energy = 100
        # Name-mangled (harder to access from outside — closest to private)
        self.__secret = "hidden"

    # ── 2. INSTANCE METHOD ──────────────────────────────────
    def speak(self) -> str:
        # 'self' is like 'this' in Dart, but you must declare it explicitly
        return f"{self.name} makes a sound."

    # ── 3. DUNDER / MAGIC METHODS ───────────────────────────
    # Dart: @override String toString() => ...
    def __str__(self) -> str:
        return f"Animal(name={self.name}, age={self.age})"

    def __repr__(self) -> str:
        # repr() is for developers; str() is for end-users
        return f"Animal({self.name!r}, {self.age!r})"

    # ── 4. PROPERTIES (getter & setter) ─────────────────────
    # Dart:  int get energy => _energy;
    #        set energy(int v) => _energy = v;
    @property
    def energy(self) -> int:
        return self._energy

    @energy.setter
    def energy(self, value: int):
        if value < 0:
            raise ValueError("Energy cannot be negative")
        self._energy = value

    # ── 5. CLASS METHOD & STATIC METHOD ─────────────────────
    # Dart: factory Animal.fromMap(Map m) — use @classmethod for this
    @classmethod
    def from_dict(cls, data: dict) -> "Animal":
        """Alternative constructor — like a Dart factory constructor."""
        return cls(data["name"], data["age"])

    # Dart: static String describe() => ...
    @staticmethod
    def describe() -> str:
        """No access to cls or self — pure utility function."""
        return "Animals are multicellular organisms."


# ── 6. INHERITANCE ───────────────────────────────────────────
# Dart:  class Dog extends Animal
# Python: class Dog(Animal)

class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)   # Dart: super(name, age)
        self.breed = breed

    # ── 7. METHOD OVERRIDING ────────────────────────────────
    # Dart: @override  (decorator is optional in Python, just redefine it)
    def speak(self) -> str:
        return f"{self.name} barks!"

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}."


# ── 8. ABSTRACT CLASS ────────────────────────────────────────
# Dart:  abstract class Shape { double area(); }
# Python: inherit from ABC and use @abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

    def describe(self) -> str:
        # Concrete method — available to all subclasses
        return f"I am a {type(self).__name__} with area {self.area():.2f}"


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


# ── 9. MULTIPLE INHERITANCE (no mixins keyword needed) ────────
# Dart uses 'with' for mixins; Python just lists multiple parents

class Flyable:
    def fly(self) -> str:
        return f"{self.__class__.__name__} is flying!"

class Swimmable:
    def swim(self) -> str:
        return f"{self.__class__.__name__} is swimming!"

class Duck(Animal, Flyable, Swimmable):
    def speak(self) -> str:
        return f"{self.name} quacks!"


# ── 10. DATACLASS (like Dart's copyWith / value objects) ──────
# Dart:  no built-in, often use freezed package
# Python: @dataclass auto-generates __init__, __repr__, __eq__

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0  # default value

    def distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5


# ── 11. DUNDER METHODS FOR OPERATOR OVERLOADING ───────────────
# Dart: you override operators with  operator +(other) => ...

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y})"


# ── DEMO ──────────────────────────────────────────────────────
if __name__ == "__main__":
    # Basic class usage
    dog = Dog("Rex", 3, "Labrador")
    print(dog)                          # Uses __str__ from Animal
    print(dog.speak())                  # Overridden method
    print(dog.energy)                   # Property getter
    dog.energy = 80                     # Property setter

    # Alternative constructor
    animal = Animal.from_dict({"name": "Leo", "age": 5})
    print(animal)

    # Abstract class
    c = Circle(5)
    print(c.describe())

    # Multiple inheritance
    duck = Duck("Donald", 2)
    print(duck.speak())
    print(duck.fly())
    print(duck.swim())

    # Dataclass
    p = Point(3.0, 4.0)
    print(p)                            # Auto-generated __repr__
    print(p.distance_to_origin())       # 5.0

    # Operator overloading
    v1 = Vector(1, 2)
    v2 = Vector(3, 4)
    print(v1 + v2)                      # Vector(4, 6)
    print(v1 == Vector(1, 2))           # True