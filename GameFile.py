import pygame, sys
from pygame.locals import *
pygame.init()

# Game Setup
clock = pygame.time.Clock()
width = 750
height = 750
screen = pygame.display.set_mode((width, height))
print(screen)

# Background Setup
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (width, height))

# Player Class
class Character:
    def __init__(self, image_path, x, y, is_player=True):
        self.image = pygame.image.load(image_path).convert_alpha()  # Loads Main Character
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

    #Enemy Attributes
        self.is_chasing = False
        self.patrol_direction = 1 # 1 for right, -1 for left
        self.patrol_range = 635
        self.start_x = x

    # Methods
    def update(self, player_rect):
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

        self.on_platform = False  # Reset to false at the start

        for platform in platforms:
            if self.rect.colliderect(platform):
                # Check if player is falling and lands on top of the platform
                if self.velocity_y > 0 and self.rect.bottom <= platform.top + self.velocity_y:
                    self.rect.bottom = platform.top  # Land directly on top of the platform
                    self.velocity_y = 0  # Stop the falling movement (no more gravity pulling)
                    self.on_platform = True  # Mark as on platform
                    break  # Stop checking further platforms if the player has landed

                # If the player collides with the bottom of the platform (player is falling through)
                elif self.rect.top < platform.bottom and self.rect.bottom > platform.top:
                    # Prevent the player from passing through the platform
                    if self.velocity_y > 0:
                        self.rect.bottom = platform.top  # Stop player just above platform
                        self.velocity_y = 0  # Stop downward motion (gravity stops)
                        self.on_platform = True
                        break

                # Handle horizontal collision (left or right sides of the player)
                if self.rect.colliderect(platform):
                    if self.rect.right > platform.left and self.rect.left < platform.right:
                        if self.velocity_x < 0:  # Moving left
                            self.rect.left = platform.right  # Stop movement on the left side
                        elif self.velocity_x > 0:  # Moving right
                            self.rect.right = platform.left  # Stop movement on the right side

        # Prevent the player from falling below the bottom of the screen (adjust as needed)
        if self.rect.bottom >= height - 5:  # Adjust this to ensure the player doesn't fall below the screen
            self.on_platform = True
            self.rect.bottom = height - 5  # Set the player's bottom to the ground level
            self.velocity_y = 0  # Stop the falling movement
            self.is_jumping = False  # Player is no longer jumping

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

        if keys[pygame.K_SPACE]:  # Jump (Add double jump later)
            if self.on_platform:
                self.velocity_y = -7  # Allows player to jump
                self.on_platform = False
                self.is_jumping = True
                print("Player jumped!")  # Debug Test

    def handle_enemies(self, player_rect):  # Handles Enemies movement
        if self.is_chasing:
            self.chase_player(player_rect)
        else:
            self.patrol()

    def chase_player(self, player_rect):
        if self.rect.x < player_rect.x:
            self.velocity_x = self.walk_speed
        elif self.rect.x > player_rect.x:
            self.velocity_x = -self.walk_speed
        else:
            self.velocity_x = 0

    def patrol(self):
        self.velocity_x = self.walk_speed * self.patrol_direction
        if self.rect.right >= 650:
            self.patrol_direction = -1  # Move left
            # If the enemy has moved past the patrol range on the left, change direction
        elif self.rect.left <= 60:
            self.patrol_direction = 1  # Move right

# Characters
player = Character('sprite.png', 60, 745, is_player=True)
enemy1 = Character('ghostsprite2.png', 650, 745, is_player=False)
enemy1.is_chasing = True
enemy2 = Character('bat.png', 305, 150, is_player=False)
enemy2.is_chasing = False

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

while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)
        if keys[pygame.K_ESCAPE]:
            sys.exit(1)

    screen.blit(background, (0, 0))
    # Update Characters
    player.update(enemy1.rect)
    enemy1.update(player.rect)
    enemy2.update(player.rect)

    # Drawing
    screen.blit(player.image, player.rect)
    screen.blit(enemy1.image, enemy1.rect)
    screen.blit(enemy2.image, enemy2.rect)
    #for platform in platforms:
        #pygame.draw.rect(screen, (255, 0, 0), platform)

    pygame.display.flip()
    clock.tick(60)
