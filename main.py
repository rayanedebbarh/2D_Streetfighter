import pygame
from pygame import mixer
import random
from fighter import Fighter

mixer.init()
pygame.init()

# Create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Street Fight")

# Set framerate
clock = pygame.time.Clock()
FPS = 60

# Define colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define game variables
intro_count = 4
last_count_update = pygame.time.get_ticks()
score = [0, 0]  # player scores. [P1, P2]
round_over = False
ROUND_OVER_COOLDOWN = 2000
paused = False  # Variable to track the pause state
round_number = 1  # Current round number
round_wins = [0, 0]  # Number of rounds won by each player
round_display_time = 4000  # Time to display the round text (in milliseconds)
round_start_displayed = False  # Flag to control the display of round start text

# Define fighter variables
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

# Load music and sounds
pygame.mixer.music.load("assets/audio/music1.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)

# Load background images for each round
bg_images = [
    pygame.image.load("assets/images/background/background1.jpg").convert_alpha(),
    pygame.image.load("assets/images/background/background2.jpg").convert_alpha(),
    pygame.image.load("assets/images/background/background3.jpg").convert_alpha()
]

# Load spritesheets
warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()

# Load victory image
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

# Load and resize the pause icon image
pause_img = pygame.image.load("assets/images/icons/pause.png").convert_alpha()
pause_img = pygame.transform.scale(pause_img, (100, 100))  # Resize the image to 100x100 pixels

# Load bird images
bird_images = [
    pygame.image.load("assets/images/icons/bird1.png").convert_alpha(),
    pygame.image.load("assets/images/icons/bird2.png").convert_alpha(),
    pygame.image.load("assets/images/icons/bird3.png").convert_alpha()
]

# Define number of steps in each animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

# Define font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

# Function for drawing text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for drawing background
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_images[round_number - 1], (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

# Function for drawing fighter health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

# Create two instances of fighters
fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

# Initialize variables for welcome screen
round_start_time = pygame.time.get_ticks()  # Get the current time
round_counter = 0
show_round_text = True  # Flag to control the display of the round text
show_welcome_screen = True  # Flag to control the display of the welcome screen
welcome_timer = 0  # Timer for the welcome screen

# Load the welcome image
welcome_image = pygame.image.load("welcome.jpg").convert_alpha()

# Bird class to handle bird properties and movement
class Bird:
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (50, 50))
        self.x = x
        self.y = y
        self.speed = random.randint(1, 3)  # Random speed

    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH:
            self.x = -50  # Reset to the left side

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Create birds
birds = []
for _ in range(20):  # Create 20 birds
    bird_image = random.choice(bird_images)
    x = random.randint(-1000, 0)  # Random starting position
    y = random.randint(50, 300)  # Random height
    birds.append(Bird(x, y, bird_image))

# Main game loop
run = True
while run:
    if show_welcome_screen:
        # Display the welcome screen
        screen.blit(welcome_image, (0, 0))  # Blit the image onto the screen

        # Calculate text dimensions
        welcome_text = "Welcome:"
        start_text = "Press Enter"
        done_by_text = ["Done by:", "-Rayane", "-Hiba", "-Tyler"]  # New text to display
        welcome_text_width, welcome_text_height = count_font.size(welcome_text)
        start_text_width, start_text_height = count_font.size(start_text)

        # Draw "Welcome:" and "Press Enter" with blinking effect
        if show_round_text:
            draw_text(welcome_text, count_font, RED, (SCREEN_WIDTH - welcome_text_width) / 2,
                      (SCREEN_HEIGHT - welcome_text_height) / 2 - 40)
            draw_text(start_text, count_font, RED, (SCREEN_WIDTH - start_text_width) / 2,
                      (SCREEN_HEIGHT - start_text_height) / 2 + 20)

        # Always draw the "Done by" text in the upper right corner
        x_offset = SCREEN_WIDTH - 320  # Move the text 20 pixels to the left
        y_offset = 20
        for line in done_by_text:
            draw_text(line, score_font, BLACK, x_offset, y_offset)
            y_offset += 30  # Adjust y_offset for the next line

        # Toggle the visibility of the "Welcome" and "Press Enter" text every second
        welcome_timer += clock.tick(FPS)
        if welcome_timer >= 2000:
            show_round_text = not show_round_text
            welcome_timer = 0

        # Check for events to start the game
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    show_welcome_screen = False
                    round_start_displayed = True  # Display the round start text
                    round_start_time = pygame.time.get_ticks()
            elif event.type == pygame.QUIT:
                run = False

    else:
        clock.tick(FPS)

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused  # Toggle pause state
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

        if not paused:
            # Draw background
            draw_bg()

            # Update and draw birds
            for bird in birds:
                bird.update()
                bird.draw()

            if round_start_displayed:
                # Display round start text
                round_text = f"Round {round_number}"
                round_text_width, round_text_height = count_font.size(round_text)
                draw_text(round_text, count_font, RED, (SCREEN_WIDTH - round_text_width) / 2, (SCREEN_HEIGHT - round_text_height) / 2)
                if pygame.time.get_ticks() - round_start_time >= round_display_time:
                    round_start_displayed = False
            else:
                # Show player stats
                draw_health_bar(fighter_1.health, 20, 20)
                draw_health_bar(fighter_2.health, 580, 20)
                draw_text("The Witcher: " + str(score[0]), score_font, RED, 20, 60)
                draw_text("Wizard: " + str(score[1]), score_font, RED, 580, 60)

                # Update countdown
                if intro_count <= 0:
                    # Move fighters
                    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
                    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
                else:
                    # Display count timer
                    draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
                    # Update count timer
                    if (pygame.time.get_ticks() - last_count_update) >= 1000:
                        intro_count -= 1
                        last_count_update = pygame.time.get_ticks()

                # Update fighters
                fighter_1.update()
                fighter_2.update()

                # Draw fighters
                fighter_1.draw(screen)
                fighter_2.draw(screen)

                # Check for player defeat
                if not round_over:
                    if not fighter_1.alive:
                        score[1] += 1
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                        round_wins[1] += 1
                    elif not fighter_2.alive:
                        score[0] += 1
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                        round_wins[0] += 1
                else:
                    # Display victory image
                    screen.blit(victory_img, (360, 150))
                    if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                        if round_number < 3:
                            round_number += 1
                            round_start_displayed = True
                            round_start_time = pygame.time.get_ticks()
                            round_over = False
                            intro_count = 3
                            fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                            fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                        else:
                            # Determine the winner
                            if round_wins[0] > round_wins[1]:
                                winner_text = "The Witcher Wins!"
                            elif round_wins[1] > round_wins[0]:
                                winner_text = "Wizard Wins!"
                            else:
                                winner_text = "It's a Draw!"
                            winner_text_width, winner_text_height = count_font.size(winner_text)
                            draw_text(winner_text, count_font, RED, (SCREEN_WIDTH - winner_text_width) / 2, SCREEN_HEIGHT / 3)
                            pygame.display.update()
                            pygame.time.wait(5000)
                            run = False  # End the game after displaying the winner
        else:
            # Draw pause icon
            screen.blit(pause_img, ((SCREEN_WIDTH - pause_img.get_width()) // 2, (SCREEN_HEIGHT - pause_img.get_height()) // 2))

    # Update display
    pygame.display.update()

# Exit pygame
pygame.quit()
