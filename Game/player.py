import pygame
import math

DIRECTIONS = {
    "UP": (0, -1), 
    "RIGHT": (1, 0), 
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
}

class Player:
    def __init__(self, x=40, y=40):
        self.x = x 
        self.y = y
        self.radius = 15
        self.angle = 0
        self.speed = 4
        self.mouth_angle = 45
        self.score = 0
        self.color = (255, 255, 0) # YELLOW
        self.direction = DIRECTIONS["RIGHT"]
        self.next_direction = DIRECTIONS["RIGHT"]

    def is_centered(self):
        # Check if player is centered on a tile (x and y are multiples of 40)
        return abs(self.x % 40) < 40 and abs(self.y % 40) < 40

    def move(self, maze):
        # Store next direction based on key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.next_direction = DIRECTIONS["LEFT"]
        if keys[pygame.K_RIGHT]:
            self.next_direction = DIRECTIONS["RIGHT"]
        if keys[pygame.K_UP]:
            self.next_direction = DIRECTIONS["UP"]
        if keys[pygame.K_DOWN]:
            self.next_direction = DIRECTIONS["DOWN"]

        # Try to change direction if centered on a tile
        if self.is_centered() and self.next_direction != self.direction:
            if not maze.check_collision(self.x, self.y, self.next_direction):
                self.direction = self.next_direction

        # Calculate new position based on current direction
        new_x = self.x
        new_y = self.y
        
        if self.direction == DIRECTIONS["LEFT"]:
            new_x -= self.speed
            self.angle = 180
        if self.direction == DIRECTIONS["RIGHT"]:
            new_x += self.speed
            self.angle = 0
        if self.direction == DIRECTIONS["UP"]:
            new_y -= self.speed
            self.angle = 90
        if self.direction == DIRECTIONS["DOWN"]:
            new_y += self.speed
            self.angle = 270

        # Move if no collision in current direction
        if not maze.check_collision(self.x, self.y, self.direction):
            self.x = new_x
            self.y = new_y
        
        if maze.eat_dot(self.x, self.y):
            self.score += 10

    def draw(self, screen):
        # Offset position by half cell size (20 pixels) for display
        display_x = self.x + 20
        display_y = self.y + 20
        
        start_angle = self.angle + self.mouth_angle
        end_angle = self.angle - self.mouth_angle
        pygame.draw.arc(
            screen, 
            self.color,
            (
                display_x - self.radius,
                display_y - self.radius,
                self.radius * 2,
                self.radius * 2
            ),
            math.radians(start_angle),
            math.radians(end_angle), 
            self.radius
        )

    def reset(self, x=40, y=40):
        self.x = x
        self.y = y
        self.angle = 0
        self.direction = DIRECTIONS["RIGHT"]
        self.next_direction = DIRECTIONS["RIGHT"]
        self.score = 0
