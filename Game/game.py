import pygame
import numpy as np

from maze import Maze
from player import Player
from ghost import Ghost, GhostType


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, screen, font):
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw the button rectangle
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, width=2, border_radius=12)
        
        # Draw the text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

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
        
        # Initialize game elements
        self.initialize_game()
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)
        
        # Button setup
        button_width, button_height = 150, 50
        button_x = (self.maze.screen_width - button_width) // 2
        button_y = self.maze.screen_height // 2 + 50
        self.restart_button = Button(
            button_x, button_y, button_width, button_height,
            "Play again", (200, 0, 0), (250, 0, 0), (255, 255, 255)
        )
    
    def initialize_game(self):
        # Setup player
        player_start_x = self.maze.tile_size * 9 + self.maze.tile_size // 2
        player_start_y = self.maze.tile_size * 15 + self.maze.tile_size // 2
        self.player = Player(player_start_x, player_start_y)
        
        # Setup ghosts with their new ghost types
        ghost_start_positions = [
            # Blinky (red) - starts outside
            (self.maze.tile_size * 9 + self.maze.tile_size // 2,
             self.maze.tile_size * 7 + self.maze.tile_size // 2,
             (255, 0, 0),
             GhostType.BLINKY),
            # Pinky (pink) - starts outside
            (self.maze.tile_size * 8 + self.maze.tile_size // 2,
             self.maze.tile_size * 7 + self.maze.tile_size // 2,
             (255, 182, 255),
             GhostType.PINKY),
            # Inky (cyan) - starts outside
            (self.maze.tile_size * 10 + self.maze.tile_size // 2,
             self.maze.tile_size * 7 + self.maze.tile_size // 2,
             (0, 255, 255),
             GhostType.INKY),
            # Clyde (orange) - starts outside
            (self.maze.tile_size * 9 + self.maze.tile_size // 2,
             self.maze.tile_size * 7 + self.maze.tile_size // 2,
             (255, 182, 85),
             GhostType.CLYDE)
        ]
        
        self.ghosts = []
        for x, y, color, ghost_type in ghost_start_positions:
            self.ghosts.append(Ghost(x, y, color, ghost_type))
        
        # Add ghosts attribute to player for Inky's targeting
        self.player.ghosts = self.ghosts
        
        # Game state
        self.running = True
        self.game_over = False
        self.win = False
        self.level = 1

    def reset_game(self):
        # Reset maze (recreate dots/pellets)
        self.maze.reset()
        
        # Reset player and ghosts
        self.initialize_game()
 
    def get_grid_player(self):
        position = np.zeros(self.maze.grid.shape)
        pos_x, pos_y = self.maze.convert_to_grid(*self.player.position)
        position[pos_y, pos_x] = 1

        next_position = np.zeros(self.maze.grid.shape)
        next_pos_x, next_pos_y = self.player.position + self.player.direction * self.player.speed
        next_pos_x, next_pos_y = self.maze.convert_to_grid(next_pos_x, next_pos_y)
        next_position[next_pos_y, next_pos_x] = 1
        
        return position, next_position
    
    def get_grid_ghosts(self):
        positions = np.zeros(self.maze.grid.shape)
        for ghost in self.ghosts:
            pos_x, pos_y = self.maze.convert_to_grid(*ghost.position)
            positions[pos_y, pos_x] = 1
        
        next_positions = np.zeros(self.maze.grid.shape)
        for ghost in self.ghosts:
            next_pos_x, next_pos_y = ghost.position + ghost.direction * ghost.speed
            next_pos_x, next_pos_y = self.maze.convert_to_grid(next_pos_x, next_pos_y)
            next_positions[next_pos_y, next_pos_x] = 1
        
        return positions, next_positions

    def check_collisions(self):
        for ghost in self.ghosts:
            distance = (ghost.position - self.player.position).length()
            if distance < (ghost.radius + self.player.radius):
                if ghost.state == ghost.state.FRIGHTENED:
                    ghost.enter_eaten_mode()
                    # Score for eating ghost increases with each ghost eaten
                    # Count how many ghosts are in eaten state
                    eaten_count = sum(1 for g in self.ghosts if g.state == g.state.EATEN)
                    points = 200 * (2 ** (eaten_count - 1))  # 200, 400, 800, 1600
                    self.player.score += points
                elif ghost.state == ghost.state.CHASE or ghost.state == ghost.state.SCATTER:
                    self.game_over = True
        
        # Check win condition
        if self.maze.count_dots() == 0:
            self.win = True
            self.game_over = True
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.player.handle_input(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over and self.restart_button.clicked(mouse_pos):
                    self.reset_game()
        
        # Check hover for button visual effect
        if self.game_over:
            self.restart_button.check_hover(mouse_pos)

    def update(self):
        if self.game_over: return
        
        power_pellet = self.player.update(self.maze)
        if power_pellet:
            for ghost in self.ghosts: ghost.enter_frightened_mode()
        
        for ghost in self.ghosts: ghost.update(self.maze, self.player)
        
        self.check_collisions()
    
    def draw(self):
        self.screen.fill((0, 0, 0))

        self.maze.draw(self.screen)
        
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        self.player.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect()
        level_rect.right = self.maze.screen_width - 10
        level_rect.top = 10
        self.screen.blit(level_text, level_rect)
        
        if self.game_over:
            if self.win:
                game_over_text = self.font.render("You Win!", True, (0, 255, 0))
            else:
                game_over_text = self.font.render("Game Over!", True, (255, 0, 0))
                
            text_rect = game_over_text.get_rect(center=(self.maze.screen_width // 2, self.maze.screen_height // 2))
            self.screen.blit(game_over_text, text_rect)
            
            # Draw restart button
            self.restart_button.draw(self.screen, self.button_font)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()