#!/usr/bin/env python3
"""
Teknisee Shimeji TikTok Desktop Pet
Phase 1 Step 1: Core Infrastructure

Very simple implementation:
- Pygame transparent window (always on top)
- Display single sprite (shime1.png)
- Basic mouse interactions (drag, double right-click kill)
- Auto-discovery of sprite packs
"""

import pygame
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel
from PyQt5.QtCore import QTimer


class SpriteDiscovery:
    """Auto-discovery system for sprite packs"""
    
    @staticmethod
    def discover_sprite_packs():
        """Scan assets folder and return list of valid sprite packs"""
        sprite_packs = []
        assets_dir = "assets"
        
        if not os.path.exists(assets_dir):
            print(f"Warning: {assets_dir} directory not found")
            return sprite_packs
            
        for folder in os.listdir(assets_dir):
            sprite_path = os.path.join(assets_dir, folder)
            
            # Validation: must have shime1.png
            if os.path.isdir(sprite_path):
                shime1_path = os.path.join(sprite_path, "shime1.png")
                if os.path.exists(shime1_path):
                    sprite_packs.append(folder)
                    print(f"Found sprite pack: {folder}")
        
        return sprite_packs


class DesktopPet:
    """Individual desktop pet sprite"""
    
    def __init__(self, sprite_name, x=100, y=100):
        self.sprite_name = sprite_name
        self.x = x
        self.y = y
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.click_count = 0
        self.last_click_time = 0
        
        # Load sprite
        sprite_path = os.path.join("assets", sprite_name, "shime1.png")
        try:
            self.image = pygame.image.load(sprite_path).convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            print(f"Loaded sprite: {sprite_path}")
        except pygame.error as e:
            print(f"Error loading sprite {sprite_path}: {e}")
            # Create a simple colored rectangle as fallback
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.image.fill((255, 100, 100, 200))  # Semi-transparent red
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
    
    def handle_mouse_down(self, pos, button):
        """Handle mouse button down events"""
        if self.rect.collidepoint(pos):
            if button == 1:  # Left click
                self.dragging = True
                self.drag_offset_x = pos[0] - self.rect.x
                self.drag_offset_y = pos[1] - self.rect.y
                return True
            elif button == 3:  # Right click
                # Double right-click detection
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time < 500:  # 500ms double-click window
                    return "kill"  # Signal to remove this pet
                self.last_click_time = current_time
        return False
    
    def handle_mouse_up(self, button):
        """Handle mouse button up events"""
        if button == 1:  # Left click
            self.dragging = False
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion for dragging"""
        if self.dragging:
            self.rect.x = pos[0] - self.drag_offset_x
            self.rect.y = pos[1] - self.drag_offset_y
    
    def update(self):
        """Update pet logic (placeholder for future animations)"""
        pass
    
    def draw(self, screen):
        """Draw the pet on screen"""
        screen.blit(self.image, self.rect)


class PygameWindow:
    """Main pygame window for desktop pets"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Get screen dimensions
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # Create window with transparency
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), 
                                            pygame.NOFRAME | pygame.SRCALPHA)
        pygame.display.set_caption("Teknisee Shimeji")
        
        # Set window properties (always on top, click-through background)
        import os
        if os.name == 'nt':  # Windows
            try:
                import win32gui
                import win32con
                hwnd = pygame.display.get_wm_info()["window"]
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            except ImportError:
                print("win32gui not available, window may not stay on top")
        
        # Game objects
        self.pets = []
        self.clock = pygame.time.Clock()
        self.running = True
    
    def add_pet(self, sprite_name, x=None, y=None):
        """Add a new pet to the screen"""
        if x is None:
            x = self.screen_width // 2
        if y is None:
            y = self.screen_height - 200  # Near bottom of screen
        
        pet = DesktopPet(sprite_name, x, y)
        self.pets.append(pet)
        print(f"Spawned pet: {sprite_name} at ({x}, {y})")
    
    def remove_pet(self, pet):
        """Remove a pet from the screen"""
        if pet in self.pets:
            self.pets.remove(pet)
            print("Pet removed")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check pet interactions
                for pet in self.pets[:]:  # Copy list to avoid modification during iteration
                    result = pet.handle_mouse_down(event.pos, event.button)
                    if result == "kill":
                        self.remove_pet(pet)
                        break
                    elif result:
                        break  # Pet handled the click
            
            elif event.type == pygame.MOUSEBUTTONUP:
                for pet in self.pets:
                    pet.handle_mouse_up(event.button)
            
            elif event.type == pygame.MOUSEMOTION:
                for pet in self.pets:
                    pet.handle_mouse_motion(event.pos)
    
    def update(self):
        """Update game logic"""
        for pet in self.pets:
            pet.update()
    
    def draw(self):
        """Draw everything on screen"""
        # Clear screen with transparent background
        self.screen.fill((0, 0, 0, 0))
        
        # Draw pets
        for pet in self.pets:
            pet.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(30)  # 30 FPS
        
        pygame.quit()


