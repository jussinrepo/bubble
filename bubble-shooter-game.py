import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 640, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Shooter")

# Colors and images
BACKGROUND = (230, 230, 255)
COLOR_NAMES = ['green', 'red', 'blue', 'yellow', 'purple', 'cyan']
BUBBLE_IMAGES = {}

# Add this color mapping
COLOR_RGB = {
    'green': (0, 255, 0),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'cyan': (0, 255, 255),
    'bomb': (0, 0, 0),  # Black for bomb
    'stone': (128, 128, 128)  # Grey for stone
}

# Update the BUBBLE_IMAGES loading section
BUBBLE_IMAGES = {}
for color in COLOR_NAMES:
    # Load regular bubble image
    image_path = os.path.join('assets', f'bubble_{color}.png')
    BUBBLE_IMAGES[color] = pygame.image.load(image_path)
    BUBBLE_IMAGES[color] = pygame.transform.scale(BUBBLE_IMAGES[color], (40, 40))
    
    # Load bomb bubble image
    bomb_image_path = os.path.join('assets', f'bomb_{color}.png')
    BUBBLE_IMAGES[f'bomb_{color}'] = pygame.image.load(bomb_image_path)
    BUBBLE_IMAGES[f'bomb_{color}'] = pygame.transform.scale(BUBBLE_IMAGES[f'bomb_{color}'], (40, 40))

# Load stone bubble image
stone_image_path = os.path.join('assets', 'bubble_stone.png')
BUBBLE_IMAGES['stone'] = pygame.image.load(stone_image_path)
BUBBLE_IMAGES['stone'] = pygame.transform.scale(BUBBLE_IMAGES['stone'], (40, 40))

# Bubble properties
BUBBLE_RADIUS = 20
COLLISION_RADIUS = 10
ROWS = 8
COLS = 15

# Special bubble probabilities
BOMB_PROBABILITY = 0.2  # 20% chance for a bomb bubble
STONE_PROBABILITY = 0.1  # 10% chance for a stone bubble

# Shooter properties
SHOOTER_Y = HEIGHT - 50
SHOOT_SPEED = 10
TURN_SPEED = 0.03

# Game state
score = 0
game_over = False
game_won = False
available_colors = COLOR_NAMES.copy()
laser_sight = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = COLOR_RGB.get(color, (255, 255, 255))
        self.initial_radius = random.randint(2, 5)
        self.radius = self.initial_radius
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = random.randint(45, 105)  # Randomized lifetime between 0.75 and 1.75 seconds
        self.max_life = self.life
        self.gravity = 0.1
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity
        self.life -= 1
        # Update radius based on remaining life
        self.radius = self.initial_radius * (self.life / self.max_life)

        # Bounce off screen borders
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -0.8
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.dy *= -0.8
            self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), max(1, int(self.radius)))
        
class Bubble:
    def __init__(self, row, col, color, is_bomb=False):
        self.row = row
        self.col = col
        self.color = color
        self.x, self.y = get_bubble_position(row, col)
        self.is_bomb = is_bomb
        self.is_stone = color == 'stone'
        self.image = BUBBLE_IMAGES[f'bomb_{color}'] if self.is_bomb else BUBBLE_IMAGES[color]
        self.falling = False
        self.fall_speed = 0
        self.exploding = False
        self.explosion_frame = 0
        self.explosion_delay = 0
        self.particles_created = False  

    def draw(self):
        if self.exploding:
            progress = self.explosion_frame / 15
            scale = 1 + progress * 0.5
            scaled_image = pygame.transform.scale(self.image, (int(40 * scale), int(40 * scale)))
            alpha = int(255 * (1 - progress))
            scaled_image.set_alpha(alpha)
            screen.blit(scaled_image, (int(self.x - BUBBLE_RADIUS * scale), int(self.y - BUBBLE_RADIUS * scale)))
        else:
            screen.blit(self.image, (int(self.x - BUBBLE_RADIUS), int(self.y - BUBBLE_RADIUS)))

    def update(self):
        if self.falling:
            self.fall_speed += 0.2
            self.y += self.fall_speed
            if self.y > HEIGHT + BUBBLE_RADIUS:
                return "score"
        elif self.exploding:
            if self.explosion_delay > 0:
                self.explosion_delay -= 1
                return False
                
            # Create particles when explosion actually starts
            if not self.particles_created:
                self.particles_created = True
                return "create_particles"
                
            self.explosion_frame += 1
            if self.explosion_frame >= 15:
                return True
        return False

    def start_explosion(self, delay=0):
        self.exploding = True
        self.explosion_delay = delay

