import enum


class ItemCategory(str, enum.Enum):
    food = "food"
    clothes = "clothes"
    water = "water"
    medicine = "medicine"
    stationary = "stationary"
