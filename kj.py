import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import pygame
from pygame.locals import *
import random
import numpy as np

pygame.init()

# SQLite3 setup
conn = sqlite3.connect('car_game.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS scores (score INTEGER)''')
conn.commit()

# PyQt5 setup
class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Car Game Menu')
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()
        
        self.label = QLabel('Car Game')
        layout.addWidget(self.label)
        
        self.start_button = QPushButton('Start Game')
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)
        
        self.quit_button = QPushButton('Quit')
        self.quit_button.clicked.connect(self.quit_game)
        layout.addWidget(self.quit_button)
        
        self.setLayout(layout)
    
    def start_game(self):
        self.close()
        start_pygame_game()
    
    def quit_game(self):
        conn.close()
        sys.exit()

class GameOverWindow(QWidget):
    def __init__(self, score):
        super().__init__()
        self.score = score
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Game Over')
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()
        
        self.label = QLabel(f'Game Over. ')
        layout.addWidget(self.label)
        
        self.play_again_button = QPushButton('Play Again')
        self.play_again_button.clicked.connect(self.play_again)
        layout.addWidget(self.play_again_button)
        
        self.quit_button = QPushButton('Quit')
        self.quit_button.clicked.connect(self.quit_game)
        layout.addWidget(self.quit_button)
        
        self.setLayout(layout)
    
    def play_again(self):
        self.close()
        start_pygame_game()

    def quit_game(self):
        conn.close()
        sys.exit()

def start_pygame_game():
    # Create the window
    width = 500
    height = 500
    screen_size = (width, height)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Car Game')

    # Colors
    gray = (100, 100, 100)
    green = (76, 208, 56)
    red = (200, 0, 0)
    white = (255, 255, 255)
    yellow = (255, 232, 0)

    # Road and marker sizes
    road_width = 300
    marker_width = 10
    marker_height = 50

    # Lane coordinates
    left_lane = 150
    center_lane = 250
    right_lane = 350
    lanes = [left_lane, center_lane, right_lane]

    # Road and edge markers
    road = (100, 0, road_width, height)
    left_edge_marker = (95, 0, marker_width, height)
    right_edge_marker = (395, 0, marker_width, height)

    # For animating movement of the lane markers
    lane_marker_move_y = 0

    # Player's starting coordinates
    player_x = 250
    player_y = 400

    # Frame settings
    clock = pygame.time.Clock()
    fps = 120

    # Game settings
    gameover = False
    speed = 2
    score = 0

    class Vehicle(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            super().__init__()
            # Scale the image down so it's not wider than the lane
            image_scale = 45 / image.get_rect().width
            new_width = int(image.get_rect().width * image_scale)
            new_height = int(image.get_rect().height * image_scale)
            self.image = pygame.transform.scale(image, (new_width, new_height))
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]

    class PlayerVehicle(Vehicle):
        def __init__(self, x, y):
            image = pygame.image.load(r'C:/Users/hp/Pictures/car.png')
            super().__init__(image, x, y)

    # Sprite groups
    player_group = pygame.sprite.Group()
    vehicle_group = pygame.sprite.Group()

    # Create the player's car
    player = PlayerVehicle(player_x, player_y)
    player_group.add(player)

    # Load the vehicle images
    image_filenames = [
        r'C:/Users/hp/Pictures/pickup_truck.png',
        r'C:/Users/hp/Pictures/semi_trailer.png',
        r'C:/Users/hp/Pictures/taxi.png',
        r'C:/Users/hp/Pictures/van.png'
    ]
    vehicle_images = [pygame.image.load(image_filename) for image_filename in image_filenames]

    # Load the crash image
    crash = pygame.image.load(r'C:/Users/hp/Pictures/crash.png')
    crash_rect = crash.get_rect()

    # Game loop
    running = True
    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Move the player's car using the left/right arrow keys
            if event.type == KEYDOWN:
                if event.key == K_LEFT and player.rect.center[0] > left_lane:
                    player.rect.x -= 100
                elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                    player.rect.x += 100

                # Check if there's a side swipe collision after changing lanes
                for vehicle in vehicle_group:
                    if pygame.sprite.collide_rect(player, vehicle):
                        gameover = True
                        # Place the player's car next to other vehicle
                        # and determine where to position the crash image
                        if event.key == K_LEFT:
                            player.rect.left = vehicle.rect.right
                            crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                        elif event.key == K_RIGHT:
                            player.rect.right = vehicle.rect.left
                            crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

        # Draw the grass
        screen.fill(green)

        # Draw the road
        pygame.draw.rect(screen, gray, road)

        # Draw the edge markers
        pygame.draw.rect(screen, yellow, left_edge_marker)
        pygame.draw.rect(screen, yellow, right_edge_marker)

        # Draw the lane markers
        lane_marker_move_y += speed * 2
        if lane_marker_move_y >= marker_height * 2:
            lane_marker_move_y = 0
        for y in range(marker_height * -2, height, marker_height * 2):
            pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
            pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

        # Draw the player's car
        player_group.draw(screen)

        # Add a vehicle
        if len(vehicle_group) < 2:
            # Ensure there's enough gap between vehicles
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False

            if add_vehicle:
                # Select a random lane
                lane = random.choice(lanes)
                # Select a random vehicle image
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, height / -2)
                vehicle_group.add(vehicle)

        # Make the vehicles move
        for vehicle in vehicle_group:
            vehicle.rect.y += speed

            # Remove vehicle once it goes off screen
            if vehicle.rect.top >= height:
                vehicle.kill()
                # Add to score
                score += 1
                # Speed up the game after passing 5 vehicles
                if score > 0 and score % 5 == 0:
                    speed += 1

        # Draw the vehicles
        vehicle_group.draw(screen)

        # Display the score
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Score: ' + str(score), True, white)
        text_rect = text.get_rect()
        text_rect.center = (50, 400)
        screen.blit(text, text_rect)

        # Check if there's a head-on collision
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]

        # Display game over
        if gameover:
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, red, (0, 50, width, 100))
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render('Game over. Play again? (Enter Y or N)', True, white)
            text_rect = text.get_rect()
            text_rect.center = (width / 2, 100)
            screen.blit(text, text_rect)

        pygame.display.update()

        # Wait for user's input to play again or exit
        while gameover:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    gameover = False
                    running = False
                # Get the user's input (y or n)
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        # Reset the game
                        gameover = False
                        speed = 2
                        score = 0
                        vehicle_group.empty()
                        player.rect.center = [player_x, player_y]
                    elif event.key == K_n:
                        # Save the score to the database
                        c.execute("INSERT INTO scores (score) VALUES (?)", (score,))
                        conn.commit()
                        # Show game over window
                        gameover = False
                        running = False
                        game_over_window = GameOverWindow(score)
                        game_over_window.show()
                        return

    pygame.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu_window = MenuWindow()
    menu_window.show()
    sys.exit(app.exec_())
