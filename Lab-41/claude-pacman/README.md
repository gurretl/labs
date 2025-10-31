# Pac-Man Game

A classic Pac-Man game implementation in Python using Pygame.

## Features

- Classic Pac-Man gameplay
- Maze with walls, pellets, and power pellets
- 4 colorful ghosts with basic AI
- Power pellets that make ghosts vulnerable
- Score tracking and lives system
- Smooth animations
- Game over and win conditions

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

Run the game:
```bash
python pacman.py
```

### Controls

- **Arrow Keys**: Move Pac-Man (Up, Down, Left, Right)
- **Space**: Restart game (after game over or win)

### Gameplay

- Eat all the pellets to win!
- Avoid the ghosts or you'll lose a life
- Eat power pellets (large dots) to make ghosts vulnerable for a short time
- Score points by eating pellets (10 points) and power pellets (50 points)
- Eat frightened ghosts for bonus points (200 points)
- You start with 3 lives

## Game Elements

- **Yellow circle**: Pac-Man
- **Blue walls**: Maze walls
- **Small white dots**: Regular pellets (10 points)
- **Large white dots**: Power pellets (50 points, make ghosts vulnerable)
- **Colored ghosts**: 
  - Red ghost
  - Pink ghost
  - Cyan ghost
  - Orange ghost
- When frightened, ghosts turn blue

Enjoy playing!
