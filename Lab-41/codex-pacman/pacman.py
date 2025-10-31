from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pygame

TILE_SIZE = 24
HALF_TILE = TILE_SIZE // 2
FPS = 60
FRIGHTENED_TIME = 6000
PLAYER_SPEED = 4
GHOST_SPEED = 3
FRIGHTENED_SPEED = 2

BASE_PATH = Path(__file__).resolve().parent
HIGH_SCORE_FILE = BASE_PATH / "highscore.txt"

COLOR_BACKGROUND = (10, 10, 30)
COLOR_GRID_LINES = (20, 20, 60)
COLOR_WALL_BASE = (30, 30, 140)
COLOR_WALL_TRIM = (70, 90, 220)
COLOR_PELLET = (252, 218, 183)
COLOR_POWER_PELLET = (255, 255, 255)
COLOR_PLAYER = (255, 215, 0)
COLOR_PLAYER_HIGHLIGHT = (255, 240, 120)
COLOR_GHOST_FRIGHTENED = (33, 33, 255)
COLOR_GHOST_EYE_WHITE = (240, 240, 255)
COLOR_GHOST_EYE_PUPIL = (30, 30, 30)

DIRECTION_VECTORS = {
    pygame.K_LEFT: pygame.Vector2(-1, 0),
    pygame.K_RIGHT: pygame.Vector2(1, 0),
    pygame.K_UP: pygame.Vector2(0, -1),
    pygame.K_DOWN: pygame.Vector2(0, 1),
}

CARDINAL_DIRECTIONS = [
    pygame.Vector2(1, 0),
    pygame.Vector2(-1, 0),
    pygame.Vector2(0, 1),
    pygame.Vector2(0, -1),
]

LEVEL_MAP = [
    "###################",
    "#........#........#",
    "#.####.#.#.####.#.#",
    "#o####.#.#.####.#o#",
    "#.................#",
    "#.####.#.####.#.###",
    "#.....#...#...#...#",
    "#####.#.#G#.#.#.###",
    "#........#........#",
    "#.####.#####.####.#",
    "#o..#...P...#..G.o#",
    "#.####.#.####.#.###",
    "#........#........#",
    "#.####.#.#.####.#.#",
    "#o####.#.#.####.#o#",
    "#.................#",
    "###################",
]

