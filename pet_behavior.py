#!/usr/bin/env python3
"""
pet_behavior.py - Enhanced pet behavior dengan XML animation system

Mengintegrasikan sistem animasi XML untuk memberikan perilaku yang lebih
realistis dan sesuai dengan konfigurasi Shimeji asli.
"""

import pygame
import time
import random
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
from dataclasses import dataclass

from config import AppConstants, get_config
from sprite_loader import get_sprite_loader

# Import animation system dengan error handling
try:
    from utils.animation import AnimationManager, create_animation_manager
    ANIMATION_SYSTEM_AVAILABLE = True
except ImportError:
    print("Warning: Animation system not available, using fallback behavior")
    ANIMATION_SYSTEM_AVAILABLE = False
    AnimationManager = None
    
    def create_animation_manager(sprite_name: str):
        """Fallback function"""
        return None


class PetState(Enum):
    """Pet behavioral states yang sesuai dengan XML actions"""
    # Basic states
    IDLE = "Stand"          # Sesuai dengan action "Stand" di XML
    WALKING = "Walk"        # Sesuai dengan action "Walk" di XML  
    SITTING = "Sit"         # Sesuai dengan action "Sit" di XML
    RUNNING = "Run"         # Sesuai dengan action "Run" di XML
    
    # Special states
    DRAGGING = "Pinched"    # Sesuai dengan action "Pinched" di XML
    FALLING = "Falling"     # Sesuai dengan action "Falling" di XML
    JUMPING = "Jumping"     # Sesuai dengan action "Jumping" di XML
    
    # Wall/ceiling interactions  
    GRAB_WALL = "GrabWall"           # Sesuai dengan action "GrabWall"
    CLIMB_WALL = "ClimbWall"         # Sesuai dengan action "ClimbWall"
    GRAB_CEILING = "GrabCeiling"     # Sesuai dengan action "GrabCeiling"
    CLIMB_CEILING = "ClimbCeiling"   # Sesuai dengan action "ClimbCeiling"
    
    # Special animations
    POSE = "PoseAction"              # Sesuai dengan action "PoseAction"
    EAT_BERRY = "EatBerryAction"     # Sesuai dengan action "EatBerryAction"
    THROW_NEEDLE = "ThrowNeedleAction"    # Sesuai dengan action "ThrowNeedleAction"
    WATCH = "WatchAction"            # Sesuai dengan action "WatchAction"


@dataclass
class PetStats:
    """Pet statistics dengan system yang lebih detailed"""
    health: float = 100.0
    happiness: float = 100.0
    energy: float = 100.0
    last_interaction: float = 0.0
    total_interactions: int = 0
    time_in_current_state: float = 0.0
    
    # Behavioral counters
    walks_taken: int = 0
    times_petted: int = 0
    special_actions_performed: int = 0


