# Python OOP Guide for Dart Developers

A plain-English walkthrough of Python's object-oriented features, written for developers coming from Dart.

---

## Table of Contents

1. [Class & Constructor](#1-class--constructor)
2. [Instance Methods](#2-instance-methods)
3. [Dunder / Magic Methods](#3-dunder--magic-methods)
4. [Properties (Getters & Setters)](#4-properties-getters--setters)
5. [Class Methods & Static Methods](#5-class-methods--static-methods)
6. [Inheritance](#6-inheritance)
7. [Method Overriding](#7-method-overriding)
8. [Abstract Classes](#8-abstract-classes)
9. [Multiple Inheritance](#9-multiple-inheritance)
10. [Dataclasses](#10-dataclasses)
11. [Operator Overloading](#11-operator-overloading)
12. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## 1. Class & Constructor

### What it does
A class is a blueprint for creating objects. The constructor is the code that runs automatically when you create a new object from that blueprint — it sets up the object's initial state.

### In plain English
Think of a class like a cookie cutter and an object as the cookie. The constructor (`__init__`) is the step where you press the cutter into the dough and stamp out the shape.

### Key syntax
```python
class Animal:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

- `class ClassName:` — declares a class (no curly braces, just a colon and indentation)
- `def __init__(self, ...)` — the constructor; always the first method you define
- `self` — refers to the current object, like `this` in Dart, **but you must write it explicitly in every method signature**
- `self.name = name` — creates an instance variable and assigns a value to it

### Variable visibility
```python
self.name     # Public — accessible from anywhere
self._name    # "Private" by convention — other devs know not to touch it (same as Dart's _name)
self.__name   # Name-mangled — Python renames it internally, making outside access harder
```

> **Dart vs Python:** Python has no `final`, `const`, or true `private` keyword. Privacy is enforced by convention, not the compiler.

---

## 2. Instance Methods

### What it does
Instance methods are functions that belong to an object. They can read and modify the object's own data.

### In plain English
If a class is a TV, instance methods are the buttons — each one does something specific to *that particular TV*, not all TVs in the world.

### Key syntax
```python
def speak(self) -> str:
    return f"{self.name} makes a sound."
```

- Every instance method **must** have `self` as its first parameter — Python passes the current object in automatically, but you still have to declare it
- `-> str` is a return type hint (optional but strongly recommended)
- `f"..."` is an f-string — Python's version of Dart's string interpolation (`'${variable}'`)

---

## 3. Dunder / Magic Methods

### What it does
Dunder methods (short for "double underscore") are special built-in methods that Python calls automatically in certain situations. You define them to customize how your objects behave.

### In plain English
Dunders let you teach Python what to do when someone prints your object, compares two objects, adds them together, and so on. They are Python's answer to operator overloading and `toString`.

### Key syntax
```python
def __str__(self) -> str:
    return f"Animal(name={self.name}, age={self.age})"

def __repr__(self) -> str:
    return f"Animal({self.name!r}, {self.age!r})"
```

- `__str__` — called by `print()` and `str()`; meant for human-readable output (like Dart's `toString()`)
- `__repr__` — called in the Python shell or by `repr()`; meant for developers and debugging; should ideally show enough detail to recreate the object
- `!r` inside an f-string adds quotes around strings automatically (useful in `__repr__`)

### Common dunders to know

| Method | When Python calls it |
|---|---|
| `__init__` | Object is created |
| `__str__` | `print(obj)` or `str(obj)` |
| `__repr__` | Developer/debug display |
| `__eq__` | `obj1 == obj2` |
| `__len__` | `len(obj)` |
| `__add__` | `obj1 + obj2` |

---

## 4. Properties (Getters & Setters)

### What it does
Properties let you control access to an object's internal data. A getter retrieves a value; a setter validates or transforms a value before storing it.

### In plain English
Imagine a hotel room with a "Do Not Disturb" sign. The getter lets someone check the status of the sign from outside. The setter makes sure only valid signs can be hung — you can't just tape a pizza box to the door.

### Key syntax
```python
@property
def energy(self) -> int:
    return self._energy

@energy.setter
def energy(self, value: int):
    if value < 0:
        raise ValueError("Energy cannot be negative")
    self._energy = value
```

- `@property` turns a method into a readable attribute — call it with `obj.energy`, not `obj.energy()`
- `@energy.setter` is the matching setter — triggered when you write `obj.energy = 80`
- You store the real value in a "private" variable (`_energy`) and expose it through the property
- If you define only `@property` and no setter, the attribute becomes **read-only**

> **Dart vs Python:** Dart uses the `get` and `set` keywords inline. Python uses decorators (`@property`, `@name.setter`) on separate methods.

---

## 5. Class Methods & Static Methods

### What it does
These are methods that don't belong to a specific object instance.

- A **class method** has access to the class itself, not a specific object. It's commonly used as an alternative constructor.
- A **static method** has no access to either the class or the object. It's a plain utility function that just happens to live inside the class for organizational reasons.

### In plain English
Imagine a bakery class. A class method would be a recipe that produces a Bakery object from a list of ingredients — it knows about the bakery concept but not about one specific bakery. A static method would be a unit converter sitting in a drawer — it doesn't need to know anything about the bakery to do its job.

### Key syntax
```python
@classmethod
def from_dict(cls, data: dict) -> "Animal":
    return cls(data["name"], data["age"])

@staticmethod
def describe() -> str:
    return "Animals are multicellular organisms."
```

- `@classmethod` — use `cls` (the class) as the first parameter instead of `self`
- `cls(...)` — calls the class constructor; useful for alternative constructors (like Dart's factory constructors)
- `@staticmethod` — no `self` or `cls`; behaves like a regular function
- Call them on the class directly: `Animal.from_dict(...)` or `Animal.describe()`

---

## 6. Inheritance

### What it does
Inheritance lets a new class take on all the attributes and methods of an existing class, then add or change things on top.

### In plain English
A `Dog` is an `Animal`. Instead of rewriting everything about animals, `Dog` just says "start with everything Animal has, then I'll add my own stuff on top."

### Key syntax
```python
class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)
        self.breed = breed
```

- `class Dog(Animal):` — `Dog` inherits from `Animal` (Dart uses `extends`)
- `super().__init__(name, age)` — calls the parent class constructor to set up the inherited parts (Dart: `super(name, age)`)
- After calling `super().__init__()`, you add the child class's own variables

---

## 7. Method Overriding

### What it does
If a child class defines a method with the same name as its parent, the child's version replaces the parent's version for that object.

### In plain English
An `Animal` makes a generic sound. A `Dog` overrides that to bark instead. If you call `speak()` on a `Dog`, you get a bark — Python automatically uses the most specific version available.

### Key syntax
```python
class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} barks!"
```

- Just redefine the method in the child class — no special keyword needed
- Python does **not** require `@override` (unlike Dart), but you can add it as a comment for clarity
- Python will always use the child's version if it exists, otherwise it walks up the inheritance chain

---

## 8. Abstract Classes

### What it does
An abstract class is a class that cannot be instantiated directly. It defines a contract — a list of methods that every subclass **must** implement.

### In plain English
Think of an abstract class as a job description. You can't hire a "job description" — you hire a specific person (subclass) who fulfills the requirements listed in it.

### Key syntax
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Circle(Shape):
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
```

- Import `ABC` and `abstractmethod` from Python's built-in `abc` module
- Inherit from `ABC` to make a class abstract
- Decorate methods with `@abstractmethod` to require subclasses to implement them
- `pass` is a no-op placeholder — the body of an abstract method is intentionally left empty
- If a subclass doesn't implement all abstract methods, Python raises a `TypeError` when you try to instantiate it

> **Dart vs Python:** Dart uses the `abstract` keyword before the class. Python uses `ABC` as a parent class.

---

## 9. Multiple Inheritance

### What it does
A class can inherit from more than one parent class at the same time, gaining the methods and attributes of all of them.

### In plain English
A `Duck` is an `Animal`, but it can also `Fly` and `Swim`. Instead of a dedicated mixin system, Python just lets you list multiple parents separated by commas.

### Key syntax
```python
class Flyable:
    def fly(self) -> str:
        return f"{self.__class__.__name__} is flying!"

class Duck(Animal, Flyable, Swimmable):
    def speak(self) -> str:
        return f"{self.name} quacks!"
```

- List all parent classes inside the parentheses: `class Child(Parent1, Parent2, ...)`
- `self.__class__.__name__` — gives you the name of the actual class at runtime (e.g., `"Duck"`)
- Python resolves method conflicts using the **MRO (Method Resolution Order)** — it searches left to right through the parent list

> **Dart vs Python:** Dart separates inheritance (`extends`) from mixins (`with`). Python uses one unified syntax for both.

---

## 10. Dataclasses

### What it does
A dataclass is a shortcut for creating simple classes that mainly hold data. Python auto-generates the constructor, `__repr__`, and equality comparison for you.

### In plain English
Instead of writing the same boilerplate `__init__` every time just to store a few values, you slap a `@dataclass` decorator on the class and Python handles it automatically.

### Key syntax
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0   # default value
```

- `@dataclass` — the decorator that does all the magic
- Declare fields directly in the class body with type annotations (`x: float`)
- Fields with default values must come **after** fields without defaults
- You get `__init__`, `__repr__`, and `__eq__` for free
- You can still add your own methods — a dataclass is a regular class with extras

> **Dart vs Python:** Dart has no built-in equivalent; developers often use packages like `freezed`. Python's `@dataclass` is part of the standard library.

---

## 11. Operator Overloading

### What it does
Operator overloading lets you define what happens when standard operators (`+`, `-`, `==`, etc.) are used on your custom objects.

### In plain English
By default, Python doesn't know how to add two `Vector` objects. By defining `__add__`, you teach it: "when someone writes `v1 + v2`, do this math and return a new Vector."

### Key syntax
```python
class Vector:
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y
```

- `__add__` — handles the `+` operator
- `__eq__` — handles the `==` operator
- `isinstance(other, Vector)` — checks if the other object is the right type before comparing
- `return NotImplemented` — the polite way to tell Python "I don't know how to handle this comparison; try the other object's method"
- `"Vector"` in quotes — a **forward reference**; used when the class isn't fully defined yet at the point of the type hint

> **Dart vs Python:** Dart uses `operator +(other)` syntax. Python uses specially named dunder methods for each operator.

---

## Quick Reference Cheat Sheet

### Syntax comparison

| Concept | Dart | Python |
|---|---|---|
| Define a class | `class Dog {}` | `class Dog:` |
| Constructor | `Dog(this.name)` | `def __init__(self, name)` |
| Refer to current object | `this` (implicit) | `self` (explicit, always declared) |
| Inheritance | `class Dog extends Animal` | `class Dog(Animal):` |
| Call parent constructor | `super(name)` | `super().__init__(name)` |
| Abstract class | `abstract class Shape {}` | `class Shape(ABC):` |
| Abstract method | `double area();` | `@abstractmethod` + `def area(self): pass` |
| Mixin | `class Duck with Flyable` | `class Duck(Animal, Flyable):` |
| Getter | `int get energy => _energy;` | `@property` decorator |
| Setter | `set energy(int v) { ... }` | `@energy.setter` decorator |
| Static method | `static String describe()` | `@staticmethod` + no `self` |
| Factory constructor | `factory Animal.fromMap(m)` | `@classmethod` + `cls(...)` |
| toString | `@override String toString()` | `def __str__(self)` |
| Operator overload | `operator +(other) => ...` | `def __add__(self, other)` |
| Private variable | `String _name` (enforced) | `self._name` (convention only) |
| Type annotation | `String name` | `name: str` |
| Default parameter | `void foo({int x = 0})` | `def foo(x: int = 0)` |

### Python-specific things that don't exist in Dart

| Feature | What it is |
|---|---|
| `@dataclass` | Auto-generates `__init__`, `__repr__`, `__eq__` for data-holder classes |
| `__repr__` | A second string representation specifically for developers/debugging |
| `pass` | A no-op placeholder; required when a block would otherwise be empty |
| `*args` / `**kwargs` | Accept variable numbers of positional / keyword arguments |
| Duck typing | Python checks behavior at runtime, not types at compile time |
| MRO | How Python resolves which parent's method wins in multiple inheritance |

### Common pitfalls coming from Dart

1. **Forgetting `self`** — every instance method and property must have `self` as the first parameter, or Python will throw an error
2. **No compile-time type safety** — type hints are informational only; Python won't stop you from passing the wrong type at runtime (use `mypy` for static checking)
3. **Indentation is the syntax** — there are no curly braces; a wrong indent is a bug
4. **No `const` or `final`** — Python has no built-in way to make a variable truly immutable (use `@dataclass(frozen=True)` for immutable dataclasses)
5. **`==` vs `is`** — `==` checks value equality (like Dart's `==`), while `is` checks if two variables point to the exact same object in memory