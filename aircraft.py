import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aerius Frontier")

# Colors
WHITE = (255, 255, 255)

RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 192, 203)

COLOR_OPTIONS = [
    (174, 171, 212),
    (248, 231, 159),
    (178, 239, 162)
    ]
    
# Game clock
clock = pygame.time.Clock()
FPS = 60

#Background Music
pygame.mixer.init()
pygame.mixer.music.load("bg-music.ogg")
shoot_sound = pygame.mixer.Sound("shoot.mp3")
hit_sound = pygame.mixer.Sound("hit.mp3")
booster_sound = pygame.mixer.Sound("boost.mp3")

pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)
shoot_sound.set_volume(0.2)
hit_sound.set_volume(0.2)
booster_sound.set_volume(0.3)

#Background Dots
dots = []

# Player settings
player_width = 50
player_height = 50
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - player_height - 10
normal_player_speed = 5
boosted_player_speed = 8
player_speed = normal_player_speed

# Speed boost duration
boost_duration = 0
boosted_shoot_interval = 10
normal_shoot_interval = 20
AUTO_SHOOT_INTERVAL = normal_shoot_interval
auto_shoot_timer = AUTO_SHOOT_INTERVAL

# Pause state
paused = False

# Passed enemy counter
passed_enemies = 0
MAX_PASSED_ENEMIES = 60

# Enemy settings
enemy_width = 50
enemy_height = 50
enemy_speed = 2.5
enemies = []

# Booster settings
booster_width = 30
booster_height = 30
booster_speed = 4  # Increased booster speed
booster_spawn_chance = 0.005  # Rare spawn chance per frame
booster = None

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_speed = 10
bullets = []

#Boss Bullet
beam_width = 5
beam_height = 10

# Boss settings
boss = None
boss_health = 100
boss_bullets = []
boss_attack_timer = 60  # Boss attacks every 60 frames
boss_speed = 3  # Speed at which the boss moves left/right
boss_direction = 1
boss_defeated = False

player_image = pygame.image.load('ship.png')
boss_image = pygame.image.load('boss1.png')
bullet_image = pygame.image.load('beam1.png')
booster_image = pygame.image.load('booster1.png')
boss_bullet_image = pygame.image.load("beam2.png")  # Replace with your actual image path
boss_bullet_rect = boss_bullet_image.get_rect()
enemy_images = [
    pygame.image.load('alien1.png'),
    pygame.image.load('alien2.png'),
    pygame.image.load('alien3.png'),
    pygame.image.load('alien4.png'),
    pygame.image.load('alien5.png'),
    pygame.image.load('alien6.png')
]

# Scale images (optional)
player_image = pygame.transform.scale(player_image, (70, 70))
enemy_images = [pygame.transform.scale(img, (50, 50)) for img in enemy_images]
boss_image = pygame.transform.scale(boss_image, (100, 100))
bullet_image = pygame.transform.scale(bullet_image, (5, 10))
boss_bullet_image = pygame.transform.scale(boss_bullet_image, (4, 10))
booster_image = pygame.transform.scale(booster_image, (50, 50))

# Dot class
class StartScreenDot:
    def __init__(self):
        self.size = random.randint(1, 2)  # Random size between 1 and 3 pixels
        self.x = random.randint(1, SCREEN_WIDTH)  # Random X position
        self.y = random.randint(50, SCREEN_HEIGHT)  # Random Y position
        self.speed = random.uniform(0.03, 0.15)  # Slower speeds for the start screen
        self.color = random.choice(COLOR_OPTIONS)
        
    def move(self):
        self.y -= self.speed  # Move the dot upwards
        if self.y < 0:  # If the dot goes off the screen, reset its position
            self.y = SCREEN_HEIGHT
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        for i in range(2):  # Increase the number of layers for a stronger glow
            glow_size = self.size + i * 1  # Increasing size for each glow layer
            alpha = 255 - i * 1  # Decreasing transparency for each layer (more faded glow)
            glow_color = (*self.color, alpha)  # Add alpha to color for transparency

            # Draw the glow using a larger circle for each layer (with transparency)
            surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, glow_color, (glow_size, glow_size), glow_size)
            screen.blit(surface, (self.x - glow_size, self.y - glow_size), special_flags=pygame.BLEND_RGBA_ADD)

            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)


