import pygame
import sys
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
TILE_SIZE = 20
FPS = 60

# Colors
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 139)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BRIGHT_YELLOW = (255, 255, 100)
BLUE = (33, 33, 222)
LIGHT_BLUE = (100, 150, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)

# High score file
HIGH_SCORE_FILE = "highscore.json"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Maze layout (1 = wall, 0 = empty, 2 = pellet, 3 = power pellet)
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,3,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,0,0,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,2,2,1,1,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,1,1,2,2,3,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

class PacMan:
    def __init__(self):
        self.x = 14
        self.y = 23
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.speed = 0.15
        self.position_offset = 0
        self.mouth_angle = 0
        self.mouth_opening = True
        
    def update(self, maze):
        # Update mouth animation
        if self.mouth_opening:
            self.mouth_angle += 5
            if self.mouth_angle >= 45:
                self.mouth_opening = False
        else:
            self.mouth_angle -= 5
            if self.mouth_angle <= 0:
                self.mouth_opening = True
        
        # Try to change direction if possible (only when aligned with grid)
        if self.position_offset == 0:
            next_x = self.x + self.next_direction.value[0]
            next_y = self.y + self.next_direction.value[1]
            if 0 <= next_y < len(maze) and 0 <= next_x < len(maze[0]):
                if maze[next_y][next_x] != 1:
                    self.direction = self.next_direction
        
        # Check if we can move in current direction
        next_x = self.x + self.direction.value[0]
        next_y = self.y + self.direction.value[1]
        
        can_move = False
        if 0 <= next_y < len(maze) and 0 <= next_x < len(maze[0]):
            if maze[next_y][next_x] != 1:
                can_move = True
        
        # Only move if there's no wall ahead
        if can_move:
            self.position_offset += self.speed
            if self.position_offset >= 1:
                self.position_offset = 0
                self.x = next_x
                self.y = next_y
                
                # Wrap around tunnel
                if self.x < 0:
                    self.x = len(maze[0]) - 1
                elif self.x >= len(maze[0]):
                    self.x = 0
    
    def get_render_position(self):
        offset_x = self.direction.value[0] * self.position_offset * TILE_SIZE
        offset_y = self.direction.value[1] * self.position_offset * TILE_SIZE
        return (self.x * TILE_SIZE + offset_x, self.y * TILE_SIZE + offset_y)
    
    def draw(self, screen):
        import math
        x, y = self.get_render_position()
        center_x = int(x + TILE_SIZE // 2)
        center_y = int(y + TILE_SIZE // 2)
        radius = TILE_SIZE // 2 - 2
        
        # Add subtle gradient effect with two circles
        pygame.draw.circle(screen, BRIGHT_YELLOW, (center_x, center_y), radius)
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius - 1)
        
        # Draw mouth (cut out a wedge)
        if self.mouth_angle > 0:
            # Determine mouth direction angle
            if self.direction == Direction.RIGHT:
                mouth_direction = 0
            elif self.direction == Direction.LEFT:
                mouth_direction = 180
            elif self.direction == Direction.UP:
                mouth_direction = 270
            else:  # DOWN
                mouth_direction = 90
            
            # Calculate the two mouth edges
            upper_angle = mouth_direction - self.mouth_angle
            lower_angle = mouth_direction + self.mouth_angle
            
            # Create points for the mouth triangle
            points = [(center_x, center_y)]
            
            # Upper edge of mouth
            upper_rad = math.radians(upper_angle)
            point_x = int(center_x + radius * math.cos(upper_rad))
            point_y = int(center_y - radius * math.sin(upper_rad))
            points.append((point_x, point_y))
            
            # Lower edge of mouth
            lower_rad = math.radians(lower_angle)
            point_x = int(center_x + radius * math.cos(lower_rad))
            point_y = int(center_y - radius * math.sin(lower_rad))
            points.append((point_x, point_y))
            
            # Draw the black mouth triangle
            pygame.draw.polygon(screen, BLACK, points)
        
        # Add eye
        eye_x = center_x
        eye_y = center_y - 3
        if self.direction == Direction.RIGHT:
            eye_x = center_x + 3
        elif self.direction == Direction.LEFT:
            eye_x = center_x - 3
        elif self.direction == Direction.UP:
            eye_y = center_y - 5
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)

