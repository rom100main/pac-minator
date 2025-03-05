import pygame
import math

DIRECTIONS = {
    "UP": (0, -1), 
    "RIGHT": (1, 0), 
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
}

class Player:
    def __init__(self, x=60, y=60):
        self.x = x 
        self.y = y
        self.radius = 15
        self.angle = 0
        self.speed = 4
        self.mouth_angle = 45
        self.score = 0
        self.color = (255, 255, 0) # YELLOW
        self.direction = DIRECTIONS["RIGHT"] 

    def move(self, maze):
        new_x = self.x
        new_y = self.y
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction = DIRECTIONS["LEFT"]
        if keys[pygame.K_RIGHT]:
            self.direction = DIRECTIONS["RIGHT"]
        if keys[pygame.K_UP]:
            self.direction = DIRECTIONS["UP"]
        if keys[pygame.K_DOWN]:
            self.direction = DIRECTIONS["DOWN"]
        
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


        if not maze.check_collision(self.x, self.y, self.direction):
            self.x = new_x
            self.y = new_y
        
        if maze.eat_dot(self.x, self.y):
            self.score += 10

    def draw(self, screen):
        start_angle = self.angle + self.mouth_angle
        end_angle = self.angle - self.mouth_angle
        pygame.draw.arc(
            screen, 
            self.color,
            (
                self.x - self.radius,
                self.y - self.radius,
                self.radius * 2,
                self.radius * 2
            ),
            math.radians(start_angle),
            math.radians(end_angle), 
            self.radius
        )

    def reset(self, x=60, y=60):
        self.x = x
        self.y = y
        self.angle = 0
        self.score = 0
