import pygame
from pygame.math import Vector2
import random
from enum import Enum

class GhostState(Enum):
    CHASE = 1
    FRIGHTENED = 2
    EATEN = 3

class Ghost:
    def __init__(self, x, y, color):
        self.position = Vector2(x, y)
        self.direction = Vector2(0, 0)
        self.next_direction = Vector2(0, 0)
        self.speed = 2
        self.radius = 13
        self.color = color
        self.state = GhostState.CHASE
        self.frightened_color = (0, 0, 255)  # blue
        self.eaten_color = (255, 255, 255)  # white
        self.frightened_timer = 0
        self.frightened_duration = 500  # duration update cycles

    def get_grid_position(self): return int(self.position.x // 16), int(self.position.y // 16)
    
    def get_grid_next_position(self): return int((self.position.x + self.direction.x * self.speed) // 16), int((self.position.y + self.direction.y * self.speed) // 16)

    def get_possible_directions(self, maze):
        possible = []
        for direction in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
            if self.can_move_in_direction(direction, maze): possible.append(direction)
        return possible
    
    def choose_direction(self, maze, target_pos):
        if self.state == GhostState.FRIGHTENED:
            possible_directions = self.get_possible_directions(maze)
            # try not to reverse direction unless it's the only option
            if len(possible_directions) > 1 and self.direction != Vector2(0, 0):
                opposite = self.direction * -1
                if opposite in possible_directions: possible_directions.remove(opposite)
            return random.choice(possible_directions)
        else:
            possible_directions = self.get_possible_directions(maze)
            if not possible_directions: return Vector2(0, 0)
            
            target_position = target_pos.position if hasattr(target_pos, 'position') else target_pos
            
            distances = []
            for direction in possible_directions:
                next_pos = self.position + direction * maze.tile_size
                distance = (next_pos - target_position).length()
                distances.append((distance, direction))
            
            if self.state == GhostState.EATEN: return min(distances, key=lambda x: x[0])[1]
            else: return min(distances, key=lambda x: x[0])[1]
    
    def can_move_in_direction(self, direction, maze):
        next_tile_pos = self.position + direction * maze.tile_size
        return not maze.is_wall(next_tile_pos.x, next_tile_pos.y)
    
    def is_at_center(self, maze):
        center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
        return (abs(self.position.x - center_x) < self.speed and abs(self.position.y - center_y) < self.speed)
    
    def enter_frightened_mode(self):
        if self.state != GhostState.EATEN:
            self.state = GhostState.FRIGHTENED
            self.frightened_timer = self.frightened_duration
    
    def update(self, maze, target_pos):
        if self.state == GhostState.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0: self.state = GhostState.CHASE
        
        if self.is_at_center(maze):
            new_direction = self.choose_direction(maze, target_pos)
            if new_direction != Vector2(0, 0):
                self.direction = new_direction
                # snap to grid when turning
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
        
        if self.direction:
            new_pos = self.position + self.direction * self.speed
            if not maze.is_wall(new_pos.x, new_pos.y): self.position = new_pos
            else: self.direction = self.choose_direction(maze, target_pos)
    
    def draw(self, screen):
        current_color = self.color
        if self.state == GhostState.FRIGHTENED: current_color = self.frightened_color
        elif self.state == GhostState.EATEN: current_color = self.eaten_color

        pygame.draw.circle(screen, current_color, (int(self.position.x), int(self.position.y)), self.radius)
        
        # bottom part of the ghost (wavy shape)
        points = [
            (self.position.x - self.radius, self.position.y),  # left side
            (self.position.x - self.radius, self.position.y + self.radius),  # bottom left
            (self.position.x - self.radius * 2/3, self.position.y + self.radius * 2/3),  # first curve
            (self.position.x - self.radius * 1/3, self.position.y + self.radius),  # second curve
            (self.position.x, self.position.y + self.radius * 2/3),  # middle curve
            (self.position.x + self.radius * 1/3, self.position.y + self.radius),  # fourth curve
            (self.position.x + self.radius * 2/3, self.position.y + self.radius * 2/3),  # fifth curve
            (self.position.x + self.radius, self.position.y + self.radius),  # bottom right
            (self.position.x + self.radius, self.position.y),  # right side
        ]
        pygame.draw.polygon(screen, current_color, [(int(x), int(y)) for x, y in points])

        eye_color = (255, 255, 255) # white
        pupil_color = (0, 0, 0) # black
        
        left_eye_pos = (int(self.position.x - self.radius/2), int(self.position.y - self.radius/4))
        pygame.draw.circle(screen, eye_color, left_eye_pos, self.radius/3)
        pupil_offset = Vector2(self.direction.x, self.direction.y).normalize() * (self.radius/6) if self.direction.length() > 0 else Vector2(0, 0)
        left_pupil_pos = (int(left_eye_pos[0] + pupil_offset.x), int(left_eye_pos[1] + pupil_offset.y))
        pygame.draw.circle(screen, pupil_color, left_pupil_pos, self.radius/6)
        
        right_eye_pos = (int(self.position.x + self.radius/2), int(self.position.y - self.radius/4))
        pygame.draw.circle(screen, eye_color, right_eye_pos, self.radius/3)
        right_pupil_pos = (int(right_eye_pos[0] + pupil_offset.x), int(right_eye_pos[1] + pupil_offset.y))
        pygame.draw.circle(screen, pupil_color, right_pupil_pos, self.radius/6)
