import os
import sys
import time
import math
import random
import curses
from enum import Enum

class RenderMode(Enum):
    MATRIX = 1
    MONOCHROME = 2
    MINIMAL = 3

class CoinWindow:
    """Individual viewport for coin rendering"""
    def __init__(self, x, y, width, height, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.zbuffer = []
        self.buffer = []
        
    def clear(self):
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.zbuffer = [[float('-inf') for _ in range(self.width)] for _ in range(self.height)]

class Matrix3DCoin:
    def __init__(self):
        # Display settings
        self.render_mode = RenderMode.MATRIX
        self.show_particles = False
        self.show_trails = True
        
        # Coin parameters
        self.coin_radius = 12
        self.coin_thickness = 3
        
        # Animation parameters
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.rotation_speed = 0.05
        self.time_offset = 0
        
        # Camera distance
        self.camera_distance = 40
        
        # Matrix rain effect
        self.matrix_chars = "01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
        self.matrix_drops = []
        
        # Trail effect for coin movement
        self.coin_trail = []
        self.max_trail_length = 5
        
    def init_curses(self, stdscr):
        """Initialize curses color pairs"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(30)  # 30ms refresh
        
        # Initialize color pairs for Matrix effect
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            
            # Matrix green gradient
            curses.init_pair(1, curses.COLOR_GREEN, -1)      # Bright green
            curses.init_pair(2, curses.COLOR_WHITE, -1)      # White (brightest)
            curses.init_pair(3, 22, -1)                      # Dark green
            curses.init_pair(4, curses.COLOR_CYAN, -1)       # Cyan accent
            curses.init_pair(5, curses.COLOR_YELLOW, -1)     # Gold for borders
            
    def create_simple_happy_face(self):
        """Create a minimalist happy face using ASCII"""
        face = []
        # Eyes - simple dots
        face.append((-3, -2, 0, '●'))
        face.append((3, -2, 0, '●'))
        
        # Smile - simple arc
        for x in range(-4, 5):
            y = int(2 + 0.2 * abs(x))
            face.append((x, y, 0, '‾'))
            
        return face
    
    def create_simple_sad_face(self):
        """Create a minimalist sad face using ASCII"""
        face = []
        # Eyes - with tears
        face.append((-3, -2, 0, '●'))
        face.append((3, -2, 0, '●'))
        face.append((-3, -1, 0, '|'))  # Tears
        face.append((3, -1, 0, '|'))
        
        # Frown - inverted arc
        for x in range(-4, 5):
            y = int(4 - 0.2 * abs(x))
            face.append((x, y, 0, '_'))
            
        return face
    
    def generate_coin_points(self):
        """Generate 3D points for a clean coin surface"""
        points = []
        
        # Create coin body - circular disc
        steps = 36  # Increased for smoother edges
        for angle in range(0, 360, 360 // steps):
            rad = math.radians(angle)
            
            # Edge points
            x = self.coin_radius * math.cos(rad)
            y = self.coin_radius * math.sin(rad)
            
            # Create rim
            for z in range(-self.coin_thickness, self.coin_thickness + 1):
                points.append((x, y, z, 'rim'))
            
        # Create front and back faces
        for r in range(0, self.coin_radius, 2):
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                x = r * math.cos(rad)
                y = r * math.sin(rad)
                
                # Front face
                points.append((x, y, self.coin_thickness, 'front'))
                # Back face
                points.append((x, y, -self.coin_thickness, 'back'))
        
        # Add faces
        happy_face = self.create_simple_happy_face()
        for x, y, z, char in happy_face:
            points.append((x, y, self.coin_thickness + 1, char))
            
        sad_face = self.create_simple_sad_face()
        for x, y, z, char in sad_face:
            points.append((x, y, -self.coin_thickness - 1, char))
            
        return points
    
    def rotate_3d(self, x, y, z, rx, ry, rz):
        """Apply 3D rotation transformations"""
        # Rotate around X axis
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # Rotate around Y axis
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
        
        # Rotate around Z axis
        cos_z, sin_z = math.cos(rz), math.sin(rz)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        
        return x, y, z
    
    def project_to_screen(self, x, y, z, window):
        """Project 3D coordinates to 2D screen space"""
        if z + self.camera_distance <= 0:
            return None, None, None
            
        factor = self.camera_distance / (z + self.camera_distance)
        screen_x = int(window.width // 2 + x * factor)
        screen_y = int(window.height // 2 + y * factor * 0.5)  # Aspect correction
        depth = 1 / (z + self.camera_distance)
        
        return screen_x, screen_y, depth
    
    def render_coin_to_window(self, window, offset_x=0, offset_y=0, time_offset=0):
        """Render coin to a specific window"""
        window.clear()
        points = self.generate_coin_points()
        
        # Apply rotation with time offset for different phases
        rx = self.rotation_x + time_offset * 0.5
        ry = self.rotation_y + time_offset
        rz = self.rotation_z + time_offset * 0.3
        
        for point in points:
            x, y, z, ptype = point[0] + offset_x, point[1] + offset_y, point[2], point[3]
            
            # Rotate point
            x, y, z = self.rotate_3d(x, y, z, rx, ry, rz)
            
            # Project to screen
            sx, sy, depth = self.project_to_screen(x, y, z, window)
            
            if sx is None or not (0 <= sx < window.width and 0 <= sy < window.height):
                continue
                
            if depth > window.zbuffer[sy][sx]:
                window.zbuffer[sy][sx] = depth
                
                # Choose character based on type and mode
                if self.render_mode == RenderMode.MATRIX:
                    if ptype in ['●', '‾', '_', '|']:  # Face components
                        char = ptype
                        color = 2  # Bright white for face
                    elif ptype == 'rim':
                        char = random.choice(['█', '▓', '▒'])
                        color = 1 if z > 0 else 3  # Green gradient
                    else:
                        brightness = max(0, min(1, (z + self.coin_thickness) / (2 * self.coin_thickness)))
                        if brightness > 0.7:
                            char = random.choice(self.matrix_chars)
                            color = 2
                        elif brightness > 0.3:
                            char = random.choice(['░', '▒', '▓'])
                            color = 1
                        else:
                            char = '░'
                            color = 3
                else:  # MONOCHROME mode
                    if ptype in ['●', '‾', '_', '|']:
                        char = ptype
                        color = 0
                    else:
                        char = '█' if z > 0 else '▓'
                        color = 0
                        
                window.buffer[sy][sx] = (char, color)
    
    def update_matrix_rain(self, height, width):
        """Update Matrix-style rain effect in background"""
        # Add new drops
        if len(self.matrix_drops) < width // 4 and random.random() < 0.1:
            self.matrix_drops.append({
                'x': random.randint(0, width - 1),
                'y': 0,
                'speed': random.uniform(0.5, 2),
                'chars': [random.choice(self.matrix_chars) for _ in range(random.randint(5, 15))]
            })
        
        # Update existing drops
        for drop in self.matrix_drops[:]:
            drop['y'] += drop['speed']
            if drop['y'] > height:
                self.matrix_drops.remove(drop)
    
    def draw_window_border(self, stdscr, window, active=False):
        """Draw border around window"""
        color = curses.color_pair(5) if active else curses.color_pair(3)
        
        # Top and bottom borders
        for x in range(window.width):
            try:
                stdscr.addstr(window.y - 1, window.x + x, '═', color)
                stdscr.addstr(window.y + window.height, window.x + x, '═', color)
            except:
                pass
                
        # Side borders
        for y in range(window.height):
            try:
                stdscr.addstr(window.y + y, window.x - 1, '║', color)
                stdscr.addstr(window.y + y, window.x + window.width, '║', color)
            except:
                pass
                
        # Corners
        try:
            stdscr.addstr(window.y - 1, window.x - 1, '╔', color)
            stdscr.addstr(window.y - 1, window.x + window.width, '╗', color)
            stdscr.addstr(window.y + window.height, window.x - 1, '╚', color)
            stdscr.addstr(window.y + window.height, window.x + window.width, '╝', color)
        except:
            pass
            
        # Label
        if window.label:
            try:
                label = f" {window.label} "
                stdscr.addstr(window.y - 1, window.x + 2, label, color | curses.A_BOLD)
            except:
                pass
    
    def run(self, stdscr):
        """Main animation loop"""
        self.init_curses(stdscr)
        
        # Get terminal dimensions
        height, width = stdscr.getmaxyx()
        
        # Create four windows in quadrants
        win_w = width // 2 - 4
        win_h = height // 2 - 3
        
        windows = [
            CoinWindow(2, 2, win_w, win_h, "FRONT VIEW"),
            CoinWindow(width // 2 + 2, 2, win_w, win_h, "SIDE VIEW"),
            CoinWindow(2, height // 2 + 1, win_w, win_h, "PERSPECTIVE"),
            CoinWindow(width // 2 + 2, height // 2 + 1, win_w, win_h, "ROTATING")
        ]
        
        frame_count = 0
        active_window = 0
        
        try:
            while True:
                stdscr.clear()
                
                # Update animations
                self.rotation_x += self.rotation_speed * 0.7
                self.rotation_y += self.rotation_speed
                self.rotation_z += self.rotation_speed * 0.3
                frame_count += 1
                
                # Update Matrix rain
                self.update_matrix_rain(height, width)
                
                # Draw Matrix rain in background
                for drop in self.matrix_drops:
                    for i, char in enumerate(drop['chars']):
                        y = int(drop['y']) - i
                        if 0 <= y < height:
                            try:
                                color = curses.color_pair(1 if i > 0 else 2)
                                stdscr.addstr(y, drop['x'], char, color)
                            except:
                                pass
                
                # Render coin in each window with different perspectives
                for i, window in enumerate(windows):
                    if i == 0:  # Front view - slow rotation
                        self.render_coin_to_window(window, 0, 0, frame_count * 0.02)
                    elif i == 1:  # Side view
                        self.render_coin_to_window(window, 0, 0, math.pi/2)
                    elif i == 2:  # Perspective view
                        offset = math.sin(frame_count * 0.05) * 5
                        self.render_coin_to_window(window, offset, 0, frame_count * 0.05)
                    else:  # Normal rotating
                        self.render_coin_to_window(window, 0, 0, 0)
                    
                    # Draw window border
                    self.draw_window_border(stdscr, window, i == active_window)
                    
                    # Draw window contents
                    for y in range(window.height):
                        for x in range(window.width):
                            if window.buffer[y][x] != ' ':
                                char, color = window.buffer[y][x]
                                try:
                                    stdscr.addstr(
                                        window.y + y,
                                        window.x + x,
                                        char,
                                        curses.color_pair(color)
                                    )
                                except:
                                    pass
                
                # Draw status bar
                status = f" MATRIX COIN | Frame: {frame_count} | Mode: {self.render_mode.name} | Press Q to quit "
                try:
                    stdscr.addstr(height - 1, (width - len(status)) // 2, status, 
                                curses.color_pair(5) | curses.A_REVERSE)
                except:
                    pass
                
                # Handle input
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('m') or key == ord('M'):
                    # Cycle through render modes
                    modes = list(RenderMode)
                    current_idx = modes.index(self.render_mode)
                    self.render_mode = modes[(current_idx + 1) % len(modes)]
                elif key == ord(' '):
                    # Pause/unpause
                    self.rotation_speed = 0 if self.rotation_speed > 0 else 0.05
                elif key == curses.KEY_RIGHT:
                    active_window = (active_window + 1) % 4
                elif key == curses.KEY_LEFT:
                    active_window = (active_window - 1) % 4
                
                stdscr.refresh()
                time.sleep(0.03)
                
        except KeyboardInterrupt:
            pass
        finally:
            # Clean exit message
            stdscr.clear()
            msg = "✨ MATRIX COIN ANIMATION ENDED ✨"
            stdscr.addstr(height // 2, (width - len(msg)) // 2, msg, 
                         curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1)

def main():
    """Entry point with curses wrapper"""
    coin = Matrix3DCoin()
    curses.wrapper(coin.run)

if __name__ == '__main__':
    main()