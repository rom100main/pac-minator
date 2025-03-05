import pygame

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

    def check_collision(self, x, y, radius):
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        
        # Check surrounding cells
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                check_x = grid_x + dx
                check_y = grid_y + dy
                
                if (
                    0 <= check_y < len(self.layout) and 
                    0 <= check_x < len(self.layout[0]) and 
                    self.layout[check_y][check_x] == 1
                ):
                    # Check collision with wall
                    wall_rect = pygame.Rect(
                        check_x * self.cell_size, 
                        check_y * self.cell_size,
                        self.cell_size, 
                        self.cell_size
                    )
                    circle_dist_x = abs(x - wall_rect.centerx)
                    circle_dist_y = abs(y - wall_rect.centery)
                    
                    if circle_dist_x > (wall_rect.width/2 + radius): continue
                    if circle_dist_y > (wall_rect.height/2 + radius): continue
                    
                    if circle_dist_x <= wall_rect.width/2: return True
                    if circle_dist_y <= wall_rect.height/2: return True
                    
                    corner_dist_sq = (
                        (circle_dist_x - wall_rect.width/2) ** 2 +
                        (circle_dist_y - wall_rect.height/2) ** 2
                    )
                    
                    if corner_dist_sq <= (radius ** 2):
                        return True
        return False

    def eat_dot(self, x, y):
        collision_radius = (self.dot_radius + 15)**2  # Square of combined radii (dot + pacman)
        for i, dot in enumerate(self.dots):
            if ((x - dot[0])**2 + (y - dot[1])**2) <= collision_radius:
                self.dots.pop(i)
                return True
        return False
