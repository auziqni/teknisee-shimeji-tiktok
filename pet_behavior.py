#!/usr/bin/env python3
"""
pet_behavior.py - Enhanced with boundary system integration

Integrates boundary collision detection, wall climbing, and corner bouncing
with the existing physics and animation system.
"""

import pygame
import time
import random
from typing import Optional, Tuple, Dict, Any, List, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

from config import AppConstants, get_config
from sprite_loader import get_sprite_loader

if TYPE_CHECKING:
    from gui_manager import BoundaryManager

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
    IDLE = "Stand"
    WALKING = "Walk"
    SITTING = "Sit"
    RUNNING = "Run"
    
    # Physics states
    DRAGGING = "Pinched"
    FALLING = "Falling"
    JUMPING = "Jumping"
    THROWN = "Thrown"
    BOUNCING = "Bouncing"
    
    # Wall/ceiling interactions (enhanced)
    GRAB_WALL = "GrabWall"
    CLIMB_WALL = "ClimbWall"
    GRAB_CEILING = "GrabCeiling"
    CLIMB_CEILING = "ClimbCeiling"
    
    # Special animations
    POSE = "PoseAction"
    EAT_BERRY = "EatBerryAction"
    THROW_NEEDLE = "ThrowNeedleAction"
    WATCH = "WatchAction"


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
    wall_climbs: int = 0  # NEW: wall climbing counter


