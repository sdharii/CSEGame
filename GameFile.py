import pygame, sys, random
from pygame.locals import *
pygame.init()

# Game Setup
clock = pygame.time.Clock()
width = 750
height = 750
screen = pygame.display.set_mode((width, height))

# Background Setup
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (width, height))

# Font Setup for Text (smaller font size)
font = pygame.font.Font(None, 20)  # Reduced the font size

# Player Class
class Character:
    def __init__(self, image_path, x, y, is_player=True):
        self.image = pygame.image.load(image_path).convert_alpha()  # Loads the character image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Attributes
        self.on_platform = False  # Confirms that character isn't on platform
        self.walk_speed = 3
        self.run = False  # Confirms that character is not running
        self.run_speed = 6
        self.gravity = 0.3  # Allows character to fall
        self.velocity_y = 0  # Allows character to jump
        self.velocity_x = 0  # Stops character when no buttons are pressed
        self.is_player = is_player
        self.is_jumping = False  # Tracks jumping status

        # Enemy Attributes
        self.is_chasing = False
        self.patrol_direction = 1  # 1 for right, -1 for left
        self.patrol_range = 635
        self.start_x = x

        # Player Health (percentage of max health)
        self.max_health = 20  # Max health (20 seconds of standing in a monster)
        self.health = self.max_health

    def update(self, player_rect, enemies, platforms, candles):
        if self.is_player:
            self.handle_player_input()  # Allows player to control main character!!!
        else:
            self.handle_enemies(player_rect)

        if not self.on_platform:
            self.velocity_y += self.gravity  # Apply gravity if not on platform
        else:
            if self.velocity_y > 0:
                self.velocity_y = 0  # Stop downward velocity when on platform

        # Update Position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.on_platform = False  # Reset to false at the start of each frame

        # Platform Collision Check
        self.check_platforms(platforms)

        if not self.is_player and self != enemy2: #ignores platforms for bat!!!
            self.check_platforms(platforms)

        # Prevent falling below the bottom of the screen
        if self.rect.bottom >= height - 5:
            self.on_platform = True
            self.rect.bottom = height - 5  # Set the player's bottom to the ground level
            self.velocity_y = 0  # Stop downward movement
            self.is_jumping = False  # Player is no longer jumping

        # Check for collisions with monsters (enemies)
        self.check_monster_collision(enemies)

        # Check for candle collisions
        self.check_candle_collision(candles)

    def fly_toward_player(self,player_rect):
        # Move towards the player's position
        direction_x = player_rect.x - self.rect.x
        direction_y = player_rect.y - self.rect.y

        # Normalize the movement to ensure smooth, diagonal movement if needed
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if distance != 0:
            direction_x /= distance
            direction_y /= distance

        # Set the bat's velocity towards the player, but at a slow pace
        self.velocity_x = direction_x * 2  # Adjust the speed as needed
        self.velocity_y = direction_y * 2

    def check_platforms(self, platforms):
        # Check if the player is colliding with any platforms
        for platform in platforms:
            if self.rect.colliderect(platform):
                # If the player is falling and collides with a platform from above
                if self.velocity_y > 0 and self.rect.bottom <= platform.top + self.velocity_y:
                    self.rect.bottom = platform.top  # Land directly on top of the platform
                    self.velocity_y = 0  # Stop downward movement (gravity stops)
                    self.on_platform = True  # Player is on the platform
                    break  # Stop checking further platforms if the player has landed
                # Prevent the player from going through the platform from below
                elif self.rect.top < platform.bottom and self.rect.bottom > platform.top:
                    if self.velocity_y > 0:
                        self.rect.bottom = platform.top  # Stop player just above platform
                        self.velocity_y = 0  # Stop downward motion (gravity stops)
                        self.on_platform = True
                        break

    def check_monster_collision(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.is_player:
                    self.health -= 0.1  # Reduce health every frame player collides with an enemy
                    if self.health <= 0:
                        print("Player died!")
                        # You could add code to reset the game or end it here.

    def check_candle_collision(self, candles):
        global score
        if self.is_player:
            for candle in candles:
                if self.rect.colliderect(candle.rect):
                    candles.remove(candle)  # Remove the candle
                    score += 1  # Increase the score
                    print("Candle collected!")
                    if score == 6:
                        print("All candles collected!")

    def check_boundaries(self):
        # Horizontal Boundaries (left and right)
        if self.rect.x < 50:
            self.rect.x = 100  # Prevent moving beyond left boundary
        elif self.rect.x > 711 - self.rect.width:
            self.rect.x = 711 - self.rect.width  # Prevent moving beyond right boundary

        # Vertical Boundaries (top boundary)
        if self.rect.bottom < 750:
            self.rect.bottom = 750

    def handle_player_input(self):  # Handles Player movement
        keys = pygame.key.get_pressed()

        # Movement & Boundaries
        if keys[pygame.K_LSHIFT] and keys[pygame.K_a] and self.rect.x > 65:  # Sprint Left
            self.velocity_x = -self.run_speed
        elif keys[pygame.K_LSHIFT] and keys[pygame.K_d] and self.rect.x < 635:  # Sprint Right
            self.velocity_x = self.run_speed
        elif keys[pygame.K_a] and self.rect.x > 65:
            self.velocity_x = -self.walk_speed
        elif keys[pygame.K_d] and self.rect.x < 635:
            self.velocity_x = self.walk_speed
        else:
            self.velocity_x = 0

        if keys[pygame.K_SPACE]:  # Jump
            if self.on_platform:
                self.velocity_y = -7  # Allows player 2 jump
                self.on_platform = False
                self.is_jumping = True
                print("Player jumped!")  # Debug Test

    def handle_enemies(self, player_rect):  # Handles Enemies movement
        if self.is_chasing:
            self.chase_player(player_rect)
        elif self == enemy2:
            self.fly_toward_player(player_rect)

    def chase_player(self, player_rect):
        if self.rect.x < player_rect.x:
            self.velocity_x = self.walk_speed
        elif self.rect.x > player_rect.x:
            self.velocity_x = -self.walk_speed
        else:
            self.velocity_x = 0

    def patrol(self):
        self.velocity_x = self.walk_speed * self.patrol_direction
        if self.rect.x - self.start_x >= self.patrol_range:
            self.patrol_direction = -1  # Changes direction
        elif self.rect.x - self.start_x <= 0:
            self.patrol_direction = 1  # Changes direction

# Candle Class
class Candle:
    def __init__(self, x, y):
        self.image = pygame.image.load('candle.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Spawn Candles Randomly
def spawn_candles(num_candles, min_distance=50):
    candles = []
    for _ in range(num_candles):
        # Try spawning a new candle
        placed = False
        while not placed:
            platform = random.choice(platforms)  # Choose a random platform for each candle
            # Ensure the candle fits on the platform
            platform_left = platform.left + 5
            platform_right = platform.right - 45

            if platform_left < platform_right:  # Ensure the range is valid
                x = random.randint(platform_left, platform_right)
                y = platform.top - 45  # Set the y-coordinate to place candle on top of platform

                # Check if this new candle is too close to any already placed candles
                too_close = False
                for candle in candles:
                    if abs(candle.rect.x - x) < min_distance:
                        too_close = True
                        break

                if not too_close:
                    candle = Candle(x, y)
                    candles.append(candle)
                    placed = True  # Successfully placed a new candle

    return candles

# Characters
player = Character('sprite.png', 60, 745, is_player=True)
enemy1 = Character('ghostsprite2.png', 650, 745, is_player=False)
enemy1.is_chasing = True
enemy2 = Character('bat2.png', 700, 161, is_player=False)
enemy2.is_chasing = False

# Score tracking
score = 0

# Platforms
platforms = [pygame.Rect(297, 675, 75, 37),
             pygame.Rect(38, 600, 225, 38),
             pygame.Rect(412, 600, 77, 38),
             pygame.Rect(487, 562, 188, 38),
             pygame.Rect(675, 487, 38, 113),
             pygame.Rect(600, 450, 38, 63),
             pygame.Rect(562, 487, 38, 26),
             pygame.Rect(637, 450, 76, 37),
             pygame.Rect(225, 487, 188, 38),
             pygame.Rect(38, 450, 150, 38),
             pygame.Rect(444, 411, 75, 39),
             pygame.Rect(337, 337, 76, 38),
             pygame.Rect(300, 300, 75, 38),
             pygame.Rect(37, 337, 151, 38),
             pygame.Rect(37, 300, 226, 38),
             pygame.Rect(412, 238, 76, 25),
             pygame.Rect(38, 150, 225, 38),
             pygame.Rect(300, 150, 75, 38),
             pygame.Rect(450, 150, 150, 38),
             pygame.Rect(562, 112, 150, 38),
             pygame.Rect(0,712,750,38), #Ground
]

# Main Loop
running = True
candles = spawn_candles(6)  # Spawn 6 candles randomly

while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)
        if keys[pygame.K_ESCAPE]:
            sys.exit(1)

    screen.blit(background, (0, 0))

    # Update Characters
    player.update(enemy1.rect, [enemy1, enemy2], platforms, candles)
    enemy1.update(player.rect, [enemy1, enemy2] , platforms, candles)
    enemy2.update(player.rect, [enemy1, enemy2], platforms, candles)

    # Drawing Candles
    for candle in candles:
        screen.blit(candle.image, candle.rect)

    # Health Bar (Above Player)
    health_bar_width = (player.health / player.max_health) * 100  # Scale health bar width to health percentage
    health_bar_width = max(health_bar_width, 0)  # Prevent negative health bar width

    # Red health bar (fills up based on health)
    pygame.draw.rect(screen, (255, 0, 0),
                     (player.rect.x + (player.rect.width // 2) - 50, player.rect.y - 40, health_bar_width, 20))
    # Background bar (grayish)
    pygame.draw.rect(screen, (60, 60, 60), (player.rect.x + (player.rect.width // 2) - 50, player.rect.y - 40, 100, 20), 5)  # Shadow/Background

    # Drawing the text "HEALTH" inside the health bar
    text = font.render("HEALTH", True, (255, 255, 255))
    screen.blit(text, (player.rect.x + (player.rect.width // 2) - 27, player.rect.y - 37))

    # Drawing the Score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # Render the score text
    screen.blit(score_text, (10, 10))  # Blit the score text at the top-left corner (10, 10)

    # Drawing Characters
    screen.blit(player.image, player.rect)
    screen.blit(enemy1.image, enemy1.rect)
    screen.blit(enemy2.image, enemy2.rect)

    pygame.display.flip()
    clock.tick(60)


    pygame.display.flip()
    clock.tick(60)
