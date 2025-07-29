#!/usr/bin/env python3
"""
pet_behavior.py - Pet behavior logic and state management

Handles individual desktop pet instances, their behaviors, interactions,
and state management with proper event handling.
"""

import pygame
import time
from typing import Optional, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass

from config import AppConstants, get_config
from sprite_loader import get_sprite_loader


class PetState(Enum):
    """Pet behavioral states"""
    IDLE = "idle"
    WALKING = "walking"
    SITTING = "sitting"
    DRAGGING = "dragging"
    FALLING = "falling"
    ANIMATING = "animating"


@dataclass
class PetStats:
    """Pet statistics and properties"""
    health: int = 100
    happiness: int = 100
    energy: int = 100
    last_interaction: float = 0
    total_interactions: int = 0


class DesktopPet:
    """Individual desktop pet with behavior and interaction handling"""
    
    def __init__(self, sprite_name: str, x: int = 100, y: int = 100, pet_id: str = None):
        self.sprite_name = sprite_name
        self.pet_id = pet_id or f"{sprite_name}_{int(time.time())}"
        
        # Position and movement
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.velocity_x = 0
        self.velocity_y = 0
        
        # State management
        self.state = PetState.IDLE
        self.previous_state = PetState.IDLE
        self.state_timer = 0.0
        self.animation_frame = 0
        self.animation_timer = 0.0
        
        # Interaction handling
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.last_click_time = 0
        self.click_count = 0
        
        # Pet properties
        self.stats = PetStats()
        self.facing_right = True
        self.on_ground = True
        self.gravity_enabled = True
        
        # Sprite and rendering
        self.sprite_loader = get_sprite_loader()
        self.current_sprite = AppConstants.SPRITE_REQUIRED_FILE
        self.image = self._load_current_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Configuration
        self.config = get_config()
        
        print(f"Created pet: {self.pet_id} at ({x}, {y})")
    
    def _load_current_sprite(self) -> pygame.Surface:
        """Load current sprite image"""
        try:
            sprite = self.sprite_loader.load_sprite(self.sprite_name, self.current_sprite)
            return sprite
        except Exception as e:
            print(f"Error loading sprite for pet {self.pet_id}: {e}")
            # Return fallback sprite
            fallback = pygame.Surface(AppConstants.DEFAULT_SPRITE_SIZE, pygame.SRCALPHA)
            fallback.fill((255, 100, 100, 200))
            return fallback
    
    def update(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Update pet logic and state"""
        self.state_timer += dt
        self.animation_timer += dt
        
        # Update position based on velocity
        if not self.dragging:
            self._update_movement(dt, screen_bounds)
        
        # Update state-specific behavior
        self._update_state_behavior(dt)
        
        # Update animation
        self._update_animation(dt)
        
        # Update statistics
        self._update_stats(dt)
        
        # Update sprite rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _update_movement(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Update pet movement and physics"""
        screen_width, screen_height = screen_bounds
        
        # Apply gravity if enabled and not on ground
        if self.gravity_enabled and not self.on_ground:
            self.velocity_y += 500 * dt  # Gravity acceleration
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Screen boundary collision
        if self.config.get('settings.screen_boundaries', True):
            # Horizontal boundaries
            if self.x < 0:
                self.x = 0
                self.velocity_x = 0
            elif self.x > screen_width - self.rect.width:
                self.x = screen_width - self.rect.width
                self.velocity_x = 0
            
            # Ground collision
            if self.y > screen_height - self.rect.height - AppConstants.SCREEN_MARGIN:
                self.y = screen_height - self.rect.height - AppConstants.SCREEN_MARGIN
                self.velocity_y = 0
                self.on_ground = True
                
                # Change state from falling to idle
                if self.state == PetState.FALLING:
                    self.change_state(PetState.IDLE)
            else:
                self.on_ground = False
    
    def _update_state_behavior(self, dt: float) -> None:
        """Update behavior based on current state"""
        if self.state == PetState.IDLE:
            # Random movement chance
            if self.state_timer > 2.0 and pygame.time.get_ticks() % 100 == 0:
                if pygame.time.get_ticks() % 500 == 0:  # 20% chance every 100ms
                    self._start_random_walk()
        
        elif self.state == PetState.WALKING:
            # Continue walking towards target
            distance_to_target = abs(self.x - self.target_x)
            if distance_to_target < 5:
                # Reached target, stop walking
                self.velocity_x = 0
                self.change_state(PetState.IDLE)
            else:
                # Move towards target
                direction = 1 if self.target_x > self.x else -1
                self.velocity_x = 50 * direction  # Walking speed
                self.facing_right = direction > 0
        
        elif self.state == PetState.SITTING:
            # Sitting behavior - stay still
            self.velocity_x = 0
            if self.state_timer > 5.0:  # Sit for 5 seconds
                self.change_state(PetState.IDLE)
        
        elif self.state == PetState.FALLING:
            # Falling behavior handled in movement update
            pass
    
    def _update_animation(self, dt: float) -> None:
        """Update sprite animation"""
        # Simple animation frame cycling (will be enhanced in P1S3)
        if self.animation_timer > 0.5:  # Change frame every 500ms
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0.0
            
            # Load different sprite based on state (placeholder)
            if self.state == PetState.WALKING:
                frame_sprites = ["shime2.png", "shime3.png"]
            elif self.state == PetState.SITTING:
                # Basic sitting animation - alternate between two sitting poses
                frame_sprites = ["shime11.png", "shime11a.png"]
            else:  # IDLE and other states
                frame_sprites = ["shime1.png", "shime1a.png"]
            
            if self.animation_frame < len(frame_sprites):
                new_sprite = frame_sprites[self.animation_frame]
                if new_sprite != self.current_sprite:
                    self.current_sprite = new_sprite
                    self.image = self._load_current_sprite()
                    
                    # Flip sprite if facing left
                    if not self.facing_right:
                        self.image = pygame.transform.flip(self.image, True, False)
    
    def _update_stats(self, dt: float) -> None:
        """Update pet statistics"""
        # Gradually decrease happiness and energy over time
        self.stats.happiness = max(0, self.stats.happiness - 0.1 * dt)
        self.stats.energy = max(0, self.stats.energy - 0.05 * dt)
        
        # Restore energy when sitting
        if self.state == PetState.SITTING:
            self.stats.energy = min(100, self.stats.energy + 1.0 * dt)
    
    def _start_random_walk(self) -> None:
        """Start random walking behavior"""
        import random
        
        # Choose random target within reasonable range
        max_distance = 200
        direction = random.choice([-1, 1])
        distance = random.randint(50, max_distance)
        
        self.target_x = self.x + (distance * direction)
        self.change_state(PetState.WALKING)
    
    def change_state(self, new_state: PetState) -> None:
        """Change pet state with proper transitions"""
        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state
            self.state_timer = 0.0
            self.animation_frame = 0
            
            print(f"Pet {self.pet_id} changed state: {self.previous_state.value} -> {new_state.value}")
            
            # State-specific initialization
            if new_state == PetState.SITTING:
                self.velocity_x = 0
            elif new_state == PetState.FALLING:
                self.on_ground = False
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int) -> str:
        """Handle mouse button down events"""
        if not self.rect.collidepoint(pos):
            return "none"
        
        current_time = pygame.time.get_ticks()
        
        if button == 1:  # Left click
            self.dragging = True
            self.drag_offset_x = pos[0] - self.rect.x
            self.drag_offset_y = pos[1] - self.rect.y
            self.change_state(PetState.DRAGGING)
            
            # Update interaction stats
            self.stats.last_interaction = time.time()
            self.stats.total_interactions += 1
            self.stats.happiness = min(100, self.stats.happiness + 5)
            
            return "drag_start"
        
        elif button == 3:  # Right click
            # Double right-click detection
            if current_time - self.last_click_time < AppConstants.DOUBLE_CLICK_TIMEOUT:
                return "kill"
            else:
                self.last_click_time = current_time
                # Single right-click - make pet sit
                if self.state != PetState.SITTING:
                    self.change_state(PetState.SITTING)
                return "sit"
        
        return "none"
    
    def handle_mouse_up(self, button: int) -> str:
        """Handle mouse button up events"""
        if button == 1 and self.dragging:  # Left click release
            self.dragging = False
            
            # Return to previous state or idle
            if self.previous_state != PetState.DRAGGING:
                self.change_state(self.previous_state)
            else:
                self.change_state(PetState.IDLE)
            
            return "drag_end"
        
        return "none"
    
    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion for dragging"""
        if self.dragging:
            self.x = pos[0] - self.drag_offset_x
            self.y = pos[1] - self.drag_offset_y
            
            # Update target position
            self.target_x = self.x
            self.target_y = self.y
    
    def handle_speech(self, text: str, duration: float = 10.0) -> None:
        """Handle speech bubble display (placeholder for Phase 2)"""
        print(f"Pet {self.pet_id} says: {text}")
        # TODO: Implement speech bubble in Phase 2
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get comprehensive state information"""
        return {
            'pet_id': self.pet_id,
            'sprite_name': self.sprite_name,
            'position': (self.x, self.y),
            'state': self.state.value,
            'facing_right': self.facing_right,
            'on_ground': self.on_ground,
            'stats': {
                'health': self.stats.health,
                'happiness': self.stats.happiness,
                'energy': self.stats.energy,
                'interactions': self.stats.total_interactions
            },
            'dragging': self.dragging
        }
    
    def save_state(self) -> Dict[str, Any]:
        """Save pet state for persistence"""
        return {
            'pet_id': self.pet_id,
            'sprite_name': self.sprite_name,
            'x': self.x,
            'y': self.y,
            'state': self.state.value,
            'stats': {
                'health': self.stats.health,
                'happiness': self.stats.happiness,
                'energy': self.stats.energy,
                'total_interactions': self.stats.total_interactions
            }
        }
    
    @classmethod
    def load_from_state(cls, state_data: Dict[str, Any]) -> 'DesktopPet':
        """Load pet from saved state"""
        pet = cls(
            sprite_name=state_data['sprite_name'],
            x=state_data['x'],
            y=state_data['y'],
            pet_id=state_data['pet_id']
        )
        
        # Restore state
        pet.change_state(PetState(state_data['state']))
        
        # Restore stats
        stats_data = state_data.get('stats', {})
        pet.stats.health = stats_data.get('health', 100)
        pet.stats.happiness = stats_data.get('happiness', 100)
        pet.stats.energy = stats_data.get('energy', 100)
        pet.stats.total_interactions = stats_data.get('total_interactions', 0)
        
        return pet
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the pet on screen"""
        screen.blit(self.image, self.rect)
        
        # Debug information (can be toggled)
        if self.config.get('settings.debug_mode', False):
            self._draw_debug_info(screen)
    
    def _draw_debug_info(self, screen: pygame.Surface) -> None:
        """Draw debug information overlay"""
        # Draw bounding box
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
        
        # Draw state text
        font = pygame.font.Font(None, 24)
        state_text = font.render(f"{self.state.value}", True, (255, 255, 255))
        screen.blit(state_text, (self.rect.x, self.rect.y - 25))
    
    def cleanup(self) -> None:
        """Cleanup pet resources"""
        print(f"Cleaning up pet: {self.pet_id}")
        # Additional cleanup if needed


# Export the class explicitly
__all__ = ['DesktopPet', 'PetState', 'PetStats']