class ControlPanel(QMainWindow):
    """Simple control panel for pet management"""
    
    def __init__(self, pygame_window):
        super().__init__()
        self.pygame_window = pygame_window
        self.sprite_packs = SpriteDiscovery.discover_sprite_packs()
        
        self.setWindowTitle("Teknisee Shimeji Control Panel")
        self.setGeometry(100, 100, 300, 200)
        
        # Create UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Sprite selection
        layout.addWidget(QLabel("Select Sprite:"))
        self.sprite_combo = QComboBox()
        if self.sprite_packs:
            self.sprite_combo.addItems(self.sprite_packs)
        else:
            self.sprite_combo.addItem("No sprites found")
        layout.addWidget(self.sprite_combo)
        
        # Spawn button
        spawn_btn = QPushButton("Spawn Pet")
        spawn_btn.clicked.connect(self.spawn_pet)
        layout.addWidget(spawn_btn)
        
        # Kill all button
        kill_all_btn = QPushButton("Kill All Pets")
        kill_all_btn.clicked.connect(self.kill_all_pets)
        layout.addWidget(kill_all_btn)
        
        # Status label
        self.status_label = QLabel(f"Found {len(self.sprite_packs)} sprite pack(s)")
        layout.addWidget(self.status_label)
        
        # Info label
        info_label = QLabel("Controls:\n• Left-click + drag to move pets\n• Double right-click to kill individual pet")
        layout.addWidget(info_label)
    
    def spawn_pet(self):
        """Spawn a new pet"""
        if self.sprite_packs:
            selected_sprite = self.sprite_combo.currentText()
            self.pygame_window.add_pet(selected_sprite)
            self.update_status()
    
    def kill_all_pets(self):
        """Remove all pets"""
        self.pygame_window.pets.clear()
        self.update_status()
        print("All pets removed")
    
    def update_status(self):
        """Update status display"""
        pet_count = len(self.pygame_window.pets)
        self.status_label.setText(f"Active pets: {pet_count}")


def main():
    """Main application entry point"""
    print("Starting Teknisee Shimeji TikTok Desktop Pet")
    print("Phase 1 Step 1: Core Infrastructure")
    
    # Discover available sprite packs
    sprite_packs = SpriteDiscovery.discover_sprite_packs()
    print(f"Discovered {len(sprite_packs)} sprite pack(s): {sprite_packs}")
    
    if not sprite_packs:
        print("Warning: No valid sprite packs found in assets/ directory")
        print("Expected structure: assets/SpriteName/shime1.png")
    
    # Create QApplication (needed for control panel)
    app = QApplication(sys.argv)
    
    # Create pygame window
    pygame_window = PygameWindow()
    
    # Create and show control panel
    control_panel = ControlPanel(pygame_window)
    control_panel.show()
    
    # Auto-spawn first pet if available
    if sprite_packs:
        pygame_window.add_pet(sprite_packs[0])
    
    # Start pygame in a timer (non-blocking)
    timer = QTimer()
    timer.timeout.connect(lambda: pygame_window.handle_events() or pygame_window.update() or pygame_window.draw())
    timer.start(33)  # ~30 FPS
    
    print("Application started successfully!")
    print("Use the control panel to spawn pets")
    
    # Run Qt event loop
    try:
        app.exec_()
    finally:
        pygame_window.running = False
        pygame.quit()


if __name__ == "__main__":
    main()