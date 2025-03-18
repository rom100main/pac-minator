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
        self.frightened_timer = 0
        self.frightened_duration = 500  # 10 seconds at 50 fps
        self.base_color = color
        self.frightened_color = (0, 0, 255)  # Blue
        self.eaten_color = (255, 255, 255)  # White
        
    def get_valid_directions(self, maze):
        valid = []
        for direction in [Vector2(0, -1), Vector2(0, 1), Vector2(-1, 0), Vector2(1, 0)]:
            if not maze.is_wall(self.position.x + direction.x * self.radius,
                              self.position.y + direction.y * self.radius):
                valid.append(direction)
        return valid
    
    def choose_direction(self, maze, player):
        if self.state == GhostState.FRIGHTENED:
            # Random movement when frightened
            valid_directions = self.get_valid_directions(maze)
            # Remove opposite of current direction unless no other choice
            if self.direction and len(valid_directions) > 1:
                opposite = Vector2(-self.direction.x, -self.direction.y)
                if opposite in valid_directions:
                    valid_directions.remove(opposite)
            return random.choice(valid_directions)
        
        # Chase mode - try to move towards player
        valid_directions = self.get_valid_directions(maze)
        if not valid_directions:
            return Vector2(0, 0)
            
        # Remove opposite direction unless it's the only option
        if self.direction and len(valid_directions) > 1:
            opposite = Vector2(-self.direction.x, -self.direction.y)
            if opposite in valid_directions:
                valid_directions.remove(opposite)
        
        # Choose direction closest to player
        best_direction = valid_directions[0]
        min_distance = float('inf')
        
        for direction in valid_directions:
            new_pos = self.position + direction * self.radius
            distance = (player.position - new_pos).length()
            if distance < min_distance:
                min_distance = distance
                best_direction = direction
                
        return best_direction
    
    def is_at_center(self, maze):
        center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
        return (abs(self.position.x - center_x) < self.speed and 
                abs(self.position.y - center_y) < self.speed)
    
    def enter_frightened_mode(self):
        if self.state != GhostState.EATEN:
            self.state = GhostState.FRIGHTENED
            self.frightened_timer = self.frightened_duration
            # Reverse direction
            self.direction = Vector2(-self.direction.x, -self.direction.y)
    
    def get_current_color(self):
        if self.state == GhostState.FRIGHTENED:
            # Flash white and blue when frightened mode is about to end
            if self.frightened_timer < 150 and self.frightened_timer % 30 < 15:
                return (255, 255, 255)
            return self.frightened_color
        elif self.state == GhostState.EATEN:
            return self.eaten_color
        return self.base_color
    
    def can_move_forward(self, maze):
        # Check one tile ahead
        next_tile_pos = self.position + self.direction * maze.tile_size
        return not maze.is_wall(next_tile_pos.x, next_tile_pos.y)

    def update(self, maze, player):
        if self.state == GhostState.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.state = GhostState.CHASE
        
        # Update direction at tile centers
        if self.is_at_center(maze):
            if not self.can_move_forward(maze):
                self.direction = self.choose_direction(maze, player)
            # Snap to grid when turning
            center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
            self.position.x = center_x
            self.position.y = center_y
        
        # Move in current direction if possible
        if self.direction:
            new_pos = self.position + self.direction * self.speed
            if not maze.is_wall(new_pos.x, new_pos.y):
                self.position = new_pos
    
    def draw(self, screen):
        # Draw ghost body
        pygame.draw.circle(screen, self.get_current_color(), 
                         (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw eyes
        eye_color = (255, 255, 255) if self.state != GhostState.EATEN else (0, 0, 255)
        eye_radius = 4
        eye_offset = 5
        
        # Calculate eye positions based on direction
        left_eye_pos = (
            int(self.position.x - eye_offset),
            int(self.position.y - eye_offset)
        )
        right_eye_pos = (
            int(self.position.x + eye_offset),
            int(self.position.y - eye_offset)
        )
        
        pygame.draw.circle(screen, eye_color, left_eye_pos, eye_radius)
        pygame.draw.circle(screen, eye_color, right_eye_pos, eye_radius)
        
        # Draw pupils
        pupil_color = (0, 0, 255)
        pupil_radius = 2
        pupil_offset = Vector2(2, 0)
        
        if self.direction.x < 0:
            pupil_offset = Vector2(-2, 0)
        elif self.direction.x > 0:
            pupil_offset = Vector2(2, 0)
        elif self.direction.y < 0:
            pupil_offset = Vector2(0, -2)
        elif self.direction.y > 0:
            pupil_offset = Vector2(0, 2)
            
        pygame.draw.circle(screen, pupil_color,
                         (int(left_eye_pos[0] + pupil_offset.x),
                          int(left_eye_pos[1] + pupil_offset.y)), 
                         pupil_radius)
        pygame.draw.circle(screen, pupil_color,
                         (int(right_eye_pos[0] + pupil_offset.x),
                          int(right_eye_pos[1] + pupil_offset.y)),
                         pupil_radius)