class Ghost:
    def __init__(self, x, y, color):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.color = color
        self.direction = Direction.LEFT
        self.speed = 0.1
        self.position_offset = 0
        self.frightened = False
        self.frightened_timer = 0
        
    def update(self, maze, pacman):
        if self.frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened = False
        
        self.position_offset += self.speed
        if self.position_offset >= 1:
            self.position_offset = 0
            
            # Simple AI: choose random valid direction
            import random
            valid_directions = []
            for direction in Direction:
                next_x = self.x + direction.value[0]
                next_y = self.y + direction.value[1]
                if 0 <= next_y < len(maze) and 0 <= next_x < len(maze[0]):
                    if maze[next_y][next_x] != 1:
                        # Don't go backwards
                        if direction.value[0] != -self.direction.value[0] or direction.value[1] != -self.direction.value[1]:
                            valid_directions.append(direction)
            
            if valid_directions:
                self.direction = random.choice(valid_directions)
                self.x += self.direction.value[0]
                self.y += self.direction.value[1]
            
            # Wrap around tunnel
            if self.x < 0:
                self.x = len(maze[0]) - 1
            elif self.x >= len(maze[0]):
                self.x = 0
    
    def get_render_position(self):
        offset_x = self.direction.value[0] * self.position_offset * TILE_SIZE
        offset_y = self.direction.value[1] * self.position_offset * TILE_SIZE
        return (self.x * TILE_SIZE + offset_x, self.y * TILE_SIZE + offset_y)
    
    def draw(self, screen):
        x, y = self.get_render_position()
        center_x = int(x + TILE_SIZE // 2)
        center_y = int(y + TILE_SIZE // 2)
        radius = TILE_SIZE // 2 - 2
        
        if self.frightened:
            # Flashing effect when frightened timer is low
            if self.frightened_timer < 100 and self.frightened_timer % 20 < 10:
                color = WHITE
            else:
                color = BLUE
        else:
            color = self.color
        
        # Draw ghost body (circle on top)
        pygame.draw.circle(screen, color, (center_x, center_y - 2), radius)
        
        # Draw ghost body rectangle
        pygame.draw.rect(screen, color, (center_x - radius, center_y - 2, radius * 2, radius + 4))
        
        # Draw wavy bottom with smoother curves
        wave_count = 3
        wave_width = (radius * 2) // wave_count
        for i in range(wave_count):
            wave_x = center_x - radius + i * wave_width + wave_width // 2
            pygame.draw.circle(screen, color, (wave_x, center_y + radius), wave_width // 2)
        
        # Cover the gaps between waves
        pygame.draw.rect(screen, color, (center_x - radius, center_y, radius * 2, radius))
        
        # Redraw wavy bottom outline
        for i in range(wave_count):
            wave_x = center_x - radius + i * wave_width + wave_width // 2
            pygame.draw.circle(screen, color, (wave_x, center_y + radius), wave_width // 2)
        
        if self.frightened:
            # Draw scared face
            eye_offset = radius // 3
            eye_radius = radius // 5
            # Draw simple dots for scared eyes
            pygame.draw.circle(screen, WHITE, (center_x - eye_offset, center_y - 2), eye_radius)
            pygame.draw.circle(screen, WHITE, (center_x + eye_offset, center_y - 2), eye_radius)
            
            # Draw wavy mouth
            mouth_y = center_y + radius // 3
            for mx in range(-radius // 2, radius // 2, 3):
                my_offset = 2 if (mx // 3) % 2 == 0 else -2
                pygame.draw.circle(screen, WHITE, (center_x + mx, mouth_y + my_offset), 1)
        else:
            # Draw normal eyes with pupils
            eye_offset = radius // 3
            eye_radius = radius // 3
            pupil_radius = radius // 5
            
            # White of eyes
            pygame.draw.circle(screen, WHITE, (center_x - eye_offset, center_y - 2), eye_radius)
            pygame.draw.circle(screen, WHITE, (center_x + eye_offset, center_y - 2), eye_radius)
            
            # Pupils looking in movement direction
            pupil_offset = 2
            pupil_x = 0
            pupil_y = 0
            if self.direction == Direction.LEFT:
                pupil_x = -pupil_offset
            elif self.direction == Direction.RIGHT:
                pupil_x = pupil_offset
            elif self.direction == Direction.UP:
                pupil_y = -pupil_offset
            elif self.direction == Direction.DOWN:
                pupil_y = pupil_offset
            
            pygame.draw.circle(screen, DARK_BLUE, (center_x - eye_offset + pupil_x, center_y - 2 + pupil_y), pupil_radius)
            pygame.draw.circle(screen, DARK_BLUE, (center_x + eye_offset + pupil_x, center_y - 2 + pupil_y), pupil_radius)
    
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = Direction.LEFT
        self.position_offset = 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.maze = [row[:] for row in MAZE]  # Copy maze
        self.pacman = PacMan()
        self.ghosts = [
            Ghost(13, 11, RED),
            Ghost(14, 11, PINK),
            Ghost(13, 13, CYAN),
            Ghost(14, 13, ORANGE)
        ]
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.high_score = self.load_high_score()
        self.combo = 0  # For ghost eating combo
        self.score_popup = []  # List of (text, x, y, timer) for score popups
    
    def load_high_score(self):
        """Load high score from file"""
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pacman.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.pacman.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT:
                    self.pacman.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.pacman.next_direction = Direction.RIGHT
                elif event.key == pygame.K_SPACE and (self.game_over or self.win):
                    self.reset_game()
        return True
    
    def reset_game(self):
        self.maze = [row[:] for row in MAZE]
        self.pacman = PacMan()
        for ghost in self.ghosts:
            ghost.reset()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.combo = 0
        self.score_popup = []
    
    def update(self):
        if self.game_over or self.win:
            return
        
        # Update score popups
        self.score_popup = [(text, x, y, timer - 1) for text, x, y, timer in self.score_popup if timer > 1]
        
        # Update Pac-Man
        self.pacman.update(self.maze)
        
        # Check pellet collision
        if self.maze[self.pacman.y][self.pacman.x] == 2:
            self.maze[self.pacman.y][self.pacman.x] = 0
            self.score += 10
        elif self.maze[self.pacman.y][self.pacman.x] == 3:
            self.maze[self.pacman.y][self.pacman.x] = 0
            self.score += 50
            self.combo = 0  # Reset combo on power pellet
            # Frighten ghosts
            for ghost in self.ghosts:
                ghost.frightened = True
                ghost.frightened_timer = 300  # 5 seconds at 60 FPS
        
        # Check win condition
        pellets_remaining = sum(row.count(2) + row.count(3) for row in self.maze)
        if pellets_remaining == 0:
            self.win = True
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        
        # Update ghosts
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman)
            
            # Check collision with Pac-Man
            if abs(ghost.x - self.pacman.x) < 1 and abs(ghost.y - self.pacman.y) < 1:
                if ghost.frightened:
                    ghost.reset()
                    # Combo scoring: 200, 400, 800, 1600
                    ghost_score = 200 * (2 ** self.combo)
                    self.score += ghost_score
                    self.combo += 1
                    # Add score popup
                    popup_x = ghost.x * TILE_SIZE + TILE_SIZE // 2
                    popup_y = ghost.y * TILE_SIZE
                    self.score_popup.append((str(ghost_score), popup_x, popup_y, 60))
                else:
                    self.lives -= 1
                    self.combo = 0
                    if self.lives <= 0:
                        self.game_over = True
                        # Update high score
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                    else:
                        self.pacman = PacMan()
                        for g in self.ghosts:
                            g.reset()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw maze with enhanced graphics
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 1:  # Wall with gradient effect
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, BLUE, rect)
                    # Add border for 3D effect
                    pygame.draw.rect(self.screen, LIGHT_BLUE, rect, 1)
                elif cell == 2:  # Pellet with glow
                    center_x = x * TILE_SIZE + TILE_SIZE // 2
                    center_y = y * TILE_SIZE + TILE_SIZE // 2
                    # Outer glow
                    pygame.draw.circle(self.screen, (100, 100, 100), (center_x, center_y), 3)
                    # Inner pellet
                    pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 2)
                elif cell == 3:  # Power pellet with animation
                    center_x = x * TILE_SIZE + TILE_SIZE // 2
                    center_y = y * TILE_SIZE + TILE_SIZE // 2
                    # Pulsing effect
                    pulse = abs((pygame.time.get_ticks() // 10) % 40 - 20) / 20
                    radius = int(5 + pulse * 2)
                    # Outer glow
                    pygame.draw.circle(self.screen, (200, 200, 150), (center_x, center_y), radius + 2)
                    # Power pellet
                    pygame.draw.circle(self.screen, WHITE, (center_x, center_y), radius)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw Pac-Man
        self.pacman.draw(self.screen)
        
        # Draw score popups
        for text, x, y, timer in self.score_popup:
            alpha = min(255, timer * 4)
            popup_surface = self.small_font.render(text, True, GOLD)
            popup_surface.set_alpha(alpha)
            self.screen.blit(popup_surface, (x - 20, y - timer // 2))
        
        # Draw top status bar with background
        status_bar_height = 50
        pygame.draw.rect(self.screen, DARK_BLUE, (0, SCREEN_HEIGHT - status_bar_height, SCREEN_WIDTH, status_bar_height))
        pygame.draw.line(self.screen, LIGHT_BLUE, (0, SCREEN_HEIGHT - status_bar_height), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - status_bar_height), 2)
        
        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, SCREEN_HEIGHT - 40))
        
        # Draw high score
        high_score_color = GOLD if self.score >= self.high_score else GRAY
        high_score_text = self.font.render(f"HIGH: {self.high_score}", True, high_score_color)
        self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 40))
        
        # Draw lives as Pac-Man icons
        for i in range(self.lives):
            life_x = SCREEN_WIDTH - 100 + i * 25
            life_y = SCREEN_HEIGHT - 30
            pygame.draw.circle(self.screen, YELLOW, (life_x, life_y), 8)
            # Draw small mouth
            points = [(life_x, life_y), (life_x + 6, life_y - 4), (life_x + 6, life_y + 4)]
            pygame.draw.polygon(self.screen, DARK_BLUE, points)
        
        # Draw game over or win message with enhanced styling
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.large_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)
            
            if self.score == self.high_score and self.score > 0:
                new_high_text = self.font.render("NEW HIGH SCORE!", True, GOLD)
                new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                self.screen.blit(new_high_text, new_high_rect)
                
        elif self.win:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            win_text = self.large_font.render("YOU WIN!", True, GOLD)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(win_text, text_rect)
            
            restart_text = self.small_font.render("Press SPACE to play again", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)
            
            if self.score == self.high_score:
                new_high_text = self.font.render("NEW HIGH SCORE!", True, GOLD)
                new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                self.screen.blit(new_high_text, new_high_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
