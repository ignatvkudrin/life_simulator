# entities.py
import random
import math
from constants import *
from utils import distance, normalize_vector

class QuadTree:
    def __init__(self, x, y, width, height, capacity=8):
        self.x = x  # Координата x верхнего левого угла области
        self.y = y  # Координата y верхнего левого угла области
        self.width = width  # Ширина области
        self.height = height  # Высота области
        self.capacity = capacity  # Максимальное количество сущностей в узле
        self.entities = []  # Список сущностей в текущем узле
        self.divided = False  # Флаг, разделён ли узел
        self.nw = None  # Северо-западный подузел
        self.ne = None  # Северо-восточный подузел
        self.sw = None  # Юго-западный подузел
        self.se = None  # Юго-восточный подузел
        # Кэшируем границы для оптимизации
        self.x_min = x
        self.x_max = x + width
        self.y_min = y
        self.y_max = y + height

    def subdivide(self):
        # Делит область на четыре квадранта
        half_w = self.width / 2
        half_h = self.height / 2
        x, y = self.x, self.y
        self.nw = QuadTree(x, y, half_w, half_h, self.capacity)
        self.ne = QuadTree(x + half_w, y, half_w, half_h, self.capacity)
        self.sw = QuadTree(x, y + half_h, half_w, half_h, self.capacity)
        self.se = QuadTree(x + half_w, y + half_h, half_w, half_h, self.capacity)
        self.divided = True
        # Перераспределяем существующие сущности в подузлы
        entities_to_redistribute = self.entities
        self.entities = []
        for entity in entities_to_redistribute:
            self.insert(entity)

    def insert(self, entity):
        # Проверяем, находится ли сущность в пределах области узла
        if not (self.x_min <= entity.x < self.x_max and self.y_min <= entity.y < self.y_max):
            return False
        # Если узел не разделён и есть место, добавляем сущность
        if len(self.entities) < self.capacity and not self.divided:
            self.entities.append(entity)
            return True
        # Если узел не разделён, но вместимость превышена, делим его
        if not self.divided:
            self.subdivide()
        # Пытаемся вставить сущность в один из подузлов
        return (self.nw.insert(entity) or
                self.ne.insert(entity) or
                self.sw.insert(entity) or
                self.se.insert(entity))

    def query(self, x, y, radius):
        # Находим сущности в радиусе radius от точки (x, y)
        found = []
        # Точная проверка пересечения круга с прямоугольником
        closest_x = max(self.x_min, min(x, self.x_max))
        closest_y = max(self.y_min, min(y, self.y_max))
        dist_to_rect = distance(x, y, closest_x, closest_y)
        if dist_to_rect > radius:
            return found
        # Проверяем сущности в текущем узле
        for entity in self.entities:
            if entity.alive and distance(x, y, entity.x, entity.y) <= radius:
                found.append(entity)
        # Если узел разделён, рекурсивно проверяем подузлы
        if self.divided:
            found.extend(self.nw.query(x, y, radius))
            found.extend(self.ne.query(x, y, radius))
            found.extend(self.sw.query(x, y, radius))
            found.extend(self.se.query(x, y, radius))
        return found

class Entity:
    def __init__(self, x, y, color, size):
        self.x = x  # Координата x сущности
        self.y = y  # Координата y сущности
        self.color = color  # Цвет сущности (RGB)
        self.size = size  # Размер сущности (для рендеринга и столкновений)
        self.alive = True  # Флаг, жива ли сущность

class Grass(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_GRASS, 1)  # Трава: зелёная, размер 1

class Feces(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_FECES, 1)  # Экскременты: коричневые, размер 1