class GameDot:
    def __init__(self):
        self.size = random.randint(1, 2)  # Random size between 2 and 6 pixels
        self.x = random.randint(1, SCREEN_WIDTH)  # Random X position
        self.y = random.randint(SCREEN_HEIGHT // 50, SCREEN_HEIGHT)  # Random Y position (lower half of the screen)
        self.speed = random.uniform(1.5, 1.5)  # Speed of the dot
        self.color = random.choice(COLOR_OPTIONS)

    def move(self):
        self.y -= self.speed  # Move the dot upwards
        if self.y < 0:  # If the dot goes off the screen, reset its position
            self.y = SCREEN_HEIGHT
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

def is_position_free(x, y):
    for enemy in enemies:
        if enemy["rect"].colliderect(pygame.Rect(x, y, enemy_width, enemy_height)):
            return False  # There's an overlap
    return True  # No overlap

# Function to spawn a new enemy with a random image
def spawn_enemy():
    while True:
        x = random.randint(0, SCREEN_WIDTH - enemy_width)
        y = random.randint(-100, -40)
        if is_position_free(x, y):
            # Select a random image from the enemy_images list
            enemy_image = random.choice(enemy_images)
            # Store both the position and the image in a dictionary
            enemies.append({"rect": pygame.Rect(x, y, enemy_width, enemy_height), "image": enemy_image})
            break  # Exit the loop once a valid position is found

# Function to spawn the boss
def spawn_boss():
    global boss, boss_direction
    if boss is None:  # Only spawn the boss if it doesn't already exist
        boss_x = SCREEN_WIDTH // 2 - 50  # Center the boss
        boss_y = 50  # Position at the top of the screen
        boss = pygame.Rect(boss_x, boss_y, 100, 100)  # Create the boss object
        boss_direction = 1
        boss_health = 100  # Reset boss health to 100 when spawned
        boss_defeated = False

# Boss attack function
def boss_attack():
    global boss_attack_timer, boss_bullets
    if boss:
        boss_attack_timer -= .5
        if boss_attack_timer <= 0:
            boss_bullet = {
                'image': boss_bullet_image,
                'rect': pygame.Rect(boss.centerx - beam_width // 2, boss.bottom, beam_width, beam_height)
            }
            boss_bullets.append(boss_bullet)
            boss_attack_timer = 60  # Reset attack timer    


# Check for boss collisions with bullets and player
def check_boss_collisions():
    global boss_health, boss, AUTO_SHOOT_INTERVAL
    if boss:  # Only check if the boss exists
        for bullet in bullets[:]:
            if boss.colliderect(bullet):  # Bullet hits the boss
                hit_sound.play()
                bullets.remove(bullet)
                boss_health -= 1
                if boss_health <= 0:  # Boss is defeated
                    boss = None
                    AUTO_SHOOT_INTERVAL = 10  # Faster shooting for two bullets
                    return 0  # Bonus points for defeating the boss
    return 0


# Check if the player is hit by any boss bullets
def check_player_hit_by_boss_bullets(player):
    global boss_bullets
    for b_bullet in boss_bullets[:]:
        if player.colliderect(b_bullet['rect']):  # Player hits the boss bullet
            save_high_score(score)
            return True  # Player is hit
    return False


# Function to load the highest score from a file
def load_high_score():
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read().strip())  # Read and return the highest score
    except FileNotFoundError:
        return 0  # Return 0 if no high score file exists

# Function to save the highest score to a file
def save_high_score(score):
    """Save the high score to a file."""
    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0
    
    # Update the high score if necessary
    if score > high_score:
        high_score = score
        with open("high_score.txt", "w") as file:
            file.write(str(high_score))
    
    return high_score

# Pause menu
def display_pause_screen():
    font = pygame.font.Font("operius-regular.ttf", 52)
    pause_text = font.render("PAUSED", True, WHITE)

    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
            
    pygame.display.flip()
    
    

# Starting screen with the highest score
def display_start_screen():
    dots = [StartScreenDot() for _ in range(100)]
            
    font = pygame.font.Font("operius-regular.ttf", 48)
    title_text = font.render("AERIUS FRONTIER", True, WHITE)
    
    high_score = load_high_score()
    font = pygame.font.Font("operius-regular.ttf", 25)
    high_score_text = font.render(f"Highest Score  {high_score}", True, WHITE)
    
    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 60)
    exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 200, 200, 60)


    waiting = True
    clock = pygame.time.Clock()
    
    while waiting:
        screen.fill(BLACK)

        for dot in dots:
            dot.move()
            dot.draw(screen)

        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.draw.rect(screen, GREEN, start_button_rect)
        start_text = font.render("START", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 115))

        pygame.draw.rect(screen, RED, exit_button_rect)
        exit_text = font.render("EXIT", True, WHITE)
        screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 215))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Start game if the Start button is clicked
                if start_button_rect.collidepoint(mouse_x, mouse_y):
                    waiting = False
                    return
                # Exit if the Exit button is clicked
                if exit_button_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()

       
        
