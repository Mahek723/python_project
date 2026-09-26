import pygame
import random
import sys
import math

# Game Configurations
width, height = 700, 500
fps = 60
gravity = 0.3

# Colors
black = (15, 12, 18)
white = (255, 255, 255)
red = (230, 40, 40)
light_red = (255, 100, 100)
green = (40, 200, 40)
light_green = (120, 255, 120)
orange = (255, 140, 0)
light_orange = (255, 200, 50)
purple = (140, 40, 200)
dark_gray = (50, 50, 50)
neon_blue = (0, 220, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fruit Shinobi")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 26)
big_font = pygame.font.SysFont("Arial", 52)


class Fruit:
    def __init__(self):
        # Pick a fruit type
        self.type = random.choice(["watermelon", "orange", "grape", "bomb"])
        self.radius = random.randint(25, 35) if self.type != "bomb" else 22
        
        # Position physics (tossed from bottom area)
        self.x = random.randint(100, width - 100)
        self.y = height + self.radius
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-14, -10)  # Upward burst
        
        # Visual parameters
        self.sliced = False
        self.angle = 0
        self.spin = random.uniform(-4, 4)
        
        # Set colors based on type
        if self.type == "watermelon":
            self.outer_color = green
            self.inner_color = red
        elif self.type == "orange":
            self.outer_color = orange
            self.inner_color = light_orange
        elif self.type == "grape":
            self.outer_color = purple
            self.inner_color = (200, 100, 255)
        else: # Bomb
            self.outer_color = dark_gray
            self.inner_color = red

    def update(self):
        # Apply standard gravity mechanics
        self.vel_y += gravity
        self.x += self.vel_x
        self.y += self.vel_y
        self.angle += self.spin

    def draw(self, surf):
        if not self.sliced:
            if self.type == "bomb":
                # Draw a bomb with a small burning fuse
                pygame.draw.circle(surf, self.outer_color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surf, self.inner_color, (int(self.x + 8), int(self.y - 8)), 6)
                fuse_end = (int(self.x + 15 * math.cos(self.angle)), int(self.y - 20 + 5 * math.sin(self.angle)))
                pygame.draw.line(surf, white, (int(self.x), int(self.y - 15)), fuse_end, 2)
            else:
                # Draw uncut whole fruit (layered circle style)
                pygame.draw.circle(surf, self.outer_color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surf, self.inner_color, (int(self.x), int(self.y)), self.radius - 5)
        else:
            # Sliced representation: Draw two halves drifting outward apart
            offset = 12
            # Left/Top half
            pygame.draw.circle(surf, self.outer_color, (int(self.x - offset), int(self.y)), self.radius, draw_top_left=True)
            pygame.draw.circle(surf, self.inner_color, (int(self.x - offset), int(self.y)), self.radius - 5, draw_top_left=True)
            # Right/Bottom half
            pygame.draw.circle(surf, self.outer_color, (int(self.x + offset), int(self.y)), self.radius, draw_bottom_right=True)
            pygame.draw.circle(surf, self.inner_color, (int(self.x + offset), int(self.y)), self.radius - 5, draw_bottom_right=True)

    def check_slice(self, mouse_pos, prev_mouse_pos):
        if self.sliced:
            return False
            
        # Standard distance algorithm check
        dist = math.hypot(self.x - mouse_pos[0], self.y - mouse_pos[1])
        if dist < self.radius + 10:
            # Make sure mouse is actively swiping fast enough to trigger cut
            swipe_dist = math.hypot(mouse_pos[0] - prev_mouse_pos[0], mouse_pos[1] - prev_mouse_pos[1])
            if swipe_dist > 2:
                self.sliced = True
                return True
        return False


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(3, 7)
        self.vel_x = random.uniform(-5, 5)
        self.vel_y = random.uniform(-5, 5)
        self.life = 255  # Opacity reduction tracker

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2  # Gravity on drops
        self.life -= 8

    def draw(self, surf):
        if self.life > 0:
            # Draw splash juice droplet
            p_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.color, self.life), (self.radius, self.radius), self.radius)
            surf.blit(p_surf, (int(self.x - self.radius), int(self.y - self.radius)))


def game_over_screen(surface, score, high_score):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))
    
    text = big_font.render("BOOM! GAME OVER", True, red)
    sub = font.render(f"Final Score: {score}  |  Best Record: {high_score}", True, white)
    hint = font.render("Click anywhere or press SPACE to play again", True, neon_blue)
    
    surface.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 60))
    surface.blit(sub, (width // 2 - sub.get_width() // 2, height // 2))
    surface.blit(hint, (width // 2 - hint.get_width() // 2, height // 2 + 60))


def main():
    fruits = []
    particles = []
    blade_trail = []
    
    score = 0
    high_score = 0
    game_over = False
    
    # Timing limits
    spawn_timer = 0
    spawn_cooldown = 45  # frames between throws
    
    prev_mouse_pos = pygame.mouse.get_pos()
    
    running = True
    while running:
        clock.tick(fps)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    game_over = False
                    fruits.clear()
                    particles.clear()
                    score = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    game_over = False
                    fruits.clear()
                    particles.clear()
                    score = 0

        # Maintain mouse swipe gesture path trail visual lengths
        if not game_over:
            blade_trail.append(mouse_pos)
            if len(blade_trail) > 8:
                blade_trail.pop(0)
        else:
            blade_trail.clear()

        if not game_over:
            # Object spawn loop timers
            spawn_timer += 1
            if spawn_timer >= spawn_cooldown:
                spawn_timer = 0
                # Spawn dynamic groups (1 to 3 objects thrown at once)
                for _ in range(random.randint(1, 3)):
                    fruits.append(Fruit())
            
            # Object physics state cycle loops
            for f in fruits[:]:
                f.update()
                
                # Check for active swipe interactions
                if f.check_slice(mouse_pos, prev_mouse_pos):
                    if f.type == "bomb":
                        game_over = True
                        if score > high_score:
                            high_score = score
                        # Massive flash explosion effects
                        for _ in range(40):
                            particles.append(Particle(f.x, f.y, red))
                            particles.append(Particle(f.x, f.y, light_orange))
                    else:
                        score += 1
                        # Create fruit splash juice drops matching item identity colors
                        for _ in range(15):
                            particles.append(Particle(f.x, f.y, f.inner_color))
                
                # Drop item out of sight bounds safely (No penalty for missing)
                if f.y > height + f.radius + 50 and f.vel_y > 0:
                    fruits.remove(f)

            # Keep active particle physics tracking
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

        # Rendering operations
        screen.fill(black)
        
        # Render Splashes background layer
        for p in particles:
            p.draw(screen)
            
        # Draw physical fruits
        for f in fruits:
            f.draw(screen)

        # Draw the visual sword blade slash path
        if len(blade_trail) > 1:
            for i in range(len(blade_trail) - 1):
                thickness = int(i * 1.2) + 1
                pygame.draw.line(screen, neon_blue, blade_trail[i], blade_trail[i+1], thickness)

        # Render Core HUD Interface
        score_text = font.render(f"Score: {score}", True, white)
        hs_text = font.render(f"Best: {high_score}", True, white)
        
        screen.blit(score_text, (20, 20))
        screen.blit(hs_text, (20, 55))

        if game_over:
            game_over_screen(screen, score, high_score)

        pygame.display.flip()
        prev_mouse_pos = mouse_pos

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()