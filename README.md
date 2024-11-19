# Bubble Shooter Game

A colorful and engaging Bubble Shooter game built with Pygame, featuring special bubbles, chain reactions, and particle effects. This project was developed in collaboration with Claude 3.5 Sonnet, an AI assistant that helped with code optimization, bug fixes, and feature implementation.

![image](https://github.com/user-attachments/assets/34749e73-48e1-4e03-a17c-16354bf7899e)

## Features

- Classic bubble shooter mechanics with modern twists
- Special bubble types:
  - Bomb bubbles that trigger chain reactions
  - Stone bubbles that add strategic challenge
- Particle effects for explosions and falling bubbles
- Score system
- Laser sight aiming guide
- Game over and victory conditions
- Intuitive controls

## Gameplay

- **Objective**: Clear the screen of bubbles by matching 3 or more of the same color
- **Controls**:
  - Left/Right Arrow Keys: Rotate the shooter
  - Spacebar: Shoot bubble
  - L: Toggle laser sight
  - R: Restart game

## Special Mechanics

- **Color Matching**: Connect 3 or more bubbles of the same color to make them disappear
- **Chain Reactions**: Bomb bubbles explode and take out neighboring bubbles
- **Dropping Bubbles**: Bubbles not connected to the top will fall, earning extra points
- **Score System**: Points awarded for:
  - Matching bubbles: 10 points per bubble
  - Falling bubbles: 20 points per bubble

## Technical Details

Built using:
- Python 3
- Pygame library
- Object-oriented programming principles

## Development Process

This game was developed through collaborative programming with Claude 3.5 Sonnet, an AI assistant. Key contributions from Claude included:
- Initial and subsequent code from a textually described game idea
- Feature implementation (bombs, stones, laser sight, particle effects etc)
- Bug fixing (shooter angle limits, wall bouncing)
- Code optimization
- Game mechanics refinement

## Requirements

- Python 3.x
- Pygame library
- Required assets (bubble images)

## Installation

1. Clone the repository
2. Install Python 3 if not already installed
3. Install Pygame:
```bash
pip install pygame
```
4. Run the game:
```bash
python bubble-shooter-game.py
```

## Assets Required

The game requires bubble images in the `assets` folder:
- Regular bubbles: `bubble_[color].png`
- Bomb bubbles: `bomb_[color].png`
- Stone bubble: `bubble_stone.png`

Where `[color]` includes: green, red, blue, yellow, purple, cyan

## Ideas for Future Improvements

- Add sound effects
- Implement different levels
- Add power-ups
- Include high score system
- Add menu system

## License

https://github.com/jussinrepo/bubble/blob/main/LICENSE

## Acknowledgments

Special thanks to:
- Claude 3.5 Sonnet for code assistance and optimization
- Pygame community for the excellent gaming framework

## Contributing

Feel free to fork the repository and submit pull requests with improvements!

---
*Note: This is a fun project created for educational purposes and gaming enjoyment. Feel free to modify and improve upon it!*