class DesktopPet:
    """Enhanced desktop pet dengan boundary system integration"""
    
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
        self.state_duration = 0.0
        
        # NEW: Walk duration tracking
        self.walk_duration = 0.0
        self.walk_start_time = 0.0
        
        # NEW: Boundary system integration
        self.boundary_manager: Optional['BoundaryManager'] = None
        self.on_wall = False
        self.wall_side = None  # 'left' or 'right'
        self.wall_climb_timer = 0.0
        
        # NEW: Collision prevention system
        self.last_collision_time = 0.0
        self.collision_cooldown = 0.5  # Minimum time between collisions
        self.direction_lock_timer = 0.0
        self.direction_lock_duration = 0.3  # Lock direction for this duration
        self.last_wall_side = None
        
        # Enhanced direction change cooldown to prevent glitches
        self.direction_change_cooldown = 0.5  # seconds
        self.last_direction_change = 0.0
        
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
        
        # Configuration and Physics parameters
        self.config = get_config()
        self.update_physics_parameters()
        
        # Behavioral properties
        self.behavior_timer = 0.0
        self.idle_timer = 0.0
        self.action_queue = []
        
        # Sprite and rendering
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
        
        # Initialize animation
        self._initialize_animation()
        
        # Lifecycle management
        self.running = True
        
        print(f"Enhanced pet created: {self.pet_id} at ({x}, {y})")

    def set_boundary_manager(self, boundary_manager: 'BoundaryManager') -> None:
        """Set the boundary manager for collision detection"""
        self.boundary_manager = boundary_manager
        print(f"Pet {self.pet_id} connected to boundary system")

    def update_physics_parameters(self) -> None:
        """Updates physics parameters from the global config."""
        self.GRAVITY_ACCELERATION = self.config.get('settings.physics_gravity_acceleration', 980)
        self.AIR_RESISTANCE_FACTOR = self.config.get('settings.physics_air_resistance_factor', 0.001)
        self.BOUNCE_COEFFICIENT = self.config.get('settings.physics_bounce_coefficient', 0.2)
        self.MIN_BOUNCE_VELOCITY = self.config.get('settings.physics_min_bounce_velocity', 100)
        self.DRAG_THROW_MULTIPLIER = self.config.get('settings.physics_drag_throw_multiplier', 6.0)
    
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
                success = self.animation_manager.play_action(self.state.value, loop=True)
                if success:
                    self.animation_manager.set_facing_direction(not self.facing_right)
                    available_actions = self.animation_manager.get_available_actions()
                    print(f"Available animations for {self.sprite_name}: {len(available_actions)} actions")
                else:
                    print(f"Warning: Could not start initial animation for {self.sprite_name}")
            except Exception as e:
                print(f"Error initializing animation: {e}")
                self.animation_manager = None
    
    def update(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Enhanced update method with direction lock timer and improved wall climbing"""
        # Update timers
        self.state_timer += dt
        self.behavior_timer += dt
        self.wall_climb_timer += dt
        self.direction_lock_timer += dt  # Update direction lock timer
        
        # Update rectangle position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Update movement with boundaries
        self._update_movement_with_boundaries(dt, screen_bounds)
        
        # Update state behavior
        self._update_state_behavior(dt)
        
        # Update behavioral AI
        self._update_behavioral_ai(dt)
        
        # Update stats
        self._update_stats(dt)
    
    def _update_movement_with_boundaries(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Enhanced movement with boundary collision detection and wall climbing"""
        if not self.boundary_manager:
            self._update_movement_fallback(dt, screen_bounds)
            return
        
        # Store previous position for collision detection
        prev_x = self.x
        prev_y = self.y
        
        # Update position based on current state
        if self.state == PetState.DRAGGING:
            # While dragging, only update position if not wall-stuck
            if not self.on_wall:
                # Normal drag movement - position is set by mouse motion
                pass
        else:
            # Apply velocity and gravity
            if self.gravity_enabled:
                self.velocity_y += self.GRAVITY_ACCELERATION * dt
            
            # Apply air resistance
            self.velocity_x *= (1 - self.AIR_RESISTANCE_FACTOR)
            self.velocity_y *= (1 - self.AIR_RESISTANCE_FACTOR)
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Check boundary collisions
        collision = self.boundary_manager.check_boundary_collision(
            self.x, self.y, self.rect.width, self.rect.height
        )
        
        # Handle collisions
        self._handle_boundary_collisions(collision, prev_x, prev_y)
        
        # Update animation
        if self.animation_manager:
            try:
                current_sprite, velocity = self.animation_manager.update(dt)
                # Update the displayed sprite
                if current_sprite:
                    self.image = current_sprite
                # Apply animation velocity if not dragging, with direction awareness
                if self.state != PetState.DRAGGING:
                    # Apply velocity based on facing direction
                    # If facing right, invert the X velocity from animation (which is hardcoded to left)
                    velocity_x = velocity[0] * dt
                    if self.facing_right and velocity[0] != 0:
                        velocity_x = -velocity[0] * dt  # Invert for right-facing movement
                    
                    self.velocity_x += velocity_x
                    self.velocity_y += velocity[1] * dt
            except Exception as e:
                print(f"Animation update error: {e}")
                self._update_fallback_animation(dt)
        
        # Update stats
        self._update_stats(dt)
    
    def _handle_boundary_collisions(self, collision: Dict[str, bool], prev_x: float, prev_y: float) -> None:
        """Enhanced boundary collision handling with wall climbing and drag support"""
        wall_climbing_enabled = self.config.get('boundaries.wall_climbing_enabled', True)
        
        # Handle wall collisions
        if collision['left_wall'] or collision['right_wall']:
            side = 'left' if collision['left_wall'] else 'right'
            self._handle_wall_collision(side, wall_climbing_enabled)
        
        # Handle ground collision
        if collision['ground']:
            self._handle_ground_collision()
        
        # Handle ceiling collision (for future use)
        if collision['ceiling']:
            self._handle_ceiling_collision()
        
        # Special handling for drag + wall collision
        if self.state == PetState.DRAGGING and (collision['left_wall'] or collision['right_wall']):
            side = 'left' if collision['left_wall'] else 'right'
            self._handle_drag_wall_collision(side)
    
    def _handle_wall_bounce(self, side: str) -> None:
        """Handle simple wall bounce when pet is on ground"""
        boundaries = self.boundary_manager.boundaries
        
        if side == 'left':
            self.x = boundaries['left_wall_x']
        else:  # right
            self.x = boundaries['right_wall_x'] - self.rect.width
        
        # Simple bounce physics
        self.velocity_x *= -self.BOUNCE_COEFFICIENT
        if abs(self.velocity_x) < self.MIN_BOUNCE_VELOCITY:
            self.velocity_x = 0
        
        self._change_direction()
        print(f"Pet {self.pet_id} bounced off {side} wall while on ground")
    
    def _handle_wall_collision(self, side: str, wall_climbing_enabled: bool) -> None:
        """Enhanced wall collision handling with proper wall climbing and drag support"""
        if not self.boundary_manager:
            return
        
        boundaries = self.boundary_manager.boundaries
        
        # Position pet exactly on the wall
        if side == 'left':
            self.x = boundaries['left_wall_x']
        else:  # right
            self.x = boundaries['right_wall_x'] - self.rect.width
        
        # Handle wall climbing logic
        if wall_climbing_enabled and self.state not in [PetState.DRAGGING] and not self.on_ground:
            # Start wall climbing if moving towards wall or already on wall
            if (side == 'left' and self.velocity_x < 0) or (side == 'right' and self.velocity_x > 0) or self.on_wall:
                self.on_wall = True
                self.wall_side = side
                self.on_ground = False
                self.gravity_enabled = False
                self.velocity_x = 0
                
                # Start climbing animation if not already climbing
                if self.state != PetState.CLIMB_WALL:
                    self.change_state(PetState.GRAB_WALL)
                    self.stats.wall_climbs += 1
                    self.wall_climb_timer = 0.0
                    print(f"Pet {self.pet_id} started wall climbing on {side} wall")
        else:
            # Regular wall bounce for non-climbing scenarios
            self.velocity_x *= -self.BOUNCE_COEFFICIENT
            if abs(self.velocity_x) < self.MIN_BOUNCE_VELOCITY:
                self.velocity_x = 0
            self._change_direction()
            self.on_wall = False
    
    def _handle_corner_collision(self, wall_side: str) -> None:
        """Enhanced corner collision handling with direction lock to prevent glitches"""
        print(f"Pet {self.pet_id} corner collision at {wall_side} wall")
        
        # Lock direction changes to prevent glitches
        self._lock_direction(0.8)  # Lock for 0.8 seconds
        
        # Turn away from the wall with proper timing
        if wall_side == 'left':
            # Move right away from left wall
            self.facing_right = True
        else:  # right wall
            # Move left away from right wall
            self.facing_right = False
        
        # Update animation facing direction (invert for visual correction)
        if self.animation_manager:
            try:
                self.animation_manager.set_facing_direction(not self.facing_right)
            except Exception as e:
                print(f"Error updating animation direction in corner collision: {e}")
        
        # Use the movement system to start walking away from the wall
        # Set a target in the new direction (away from the wall)
        if self.boundary_manager:
            playable = self.boundary_manager.get_playable_area()
            if self.facing_right:
                # Move right away from left wall
                self.target_x = min(self.x + 120, playable['right'] - self.rect.width)
            else:
                # Move left away from right wall
                self.target_x = max(self.x - 120, playable['left'])
        else:
            # Fallback movement
            if self.facing_right:
                self.target_x = min(self.x + 120, 1920 - self.rect.width)
            else:
                self.target_x = max(self.x - 120, 0)
        
        # Change to walking state
        self.change_state(PetState.WALKING)
        print(f"Pet {self.pet_id} turning away from {wall_side} wall, direction locked for 0.8s")
    
    def _handle_wall_turn_around(self, wall_side: str) -> None:
        """Enhanced wall turn around with direction lock to prevent glitches"""
        print(f"Pet {self.pet_id} turned around at {wall_side} wall")
        
        # Lock direction changes to prevent glitches
        self._lock_direction(0.6)  # Lock for 0.6 seconds
        
        # Stop horizontal movement to prevent oscillation
        self.velocity_x = 0
        
        # Turn around with proper timing
        self._change_direction()
        
        # Set a brief pause to prevent immediate re-collision
        self.behavior_timer = 0.0  # Reset behavior timer
        
        # Use the movement system to start walking in the new direction
        # Set a target in the new direction (away from the wall)
        if self.boundary_manager:
            playable = self.boundary_manager.get_playable_area()
            if self.facing_right:
                # Move right away from left wall
                self.target_x = min(self.x + 150, playable['right'] - self.rect.width)
            else:
                # Move left away from right wall
                self.target_x = max(self.x - 150, playable['left'])
        else:
            # Fallback movement
            if self.facing_right:
                self.target_x = min(self.x + 150, 1920 - self.rect.width)
            else:
                self.target_x = max(self.x - 150, 0)
        
        # Change to walking state to start movement
        self.change_state(PetState.WALKING)
        print(f"Pet {self.pet_id} turned around at {wall_side} wall, direction locked for 0.6s")
    
    def _handle_drag_wall_collision(self, side: str) -> None:
        """Handle wall collision while dragging - pet sticks to wall"""
        if not self.boundary_manager:
            return
        
        boundaries = self.boundary_manager.boundaries
        
        # Position pet exactly on the wall
        if side == 'left':
            self.x = boundaries['left_wall_x']
            self.facing_right = False  # Face toward left wall
        else:  # right
            self.x = boundaries['right_wall_x'] - self.rect.width
            self.facing_right = True  # Face toward right wall
        
        # Set wall sticking state
        self.on_wall = True
        self.wall_side = side
        self.on_ground = False
        self.gravity_enabled = False
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Update animation facing direction
        if self.animation_manager:
            try:
                # Animation manager's set_facing_direction expects the visual direction
                self.animation_manager.set_facing_direction(self.facing_right)
            except:
                pass
        
        print(f"Pet {self.pet_id} stuck to {side} wall during drag")
    
    def _handle_ground_collision(self) -> None:
        """Handle ground collision"""
        if not self.boundary_manager:
            return
        
        boundaries = self.boundary_manager.boundaries
        self.y = boundaries['ground_y'] - self.rect.height
        
        if abs(self.velocity_y) > self.MIN_BOUNCE_VELOCITY:
            self.velocity_y *= -self.BOUNCE_COEFFICIENT
            self.change_state(PetState.BOUNCING)
        else:
            self.velocity_y = 0
            self.on_ground = True
            self.on_wall = False
            if self.state in [PetState.FALLING, PetState.THROWN, PetState.BOUNCING]:
                self.change_state(PetState.IDLE)
    
    def _handle_ceiling_collision(self) -> None:
        """Handle ceiling collision"""
        if not self.boundary_manager:
            return
        
        boundaries = self.boundary_manager.boundaries
        self.y = boundaries['ceiling_y']
        self.velocity_y = max(0, self.velocity_y)  # Stop upward movement
    
    def _update_movement_fallback(self, dt: float, screen_bounds: Tuple[int, int]) -> None:
        """Fallback movement system when boundary manager not available"""
        screen_width, screen_height = screen_bounds
        
        # Apply gravity if enabled and not on ground
        if self.gravity_enabled and not self.on_ground:
            self.velocity_y += self.GRAVITY_ACCELERATION * dt
            
            # Apply air resistance
            self.velocity_x *= (1 - self.AIR_RESISTANCE_FACTOR * dt)
            self.velocity_y *= (1 - self.AIR_RESISTANCE_FACTOR * dt)
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Basic screen boundary collision
        if self.config.get('settings.screen_boundaries', True):
            # Horizontal boundaries
            if self.x < 0:
                self.x = 0
                self.velocity_x *= -self.BOUNCE_COEFFICIENT
                if abs(self.velocity_x) < self.MIN_BOUNCE_VELOCITY: 
                    self.velocity_x = 0
                self._change_direction()
            elif self.x > screen_width - self.rect.width:
                self.x = screen_width - self.rect.width
                self.velocity_x *= -self.BOUNCE_COEFFICIENT
                if abs(self.velocity_x) < self.MIN_BOUNCE_VELOCITY: 
                    self.velocity_x = 0
                self._change_direction()
            
            # Ground collision
            ground_y = screen_height - self.rect.height - AppConstants.SCREEN_MARGIN
            if self.y >= ground_y:
                self.y = ground_y
                
                if abs(self.velocity_y) > self.MIN_BOUNCE_VELOCITY:
                    self.velocity_y *= -self.BOUNCE_COEFFICIENT
                    self.change_state(PetState.BOUNCING)
                else:
                    self.velocity_y = 0
                    self.on_ground = True
                    if self.state in [PetState.FALLING, PetState.THROWN, PetState.BOUNCING]:
                        self.change_state(PetState.IDLE)
            else:
                self.on_ground = False
                if self.state not in [PetState.DRAGGING, PetState.FALLING, PetState.THROWN, PetState.BOUNCING]:
                    self.change_state(PetState.FALLING)
    
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
            elif self.state in [PetState.FALLING, PetState.THROWN]:
                frame_sprites = ["shime4.png", "shime4.png"]
            elif self.state in [PetState.GRAB_WALL, PetState.CLIMB_WALL]:
                frame_sprites = ["shime13.png", "shime13a.png"]  # Wall grab sprites
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
    
    def _update_state_behavior(self, dt: float) -> None:
        """Enhanced state behavior management with wall climbing"""
        if self.state == PetState.IDLE:
            if self.state_timer > 3.0:
                self._decide_next_action()
        
        elif self.state in [PetState.WALKING, PetState.RUNNING]:
            distance_to_target = abs(self.x - self.target_x)
            animation_completed = True
            
            if self.animation_manager:
                try:
                    animation_completed = self.animation_manager.is_animation_completed()
                except:
                    animation_completed = True
            
            # Check if walk duration has expired (1-5 seconds)
            walk_time_elapsed = self.state_timer - self.walk_start_time
            if walk_time_elapsed >= self.walk_duration:
                self.velocity_x = 0
                self.change_state(PetState.IDLE)
                self.stats.walks_taken += 1
                print(f"Pet {self.pet_id} finished walking after {walk_time_elapsed:.1f}s")
                return
            
            # Reduce speed as we approach target
            if distance_to_target < 50:
                self.velocity_x *= 0.9
            
            if distance_to_target < 10 or animation_completed:
                self.velocity_x = 0
                self.change_state(PetState.IDLE)
                self.stats.walks_taken += 1
        
        elif self.state == PetState.SITTING:
            # Sitting behavior - gradually restore energy
            self.stats.energy = min(100, self.stats.energy + 10 * dt)
            if self.state_timer > 5.0:  # Sit for 5 seconds
                self.change_state(PetState.IDLE)
        
        elif self.state == PetState.GRAB_WALL:
            # Wall grabbing - wait before climbing
            if self.state_timer > 1.0:  # Grab for 1 second
                if self.config.get('boundaries.wall_climbing_enabled', True):
                    self.change_state(PetState.CLIMB_WALL)
                    print(f"Pet {self.pet_id} started climbing wall")
                else:
                    # Fall off wall if climbing disabled
                    self.on_wall = False
                    self.wall_side = None
                    self.gravity_enabled = True
                    self.change_state(PetState.FALLING)
        
        elif self.state == PetState.CLIMB_WALL:
            # Enhanced wall climbing behavior with proper animation
            if self.on_wall and self.boundary_manager:
                # Climb up slowly using animation velocity
                climb_speed = 25  # pixels per second (reduced for smoother animation)
                self.y -= climb_speed * dt
                
                # Update animation facing direction for wall climbing
                if self.animation_manager:
                    try:
                        # For wall climbing, face away from the wall
                        if self.wall_side == 'left':
                            self.facing_right = True  # Face right when climbing left wall
                        else:
                            self.facing_right = False  # Face left when climbing right wall
                        
                        # Animation manager's set_facing_direction expects the visual direction
                        self.animation_manager.set_facing_direction(self.facing_right)
                    except Exception as e:
                        print(f"Error updating wall climbing animation: {e}")
                
                # Check if reached top or should stop climbing
                boundaries = self.boundary_manager.boundaries
                if self.y <= boundaries['ceiling_y'] + 80:  # Near ceiling (increased threshold)
                    # Transition to ceiling grab or fall
                    self.on_wall = False
                    self.wall_side = None
                    self.gravity_enabled = True
                    self.change_state(PetState.FALLING)
                    print(f"Pet {self.pet_id} reached ceiling, falling")
                elif self.state_timer > 10.0:  # Climb for max 10 seconds (increased)
                    # Get tired and fall
                    self.on_wall = False
                    self.wall_side = None
                    self.gravity_enabled = True
                    self.velocity_y = 0  # Start falling gently
                    self.change_state(PetState.FALLING)
                    print(f"Pet {self.pet_id} got tired, falling from wall")
            else:
                # Lost wall contact
                self.on_wall = False
                self.wall_side = None
                self.gravity_enabled = True
                self.change_state(PetState.FALLING)
                print(f"Pet {self.pet_id} lost wall contact, falling")
        
        elif self.state in [PetState.POSE, PetState.EAT_BERRY, PetState.THROW_NEEDLE, PetState.WATCH]:
            # Special actions - wait for animation to complete
            animation_completed = True
            if self.animation_manager:
                try:
                    animation_completed = self.animation_manager.is_animation_completed()
                except:
                    animation_completed = True
            
            if animation_completed or self.state_timer > 3.0:
                self.change_state(PetState.IDLE)
                if self.state != PetState.WATCH:
                    self.stats.special_actions_performed += 1
        
        elif self.state in [PetState.FALLING, PetState.THROWN]:
            # While falling/thrown, ensure gravity is active
            self.gravity_enabled = True
        
        elif self.state == PetState.BOUNCING:
            # Bounce state is brief
            if self.on_ground and abs(self.velocity_y) < self.MIN_BOUNCE_VELOCITY:
                self.change_state(PetState.IDLE)
            self.gravity_enabled = True

        elif self.state == PetState.DRAGGING:
            # While dragging, disable gravity and wall climbing
            self.gravity_enabled = False
            self.on_wall = False
            self.wall_side = None
    
    def _update_behavioral_ai(self, dt: float) -> None:
        """Enhanced AI dengan wall climbing consideration"""
        # Only make decisions when idle and on ground (or on wall)
        if self.state != PetState.IDLE or (not self.on_ground and not self.on_wall):
            return
        
        # Random behavior selection
        if self.behavior_timer > 2.0:
            self.behavior_timer = 0.0
            
            # Calculate behavior probabilities
            energy_factor = self.stats.energy / 100.0
            happiness_factor = self.stats.happiness / 100.0
            activity_chance = (energy_factor + happiness_factor) / 2.0
            
            # Special wall climbing behavior
            if self.on_wall and random.random() < 0.3:
                # Continue climbing or fall off
                if random.random() < 0.7:
                    self.change_state(PetState.CLIMB_WALL)
                else:
                    self.on_wall = False
                    self.wall_side = None
                    self.gravity_enabled = True
                    self.change_state(PetState.FALLING)
                return
            
            if random.random() < activity_chance * 0.3:
                self._decide_next_action()
    
    def _decide_next_action(self) -> None:
        """Enhanced action decision dengan wall climbing options"""
        possible_actions = []
        
        # Basic movement actions
        if self.stats.energy > 30:
            possible_actions.extend([
                (PetState.WALKING, 40),
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
        
        # Wall climbing actions (if near boundary walls)
        if self.boundary_manager and self.config.get('boundaries.wall_climbing_enabled', True):
            boundaries = self.boundary_manager.boundaries
            near_left_wall = abs(self.x - boundaries['left_wall_x']) < 50
            near_right_wall = abs(self.x - boundaries['right_wall_x']) < 50
            
            if near_left_wall or near_right_wall:
                possible_actions.extend([
                    (PetState.GRAB_WALL, 25),  # Higher chance near walls
                ])
        
        # Random special actions
        if random.random() < 0.1:
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
                    elif action == PetState.GRAB_WALL:
                        self._start_wall_climbing()
                    else:
                        self.change_state(action)
                    break
    
    def _start_movement(self, movement_type: PetState) -> None:
        """Start movement dengan target random dan wall-aware direction selection"""
        # Set random walk duration between 1-5 seconds
        self.walk_duration = random.uniform(1.0, 5.0)
        self.walk_start_time = self.state_timer
        
        if self.boundary_manager:
            # Use boundary-aware movement with wall proximity detection
            playable = self.boundary_manager.get_playable_area()
            boundaries = self.boundary_manager.boundaries
            max_distance = 300 if movement_type == PetState.RUNNING else 150
            
            # Check proximity to walls for direction bias
            left_distance = abs(self.x - boundaries['left_wall_x'])
            right_distance = abs(self.x - boundaries['right_wall_x'])
            wall_proximity_threshold = 100  # Distance to consider "near wall"
            
            # Determine direction with wall bias
            if left_distance < wall_proximity_threshold:
                # Near left wall - bias towards right (2x probability)
                direction = 1 if random.random() < 0.67 else -1
                print(f"Pet {self.pet_id} near left wall, biased towards right")
            elif right_distance < wall_proximity_threshold:
                # Near right wall - bias towards left (2x probability)
                direction = -1 if random.random() < 0.67 else 1
                print(f"Pet {self.pet_id} near right wall, biased towards left")
            else:
                # Not near walls - random direction
                direction = random.choice([-1, 1])
            
            distance = random.randint(50, max_distance)
            self.target_x = self.x + (distance * direction)
            # Clamp to playable area
            self.target_x = max(playable['left'], min(playable['right'] - self.rect.width, self.target_x))
        else:
            # Fallback movement (no wall detection)
            max_distance = 300 if movement_type == PetState.RUNNING else 150
            direction = random.choice([-1, 1])
            distance = random.randint(50, max_distance)
            self.target_x = self.x + (distance * direction)
            self.target_x = max(0.0, min(1920.0, self.target_x))
        
        # Determine facing direction based on target
        self.facing_right = self.target_x > self.x
        
        # Update animation facing direction (invert for visual correction)
        if self.animation_manager:
            try:
                self.animation_manager.set_facing_direction(not self.facing_right)
            except:
                pass
        
        # Debug: Log the actual direction and target
        direction_text = "right" if self.facing_right else "left"
        print(f"Pet {self.pet_id} starting {movement_type.value} for {self.walk_duration:.1f}s towards {direction_text} (target_x: {self.target_x:.1f}, current_x: {self.x:.1f})")
        self.change_state(movement_type)
    
    def _start_wall_climbing(self) -> None:
        """Start wall climbing behavior"""
        if not self.boundary_manager:
            return
        
        boundaries = self.boundary_manager.boundaries
        
        # Determine which wall to climb
        left_distance = abs(self.x - boundaries['left_wall_x'])
        right_distance = abs(self.x - boundaries['right_wall_x'])
        
        if left_distance < right_distance:
            # Move to left wall
            self.target_x = boundaries['left_wall_x']
            self.wall_side = 'left'
            self.facing_right = False
        else:
            # Move to right wall
            self.target_x = boundaries['right_wall_x'] - self.rect.width
            self.wall_side = 'right'
            self.facing_right = True
        
        # Update animation facing direction (invert for visual correction)
        if self.animation_manager:
            try:
                self.animation_manager.set_facing_direction(not self.facing_right)
            except:
                pass
        
        # Start walking to wall
        self.change_state(PetState.WALKING)
    
    def _change_direction(self) -> None:
        """Enhanced direction change with cooldown to prevent glitches"""
        current_time = time.time()
        
        # Check if enough time has passed since last direction change
        if current_time - self.last_direction_change < self.direction_change_cooldown:
            return  # Skip direction change if too soon
        
        # Check if direction is locked
        if self.direction_lock_timer < self.direction_lock_duration:
            return  # Skip direction change if still locked
        
        # Change direction
        self.facing_right = not self.facing_right
        self.last_direction_change = current_time
        
        # Update animation facing direction
        if self.animation_manager:
            try:
                self.animation_manager.set_facing_direction(not self.facing_right)  
            except Exception as e:
                print(f"Error updating animation direction: {e}")
        
        print(f"Pet {self.pet_id} changed direction to {'right' if self.facing_right else 'left'}")
    
    def _lock_direction(self, duration: float = None) -> None:
        """Lock direction changes for a specified duration"""
        if duration is None:
            duration = self.direction_lock_duration
        self.direction_lock_timer = 0.0  # Reset timer
        self.direction_lock_duration = duration
    
    def _update_stats(self, dt: float) -> None:
        """Enhanced stats management"""
        # Gradually decrease happiness and energy over time
        self.stats.happiness = max(0, self.stats.happiness - 0.5 * dt)
        self.stats.energy = max(0, self.stats.energy - 0.3 * dt)
        
        # Restore energy when sitting, idle, or wall climbing
        if self.state in [PetState.SITTING, PetState.IDLE, PetState.GRAB_WALL]:
            self.stats.energy = min(100, self.stats.energy + 0.5 * dt)
        
        # Wall climbing uses energy
        if self.state == PetState.CLIMB_WALL:
            self.stats.energy = max(0, self.stats.energy - 1.0 * dt)
        
        # Restore happiness with interactions
        time_since_interaction = time.time() - self.stats.last_interaction
        if time_since_interaction < 10:
            self.stats.happiness = min(100, self.stats.happiness + 1 * dt)
    
    def change_state(self, new_state: PetState) -> None:
        """Enhanced state changing dengan wall climbing integration"""
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
                                                 PetState.GRAB_WALL, PetState.GRAB_CEILING,
                                                 PetState.CLIMB_WALL, PetState.BOUNCING]
                    self.animation_manager.play_action(new_state.value, loop=loop_animation)
                except Exception as e:
                    print(f"Error starting animation for {new_state.value}: {e}")
            
            # State-specific initialization
            if new_state == PetState.SITTING:
                self.velocity_x = 0
                self.velocity_y = 0
                self.gravity_enabled = False
                self.on_ground = True
                self.on_wall = False
            elif new_state in [PetState.FALLING, PetState.THROWN]:
                self.on_ground = False
                self.on_wall = False
                self.gravity_enabled = True
            elif new_state == PetState.DRAGGING:
                self.velocity_x = 0
                self.velocity_y = 0
                self.gravity_enabled = False
                self.on_ground = False
                self.on_wall = False
            elif new_state == PetState.BOUNCING:
                self.on_ground = False
                self.on_wall = False
                self.gravity_enabled = True
            elif new_state == PetState.IDLE:
                self.velocity_x = 0
                self.velocity_y = 0
                if not self.on_wall:
                    self.on_ground = True
                    self.gravity_enabled = True
            elif new_state in [PetState.GRAB_WALL, PetState.CLIMB_WALL]:
                # Enhanced wall climbing states with proper animation
                self.on_ground = False
                self.gravity_enabled = False
                self.velocity_x = 0
                self.velocity_y = 0
                
                # Lock direction changes during wall climbing to prevent glitches
                self._lock_direction(2.0)  # Lock for 2 seconds during wall climbing
                
                # Set proper facing direction for wall climbing
                if self.wall_side == 'left':
                    self.facing_right = False  # Face left (toward left wall)
                elif self.wall_side == 'right':
                    self.facing_right = True  # Face right (toward right wall)
                
                # Update animation facing direction (animation manager uses opposite logic)
                if self.animation_manager:
                    try:
                        # For wall climbing, we want the sprite to face away from the wall
                        # Animation manager's set_facing_direction expects the visual direction
                        self.animation_manager.set_facing_direction(self.facing_right)
                        print(f"Pet {self.pet_id} wall climbing animation direction set to {'right' if self.facing_right else 'left'}")
                    except Exception as e:
                        print(f"Error setting wall climbing animation direction: {e}")
                
                print(f"Pet {self.pet_id} entered {new_state.value} state with direction lock")
            elif new_state in [PetState.WALKING, PetState.RUNNING]:
                # Initialize walk duration tracking
                if not hasattr(self, 'walk_duration') or self.walk_duration == 0.0:
                    self.walk_duration = random.uniform(1.0, 5.0)
                    self.walk_start_time = self.state_timer
    
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
                self.stop()  # Mark pet as not running
                return "kill"
            else:
                self.last_click_time = current_time
                # Single right-click actions
                if self.state != PetState.SITTING:
                    self.change_state(PetState.SITTING)
                else:
                    # Cycle through special actions
                    special_actions = [PetState.POSE, PetState.EAT_BERRY, PetState.WATCH, PetState.THROW_NEEDLE]
                    if self.boundary_manager and self.config.get('boundaries.wall_climbing_enabled', True):
                        special_actions.append(PetState.GRAB_WALL)
                    
                    chosen_action = random.choice(special_actions)
                    self.change_state(chosen_action)
                return "sit"
        
        return "none"
    
    def handle_mouse_up(self, button: int, mouse_dx: float = 0.0, mouse_dy: float = 0.0) -> str:
        """Enhanced mouse up handling with wall sticking release"""
        if button == 1 and self.dragging:
            self.dragging = False
            
            # Release wall sticking state
            if self.on_wall:
                self.on_wall = False
                self.wall_side = None
                self.gravity_enabled = True
                print(f"Pet {self.pet_id} released from wall")
            
            # Apply throw velocity
            self.velocity_x = mouse_dx * self.DRAG_THROW_MULTIPLIER
            self.velocity_y = mouse_dy * self.DRAG_THROW_MULTIPLIER
            
            self.change_state(PetState.THROWN)
            self.on_ground = False
            self.gravity_enabled = True
            
            return "drag_end"
        
        return "none"
    
    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Enhanced mouse motion handling with wall collision prevention"""
        if self.dragging:
            new_x = float(pos[0] - self.drag_offset_x)
            new_y = float(pos[1] - self.drag_offset_y)
            
            # Check if new position would cross wall boundaries
            if self.boundary_manager:
                boundaries = self.boundary_manager.boundaries
                
                # Prevent crossing left wall
                if new_x < boundaries['left_wall_x']:
                    new_x = boundaries['left_wall_x']
                    # Trigger wall sticking
                    if not self.on_wall:
                        self._handle_drag_wall_collision('left')
                
                # Prevent crossing right wall
                elif new_x + self.rect.width > boundaries['right_wall_x']:
                    new_x = boundaries['right_wall_x'] - self.rect.width
                    # Trigger wall sticking
                    if not self.on_wall:
                        self._handle_drag_wall_collision('right')
                
                # Prevent crossing ground
                if new_y + self.rect.height > boundaries['ground_y']:
                    new_y = boundaries['ground_y'] - self.rect.height
                
                # Prevent crossing ceiling
                if new_y < boundaries['ceiling_y']:
                    new_y = boundaries['ceiling_y']
            
            # Update position
            self.x = new_x
            self.y = new_y
            
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
        """Enhanced state information dengan boundary info"""
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
            'on_wall': self.on_wall,
            'wall_side': self.wall_side,
            'dragging': self.dragging,
            'boundary_manager_connected': self.boundary_manager is not None,
            'stats': {
                'health': self.stats.health,
                'happiness': self.stats.happiness,
                'energy': self.stats.energy,
                'interactions': self.stats.total_interactions,
                'walks_taken': self.stats.walks_taken,
                'times_petted': self.stats.times_petted,
                'special_actions': self.stats.special_actions_performed,
                'wall_climbs': self.stats.wall_climbs,
                'time_in_state': self.stats.time_in_current_state
            },
            'animation': animation_info,
            'animation_system': self.animation_manager is not None
        }
    
    def save_state(self) -> Dict[str, Any]:
        """Enhanced state persistence dengan boundary info"""
        return {
            'pet_id': self.pet_id,
            'sprite_name': self.sprite_name,
            'x': self.x,
            'y': self.y,
            'target_x': self.target_x,
            'target_y': self.target_y,
            'state': self.state.value,
            'facing_right': self.facing_right,
            'velocity_x': self.velocity_x,
            'velocity_y': self.velocity_y,
            'on_ground': self.on_ground,
            'on_wall': self.on_wall,
            'wall_side': self.wall_side,
            'gravity_enabled': self.gravity_enabled,
            'running': self.running,
            'stats': {
                'health': self.stats.health,
                'happiness': self.stats.happiness,
                'energy': self.stats.energy,
                'total_interactions': self.stats.total_interactions,
                'walks_taken': self.stats.walks_taken,
                'times_petted': self.stats.times_petted,
                'special_actions_performed': self.stats.special_actions_performed,
                            'wall_climbs': self.stats.wall_climbs
            }
        }
    
    @classmethod
    def load_from_state(cls, state_data: Dict[str, Any]) -> 'DesktopPet':
        """Load pet dari saved state dengan boundary support"""
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
        pet.velocity_x = state_data.get('velocity_x', 0.0)
        pet.velocity_y = state_data.get('velocity_y', 0.0)
        pet.on_ground = state_data.get('on_ground', True)
        pet.on_wall = state_data.get('on_wall', False)
        pet.wall_side = state_data.get('wall_side', None)
        pet.gravity_enabled = state_data.get('gravity_enabled', True)
        
        # Restore state
        try:
            pet.change_state(PetState(state_data['state']))
        except ValueError:
            pet.change_state(PetState.IDLE)
        
        # Restore running status
        pet.running = state_data.get('running', True)
        
        # Restore stats
        stats_data = state_data.get('stats', {})
        pet.stats.health = stats_data.get('health', 100)
        pet.stats.happiness = stats_data.get('happiness', 100)
        pet.stats.energy = stats_data.get('energy', 100)
        pet.stats.total_interactions = stats_data.get('total_interactions', 0)
        pet.stats.walks_taken = stats_data.get('walks_taken', 0)
        pet.stats.times_petted = stats_data.get('times_petted', 0)
        pet.stats.special_actions_performed = stats_data.get('special_actions_performed', 0)
        pet.stats.wall_climbs = stats_data.get('wall_climbs', 0)
        
        # Update animation facing direction (invert for visual correction)
        if pet.animation_manager:
            try:
                pet.animation_manager.set_facing_direction(not pet.facing_right)
            except:
                pass
        
        return pet
    
    def draw(self, screen: pygame.Surface) -> None:
        """Enhanced drawing dengan boundary-aware debug info"""
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback drawing
            pygame.draw.rect(screen, (255, 100, 100), self.rect)
        
        # Debug information
        if self.config.get('settings.debug_mode', False):
            self._draw_debug_info(screen)
        
        # Stats overlay (only when debug mode is active)
        if self.config.get('settings.debug_mode', False) and self.config.get('settings.show_stats', False):
            self._draw_stats_overlay(screen)
    
    def _draw_debug_info(self, screen: pygame.Surface) -> None:
        """Enhanced debug information dengan boundary info"""
        # Draw bounding box
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
        
        # Draw velocity vector
        scale_factor = 0.1 
        start_pos = (self.rect.centerx, self.rect.centery)
        end_pos = (
            int(start_pos[0] + self.velocity_x * scale_factor),
            int(start_pos[1] + self.velocity_y * scale_factor)
        )
        pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)
        
        # Draw target position
        if abs(self.target_x - self.x) > 5 or abs(self.target_y - self.y) > 5:
            target_rect = pygame.Rect(int(self.target_x), int(self.target_y), 5, 5)
            pygame.draw.rect(screen, (0, 0, 255), target_rect)
        
        # Draw state text
        font = pygame.font.Font(None, 20)
        state_text = font.render(f"{self.state.value}", True, (255, 255, 255))
        screen.blit(state_text, (self.rect.x, self.rect.y - 25))
        
        # Draw wall climbing indicator
        if self.on_wall:
            wall_color = (255, 255, 0)  # Yellow for wall climbing
            wall_indicator = font.render(f"WALL-{self.wall_side.upper()}", True, wall_color)
            screen.blit(wall_indicator, (self.rect.x, self.rect.y - 50))
        
        # Draw facing direction indicator (consisten dengan visual direction)
        # Arrow harus menunjukkan arah visual yang sebenarnya dari sprite
        visual_facing_right = self.facing_right
        
        # Untuk wall climbing, sprite menghadap ke dinding (bukan menjauh dari dinding)
        if self.on_wall and self.wall_side:
            if self.wall_side == 'left':
                visual_facing_right = False  # Sprite menghadap kiri (ke dinding kiri)
            elif self.wall_side == 'right':
                visual_facing_right = True  # Sprite menghadap kanan (ke dinding kanan)
        
        if visual_facing_right:
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
        
        # Display velocity values
        velocity_text = font.render(f"Vel: ({self.velocity_x:.0f}, {self.velocity_y:.0f})", True, (255, 255, 255))
        screen.blit(velocity_text, (self.rect.x, self.rect.y - 75))
        
        # Display boundary status
        status_indicators = []
        if self.on_ground:
            status_indicators.append("GND")
        if self.on_wall:
            status_indicators.append(f"WALL-{self.wall_side.upper()}")
        if self.gravity_enabled:
            status_indicators.append("GRAV")
        
        if status_indicators:
            status_text = font.render(" | ".join(status_indicators), True, (0, 255, 255))
            screen.blit(status_text, (self.rect.x, self.rect.y - 100))

    def _draw_stats_overlay(self, screen: pygame.Surface) -> None:
        """Enhanced stats overlay dengan boundary stats"""
        font = pygame.font.Font(None, 16)
        y_offset = 0
        
        stats_info = [
            f"Health: {self.stats.health:.0f}",
            f"Happy: {self.stats.happiness:.0f}",
            f"Energy: {self.stats.energy:.0f}",
            f"State: {self.state.value}",
            f"Climbs: {self.stats.wall_climbs}",
        ]
        
        for stat_text in stats_info:
            text_surface = font.render(stat_text, True, (255, 255, 255))
            # Draw background
            bg_rect = text_surface.get_rect()
            bg_rect.x = self.rect.x - 60
            bg_rect.y = self.rect.y + y_offset
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            # Draw text
            screen.blit(text_surface, (self.rect.x - 60, self.rect.y + y_offset))
            y_offset += 18
    
    def get_available_actions(self) -> List[str]:
        """Get list semua action yang tersedia"""
        if self.animation_manager:
            try:
                return self.animation_manager.get_available_actions()
            except:
                pass
        return ["Stand", "Walk", "Sit", "Run", "GrabWall", "ClimbWall"]  # Enhanced fallback actions
    
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
            'boundary_system_connected': self.boundary_manager is not None,
            'current_animation': animation_info,
            'wall_climbing_stats': {
                'on_wall': self.on_wall,
                'wall_side': self.wall_side,
                'total_climbs': self.stats.wall_climbs
            },
            'update_frequency': '30 FPS target',
            'memory_footprint': 'Light (sprites cached)'
        }
    
    def stop(self) -> None:
        """Stop the pet (mark as not running)"""
        self.running = False
        print(f"Pet {self.pet_id} stopped")
    
    def cleanup(self) -> None:
        """Enhanced cleanup"""
        print(f"Cleaning up enhanced pet: {self.pet_id}")
        
        # Mark as not running
        self.running = False
        
        # Stop any running animations
        if self.animation_manager:
            try:
                self.animation_manager.stop_current_animation()
            except:
                pass
        
        # Clear boundary manager reference
        self.boundary_manager = None
        
        # Clear references
        self.animation_manager = None
        self.current_sprite = None