class Shooter:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = SHOOTER_Y
        self.angle = math.pi/2  # This sets the initial angle to straight up (90 degrees)
        self.color = random.choice(available_colors)
        self.image = BUBBLE_IMAGES[self.color]

    def draw(self):
        end_x = self.x + math.cos(self.angle) * 50
        end_y = self.y - math.sin(self.angle) * 50
        pygame.draw.line(screen, (0, 0, 0), (self.x, self.y), (end_x, end_y), 5)
        screen.blit(self.image, (int(self.x - BUBBLE_RADIUS), int(self.y - BUBBLE_RADIUS)))

    def rotate(self, direction):
        self.angle += direction * TURN_SPEED
        # Limit angle between 0.1π and 0.9π (18 to 162 degrees)
        self.angle = max(0.1 * math.pi, min(self.angle, 0.9 * math.pi))

    def shoot(self):
        return FlyingBubble(self.x, self.y, self.color, math.cos(self.angle) * SHOOT_SPEED, -math.sin(self.angle) * SHOOT_SPEED)

class FlyingBubble:
    def __init__(self, x, y, color, dx, dy):
        self.x = x
        self.y = y
        self.color = color
        self.dx = dx
        self.dy = dy
        self.image = BUBBLE_IMAGES[color]

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        screen.blit(self.image, (int(self.x - BUBBLE_RADIUS), int(self.y - BUBBLE_RADIUS)))

def get_bubble_position(row, col):
    x = col * (BUBBLE_RADIUS * 2 + 1) + BUBBLE_RADIUS + (BUBBLE_RADIUS if row % 2 == 1 else 0)
    y = row * (BUBBLE_RADIUS * math.sqrt(3) + 1) + BUBBLE_RADIUS
    return x, y

def get_grid_position(x, y):
    col = round((x - BUBBLE_RADIUS) / (BUBBLE_RADIUS * 2 + 1))
    row = round((y - BUBBLE_RADIUS) / (BUBBLE_RADIUS * math.sqrt(3) + 1))
    return row, col

def get_neighbors(row, col):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]
    if row % 2 == 1:
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
    return [(row + dr, col + dc) for dr, dc in directions]

def find_snap_position(flying_bubble, bubbles):
    collided_bubble = next((b for b in bubbles if math.hypot(b.x - flying_bubble.x, b.y - flying_bubble.y) < BUBBLE_RADIUS + COLLISION_RADIUS), None)
    if collided_bubble:
        neighbors = get_neighbors(collided_bubble.row, collided_bubble.col)
        empty_neighbors = [(r, c) for r, c in neighbors if not any(b.row == r and b.col == c for b in bubbles)]
        if empty_neighbors:
            return min(empty_neighbors, key=lambda pos: math.hypot(flying_bubble.x - get_bubble_position(*pos)[0], flying_bubble.y - get_bubble_position(*pos)[1]))
    return get_grid_position(flying_bubble.x, flying_bubble.y)

