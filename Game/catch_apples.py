import pygame
import random
import os
import sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Apple")

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
RED = (255, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
BUTTON_COLOR = (50, 150, 50)
HEART_COLOR = (255, 105, 180)
RESTART_COLOR = (70, 130, 180)

# Game settings
GRAVITY = 0.05
INITIAL_SPEED = 0.8
TERMINAL_VELOCITY = 3
MAX_APPLES = 5
LIVES = 3

# High score file
HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as file:
        file.write(str(score))

def draw_heartbroken(surface, size=60):
    """Draw a heartbroken emoji"""
    pygame.draw.circle(surface, HEART_COLOR, (size//3, size//3), size//4)
    pygame.draw.circle(surface, HEART_COLOR, (2*size//3, size//3), size//4)
    points = [
        (size//6, size//3),
        (size//2, size),
        (5*size//6, size//3)
    ]
    pygame.draw.polygon(surface, HEART_COLOR, points)
    pygame.draw.line(surface, BLACK, (size//3, size//3), (2*size//3, 2*size//3), 3)

def draw_restart(surface, size=40):
    """Draw a restart arrow emoji"""
    pygame.draw.circle(surface, RESTART_COLOR, (size//2, size//2), size//2 - 5, 2)
    points = [
        (size//2, size//4),
        (3*size//4, size//2),
        (size//2, 3*size//4),
        (size//2, size//2 + 5)
    ]
    pygame.draw.polygon(surface, WHITE, points)

def load_and_scale_image(name, max_width=None):
    """Load images or create fallback surfaces"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_path, "assets", "images", name)
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            if max_width and img.get_width() > max_width:
                scale = max_width / img.get_width()
                new_height = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (max_width, new_height))
            return img
    except Exception as e:
        print(f"Error loading {name}: {e}")

    size = max_width if max_width else 60
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    if name == "apple.png":
        pygame.draw.circle(surface, RED, (size//2, size//2), size//2)
        pygame.draw.circle(surface, (255, 200, 200), (size//3, size//3), size//6)
    elif name == "basket.png":
        pygame.draw.ellipse(surface, BROWN, (0, 0, size, size//2))
        pygame.draw.ellipse(surface, BLACK, (0, 0, size, size//2), 2)
    elif name == "heart_broken.png":
        draw_heartbroken(surface, size)
    elif name == "restart.png":
        draw_restart(surface, size)
    
    return surface

def draw_button(surface, color, x, y, width, height, text, text_color=WHITE):
    """Draw a button with text"""
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, button_rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=10)
    
    font = pygame.font.SysFont('Arial', 32)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=button_rect.center)
    surface.blit(text_surf, text_rect)
    
    return button_rect

def show_main_menu():
    """Display the main menu screen"""
    title_font = pygame.font.SysFont('Arial', 72, bold=True)
    subtitle_font = pygame.font.SysFont('Arial', 24)
    
    title = title_font.render("CATCH THE APPLE", True, GRASS_GREEN)
    subtitle = subtitle_font.render("A relaxing fruit-catching game", True, BLACK)
    
    logo = load_and_scale_image("apple.png", 100)
    logo_rect = logo.get_rect(center=(WIDTH//2, HEIGHT//3 + 50))
    
    while True:
        screen.fill(LIGHT_BLUE)
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT-50, WIDTH, 50))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 180))
        screen.blit(logo, logo_rect)
        
        play_button = draw_button(screen, BUTTON_COLOR, WIDTH//2-100, HEIGHT//2, 200, 50, "PLAY")
        quit_button = draw_button(screen, BUTTON_COLOR, WIDTH//2-100, HEIGHT//2+70, 200, 50, "QUIT")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button.collidepoint(mouse_pos):
                    return True
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()

class Apple:
    def __init__(self):
        self.original_image = load_and_scale_image("apple.png", 60)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.reset_position()
        self.rotation = 0
    
    def reset_position(self):
        self.rect.x = random.randint(0, max(1, WIDTH - self.rect.width))
        self.rect.y = -self.rect.height
        self.speed_y = INITIAL_SPEED * random.uniform(0.7, 1.0)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.time = 0
    
    def update(self):
        self.speed_y = min(self.speed_y + GRAVITY, TERMINAL_VELOCITY)
        self.time += 0.02
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        self.rotation += 0.5 * (1 if self.speed_x > 0 else -1)
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
    
    def draw(self):
        screen.blit(self.image, self.rect)

class Basket:
    def __init__(self):
        self.image = load_and_scale_image("basket.png", 150)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2 - self.rect.width // 2
        self.rect.y = HEIGHT - self.rect.height - 30
        self.speed = 6
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
    
    def draw(self):
        screen.blit(self.image, self.rect)

def draw_grass():
    """Draw grass with stable green color"""
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 40, WIDTH, 40))
    for x in range(0, WIDTH, 4):
        blade_h = random.randint(5, 15)
        pygame.draw.line(screen, (0, 100, 0), 
                        (x, HEIGHT - 40), 
                        (x, HEIGHT - 40 - blade_h), 
                        2)

def run_game():
    basket = Basket()
    apples = []
    score = 0
    lives = LIVES
    game_over = False
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 32)
    last_apple_time = 0
    high_score = load_high_score()
    
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        if not game_over:
            if len(apples) < MAX_APPLES and current_time - last_apple_time > 1500:
                apples.append(Apple())
                last_apple_time = current_time
            
            basket.update()
            for apple in apples[:]:
                apple.update()
                
                if apple.rect.colliderect(basket.rect):
                    apples.remove(apple)
                    score += 1
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                elif apple.rect.top > HEIGHT:
                    apples.remove(apple)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
        
        screen.fill(SKY_BLUE)
        draw_grass()
        
        for apple in apples:
            apple.draw()
        
        basket.draw()
        
        score_text = font.render(f"Score: {score}", True, BLACK)
        lives_text = font.render(f"Lives: {lives}", True, BLACK)
        high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (WIDTH - 150, 20))
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, 20))
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            font_large = pygame.font.SysFont('Arial', 48)
            game_over_text = font_large.render("GAME OVER", True, WHITE)
            heartbroken_img = load_and_scale_image("heart_broken.png", 60)
            
            game_over_x = WIDTH//2 - (game_over_text.get_width() + heartbroken_img.get_width() + 10)//2
            screen.blit(game_over_text, (game_over_x, HEIGHT//2 - 100))
            screen.blit(heartbroken_img, (game_over_x + game_over_text.get_width() + 10, HEIGHT//2 - 100))
            
            score_text = font.render(f"Your Score: {score}", True, WHITE)
            high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))
            screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 10))
            
            restart_text = font.render("Press R to restart", True, WHITE)
            restart_img = load_and_scale_image("restart.png", 40)
            restart_x = WIDTH//2 - (restart_text.get_width() + restart_img.get_width() + 10)//2
            screen.blit(restart_text, (restart_x, HEIGHT//2 + 70))
            screen.blit(restart_img, (restart_x + restart_text.get_width() + 10, HEIGHT//2 + 70))
            
            menu_text = font.render("ESC for Main Menu", True, WHITE)
            screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 120))
        
        pygame.display.flip()
        clock.tick(60)

def main():
    while True:
        if show_main_menu():
            while run_game():
                pass
        else:
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


