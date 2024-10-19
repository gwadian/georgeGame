import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 1075, 683
PLAYER_SIZE = 35
ROCK_SIZE = 35
ROCK_SHOOT_COOLDOWN = 40
BULLET_SIZE = 15
FPS = 100
ROCK_FALL_SPEED = 3
ROCK_SPAWN_INTERVAL = 25  # Number of frames between rock spawns
BULLET_SPEED = 10
BULLET_COOLDOWN = 0.2  # seconds
MAX_HITS = 10  # Number of hits before game over
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_COLOR = (0, 0, 255)  # Blue for health bar
HEALTH_BAR_BG_COLOR = (100, 100, 100)  # Gray for background of health
BG_COLOR = (0, 0, 0)  # Black for the sky

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keplar defense")
# Initialize clock
clock = pygame.time.Clock()

# Load textures
player_image = pygame.image.load('playerTexture.png')
rock_image = pygame.image.load('rockTexture.png')
bullet_image = pygame.image.load('ammoTexture.png')

# Resize images to appropriate sizes
player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
rock_image = pygame.transform.scale(rock_image, (ROCK_SIZE, ROCK_SIZE))
bullet_image = pygame.transform.scale(bullet_image, (BULLET_SIZE, BULLET_SIZE))

# Player
player_pos = [WIDTH // 8 - PLAYER_SIZE // 8, HEIGHT - PLAYER_SIZE]
player_speed = 6

# Rocks
rocks = []
rock_timer = 0

# Bullets
bullets = []
last_bullet_time = time.time()

# Rock Shots
rock_shots = []

# Health
player_health = MAX_HITS  # Start with maximum health

# Score
score = 0  # Initialize score

# Game states
in_game = False
show_game_over_message = False  # Control the display of the game over message
final_score = 0  # Variable to keep the final score


def draw_player():
    screen.blit(player_image, player_pos)  # Draw the player image


def draw_rocks():
    for rock in rocks:
        screen.blit(rock_image, rock['pos'])  # Draw the rock image


def draw_bullets():
    for bullet in bullets:
        screen.blit(bullet_image, bullet['pos'])  # Draw the bullet image


def draw_rock_shots():
    for shot in rock_shots:
        screen.blit(bullet_image, shot['pos'])  # Draw the rock shot image


def draw_health_bar():
    # Draw health bar background
    pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, (10, 10, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
    # Calculate health bar fill width
    fill_width = (HEALTH_BAR_WIDTH * player_health) / MAX_HITS
    # Draw health bar fill
    pygame.draw.rect(screen, HEALTH_BAR_COLOR, (10, 10, fill_width, HEALTH_BAR_HEIGHT))


def draw_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))  # Top right corner


def handle_input():
    global last_bullet_time, in_game
    keys = pygame.key.get_pressed()
    if in_game:
        if keys[pygame.K_a]:
            player_pos[0] -= player_speed
        if keys[pygame.K_d]:
            player_pos[0] += player_speed
        if keys[pygame.K_s]:
            current_time = time.time()
            if current_time - last_bullet_time >= BULLET_COOLDOWN:
                shoot_bullet()
                last_bullet_time = current_time

        # Ensure player stays within bounds
        player_pos[0] = max(0, min(WIDTH - PLAYER_SIZE, player_pos[0]))
    else:
        if keys[pygame.K_SPACE]:
            start_game()  # Start game when SPACE is pressed


def shoot_bullet():
    bullet_x = player_pos[0] + PLAYER_SIZE // 2 - BULLET_SIZE // 2
    bullet_y = player_pos[1] - BULLET_SIZE
    bullets.append({'pos': [bullet_x, bullet_y]})


def update_rocks():
    global rocks
    for rock in rocks:
        rock['pos'][1] += ROCK_FALL_SPEED
    rocks = [rock for rock in rocks if rock['pos'][1] < HEIGHT]


def update_bullets():
    global bullets
    for bullet in bullets:
        bullet['pos'][1] -= BULLET_SPEED
    bullets = [bullet for bullet in bullets if bullet['pos'][1] > -BULLET_SIZE]


