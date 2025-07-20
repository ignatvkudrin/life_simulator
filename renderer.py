# renderer.py
import pygame
import os
from constants import *

class Renderer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((FIELD_WIDTH + 200, FIELD_HEIGHT))
        pygame.display.set_caption("Life Simulator")
        self.font = pygame.font.SysFont('arial', 20)
        self.background = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
        self.background.fill((255, 255, 255))
        self.snapshot_dir = "snapshots"
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)

    def draw(self, state):
        if not state:
            return
        self.screen.blit(self.background, (0, 0))
        for grass in state['grass']:
            if grass.alive:
                pygame.draw.rect(self.screen, grass.color, (grass.x, grass.y, grass.size, grass.size))
        for feces in state['feces']:
            if feces.alive:
                pygame.draw.rect(self.screen, feces.color, (feces.x, feces.y, grass.size, grass.size))
        for herbivore in state['herbivores']:
            if herbivore.alive:
                pygame.draw.rect(self.screen, herbivore.color, (herbivore.x, herbivore.y, herbivore.size, herbivore.size))
        for predator in state['predators']:
            if predator.alive:
                pygame.draw.rect(self.screen, predator.color, (predator.x, predator.y, predator.size, predator.size))

    def draw_statistics(self, state, speed, current_round, simulation_round, frames_skipped):
        stats_surface = pygame.Surface((200, FIELD_HEIGHT))
        stats_surface.fill((200, 200, 200))
        if state:
            avg_hunger = sum(p.hunger for p in state['predators'] if p.alive) / max(1, len([p for p in state['predators'] if p.alive]))
            stats = [
                f"Травы: {len([g for g in state['grass'] if g.alive])}",
                f"Травоядных: {len([h for h in state['herbivores'] if h.alive])}",
                f"Хищников: {len([p for p in state['predators'] if p.alive])}",
                f"Экскрементов: {len([f for f in state['feces'] if f.alive])}",
                f"Средний голод: {avg_hunger:.1f}",
                f"Скорость: x{speed}",
                f"Раунд: {current_round}",
                f"Раундов вперёд: {simulation_round - current_round}",
                f"Пропущено кадров: {frames_skipped}",
            ]
        else:
            stats = ["Ожидание состояния..."]
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, (0, 0, 0))
            stats_surface.blit(text, (10, 10 + i * 30))
        self.screen.blit(stats_surface, (FIELD_WIDTH, 0))

    def save_snapshot(self, state, speed, current_round, simulation_round, frames_skipped, snapshot_path):
        if not state:
            return
        self.draw(state)
        self.draw_statistics(state, speed, current_round, simulation_round, frames_skipped)
        pygame.image.save(self.screen, snapshot_path)