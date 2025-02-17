import pygame, sys

# Инициализация pygame
pygame.init()

# Размеры экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Маг в подземелье')

# Цвета
WHITE    = (0, 255, 255)
BLACK    = (0, 0, 0)
RED      = (200, 50, 50) 
BLUE     = (50, 50, 200)
YELLOW   = (200, 200, 50)
GRAY = (50, 50, 50)

# Загрузка заднего фона
global_bg = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/global_background.png')
global_bg = pygame.transform.scale(global_bg, (WIDTH, HEIGHT))

player_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/player.png')
enemy_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/enemy.png')
enemy2_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/enemy2.png')
background_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/background.png')
chest_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/chest.png')
library_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/library.png')

# Текстуры для комнаты с ловушками
floor_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/floor.png')
trap_img = pygame.image.load('/Users/tpaba/Desktop/Игра на Python/Текстуры/trap.png')

# Масштабы текстур для комнат
player_img = pygame.transform.scale(player_img, (100, 100))
enemy_img = pygame.transform.scale(enemy_img, (100, 100))
enemy2_img = pygame.transform.scale(enemy2_img, (100, 100))
background_img = pygame.transform.scale(background_img, (700, 400))
chest_img = pygame.transform.scale(chest_img, (150, 150))
library_img = pygame.transform.scale(library_img, (700, 400))

# --- Настройки комнаты с ловушками ---
# Размеры клетки комнаты с ловушками
TRAP_CELL_WIDTH = 70
TRAP_CELL_HEIGHT = 80

# Масштабирование текстур для комнаты с ловушками
floor_img = pygame.transform.scale(floor_img, (TRAP_CELL_WIDTH, TRAP_CELL_HEIGHT))
trap_img = pygame.transform.scale(trap_img, (TRAP_CELL_WIDTH, TRAP_CELL_HEIGHT))
# Текстура сундука для восстановления (на клетке (9,0))
trap_chest_img = pygame.transform.scale(chest_img, (TRAP_CELL_WIDTH, TRAP_CELL_HEIGHT))

# Класс для врагов
class Enemy:
    def __init__(self, name, hp, weakness, immunity):
        self.name = name          # Имя врага
        self.hp = hp              # Здоровье врага
        self.weakness = weakness  # Слабость (заклинание, наносящее критический урон)
        self.immunity = immunity  # Иммунитет (заклинание, не наносящее урон)
        self.alive = True         # Флаг: враг жив

    def take_damage(self, spell):
        # Наносим урон в зависимости от выбранного заклинания
        if spell == self.immunity:
            return # Иммунитет
        elif spell == self.weakness:
            self.hp -= 20
            return # Критический урон
        else:
            self.hp -= 10
            return # Обычный урон

