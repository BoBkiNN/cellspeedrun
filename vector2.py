import math

class Vector:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
    
    @staticmethod
    def fromTuple(t: tuple):
        return Vector(t[0], t[1])
    
    def add(self, x: int = 0, y: int = 0):
        self.x+=x
        self.y+=y

    def asList(self):
        return [self.x, self.y]
    
    def copy(self):
        return Vector(self.x, self.y)
    
    def __abs__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def __len__(self) -> float:
        return abs(self)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return str(self)

    def normalize(self):
        lenght = abs(self)
        if lenght > 0:
            self.x /= lenght
            self.y /= lenght