def update_rock_shots():
    global rock_shots
    for shot in rock_shots:
        shot['pos'][1] += BULLET_SPEED
    rock_shots = [shot for shot in rock_shots if shot['pos'][1] < HEIGHT]


def check_bullet_rock_collisions():
    global rocks, bullets, score
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(*bullet['pos'], BULLET_SIZE, BULLET_SIZE)
        for rock in rocks[:]:
            rock_rect = pygame.Rect(*rock['pos'], ROCK_SIZE, ROCK_SIZE)
            if bullet_rect.colliderect(rock_rect):
                score += 1  # Increment score on hit
                bullets.remove(bullet)
                rocks.remove(rock)  # Remove the rock on hit
                break  # Exit the inner loop since we removed the rock


def check_rock_shot_collisions():
    global rock_shots, player_health
    for shot in rock_shots[:]:
        shot_rect = pygame.Rect(*shot['pos'], BULLET_SIZE, BULLET_SIZE)
        player_rect = pygame.Rect(*player_pos, PLAYER_SIZE, PLAYER_SIZE)
        if shot_rect.colliderect(player_rect):
            rock_shots.remove(shot)
            player_health -= 1
            if player_health <= 0:
                game_over()
            break


def check_player_rock_collisions():
    player_rect = pygame.Rect(*player_pos, PLAYER_SIZE, PLAYER_SIZE)
    for rock in rocks:
        rock_rect = pygame.Rect(*rock['pos'], ROCK_SIZE, ROCK_SIZE)
        if player_rect.colliderect(rock_rect):
            return True
    return False


def spawn_rock():
    x_pos = random.randint(0, WIDTH - ROCK_SIZE)
    rocks.append({'pos': [x_pos, -ROCK_SIZE]})


def rock_shoot():
    current_time = time.time()
    for rock in rocks:
        if current_time - rock.get('last_shot_time', 0) >= ROCK_SHOOT_COOLDOWN:
            rock_x = rock['pos'][0] + ROCK_SIZE // 2 - BULLET_SIZE // 2
            rock_y = rock['pos'][1] + ROCK_SIZE
            rock_shots.append({'pos': [rock_x, rock_y]})
            rock['last_shot_time'] = current_time


def game_over():
    global player_health, score, rocks, rock_shots, in_game, show_game_over_message, final_score

    show_game_over_message = True  # Show game over message
    player_health = MAX_HITS  # Reset health
    rocks.clear()  # Clear rocks
    rock_shots.clear()  # Clear rock shots
    in_game = False  # Return to lobby
    final_score = score  # Save the final score


def start_game():
    global in_game, score, player_health
    in_game = True  # Set game state to in-game
    score = 0  # Reset score
    player_health = MAX_HITS  # Reset health
    rocks.clear()  # Clear any existing rocks
    rock_shots.clear()  # Clear any existing rock shots


def display_lobby():
    global show_game_over_message  # Ensure we are using the global variable
    screen.fill(BG_COLOR)
    font = pygame.font.SysFont(None, 55)
    title_text = font.render('Press SPACE to Start', True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2))

    # Reset the game over message when displaying the lobby
    show_game_over_message = False  # Reset death message

    # Display game over message if needed
    if show_game_over_message:
        game_over_text = font.render('HEALTH CRITICAL, RETURNING TO HANGAR.', True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 + 30))

    # Display the score in the top right corner
    score_text = font.render(f'Score: {final_score}', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))  # Top right corner

    pygame.display.flip()


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_input()

    if in_game:
        rock_timer += 1
        if rock_timer >= ROCK_SPAWN_INTERVAL:
            spawn_rock()
            rock_timer = 0

        update_rocks()
        update_bullets()
        update_rock_shots()
        rock_shoot()

        check_bullet_rock_collisions()
        check_rock_shot_collisions()
        if check_player_rock_collisions():
            game_over()

        screen.fill(BG_COLOR)
        draw_rocks()
        draw_bullets()
        draw_rock_shots()
        draw_player()
        draw_health_bar()
        draw_score()  # Draw the score
    else:
        display_lobby()  # Display the lobby

    pygame.display.flip()
    clock.tick(FPS)
