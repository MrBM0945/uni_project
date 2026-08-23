import pygame
from src.config import settings

from src.config.settings import CELL, BLACK


class Renderer:
    def __init__(self, screen):
        self.screen = screen

        # --- Кешовані шрифти (створюються один раз) ---
        self.title_font = pygame.font.SysFont("arialblack", 60)
        self.stats_font = pygame.font.SysFont("comicsans", 25)
        self.medium_font = pygame.font.SysFont("arialblack", 50)
        self.font = pygame.font.SysFont("comicsans", 30)

        # --- Кешований фон сітки (рендериться один раз) ---
        self._grid_surface = self._build_grid_surface(
            settings.COLS, settings.ROWS, settings.GRID_LINE
        )
        # --- Кешовані Surface для overlay ---
        self._overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self._overlay.set_alpha(180)
        self._overlay.fill((0, 0, 0))


    def _build_grid_surface(self, cols: int, rows: int, grid_line) -> pygame.Surface:
        """Будує Surface з намальованою сіткою (фон + лінії).
        Викликається один раз при ініціалізації — дуже дешево під час гри."""
        width = cols * CELL
        height = rows * CELL
        surf = pygame.Surface((width, height))

        # Градієнтний фон: зверху світліше
        for i in range(rows):
            shade = int(235 - i * 2)
            color = (shade, shade + 10, shade + 20)
            pygame.draw.rect(surf, color, (0, i * CELL, width, CELL))

        # Шахова текстура поверх градієнту
        for x in range(cols):
            for y in range(rows):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(surf, (228, 238, 248), (x * CELL, y * CELL, CELL, CELL))

        # Вертикальні лінії
        for x in range(cols + 1):
            pygame.draw.line(surf, grid_line, (x * CELL, 0), (x * CELL, height), 2)

        # Горизонтальні лінії
        for y in range(rows + 1):
            pygame.draw.line(surf, grid_line, (0, y * CELL), (width, y * CELL), 2)

        # Зовнішня рамка
        pygame.draw.rect(surf, (120, 150, 180), (0, 0, width, height), 3)

        return surf

    def adjust_color(self, color, amount):
        return tuple(max(0, min(255, c + amount)) for c in color)

    # ------------------------------------------------------------------
    # Публічні методи малювання
    # ------------------------------------------------------------------

    def draw_title(self):
        title = "TETRIS"
        panel_x = settings.GRID_X + settings.COLS * settings.CELL + 20
        x = panel_x + 60
        y = 40

        shadow = self.title_font.render(title, True, (0, 0, 0))
        self.screen.blit(shadow, (x + 4, y + 4))

        text = self.title_font.render(title, True, (0, 220, 255))
        self.screen.blit(text, (x, y))

    def draw_game_stats(self, start_time_str: str, duration_str: str):
        """Відображає час початку та тривалість гри (шрифт кешований)."""
        base_x = settings.GRID_X + settings.COLS * settings.CELL + 30
        base_y = settings.GRID_Y + 160

        start_label = self.stats_font.render(f"Started: {start_time_str}", True, settings.WHITE)
        self.screen.blit(start_label, (base_x, base_y))

        duration_label = self.stats_font.render(f"Duration: {duration_str}", True, (0, 255, 100))
        self.screen.blit(duration_label, (base_x, base_y + 30))

    def draw_grid(self, grid_x: int, grid_y: int):
        """Малює кешований фон сітки одним blit."""
        self.screen.blit(self._grid_surface, (grid_x, grid_y))

    def draw_shape(self, shape, color, x: int, y: int):
        light = self.adjust_color(color, 40)
        dark = self.adjust_color(color, -40)

        for block in shape:
            bx = x + block[0] * CELL
            by = y + block[1] * CELL
            rect = pygame.Rect(bx, by, CELL, CELL)

            pygame.draw.rect(self.screen, color, rect)

            # Верхній відблиск
            pygame.draw.polygon(self.screen, light, [
                (bx, by), (bx + CELL, by),
                (bx + CELL - 4, by + 4), (bx + 4, by + 4)
            ])
            # Лівий відблиск
            pygame.draw.polygon(self.screen, light, [
                (bx, by), (bx, by + CELL),
                (bx + 4, by + CELL - 4), (bx + 4, by + 4)
            ])
            # Нижня тінь
            pygame.draw.polygon(self.screen, dark, [
                (bx, by + CELL), (bx + CELL, by + CELL),
                (bx + CELL - 4, by + CELL - 4), (bx + 4, by + CELL - 4)
            ])
            # Права тінь
            pygame.draw.polygon(self.screen, dark, [
                (bx + CELL, by), (bx + CELL, by + CELL),
                (bx + CELL - 4, by + CELL - 4), (bx + CELL - 4, by + 4)
            ])

            # Рамка
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_ghost_shape(self, shape, color, x: int, y: int):
        for block in shape:
            bx = x + block[0] * CELL
            by = y + block[1] * CELL
            rect = pygame.Rect(bx, by, CELL, CELL)

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (220, 220, 220), rect, 1)

    def draw_ghost(self, shape_coords, base_color):
        """Розраховує колір і малює тінь."""
        if not shape_coords:
            return
        
        r, g, b = base_color
        ghost_color = ((r + 255 * 3) // 4, (g + 255 * 3) // 4, (b + 255 * 3) // 4)
        
        for block in shape_coords:
            bx = settings.GRID_X + block[0] * CELL
            by = settings.GRID_Y + block[1] * CELL
            rect = pygame.Rect(bx, by, CELL, CELL)
            pygame.draw.rect(self.screen, ghost_color, rect)
            pygame.draw.rect(self.screen, (220, 220, 220), rect, 1)

    def draw_ui_panel(self, score, high_score, start_time, elapsed_seconds, held_type, next_shapes):
        """Малює всю праву частину екрана."""
        x = settings.GRID_X + settings.COLS * settings.CELL + 30
        
        # Score & High Score
        self.screen.blit(self.font.render(f"Score: {score}", True, settings.WHITE), (x, settings.GRID_Y + 50))
        self.screen.blit(self.font.render(f"High Score: {high_score}", True, (255, 215, 0)), (x, settings.GRID_Y + 100))
        
        # Date & Time
        date_str = start_time.strftime("%d.%m.%Y")
        self.screen.blit(self.font.render(f"Date: {date_str}", True, settings.WHITE), (x, settings.GRID_Y + 130))
        
        start_time_str = start_time.strftime("%H:%M:%S")
        duration_str = f"{elapsed_seconds // 60:02}:{elapsed_seconds % 60:02}"
        self.draw_game_stats(start_time_str, duration_str)

        # Hold
        if held_type:
            from src.entities.tetrominoes import TetrominoRegistry
            held_def = TetrominoRegistry.get_definition(held_type)
            self.screen.blit(self.font.render("Hold:", True, settings.WHITE), (x, settings.GRID_Y + 210))
            self.draw_shape(held_def.get_state(0), held_def.color, x + 40, settings.GRID_Y + 240)

        # Next
        if next_shapes:
            from src.entities.tetrominoes import TetrominoRegistry
            next_def = TetrominoRegistry.get_definition(next_shapes[0])
            self.screen.blit(self.font.render("Next:", True, settings.WHITE), (x, settings.GRID_Y + 350))
            self.draw_shape(next_def.get_state(0), next_def.color, x + 40, settings.GRID_Y + 400)

    def draw_pause(self):
        self.screen.blit(self._overlay, (0, 0))
        
        # Заголовок та підказки
        label = self.title_font.render("PAUSED", True, settings.WHITE)
        continue_label = self.font.render("Press P to continue", True, settings.WHITE)
        menu_label = self.font.render("Press ESC to Menu", True, (200, 200, 200))
        
        cx = settings.WIDTH // 2
        cy = settings.HEIGHT // 2
        
        self.screen.blit(label, (cx - label.get_width() // 2, cy - 80))
        self.screen.blit(continue_label, (cx - continue_label.get_width() // 2, cy + 20))
        self.screen.blit(menu_label, (cx - menu_label.get_width() // 2, cy + 60))

    # pyrefly: ignore [parse-error]
    def draw_game_over(self, score):
        self.screen.blit(self._overlay, (0, 0))
        
        # Заголовок, очки та підказки
        go_label = self.medium_font.render("GAME OVER", True, settings.WHITE)
        sc_label = self.font.render(f"Final Score: {score}", True, settings.WHITE)
        restart_label = self.font.render("Press ENTER to Restart", True, (0, 255, 100))
        menu_label = self.font.render("Press ESC to Menu", True, settings.WHITE)
        
        cx = settings.WIDTH // 2
        cy = settings.HEIGHT // 2
        
        self.screen.blit(go_label, (cx - go_label.get_width() // 2, cy - 120))
        self.screen.blit(sc_label, (cx - sc_label.get_width() // 2, cy - 40))
        self.screen.blit(restart_label, (cx - restart_label.get_width() // 2, cy + 30))
        self.screen.blit(menu_label, (cx - menu_label.get_width() // 2, cy + 70))
   
    # pyrefly: ignore [parse-error]
    def draw_main_menu(self):
        # Використовуємо наш темний напівпрозорий оверлей як фон
        self.screen.fill((40, 40, 50)) 
        
        # Заголовок
        title = self.title_font.render("TETRIS", True, (0, 220, 255))
        title_shadow = self.title_font.render("TETRIS", True, (0, 0, 0))
        
        # Підказки
        start_label = self.font.render("Press ENTER to Start", True, settings.WHITE)
        exit_label = self.font.render("Press ESC to Exit", True, (200, 200, 200))
        
        # Центруємо
        cx = settings.WIDTH // 2
        cy = settings.HEIGHT // 2
        
        self.screen.blit(title_shadow, (cx - title.get_width() // 2 + 4, cy - 100 + 4))
        self.screen.blit(title, (cx - title.get_width() // 2, cy - 100))
        self.screen.blit(start_label, (cx - start_label.get_width() // 2, cy + 20))
        self.screen.blit(exit_label, (cx - exit_label.get_width() // 2, cy + 80))