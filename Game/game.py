import pygame
import sys
from maze import Maze
from ghost import Ghost
from player import Player

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
        
        # Initialize player and game state
        self.player = Player()
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
            # Update player
            self.player.move(self.maze)
            
            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, self.player.x, self.player.y)
                if ghost.collides_with_pacman(self.player.x, self.player.y, self.player.radius):
                    self.game_over = True
                    
            # Check win condition
            if len(self.maze.dots) == 0:
                self.game_over = True

    def draw(self):
        self.screen.fill(self.BLACK)
        self.maze.draw(self.screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)
            
        # Draw player if game is not over
        if not self.game_over:
            self.player.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.player.score}', True, self.YELLOW)
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
        self.player.reset()
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
