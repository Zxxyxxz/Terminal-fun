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
    # Terminal dimensions
    width = 80
    height = 24

    # Parameters for the coin
    angle_increment = 10  # Adjust for rotation speed

    try:
        angle = 0.0
        while True:
            clear_screen()
            output = [' ' for _ in range(width * height)]
            zbuffer = [float('-inf') for _ in range(width * height)]

            # Parameters for the ellipse (coin projection)
            for y in range(-10, 11):
                for x in range(-20, 21):
                    # Calculate the rotated coordinates
                    theta = angle
                    cos_theta = math.cos(theta)
                    sin_theta = math.sin(theta)

                    # Rotate the point around the X-axis to simulate tilting
                    X = x
                    Y = y * cos_theta
                    Z = y * sin_theta

                    # Perspective projection
                    K1 = 30  # Distance from viewer to screen
                    if Z + K1 == 0:
                        continue  # Avoid division by zero
                    ooz = 1 / (Z + K1)

                    xp = int(width / 2 + X * ooz * K1)
                    yp = int(height / 2 - Y * ooz * K1)

                    idx = xp + yp * width
                    if 0 <= idx < len(output):
                        if ooz > zbuffer[idx]:
                            zbuffer[idx] = ooz
                            # Use luminance to simulate shading
                            luminance = max(0, cos_theta)
                            if luminance > 0.7:
                                char = '@'
                            elif luminance > 0.5:
                                char = '#'
                            elif luminance > 0.3:
                                char = '*'
                            elif luminance > 0.1:
                                char = ':'
                            else:
                                char = '.'
                            output[idx] = char

            # Render the frame
            for i in range(0, len(output), width):
                print(''.join(output[i:i+width]))

            # Update rotation angle
            angle += angle_increment
            if angle >= 2 * math.pi:
                angle -= 2 * math.pi

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass  # Allow the user to exit with Ctrl+C

if __name__ == '__main__':
    main()
