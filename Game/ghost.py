import pygame
import random
import math

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 15
        self.speed = 3
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.target_time = 0
        self.direction_change_interval = 2000  # change direction every 2 seconds
        
    def update(self, maze, pacman_x, pacman_y):
        current_time = pygame.time.get_ticks()
        
        # change direction periodically or when hitting a wall
        if (
            current_time - self.target_time > self.direction_change_interval or 
            maze.check_collision(self.x, self.y, self.direction)
        ):    
            self.choose_direction(maze, pacman_x, pacman_y)
            self.target_time = current_time
            
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        
        if not maze.check_collision(self.x, self.y, self.direction):
            self.x = new_x
            self.y = new_y
            
    def choose_direction(self, maze, pacman_x, pacman_y):
        # Possible directions: up, down, left, right
        possible_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        valid_directions = []
        
        # Check valid directions (don't hit walls)
        for dx, dy in possible_directions:
            # Look ahead further to avoid getting stuck
            # Test if direction is valid
            if not maze.check_collision(self.x, self.y, (dx, dy)):
                valid_directions.append((dx, dy))
                
        if valid_directions:
            # 70% chance to move towards Pacman, 30% chance to move randomly
            if random.random() < 0.7:
                # Calculate direction towards Pacman
                dx = pacman_x - self.x
                dy = pacman_y - self.y
                
                # Choose the valid direction that most closely matches the direction to Pacman
                best_direction = valid_directions[0]
                best_dot_product = float('-inf')
                
                # Normalize the direction vector to Pacman
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    dx, dy = dx/length, dy/length
                    
                    for vdx, vdy in valid_directions:
                        # Calculate dot product to find most similar direction
                        dot_product = dx * vdx + dy * vdy
                        if dot_product > best_dot_product:
                            best_dot_product = dot_product
                            best_direction = (vdx, vdy)
                            
                self.direction = best_direction
            else:
                # Choose random valid direction
                self.direction = random.choice(valid_directions)
                
    def draw(self, screen):
        # Offset position by half cell size (20 pixels) for display
        display_x = self.x + 20
        display_y = self.y + 20
        
        # Body
        pygame.draw.circle(screen, self.color, (int(display_x), int(display_y)), self.radius)
        
        # "skirt"
        points = [
            (display_x - self.radius, display_y + self.radius),
            (display_x - self.radius/2, display_y + self.radius/2),
            (display_x, display_y + self.radius),
            (display_x + self.radius/2, display_y + self.radius/2),
            (display_x + self.radius, display_y + self.radius)
        ]
        pygame.draw.lines(screen, self.color, False, points, 3)
        
        # Eyes
        eye_color = (255, 255, 255)  # White
        eye_radius = 4
        eye_offset_x = 6
        eye_offset_y = -2

        pygame.draw.circle(
            screen, 
            eye_color,
            (
                int(display_x - eye_offset_x), 
                int(display_y + eye_offset_y)
            ),
            eye_radius
        )
        pygame.draw.circle(
            screen, 
            eye_color,
            (
                int(display_x + eye_offset_x), 
                int(display_y + eye_offset_y)
            ),
            eye_radius
        )
        
    def collides_with_pacman(self, pacman_x, pacman_y, pacman_radius):
        # No need to adjust for display offset since both ghost and pacman 
        # use the same coordinate system internally
        distance = math.sqrt((self.x - pacman_x)**2 + (self.y - pacman_y)**2)
        return distance < (self.radius + pacman_radius)
