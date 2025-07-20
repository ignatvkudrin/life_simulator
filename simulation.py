# simulation.py
import random
import copy
from threading import Thread
import pickle
from constants import *
from entities import Grass, Herbivore, Predator, Feces, QuadTree
from utils import distance  # Добавлен импорт distance

class Simulation:
    def __init__(self):
        self.grass = []
        self.herbivores = []
        self.predators = []
        self.feces = []
        self.states = []
        self.current_round = 0
        self.simulation_round = 0
        self.speed = 1
        self.running = True
        self.save_interval = max(1, int(30 / ROUNDS_PER_SECOND))  # Например, 30 / 10 = 3 раунда на снимок

    def initialize(self):
        print("Инициализация симуляции...")
        try:
            for _ in range(INITIAL_GRASS_COUNT):
                self.grass.append(Grass(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT)))
            for _ in range(INITIAL_HERBIVORE_COUNT):
                self.herbivores.append(Herbivore(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT)))
            for _ in range(INITIAL_PREDATOR_COUNT):
                self.predators.append(Predator(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT)))
            self.save_state()
            print(f"Начальное состояние сохранено: {len(self.grass)} травы, {len(self.herbivores)} травоядных, {len(self.predators)} хищников")
        except Exception as e:
            print(f"Ошибка при инициализации: {e}")
            raise

    def save_state(self):
        try:
            state = {
                'grass': copy.deepcopy(self.grass),
                'herbivores': copy.deepcopy(self.herbivores),
                'predators': copy.deepcopy(self.predators),
                'feces': copy.deepcopy(self.feces),
                'round': self.simulation_round
            }
            pickle.dumps(state)  # Тестовая сериализация
            self.states.append(state)
            while len(self.states) > 50:  # Ограничить буфер до 50 состояний
                self.states.pop(0)
        except Exception as e:
            print(f"Ошибка при сохранении состояния: {e}")

    def update_herbivores(self):
        grass_quadtree = QuadTree(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
        for g in self.grass:
            if g.alive:
                grass_quadtree.insert(g)
        new_herbivores = []
        for herbivore in self.herbivores:
            if herbivore.alive:
                herbivore.move(grass_quadtree)
                new_herbivores.extend(herbivore.eat(grass_quadtree, self.feces))
        self.herbivores[:] = [h for h in self.herbivores if h.alive] + new_herbivores

    def update_predators(self):
        herbivore_quadtree = QuadTree(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
        for h in self.herbivores:
            if h.alive:
                herbivore_quadtree.insert(h)
        new_predators = []
        for predator in self.predators:
            if predator.alive:
                predator.move(herbivore_quadtree)
                new_predators.extend(predator.eat(herbivore_quadtree, self.feces))
                predator.update_hunger()
        self.predators[:] = [p for p in self.predators if p.alive] + new_predators

    def update_all(self):
        try:
            print(f"Запуск update_all, раунд {self.simulation_round}")
            # Обновление травы
            new_grass = []
            for _ in range(GRASS_SPAWN_PER_ROUND):
                new_grass.append(Grass(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT)))
            for f in list(self.feces):
                if not f.alive:
                    continue
                for g in list(self.grass):
                    if g.alive and distance(f.x, f.y, g.x, g.y) < GRASS_SPAWN_RADIUS:
                        for _ in range(GRASS_SPAWN_BONUS):
                            new_grass.append(Grass(f.x + random.uniform(-5, 5), f.y + random.uniform(-5, 5)))
                        f.alive = False
                        break
            self.grass[:] = [g for g in self.grass if g.alive] + new_grass
            self.feces[:] = [f for f in self.feces if f.alive]

            # Запуск обновления травоядных и хищников в отдельных потоках
            herbivore_thread = Thread(target=self.update_herbivores)
            predator_thread = Thread(target=self.update_predators)
            herbivore_thread.start()
            predator_thread.start()
            herbivore_thread.join()
            predator_thread.join()

            if not any(h.alive for h in self.herbivores) or not any(p.alive for p in self.predators):
                self.running = False
                print("Симуляция остановлена: все травоядные или хищники вымерли")
        except Exception as e:
            print(f"Ошибка в update_all: {e}")
            self.running = False
            raise

    def update(self):
        if not self.running:
            return
        print(f"Обновление симуляции, раунд {self.simulation_round}")
        try:
            self.update_all()
            self.simulation_round += 1
            if self.simulation_round % self.save_interval == 0:
                self.save_state()
                print(f"Состояние сохранено для раунда {self.simulation_round}")
        except Exception as e:
            print(f"Ошибка в update: {e}")
            self.running = False

    def adjust_speed(self, increase):
        self.speed = min(self.speed + 1, 100) if increase else max(self.speed - 1, 1)
        print(f"Скорость изменена на {self.speed}")

    def stop(self):
        self.running = False
        print("Симуляция остановлена")

    def get_current_state(self, round_num):
        for state in self.states:
            if state['round'] == round_num:
                return state
        print(f"Состояние для раунда {round_num} не найдено")
        return None