def remove_connected_bubbles(start_bubble, bubbles):
    color_match = start_bubble.color
    to_remove = set()
    to_check = [start_bubble]
    
    # First, find all connected bubbles of the same color
    while to_check:
        bubble = to_check.pop()
        if bubble not in to_remove and bubble.color == color_match:
            to_remove.add(bubble)
            neighbors = get_neighbors(bubble.row, bubble.col)
            for row, col in neighbors:
                neighbor = next((b for b in bubbles if b.row == row and b.col == col and b.color == color_match), None)
                if neighbor and neighbor not in to_remove:
                    to_check.append(neighbor)
    
    # If we have a match of 3 or more, then we start the removal process
    if len(to_remove) >= 3 or start_bubble.is_bomb:
        bombs_to_process = [(start_bubble, 0)] if start_bubble.is_bomb else []
        processed_bombs = set()
        explosion_sequence = []
        current_delay = 0
        
        # If starting with color match (not bomb), add all matched bubbles first
        if not start_bubble.is_bomb and len(to_remove) >= 3:
            for bubble in to_remove:
                explosion_sequence.append((bubble, current_delay))
                if bubble.is_bomb and bubble not in processed_bombs:
                    bombs_to_process.append((bubble, current_delay + 5))
                    processed_bombs.add(bubble)
        
        # Process chain reaction of bombs
        while bombs_to_process:
            bomb, delay = bombs_to_process.pop(0)
            current_delay = delay  # Update current delay based on this bomb
            
            # Get all neighbors of the exploding bomb
            neighbors = get_neighbors(bomb.row, bomb.col)
            for row, col in neighbors:
                neighbor = next((b for b in bubbles if b.row == row and b.col == col), None)
                if neighbor and (neighbor, current_delay) not in explosion_sequence:
                    explosion_sequence.append((neighbor, current_delay))
                    if neighbor.is_bomb and neighbor not in processed_bombs:
                        bombs_to_process.append((neighbor, current_delay + 5))
                        processed_bombs.add(neighbor)
        
        # Start explosions with appropriate delays
        for bubble, delay in explosion_sequence:
            bubble.start_explosion(delay)
            to_remove.add(bubble)
        
        return list(to_remove)
    else:
        return []

def explode_bomb(bomb, bubbles):
    to_remove = set()
    neighbors = get_neighbors(bomb.row, bomb.col)
    for row, col in neighbors:
        neighbor = next((b for b in bubbles if b.row == row and b.col == col), None)
        if neighbor:
            to_remove.add(neighbor)
    return to_remove

def find_floating_bubbles(bubbles):
    connected = set()
    to_check = [b for b in bubbles if b.row == 0]
    while to_check:
        bubble = to_check.pop()
        if bubble not in connected:
            connected.add(bubble)
            neighbors = get_neighbors(bubble.row, bubble.col)
            for row, col in neighbors:
                neighbor = next((b for b in bubbles if b.row == row and b.col == col), None)
                if neighbor and neighbor not in connected:
                    to_check.append(neighbor)
    return [b for b in bubbles if b not in connected]

def update_available_colors(bubbles):
    global available_colors
    colors_in_play = set(bubble.color for bubble in bubbles if bubble.color in COLOR_NAMES)
    available_colors = [color for color in COLOR_NAMES if color in colors_in_play]

def create_initial_bubbles():
    bubbles = []
    for row in range(ROWS):
        for col in range(COLS):
            if row == 0:
                color = random.choice(COLOR_NAMES)
                is_bomb = random.random() < BOMB_PROBABILITY
            else:
                color = 'stone' if random.random() < STONE_PROBABILITY else random.choice(COLOR_NAMES)
                is_bomb = random.random() < BOMB_PROBABILITY if color != 'stone' else False
            new_bubble = Bubble(row, col, color, is_bomb)
            bubbles.append(new_bubble)
    return bubbles

bubbles = create_initial_bubbles()

shooter = Shooter()
flying_bubble = None
particles = []

# Game loop
running = True
clock = pygame.time.Clock()
falling_bubble_count = 0

def check_and_drop_floating_bubbles():
    global bubbles, particles
    floating_bubbles = find_floating_bubbles(bubbles)
    for bubble in floating_bubbles:
        bubble.falling = True
    return len(floating_bubbles)

def check_game_over():
    return any(bubble.y + BUBBLE_RADIUS > SHOOTER_Y for bubble in bubbles if not bubble.falling)

def create_fresh_game():
    global bubbles, shooter, flying_bubble, particles, score, game_over, game_won, falling_bubble_count, laser_sight
    bubbles = create_initial_bubbles()
    shooter = Shooter()
    flying_bubble = None
    particles = []
    score = 0
    game_over = False
    game_won = False
    falling_bubble_count = 0
    laser_sight = False

