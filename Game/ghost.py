import pygame
from pygame.math import Vector2
import random
from enum import Enum
import math

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
        self.frightened_color = (0, 0, 255)  # Blue when frightened
        self.eaten_color = (255, 255, 255)  # White when eaten
        self.frightened_timer = 0
        self.frightened_duration = 500  # Duration in update cycles
    
    def get_possible_directions(self, maze):
        possible = []
        for direction in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
            if self.can_move_in_direction(direction, maze):
                possible.append(direction)
        return possible
    
    def choose_direction(self, maze, target_pos):
        if self.state == GhostState.FRIGHTENED:
            # In frightened state, choose random valid direction
            possible_directions = self.get_possible_directions(maze)
            # Try not to reverse direction unless it's the only option
            if len(possible_directions) > 1 and self.direction != Vector2(0, 0):
                opposite = self.direction * -1
                if opposite in possible_directions:
                    possible_directions.remove(opposite)
            return random.choice(possible_directions)
        else:
            # In chase or eaten state, try to move towards target
            possible_directions = self.get_possible_directions(maze)
            if not possible_directions:
                return Vector2(0, 0)
            
            # Get actual target position (either player position or home position)
            target_position = target_pos.position if hasattr(target_pos, 'position') else target_pos
            
            # Calculate distances to target for each possible direction
            distances = []
            for direction in possible_directions:
                next_pos = self.position + direction * maze.tile_size
                distance = (next_pos - target_position).length()
                distances.append((distance, direction))
            
            # If eaten, move towards home
            if self.state == GhostState.EATEN:
                return min(distances, key=lambda x: x[0])[1]
            # If chasing, move towards target
            else:
                return min(distances, key=lambda x: x[0])[1]
    
    def can_move_in_direction(self, direction, maze):
        # Check if we can move in the given direction from current position
        next_tile_pos = self.position + direction * maze.tile_size
        return not maze.is_wall(next_tile_pos.x, next_tile_pos.y)
    
    def is_at_center(self, maze):
        center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
        return (abs(self.position.x - center_x) < self.speed and 
                abs(self.position.y - center_y) < self.speed)
    
    def enter_frightened_mode(self):
        if self.state != GhostState.EATEN:
            self.state = GhostState.FRIGHTENED
            self.frightened_timer = self.frightened_duration
    
    def update(self, maze, target_pos):
        # Update frightened state
        if self.state == GhostState.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.state = GhostState.CHASE
        
        # Choose new direction at intersections
        if self.is_at_center(maze):
            new_direction = self.choose_direction(maze, target_pos)
            if new_direction != Vector2(0, 0):
                self.direction = new_direction
                # Snap to grid when turning
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
        
        # Continue moving in current direction if possible
        if self.direction:
            new_pos = self.position + self.direction * self.speed
            if not maze.is_wall(new_pos.x, new_pos.y):
                self.position = new_pos
            else:
                # If we hit a wall, try to choose a new direction
                self.direction = self.choose_direction(maze, target_pos)
    
    def draw(self, screen):
        # Determine color based on state
        current_color = self.color
        if self.state == GhostState.FRIGHTENED:
            current_color = self.frightened_color
        elif self.state == GhostState.EATEN:
            current_color = self.eaten_color

        # Draw the main body of the ghost
        pygame.draw.circle(screen, current_color, (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw the bottom part of the ghost (wavy shape)
        points = [
            (self.position.x - self.radius, self.position.y),  # Left side
            (self.position.x - self.radius, self.position.y + self.radius),  # Bottom left
            (self.position.x - self.radius * 2/3, self.position.y + self.radius * 2/3),  # First curve
            (self.position.x - self.radius * 1/3, self.position.y + self.radius),  # Second curve
            (self.position.x, self.position.y + self.radius * 2/3),  # Middle curve
            (self.position.x + self.radius * 1/3, self.position.y + self.radius),  # Fourth curve
            (self.position.x + self.radius * 2/3, self.position.y + self.radius * 2/3),  # Fifth curve
            (self.position.x + self.radius, self.position.y + self.radius),  # Bottom right
            (self.position.x + self.radius, self.position.y),  # Right side
        ]
        pygame.draw.polygon(screen, current_color, [(int(x), int(y)) for x, y in points])

        # Draw the eyes
        eye_color = (255, 255, 255)  # White eyes
        pupil_color = (0, 0, 0)      # Black pupils
        
        # Left eye
        left_eye_pos = (int(self.position.x - self.radius/2), int(self.position.y - self.radius/4))
        pygame.draw.circle(screen, eye_color, left_eye_pos, self.radius/3)
        # Left pupil (looking in movement direction)
        pupil_offset = Vector2(self.direction.x, self.direction.y).normalize() * (self.radius/6) if self.direction.length() > 0 else Vector2(0, 0)
        left_pupil_pos = (int(left_eye_pos[0] + pupil_offset.x), int(left_eye_pos[1] + pupil_offset.y))
        pygame.draw.circle(screen, pupil_color, left_pupil_pos, self.radius/6)
        
        # Right eye
        right_eye_pos = (int(self.position.x + self.radius/2), int(self.position.y - self.radius/4))
        pygame.draw.circle(screen, eye_color, right_eye_pos, self.radius/3)
        # Right pupil (looking in movement direction)
        right_pupil_pos = (int(right_eye_pos[0] + pupil_offset.x), int(right_eye_pos[1] + pupil_offset.y))
        pygame.draw.circle(screen, pupil_color, right_pupil_pos, self.radius/6)
