import pygame
import random
import sys

# Game Dimensions & Configurations
width, height = 480, 700
fps = 60
lanes = 3
lane_padding = 60
player_width, player_height = 50, 90
enemy_width, enemy_height = 50, 90
base_enemy_speed = 6
spawn_interval = 900
difficulty_increase_rate = 0.015

# Colors
white = (255, 255, 255)
gray = (35, 35, 35)
dark_gray = (25, 25, 25)
green = (40, 170, 40)
red = (220, 40, 40)
yellow = (240, 220, 40)
blue = (66, 135, 245)
brown = (110, 70, 40)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Car crash dash")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)

lane_width = (width - 2 * lane_padding) / lanes
lanee_centers = [int(lane_padding + lane_width * i + lane_width / 2) for i in range(lanes)]


class Player:
    def __init__(self):
        self.lane = lanes // 2
        self.rect = pygame.Rect(0, 0, player_width, player_height)
        self.rect.centerx = lanee_centers[self.lane]
        self.rect.bottom = height - 50
        self.color = blue
        self.alive = True

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.rect.centerx = lanee_centers[self.lane]

    def move_right(self):
        if self.lane < lanes - 1:
            self.lane += 1
            self.rect.centerx = lanee_centers[self.lane]

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= 6
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += 6

        # Limit player within designated vertical boundaries
        if self.rect.top < 100:
            self.rect.top = 100
        if self.rect.bottom > height - 30:
            self.rect.bottom = height - 30

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=8)
        # Windshield
        wind_rect = pygame.Rect(0, 0, self.rect.width * 0.6, self.rect.height * 0.2)
        wind_rect.centerx = self.rect.centerx
        wind_rect.centery = self.rect.centery - 15
        pygame.draw.rect(surf, (200, 230, 255), wind_rect, border_radius=4)


class Enemy:
    def __init__(self, lane, speed):
        self.lane = lane
        self.speed = speed
        self.rect = pygame.Rect(0, -enemy_height, enemy_width, enemy_height)
        self.rect.centerx = lanee_centers[self.lane]
        self.color = random.choice([red, yellow, (200, 60, 200)])
        self.rect.x += random.randint(-6, 6)

    def update(self, dt):
        self.rect.y += self.speed * dt

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
        bumper = pygame.Rect(self.rect.left + 8, self.rect.top + 8, self.rect.width - 16, 8)
        pygame.draw.rect(surf, dark_gray, bumper, border_radius=4)


class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(25, 40)
        self.color_left = green
        self.color_trunk = brown

    def update(self, speed):
        self.y += speed
        if self.y > height + 50:
            self.y = random.randint(-100, -40)
            self.x = random.choice([
                random.randint(10, lane_padding - 25),
                random.randint(width - lane_padding + 10, width - 40)
            ])
            self.size = random.randint(25, 40)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_trunk, (self.x + self.size // 2 - 4, self.y + self.size, 8, 15))
        pygame.draw.circle(surf, self.color_left, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)


def create_trees():
    trees = []
    for _ in range(5):
        y = random.randint(0, height)
        x = random.randint(10, lane_padding - 25)
        trees.append(Tree(x, y))
    for _ in range(5):
        y = random.randint(0, height)
        x = random.randint(width - lane_padding + 10, width - 40)
        trees.append(Tree(x, y))
    return trees


def draw_road(surface):
    surface.fill(gray)
    pygame.draw.rect(surface, dark_gray, (lane_padding - 20, 0, width - 2 * (lane_padding - 20), height))
    marker_h = 40
    marker_w = 6
    space = 30
    for i in range(1, lanes):
        x = int(lane_padding + lane_width * i)
        y = 20
        while y < height:
            pygame.draw.rect(surface, white, (x - marker_w // 2, y, marker_w, marker_h), border_radius=3)
            y += marker_h + space


def draw_ui(surface, score, high_score):
    score_surf = font.render(f"Score: {int(score)}", True, white)
    hs_surf = font.render(f"Best: {int(high_score)}", True, white)
    surface.blit(score_surf, (12, 10))
    surface.blit(hs_surf, (width - hs_surf.get_width() - 12, 10))


def game_over_screen(surface, score, high_score):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (0, 0))
    text = big_font.render("CRASH!", True, red)
    sub = font.render(f"Score: {int(score)}  Best: {int(high_score)}", True, white)
    hint = font.render("Press R to Restart | ESC to Quit", True, white)
    surface.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 70))
    surface.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 - 10))
    surface.blit(hint, (width // 2 - hint.get_width() // 2, height // 2 + 40))


def main():
    player = Player()
    enemies = []
    trees = create_trees()
    running = True
    last_spawn = pygame.time.get_ticks()
    current_spawn_interval = spawn_interval
    enemy_speed = base_enemy_speed
    tree_scroll_speed = 3
    score = 0.0
    high_score = 0.0
    crashed = False

    while running:
        dt = clock.tick(fps) / 16.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) and not crashed:
                    player.move_left()
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and not crashed:
                    player.move_right()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and crashed:
                    player = Player()
                    enemies = []
                    trees = create_trees()
                    score = 0.0
                    enemy_speed = base_enemy_speed
                    current_spawn_interval = spawn_interval
                    crashed = False
                    last_spawn = pygame.time.get_ticks()

        if not crashed:
            player.update()
            
            for t in trees:
                t.update(tree_scroll_speed)

            # Spawn enemies logic
            now = pygame.time.get_ticks()
            if now - last_spawn >= current_spawn_interval:
                lane = random.randrange(0, lanes)
                enemies.append(Enemy(lane, enemy_speed))
                last_spawn = now

            for e in enemies:
                e.update(dt)

            # Clean off-screen enemies
            enemies = [e for e in enemies if e.rect.top <= height + 50]

            # Collision Check
            for e in enemies:
                if player.rect.colliderect(e.rect):
                    crashed = True
                    player.alive = False
                    if score > high_score:
                        high_score = score
                    break

            # Scoring and progression update
            score += 0.1 * dt * (1 + enemy_speed / 10.0)
            enemy_speed = base_enemy_speed + score * difficulty_increase_rate
            current_spawn_interval = max(300, spawn_interval - int(score * 4))

        # Drawing Routine
        draw_road(screen)
        for t in trees:
            t.draw(screen)
        for e in enemies:
            e.draw(screen)
        player.draw(screen)
        draw_ui(screen, score, high_score)
        
        if crashed:
            game_over_screen(screen, score, high_score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    