# Основной класс игры
class Game:
    def __init__(self):
        # Последовательность комнат: 0 и 2 – боевые, 1 – ловушечная, 3 – победная
        self.rooms = ["enemy", "trap", "enemy", "victory"]
        self.current_room = 0  # Начинаем с первой комнаты
        self.spells = ['огонь', 'молния', 'лёд']  # Доступные заклинания
        self.font = pygame.font.Font(None, 36)      # Шрифт для сообщений

        # Создаём врагов для боевых комнат
        self.enemy_rooms = [
            Enemy('ледяной голем', 30, 'огонь', 'лёд'),
            Enemy('Электрический атронарх', 30, 'лёд', 'молния')
        ]

        # Карта ловушечной комнаты (5 строк по 10 символов)
        # Символ '#' означает ловушку, '.' – пустая клетка
        self.trap_map = [
            "...#......",
            "..##.#.#.#",
            ".....#.#..",
            "##.#....#.",
            "#.....#..."
        ]
        # Начальная позиция игрока в ловушечной комнате (формат: (столбец, строка))
        self.trap_player_pos = (0, 2)
        # Фиксированная клетка выхода – (9,2)

        self.player_hp = 100    # Здоровье игрока
        self.player_mana = 100  # Мана игрока

        # Флаг, показывающий, использован ли сундук для восстановления (на клетке (9,0))
        self.trap_chest_used = False

        # Переменные для анимации заклинания игрока (магии)
        self.animating_spell = False  # Флаг: активна ли анимация шара от игрока
        self.spell_progress = 0.0     # Прогресс анимации (от 0 до 1)
        self.spell_start_pos = (0, 0)   # Начальная позиция (центр игрока)
        self.spell_end_pos = (0, 0)     # Конечная позиция (центр врага)
        self.spell_hit_effect = False # Флаг: активен ли эффект попадания (большой шар)
        self.spell_hit_timer = 0      # Таймер эффекта попадания
        self.pending_spell = None     # Сохраняет выбранное заклинание для нанесения урона врагу

        # Переменные для анимации контратакующего заклинания врага
        self.enemy_animating_spell = False  # Флаг: активна ли анимация шара врага
        self.enemy_spell_progress = 0.0       # Прогресс анимации вражеского шара
        self.enemy_spell_start_pos = (0, 0)     # Начальная позиция вражеского шара (центр врага)
        self.enemy_spell_end_pos = (0, 0)       # Конечная позиция вражеского шара (центр игрока)
        self.enemy_spell_hit_effect = False   # Флаг: активен ли эффект попадания в игрока (большой шар)
        self.enemy_spell_hit_timer = 0        # Таймер эффекта попадания врага

        # Переменные для анимации ловушки
        self.trap_animating = False    # Флаг: активна ли анимация ловушки
        self.trap_anim_progress = 0.0    # Прогресс анимации ловушки (от 0 до 1)
        self.trap_anim_cell = None       # Координаты клетки (столбец, строка), где сработала ловушка

    def get_trap_grid_origin(self):
        """
        Вычисляет и возвращает координаты начала сетки ловушечной комнаты.
        Сетка располагается внутри прямоугольника (50, 50, 700, 400).
        """
        grid_width = 10 * TRAP_CELL_WIDTH
        grid_height = 5 * TRAP_CELL_HEIGHT
        grid_origin_x = 50 + (700 - grid_width) // 2
        grid_origin_y = 50 + (400 - grid_height) // 2
        return grid_origin_x, grid_origin_y

    def draw(self):
        # Отрисовываем фон
        screen.blit(global_bg, (0, 0))
        # Если текущая комната не ловушечная, рисуем рамку вокруг игровой области
        if self.rooms[self.current_room] != "trap":
            pygame.draw.rect(screen, BLACK, (50, 50, 700, 400), 5)

        # Отрисовка комнаты в зависимости от её типа
        room_type = self.rooms[self.current_room]
        if room_type == "enemy":
            self.draw_enemy_room()
        elif room_type == "trap":
            self.draw_trap_room()
        elif room_type == "victory":
            self.draw_victory_room()

        # Отрисовываем индикаторы здоровья и маны
        self.draw_status_bars()

        # Обновляем анимации заклинаний (игрока и врага)
        self.update_spell_animation()
        # Обновляем анимацию ловушки (если активна)
        self.update_trap_animation()

        # Обновляем экран
        pygame.display.flip()

    def draw_status_bars(self):
        # Определяем отступы и размеры полос
        margin_x = 20
        margin_y = 20
        bar_width = 120
        bar_height = 20

        # Прямоугольники для полос HP и маны
        hp_bar_rect = pygame.Rect(WIDTH - (bar_width + margin_x),
                                  HEIGHT - (2 * bar_height + margin_y + 10),
                                  bar_width, bar_height)
        mana_bar_rect = pygame.Rect(WIDTH - (bar_width + margin_x),
                                    HEIGHT - (bar_height + margin_y),
                                    bar_width, bar_height)

        # задний фон полос статов хп и маны
        pygame.draw.rect(screen, GRAY, hp_bar_rect)
        pygame.draw.rect(screen, GRAY, mana_bar_rect)
        # полосы пропорционально текущим значениям
        pygame.draw.rect(screen, RED,
                         (hp_bar_rect.x, hp_bar_rect.y,
                          bar_width * (self.player_hp / 100), bar_height))
        pygame.draw.rect(screen, BLUE,
                         (mana_bar_rect.x, mana_bar_rect.y,
                          bar_width * (self.player_mana / 100), bar_height))

        # текстовые метки слева от статов хп и маны
        hp_text = self.font.render('HP', True, BLACK)
        mana_text = self.font.render('Mana', True, BLACK)
        screen.blit(hp_text, (hp_bar_rect.x - 40, hp_bar_rect.y))
        screen.blit(mana_text, (mana_bar_rect.x - 50, mana_bar_rect.y))

    def draw_enemy_room(self):
        # Отрисовываем фон боевой комнаты
        screen.blit(background_img, (50, 50))
        # Выбираем врага: для комнаты 0 – первый враг, для комнаты 2 – второй враг
        enemy = self.enemy_rooms[0] if self.current_room == 0 else self.enemy_rooms[1]

        if enemy and enemy.alive:
            # Выводим имя врага и его HP
            enemy_text = self.font.render(f'{enemy.name} - HP: {enemy.hp}', True, WHITE)
            screen.blit(enemy_text, (50, 20))
            # Для комнаты 2 используем новую текстуру врага
            if self.current_room == 2:
                screen.blit(enemy2_img, (600, 300))
            else:
                screen.blit(enemy_img, (600, 300))
        elif enemy and not enemy.alive:
            # Если враг побеждён, рисуем стрелку для перехода в следующую комнату
            arrow_color = WHITE
            arrow_points = [(700, 245), (700, 295), (730, 270)]
            pygame.draw.polygon(screen, arrow_color, arrow_points)

        # Отрисовываем игрока
        screen.blit(player_img, (100, 300))
        # Отрисовываем кнопки-заклинания в нижней части экрана
        for i, spell in enumerate(self.spells):
            color = RED if spell == 'огонь' else BLUE if spell == 'молния' else YELLOW
            pygame.draw.rect(screen, color, (50 + i * 150, HEIGHT - 100, 120, 50))
            spell_text = self.font.render(spell.capitalize(), True, BLACK)
            screen.blit(spell_text, (70 + i * 150, HEIGHT - 85))

    def draw_trap_room(self):
        # Вычисляем размеры и положение сетки 10 горизонтальных x 5 вертикальных
        grid_origin_x, grid_origin_y = self.get_trap_grid_origin()

        for r in range(5):
            for h in range(10):
                cell_x = grid_origin_x + h * TRAP_CELL_WIDTH
                cell_y = grid_origin_y + r * TRAP_CELL_HEIGHT

                # объекты для взаимодействия (рисуем)
                # 1. Клетка выхода (9,2)
                if (h, r) == (9, 2):
                    screen.blit(floor_img, (cell_x, cell_y))
                # 2. Клетка с сундуком для восстановления (9,0)
                elif (h, r) == (9, 0):
                    if not self.trap_chest_used:
                        screen.blit(trap_chest_img, (cell_x, cell_y))
                    else:
                        screen.blit(floor_img, (cell_x, cell_y))
                # 3. Если по карте стоит символ '#' – ловушка
                elif self.trap_map[r][h] == '#':
                    screen.blit(trap_img, (cell_x, cell_y))
                # 4. Иначе – пол
                else:
                    screen.blit(floor_img, (cell_x, cell_y))

        # Отрисовываем игрока поверх клетки, на которой он находится
        pr, ph = self.trap_player_pos  # pr – столбец, ph – строка
        player_cell_x = grid_origin_x + pr * TRAP_CELL_WIDTH
        player_cell_y = grid_origin_y + ph * TRAP_CELL_HEIGHT
        trap_player_img = pygame.transform.scale(player_img, (TRAP_CELL_WIDTH, TRAP_CELL_HEIGHT))
        trap_player_img.set_alpha(255)
        screen.blit(trap_player_img, (player_cell_x, player_cell_y))

        # Если активна анимация ловушки, рисуем красный круг в центре клетки
        if self.trap_animating and self.trap_anim_cell is not None:
            cell_col, cell_row = self.trap_anim_cell
            center_x = grid_origin_x + int((cell_col + 0.5) * TRAP_CELL_WIDTH)
            center_y = grid_origin_y + int((cell_row + 0.5) * TRAP_CELL_HEIGHT)
            # Радиус красного круга растёт типо анимации (макс. 30 пикселей)
            radius = int(self.trap_anim_progress * 30)
            pygame.draw.circle(screen, RED, (center_x, center_y), radius)

    def draw_victory_room(self):
        # другой фон победной комнаты (библиотека)
        screen.blit(library_img, (50, 50))
        victory_text = self.font.render("Вы победили!", True, WHITE)
        screen.blit(victory_text, (50, 20))
        # сундук в победной комнате
        chest_x = 50 + (700 - chest_img.get_width()) // 2
        chest_y = 50 + 400 - chest_img.get_height() - 20
        screen.blit(chest_img, (chest_x, chest_y))

    def cast_spell(self, spell):
        # Трата маны на заклинание
        self.player_mana -= 20

        # Запускаем анимацию заклинания игрока, если не идет другая анимация
        if self.rooms[self.current_room] == "enemy" and not self.animating_spell and not self.spell_hit_effect:
            self.animating_spell = True
            self.spell_progress = 0.0
            # центр игрока
            self.spell_start_pos = (150, 350)
            # центр врага
            self.spell_end_pos = (650, 350)
            # Сохраняем выбранное заклинание для нанесения урона врагу
            self.pending_spell = spell

    def update_spell_animation(self):
        # Анимация магического шара игрока
        if self.animating_spell:
            self.spell_progress += 0.02
            cur_x = self.spell_start_pos[0] + self.spell_progress * (self.spell_end_pos[0] - self.spell_start_pos[0])
            cur_y = self.spell_start_pos[1] + self.spell_progress * (self.spell_end_pos[1] - self.spell_start_pos[1])
            pygame.draw.circle(screen, WHITE, (int(cur_x), int(cur_y)), 10)
            if self.spell_progress >= 1.0:
                self.animating_spell = False
                self.spell_hit_effect = True
                self.spell_hit_timer = 30  # эффект попадания 30 кадров
                # Когда шар достигает врага, наносим ему урон
                enemy = self.enemy_rooms[0] if self.current_room == 0 else self.enemy_rooms[1]
                if enemy.alive and self.pending_spell is not None:
                    result = enemy.take_damage(self.pending_spell)
                    print(result)
                    if enemy.hp <= 0:
                        enemy.alive = False
                    else:
                        # Если враг остался жив, воспроизводится анимация его контратаки
                        self.enemy_animating_spell = True
                        self.enemy_spell_progress = 0.0
                        self.enemy_spell_start_pos = (650, 350)  # Центр врага
                        self.enemy_spell_end_pos = (150, 350)    # Центр игрока
                self.pending_spell = None

        # Эффект попадания (большой белый шар в центре врага)
        if self.spell_hit_effect:
            pygame.draw.circle(screen, WHITE, (650, 350), 30)
            self.spell_hit_timer -= 1
            if self.spell_hit_timer <= 0:
                self.spell_hit_effect = False

        # Анимация вражеского шара (контратака)
        if self.enemy_animating_spell:
            self.enemy_spell_progress += 0.02
            enemy_cur_x = self.enemy_spell_start_pos[0] + self.enemy_spell_progress * (self.enemy_spell_end_pos[0] - self.enemy_spell_start_pos[0])
            enemy_cur_y = self.enemy_spell_start_pos[1] + self.enemy_spell_progress * (self.enemy_spell_end_pos[1] - self.enemy_spell_start_pos[1])
            pygame.draw.circle(screen, WHITE, (int(enemy_cur_x), int(enemy_cur_y)), 10)
            if self.enemy_spell_progress >= 1.0:
                self.enemy_animating_spell = False
                self.enemy_spell_hit_effect = True
                self.enemy_spell_hit_timer = 30
                # Наносим урон игроку после попадания в него
                self.player_hp -= 20
                if self.player_hp <= 0:
                    pygame.quit(), sys.exit()
        if self.enemy_spell_hit_effect:
            pygame.draw.circle(screen, WHITE, (150, 350), 30)
            self.enemy_spell_hit_timer -= 1
            if self.enemy_spell_hit_timer <= 0:
                self.enemy_spell_hit_effect = False

    def update_trap_animation(self):
        # Если анимация ловушки активна, обновляем прогресс
        if self.trap_animating:
            self.trap_anim_progress += 0.05  # скорость анимации (можно регулировать)
            if self.trap_anim_progress >= 1.0:
                self.trap_animating = False
                # После завершения анимации игрок получает урон
                self.player_hp -= 30
                if self.player_hp <= 0:
                    pygame.quit()
                    sys.exit()

    def next_room(self):
        # Переходим к следующей комнате
        self.current_room += 1
        if self.current_room >= len(self.rooms):
            pygame.quit()
            sys.exit()
        # Если следующая комната – с ловушками, задаём начальную позицию игрока
        if self.rooms[self.current_room] == "trap":
            self.trap_player_pos = (0, 2)

    def handle_victory_room_click(self, x, y):
        # Определяем область сундука в победной комнате
        chest_x = 50 + (700 - chest_img.get_width()) // 2
        chest_y = 50 + 400 - chest_img.get_height() - 20
        chest_rect = pygame.Rect(chest_x, chest_y, chest_img.get_width(), chest_img.get_height())
        if chest_rect.collidepoint(x, y):
            pygame.quit()
            sys.exit()

    def handle_trap_room_click(self, x, y):
        # Вычисляем размеры и положение сетки комнаты с ловушками
        grid_origin_x, grid_origin_y = self.get_trap_grid_origin()

        # Если игрок уже находится в клетке выхода (9,2) и кликает внутри неё тогда происходит переход в следующую комнату
        if self.trap_player_pos == (9, 2):
            exit_rect = pygame.Rect(grid_origin_x + 9 * TRAP_CELL_WIDTH,
                                    grid_origin_y + 2 * TRAP_CELL_HEIGHT,
                                    TRAP_CELL_WIDTH, TRAP_CELL_HEIGHT)
            if exit_rect.collidepoint(x, y):
                self.next_room()
                return

        # Определяем, по какой клетке произошёл клик
        clicked_c = (x - grid_origin_x) // TRAP_CELL_WIDTH
        clicked_r = (y - grid_origin_y) // TRAP_CELL_HEIGHT

        if clicked_c < 0 or clicked_c >= 10 or clicked_r < 0 or clicked_r >= 5:
            return

        current_c, current_r = self.trap_player_pos
        # перемещение только на соседнюю клетку
        if abs(clicked_c - current_c) + abs(clicked_r - current_r) == 1:
            self.trap_player_pos = (clicked_c, clicked_r)
            # Если новая клетка по карте содержит ловушку ('#')
            if self.trap_map[clicked_r][clicked_c] == '#':
                # Запускаем анимацию ловушки, если она ещё не активна
                if not self.trap_animating:
                    self.trap_animating = True
                    self.trap_anim_progress = 0.0
                    self.trap_anim_cell = (clicked_c, clicked_r)
            # Если игрок попадает на клетку с сундуком для восстановления (9,0) и сундук ещё не использован
            if self.trap_player_pos == (9, 0) and not self.trap_chest_used:
                self.player_hp = min(100, self.player_hp + 50)
                self.player_mana = min(100, self.player_mana + 50)
                self.trap_chest_used = True
                # игрок востановит 50 хп и маны
    def handle_click(self, x, y):
        # Определяем тип текущей комнаты и передаём клик в соответствующую обработку
        room_type = self.rooms[self.current_room]
        if room_type == "enemy":
            enemy = self.enemy_rooms[0] if self.current_room == 0 else self.enemy_rooms[1]
            if enemy and not enemy.alive:
                arrow_rect = pygame.Rect(700, 245, 30, 50)
                if arrow_rect.collidepoint(x, y):
                    self.next_room()
            elif HEIGHT - 100 <= y <= HEIGHT - 50:
                for i, spell in enumerate(self.spells):
                    if 50 + i * 150 <= x <= 170 + i * 150:
                        self.cast_spell(spell)
        elif room_type == "trap":
            self.handle_trap_room_click(x, y)
        elif room_type == "victory":
            self.handle_victory_room_click(x, y)

# Основной цикл игры
game = Game()  # Создаём объект игры
running = True  # Флаг продолжения основного цикла

while running:
    game.draw()  # Отрисовываем текущую сцену
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Если окно закрыто, завершаем цикл
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:  # Если произошёл клик мышью
            x, y = event.pos
            game.handle_click(x, y)
    pygame.time.delay(30)  # Задержка для контроля частоты обновления экрана

pygame.quit()  # Завершаем работу pygame