class Herbivore(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_HERBIVORE, 2)  # Травоядное: фиолетовое, размер 2
        while True:
            dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
            if abs(dx) > 0.2 or abs(dy) > 0.2:  # Убедимся, что направление не слишком слабое
                self.direction = (dx, dy)
                break
        self.grass_eaten = 0  # Счётчик съеденной травы

    def move(self, grass_quadtree):
        # Движение травоядного к ближайшей траве или случайно
        nearest_grass = None
        min_dist = float('inf')
        nearby_grass = grass_quadtree.query(self.x, self.y, HERBIVORE_VISION)
        for grass in nearby_grass:
            if grass.alive:
                dist = distance(self.x, self.y, grass.x, grass.y)
                if dist < min_dist:
                    min_dist = dist
                    nearest_grass = grass

        if nearest_grass:
            dx = nearest_grass.x - self.x
            dy = nearest_grass.y - self.y
            dx, dy = normalize_vector(dx, dy)
            self.x += dx * HERBIVORE_SPEED_TO_GRASS
            self.y += dy * HERBIVORE_SPEED_TO_GRASS
        else:
            dx, dy = normalize_vector(*self.direction)
            self.x += dx * HERBIVORE_SPEED
            self.y += dy * HERBIVORE_SPEED
            self.direction = (random.uniform(-1, 1), random.uniform(-1, 1))

        # Ограничиваем движение пределах поля
        self.x = max(0, min(self.x, FIELD_WIDTH - self.size))
        self.y = max(0, min(self.y, FIELD_HEIGHT - self.size))

    def eat(self, grass_quadtree, feces_list):
        # Поедание травы и размножение
        new_herbivores = []
        nearby_grass = grass_quadtree.query(self.x, self.y, self.size)
        for grass in nearby_grass:
            if grass.alive:
                grass.alive = False
                self.grass_eaten += 1
                if self.grass_eaten >= HERBIVORE_GRASS_TO_REPRODUCE:
                    self.grass_eaten = 0
                    feces_list.append(Feces(self.x, self.y))
                    new_herbivores.extend([
                        Herbivore(self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5))
                        for _ in range(HERBIVORE_REPRODUCTION_COUNT)
                    ])
                break
        return new_herbivores

class Predator(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_PREDATOR, 6)  # Хищник: красный, размер 6
        self.hunger = PREDATOR_HUNGER_MAX  # Начальный уровень голода
        while True:
            dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
            if abs(dx) > 0.2 or abs(dy) > 0.2:
                self.direction = (dx, dy)
                break
        self.eating_timer = 0  # Таймер переваривания
        self.feces_timer = 0  # Таймер появления экскрементов
        self.target = None  # Цель (травоядное)

    def move(self, herbivore_quadtree):
        # Движение хищника к добыче или случайно
        if self.eating_timer > 0:
            self.eating_timer -= 1
            self.hunger = PREDATOR_HUNGER_MAX
            return

        nearest_herbivore = None
        min_dist = float('inf')
        nearby_herbivores = herbivore_quadtree.query(self.x, self.y, PREDATOR_VISION)
        for herbivore in nearby_herbivores:
            if herbivore.alive:
                dist = distance(self.x, self.y, herbivore.x, herbivore.y)
                if dist < min_dist:
                    min_dist = dist
                    nearest_herbivore = herbivore

        if nearest_herbivore:
            self.target = nearest_herbivore
            dx = nearest_herbivore.x - self.x
            dy = nearest_herbivore.y - self.y
            dx, dy = normalize_vector(dx, dy)
            self.x += dx * PREDATOR_SPEED_TO_PREY
            self.y += dy * PREDATOR_SPEED_TO_PREY
        else:
            self.target = None
            dx, dy = normalize_vector(*self.direction)
            self.x += dx * PREDATOR_SPEED
            self.y += dy * PREDATOR_SPEED
            self.direction = (random.uniform(-1, 1), random.uniform(-1, 1))

        # Ограничиваем движение пределах поля
        self.x = max(0, min(self.x, FIELD_WIDTH - self.size))
        self.y = max(0, min(self.y, FIELD_HEIGHT - self.size))
        self.hunger -= PREDATOR_HUNGER_DECREASE

    def eat(self, herbivore_quadtree, feces_list):
        # Поедание травоядного и размножение
        self.feces_timer += 1
        if self.feces_timer >= PREDATOR_FECES_INTERVAL:
            self.feces_timer = 0
            feces_list.append(Feces(self.x, self.y))

        if self.target and self.target.alive:
            nearby_herbivores = herbivore_quadtree.query(self.x, self.y, self.size)
            if self.target in nearby_herbivores:
                self.target.alive = False
                self.target = None
                self.eating_timer = PREDATOR_EATING_TIME
                self.hunger = PREDATOR_HUNGER_MAX
                return []
        elif self.eating_timer == 1:
            self.eating_timer = 0
            return [Predator(self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5))
                    for _ in range(PREDATOR_REPRODUCTION_COUNT)]
        return []

    def update_hunger(self):
        # Обновление голода хищника
        if self.hunger <= 0:
            self.alive = False