# Add this function to simulate bubble path:
def simulate_bubble_path(start_x, start_y, dx, dy):
    x, y = start_x, start_y
    while y > BUBBLE_RADIUS:  # Stop at top of screen
        x += dx
        y += dy
        
        # Bounce off walls
        if x <= BUBBLE_RADIUS:
            x = BUBBLE_RADIUS
            dx *= -1
        elif x >= WIDTH - BUBBLE_RADIUS:
            x = WIDTH - BUBBLE_RADIUS
            dx *= -1
            
        # Check for collision with existing bubbles
        for bubble in bubbles:
            if math.hypot(bubble.x - x, bubble.y - y) < BUBBLE_RADIUS + COLLISION_RADIUS:
                return (x, y)
    
    return (x, y)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not flying_bubble and not game_over and not game_won:
                flying_bubble = shooter.shoot()
            elif event.key == pygame.K_l:  # Add this section
                laser_sight = not laser_sight
            elif event.key == pygame.K_r:  # Add this section
                create_fresh_game()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                pygame.quit() # Quit the game

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        shooter.rotate(1)
    if keys[pygame.K_RIGHT]:
        shooter.rotate(-1)

    if flying_bubble:
        flying_bubble.move()

        # Bounce off walls
        if flying_bubble.x <= BUBBLE_RADIUS or flying_bubble.x >= WIDTH - BUBBLE_RADIUS:
            flying_bubble.dx *= -1

        # Check for collision with existing bubbles or top of the screen
        if flying_bubble.y <= BUBBLE_RADIUS or any(math.hypot(b.x - flying_bubble.x, b.y - flying_bubble.y) < BUBBLE_RADIUS + COLLISION_RADIUS for b in bubbles):
            row, col = find_snap_position(flying_bubble, bubbles)
            new_bubble = Bubble(row, col, flying_bubble.color)
            bubbles.append(new_bubble)
            
            # Check for matches
            matches = remove_connected_bubbles(new_bubble, bubbles)
            if matches:
                for bubble in matches:
                    bubbles.remove(bubble)
                bubbles.extend(matches)  # Add back to animate explosion
                score += len(matches) * 10
            
            # Check for floating bubbles immediately
            falling_bubble_count += check_and_drop_floating_bubbles()
            
            flying_bubble = None
            
            # Update available colors
            update_available_colors(bubbles)
            shooter.color = random.choice(available_colors)
            shooter.image = BUBBLE_IMAGES[shooter.color]

            # Check for win condition
            if not bubbles:
                game_won = True

    # Update bubbles and particles
    bubbles_to_remove = []
    for bubble in bubbles:
        result = bubble.update()
        if result == "score":
            score += 20  # Score for a single falling bubble
            falling_bubble_count -= 1
            # Create explosion effect
            for _ in range(20):
                particles.append(Particle(bubble.x, HEIGHT - BUBBLE_RADIUS, bubble.color))
            bubbles_to_remove.append(bubble)
        elif result == "create_particles":
            # Create particles for popping effect
            particle_color = 'white' if bubble.is_bomb else bubble.color
            for _ in range(40 if bubble.is_bomb else 20):
                particles.append(Particle(bubble.x, bubble.y, particle_color))
        elif result:
            bubbles_to_remove.append(bubble)

    for bubble in bubbles_to_remove:
        bubbles.remove(bubble)
    
    # Check for floating bubbles again after updates
    falling_bubble_count += check_and_drop_floating_bubbles()
    
    # Check for game over condition (only for non-falling bubbles)
    if check_game_over():
        game_over = True

    # Check for win condition
    if not bubbles:
        game_won = True

    particles = [p for p in particles if p.life > 0]
    for particle in particles:
        particle.move()

    # Draw everything
    screen.fill(BACKGROUND)
    
    for bubble in bubbles:
        bubble.draw()
    
    if flying_bubble:
        flying_bubble.draw()
    
    for particle in particles:
        particle.draw()

    # Draw laser sight if enabled
    if laser_sight and not flying_bubble and not game_over and not game_won:
        dx = math.cos(shooter.angle) * SHOOT_SPEED
        dy = -math.sin(shooter.angle) * SHOOT_SPEED
        end_x, end_y = simulate_bubble_path(shooter.x, shooter.y, dx, dy)
        # Draw a red dot at the landing point
        pygame.draw.circle(screen, (255, 0, 0), (int(end_x), int(end_y)), 5)

    shooter.draw()

    # Draw score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    score_rect = score_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(score_text, score_rect)

    if game_over:
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        restart_text = font.render("Press R to restart", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 70, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 85, HEIGHT // 2 + 20))
    elif game_won:
        game_won_text = font.render("YOU WIN!", True, (0, 255, 0))
        restart_text = font.render("Press R to restart", True, (0, 255, 0))
        screen.blit(game_won_text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 85, HEIGHT // 2 + 20))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()