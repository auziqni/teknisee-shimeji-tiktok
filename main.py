#!/usr/bin/env python3
"""
Teknisee Shimeji TikTok Desktop Pet
Phase 1 Step 2: Control Panel Foundation

Enhanced implementation:
- Pygame transparent window (always on top)
- Display single sprite (shime1.png)
- Basic mouse interactions (drag, double right-click kill)
- Auto-discovery of sprite packs
- Tabbed control panel with settings
- JSON config save/load system
"""

import pygame
import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QComboBox, QLabel, QTabWidget, QHBoxLayout,
                           QSlider, QCheckBox, QSpinBox, QGroupBox)
from PyQt5.QtCore import QTimer, Qt


class ConfigManager:
    """JSON configuration management system"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "settings": {
                "volume": 70,
                "behavior_frequency": 50,
                "screen_boundaries": True,
                "auto_save": True,
                "spawn_x": None,  # None = auto-center
                "spawn_y": None   # None = auto-bottom
            },
            "tiktok": {
                "enabled": False,
                "last_successful_username": "",
                "auto_connect": False
            },
            "sprite_packs": [],
            "logging": {
                "level": "INFO",
                "save_to_file": True,
                "max_log_size": "10MB"
            },
            "ui": {
                "control_panel_x": 100,
                "control_panel_y": 100,
                "selected_sprite": ""
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = self.default_config.copy()
                self._deep_update(config, loaded_config)
                print(f"Configuration loaded from {self.config_file}")
                return config
            else:
                print("No config file found, using defaults")
                return self.default_config.copy()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}, using defaults")
            return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def _deep_update(self, base_dict, update_dict):
        """Recursively update nested dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key_path, default=None):
        """Get config value using dot notation (e.g., 'settings.volume')"""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """Set config value using dot notation"""
        keys = key_path.split('.')
        config_section = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config_section:
                config_section[key] = {}
            config_section = config_section[key]
        
        # Set the final value
        config_section[keys[-1]] = value
        
        # Auto-save if enabled
        if self.get('settings.auto_save', True):
            self.save_config()


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
    """Enhanced control panel with tabbed interface and settings"""
    
    def __init__(self, pygame_window, config_manager):
        super().__init__()
        self.pygame_window = pygame_window
        self.config = config_manager
        self.sprite_packs = SpriteDiscovery.discover_sprite_packs()
        
        # Update config with discovered sprite packs
        self.config.set('sprite_packs', self.sprite_packs)
        
        self.setWindowTitle("Teknisee Shimeji Control Panel")
        self.setGeometry(
            self.config.get('ui.control_panel_x', 100),
            self.config.get('ui.control_panel_y', 100),
            400, 500
        )
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Create the tabbed interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(tab_widget)
        
        # Create tabs
        self.create_pet_management_tab(tab_widget)
        self.create_settings_tab(tab_widget)
        self.create_about_tab(tab_widget)
    
    def create_pet_management_tab(self, tab_widget):
        """Create pet management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sprite selection group
        sprite_group = QGroupBox("Sprite Selection")
        sprite_layout = QVBoxLayout(sprite_group)
        
        sprite_layout.addWidget(QLabel("Select Sprite Pack:"))
        self.sprite_combo = QComboBox()
        if self.sprite_packs:
            self.sprite_combo.addItems(self.sprite_packs)
            # Set saved selection
            saved_sprite = self.config.get('ui.selected_sprite')
            if saved_sprite and saved_sprite in self.sprite_packs:
                self.sprite_combo.setCurrentText(saved_sprite)
        else:
            self.sprite_combo.addItem("No sprites found")
        self.sprite_combo.currentTextChanged.connect(self.on_sprite_changed)
        sprite_layout.addWidget(self.sprite_combo)
        
        layout.addWidget(sprite_group)
        
        # Pet actions group
        actions_group = QGroupBox("Pet Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Spawn controls
        spawn_layout = QHBoxLayout()
        spawn_btn = QPushButton("Spawn Pet")
        spawn_btn.clicked.connect(self.spawn_pet)
        spawn_layout.addWidget(spawn_btn)
        
        self.spawn_count_spin = QSpinBox()
        self.spawn_count_spin.setRange(1, 10)
        self.spawn_count_spin.setValue(1)
        spawn_layout.addWidget(QLabel("Count:"))
        spawn_layout.addWidget(self.spawn_count_spin)
        actions_layout.addLayout(spawn_layout)
        
        # Kill all button
        kill_all_btn = QPushButton("Kill All Pets")
        kill_all_btn.clicked.connect(self.kill_all_pets)
        actions_layout.addWidget(kill_all_btn)
        
        layout.addWidget(actions_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel(f"Found {len(self.sprite_packs)} sprite pack(s)")
        status_layout.addWidget(self.status_label)
        
        self.pet_count_label = QLabel("Active pets: 0")
        status_layout.addWidget(self.pet_count_label)
        
        layout.addWidget(status_group)
        
        # Controls info
        info_group = QGroupBox("Controls")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel(
            "• Left-click + drag to move pets\n"
            "• Double right-click to kill individual pet\n"
            "• Settings are auto-saved"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        tab_widget.addTab(tab, "Pet Management")
    
    def create_settings_tab(self, tab_widget):
        """Create settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.config.get('settings.volume', 70))
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        self.volume_label = QLabel(f"{self.volume_slider.value()}%")
        volume_layout.addWidget(self.volume_label)
        general_layout.addLayout(volume_layout)
        
        # Behavior frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Behavior Frequency:"))
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(10, 100)
        self.freq_slider.setValue(self.config.get('settings.behavior_frequency', 50))
        self.freq_slider.valueChanged.connect(self.on_frequency_changed)
        freq_layout.addWidget(self.freq_slider)
        self.freq_label = QLabel(f"{self.freq_slider.value()}%")
        freq_layout.addWidget(self.freq_label)
        general_layout.addLayout(freq_layout)
        
        # Checkboxes
        self.boundaries_check = QCheckBox("Keep pets within screen boundaries")
        self.boundaries_check.setChecked(self.config.get('settings.screen_boundaries', True))
        self.boundaries_check.toggled.connect(self.on_boundaries_changed)
        general_layout.addWidget(self.boundaries_check)
        
        self.autosave_check = QCheckBox("Auto-save settings")
        self.autosave_check.setChecked(self.config.get('settings.auto_save', True))
        self.autosave_check.toggled.connect(self.on_autosave_changed)
        general_layout.addWidget(self.autosave_check)
        
        layout.addWidget(general_group)
        
        # Configuration management
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        config_buttons_layout = QHBoxLayout()
        
        save_config_btn = QPushButton("Save Config")
        save_config_btn.clicked.connect(self.save_config_manual)
        config_buttons_layout.addWidget(save_config_btn)
        
        reload_config_btn = QPushButton("Reload Config")
        reload_config_btn.clicked.connect(self.reload_config)
        config_buttons_layout.addWidget(reload_config_btn)
        
        config_layout.addLayout(config_buttons_layout)
        
        # Config file info
        config_info = QLabel(f"Config file: {self.config.config_file}")
        config_info.setWordWrap(True)
        config_layout.addWidget(config_info)
        
        layout.addWidget(config_group)
        
        # Spacer
        layout.addStretch()
        
        tab_widget.addTab(tab, "Settings")
    
    def create_about_tab(self, tab_widget):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Project info
        info_group = QGroupBox("About")
        info_layout = QVBoxLayout(info_group)
        
        title_label = QLabel("Teknisee Shimeji TikTok")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_layout.addWidget(title_label)
        
        version_label = QLabel("Phase 1 Step 2: Control Panel Foundation")
        info_layout.addWidget(version_label)
        
        description_label = QLabel(
            "A desktop pet application inspired by Shimeji with TikTok Live integration capabilities.\n\n"
            "Features interactive desktop pets that can respond to TikTok Live chat in real-time."
        )
        description_label.setWordWrap(True)
        info_layout.addWidget(description_label)
        
        layout.addWidget(info_group)
        
        # Development status
        dev_group = QGroupBox("Development Status")
        dev_layout = QVBoxLayout(dev_group)
        
        status_text = QLabel(
            "✅ Phase 1 Step 1: Core Infrastructure (Complete)\n"
            "🔄 Phase 1 Step 2: Control Panel Foundation (Current)\n"
            "⏳ Phase 1 Step 3: XML Parser & Animation System\n"
            "⏳ Phase 1 Step 4: Desktop Boundaries & Physics"
        )
        status_text.setWordWrap(True)
        dev_layout.addWidget(status_text)
        
        layout.addWidget(dev_group)
        
        # Spacer
        layout.addStretch()
        
        tab_widget.addTab(tab, "About")
    
    def load_settings(self):
        """Load settings into UI components"""
        # Settings are already loaded in setup_ui, but this can be used for refresh
        pass
    
    def on_sprite_changed(self, sprite_name):
        """Handle sprite selection change"""
        self.config.set('ui.selected_sprite', sprite_name)
    
    def on_volume_changed(self, value):
        """Handle volume slider change"""
        self.config.set('settings.volume', value)
        self.volume_label.setText(f"{value}%")
    
    def on_frequency_changed(self, value):
        """Handle frequency slider change"""
        self.config.set('settings.behavior_frequency', value)
        self.freq_label.setText(f"{value}%")
    
    def on_boundaries_changed(self, checked):
        """Handle boundaries checkbox change"""
        self.config.set('settings.screen_boundaries', checked)
    
    def on_autosave_changed(self, checked):
        """Handle auto-save checkbox change"""
        self.config.set('settings.auto_save', checked)
    
    def spawn_pet(self):
        """Spawn new pet(s)"""
        if self.sprite_packs:
            selected_sprite = self.sprite_combo.currentText()
            count = self.spawn_count_spin.value()
            
            for i in range(count):
                # Add some randomization to spawn position for multiple pets
                offset_x = i * 50 if count > 1 else 0
                spawn_x = self.config.get('settings.spawn_x')
                spawn_y = self.config.get('settings.spawn_y')
                
                if spawn_x is None:
                    spawn_x = self.pygame_window.screen_width // 2 + offset_x
                if spawn_y is None:
                    spawn_y = self.pygame_window.screen_height - 200
                
                self.pygame_window.add_pet(selected_sprite, spawn_x, spawn_y)
            
            self.update_status()
    
    def kill_all_pets(self):
        """Remove all pets"""
        self.pygame_window.pets.clear()
        self.update_status()
        print("All pets removed")
    
    def update_status(self):
        """Update status displays"""
        pet_count = len(self.pygame_window.pets)
        self.pet_count_label.setText(f"Active pets: {pet_count}")
    
    def save_config_manual(self):
        """Manually save configuration"""
        if self.config.save_config():
            print("Configuration saved successfully")
        else:
            print("Failed to save configuration")
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config.config = self.config.load_config()
        
        # Update UI with reloaded settings
        self.volume_slider.setValue(self.config.get('settings.volume', 70))
        self.freq_slider.setValue(self.config.get('settings.behavior_frequency', 50))
        self.boundaries_check.setChecked(self.config.get('settings.screen_boundaries', True))
        self.autosave_check.setChecked(self.config.get('settings.auto_save', True))
        
        saved_sprite = self.config.get('ui.selected_sprite')
        if saved_sprite and saved_sprite in self.sprite_packs:
            self.sprite_combo.setCurrentText(saved_sprite)
        
        print("Configuration reloaded")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window position
        pos = self.pos()
        self.config.set('ui.control_panel_x', pos.x())
        self.config.set('ui.control_panel_y', pos.y())
        
        # Save final config
        self.config.save_config()
        
        event.accept()


