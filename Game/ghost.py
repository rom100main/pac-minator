import pygame
from pygame.math import Vector2
import random
from enum import Enum

class GhostState(Enum):
    SCATTER = 0
    CHASE = 1
    FRIGHTENED = 2
    EATEN = 3

class GhostType(Enum):
    BLINKY = 0  # Red - Shadow - Pursuer
    PINKY = 1   # Pink - Ambusher
    INKY = 2    # Cyan - Bashful - Unpredictable
    CLYDE = 3   # Orange - Pokey - Feigned ignorance

class Ghost:
    def __init__(self, x, y, color, ghost_type):
        self.position = Vector2(x, y)
        self.direction = Vector2(0, 0)
        self.next_direction = Vector2(0, 0)
        self.speed = 2
        self.original_speed = 2
        self.radius = 13
        self.color = color
        self.ghost_type = ghost_type
        self.state = GhostState.SCATTER
        self.frightened_color = (0, 0, 255)  # blue
        self.eaten_color = (255, 255, 255)  # white
        self.frightened_timer = 0
        self.frightened_duration = 500  # duration update cycles
        self.scatter_timer = 0
        self.scatter_duration = 350  # ~7 seconds at 50fps
        self.chase_duration = 1000   # ~20 seconds at 50fps
        self.home_corner = self._get_home_corner(ghost_type)
        self.spawn_point = Vector2(x, y)
        self.eaten_speed_multiplier = 2.0
        
        # For mode switching
        self.mode_timer = 0
        self.mode_durations = [(self.scatter_duration, GhostState.SCATTER), 
                              (self.chase_duration, GhostState.CHASE)]
        self.mode_index = 0

         # Add variables to detect stuck ghosts
        self.last_position = Vector2(x, y)
        self.stuck_timer = 0
        self.stuck_threshold = 10  # If not moved for 10 frames, ghost is considered stuck
        self.override_direction = None
        self.override_timer = 0
        
    def _get_home_corner(self, ghost_type):
        # Define scatter corners for each ghost
        if ghost_type == GhostType.BLINKY:  # Red
            return Vector2(18 * 30, 0)      # Top-right corner
        elif ghost_type == GhostType.PINKY:  # Pink
            return Vector2(0, 0)            # Top-left corner
        elif ghost_type == GhostType.INKY:   # Cyan
            return Vector2(18 * 30, 20 * 30)  # Bottom-right corner
        elif ghost_type == GhostType.CLYDE:  # Orange
            return Vector2(0, 20 * 30)      # Bottom-left corner
        return Vector2(0, 0)  # Default

    def get_possible_directions(self, maze):
        possible = []
        for direction in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
            if self.can_move_in_direction(direction, maze): 
                possible.append(direction)
        return possible
    
    def choose_direction(self, maze, player):
        possible_directions = self.get_possible_directions(maze)
        
        # If we have an override direction from being stuck, use it
        if self.override_direction and self.override_direction in possible_directions:
            if self.override_timer > 0:
                self.override_timer -= 1
                return self.override_direction
            else:
                self.override_direction = None
        
        # Remove reverse direction unless it's the only option
        if len(possible_directions) > 1 and self.direction != Vector2(0, 0):
            opposite = self.direction * -1
            if opposite in possible_directions:
                possible_directions.remove(opposite)
        
        if not possible_directions:
            return Vector2(0, 0)
        
        if self.state == GhostState.FRIGHTENED:
            # Random movement during frightened mode
            return random.choice(possible_directions)
        
        elif self.state == GhostState.EATEN:
            # Head directly to spawn point
            return self._choose_direction_to_target(possible_directions, self.spawn_point)
        
        elif self.state == GhostState.SCATTER:
            # Head to home corner
            return self._choose_direction_to_target(possible_directions, self.home_corner)
        
        elif self.state == GhostState.CHASE:
            # Each ghost has a unique targeting strategy
            target = self._get_chase_target(player, maze)
            return self._choose_direction_to_target(possible_directions, target)
        
        # Default behavior if no state matches
        return random.choice(possible_directions)
    
    def _choose_direction_to_target(self, possible_directions, target_pos):
        # Find direction that minimizes distance to target
        best_dist = float('inf')
        best_dir = possible_directions[0]
        
        for direction in possible_directions:
            next_pos = self.position + direction * 30  # Approximating one tile distance
            dist = (next_pos - target_pos).length_squared()  # Squared for efficiency
            if dist < best_dist:
                best_dist = dist
                best_dir = direction
        
        return best_dir
    
    def _get_chase_target(self, player, maze):
        if self.ghost_type == GhostType.BLINKY:  # Red - direct chase
            return player.position
        
        elif self.ghost_type == GhostType.PINKY:  # Pink - ambush ahead
            # Target 4 tiles ahead of player
            target = player.position + player.direction * 4 * maze.tile_size
            # Classic Pac-Man bug: when facing up, also offset left
            if player.direction.y < 0:
                target += Vector2(-4 * maze.tile_size, 0)
            return target
        
        elif self.ghost_type == GhostType.INKY:  # Cyan - complex targeting
            # Need Blinky's position for calculation
            blinky_pos = None
            # This would require access to all ghosts
            # As a workaround, if not available, use a default value
            if hasattr(player, 'ghosts') and len(player.ghosts) > 0:
                for ghost in player.ghosts:
                    if ghost.ghost_type == GhostType.BLINKY:
                        blinky_pos = ghost.position
                        break
            
            # 2 tiles ahead of player
            pivot = player.position + player.direction * 2 * maze.tile_size
            
            # Classic Pac-Man bug: when facing up, also offset left
            if player.direction.y < 0:
                pivot += Vector2(-2 * maze.tile_size, 0)
            
            if blinky_pos:
                # Vector from Blinky to pivot point, doubled
                offset = pivot - blinky_pos
                return pivot + offset
            else:
                # Fallback if can't find Blinky
                return pivot
        
        elif self.ghost_type == GhostType.CLYDE:  # Orange - shy behavior
            # Chase directly if far, scatter if close
            distance_to_player = (self.position - player.position).length()
            if distance_to_player > 8 * maze.tile_size:
                return player.position
            else:
                return self.home_corner
        
        # Default fallback
        return player.position
    
    def can_move_in_direction(self, direction, maze):
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
            self.direction = self.direction * -1  # Reverse direction
            self.speed = self.original_speed * 0.5  # Slow down
    
    def exit_frightened_mode(self):
        if self.state == GhostState.FRIGHTENED:
            # Return to previous mode based on timer
            self.update_mode()
            self.state = GhostState.CHASE
            self.speed = self.original_speed
    
    def update_mode(self):
        # Check if we should switch between scatter and chase
        current_duration, current_state = self.mode_durations[self.mode_index]
        self.mode_timer += 1
        
        if self.mode_timer >= current_duration:
            self.mode_timer = 0
            self.mode_index = (self.mode_index + 1) % len(self.mode_durations)
            _, new_state = self.mode_durations[self.mode_index]
            if self.state != GhostState.FRIGHTENED and self.state != GhostState.EATEN:
                self.state = new_state
                # Reverse direction on mode switch
                self.direction = self.direction * -1
    
    def enter_eaten_mode(self):
        self.state = GhostState.EATEN
        self.speed = self.original_speed * self.eaten_speed_multiplier
    
    def reached_home(self):
        return (self.state == GhostState.EATEN and
                (self.position - self.spawn_point).length() < self.speed * 2)
    
    def revive(self):
        self.state = GhostState.SCATTER
        self.speed = self.original_speed
        self.position = Vector2(self.spawn_point)
    
    def update(self, maze, player):
        # Handle mode switching for scatter/chase
        if self.state != GhostState.FRIGHTENED and self.state != GhostState.EATEN:
            self.update_mode()
        
        # Update frightened timer
        if self.state == GhostState.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.exit_frightened_mode()
        
        # Check if eaten ghost has reached home
        if self.reached_home():
            self.revive()
        
        # Check for stuck ghosts (haven't moved significantly)
        distance_moved = (self.position - self.last_position).length()
        if distance_moved < 0.5:  # If barely moved
            self.stuck_timer += 1
            if self.stuck_timer >= self.stuck_threshold:
                # Ghost is stuck, choose a random direction to escape
                possible = self.get_possible_directions(maze)
                if possible:
                    self.override_direction = random.choice(possible)
                    self.override_timer = 10  # Use this direction for next 10 frames
                    self.stuck_timer = 0
        else:
            self.stuck_timer = 0  # Reset stuck timer if moving
        
        # Save current position for next frame's comparison
        self.last_position = Vector2(self.position)
        
        # Movement logic
        if self.is_at_center(maze):
            new_direction = self.choose_direction(maze, player)
            if new_direction != Vector2(0, 0):
                self.direction = new_direction
                # Snap to grid when turning to prevent getting stuck on walls
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
        
        if self.direction:
            new_pos = self.position + self.direction * self.speed
            if not maze.is_wall(new_pos.x, new_pos.y):
                self.position = new_pos
            else:
                # Try to unstick from wall if needed
                self.unstick_from_wall(maze, player)
                
    def unstick_from_wall(self, maze, player):
        """Attempt to recover from being stuck against a wall"""
        # First try: snap to grid and rechoose direction
        center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
        self.position.x = center_x
        self.position.y = center_y
        
        # Force a random direction if we're in a tight spot
        if self.stuck_timer > 5:
            possible = self.get_possible_directions(maze)
            if possible:
                self.direction = random.choice(possible)
        else:
            self.direction = self.choose_direction(maze, player)

    def draw(self, screen):
        current_color = self.color
        if self.state == GhostState.FRIGHTENED:
            # Blinking when frightened mode is ending
            if self.frightened_timer < 100 and self.frightened_timer % 20 < 10:
                current_color = (255, 255, 255)  # White flash
            else:
                current_color = self.frightened_color
        elif self.state == GhostState.EATEN:
            current_color = self.eaten_color

        # Draw ghost body
        pygame.draw.circle(screen, current_color, (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw the bottom wavy part of the ghost
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
        
        # Don't draw eyes in eaten mode - just show eyes moving back to home
        if self.state == GhostState.EATEN:
            eye_color = (0, 0, 255)  # Blue eyes
            left_eye_pos = (int(self.position.x - self.radius/2), int(self.position.y))
            right_eye_pos = (int(self.position.x + self.radius/2), int(self.position.y))
            pygame.draw.circle(screen, eye_color, left_eye_pos, self.radius/3)
            pygame.draw.circle(screen, eye_color, right_eye_pos, self.radius/3)
            return
        
        # Draw eyes for non-eaten states
        eye_color = (255, 255, 255)  # white
        pupil_color = (0, 0, 0)  # black
        
        left_eye_pos = (int(self.position.x - self.radius/2), int(self.position.y - self.radius/4))
        pygame.draw.circle(screen, eye_color, left_eye_pos, self.radius/3)
        pupil_offset = Vector2(self.direction.x, self.direction.y).normalize() * (self.radius/6) if self.direction.length() > 0 else Vector2(0, 0)
        left_pupil_pos = (int(left_eye_pos[0] + pupil_offset.x), int(left_eye_pos[1] + pupil_offset.y))
        pygame.draw.circle(screen, pupil_color, left_pupil_pos, self.radius/6)
        
        right_eye_pos = (int(self.position.x + self.radius/2), int(self.position.y - self.radius/4))
        pygame.draw.circle(screen, eye_color, right_eye_pos, self.radius/3)
        right_pupil_pos = (int(right_eye_pos[0] + pupil_offset.x), int(right_eye_pos[1] + pupil_offset.y))
        pygame.draw.circle(screen, pupil_color, right_pupil_pos, self.radius/6)
        
        # Draw scared state (in frightened mode)
        if self.state == GhostState.FRIGHTENED:
            # Override eyes with white, draw a scared mouth
            pygame.draw.line(screen, (255, 255, 255),
                           (self.position.x - self.radius/2, self.position.y + self.radius/3),
                           (self.position.x + self.radius/2, self.position.y + self.radius/3), 2)