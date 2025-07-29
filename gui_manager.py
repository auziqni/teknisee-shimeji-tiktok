#!/usr/bin/env python3
"""
gui_manager.py - Hybrid Tkinter+Pygame Transparent Desktop Pet

Menggunakan Tkinter untuk transparency dan Pygame untuk sprite rendering.
Solusi ini lebih reliable di sistem yang tidak support pygame alpha.
"""

import pygame
import tkinter as tk
import os
import time
import threading
from typing import List, Tuple, Optional, Dict, Any, TYPE_CHECKING

from config import AppConstants, get_config
from sprite_loader import get_sprite_loader

if TYPE_CHECKING:
    from pet_behavior import DesktopPet
    from control_panel import ControlPanel


class BoundaryManager:
    """Manages screen boundaries and collision detection"""
    
    def __init__(self, screen_width: int, screen_height: int, config_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_manager
        self.boundaries = self._calculate_boundaries()
    
    def _calculate_boundaries(self) -> Dict[str, int]:
        """Calculate boundary positions from config percentages"""
        return self.config.get_boundary_pixels(self.screen_width, self.screen_height)
    
    def update_boundaries(self) -> None:
        """Recalculate boundaries when config changes"""
        self.boundaries = self._calculate_boundaries()
    
    def get_playable_area(self) -> Dict[str, int]:
        """Get the playable area dimensions"""
        return {
            'left': self.boundaries['left_wall_x'],
            'right': self.boundaries['right_wall_x'],
            'top': self.boundaries['ceiling_y'],
            'bottom': self.boundaries['ground_y'],
            'width': self.boundaries['right_wall_x'] - self.boundaries['left_wall_x'],
            'height': self.boundaries['ground_y'] - self.boundaries['ceiling_y']
        }
    
    def check_boundary_collision(self, x: float, y: float, width: int, height: int) -> Dict[str, bool]:
        """Check if a rectangle collides with any boundaries"""
        return {
            'left_wall': x <= self.boundaries['left_wall_x'],
            'right_wall': x + width >= self.boundaries['right_wall_x'],
            'ground': y + height >= self.boundaries['ground_y'],
            'ceiling': y <= self.boundaries['ceiling_y']
        }
    
    def clamp_to_boundaries(self, x: float, y: float, width: int, height: int) -> Tuple[float, float]:
        """Clamp position to stay within boundaries"""
        # Clamp X position
        if x < self.boundaries['left_wall_x']:
            x = self.boundaries['left_wall_x']
        elif x + width > self.boundaries['right_wall_x']:
            x = self.boundaries['right_wall_x'] - width
        
        # Clamp Y position
        if y < self.boundaries['ceiling_y']:
            y = self.boundaries['ceiling_y']
        elif y + height > self.boundaries['ground_y']:
            y = self.boundaries['ground_y'] - height
        
        return x, y
    
    def draw_boundaries(self, screen: pygame.Surface) -> None:
        """Draw boundary lines for debug visualization"""
        # Draw ground (blue line)
        pygame.draw.line(
            screen,
            AppConstants.DEBUG_COLORS['ground'],
            (0, self.boundaries['ground_y']),
            (self.screen_width, self.boundaries['ground_y']),
            3
        )
        
        # Draw left wall (purple line)
        pygame.draw.line(
            screen,
            AppConstants.DEBUG_COLORS['left_wall'],
            (self.boundaries['left_wall_x'], 0),
            (self.boundaries['left_wall_x'], self.screen_height),
            3
        )
        
        # Draw right wall (purple line)
        pygame.draw.line(
            screen,
            AppConstants.DEBUG_COLORS['right_wall'],
            (self.boundaries['right_wall_x'], 0),
            (self.boundaries['right_wall_x'], self.screen_height),
            3
        )
        
        # Draw ceiling (yellow line)
        pygame.draw.line(
            screen,
            AppConstants.DEBUG_COLORS['ceiling'],
            (0, self.boundaries['ceiling_y']),
            (self.screen_width, self.boundaries['ceiling_y']),
            3
        )
    
    def _draw_corner_indicators(self, screen: pygame.Surface) -> None:
        """Draw corner indicators for debugging"""
        corner_size = 10
        corner_color = (255, 255, 0)  # Yellow
        
        # Top-left corner
        pygame.draw.rect(screen, corner_color, 
                        (self.boundaries['left_wall_x'] - corner_size//2, 
                         self.boundaries['ceiling_y'] - corner_size//2, 
                         corner_size, corner_size))
        
        # Top-right corner
        pygame.draw.rect(screen, corner_color, 
                        (self.boundaries['right_wall_x'] - corner_size//2, 
                         self.boundaries['ceiling_y'] - corner_size//2, 
                         corner_size, corner_size))
        
        # Bottom-left corner
        pygame.draw.rect(screen, corner_color, 
                        (self.boundaries['left_wall_x'] - corner_size//2, 
                         self.boundaries['ground_y'] - corner_size//2, 
                         corner_size, corner_size))
        
        # Bottom-right corner
        pygame.draw.rect(screen, corner_color, 
                        (self.boundaries['right_wall_x'] - corner_size//2, 
                         self.boundaries['ground_y'] - corner_size//2, 
                         corner_size, corner_size))


class PygameWindow:
    """Hybrid transparent window menggunakan Tkinter + Pygame dengan boundary system"""
    
    def __init__(self):
        # Initialize Pygame (embedded mode)
        pygame.init()
        
        # Get screen info
        self.display_info = pygame.display.Info()
        self.screen_width = self.display_info.current_w
        self.screen_height = self.display_info.current_h
        
        # Create Tkinter transparent window
        self.tk_root = self._create_transparent_tkinter_window()
        
        # Embed pygame dalam tkinter
        self._setup_pygame_in_tkinter()
        
        # Configuration and boundary system
        self.config = get_config()
        self.boundary_manager = BoundaryManager(self.screen_width, self.screen_height, self.config)
        
        # Game state
        self.pets: List['DesktopPet'] = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.last_frame_time = time.time()
        
        # Performance tracking
        self.frame_count = 0
        self.fps_counter = 0.0
        self.last_fps_update = time.time()

        # Mouse tracking
        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        self.current_mouse_pos: Optional[Tuple[int, int]] = None
        self.mouse_dx: float = 0.0
        self.mouse_dy: float = 0.0
        
        # Sprite loader
        self.sprite_loader = get_sprite_loader()
        
        # Reference to control panel
        self.control_panel: Optional['ControlPanel'] = None
        
        # Game loop control
        self.game_thread = None
        self.game_running = False
        
        print(f"🎮 Hybrid transparent window created: {self.screen_width}x{self.screen_height}")
        print("✅ Using Tkinter transparency + Pygame rendering")
        print(f"🎯 Boundary system initialized")
    
    def _create_transparent_tkinter_window(self) -> tk.Tk:
        """Create fully transparent Tkinter window"""
        root = tk.Tk()
        
        # Remove window decorations
        root.overrideredirect(True)
        
        # Set window size and position
        root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        # Make window transparent
        root.wm_attributes('-transparentcolor', 'black')  # Black = transparent
        root.wm_attributes('-topmost', True)  # Always on top
        
        # Set transparent background
        root.configure(bg='black')
        
        # Make window click-through for background (except widgets)
        try:
            # Windows-specific: allow click-through
            root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        print("✅ Tkinter transparent window created")
        return root
    
    def _setup_pygame_in_tkinter(self):
        """Setup pygame surface dalam tkinter window"""
        try:
            # Set pygame to use tkinter window
            os.environ['SDL_WINDOWID'] = str(self.tk_root.winfo_id())
            
            # Wait for tkinter window to be ready
            self.tk_root.update()
            
            # Create pygame display dalam tkinter
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.NOFRAME
            )
            
            pygame.display.set_caption("Desktop Pet")
            
            # Set black sebagai background (akan jadi transparent)
            self.screen.fill((0, 0, 0))  # Black = transparent di tkinter
            pygame.display.flip()
            
            print("✅ Pygame embedded dalam Tkinter")
            
        except Exception as e:
            print(f"❌ Error embedding pygame: {e}")
            # Fallback: create separate pygame window
            self.screen = pygame.display.set_mode((800, 600))
            self.screen.fill((50, 50, 50))
    
    def set_control_panel(self, panel: 'ControlPanel') -> None:
        """Connect control panel"""
        self.control_panel = panel
        self.control_panel.settings_changed.connect(self._on_settings_changed)

    def _on_settings_changed(self, setting_name: str, value: Any) -> None:
        """Handle settings changes"""
        # Update the config manager first
        self.config.set(f'settings.{setting_name}' if not setting_name.endswith('_percent') and not setting_name.endswith('_enabled') else f'boundaries.{setting_name}', value) 
        print(f"Setting changed: {setting_name} = {value}")

        # Handle boundary-specific changes
        if setting_name in ['left_wall_percent', 'right_wall_percent', 'ground_percent', 'wall_climbing_enabled', 'corner_bounce_enabled']:
            self.boundary_manager.update_boundaries()
            print(f"Boundaries updated: {self.boundary_manager.boundaries}")

        # Propagate physics changes to all active pets
        if setting_name.startswith('physics_'):
            for pet in self.pets:
                pet.update_physics_parameters()
    
    def add_pet(self, sprite_name: str, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Add new pet"""
        from pet_behavior import DesktopPet
        
        if x is None:
            x = self.config.get('settings.spawn_x') or (self.screen_width // 2)
        if y is None:
            y = self.config.get('settings.spawn_y') or (self.screen_height - AppConstants.SPAWN_OFFSET)
        
        pet = DesktopPet(sprite_name, x, y)
        pet.set_boundary_manager(self.boundary_manager)
        self.pets.append(pet)
        
        print(f"🐾 Added pet: {pet.pet_id} at ({x}, {y})")
        return pet.pet_id
    
    def remove_pet(self, pet: 'DesktopPet') -> bool:
        """Remove pet"""
        if pet in self.pets:
            pet.cleanup()
            self.pets.remove(pet)
            print(f"Removed pet: {pet.pet_id}")
            return True
        return False
    
    def remove_pet_by_id(self, pet_id: str) -> bool:
        """Remove pet by ID"""
        for pet in self.pets[:]:
            if pet.pet_id == pet_id:
                return self.remove_pet(pet)
        return False
    
    def clear_all_pets(self) -> int:
        """Remove all pets"""
        count = len(self.pets)
        for pet in self.pets[:]:
            pet.cleanup()
        self.pets.clear()
        print(f"Removed all {count} pets")
        return count
    
    def get_pet_by_id(self, pet_id: str) -> Optional['DesktopPet']:
        """Get pet by ID"""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None
    
    def handle_events(self) -> None:
        """Handle pygame events"""
        # Track mouse for velocity
        try:
            self.current_mouse_pos = pygame.mouse.get_pos()
            if self.last_mouse_pos:
                self.mouse_dx = self.current_mouse_pos[0] - self.last_mouse_pos[0]
                self.mouse_dy = self.current_mouse_pos[1] - self.last_mouse_pos[1]
            self.last_mouse_pos = self.current_mouse_pos
        except:
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.pos, event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event.button, self.mouse_dx, self.mouse_dy)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)
    
    def _handle_mouse_down(self, pos: Tuple[int, int], button: int) -> None:
        """Handle mouse down"""
        for pet in reversed(self.pets):
            result = pet.handle_mouse_down(pos, button)
            
            if result == "kill":
                self.remove_pet(pet)
                break
            elif result in ["drag_start", "sit"]:
                break
    
    def _handle_mouse_up(self, button: int, mouse_dx: float, mouse_dy: float) -> None:
        """Handle mouse up"""
        for pet in self.pets:
            pet.handle_mouse_up(button, mouse_dx, mouse_dy)
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion"""
        for pet in self.pets:
            pet.handle_mouse_motion(pos)
    
    def _handle_key_down(self, key: int) -> None:
        """Handle key press"""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_F1:
            debug_mode = self.config.get('settings.debug_mode', False)
            self.config.set('settings.debug_mode', not debug_mode)
            print(f"Debug mode: {not debug_mode}")
        elif key == pygame.K_F2:
            self._print_performance_info()
    
    def update(self) -> None:
        """Update game logic"""
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update all pets
        for pet in self.pets[:]:
            pet.update(dt, (self.screen_width, self.screen_height))
        
        # Remove dead pets
        self.pets = [pet for pet in self.pets if pet.running]
        
        # Update performance
        self._update_performance_counters(dt)
    
    def _update_performance_counters(self, dt: float) -> None:
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.fps_counter = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def draw(self) -> None:
        """Draw everything"""
        # Clear dengan black (transparent di tkinter)
        self.screen.fill((0, 0, 0))  # Black = transparent
        
        # Draw boundaries if debug mode is enabled
        if self.config.get('settings.debug_mode', False):
            self.boundary_manager.draw_boundaries(self.screen)
            self.boundary_manager._draw_corner_indicators(self.screen)
        
        # Draw all pets
        for pet in self.pets:
            pet.draw(self.screen)
        
        # Draw debug overlay if enabled
        if self.config.get('settings.show_stats', False):
            self._draw_debug_overlay()
        
        # Update display
        pygame.display.flip()
    
    def _draw_debug_overlay(self) -> None:
        """Draw debug info"""
        font = pygame.font.Font(None, 24)
        debug_color = (255, 255, 255)
        
        debug_info = [
            f"FPS: {self.fps_counter:.1f}",
            f"Pets: {len(self.pets)}",
            f"Method: Tkinter+Pygame",
            f"Transparency: Active",
            f"Resolution: {self.screen_width}x{self.screen_height}"
        ]
        
        # Draw debug text dengan background
        for i, info in enumerate(debug_info):
            # Background rectangle
            text_surface = font.render(info, True, debug_color)
            bg_rect = pygame.Rect(10, 10 + i * 25, text_surface.get_width() + 10, 25)
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
            
            # Text
            self.screen.blit(text_surface, (15, 15 + i * 25))
    
    def _game_loop(self):
        """Game loop dalam thread terpisah"""
        self.game_running = True
        
        while self.game_running and self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(AppConstants.TARGET_FPS)
            except Exception as e:
                print(f"Error in game loop: {e}")
                break
        
        print("Game loop stopped")
    
    def start_game_loop(self):
        """Start game loop dalam thread"""
        if not self.game_thread or not self.game_thread.is_alive():
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()
            print("🎮 Game loop started dalam thread")
    
    def run(self) -> None:
        """Main run method - start both tkinter dan pygame"""
        print("🎮 Starting hybrid transparent desktop pet window...")
        
        # Start pygame game loop dalam thread
        self.start_game_loop()
        
        # Setup tkinter close handler
        def on_closing():
            self.running = False
            self.game_running = False
            self.cleanup()
            self.tk_root.quit()
        
        self.tk_root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run tkinter main loop
        try:
            self.tk_root.mainloop()
        except KeyboardInterrupt:
            print("Interrupted by user")
            on_closing()
    
    def step(self) -> bool:
        """Single frame update untuk integration dengan Qt"""
        if not self.running:
            return False
        
        # Update tkinter
        try:
            self.tk_root.update_idletasks()
            self.tk_root.update()
        except:
            return False
        
        # Update pygame jika thread tidak berjalan
        if not self.game_thread or not self.game_thread.is_alive():
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(AppConstants.TARGET_FPS)
            except:
                return False
        
        return self.running
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance info"""
        cache_info = self.sprite_loader.get_cache_info()
        
        return {
            'fps': self.fps_counter,
            'pet_count': len(self.pets),
            'screen_size': (self.screen_width, self.screen_height),
            'boundaries': self.boundary_manager.boundaries,
            'transparency_method': 'Tkinter+Pygame',
            'sprite_cache': cache_info,
            'memory_usage_mb': cache_info['estimated_memory_mb']
        }
    
    def _print_performance_info(self) -> None:
        """Print performance info"""
        perf_info = self.get_performance_info()
        print("=== Performance Info ===")
        print(f"FPS: {perf_info['fps']:.1f}")
        print(f"Pets: {perf_info['pet_count']}")
        print(f"Method: {perf_info['transparency_method']}")
        print(f"Memory: {perf_info['memory_usage_mb']:.1f}MB")
        print("========================")
    
    def save_pets_state(self) -> List[Dict[str, Any]]:
        """Save pets state"""
        return [pet.save_state() for pet in self.pets]
    
    def load_pets_state(self, pets_data: List[Dict[str, Any]]) -> int:
        """Load pets state"""
        from pet_behavior import DesktopPet
        
        self.clear_all_pets()
        loaded_count = 0
        
        for pet_data in pets_data:
            try:
                pet = DesktopPet.load_from_state(pet_data)
                pet.set_boundary_manager(self.boundary_manager)
                self.pets.append(pet)
                loaded_count += 1
            except Exception as e:
                print(f"Error loading pet state: {e}")
        
        print(f"Loaded {loaded_count} pets from saved state")
        return loaded_count
    
    def get_pets_info(self) -> List[Dict[str, Any]]:
        """Get pets info"""
        return [pet.get_state_info() for pet in self.pets]
    
    def cleanup(self) -> None:
        """Cleanup"""
        print("Cleaning up hybrid transparent window")
        
        # Stop game loop
        self.game_running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=1.0)
        
        # Save state
        pets_state = self.save_pets_state()
        self.config.set('active_pets', pets_state)
        
        # Cleanup pets
        self.clear_all_pets()
        self.sprite_loader.clear_cache()
        
        # Cleanup pygame
        pygame.quit()
        
        # Cleanup tkinter
        try:
            self.tk_root.destroy()
        except:
            pass
    
    def __del__(self):
        """Destructor"""
        if hasattr(self, 'running') and self.running:
            self.cleanup()


# Alias for backward compatibility
TkinterPygameWindow = PygameWindow