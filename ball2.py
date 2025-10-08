import os
import sys
import time
import random

def get_terminal_size():
    size = os.get_terminal_size()
    width = size.columns
    height = size.lines
    return width, height

def clear_screen():
    sys.stdout.write('\033[2J')
    sys.stdout.write('\033[H')
    sys.stdout.flush()

class Ball:
    def __init__(self, x, y, vx, vy):
        self.x = x  # x position (float)
        self.y = y  # y position (float)
        self.vx = vx  # x velocity
        self.vy = vy  # y velocity

def main():
    width, height = get_terminal_size()
    # Ensure minimum size for proper animation
    width = max(20, width)
    height = max(10, height)
    max_balls = 100  # Limit to prevent too many balls
    balls = []
    # Initialize one ball at a random position
    initial_x = random.uniform(1, width - 2)
    initial_y = random.uniform(1, height - 2)
    initial_vx = random.choice([-1, 1]) * random.uniform(0.5, 1.0)
    initial_vy = random.choice([-1, 1]) * random.uniform(0.5, 1.0)
    balls.append(Ball(initial_x, initial_y, initial_vx, initial_vy))
    
    try:
        while True:
            clear_screen()
            # Create an empty grid with spaces
            grid = [[' ' for _ in range(width)] for _ in range(height)]
            # Draw the balls
            for ball in balls:
                x_int = int(round(ball.x))
                y_int = int(round(ball.y))
                if 0 <= x_int < width and 0 <= y_int < height:
                    grid[y_int][x_int] = 'O'
            # Print the grid
            for row in grid:
                print(''.join(row))
            # Update the positions and velocities
            new_balls = []
            for ball in balls:
                ball.x += ball.vx
                ball.y += ball.vy
                split = False
                # Check for collision with walls
                if ball.x <= 0:
                    split = True
                    ball.x = 0
                    ball.vx = abs(ball.vx)
                elif ball.x >= width - 1:
                    split = True
                    ball.x = width - 1
                    ball.vx = -abs(ball.vx)
                if ball.y <= 0:
                    split = True
                    ball.y = 0
                    ball.vy = abs(ball.vy)
                elif ball.y >= height - 1:
                    split = True
                    ball.y = height - 1
                    ball.vy = -abs(ball.vy)
                if split and len(balls) + len(new_balls) < max_balls:
                    # Split the ball into two
                    new_vx = random.choice([-1, 1]) * random.uniform(0.5, 1.0)
                    new_vy = random.choice([-1, 1]) * random.uniform(0.5, 1.0)
                    new_ball = Ball(ball.x, ball.y, new_vx, new_vy)
                    new_balls.append(new_ball)
            balls.extend(new_balls)
            # Control the animation speed (increase sleep time for slower animation)
            # time.sleep(0.1)
    except KeyboardInterrupt:
        pass  # Allow the user to exit with Ctrl+C

if __name__ == "__main__":
    main()
