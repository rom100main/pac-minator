import pygame

DIRECTIONS = {
    "UP": (0, -1), 
    "RIGHT": (1, 0), 
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
}

class Maze:
    def __init__(self, width, height):
        self.cell_size = 40
        self.width = width
        self.height = height
        self.rows = height // self.cell_size
        self.cols = width // self.cell_size
        
        # Colors
        self.BLUE = (0, 0, 255)
        self.WHITE = (255, 255, 255)
        
        # Maze
        # 1 for walls, 
        # 0 for paths, 
        # 2 for dots
        self.layout = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
            [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        
        self.dot_radius = 3
        self.dots = []
        self.init_dots()

    def init_dots(self):
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                if self.layout[row][col] == 2:
                    x = col * self.cell_size + self.cell_size // 2
                    y = row * self.cell_size + self.cell_size // 2
                    self.dots.append((x, y))

    def draw(self, screen):
        # Walls
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                if self.layout[row][col] == 1:
                    pygame.draw.rect(
                        screen, 
                        self.BLUE, 
                        (
                            col * self.cell_size, 
                            row * self.cell_size, 
                            self.cell_size, 
                            self.cell_size
                        )
                    )

        # Dots
        for dot in self.dots:
            pygame.draw.circle(
                screen, 
                self.WHITE, 
                (
                    int(dot[0]), 
                    int(dot[1])
                ), 
                self.dot_radius
            )

    def check_collision(self, x, y, direction):
        # Convert position to grid coordinates
        grid_x = round(x / self.cell_size)
        grid_y = round(y / self.cell_size)
        
        # Get the next cell position based on direction
        next_x = (grid_x + direction[0])*self.cell_size
        next_y = (grid_y + direction[1])*self.cell_size
        
        if direction == DIRECTIONS["UP"] and self.layout[grid_y-1][grid_x] == 1:
            return y < next_y + self.cell_size
        if direction == DIRECTIONS["DOWN"] and self.layout[grid_y+1][grid_x] == 1:
            return y > next_y - self.cell_size
        if direction == DIRECTIONS["LEFT"] and self.layout[grid_y][grid_x-1] == 1:
            return x < next_x + self.cell_size
        if direction == DIRECTIONS["RIGHT"] and self.layout[grid_y][grid_x+1] == 1:
            return x > next_x - self.cell_size
            
        return False

    def eat_dot(self, x, y):
        # Adjust x,y by half cell size to match display coordinates
        x = x + self.cell_size/2
        y = y + self.cell_size/2
        collision_radius = (self.dot_radius + 15)**2  # Square of combined radii (dot + pacman)
        for i, dot in enumerate(self.dots):
            if ((x - dot[0])**2 + (y - dot[1])**2) <= collision_radius:
                self.dots.pop(i)
                return True
        return False
