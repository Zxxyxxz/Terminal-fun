import os
import sys
import time
import math
import random
from collections import deque

class Advanced3DCoin:
    def __init__(self):
        # Terminal dimensions
        self.width = 120
        self.height = 40
        
        # Coin parameters
        self.radius = 15
        self.thickness = 4
        self.rotation_speed_x = 0.07
        self.rotation_speed_y = 0.05
        self.rotation_speed_z = 0.03
        
        # Advanced rendering parameters
        self.K1 = 50  # Distance from viewer
        self.K2 = 5   # Scaling factor
        
        # Animation state
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.frame_count = 0
        
        # Particle system for sparkles
        self.particles = []
        self.max_particles = 30
        
        # Color codes for terminal
        self.colors = {
            'gold': '\033[93m',
            'silver': '\033[37m',
            'bright': '\033[97m',
            'yellow': '\033[33m',
            'cyan': '\033[96m',
            'magenta': '\033[95m',
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m'
        }
        
        # ASCII gradient for shading
        self.shading_chars = ' .,-~:;=!*#$@'
        
        # Special effects toggle
        self.rainbow_mode = False
        self.pulse_effect = True
        
    def clear_screen(self):
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
    
    def create_happy_face(self, x, y, z, scale=1.0):
        """Generate points for a happy face"""
        points = []
        
        # Eyes
        for dx in [-5, 5]:
            for dy in range(-1, 2):
                points.append((x + dx * scale, y + dy * scale - 3 * scale, z))
        
        # Smile (using parametric curve)
        for t in range(-8, 9):
            smile_x = t * scale
            smile_y = 3 * scale + 0.15 * (t * scale) ** 2
            points.append((x + smile_x, y + smile_y, z))
        
        # Nose
        points.append((x, y - scale, z))
        
        return points
    
    def create_sad_face(self, x, y, z, scale=1.0):
        """Generate points for a sad face"""
        points = []
        
        # Eyes with tears
        for dx in [-5, 5]:
            for dy in range(-1, 2):
                points.append((x + dx * scale, y + dy * scale - 3 * scale, z))
            # Tears
            for tear in range(0, 3):
                points.append((x + dx * scale, y + tear * scale, z))
        
        # Frown (inverted smile)
        for t in range(-8, 9):
            frown_x = t * scale
            frown_y = 5 * scale - 0.15 * (t * scale) ** 2
            points.append((x + frown_x, y + frown_y, z))
        
        return points
    
    def generate_coin_surface(self, face_type='happy'):
        """Generate 3D points for the coin surface with face"""
        points = []
        
        # Create the main coin disc using parametric equations
        for theta in range(0, 360, 5):
            for r in range(0, self.radius, 2):
                rad_theta = math.radians(theta)
                x = r * math.cos(rad_theta)
                y = r * math.sin(rad_theta)
                
                # Front face
                points.append((x, y, self.thickness / 2, 'front'))
                # Back face
                points.append((x, y, -self.thickness / 2, 'back'))
        
        # Create the rim (edge) of the coin
        for theta in range(0, 360, 3):
            rad_theta = math.radians(theta)
            x = self.radius * math.cos(rad_theta)
            y = self.radius * math.sin(rad_theta)
            
            # Create thickness
            for z in range(-self.thickness // 2, self.thickness // 2 + 1):
                points.append((x, y, z, 'edge'))
        
        # Add face features
        if face_type == 'happy':
            face_points = self.create_happy_face(0, 0, self.thickness / 2 + 0.5, 0.7)
            points.extend([(p[0], p[1], p[2], 'face') for p in face_points])
            
            # Back side gets sad face
            sad_points = self.create_sad_face(0, 0, -self.thickness / 2 - 0.5, 0.7)
            points.extend([(p[0], p[1], p[2], 'face') for p in sad_points])
        
        return points
    
    def rotate_point(self, x, y, z):
        """Apply 3D rotation matrices"""
        # Rotation around X axis
        cos_x, sin_x = math.cos(self.angle_x), math.sin(self.angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # Rotation around Y axis
        cos_y, sin_y = math.cos(self.angle_y), math.sin(self.angle_y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
        
        # Rotation around Z axis
        cos_z, sin_z = math.cos(self.angle_z), math.sin(self.angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        
        return x, y, z
    
    def calculate_lighting(self, nx, ny, nz):
        """Calculate Phong lighting model"""
        # Light direction (normalized)
        lx, ly, lz = 0.5, 0.5, -0.7
        
        # Diffuse lighting
        dot_product = nx * lx + ny * ly + nz * lz
        diffuse = max(0, dot_product)
        
        # Specular lighting
        reflection = 2 * dot_product
        rx = reflection * nx - lx
        ry = reflection * ny - ly
        rz = reflection * nz - lz
        
        # View vector (looking at origin)
        view_dot = max(0, -rz)
        specular = view_dot ** 20  # Shininess factor
        
        # Ambient light
        ambient = 0.2
        
        return min(1, ambient + diffuse * 0.7 + specular * 0.3)
    
    def update_particles(self):
        """Update particle system for sparkle effects"""
        # Add new particles
        if len(self.particles) < self.max_particles and random.random() < 0.3:
            angle = random.uniform(0, 2 * math.pi)
            r = self.radius + random.uniform(2, 5)
            self.particles.append({
                'x': r * math.cos(angle),
                'y': r * math.sin(angle),
                'z': random.uniform(-5, 5),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'vz': random.uniform(-0.3, 0.3),
                'life': 20,
                'char': random.choice(['*', '·', '°', '˚', '✦', '✧', '⋆', '₊'])
            })
        
        # Update existing particles
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['z'] += p['vz']
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def get_rainbow_color(self, index):
        """Generate rainbow colors"""
        colors = [
            '\033[91m',  # Red
            '\033[93m',  # Yellow
            '\033[92m',  # Green
            '\033[96m',  # Cyan
            '\033[94m',  # Blue
            '\033[95m',  # Magenta
        ]
        return colors[index % len(colors)]
    
    def render_frame(self):
        """Render a single frame of the animation"""
        # Initialize buffers
        output = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        zbuffer = [[float('-inf') for _ in range(self.width)] for _ in range(self.height)]
        
        # Generate coin points
        points = self.generate_coin_surface()
        
        # Pulse effect
        pulse = 1.0
        if self.pulse_effect:
            pulse = 1.0 + 0.1 * math.sin(self.frame_count * 0.1)
        
        # Render coin points
        for point in points:
            x, y, z = point[0] * pulse, point[1] * pulse, point[2]
            point_type = point[3] if len(point) > 3 else 'front'
            
            # Apply rotation
            x, y, z = self.rotate_point(x, y, z)
            
            # Perspective projection
            if z + self.K1 <= 0:
                continue
            
            ooz = 1 / (z + self.K1)
            xp = int(self.width / 2 + x * ooz * self.K1)
            yp = int(self.height / 2 - y * ooz * self.K1 / 2)  # Aspect ratio correction
            
            if 0 <= xp < self.width and 0 <= yp < self.height:
                if ooz > zbuffer[yp][xp]:
                    zbuffer[yp][xp] = ooz
                    
                    # Calculate lighting
                    nx, ny, nz = x / self.radius, y / self.radius, z / self.thickness
                    norm = math.sqrt(nx**2 + ny**2 + nz**2)
                    if norm > 0:
                        nx, ny, nz = nx/norm, ny/norm, nz/norm
                    
                    brightness = self.calculate_lighting(nx, ny, nz)
                    char_index = int(brightness * (len(self.shading_chars) - 1))
                    char = self.shading_chars[char_index]
                    
                    # Special characters for faces
                    if point_type == 'face':
                        if z > 0:  # Front face (happy)
                            char = random.choice(['☺', '◉', '●', '@']) if char != ' ' else char
                        else:  # Back face (sad)
                            char = random.choice(['☹', '○', '◌', '#']) if char != ' ' else char
                    elif point_type == 'edge':
                        char = random.choice(['║', '│', '┃', '█']) if char != ' ' else char
                    
                    # Apply color
                    if self.rainbow_mode:
                        color = self.get_rainbow_color(int(math.degrees(math.atan2(y, x))))
                    else:
                        if brightness > 0.8:
                            color = self.colors['bright'] + self.colors['bold']
                        elif brightness > 0.6:
                            color = self.colors['gold']
                        elif brightness > 0.3:
                            color = self.colors['yellow']
                        else:
                            color = self.colors['dim']
                    
                    output[yp][xp] = color + char + self.colors['reset']
        
        # Render particles
        for particle in self.particles:
            x, y, z = self.rotate_point(particle['x'], particle['y'], particle['z'])
            
            if z + self.K1 <= 0:
                continue
            
            ooz = 1 / (z + self.K1)
            xp = int(self.width / 2 + x * ooz * self.K1)
            yp = int(self.height / 2 - y * ooz * self.K1 / 2)
            
            if 0 <= xp < self.width and 0 <= yp < self.height:
                color = random.choice([
                    self.colors['cyan'],
                    self.colors['magenta'],
                    self.colors['bright']
                ])
                output[yp][xp] = color + particle['char'] + self.colors['reset']
        
        return output
    
    def add_frame_decorations(self, output):
        """Add decorative elements around the frame"""
        # Top border
        border = "═" * self.width
        print(self.colors['gold'] + "╔" + border[:self.width-2] + "╗" + self.colors['reset'])
        
        # Main content with side borders
        for row in output:
            print(self.colors['gold'] + "║" + self.colors['reset'] + 
                  ''.join(row[:self.width-2]) + 
                  self.colors['gold'] + "║" + self.colors['reset'])
        
        # Bottom border with info
        info = f" Frame: {self.frame_count} | Particles: {len(self.particles)} | Mode: {'Rainbow' if self.rainbow_mode else 'Gold'} "
        border_with_info = "═" * ((self.width - len(info)) // 2) + info + "═" * ((self.width - len(info)) // 2)
        print(self.colors['gold'] + "╚" + border_with_info[:self.width-2] + "╝" + self.colors['reset'])
    
    def run(self):
        """Main animation loop"""
        try:
            while True:
                self.clear_screen()
                
                # Update animation state
                self.angle_x += self.rotation_speed_x
                self.angle_y += self.rotation_speed_y
                self.angle_z += self.rotation_speed_z
                self.frame_count += 1
                
                # Toggle rainbow mode periodically
                if self.frame_count % 200 == 0:
                    self.rainbow_mode = not self.rainbow_mode
                
                # Update particles
                self.update_particles()
                
                # Render and display frame
                frame = self.render_frame()
                self.add_frame_decorations(frame)
                
                # Control frame rate
                time.sleep(0.03)
                
        except KeyboardInterrupt:
            print("\n" + self.colors['gold'] + "✨ Animation ended! Thanks for watching! ✨" + self.colors['reset'])

if __name__ == '__main__':
    coin = Advanced3DCoin()
    coin.run()
