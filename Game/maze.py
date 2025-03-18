import pygame
import numpy as np

class Maze:
    def __init__(self):
        self.tile_size = 30
        # 0: empty path, 1: wall, 2: dot, 3: power pellet
        self.grid = np.array([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 3, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 1, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 1],
            [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
            [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 3, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 3, 1],
            [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ])
        self.height, self.width = self.grid.shape
        self.screen_width = self.width * self.tile_size
        self.screen_height = self.height * self.tile_size
        
        # Colors
        self.WALL_COLOR = (0, 0, 255)
        self.DOT_COLOR = (255, 255, 255)
        self.POWER_PELLET_COLOR = (255, 255, 0)
        
    def is_wall(self, x, y):
        # Convert pixel coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == 1
        return True
    
    def get_tile_center(self, x, y):
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        return (grid_x * self.tile_size + self.tile_size // 2,
                grid_y * self.tile_size + self.tile_size // 2)
    
    def get_tile(self, x, y):
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x]
        return 1
    
    def eat_dot(self, x, y):
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            if self.grid[grid_y][grid_x] in [2, 3]:
                is_power_pellet = self.grid[grid_y][grid_x] == 3
                self.grid[grid_y][grid_x] = 0
                return True, is_power_pellet
        return False, False
    
    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pos_x = x * self.tile_size
                pos_y = y * self.tile_size
                
                if self.grid[y][x] == 1:  # Wall
                    pygame.draw.rect(screen, self.WALL_COLOR, 
                                  (pos_x, pos_y, self.tile_size, self.tile_size))
                elif self.grid[y][x] == 2:  # Dot
                    pygame.draw.circle(screen, self.DOT_COLOR,
                                    (pos_x + self.tile_size // 2, 
                                     pos_y + self.tile_size // 2), 3)
                elif self.grid[y][x] == 3:  # Power Pellet
                    pygame.draw.circle(screen, self.POWER_PELLET_COLOR,
                                    (pos_x + self.tile_size // 2, 
                                     pos_y + self.tile_size // 2), 8)