ROWS = len(LEVEL_MAP)
COLS = len(LEVEL_MAP[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE


def tile_from_pixel(pixel_pos: pygame.Vector2) -> tuple[int, int]:
    return int(pixel_pos.x // TILE_SIZE), int(pixel_pos.y // TILE_SIZE)


def pixel_from_tile(tile: tuple[int, int]) -> pygame.Vector2:
    return pygame.Vector2(tile[0] * TILE_SIZE + HALF_TILE, tile[1] * TILE_SIZE + HALF_TILE)


def is_centered(pixel_pos: pygame.Vector2) -> bool:
    return (
        abs(((pixel_pos.x - HALF_TILE) % TILE_SIZE)) < 1
        and abs(((pixel_pos.y - HALF_TILE) % TILE_SIZE)) < 1
    )


def opposite(direction: pygame.Vector2) -> pygame.Vector2:
    return pygame.Vector2(-direction.x, -direction.y)


class Player:
    def __init__(self, start_tile: tuple[int, int]):
        self.start_tile = start_tile
        self.pixel_pos = pixel_from_tile(start_tile)
        self.grid_pos = start_tile
        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)
        self.speed = PLAYER_SPEED

    def reset(self):
        self.pixel_pos = pixel_from_tile(self.start_tile)
        self.grid_pos = self.start_tile
        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)

    def set_next_direction(self, direction: pygame.Vector2):
        if direction.length_squared() == 0:
            return
        self.next_direction = direction

    def can_move(self, direction: pygame.Vector2, walls: set[tuple[int, int]]) -> bool:
        if direction.length_squared() == 0:
            return False
        target = (self.grid_pos[0] + int(direction.x), self.grid_pos[1] + int(direction.y))
        return target not in walls

    def update(self, walls: set[tuple[int, int]]):
        if is_centered(self.pixel_pos):
            self.grid_pos = tile_from_pixel(self.pixel_pos)
            if self.next_direction.length_squared() and self.can_move(self.next_direction, walls):
                self.direction = self.next_direction
            if not self.can_move(self.direction, walls):
                self.direction = pygame.Vector2(0, 0)
        self.pixel_pos += self.direction * self.speed
        self.grid_pos = tile_from_pixel(self.pixel_pos)
        if is_centered(self.pixel_pos):
            self.pixel_pos = pixel_from_tile(self.grid_pos)

    def draw(self, surface: pygame.Surface):
        center = pygame.Vector2(self.pixel_pos)
        radius = HALF_TILE - 2
        pygame.draw.circle(surface, COLOR_PLAYER_HIGHLIGHT, (int(center.x), int(center.y)), radius + 1)
        pygame.draw.circle(surface, COLOR_PLAYER, (int(center.x), int(center.y)), radius)

        direction = self.direction
        if direction.length_squared() == 0:
            direction = self.next_direction
        has_direction = direction.length_squared() != 0
        if has_direction:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(1, 0)

        mouth_cycle = (pygame.time.get_ticks() // 120) % 4
        mouth_angles = [5, 22, 5, 0]
        opening_angle = mouth_angles[mouth_cycle] if has_direction else 0
        if opening_angle:
            v1 = direction.rotate(opening_angle) * radius
            v2 = direction.rotate(-opening_angle) * radius

            def to_tuple(vec: pygame.Vector2) -> tuple[int, int]:
                return int(center.x + vec.x), int(center.y + vec.y)

            pygame.draw.polygon(
                surface,
                COLOR_BACKGROUND,
                [
                    (int(center.x), int(center.y)),
                    to_tuple(v1),
                    to_tuple(v2),
                ],
            )

        highlight_center = center + pygame.Vector2(-radius * 0.25, -radius * 0.35)
        pygame.draw.circle(
            surface,
            COLOR_PLAYER_HIGHLIGHT,
            (int(highlight_center.x), int(highlight_center.y)),
            max(1, radius // 4),
        )


class Ghost:
    def __init__(self, spawn_tile: tuple[int, int], color: tuple[int, int, int]):
        self.spawn_tile = spawn_tile
        self.color = color
        self.pixel_pos = pixel_from_tile(spawn_tile)
        self.grid_pos = spawn_tile
        self.direction = pygame.Vector2(0, 0)
        self.speed = GHOST_SPEED
        self.mode = "chase"
        self.frightened_until = 0

    def reset(self):
        self.pixel_pos = pixel_from_tile(self.spawn_tile)
        self.grid_pos = self.spawn_tile
        self.direction = pygame.Vector2(0, 0)
        self.mode = "chase"
        self.frightened_until = 0

    def set_frightened(self, now_ms: int):
        self.mode = "frightened"
        self.frightened_until = now_ms + FRIGHTENED_TIME
        self.direction = opposite(self.direction)

    def update(self, now_ms: int, walls: set[tuple[int, int]], target_tile: tuple[int, int]):
        if self.mode == "frightened" and now_ms >= self.frightened_until:
            self.mode = "chase"

        if is_centered(self.pixel_pos):
            self.grid_pos = tile_from_pixel(self.pixel_pos)
            options = self._valid_directions(walls)
            if not options:
                self.direction = opposite(self.direction)
            elif self.mode == "frightened":
                self.direction = random.choice(options)
            else:
                self.direction = self._choose_chase_direction(options, target_tile)
            speed = FRIGHTENED_SPEED if self.mode == "frightened" else GHOST_SPEED
            self.speed = speed
        self.pixel_pos += self.direction * self.speed
        self.grid_pos = tile_from_pixel(self.pixel_pos)
        if is_centered(self.pixel_pos):
            self.pixel_pos = pixel_from_tile(self.grid_pos)

    def _valid_directions(self, walls: set[tuple[int, int]]):
        options = []
        for direction in CARDINAL_DIRECTIONS:
            if direction == opposite(self.direction):
                continue
            target = (self.grid_pos[0] + int(direction.x), self.grid_pos[1] + int(direction.y))
            if target in walls:
                continue
            options.append(direction)
        return options

    def _choose_chase_direction(self, options: list[pygame.Vector2], target_tile: tuple[int, int]):
        best_dir = self.direction
        best_dist = math.inf
        for direction in options:
            candidate = (self.grid_pos[0] + int(direction.x), self.grid_pos[1] + int(direction.y))
            dist = abs(candidate[0] - target_tile[0]) + abs(candidate[1] - target_tile[1])
            if dist < best_dist:
                best_dist = dist
                best_dir = direction
        return best_dir

    def respawn(self):
        self.reset()

    def draw(self, surface: pygame.Surface):
        color = COLOR_GHOST_FRIGHTENED if self.mode == "frightened" else self.color
        center = pygame.Vector2(self.pixel_pos)
        radius = HALF_TILE - 2

        head_center = center + pygame.Vector2(0, -radius * 0.25)
        pygame.draw.circle(surface, color, (int(head_center.x), int(head_center.y)), radius)

        body_height = int(radius * 1.6)
        body_rect = pygame.Rect(0, 0, int(radius * 2), body_height)
        body_rect.center = (int(center.x), int(center.y + radius * 0.4))
        pygame.draw.rect(surface, color, body_rect)

        foot_radius = max(2, radius // 3)
        foot_spacing = body_rect.width / 4
        foot_y = body_rect.bottom
        for index in range(4):
            foot_center_x = body_rect.left + foot_spacing * (index + 0.5)
            pygame.draw.circle(surface, color, (int(foot_center_x), int(foot_y)), foot_radius)

        eye_direction = self.direction
        if eye_direction.length_squared() == 0:
            eye_direction = pygame.Vector2(1, 0)
        else:
            eye_direction = eye_direction.normalize()
        perpendicular = pygame.Vector2(-eye_direction.y, eye_direction.x)
        eye_forward = eye_direction * radius * 0.35
        eye_vertical = pygame.Vector2(0, -radius * 0.25)
        eye_side = perpendicular * radius * 0.35
        eye_radius = max(3, radius // 2 - 1)
        pupil_offset = eye_direction * radius * 0.2
        pupil_radius = max(2, eye_radius // 2)
        left_eye_center = head_center + eye_vertical - eye_side + eye_forward
        right_eye_center = head_center + eye_vertical + eye_side + eye_forward
        for eye_center in (left_eye_center, right_eye_center):
            pygame.draw.circle(surface, COLOR_GHOST_EYE_WHITE, (int(eye_center.x), int(eye_center.y)), eye_radius)
            pygame.draw.circle(
                surface,
                COLOR_GHOST_EYE_PUPIL,
                (int(eye_center.x + pupil_offset.x), int(eye_center.y + pupil_offset.y)),
                pupil_radius,
            )


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pac-Man")
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.large_font = pygame.font.SysFont("arial", 32, bold=True)
        self.high_score = self._load_high_score()
        self.walls: set[tuple[int, int]] = set()
        self.pellets: set[tuple[int, int]] = set()
        self.power_pellets: set[tuple[int, int]] = set()
        self.ghosts: list[Ghost] = []
        self.player: Player | None = None
        self.lives = 3
        self.score = 0
        self.state = "playing"
        self._parse_level()

    def _parse_level(self):
        ghost_colors = [(255, 0, 0), (255, 128, 0), (0, 255, 255), (255, 105, 180)]
        color_index = 0
        player_start = (1, 1)
        for row_index, row in enumerate(LEVEL_MAP):
            if len(row) != COLS:
                raise ValueError("Level rows must be equal length")
            for col_index, cell in enumerate(row):
                tile = (col_index, row_index)
                if cell == "#":
                    self.walls.add(tile)
                elif cell == ".":
                    self.pellets.add(tile)
                elif cell == "o":
                    self.power_pellets.add(tile)
                elif cell == "P":
                    player_start = tile
                elif cell == "G":
                    color = ghost_colors[color_index % len(ghost_colors)]
                    color_index += 1
                    self.ghosts.append(Ghost(tile, color))
        self.player = Player(player_start)

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            now_ms = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._save_high_score()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key in DIRECTION_VECTORS and self.player:
                        self.player.set_next_direction(DIRECTION_VECTORS[event.key])
                    if event.key == pygame.K_ESCAPE:
                        self._save_high_score()
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r and self.state != "playing":
                        self.reset()
            if self.state == "playing":
                self.update(now_ms)
            self.draw()

    def reset(self):
        self.walls.clear()
        self.pellets.clear()
        self.power_pellets.clear()
        self.ghosts.clear()
        self.lives = 3
        self.score = 0
        self.state = "playing"
        self._parse_level()
        if self.player:
            self.player.reset()

    def update(self, now_ms: int):
        if not self.player:
            return
        self.player.update(self.walls)
        tile = self.player.grid_pos
        if tile in self.pellets:
            self.pellets.remove(tile)
            self._add_score(10)
        if tile in self.power_pellets:
            self.power_pellets.remove(tile)
            self._add_score(50)
            for ghost in self.ghosts:
                ghost.set_frightened(now_ms)
        for ghost in self.ghosts:
            ghost.update(now_ms, self.walls, self.player.grid_pos)
        self._check_collisions()
        if not self.pellets and not self.power_pellets:
            self.state = "won"

    def _check_collisions(self):
        if not self.player:
            return
        for ghost in self.ghosts:
            distance = self.player.pixel_pos.distance_to(ghost.pixel_pos)
            if distance <= TILE_SIZE * 0.6:
                if ghost.mode == "frightened":
                    ghost.respawn()
                    self._add_score(200)
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = "gameover"
                    self._reset_positions()
                    break

    def _reset_positions(self):
        if self.player:
            self.player.reset()
        for ghost in self.ghosts:
            ghost.reset()

    def draw(self):
        self.canvas.fill(COLOR_BACKGROUND)
        self._draw_grid()
        for wall in self.walls:
            rect = pygame.Rect(wall[0] * TILE_SIZE, wall[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.canvas, COLOR_WALL_BASE, rect)
            inset = rect.inflate(-TILE_SIZE // 3, -TILE_SIZE // 3)
            if inset.width > 0 and inset.height > 0:
                pygame.draw.rect(self.canvas, COLOR_WALL_TRIM, inset, border_radius=4)
        now_ms = pygame.time.get_ticks()
        pulse = 1 + int(1.5 * (1 + math.sin(now_ms / 200)))
        for pellet in self.pellets:
            pos = pixel_from_tile(pellet)
            pygame.draw.circle(self.canvas, COLOR_PELLET, pos, 3)
        for pellet in self.power_pellets:
            pos = pixel_from_tile(pellet)
            radius = 6 + pulse
            pygame.draw.circle(self.canvas, COLOR_POWER_PELLET, pos, radius, width=2)
            pygame.draw.circle(self.canvas, COLOR_PLAYER_HIGHLIGHT, pos, max(2, radius - 5))
        if self.player:
            self.player.draw(self.canvas)
        for ghost in self.ghosts:
            ghost.draw(self.canvas)
        self._draw_hud()
        scaled = pygame.transform.scale(self.canvas, self.window.get_size())
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()

    def _draw_hud(self):
        score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surface = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        high_surface = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
        self.canvas.blit(score_surface, (10, 5))
        self.canvas.blit(lives_surface, (WIDTH - lives_surface.get_width() - 10, 5))
        self.canvas.blit(high_surface, ((WIDTH - high_surface.get_width()) // 2, 5))
        if self.state == "gameover":
            self._draw_center_text("Game Over - Press R to Restart")
        elif self.state == "won":
            self._draw_center_text("You Win! Press R to Restart")

    def _draw_grid(self):
        for x in range(0, WIDTH + 1, TILE_SIZE):
            pygame.draw.line(self.canvas, COLOR_GRID_LINES, (x, 0), (x, HEIGHT))
        for y in range(TILE_SIZE, HEIGHT + 1, TILE_SIZE):
            pygame.draw.line(self.canvas, COLOR_GRID_LINES, (0, y), (WIDTH, y))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        if not words:
            return []
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def _draw_center_text(self, message: str):
        lines = self._wrap_text(message, self.large_font, WIDTH - 40)
        if not lines:
            return
        line_height = self.large_font.get_linesize()
        total_height = len(lines) * line_height
        start_y = (HEIGHT - total_height) // 2
        for index, line in enumerate(lines):
            text_surface = self.large_font.render(line, True, (255, 255, 255))
            center_y = start_y + index * line_height + line_height // 2
            rect = text_surface.get_rect(center=(WIDTH // 2, center_y))
            self.canvas.blit(text_surface, rect)

    def _load_high_score(self) -> int:
        try:
            return int(HIGH_SCORE_FILE.read_text().strip())
        except (OSError, ValueError):
            return 0

    def _save_high_score(self):
        try:
            HIGH_SCORE_FILE.write_text(str(self.high_score))
        except OSError:
            pass

    def _add_score(self, points: int):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