class DesktopPet:
    """Enhanced desktop pet dengan XML-driven animations (backward compatible)"""
    
    def __init__(self, sprite_name: str, x: int = 100, y: int = 100, pet_id: str = None):
        self.sprite_name = sprite_name
        self.pet_id = pet_id or f"{sprite_name}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Position and movement
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # State management
        self.state = PetState.IDLE
        self.previous_state = PetState.IDLE
        self.state_timer = 0.0
        self.state_duration = 0.0  # How long to stay in current state
        
        # Animation system - with fallback
        self.animation_manager = None
        if ANIMATION_SYSTEM_AVAILABLE and create_animation_manager:
            try:
                self.animation_manager = create_animation_manager(sprite_name)
                if self.animation_manager:
                    print(f"Animation system loaded for {sprite_name}")
                else:
                    print(f"Warning: Failed to create animation manager for {sprite_name}")
            except Exception as e:
                print(f"Error creating animation manager: {e}")
                self.animation_manager = None
        
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
        
        # Behavioral properties
        self.behavior_timer = 0.0
        self.idle_timer = 0.0
        self.action_queue = []  # Queue of actions to perform
        
        # Sprite and rendering - with fallback system
        self.sprite_loader = get_sprite_loader()
        self.current_sprite = None
        self.current_velocity = (0.0, 0.0)
        self.current_sprite_name = AppConstants.SPRITE_REQUIRED_FILE
        self.animation_frame = 0
        self.animation_timer = 0.0
        
        # Load initial sprite
        self.image = self._load_current_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Configuration
        self.config = get_config()
        
        # Initialize animation
        self._initialize_animation()
        
        print(f"Enhanced pet created: {self.pet_id} at ({x}, {y})")
    
    def _load_current_sprite(self) -> pygame.Surface:
        """Load current sprite image dengan error handling"""
        try:
            sprite = self.sprite_loader.load_sprite(self.sprite_name, self.current_sprite_name)
            return sprite
        except Exception as e:
            print(f"Error loading sprite for pet {self.pet_id}: {e}")
            # Return fallback sprite
            fallback = pygame.Surface(AppConstants.DEFAULT_SPRITE_SIZE, pygame.SRCALPHA)
            fallback.fill((255, 100, 100, 200))
            return fallback
    
    def _initialize_animation(self) -> None:
        """Initialize animation system dengan fallback"""
        if self.animation_manager:
            try:
                # Start with idle animation
                success = self.animation_manager.play_action(self.state.value, loop=True)
                if success:
                    self.animation_manager.set_facing_direction(self.facing_right)
                    
                    # Get available actions for debugging
                    available_actions = self.animation_manager.get_available_actions()
                    print(f"Available animations for {self.sprite_name}: {len(available_actions)} actions")
                else:
                    print(f"Warning: Could not start initial animation for {self.sprite_name}")
            except Exception as e:
                print(f"Error initializing animation: {e}")
                self.animation_manager = None
    
    def update(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Enhanced update dengan XML animation system dan fallback"""
        self.state_timer += dt
        self.behavior_timer += dt
        self.stats.time_in_current_state += dt
        
        # Update animation system
        if self.animation_manager:
            try:
                self.current_sprite, anim_velocity = self.animation_manager.update(dt)
                
                # Use animation velocity if not dragging
                if not self.dragging and self.state in [PetState.WALKING, PetState.RUNNING]:
                    # Apply animation velocity dengan facing direction
                    vel_x = anim_velocity[0] if self.facing_right else -anim_velocity[0]
                    self.velocity_x = vel_x
                    self.velocity_y = anim_velocity[1]
                
                # Update image reference
                if self.current_sprite:
                    self.image = self.current_sprite
            except Exception as e:
                print(f"Error updating animation: {e}")
                # Fallback to basic animation
                self._update_fallback_animation(dt)
        else:
            # Use fallback animation system
            self._update_fallback_animation(dt)
        
        # Update position based on velocity
        if not self.dragging:
            self._update_movement(dt, screen_bounds)
        
        # Update state-specific behavior
        self._update_state_behavior(dt)
        
        # Update behavioral AI
        self._update_behavioral_ai(dt)
        
        # Update statistics  
        self._update_stats(dt)
        
        # Update sprite rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _update_fallback_animation(self, dt: float) -> None:
        """Fallback animation system untuk compatibility"""
        self.animation_timer += dt
        
        # Simple animation frame cycling
        if self.animation_timer > 0.5:  # Change frame every 500ms
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0.0
            
            # Load different sprite based on state
            if self.state == PetState.WALKING:
                frame_sprites = ["shime2.png", "shime3.png"]
            elif self.state == PetState.SITTING:
                frame_sprites = ["shime11.png", "shime11a.png"]
            elif self.state == PetState.RUNNING:
                frame_sprites = ["shime3e.png", "shime3f.png"]
            else:  # IDLE and other states
                frame_sprites = ["shime1.png", "shime1a.png"]
            
            if self.animation_frame < len(frame_sprites):
                new_sprite = frame_sprites[self.animation_frame]
                if new_sprite != self.current_sprite_name:
                    self.current_sprite_name = new_sprite
                    self.image = self._load_current_sprite()
                    
                    # Flip sprite if facing left
                    if not self.facing_right:
                        self.image = pygame.transform.flip(self.image, True, False)
    
    def _update_movement(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Enhanced movement dengan better physics"""
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
                self._change_direction()
            elif self.x > screen_width - self.rect.width:
                self.x = screen_width - self.rect.width
                self.velocity_x = 0
                self._change_direction()
            
            # Ground collision
            ground_y = screen_height - self.rect.height - AppConstants.SCREEN_MARGIN
            if self.y >= ground_y:
                self.y = ground_y
                self.velocity_y = 0
                self.on_ground = True
                
                # Change state from falling to idle
                if self.state == PetState.FALLING:
                    self.change_state(PetState.IDLE)
            else:
                self.on_ground = False
    
    def _update_state_behavior(self, dt: float) -> None:
        """Enhanced state behavior management"""
        if self.state == PetState.IDLE:
            # Check if idle too long, maybe do something interesting
            if self.state_timer > 3.0:
                self._decide_next_action()
        
        elif self.state in [PetState.WALKING, PetState.RUNNING]:
            # Check if reached target or animation completed
            distance_to_target = abs(self.x - self.target_x)
            animation_completed = True
            
            if self.animation_manager:
                try:
                    animation_completed = self.animation_manager.is_animation_completed()
                except:
                    animation_completed = True
            
            if distance_to_target < 10 or animation_completed:
                self.velocity_x = 0
                self.change_state(PetState.IDLE)
                self.stats.walks_taken += 1
        
        elif self.state == PetState.SITTING:
            # Sitting behavior - gradually restore energy
            self.stats.energy = min(100, self.stats.energy + 10 * dt)
            if self.state_timer > 5.0:  # Sit for 5 seconds
                self.change_state(PetState.IDLE)
        
        elif self.state in [PetState.POSE, PetState.EAT_BERRY, PetState.THROW_NEEDLE]:
            # Special actions - wait for animation to complete
            animation_completed = True
            if self.animation_manager:
                try:
                    animation_completed = self.animation_manager.is_animation_completed()
                except:
                    animation_completed = True
            
            if animation_completed or self.state_timer > 3.0:  # Fallback timeout
                self.change_state(PetState.IDLE)
                self.stats.special_actions_performed += 1
        
        elif self.state == PetState.WATCH:
            # Watch behavior - stay focused
            if self.state_timer > 10.0:  # Watch for 10 seconds
                self.change_state(PetState.IDLE)
    
    def _update_behavioral_ai(self, dt: float) -> None:
        """Advanced AI untuk behavior selection"""
        # Only make decisions when idle and on ground
        if self.state != PetState.IDLE or not self.on_ground:
            return
        
        # Random behavior selection based on stats and time
        if self.behavior_timer > 2.0:  # Check every 2 seconds
            self.behavior_timer = 0.0
            
            # Calculate behavior probabilities based on stats
            energy_factor = self.stats.energy / 100.0
            happiness_factor = self.stats.happiness / 100.0
            
            # Higher chance of activity when happy and energetic
            activity_chance = (energy_factor + happiness_factor) / 2.0
            
            if random.random() < activity_chance * 0.3:  # 30% base chance
                self._decide_next_action()
    
    def _decide_next_action(self) -> None:
        """Decide next action berdasarkan AI"""
        possible_actions = []
        
        # Basic movement actions
        if self.stats.energy > 30:
            possible_actions.extend([
                (PetState.WALKING, 40),  # (action, weight)
                (PetState.RUNNING, 20),
            ])
        
        # Rest actions
        if self.stats.energy < 70:
            possible_actions.extend([
                (PetState.SITTING, 30),
            ])
        
        # Special actions
        if self.stats.happiness > 50:
            possible_actions.extend([
                (PetState.POSE, 15),
                (PetState.EAT_BERRY, 10),
                (PetState.WATCH, 20),
            ])
        
        # Random special actions
        if random.random() < 0.1:  # 10% chance
            possible_actions.extend([
                (PetState.THROW_NEEDLE, 5),
            ])
        
        if possible_actions:
            # Weighted random selection
            total_weight = sum(weight for _, weight in possible_actions)
            random_value = random.randint(1, total_weight)
            
            current_weight = 0
            for action, weight in possible_actions:
                current_weight += weight
                if random_value <= current_weight:
                    if action in [PetState.WALKING, PetState.RUNNING]:
                        self._start_movement(action)
                    else:
                        self.change_state(action)
                    break
    
    def _start_movement(self, movement_type: PetState) -> None:
        """Start movement dengan target random"""
        # Choose random target within reasonable range
        max_distance = 300 if movement_type == PetState.RUNNING else 150
        direction = random.choice([-1, 1])
        distance = random.randint(50, max_distance)
        
        self.target_x = max(0, min(1920, self.x + (distance * direction)))  # Clamp to screen
        self.facing_right = direction > 0
        
        # Update animation facing direction
        if self.animation_manager:
            try:
                self.animation_manager.set_facing_direction(self.facing_right)
            except:
                pass
        
        self.change_state(movement_type)
    
    def _change_direction(self) -> None:
        """Change facing direction"""
        self.facing_right = not self.facing_right
        if self.animation_manager:
            try:
                self.animation_manager.set_facing_direction(self.facing_right)  
            except:
                pass
    
    def _update_stats(self, dt: float) -> None:
        """Enhanced stats management"""
        # Gradually decrease happiness and energy over time
        self.stats.happiness = max(0, self.stats.happiness - 0.5 * dt)
        self.stats.energy = max(0, self.stats.energy - 0.3 * dt)
        
        # Restore energy when sitting or idle
        if self.state in [PetState.SITTING, PetState.IDLE]:
            self.stats.energy = min(100, self.stats.energy + 0.5 * dt)
        
        # Restore happiness with interactions
        time_since_interaction = time.time() - self.stats.last_interaction
        if time_since_interaction < 10:  # Recent interaction
            self.stats.happiness = min(100, self.stats.happiness + 1 * dt)
    
    def change_state(self, new_state: PetState) -> None:
        """Enhanced state changing dengan animation integration"""
        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state
            self.state_timer = 0.0
            
            print(f"Pet {self.pet_id} changed state: {self.previous_state.value} -> {new_state.value}")
            
            # Start appropriate animation
            if self.animation_manager:
                try:
                    loop_animation = new_state in [PetState.IDLE, PetState.WALKING, 
                                                 PetState.RUNNING, PetState.SITTING,
                                                 PetState.GRAB_WALL, PetState.GRAB_CEILING]
                    self.animation_manager.play_action(new_state.value, loop=loop_animation)
                except Exception as e:
                    print(f"Error starting animation for {new_state.value}: {e}")
            
            # State-specific initialization
            if new_state == PetState.SITTING:
                self.velocity_x = 0
            elif new_state == PetState.FALLING:
                self.on_ground = False
            elif new_state == PetState.DRAGGING:
                self.velocity_x = 0
                self.velocity_y = 0
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int) -> str:
        """Enhanced mouse handling"""
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
            self.stats.times_petted += 1
            self.stats.happiness = min(100, self.stats.happiness + 10)
            
            return "drag_start"
        
        elif button == 3:  # Right click
            # Double right-click detection
            if current_time - self.last_click_time < AppConstants.DOUBLE_CLICK_TIMEOUT:
                return "kill"
            else:
                self.last_click_time = current_time
                # Single right-click - cycle through sitting actions
                if self.state != PetState.SITTING:
                    self.change_state(PetState.SITTING)
                else:
                    # If already sitting, do a special action
                    special_actions = [PetState.POSE, PetState.EAT_BERRY, PetState.WATCH]
                    chosen_action = random.choice(special_actions)
                    self.change_state(chosen_action)
                return "sit"
        
        return "none"
    
    def handle_mouse_up(self, button: int) -> str:
        """Enhanced mouse up handling"""
        if button == 1 and self.dragging:  # Left click release
            self.dragging = False
            
            # Return to appropriate state based on position
            if self.on_ground:
                self.change_state(PetState.IDLE)
            else:
                self.change_state(PetState.FALLING)
            
            return "drag_end"
        
        return "none"
    
    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Enhanced mouse motion handling"""
        if self.dragging:
            self.x = float(pos[0] - self.drag_offset_x) 
            self.y = float(pos[1] - self.drag_offset_y)
            
            # Update target position
            self.target_x = self.x
            self.target_y = self.y
    
    def handle_speech(self, text: str, duration: float = 10.0) -> None:
        """Handle speech bubble display (enhanced for Phase 2)"""
        print(f"Pet {self.pet_id} says: {text}")
        # TODO: Implement speech bubble system dalam Phase 2
        
        # Update happiness when receiving speech
        self.stats.happiness = min(100, self.stats.happiness + 5)
        self.stats.last_interaction = time.time()
    
    def trigger_special_action(self, action_name: str) -> bool:
        """Trigger special action dari external command"""
        try:
            special_state = PetState(action_name)
            if special_state != self.state:
                self.change_state(special_state)
                return True
        except ValueError:
            print(f"Unknown action: {action_name}")
        return False
    
    def get_state_info(self) -> Dict[str, Any]:
        """Enhanced state information"""
        animation_info = {}
        if self.animation_manager:
            try:
                animation_info = self.animation_manager.get_current_animation_info()
            except:
                animation_info = {'error': 'animation_manager_error'}
        
        return {
            'pet_id': self.pet_id,
            'sprite_name': self.sprite_name,
            'position': (self.x, self.y),
            'target_position': (self.target_x, self.target_y),
            'velocity': (self.velocity_x, self.velocity_y),
            'state': self.state.value,
            'previous_state': self.previous_state.value,
            'state_timer': self.state_timer,
            'facing_right': self.facing_right,
            'on_ground': self.on_ground,
            'dragging': self.dragging,
            'stats': {
                'health': self.stats.health,
                'happiness': self.stats.happiness,
                'energy': self.stats.energy,
                'interactions': self.stats.total_interactions,
                'walks_taken': self.stats.walks_taken,
                'times_petted': self.stats.times_petted,
                'special_actions': self.stats.special_actions_performed,
                'time_in_state': self.stats.time_in_current_state
            },
            'animation': animation_info,
            'animation_system': self.animation_manager is not None
        }
    
    def save_state(self) -> Dict[str, Any]:
        """Enhanced state persistence"""
        return {
            'pet_id': self.pet_id,
            'sprite_name': self.sprite_name,
            'x': self.x,
            'y': self.y,
            'target_x': self.target_x,
            'target_y': self.target_y,
            'state': self.state.value,
            'facing_right': self.facing_right,
            'stats': {
                'health': self.stats.health,
                'happiness': self.stats.happiness,
                'energy': self.stats.energy,
                'total_interactions': self.stats.total_interactions,
                'walks_taken': self.stats.walks_taken,
                'times_petted': self.stats.times_petted,
                'special_actions_performed': self.stats.special_actions_performed
            }
        }
    
    @classmethod
    def load_from_state(cls, state_data: Dict[str, Any]) -> 'DesktopPet':
        """Load pet dari saved state dengan enhancement"""
        pet = cls(
            sprite_name=state_data['sprite_name'],
            x=int(state_data['x']),
            y=int(state_data['y']),
            pet_id=state_data['pet_id']
        )
        
        # Restore position dan targets
        pet.target_x = state_data.get('target_x', pet.x)
        pet.target_y = state_data.get('target_y', pet.y)
        pet.facing_right = state_data.get('facing_right', True)
        
        # Restore state
        try:
            pet.change_state(PetState(state_data['state']))
        except ValueError:
            pet.change_state(PetState.IDLE)
        
        # Restore stats
        stats_data = state_data.get('stats', {})
        pet.stats.health = stats_data.get('health', 100)
        pet.stats.happiness = stats_data.get('happiness', 100)
        pet.stats.energy = stats_data.get('energy', 100)
        pet.stats.total_interactions = stats_data.get('total_interactions', 0)
        pet.stats.walks_taken = stats_data.get('walks_taken', 0)
        pet.stats.times_petted = stats_data.get('times_petted', 0)
        pet.stats.special_actions_performed = stats_data.get('special_actions_performed', 0)
        
        # Update animation facing direction
        if pet.animation_manager:
            try:
                pet.animation_manager.set_facing_direction(pet.facing_right)
            except:
                pass
        
        return pet
    
    def draw(self, screen: pygame.Surface) -> None:
        """Enhanced drawing dengan better sprite handling"""
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback drawing
            pygame.draw.rect(screen, (255, 100, 100), self.rect)
        
        # Debug information
        if self.config.get('settings.debug_mode', False):
            self._draw_debug_info(screen)
        
        # Stats overlay (optional)
        if self.config.get('settings.show_stats', False):
            self._draw_stats_overlay(screen)
    
    def _draw_debug_info(self, screen: pygame.Surface) -> None:
        """Enhanced debug information"""
        # Draw bounding box
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
        
        # Draw velocity vector
        if abs(self.velocity_x) > 0 or abs(self.velocity_y) > 0:
            start_pos = (self.rect.centerx, self.rect.centery)
            end_pos = (
                int(start_pos[0] + self.velocity_x / 10),
                int(start_pos[1] + self.velocity_y / 10)
            )
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)
        
        # Draw target position
        if abs(self.target_x - self.x) > 5:
            target_rect = pygame.Rect(int(self.target_x), int(self.target_y), 5, 5)
            pygame.draw.rect(screen, (0, 0, 255), target_rect)
        
        # Draw state text
        font = pygame.font.Font(None, 20)
        state_text = font.render(f"{self.state.value}", True, (255, 255, 255))
        screen.blit(state_text, (self.rect.x, self.rect.y - 25))
        
        # Draw facing direction indicator
        if self.facing_right:
            pygame.draw.polygon(screen, (255, 255, 0), [
                (self.rect.right - 10, self.rect.top + 5),
                (self.rect.right - 5, self.rect.top + 10),
                (self.rect.right - 10, self.rect.top + 15)
            ])
        else:
            pygame.draw.polygon(screen, (255, 255, 0), [
                (self.rect.left + 10, self.rect.top + 5),
                (self.rect.left + 5, self.rect.top + 10),
                (self.rect.left + 10, self.rect.top + 15)
            ])
    
    def _draw_stats_overlay(self, screen: pygame.Surface) -> None:
        """Draw stats overlay untuk monitoring"""
        font = pygame.font.Font(None, 16)
        y_offset = 0
        
        stats_info = [
            f"Health: {self.stats.health:.0f}",
            f"Happy: {self.stats.happiness:.0f}",
            f"Energy: {self.stats.energy:.0f}",
            f"State: {self.state.value}",
        ]
        
        for stat_text in stats_info:
            text_surface = font.render(stat_text, True, (255, 255, 255))
            # Draw background
            bg_rect = text_surface.get_rect()
            bg_rect.x = self.rect.x - 50
            bg_rect.y = self.rect.y + y_offset
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            # Draw text
            screen.blit(text_surface, (self.rect.x - 50, self.rect.y + y_offset))
            y_offset += 18
    
    def get_available_actions(self) -> List[str]:
        """Get list semua action yang tersedia"""
        if self.animation_manager:
            try:
                return self.animation_manager.get_available_actions()
            except:
                pass
        return ["Stand", "Walk", "Sit", "Run"]  # Fallback actions
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information untuk debugging"""
        animation_info = {}
        if self.animation_manager:
            try:
                animation_info = self.animation_manager.get_current_animation_info()
            except:
                animation_info = {'error': 'animation_manager_error'}
        
        return {
            'pet_id': self.pet_id,
            'sprite_name': self.sprite_name,
            'animation_system_loaded': self.animation_manager is not None,
            'current_animation': animation_info,
            'update_frequency': '30 FPS target',
            'memory_footprint': 'Light (sprites cached)'
        }
    
    def cleanup(self) -> None:
        """Enhanced cleanup"""
        print(f"Cleaning up enhanced pet: {self.pet_id}")
        
        # Stop any running animations
        if self.animation_manager:
            try:
                self.animation_manager.stop_current_animation()
            except:
                pass
        
        # Clear references
        self.animation_manager = None
        self.current_sprite = None


# Export classes
__all__ = ['DesktopPet', 'PetState', 'PetStats']