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
        self.color = (255, 255, 0)  # bright yellow
        self.eye_color = (0, 0, 0)
        
        # Enhanced mouth animation
        self.min_mouth_angle = 5  # mouth never fully closes
        self.max_mouth_angle = 45  # maximum mouth opening
        self.mouth_angle = self.max_mouth_angle
        self.animation_timer = 0
        self.animation_speed = 0.1
        
        # Death animation
        self.is_dying = False
        self.death_timer = 0
        self.death_animation_duration = 1.5  # seconds
        
        # Score and power state
        self.score = 0
        self.powered_up = False
        self.power_timer = 0
        self.power_duration = 10  # seconds
        self.power_flash_threshold = 3  # seconds remaining when blinking starts
        
        # For smoother turning
        self.turning_cooldown = 0

    def can_move_in_direction(self, direction, maze):
        next_tile_pos = self.position + direction * maze.tile_size
        return not maze.is_wall(next_tile_pos.x, next_tile_pos.y)
    
    def is_at_center(self, maze):
        center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
        return (abs(self.position.x - center_x) < self.speed and abs(self.position.y - center_y) < self.speed)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and not self.is_dying:
            if event.key in [pygame.K_LEFT, pygame.K_q]: 
                self.next_direction = Vector2(-1, 0)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]: 
                self.next_direction = Vector2(1, 0)
            elif event.key in [pygame.K_UP, pygame.K_z]: 
                self.next_direction = Vector2(0, -1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]: 
                self.next_direction = Vector2(0, 1)

    def update(self, maze, dt=1/60):
        if self.is_dying:
            self.update_death_animation(dt)
            return False
            
        if self.powered_up:
            self.update_power_state(dt)
            
        if self.turning_cooldown > 0:
            self.turning_cooldown -= dt
        
        if self.next_direction and self.is_at_center(maze) and self.turning_cooldown <= 0:
            if self.can_move_in_direction(self.next_direction, maze):
                self.direction = self.next_direction
                # snap to grid when turning
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
                self.next_direction = Vector2(0, 0)
                self.turning_cooldown = 0.1  # prevent rapid turning
        
        if self.direction:
            if not self.can_move_in_direction(self.direction, maze) and self.is_at_center(maze):
                # stop at center if we can't move forward
                center_x, center_y = maze.get_tile_center(self.position.x, self.position.y)
                self.position.x = center_x
                self.position.y = center_y
            else:
                new_pos = self.position + self.direction * self.speed
                if not maze.is_wall(new_pos.x, new_pos.y): 
                    self.position = new_pos
        
        # Update mouth animation - smoother sine wave animation
        self.animation_timer += self.animation_speed
        if self.animation_timer > 2 * math.pi:
            self.animation_timer = 0
            
        # Calculate mouth angle using sine wave between min and max values
        self.mouth_angle = self.min_mouth_angle + (self.max_mouth_angle - self.min_mouth_angle) * (
            (math.sin(self.animation_timer) + 1) / 2)  # Normalized to 0-1 range
            
        # Check if pacman ate anything
        eaten, power = maze.eat_dot(self.position.x, self.position.y)
        if eaten: 
            self.score += 10 if not power else 50
            # Speed up mouth animation briefly when eating
            self.animation_speed = 0.2
            pygame.time.set_timer(pygame.USEREVENT + 1, 250)  # Reset animation speed after delay
            
        if power:
            self.powered_up = True
            self.power_timer = 0
            
        return power
    
    def update_power_state(self, dt):
        self.power_timer += dt
        if self.power_timer >= self.power_duration:
            self.powered_up = False
            
    def update_death_animation(self, dt):
        self.death_timer += dt
        return self.death_timer >= self.death_animation_duration
        
    def trigger_death_animation(self):
        self.is_dying = True
        self.death_timer = 0
        
    def draw(self, screen):
        if self.is_dying:
            self.draw_death_animation(screen)
        else:
            self.draw_normal(screen)
            
    def draw_normal(self, screen):
        # Calculate rotation based on direction
        rotation = 0
        if self.direction.x < 0: rotation = 180
        elif self.direction.x > 0: rotation = 0
        elif self.direction.y < 0: rotation = 90
        elif self.direction.y > 0: rotation = 270
        
        # Get pacman color - flash if power is ending
        color = self.color
        if self.powered_up and self.power_timer > self.power_duration - self.power_flash_threshold:
            if int(self.power_timer * 5) % 2 == 0:
                color = (200, 200, 200)  # Flash to white-yellow
        
        # Draw the circle (body)
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw the mouth - more realistic shape using a pie slice technique
        # Create a polygon for the mouth
        mouth_points = [self.position]
        angle_step = 1  # Smaller steps for smoother curve
        
        for angle in range(-int(self.mouth_angle), int(self.mouth_angle) + 1, angle_step):
            point = self.position + Vector2(self.radius + 1, 0).rotate(angle - rotation)
            mouth_points.append(point)
            
        # Fill the mouth with black
        if len(mouth_points) > 2:  # Need at least 3 points for a polygon
            pygame.draw.polygon(screen, (0, 0, 0), mouth_points)
            
    def draw_death_animation(self, screen):
        # Death animation - pacman gradually disappears with a 360 degree mouth opening
        progress = self.death_timer / self.death_animation_duration
        
        if progress < 1:
            # Full circle with increasingly larger mouth angle (up to 360)
            death_angle = min(359, progress * 360)
            
            # Draw the circle (body)
            pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
            
            # Create a polygon for the expanding mouth
            mouth_points = [self.position]
            angle_step = 5  # Can use larger steps for death animation
            
            for angle in range(-int(death_angle/2), int(death_angle/2) + 1, angle_step):
                point = self.position + Vector2(self.radius + 1, 0).rotate(angle)
                mouth_points.append(point)
                
            # Fill the mouth with black
            if len(mouth_points) > 2:
                pygame.draw.polygon(screen, (0, 0, 0), mouth_points)