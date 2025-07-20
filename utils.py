# utils.py
import math

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def normalize_vector(dx, dy):
    magnitude = math.sqrt(dx ** 2 + dy ** 2)
    if magnitude == 0:
        return 0, 0
    return dx / magnitude, dy / magnitude