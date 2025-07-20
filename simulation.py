import random
import copy
from threading import Thread
import pickle
from constants import *
from entities import Grass, Herbivore, Predator, Feces, QuadTree
from utils import distance

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
        self.save_interval = max(1, int(60 / ROUNDS_PER_SECOND))  # Увеличено с 30 до 60 FPS для реже сохранения

    def initialize(self):
        print("Инициализация симуляции...")
        try:
            self.grass = [Grass(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT))
                          for _ in range(INITIAL_GRASS_COUNT)]
            self.herbivores = [Herbivore(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT))
                               for _ in range(INITIAL_HERBIVORE_COUNT)]
            self.predators = [Predator(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT))
                              for _ in range(INITIAL_PREDATOR_COUNT)]
            self.save_state()
            print(f"Начальное состояние сохранено: {len(self.grass)} травы, {len(self.herbivores)} травоядных, {len(self.predators)} хищников")
        except Exception as e:
            print(f"Ошибка при инициализации: {e}")
            raise

    def save_state(self):
        try:
            state = {
                'grass': [g for g in self.grass if g.alive],
                'herbivores': [h for h in self.herbivores if h.alive],
                'predators': [p for p in self.predators if p.alive],
                'feces': [f for f in self.feces if f.alive],
                'round': self.simulation_round
            }
            pickle.dumps(state)
            self.states.append(state)
            while len(self.states) > 20:  # Уменьшено с 50 до 20
                self.states.pop(0)
        except Exception as e:
            print(f"Ошибка при сохранении состояния: {e}")

    def update_herbivores(self):
        grass_quadtree = QuadTree(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
        for g in [g for g in self.grass if g.alive]:
            grass_quadtree.insert(g)
        new_herbivores = []
        for herbivore in self.herbivores:
            if herbivore.alive:
                herbivore.move(grass_quadtree)
                new_herbivores.extend(herbivore.eat(grass_quadtree, self.feces))
        self.herbivores[:] = [h for h in self.herbivores if h.alive] + new_herbivores
        grass_quadtree.clear_cache()

    def update_predators(self):
        herbivore_quadtree = QuadTree(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
        for h in [h for h in self.herbivores if h.alive]:
            herbivore_quadtree.insert(h)
        new_predators = []
        for predator in self.predators:
            if predator.alive:
                predator.move(herbivore_quadtree)
                new_predators.extend(predator.eat(herbivore_quadtree, self.feces))
                predator.update_hunger()
        self.predators[:] = [p for p in self.predators if p.alive] + new_predators
        herbivore_quadtree.clear_cache()

    def update_all(self):
        try:
            print(f"Запуск update_all, раунд {self.simulation_round}")
            new_grass = [Grass(random.uniform(0, FIELD_WIDTH), random.uniform(0, FIELD_HEIGHT))
                         for _ in range(GRASS_SPAWN_PER_ROUND)]
            for f in [f for f in self.feces if f.alive]:
                for g in [g for g in self.grass if g.alive]:
                    if distance(f.x, f.y, g.x, g.y) < GRASS_SPAWN_RADIUS:
                        new_grass.extend([Grass(f.x + random.uniform(-5, 5), f.y + random.uniform(-5, 5))
                                          for _ in range(GRASS_SPAWN_BONUS)])
                        f.alive = False
                        break
            self.grass[:] = [g for g in self.grass if g.alive] + new_grass
            self.feces[:] = [f for f in self.feces if f.alive]

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