import os
import sys
import time
import math

def clear_screen():
    # Clear the terminal screen
    sys.stdout.write('\033[2J')
    sys.stdout.write('\033[H')
    sys.stdout.flush()

def main():
    # Terminal dimensions (adjust if necessary)
    width = 80
    height = 24

    # Coin parameters
    radius = 10  # Radius of the coin
    angle_increment = 0.1  # Rotation speed

    try:
        angle = 0.0
        while True:
            clear_screen()
            output = [[' ' for _ in range(width)] for _ in range(height)]
            zbuffer = [[float('-inf') for _ in range(width)] for _ in range(height)]

            # Loop over points on the coin's surface
            for theta in frange(0, 2 * math.pi, 0.05):
                for r in frange(-radius, radius, 0.5):
                    x = r * math.cos(theta)
                    y = r * math.sin(theta)
                    z = 0

                    # Rotate around the vertical (z) axis
                    cos_angle = math.cos(angle)
                    sin_angle = math.sin(angle)
                    x_rot = x * cos_angle - y * sin_angle
                    y_rot = x * sin_angle + y * cos_angle
                    z_rot = z

                    # Perspective projection
                    K1 = 20  # Scaling factor
                    viewer_distance = 50  # Distance from the viewer
                    ooz = 1 / (viewer_distance - z_rot)
                    xp = int(width / 2 + x_rot * K1 * ooz)
                    yp = int(height / 2 - y_rot * K1 * ooz)  # Inverted y-axis for correct orientation

                    # Check boundaries and update output
                    if 0 <= xp < width and 0 <= yp < height:
                        if ooz > zbuffer[yp][xp]:
                            zbuffer[yp][xp] = ooz
                            output[yp][xp] = 'O'

            # Render the frame
            for row in output:
                print(''.join(row))

            # Update rotation angle
            angle += angle_increment
            if angle >= 2 * math.pi:
                angle -= 2 * math.pi

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass  # Allow the user to exit with Ctrl+C

def frange(start, stop, step):
    # Floating point range generator
    while start < stop:
        yield start
        start += step

if __name__ == '__main__':
    main()