# Game over screen with Exit button and highest score
def display_game_over_screen(score):
    font = pygame.font.Font("operius-regular.ttf", 60)
    game_over_text = font.render("GAME OVER!", True, WHITE)
    
    font = pygame.font.Font("operius-regular.ttf", 23)
    score_text = font.render(f"Score: {score}", True, WHITE)

    # Load highest score
    high_score = load_high_score()
    high_score_text = font.render(f"Highest Score: {high_score}", True, WHITE)
    
    screen.fill(BLACK)
    # Display game over text
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                 SCREEN_HEIGHT // 3 - game_over_text.get_height() // 2))
    # Display score
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                             SCREEN_HEIGHT // 2 - 10))

    # Display highest score
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2,
                                  SCREEN_HEIGHT // 2 + 40))

    # Create Exit button
    exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, 200, 60)
    pygame.draw.rect(screen, RED, exit_button_rect)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 + 165))
    
    pygame.display.flip()

    # Wait for user input (Exit)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check if the user clicked the exit button
                if exit_button_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()

boss_defeated_timer = 0

# Main game loop
def game_loop():
    global player_x, player_y, auto_shoot_timer, paused, boss_defeated_timer, passed_enemies, booster, MAX_PASSED_ENEMIES, player_speed, boost_duration, AUTO_SHOOT_INTERVAL, boss, boss_bullets, boss_health, boss_direction, boss_defeated, score, enemies
    running = True
    score = 0
    high_score = save_high_score(0)

    boss_spawned_100 = False
    boss_spawned_250 = False
    boss_spawned_500 = False
    dots = [GameDot() for _ in range(100)]
    # Spawn initial enemies
    for _ in range(5):
        spawn_enemy()

    while running:
        screen.fill(BLACK)
        boss_attack()
        # Handle events
        if boss_defeated:
            boss_defeated_timer = 100

        if AUTO_SHOOT_INTERVAL == 10 and boss_defeated_timer > 0:
            pass

        if boss_defeated_timer > 0:
            boss_defeated_timer -= 1
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Toggle pause with ESC
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

        for dot in dots:
            dot.move()
            dot.draw(screen)
            
        if paused:
            display_pause_screen()
            continue

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < SCREEN_HEIGHT - player_height:
            player_y += player_speed

        # Boost duration countdown
        if boost_duration > 0:
            boost_duration -= 1 / FPS
            if boost_duration <= 0:
                player_speed = normal_player_speed
                AUTO_SHOOT_INTERVAL = normal_shoot_interval

        # Automatic shooting logic
        auto_shoot_timer -= 1.8
        if auto_shoot_timer <= 0:
            # Single bullet
            bullet1 = pygame.Rect(
                player_x + player_width // 2 - bullet_width // 2 - 10,
                player_y,
                bullet_width,
                bullet_height,
            )
            # Second bullet slightly offset
            bullet2 = pygame.Rect(
                player_x + player_width // 2 - bullet_width // 2 + 10,
                player_y,
                bullet_width,
                bullet_height,
            )
            
            bullets.append(bullet1)
            bullets.append(bullet2)
            shoot_sound.play()  # Play the shooting sound
            auto_shoot_timer = AUTO_SHOOT_INTERVAL


        # Bullet movement
        for bullet in bullets[:]:
            bullet.y -= bullet_speed  # Bullets move upwards
            if bullet.y < 0:
                bullets.remove(bullet)
            screen.blit(bullet_image, (bullet.x, bullet.y))

        # Player rectangle
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        screen.blit(player_image, (player_x, player_y)) 

       

        # Enemy movement and collision detection
        for enemy in enemies[:]:
            enemy["rect"].y += enemy_speed  # Move enemy down
            
            if enemy["rect"].y > SCREEN_HEIGHT:
                if enemy in enemies:
                    enemies.remove(enemy)
                spawn_enemy()
                passed_enemies += 1

            if enemy["rect"].colliderect(player_rect):
                if enemy in enemies:
                    enemies.remove(enemy)
                    save_high_score(score)
                    display_game_over_screen(score)
                
            if passed_enemies > MAX_PASSED_ENEMIES:
                if enemy in enemies:
                    enemies.remove(enemy)
                    display_game_over_screen(score)

            for bullet in bullets [:]:
                if enemy["rect"].colliderect(bullet):
                    hit_sound.play()
                    if enemy in enemies:
                        enemies.remove(enemy)
                        spawn_enemy()
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 1
                

            # Draw the enemy with its random image
            screen.blit(enemy["image"], (enemy["rect"].x, enemy["rect"].y))

            
        if score >= 100 and not boss_spawned_100:
            spawn_boss()
            boss_spawned_100 = True  # Set flag to prevent spawning again
        if score >= 250 and not boss_spawned_250:
            spawn_boss()
            boss_health = 150
            boss_spawned_250 = True  # Set flag to prevent spawning again
        if score >= 500 and not boss_spawned_500:
            spawn_boss()
            boss_health = 200
            boss_spawned_500 = True
            
        # Boss logic
        if boss:
            screen.blit(boss_image, (boss.x, boss.y))
            boss.x += boss_speed * boss_direction
            if boss.left <= 0 or boss.right >= SCREEN_WIDTH:
                boss_direction *= -1  # Reverse direction
            check_boss_collisions()
            boss_attack()

            if boss_health <= 0 and not boss_defeated:
                score += 50
                passed_enemies = max(0, passed_enemies - 10)
                boss = None
                boss_bullets.clear()
                boss_defeated = True

            if boss:
                screen.blit(boss_image, (boss.x, boss.y))  # Draw boss image first
                # Draw health bar
                boss_health_bar_width = 200
                current_bar_width = int(boss_health_bar_width * (boss_health / 100))
                health_bar = pygame.Rect((SCREEN_WIDTH - boss_health_bar_width) // 2, 30, current_bar_width, 10)
                font = pygame.font.Font("operius-regular.ttf", 15)
                boss_text = font.render(f"BOSS", True, RED)
                screen.blit(boss_text, (366, 8))
                pygame.draw.rect(screen, GREEN, health_bar)
                pygame.draw.rect(screen, WHITE, health_bar, 2)


            for bullet in boss_bullets[:]:  # Use a copy of the list to avoid modification while iterating
                # Draw the boss bullet image at the current position
                screen.blit(bullet['image'], bullet['rect'])

                # Update bullet position (move downwards)
                bullet['rect'].y += 2

                # Remove bullets that go off-screen
                if bullet['rect'].y > screen.get_height():
                    boss_bullets.remove(bullet)

        # Spawn booster
        if booster is None and random.random() < booster_spawn_chance:  # Ensure only one booster can be on screen at a time
            booster_x = random.randint(0, SCREEN_WIDTH - booster_width)
            booster_y = random.randint(-100, -40)
            booster = pygame.Rect(booster_x, booster_y, booster_width, booster_height)

        # Update booster position and render it
        if booster:
            booster.y += booster_speed
            screen.blit(booster_image, (booster.x, booster.y))
            if booster.colliderect(player_rect):  # Check for collision with player
                booster_sound.play()
                passed_enemies = max(0, passed_enemies - 5)
                boost_duration = 3.5
                player_speed = boosted_player_speed
                AUTO_SHOOT_INTERVAL = boosted_shoot_interval
                booster = None


        # Check if the player is hit by boss bullets
        if check_player_hit_by_boss_bullets(player_rect):
            display_game_over_screen(score)

        # Display score
        font = pygame.font.Font("operius-regular.ttf", 14)
        score_text = font.render(f"SCORE", True, GREEN)
        scorecount_text = font.render(f"{score}", True, WHITE)
        passed_enemies_text = font.render(f"ENEMIES PASSED", True, RED)
        passed_e_count_text = font.render(f"{passed_enemies} / {MAX_PASSED_ENEMIES}", True, WHITE)
        high_score_text = font.render(f"HIGHEST SCORE {high_score}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(scorecount_text, (100, 10))
        screen.blit(passed_enemies_text, (10, 40))
        screen.blit(passed_e_count_text, (10, 60))
        screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))
        
        pygame.display.update()
        clock.tick(FPS)

# Main execution starts here
display_start_screen()
game_loop()
