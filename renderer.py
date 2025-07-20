import pygame
import os
from constants import *

class Renderer:
    def __init__(self, disable_rendering=False):
        self.disable_rendering = disable_rendering
        if not disable_rendering:
            pygame.init()
            self.screen = pygame.Surface((FIELD_WIDTH + 200, FIELD_HEIGHT))  # Используем Surface вместо display
            self.font = pygame.font.SysFont('arial', 20)
            self.background = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
            self.background.fill((255, 255, 255))
        self.snapshot_dir = "snapshots"
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)

    def draw(self, state):
        if self.disable_rendering or not state:
            return
        self.screen.blit(self.background, (0, 0))
        for entity_list in [state['grass'], state['herbivores'], state['predators'], state['feces']]:
            for entity in entity_list:
                if entity.alive:
                    pygame.draw.rect(self.screen, entity.color, (entity.x, entity.y, entity.size, entity.size))

    def draw_statistics(self, state, speed, current_round, simulation_round, frames_skipped):
        if self.disable_rendering:
            return
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
        if self.disable_rendering or not state:
            return
        self.draw(state)
        self.draw_statistics(state, speed, current_round, simulation_round, frames_skipped)
        pygame.image.save(self.screen, snapshot_path)