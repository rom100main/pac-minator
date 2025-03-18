import pygame
from maze import Maze
from player import Player
from ghost import Ghost
from pygame.math import Vector2

class Game:
    def __init__(self):
        pygame.init()
        self.maze = Maze()
        self.screen = pygame.display.set_mode(
            (self.maze.screen_width, self.maze.screen_height)
        )
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.fps = 50
        
        # Initialize player at a valid starting position
        player_start_x = self.maze.tile_size * 9 + self.maze.tile_size // 2
        player_start_y = self.maze.tile_size * 15 + self.maze.tile_size // 2
        self.player = Player(player_start_x, player_start_y)
        
        # Initialize ghosts with different colors
        self.ghosts = [
            Ghost(self.maze.tile_size * 9 + self.maze.tile_size // 2,  # Red ghost
                 self.maze.tile_size * 7 + self.maze.tile_size // 2,
                 (255, 0, 0)),
            Ghost(self.maze.tile_size * 8 + self.maze.tile_size // 2,  # Pink ghost
                 self.maze.tile_size * 7 + self.maze.tile_size // 2,
                 (255, 182, 255)),
            Ghost(self.maze.tile_size * 10 + self.maze.tile_size // 2,  # Cyan ghost
                 self.maze.tile_size * 7 + self.maze.tile_size // 2,
                 (0, 255, 255)),
            Ghost(self.maze.tile_size * 9 + self.maze.tile_size // 2,  # Orange ghost
                 self.maze.tile_size * 7 + self.maze.tile_size // 2,
                 (255, 182, 85))
        ]
        
        # Game state
        self.running = True
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.player.handle_input(event)
    
    def check_collisions(self):
        for ghost in self.ghosts:
            distance = (ghost.position - self.player.position).length()
            if distance < (ghost.radius + self.player.radius):
                if ghost.state == ghost.state.FRIGHTENED:
                    ghost.state = ghost.state.EATEN
                elif ghost.state == ghost.state.CHASE:
                    self.game_over = True
    
    def update(self):
        if self.game_over:
            return
            
        # Update player and check if power pellet was eaten
        power_pellet = self.player.update(self.maze)
        if power_pellet:
            for ghost in self.ghosts:
                ghost.enter_frightened_mode()
        
        # Update ghosts
        for ghost in self.ghosts:
            ghost.update(self.maze, self.player)
        
        # Check for collisions
        self.check_collisions()
    
    def draw(self):
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw maze
        self.maze.draw(self.screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over message if applicable
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.maze.screen_width // 2,
                                                       self.maze.screen_height // 2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
