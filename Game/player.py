import pygame
from pygame.math import Vector2
import math

class Player:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.direction = Vector2(0, 0)
        self.next_direction = Vector2(0, 0)
        self.speed = 2
        self.radius = 13
        self.color = (255, 255, 0) # yellow
        self.mouth_angle = 45
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.score = 0
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: self.next_direction = Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT: self.next_direction = Vector2(1, 0)
            elif event.key == pygame.K_UP: self.next_direction = Vector2(0, -1)
            elif event.key == pygame.K_DOWN: self.next_direction = Vector2(0, 1)
    
    def can_move_in_direction(self, direction, maze):
        next_tile_pos = self.position + direction * maze.tile_size
        return not maze.is_wall(next_tile_pos.x, next_tile_pos.y)
    
    def is_at_center(self, maze):
        center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
        return (abs(self.position.x - center_x) < self.speed and abs(self.position.y - center_y) < self.speed)

    def update(self, maze):
        if self.next_direction and self.is_at_center(maze):
            if self.can_move_in_direction(self.next_direction, maze):
                self.direction = self.next_direction
                # snap to grid when turning
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
                self.next_direction = Vector2(0, 0)
        
        if self.direction:
            if not self.can_move_in_direction(self.direction, maze) and self.is_at_center(maze):
                # stop at center if we can't move forward
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
            else:
                new_pos = self.position + self.direction * self.speed
                if not maze.is_wall(new_pos.x, new_pos.y): self.position = new_pos
        
        # update mouth animation
        self.animation_timer += self.animation_speed
        if self.animation_timer > 1: self.animation_timer = 0
            
        eaten, power = maze.eat_dot(self.position.x, self.position.y)
        if eaten: self.score += 10 if not power else 50
        return power
    
    def draw(self, screen):
        current_angle = self.mouth_angle * abs(math.sin(self.animation_timer * math.pi))
        
        rotation = 0
        if self.direction.x < 0: rotation = 180
        elif self.direction.x > 0: rotation = 0
        elif self.direction.y < 0: rotation = 90
        elif self.direction.y > 0: rotation = 270
            
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        
        mouth_points = [
            self.position,
            self.position + Vector2(self.radius, 0).rotate(current_angle - rotation),
            self.position + Vector2(self.radius, 0).rotate(-current_angle - rotation)
        ]
        pygame.draw.polygon(screen, (0, 0, 0), mouth_points)
