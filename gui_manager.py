#!/usr/bin/env python3
"""
gui_manager.py - Pygame window and rendering management

Handles the main pygame window, rendering loop, event handling,
and pet management with proper performance optimization.
"""

import pygame
import os
import time
from typing import List, Tuple, Optional, Dict, Any, TYPE_CHECKING

from config import AppConstants, get_config
from sprite_loader import get_sprite_loader

if TYPE_CHECKING:
    from pet_behavior import DesktopPet
    from control_panel import ControlPanel # Import ControlPanel for type hinting


class PygameWindow:
    """Main pygame window manager for desktop pets"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Get screen dimensions
        self.display_info = pygame.display.Info()
        self.screen_width = self.display_info.current_w
        self.screen_height = self.display_info.current_h
        
        # Create transparent window
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.NOFRAME | pygame.SRCALPHA
        )
        pygame.display.set_caption(AppConstants.APP_NAME)
        
        # Initialize window properties
        self._setup_window_properties()
        
        # Game state
        self.pets: List['DesktopPet'] = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.last_frame_time = time.time()
        
        # Performance tracking
        self.frame_count = 0
        self.fps_counter = 0.0
        self.last_fps_update = time.time()

        # Mouse tracking for velocity (new)
        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        self.current_mouse_pos: Optional[Tuple[int, int]] = None
        self.mouse_dx: float = 0.0
        self.mouse_dy: float = 0.0
        
        # Configuration
        self.config = get_config()
        self.sprite_loader = get_sprite_loader()
        
        # Reference to control panel for signal connection (will be set after control panel is created)
        self.control_panel: Optional['ControlPanel'] = None 

        print(f"Pygame window initialized: {self.screen_width}x{self.screen_height}")
    
    def set_control_panel(self, panel: 'ControlPanel') -> None:
        """Set the control panel instance and connect signals."""
        self.control_panel = panel
        # Connect the settings_changed signal to a handler in PygameWindow
        self.control_panel.settings_changed.connect(self._on_settings_changed)
        print("Control panel connected to PygameWindow for settings updates.")

    def _on_settings_changed(self, setting_name: str, value: Any) -> None:
        """Handle settings changes from the control panel."""
        # Update the config manager first
        self.config.set(f'settings.{setting_name}', value) 
        print(f"Setting changed: {setting_name} = {value}. Propagating to pets...")

        # Propagate changes to all active pets if it's a physics setting
        if setting_name.startswith('physics_'):
            for pet in self.pets:
                pet.update_physics_parameters() # Call new method on DesktopPet
    
    def _setup_window_properties(self) -> None:
        """Setup window properties for always-on-top behavior"""
        if os.name == 'nt':  # Windows
            try:
                import win32gui
                import win32con
                
                hwnd = pygame.display.get_wm_info()["window"]
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
                print("Window set to always-on-top")
                
            except ImportError:
                print("win32gui not available, window may not stay on top")
            except Exception as e:
                print(f"Error setting window properties: {e}")
    
    def add_pet(self, sprite_name: str, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Add a new pet to the screen"""
        # Import here to avoid circular import
        from pet_behavior import DesktopPet
        
        # Use config defaults if position not specified
        if x is None:
            x = self.config.get('settings.spawn_x') or (self.screen_width // 2)
        if y is None:
            y = self.config.get('settings.spawn_y') or (self.screen_height - AppConstants.SCREEN_MARGIN)
        
        # Create new pet
        pet = DesktopPet(sprite_name, x, y)
        self.pets.append(pet)
        
        print(f"Added pet: {pet.pet_id} at ({x}, {y})")
        return pet.pet_id
    
    def remove_pet(self, pet: 'DesktopPet') -> bool:
        """Remove a pet from the screen"""
        if pet in self.pets:
            pet.cleanup()
            self.pets.remove(pet)
            print(f"Removed pet: {pet.pet_id}")
            return True
        return False
    
    def remove_pet_by_id(self, pet_id: str) -> bool:
        """Remove a pet by its ID"""
        for pet in self.pets[:]:  # Copy list to avoid modification during iteration
            if pet.pet_id == pet_id:
                return self.remove_pet(pet)
        return False
    
    def clear_all_pets(self) -> int:
        """Remove all pets from the screen"""
        count = len(self.pets)
        for pet in self.pets[:]:
            pet.cleanup()
        self.pets.clear()
        print(f"Removed all {count} pets")
        return count
    
    def get_pet_by_id(self, pet_id: str) -> Optional['DesktopPet']:
        """Get pet by its ID"""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None
    
    def handle_events(self) -> None:
        """Handle pygame events and pet interactions"""
        # Update current mouse position for velocity calculation
        self.current_mouse_pos = pygame.mouse.get_pos()
        if self.last_mouse_pos:
            self.mouse_dx = self.current_mouse_pos[0] - self.last_mouse_pos[0]
            self.mouse_dy = self.current_mouse_pos[1] - self.last_mouse_pos[1]
        self.last_mouse_pos = self.current_mouse_pos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.pos, event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                # Pass current mouse velocity (dx, dy) to handle_mouse_up
                self._handle_mouse_up(event.button, self.mouse_dx, self.mouse_dy)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)
    
    def _handle_mouse_down(self, pos: Tuple[int, int], button: int) -> None:
        """Handle mouse button down events"""
        # Check pet interactions (reverse order for top-most pet)
        for pet in reversed(self.pets):
            result = pet.handle_mouse_down(pos, button)
            
            if result == "kill":
                self.remove_pet(pet)
                break
            elif result in ["drag_start", "sit"]:
                # Pet handled the click, stop processing
                break
    
    def _handle_mouse_up(self, button: int, mouse_dx: float, mouse_dy: float) -> None:
        """Handle mouse button up events"""
        for pet in self.pets:
            pet.handle_mouse_up(button, mouse_dx, mouse_dy) # Pass mouse dx, dy
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion for dragging"""
        for pet in self.pets:
            pet.handle_mouse_motion(pos)
    
    def _handle_key_down(self, key: int) -> None:
        """Handle keyboard events"""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_F1:
            # Toggle debug mode
            debug_mode = self.config.get('settings.debug_mode', False)
            self.config.set('settings.debug_mode', not debug_mode)
        elif key == pygame.K_F2:
            # Print performance info
            self._print_performance_info()
    
    def update(self) -> None:
        """Update game logic"""
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update all pets
        screen_bounds = (self.screen_width, self.screen_height)
        for pet in self.pets[:]:  # Copy list in case pets are removed during update
            pet.update(dt, screen_bounds)
        
        # Update performance counters
        self._update_performance_counters(dt)
    
    def _update_performance_counters(self, dt: float) -> None:
        """Update performance tracking"""
        self.frame_count += 1
        current_time = time.time()
        
        # Update FPS every second
        if current_time - self.last_fps_update >= 1.0:
            self.fps_counter = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def draw(self) -> None:
        """Render everything to screen"""
        # Clear screen with transparent background
        self.screen.fill((0, 0, 0, 0))
        
        # Draw all pets
        for pet in self.pets:
            pet.draw(self.screen)
        
        # Draw debug overlay if enabled
        if self.config.get('settings.debug_mode', False):
            self._draw_debug_overlay()
        
        # Update display
        pygame.display.flip()
    
    def _draw_debug_overlay(self) -> None:
        """Draw debug information overlay"""
        font = pygame.font.Font(None, 24)
        debug_color = (255, 255, 255)
        
        # FPS counter
        fps_text = font.render(f"FPS: {self.fps_counter:.1f}", True, debug_color)
        self.screen.blit(fps_text, (10, 10))
        
        # Pet count
        pet_count_text = font.render(f"Pets: {len(self.pets)}", True, debug_color)
        self.screen.blit(pet_count_text, (10, 35))
        
        # Screen resolution
        res_text = font.render(f"Resolution: {self.screen_width}x{self.screen_height}", True, debug_color)
        self.screen.blit(res_text, (10, 60))
        
        # Memory usage (sprite cache)
        cache_info = self.sprite_loader.get_cache_info()
        memory_text = font.render(f"Cache: {cache_info['cached_sprites']} sprites, {cache_info['estimated_memory_mb']:.1f}MB", True, debug_color)
        self.screen.blit(memory_text, (10, 85))
    
    def run(self) -> None:
        """Main game loop (blocking)"""
        print("Starting main game loop")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(AppConstants.TARGET_FPS)
        
        self.cleanup()
    
    def step(self) -> bool:
        """Single frame update (non-blocking)"""
        if not self.running:
            return False
        
        self.handle_events()
        self.update()
        self.draw()
        self.clock.tick(AppConstants.TARGET_FPS)
        
        return self.running
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information"""
        cache_info = self.sprite_loader.get_cache_info()
        
        return {
            'fps': self.fps_counter,
            'pet_count': len(self.pets),
            'screen_size': (self.screen_width, self.screen_height),
            'sprite_cache': cache_info,
            'memory_usage_mb': cache_info['estimated_memory_mb']
        }
    
    def _print_performance_info(self) -> None:
        """Print performance information to console"""
        perf_info = self.get_performance_info()
        print("=== Performance Info ===")
        print(f"FPS: {perf_info['fps']:.1f}")
        print(f"Pets: {perf_info['pet_count']}")
        print(f"Screen: {perf_info['screen_size'][0]}x{perf_info['screen_size'][1]}")
        print(f"Sprite Cache: {perf_info['sprite_cache']['cached_sprites']} sprites")
        print(f"Memory: {perf_info['memory_usage_mb']:.1f}MB")
        print("========================")
    
    def save_pets_state(self) -> List[Dict[str, Any]]:
        """Save state of all pets"""
        return [pet.save_state() for pet in self.pets]
    
    def load_pets_state(self, pets_data: List[Dict[str, Any]]) -> int:
        """Load pets from saved state"""
        # Import here to avoid circular import
        from pet_behavior import DesktopPet
        
        self.clear_all_pets()
        loaded_count = 0
        
        for pet_data in pets_data:
            try:
                pet = DesktopPet.load_from_state(pet_data)
                self.pets.append(pet)
                loaded_count += 1
            except Exception as e:
                print(f"Error loading pet state: {e}")
        
        print(f"Loaded {loaded_count} pets from saved state")
        return loaded_count
    
    def get_pets_info(self) -> List[Dict[str, Any]]:
        """Get information about all pets"""
        return [pet.get_state_info() for pet in self.pets]
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        print("Cleaning up pygame window")
        
        # Save pets state to config
        pets_state = self.save_pets_state()
        self.config.set('active_pets', pets_state)
        
        # Cleanup all pets
        self.clear_all_pets()
        
        # Clear sprite cache
        self.sprite_loader.clear_cache()
        
        # Quit pygame
        pygame.quit()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        if hasattr(self, 'running') and self.running:
            self.cleanup()
