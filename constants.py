# constants.py
# Размеры игрового поля
FIELD_WIDTH = 400  # Ширина поля в пикселях
FIELD_HEIGHT = 400  # Высота поля в пикселях

# Начальное количество сущностей
INITIAL_GRASS_COUNT = 10  # Начальное количество травы
INITIAL_HERBIVORE_COUNT = 200  # Начальное количество травоядных
INITIAL_PREDATOR_COUNT = 1  # Начальное количество хищников

# Параметры симуляции
MAX_ROUNDS = 1000  # Максимальное количество раундов для симуляции
ROUNDS_PER_SECOND = 100  # Количество раундов в секунду в видео

# Параметры травы
GRASS_SPAWN_PER_ROUND = 2  # Количество новой травы, появляющейся за раунд
GRASS_SPAWN_BONUS = 2  # Дополнительная трава, появляющаяся рядом с экскрементами
GRASS_SPAWN_RADIUS = 10  # Радиус появления новой травы вокруг экскрементов

# Параметры травоядных
HERBIVORE_SPEED = 1  # Скорость движения травоядного (пиксели/раунд)
HERBIVORE_SPEED_TO_GRASS = 2  # Скорость движения к траве (пиксели/раунд)
HERBIVORE_VISION = 10  # Радиус обзора травоядного для поиска травы
HERBIVORE_REPRODUCTION_COUNT = 3  # Количество потомков при размножении
HERBIVORE_GRASS_TO_REPRODUCE = 10  # Количество травы, необходимое для размножения

# Параметры хищников
PREDATOR_SPEED = 2  # Скорость движения хищника (пиксели/раунд)
PREDATOR_SPEED_TO_PREY = 3  # Скорость движения к добыче (пиксели/раунд)
PREDATOR_VISION = 15  # Радиус обзора хищника для поиска травоядных
PREDATOR_EATING_TIME = 50  # Время переваривания добычи (раунды)
PREDATOR_REPRODUCTION_COUNT = 2  # Количество потомков при размножении
PREDATOR_FECES_INTERVAL = 5  # Интервал появления экскрементов (раунды)
PREDATOR_HUNGER_MAX = 200  # Максимальный уровень голода хищника
PREDATOR_HUNGER_DECREASE = 1  # Уменьшение голода за раунд

# Цвета сущностей
COLOR_GRASS = (0, 255, 0)  # Цвет травы (RGB)
COLOR_HERBIVORE = (128, 0, 128)  # Цвет травоядного (RGB)
COLOR_PREDATOR = (255, 0, 0)  # Цвет хищника (RGB)
COLOR_FECES = (139, 69, 19)  # Цвет экскрементов (RGB)