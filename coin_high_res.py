import os
import sys
import time
import math
import numpy as np

class HighResCoin:
    def __init__(self):
        # Terminal settings - much higher resolution
        self.width = 160
        self.height = 50
        
        # Coin parameters
        self.radius = 20
        self.thickness = 0.15  # Relative thickness
        
        # Rotation angles
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
        # Animation speed
        self.speed_x = 0.03
        self.speed_y = 0.05
        self.speed_z = 0.02
        
        # Frame counter
        self.frame = 0
        
        # ASCII gradient for fine detail (from darkest to brightest)
        self.gradient = ' ·․∙‧•◦○●'
        self.edge_chars = '─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬'
        
        # Fine-detail ASCII for smooth rendering
        self.fine_ascii = {
            'empty': ' ',
            'light': '·',
            'medium': '▪',
            'heavy': '█',
            'edge_h': '─',
            'edge_v': '│',
            'edge_curve': '╱',
            'face_eye': '◉',
            'face_mouth': '‿',
            'face_sad': '︵'
        }
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def bresenham_circle(self, center_x, center_y, radius, z=0):
        """Generate circle points using Bresenham's algorithm for smooth edges"""
        points = []
        x = 0
        y = radius
        d = 3 - 2 * radius
        
        while y >= x:
            # Generate 8 octants for complete circle
            octants = [
                (center_x + x, center_y + y, z),
                (center_x - x, center_y + y, z),
                (center_x + x, center_y - y, z),
                (center_x - x, center_y - y, z),
                (center_x + y, center_y + x, z),
                (center_x - y, center_y + x, z),
                (center_x + y, center_y - x, z),
                (center_x - y, center_y - x, z)
            ]
            points.extend(octants)
            
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
                
        return points
    
    def generate_filled_circle(self, center_x, center_y, radius, z=0):
        """Generate a filled circle with anti-aliasing"""
        points = []
        
        # Use supersampling for smoother edges
        for y in range(-radius, radius + 1):
            for x in range(-radius, radius + 1):
                # Calculate distance from center
                dist = math.sqrt(x*x + y*y)
                
                if dist <= radius:
                    # Anti-aliasing: calculate intensity based on distance to edge
                    edge_dist = radius - dist
                    if edge_dist < 1:
                        intensity = edge_dist  # Smooth edge
                    else:
                        intensity = 1.0  # Solid interior
                    
                    points.append((
                        center_x + x,
                        center_y + y,
                        z,
                        intensity
                    ))
                    
        return points
    
    def create_face_points(self, face_type='happy'):
        """Create high-resolution face with clear features"""
        points = []
        
        if face_type == 'happy':
            # Eyes - clear circles
            left_eye = self.bresenham_circle(-8, -5, 2, 0.1)
            right_eye = self.bresenham_circle(8, -5, 2, 0.1)
            points.extend([(x, y, z, 'eye') for x, y, z in left_eye])
            points.extend([(x, y, z, 'eye') for x, y, z in right_eye])
            
            # Smile - using parametric curve for smoothness
            for t in np.linspace(-0.7, 0.7, 30):
                x = int(15 * t)
                y = int(5 + 3 * math.cos(t * 2))  # Smile curve
                points.append((x, y, 0.1, 'mouth'))
                
        else:  # sad face
            # Eyes with tears
            left_eye = self.bresenham_circle(-8, -5, 2, -0.1)
            right_eye = self.bresenham_circle(8, -5, 2, -0.1)
            points.extend([(x, y, z, 'eye') for x, y, z in left_eye])
            points.extend([(x, y, z, 'eye') for x, y, z in right_eye])
            
            # Tears
            for i in range(5):
                points.append((-8, -3 + i, -0.1, 'tear'))
                points.append((8, -3 + i, -0.1, 'tear'))
            
            # Frown
            for t in np.linspace(-0.7, 0.7, 30):
                x = int(15 * t)
                y = int(8 - 3 * math.cos(t * 2))  # Frown curve
                points.append((x, y, -0.1, 'mouth'))
                
        return points
    
    def generate_3d_coin(self):
        """Generate complete 3D coin with high resolution"""
        points = []
        
        # Generate main coin body - front and back faces
        front_circle = self.generate_filled_circle(0, 0, self.radius, self.thickness * self.radius)
        back_circle = self.generate_filled_circle(0, 0, self.radius, -self.thickness * self.radius)
        
        # Add faces with proper depth
        points.extend([(x, y, z, 'front', intensity) for x, y, z, intensity in front_circle])
        points.extend([(x, y, z, 'back', intensity) for x, y, z, intensity in back_circle])
        
        # Generate rim (edge) with high detail
        rim_resolution = 120  # High resolution for smooth edge
        for i in range(rim_resolution):
            angle = 2 * math.pi * i / rim_resolution
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            
            # Create thickness with multiple layers
            for z_layer in np.linspace(-self.thickness * self.radius, self.thickness * self.radius, 5):
                points.append((x, y, z_layer, 'rim', 1.0))
        
        # Add face features
        happy_face = self.create_face_points('happy')
        sad_face = self.create_face_points('sad')
        
        # Adjust face positions to be on coin surfaces
        for x, y, z, feature in happy_face:
            points.append((x, y, self.thickness * self.radius + z, feature, 1.0))
        
        for x, y, z, feature in sad_face:
            points.append((x, y, -self.thickness * self.radius + z, feature, 1.0))
            
        return points
    
    def rotate_3d(self, x, y, z):
        """Apply 3D rotation with proper matrix multiplication"""
        # Rotation matrix X
        cos_x, sin_x = math.cos(self.angle_x), math.sin(self.angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # Rotation matrix Y
        cos_y, sin_y = math.cos(self.angle_y), math.sin(self.angle_y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
        
        # Rotation matrix Z
        cos_z, sin_z = math.cos(self.angle_z), math.sin(self.angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        
        return x, y, z
    
    def calculate_lighting(self, x, y, z, normal_z):
        """Calculate lighting with proper shading"""
        # Light vector (from top-right)
        light = np.array([1, -1, -2])
        light = light / np.linalg.norm(light)
        
        # Surface normal approximation
        if abs(x) + abs(y) > 0:
            normal = np.array([x, y, normal_z * self.radius])
            normal = normal / np.linalg.norm(normal)
        else:
            normal = np.array([0, 0, -1 if normal_z < 0 else 1])
        
        # Calculate diffuse lighting
        diffuse = max(0, np.dot(normal, light))
        
        # Add ambient light
        ambient = 0.3
        brightness = min(1, ambient + diffuse * 0.7)
        
        return brightness
    
    def render_frame(self):
        """Render a single frame with high quality"""
        # Create buffers
        buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        zbuffer = [[float('-inf') for _ in range(self.width)] for _ in range(self.height)]
        
        # Generate coin points
        coin_points = self.generate_3d_coin()
        
        # Camera distance
        camera_z = 60
        
        # Render each point
        for point in coin_points:
            x, y, z = point[0], point[1], point[2]
            point_type = point[3] if len(point) > 3 else 'front'
            intensity = point[4] if len(point) > 4 else 1.0
            
            # Apply rotation
            x, y, z = self.rotate_3d(x, y, z)
            
            # Perspective projection
            if z + camera_z <= 0:
                continue
                
            factor = camera_z / (z + camera_z)
            screen_x = int(self.width / 2 + x * factor * 2)
            screen_y = int(self.height / 2 + y * factor)
            
            # Bounds check
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                depth = 1 / (z + camera_z)
                
                if depth > zbuffer[screen_y][screen_x]:
                    zbuffer[screen_y][screen_x] = depth
                    
                    # Calculate lighting
                    brightness = self.calculate_lighting(x, y, z, 1 if z > 0 else -1)
                    brightness *= intensity  # Apply anti-aliasing intensity
                    
                    # Choose character based on type and brightness
                    if point_type == 'eye':
                        char = '●' if brightness > 0.5 else '○'
                    elif point_type == 'mouth':
                        char = '‿' if z > 0 else '︵'
                    elif point_type == 'tear':
                        char = '│'
                    elif point_type == 'rim':
                        # Edge should be clearly defined
                        if abs(x) > abs(y):
                            char = '║' if brightness > 0.5 else '│'
                        else:
                            char = '═' if brightness > 0.5 else '─'
                    elif point_type in ['front', 'back']:
                        # Use gradient for smooth shading
                        if intensity < 0.3:  # Near edge
                            char = '░'
                        elif intensity < 0.7:
                            idx = int(brightness * (len(self.gradient) - 1))
                            char = self.gradient[idx]
                        else:  # Solid interior
                            if brightness > 0.8:
                                char = '█'
                            elif brightness > 0.6:
                                char = '▓'
                            elif brightness > 0.4:
                                char = '▒'
                            elif brightness > 0.2:
                                char = '░'
                            else:
                                char = '·'
                    else:
                        char = '·'
                    
                    buffer[screen_y][screen_x] = char
        
        return buffer
    
    def draw_frame(self, buffer):
        """Draw the frame with proper formatting"""
        # Top border
        print('╔' + '═' * (self.width - 2) + '╗')
        
        # Content with side borders
        for row in buffer:
            print('║' + ''.join(row) + '║')
        
        # Bottom border with info
        info = f" Frame: {self.frame} | Rotation: X:{self.angle_x:.2f} Y:{self.angle_y:.2f} Z:{self.angle_z:.2f} "
        bottom = '╚' + '═' * ((self.width - len(info)) // 2 - 1)
        bottom += info
        bottom += '═' * (self.width - len(bottom) - 1) + '╝'
        print(bottom[:self.width])
    
    def run(self):
        """Main animation loop"""
        try:
            while True:
                self.clear_screen()
                
                # Update rotation
                self.angle_x += self.speed_x
                self.angle_y += self.speed_y
                self.angle_z += self.speed_z
                self.frame += 1
                
                # Keep angles in range
                self.angle_x %= (2 * math.pi)
                self.angle_y %= (2 * math.pi)
                self.angle_z %= (2 * math.pi)
                
                # Render and display
                buffer = self.render_frame()
                self.draw_frame(buffer)
                
                # Control frame rate
                time.sleep(0.03)
                
        except KeyboardInterrupt:
            print("\n✨ Coin animation stopped ✨")

if __name__ == '__main__':
    coin = HighResCoin()
    coin.run()