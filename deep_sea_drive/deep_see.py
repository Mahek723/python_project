mport pygame
import random
import sys

# Game Dimensions & Configurations
width, height = 480, 700
fps = 60
player_width, player_height = 60, 40
obstacle_width, obstacle_height = 40, 50
item_width, item_height = 35, 30

base_speed = 4
spawn_interval = 800  # ms
difficulty_increase_rate = 0.15

# Colors (Ocean Theme)
ocean_blue = (10, 40, 95)
water_light = (20, 75, 160)
sand_yellow = (210, 180, 120)
sub_yellow = (240, 200, 20)
sub_window = (100, 220, 255)
anchor_gray = (70, 75, 80)
gold = (255, 215, 0)
white = (255, 255, 255)
red = (220, 40, 40)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Deep Sea Diver")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)


class Submarine:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, player_width, player_height)
        self.rect.centerx = width // 2
        self.rect.bottom = height - 80
        self.speed = 6

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Bound within screen edges
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width

    def draw(self, surf):
        # Submarine Body
        pygame.draw.ellipse(surf, sub_yellow, self.rect)
        # Propeller / Tail
        tail_rect = pygame.Rect(self.rect.right - 8, self.rect.centery - 10, 8, 20)
        pygame.draw.rect(surf, sub_yellow, tail_rect, border_radius=3)
        # Windows
        win_center = (self.rect.centerx - 10, self.rect.centery)
        pygame.draw.circle(surf, sub_window, win_center, 6)
        win_center2 = (self.rect.centerx + 10, self.rect.centery)
        pygame.draw.circle(surf, sub_window, win_center2, 6)


class Anchor:
    def __init__(self, speed):
        self.rect = pygame.Rect(random.randint(20, width - 20 - obstacle_width), -obstacle_height, obstacle_width, obstacle_height)
        self.speed = speed

    def update(self, dt):
        self.rect.y += self.speed * dt

    def draw(self, surf):
        # Anchor Top Ring
        pygame.draw.circle(surf, anchor_gray, (self.rect.centerx, self.rect.top + 10), 10, 4)
        # Anchor Shank (Vertical bar)
        pygame.draw.rect(surf, anchor_gray, (self.rect.centerx - 4, self.rect.top + 10, 8, 30))
        # Anchor Flukes (Horizontal curved base)
        pygame.draw.rect(surf, anchor_gray, (self.rect.left, self.rect.bottom - 12, self.rect.width, 8), border_radius=4)


class Treasure:
    def __init__(self, speed):
        self.rect = pygame.Rect(random.randint(20, width - 20 - item_width), -item_height, item_width, item_height)
        self.speed = speed

    def update(self, dt):
        self.rect.y += self.speed * dt

    def draw(self, surf):
        # Chest base
        pygame.draw.rect(surf, gold, self.rect, border_radius=4)
        # Chest lock
        lock = pygame.Rect(self.rect.centerx - 3, self.rect.centery - 2, 6, 6)
        pygame.draw.rect(surf, (50, 40, 20), lock)


class Bubble:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.radius = random.randint(2, 6)
        self.speed = random.uniform(1.0, 3.0)

    def update(self):
        self.y -= self.speed
        if self.y < -10:
            self.y = height + 10
            self.x = random.randint(0, width)


def draw_background(surface, bubbles):
    surface.fill(ocean_blue)
    # Draw environmental ambient bubbles
    for b in bubbles:
        b.update()
        pygame.draw.circle(surface, water_light, (b.x, b.y), b.radius, 1)
    # Sea floor sand
    pygame.draw.rect(surface, sand_yellow, (0, height - 30, width, 30))


def draw_ui(surface, score, high_score):
    score_surf = font.render(f"Treasure: {int(score)}", True, white)
    hs_surf = font.render(f"Best Depth: {int(high_score)}", True, white)
    surface.blit(score_surf, (15, 15))
    surface.blit(hs_surf, (width - hs_surf.get_width() - 15, 15))


def game_over_screen(surface, score, high_score):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    
    text = big_font.render("CRUSHED!", True, red)
    sub = font.render(f"Treasure Collected: {int(score)}  Best: {int(high_score)}", True, white)
    hint = font.render("Press R to Dive Again | ESC to Exit", True, white)
    
    surface.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 70))
    surface.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 - 10))
    surface.blit(hint, (width // 2 - hint.get_width() // 2, height // 2 + 40))


def main():
    player = Submarine()
    anchors = []
    treasures = []
    bubbles = [Bubble() for _ in range(25)]
    
    running = True
    last_spawn = pygame.time.get_ticks()
    current_speed = base_speed
    score = 0
    high_score = 0
    game_over = False

    while running:
        dt = clock.tick(fps) / 16.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    player = Submarine()
                    anchors = []
                    treasures = []
                    score = 0
                    current_speed = base_speed
                    game_over = False
                    last_spawn = pygame.time.get_ticks()

        if not game_over:
            player.update()
            
            # Spawn objects periodically
            now = pygame.time.get_ticks()
            if now - last_spawn >= spawn_interval:
                # Randomly decide to spawn an anchor or a treasure chest
                if random.random() < 0.6:
                    anchors.append(Anchor(current_speed))
                else:
                    treasures.append(Treasure(current_speed))
                last_spawn = now

            # Update Anchors
            for a in anchors:
                a.update(dt)
            # Update Treasure
            for t in treasures:
                t.update(dt)

            # Clear out off-screen objects
            anchors = [a for a in anchors if a.rect.top <= height]
            treasures = [t for t in treasures if t.rect.top <= height]

            # Check collisions with Treasure Chests
            for t in treasures[:]:
                if player.rect.colliderect(t.rect):
                    score += 1
                    treasures.remove(t)
                    # Dynamically increase fall speeds as you get richer
                    current_speed = base_speed + (score * difficulty_increase_rate)

            # Check collisions with Anchors
            for a in anchors:
                if player.rect.colliderect(a.rect):
                    game_over = True
                    if score > high_score:
                        high_score = score
                    break

        # Render Scene
        draw_background(screen, bubbles)
        
        for t in treasures:
            t.draw(screen)
        for a in anchors:
            a.draw(screen)
            
        player.draw(screen)
        draw_ui(screen, score, high_score)
        
        if game_over:
            game_over_screen(screen, score, high_score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
