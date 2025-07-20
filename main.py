import pygame
import time
import cv2
import os
import glob
import shutil
from simulation import Simulation
from renderer import Renderer
from constants import *

def create_video(snapshot_dir, output_path, fps=30):
    print("Создание видео...")
    images = sorted(glob.glob(os.path.join(snapshot_dir, "snapshot_*.png")), key=lambda x: int(x.split('_')[-1].split('.')[0]))
    if not images:
        print("Ошибка: снимки не найдены в папке snapshots!")
        return

    try:
        frame = cv2.imread(images[0])
        if frame is None:
            print(f"Ошибка: не удалось загрузить изображение {images[0]}")
            return
        height, width, _ = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for image in images:
            frame = cv2.imread(image)
            if frame is None:
                print(f"Ошибка: не удалось загрузить изображение {image}")
                continue
            video.write(frame)

        video.release()
        print(f"Видео сохранено как {output_path}")
    except Exception as e:
        print(f"Ошибка при создании видео: {e}")

def main():
    try:
        snapshot_dir = "snapshots"
        output_path = "simulation_output.mp4"
        if os.path.exists(snapshot_dir):
            shutil.rmtree(snapshot_dir)
            print(f"Папка {snapshot_dir} очищена")
        os.makedirs(snapshot_dir)
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"Видео {output_path} удалено")

        # Инициализация симуляции
        simulation = Simulation()
        renderer = Renderer(disable_rendering=False)  # Отключаем рендеринг
        simulation.initialize()
        print("Симуляция инициализирована")

        snapshot_interval = max(1, int(60 / ROUNDS_PER_SECOND))  # Синхронизировано с save_interval
        frames_skipped = 0
        start_time = time.time()

        # Первый раунд
        round_start_time = time.time()
        simulation.update()
        if time.time() - round_start_time > 60:
            print(f"Начальный раунд превысил 60 секунд, остановка симуляции...")
            simulation.stop()
        else:
            state = simulation.get_current_state(0)
            if state and not renderer.disable_rendering:
                snapshot_path = os.path.join(renderer.snapshot_dir, f"snapshot_{simulation.current_round:06d}.png")
                renderer.save_snapshot(state, simulation.speed, simulation.current_round, simulation.simulation_round, frames_skipped, snapshot_path)
                print(f"Снимок сохранён для раунда {simulation.current_round}")

        # Основной цикл
        while simulation.simulation_round < MAX_ROUNDS and simulation.running:
            round_start_time = time.time()
            simulation.update()
            round_time = time.time() - round_start_time
            print(f"Раунд {simulation.simulation_round} выполнен за {round_time:.3f} секунд")
            if round_time > 60:
                print(f"Раунд {simulation.simulation_round} превысил 60 секунд, остановка симуляции...")
                simulation.stop()
                break

            if simulation.simulation_round % snapshot_interval == 0:
                simulation.current_round = simulation.simulation_round
                state = simulation.get_current_state(simulation.current_round)
                if state and not renderer.disable_rendering:
                    snapshot_path = os.path.join(renderer.snapshot_dir, f"snapshot_{simulation.current_round:06d}.png")
                    renderer.save_snapshot(state, simulation.speed, simulation.current_round, simulation.simulation_round, frames_skipped, snapshot_path)
                    print(f"Снимок сохранён для раунда {simulation.current_round}")
            frames_skipped += 1

        # Создание видео, если рендеринг включён
        if not renderer.disable_rendering:
            create_video(renderer.snapshot_dir, output_path, fps=30)

        simulation.stop()
        if not renderer.disable_rendering:
            pygame.quit()
        print(f"Программа завершена. Общее время: {time.time() - start_time:.2f} секунд")
    except Exception as e:
        print(f"Ошибка: {e}")
        if not renderer.disable_rendering:
            pygame.quit()

if __name__ == "__main__":
    main()