def main():
    """Main application entry point"""
    print("Starting Teknisee Shimeji TikTok Desktop Pet")
    print("Phase 1 Step 2: Control Panel Foundation")
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Discover available sprite packs
    sprite_packs = SpriteDiscovery.discover_sprite_packs()
    print(f"Discovered {len(sprite_packs)} sprite pack(s): {sprite_packs}")
    
    if not sprite_packs:
        print("Warning: No valid sprite packs found in assets/ directory")
        print("Expected structure: assets/SpriteName/shime1.png")
    
    # Update config with discovered packs
    config_manager.set('sprite_packs', sprite_packs)
    
    # Create QApplication (needed for control panel)
    app = QApplication(sys.argv)
    
    # Create pygame window
    pygame_window = PygameWindow()
    
    # Create and show enhanced control panel
    control_panel = ControlPanel(pygame_window, config_manager)
    control_panel.show()
    
    # Auto-spawn first pet if available and enabled
    if sprite_packs:
        selected_sprite = config_manager.get('ui.selected_sprite')
        if not selected_sprite or selected_sprite not in sprite_packs:
            selected_sprite = sprite_packs[0]
        
        spawn_x = config_manager.get('settings.spawn_x')
        spawn_y = config_manager.get('settings.spawn_y')
        pygame_window.add_pet(selected_sprite, spawn_x, spawn_y)
        control_panel.update_status()
    
    # Start pygame in a timer (non-blocking)
    timer = QTimer()
    timer.timeout.connect(lambda: pygame_window.handle_events() or pygame_window.update() or pygame_window.draw())
    timer.start(33)  # ~30 FPS
    
    print("Enhanced application started successfully!")
    print("Features: Tabbed control panel, JSON config, settings persistence")
    
    # Run Qt event loop
    try:
        app.exec_()
    finally:
        pygame_window.running = False
        pygame.quit()


if __name__ == "__main__":
    main()