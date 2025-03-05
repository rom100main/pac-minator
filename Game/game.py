import pygame
import sys
import math
from maze import Maze
from ghost import Ghost

class PacmanGame:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 760  # Adjusted for maze height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.PINK = (255, 182, 255)
        self.CYAN = (0, 255, 255)
        self.ORANGE = (255, 182, 85)
        
        # Initialize maze
        self.maze = Maze(self.width, self.height)
        
        # Pacman initial position (aligned with maze grid)
        self.pacman_x = 60  # One cell + half a cell (40 + 20)
        self.pacman_y = 60  # One cell + half a cell (40 + 20)
        self.pacman_radius = 15  # Slightly smaller to fit maze better
        self.pacman_angle = 0
        self.pacman_speed = 4
        self.mouth_angle = 45  # Angle for pacman's mouth
        
        # Score and game state
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        
        # Initialize ghosts (positions aligned with maze grid)
        self.ghosts = [
            Ghost(380, 380, self.RED),     # Center
            Ghost(340, 380, self.PINK),    # Left of center
            Ghost(420, 380, self.CYAN),    # Right of center
            Ghost(380, 340, self.ORANGE),  # Above center
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if not self.game_over:
            # Store current position
            new_x = self.pacman_x
            new_y = self.pacman_y
            
            # Update position based on input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                new_x -= self.pacman_speed
                self.pacman_angle = 180
            if keys[pygame.K_RIGHT]:
                new_x += self.pacman_speed
                self.pacman_angle = 0
            if keys[pygame.K_UP]:
                new_y -= self.pacman_speed
                self.pacman_angle = 90
            if keys[pygame.K_DOWN]:
                new_y += self.pacman_speed
                self.pacman_angle = 270
                
            # Check for wall collision before updating position
            if not self.maze.check_collision(new_x, new_y, self.pacman_radius):
                self.pacman_x = new_x
                self.pacman_y = new_y
                
            # Check for dot collision
            if self.maze.eat_dot(self.pacman_x, self.pacman_y):
                self.score += 10
            
            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman_x, self.pacman_y)
                if ghost.collides_with_pacman(self.pacman_x, self.pacman_y, self.pacman_radius):
                    self.game_over = True
                    
            # Check win condition
            if len(self.maze.dots) == 0:
                self.game_over = True

    def draw_pacman(self):
        # Draw Pacman as a circle with a mouth
        start_angle = self.pacman_angle + self.mouth_angle
        end_angle = self.pacman_angle - self.mouth_angle
        pygame.draw.arc(self.screen, self.YELLOW,
                       (self.pacman_x - self.pacman_radius,
                        self.pacman_y - self.pacman_radius,
                        self.pacman_radius * 2,
                        self.pacman_radius * 2),
                       math.radians(start_angle),
                       math.radians(end_angle), self.pacman_radius)

    def draw(self):
        self.screen.fill(self.BLACK)
        self.maze.draw(self.screen)
        
        # Draw ghosts behind Pacman
        for ghost in self.ghosts:
            ghost.draw(self.screen)
            
        # Only draw Pacman if game is not over
        if not self.game_over:
            self.draw_pacman()
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, self.YELLOW)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over or win message
        if self.game_over:
            if len(self.maze.dots) == 0:
                message = "YOU WIN!"
            else:
                message = "GAME OVER"
            
            game_over_text = self.font.render(message, True, self.YELLOW)
            text_rect = game_over_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(game_over_text, text_rect)
            
            # Draw restart instruction
            restart_text = self.font.render("Press SPACE to restart", True, self.YELLOW)
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def reset_game(self):
        self.pacman_x = 60
        self.pacman_y = 60
        self.pacman_angle = 0
        self.score = 0
        self.game_over = False
        self.maze = Maze(self.width, self.height)
        self.ghosts = [
            Ghost(380, 380, self.RED),
            Ghost(340, 380, self.PINK),
            Ghost(420, 380, self.CYAN),
            Ghost(380, 340, self.ORANGE),
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PacmanGame()
    game.run()
