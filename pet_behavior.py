#!/usr/bin/env python3
"""
pet_behavior.py - Enhanced pet behavior dengan Pinch Animation & Random Behavior

Menambahkan:
1. Pinch animation yang smooth berdasarkan mouse position
2. Random behavior berdasarkan XML frequency 
3. Multi-monitor support
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
    IDLE = "Stand"
    WALKING = "Walk"
    SITTING = "Sit"
    RUNNING = "Run"
    
    # Special states
    DRAGGING = "Pinched"
    FALLING = "Falling"
    JUMPING = "Jumping"
    THROWN = "Thrown"
    BOUNCING = "Bouncing"
    
    # Wall/ceiling interactions  
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


class DesktopPet:
    """Enhanced desktop pet dengan Pinch Animation, Random Behavior, dan Multi-Monitor"""
    
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
        
        # Multi-monitor support
        self.monitors = []
        self.current_monitor = None
        
        # State management
        self.state = PetState.IDLE
        self.previous_state = PetState.IDLE
        self.state_timer = 0.0
        self.state_duration = 0.0
        
        # Animation system
        self.animation_manager = None
        if ANIMATION_SYSTEM_AVAILABLE and create_animation_manager:
            try:
                self.animation_manager = create_animation_manager(sprite_name)
                if self.animation_manager:
                    print(f"✅ Animation system loaded for {sprite_name}")
                else:
                    print(f"⚠️ Failed to create animation manager for {sprite_name}")
            except Exception as e:
                print(f"Error creating animation manager: {e}")
                self.animation_manager = None
        
        # Pinch animation system
        self.pinch_sprites = self._load_pinch_sprites()
        self.pinch_animation_active = False
        self.mouse_relative_x = 0.0  # Mouse position relative to pet center
        
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
        
        # Configuration and Physics
        self.config = get_config()
        self.update_physics_parameters()
        
        # Random behavior system
        self.behavior_timer = 0.0
        self.idle_timer = 0.0
        self.action_queue = []
        self.behavior_weights = self._load_behavior_weights()
        self.next_behavior_time = random.uniform(2.0, 8.0)  # Random initial delay
        
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
        
        print(f"🐾 Enhanced pet created: {self.pet_id} at ({x}, {y}) with pinch & random behavior")

    def _load_pinch_sprites(self) -> Dict[str, str]:
        """Load pinch animation sprite mappings"""
        return {
            'far_left': 'shime9.png',      # Mouse far to left of pet
            'left': 'shime7.png',          # Mouse to left of pet  
            'near_left': 'shime5.png',     # Mouse near left of pet
            'center': 'shime5a.png',       # Mouse at center of pet
            'near_right': 'shime6.png',    # Mouse near right of pet
            'right': 'shime8.png',         # Mouse to right of pet
            'far_right': 'shime10.png'     # Mouse far to right of pet
        }
    
    def _load_behavior_weights(self) -> Dict[str, int]:
        """Load behavior weights dari XML atau fallback defaults"""
        behavior_weights = {
            # Basic behaviors (high frequency)
            'WALKING': 200,
            'RUNNING': 100,
            'SITTING': 200,
            
            # Special behaviors (lower frequency)
            'POSE': 30,
            'EAT_BERRY': 45,
            'THROW_NEEDLE': 30,
            'WATCH': 45,
            
            # Rest behavior
            'IDLE': 150
        }
        
        # Try to load from XML if available
        try:
            from utils.xml_parser import XMLParser
            xml_parser = XMLParser()
            if xml_parser.parse_sprite_pack(self.sprite_name):
                behaviors = xml_parser.get_all_behaviors()
                
                # Update weights berdasarkan XML frequency
                for behavior_name, behavior_data in behaviors.items():
                    if not behavior_data.hidden and behavior_data.frequency > 0:
                        # Map XML behavior names ke PetState names
                        state_name = self._map_behavior_to_state(behavior_name)
                        if state_name and hasattr(PetState, state_name):
                            behavior_weights[state_name] = behavior_data.frequency
                
                print(f"✅ Loaded {len(behaviors)} behavior weights from XML")
        except Exception as e:
            print(f"⚠️ Using fallback behavior weights: {e}")
        
        return behavior_weights
    
    def _map_behavior_to_state(self, behavior_name: str) -> Optional[str]:
        """Map XML behavior names ke PetState enum names"""
        behavior_mapping = {
            'StandUp': 'IDLE',
            'SitDown': 'SITTING', 
            'WalkAlongWorkAreaFloor': 'WALKING',
            'RunAlongWorkAreaFloor': 'RUNNING',
            'Pose': 'POSE',
            'EatBerry': 'EAT_BERRY',
            'ThrowNeedle': 'THROW_NEEDLE',
            'WatchShows (CanEnd)': 'WATCH'
        }
        return behavior_mapping.get(behavior_name)
    
    def set_monitor_bounds(self, monitors: List[Dict[str, int]]) -> None:
        """Set multi-monitor boundaries"""
        self.monitors = monitors
        self.current_monitor = self._get_current_monitor()
        print(f"Pet {self.pet_id} set to monitor bounds: {len(monitors)} monitors")
    
    def _get_current_monitor(self) -> Dict[str, int]:
        """Get current monitor based on pet position"""
        if not self.monitors:
            return {'left': 0, 'top': 0, 'width': 1920, 'height': 1080, 'right': 1920, 'bottom': 1080}
        
        # Find which monitor contains the pet
        for monitor in self.monitors:
            if (monitor['left'] <= self.x < monitor['right'] and 
                monitor['top'] <= self.y < monitor['bottom']):
                return monitor
        
        # Default to first monitor if not found
        return self.monitors[0]

    def update_physics_parameters(self) -> None:
        """Updates physics parameters from the global config."""
        self.GRAVITY_ACCELERATION = self.config.get('settings.physics_gravity_acceleration')
        self.AIR_RESISTANCE_FACTOR = self.config.get('settings.physics_air_resistance_factor')
        self.BOUNCE_COEFFICIENT = self.config.get('settings.physics_bounce_coefficient')
        self.MIN_BOUNCE_VELOCITY = self.config.get('settings.physics_min_bounce_velocity')
        self.DRAG_THROW_MULTIPLIER = self.config.get('settings.physics_drag_throw_multiplier')
        print(f"Pet {self.pet_id} physics parameters updated.")
    
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
                    self.animation_manager.set_facing_direction(self.facing_right)
                    available_actions = self.animation_manager.get_available_actions()
                    print(f"Available animations for {self.sprite_name}: {len(available_actions)} actions")
                else:
                    print(f"Warning: Could not start initial animation for {self.sprite_name}")
            except Exception as e:
                print(f"Error initializing animation: {e}")
                self.animation_manager = None
    
    def update(self, dt: float, monitors: List[Dict[str, int]]) -> None:
        """Enhanced update dengan pinch animation, random behavior, dan multi-monitor"""
        # Update monitor info
        self.monitors = monitors
        self.current_monitor = self._get_current_monitor()
        
        # Update timers
        self.state_timer += dt
        self.behavior_timer += dt
        self.stats.time_in_current_state += dt
        
        # Update animation system dengan pinch support
        if self.animation_manager:
            try:
                if self.state == PetState.DRAGGING and self.pinch_animation_active:
                    # Use pinch animation
                    self.current_sprite = self._get_pinch_sprite()
                else:
                    # Use normal animation
                    self.current_sprite, anim_velocity = self.animation_manager.update(dt)
                    
                    # Apply animation velocity for walking/running
                    if not self.dragging and self.state in [PetState.WALKING, PetState.RUNNING]:
                        vel_x = anim_velocity[0] if self.facing_right else -anim_velocity[0]
                        self.velocity_x = vel_x
                        self.velocity_y = anim_velocity[1]
                
                if self.current_sprite:
                    self.image = self.current_sprite
            except Exception as e:
                print(f"Error updating animation: {e}")
                self._update_fallback_animation(dt)
        else:
            self._update_fallback_animation(dt)
        
        # Update position based on velocity
        if not self.dragging:
            self._update_movement_multimonitor(dt)
        
        # Update state-specific behavior
        self._update_state_behavior(dt)
        
        # Update random behavioral AI
        self._update_random_behavior_ai(dt)
        
        # Update statistics  
        self._update_stats(dt)
        
        # Update sprite rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _get_pinch_sprite(self) -> pygame.Surface:
        """Get appropriate pinch sprite berdasarkan mouse position dengan debug info"""
        try:
            # Determine which pinch sprite to use based on mouse_relative_x
            sprite_key = ""
            if self.mouse_relative_x < -50:
                sprite_key = 'far_left'
                sprite_name = self.pinch_sprites['far_left']
            elif self.mouse_relative_x < -30:
                sprite_key = 'left'
                sprite_name = self.pinch_sprites['left']
            elif self.mouse_relative_x < -15:
                sprite_key = 'near_left'
                sprite_name = self.pinch_sprites['near_left']
            elif self.mouse_relative_x < 15:
                sprite_key = 'center'
                sprite_name = self.pinch_sprites['center']
            elif self.mouse_relative_x < 30:
                sprite_key = 'near_right'
                sprite_name = self.pinch_sprites['near_right']
            elif self.mouse_relative_x < 50:
                sprite_key = 'right'
                sprite_name = self.pinch_sprites['right']
            else:
                sprite_key = 'far_right'
                sprite_name = self.pinch_sprites['far_right']
            
            # Debug: print pinch changes
            if hasattr(self, '_last_pinch_key') and self._last_pinch_key != sprite_key:
                print(f"🤏 Pinch changed: {sprite_key} (offset: {self.mouse_relative_x:.0f})")
            self._last_pinch_key = sprite_key
            
            # Load and return sprite
            sprite = self.sprite_loader.load_sprite(self.sprite_name, sprite_name)
            
            # Flip sprite if facing left
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            
            return sprite
            
        except Exception as e:
            print(f"Error loading pinch sprite {sprite_key}: {e}")
            # Fallback to center pinch sprite
            try:
                fallback_sprite = self.sprite_loader.load_sprite(self.sprite_name, self.pinch_sprites['center'])
                if not self.facing_right:
                    fallback_sprite = pygame.transform.flip(fallback_sprite, True, False)
                return fallback_sprite
            except:
                # Ultimate fallback to current loaded sprite
                return self._load_current_sprite()
    
    def _update_fallback_animation(self, dt: float) -> None:
        """Enhanced fallback animation dengan pinch support dan falling fix"""
        self.animation_timer += dt
        
        # Handle pinch animation in fallback mode
        if self.state == PetState.DRAGGING and self.pinch_animation_active:
            self.current_sprite = self._get_pinch_sprite()
            if self.current_sprite:
                self.image = self.current_sprite
            return
        
        # Normal fallback animation dengan timing yang tepat
        animation_speed = 0.3 if self.state in [PetState.FALLING, PetState.THROWN] else 0.5
        
        if self.animation_timer > animation_speed:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0.0
            
            # Load different sprite based on state dengan falling fix
            if self.state == PetState.WALKING:
                frame_sprites = ["shime2.png", "shime3.png"]
            elif self.state == PetState.SITTING:
                frame_sprites = ["shime11.png", "shime11a.png"]
            elif self.state == PetState.RUNNING:
                frame_sprites = ["shime3e.png", "shime3f.png"]
            elif self.state == PetState.FALLING:
                # Proper falling animation
                frame_sprites = ["shime4.png", "shime4.png"]  # Consistent falling pose
            elif self.state == PetState.THROWN:
                # Thrown animation (spinning effect)
                frame_sprites = ["shime4.png", "shime22.png"] if self.animation_frame == 0 else ["shime22.png", "shime4.png"]
            elif self.state == PetState.BOUNCING:
                # Bouncing animation
                frame_sprites = ["shime18.png", "shime19.png"]
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
    
    def _update_movement_multimonitor(self, dt: float) -> None:
        """Enhanced movement dengan multi-monitor support"""
        # Apply gravity if enabled and not on ground
        if self.gravity_enabled and not self.on_ground:
            self.velocity_y += self.GRAVITY_ACCELERATION * dt
            
            # Apply air resistance
            self.velocity_x *= (1 - self.AIR_RESISTANCE_FACTOR * dt)
            self.velocity_y *= (1 - self.AIR_RESISTANCE_FACTOR * dt)
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Multi-monitor boundary collision
        if self.config.get('settings.screen_boundaries', True):
            monitor = self.current_monitor or self.monitors[0] if self.monitors else {
                'left': 0, 'top': 0, 'right': 1920, 'bottom': 1080
            }
            
            # Horizontal boundaries
            if self.x < monitor['left']:
                self.x = monitor['left']
                self.velocity_x *= -self.BOUNCE_COEFFICIENT
                if abs(self.velocity_x) < self.MIN_BOUNCE_VELOCITY: 
                    self.velocity_x = 0
                self._change_direction()
            elif self.x > monitor['right'] - self.rect.width:
                self.x = monitor['right'] - self.rect.width
                self.velocity_x *= -self.BOUNCE_COEFFICIENT
                if abs(self.velocity_x) < self.MIN_BOUNCE_VELOCITY: 
                    self.velocity_x = 0
                self._change_direction()
            
            # Ground collision (Floor)
            ground_y = monitor['bottom'] - self.rect.height - AppConstants.SCREEN_MARGIN
            if self.y >= ground_y:
                self.y = ground_y
                
                # Check for bounce
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
    
    def _update_random_behavior_ai(self, dt: float) -> None:
        """Enhanced random behavior AI dengan XML frequency-based selection"""
        if self.state != PetState.IDLE or not self.on_ground:
            return
        
        # Check if it's time for next behavior
        if self.behavior_timer >= self.next_behavior_time:
            self.behavior_timer = 0.0
            
            # Calculate behavior probabilities based on stats and time
            energy_factor = self.stats.energy / 100.0
            happiness_factor = self.stats.happiness / 100.0
            
            # Adjust behavior weights based on pet stats
            adjusted_weights = {}
            for behavior_name, base_weight in self.behavior_weights.items():
                weight = base_weight
                
                # Energy-based adjustments
                if behavior_name in ['WALKING', 'RUNNING'] and energy_factor < 0.3:
                    weight *= 0.5  # Less likely to walk/run when tired
                elif behavior_name == 'SITTING' and energy_factor < 0.5:
                    weight *= 1.5  # More likely to sit when low energy
                
                # Happiness-based adjustments
                if behavior_name in ['POSE', 'EAT_BERRY', 'WATCH'] and happiness_factor > 0.7:
                    weight *= 1.3  # More likely to do special actions when happy
                
                adjusted_weights[behavior_name] = max(1, int(weight))
            
            # Weighted random selection
            selected_behavior = self._weighted_random_choice(adjusted_weights)
            if selected_behavior:
                self._execute_behavior(selected_behavior)
            
            # Set next behavior time (random interval)
            base_interval = 60.0 / self.config.get('settings.behavior_frequency', 50)  # Convert frequency to interval
            self.next_behavior_time = random.uniform(base_interval * 0.5, base_interval * 2.0)
    
    def _weighted_random_choice(self, weights: Dict[str, int]) -> Optional[str]:
        """Weighted random selection dari behavior weights"""
        if not weights:
            return None
        
        total_weight = sum(weights.values())
        if total_weight <= 0:
            return None
        
        random_value = random.randint(1, total_weight)
        current_weight = 0
        
        for behavior_name, weight in weights.items():
            current_weight += weight
            if random_value <= current_weight:
                return behavior_name
        
        return None
    
    def _execute_behavior(self, behavior_name: str) -> None:
        """Execute selected behavior"""
        try:
            if behavior_name == 'WALKING':
                self._start_movement(PetState.WALKING)
            elif behavior_name == 'RUNNING':
                self._start_movement(PetState.RUNNING)
            elif behavior_name == 'SITTING':
                self.change_state(PetState.SITTING)
            elif behavior_name in ['POSE', 'EAT_BERRY', 'THROW_NEEDLE', 'WATCH']:
                state = getattr(PetState, behavior_name)
                self.change_state(state)
            elif behavior_name == 'IDLE':
                self.change_state(PetState.IDLE)
            
            print(f"🎲 Pet {self.pet_id} executed random behavior: {behavior_name}")
        except Exception as e:
            print(f"Error executing behavior {behavior_name}: {e}")
    
    def _update_state_behavior(self, dt: float) -> None:
        """Enhanced state behavior management"""
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
            
            if distance_to_target < 50:
                self.velocity_x *= 0.9
            
            if distance_to_target < 10 or animation_completed:
                self.velocity_x = 0
                self.change_state(PetState.IDLE)
                self.stats.walks_taken += 1
        
        elif self.state == PetState.SITTING:
            self.stats.energy = min(100, self.stats.energy + 10 * dt)
            if self.state_timer > 5.0:
                self.change_state(PetState.IDLE)
        
        elif self.state in [PetState.POSE, PetState.EAT_BERRY, PetState.THROW_NEEDLE, PetState.WATCH]:
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
        
        elif self.state == PetState.FALLING or self.state == PetState.THROWN:
            self.gravity_enabled = True
        
        elif self.state == PetState.BOUNCING:
            if self.on_ground and abs(self.velocity_y) < self.MIN_BOUNCE_VELOCITY:
                self.change_state(PetState.IDLE)
            self.gravity_enabled = True

        elif self.state == PetState.DRAGGING:
            self.gravity_enabled = False
    
    def _decide_next_action(self) -> None:
        """Decide next action berdasarkan AI (legacy method, now uses random behavior AI)"""
        possible_actions = []
        
        if self.stats.energy > 30:
            possible_actions.extend([
                (PetState.WALKING, 40),
                (PetState.RUNNING, 20),
            ])
        
        if self.stats.energy < 70:
            possible_actions.extend([
                (PetState.SITTING, 30),
            ])
        
        if self.stats.happiness > 50:
            possible_actions.extend([
                (PetState.POSE, 15),
                (PetState.EAT_BERRY, 10),
                (PetState.WATCH, 20),
            ])
        
        if random.random() < 0.1:
            possible_actions.extend([
                (PetState.THROW_NEEDLE, 5),
            ])
        
        if possible_actions:
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
        """Start movement dengan target random (multi-monitor aware)"""
        max_distance = 300 if movement_type == PetState.RUNNING else 150
        direction = random.choice([-1, 1])
        distance = random.randint(50, max_distance)
        
        # Calculate target within current monitor bounds
        monitor = self.current_monitor or {'left': 0, 'right': 1920}
        self.target_x = self.x + (distance * direction)
        self.target_x = max(monitor['left'], min(monitor['right'] - self.rect.width, self.target_x))
        
        self.facing_right = direction > 0
        
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
        self.stats.happiness = max(0, self.stats.happiness - 0.5 * dt)
        self.stats.energy = max(0, self.stats.energy - 0.3 * dt)
        
        if self.state in [PetState.SITTING, PetState.IDLE]:
            self.stats.energy = min(100, self.stats.energy + 0.5 * dt)
        
        time_since_interaction = time.time() - self.stats.last_interaction
        if time_since_interaction < 10:
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
                                                 PetState.GRAB_WALL, PetState.GRAB_CEILING,
                                                 PetState.BOUNCING]
                    self.animation_manager.play_action(new_state.value, loop=loop_animation)
                except Exception as e:
                    print(f"Error starting animation for {new_state.value}: {e}")
            
            # State-specific initialization
            if new_state == PetState.SITTING:
                self.velocity_x = 0
                self.velocity_y = 0
                self.gravity_enabled = False
                self.on_ground = True
            elif new_state == PetState.FALLING or new_state == PetState.THROWN:
                self.on_ground = False
                self.gravity_enabled = True
            elif new_state == PetState.DRAGGING:
                self.velocity_x = 0
                self.velocity_y = 0
                self.gravity_enabled = False
                self.on_ground = False
                self.pinch_animation_active = True  # Enable pinch animation
            elif new_state == PetState.BOUNCING:
                self.on_ground = False
                self.gravity_enabled = True
            elif new_state == PetState.IDLE:
                self.velocity_x = 0
                self.velocity_y = 0
                self.on_ground = True
                self.gravity_enabled = True
                self.pinch_animation_active = False  # Disable pinch animation
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int) -> str:
        """Enhanced mouse handling dengan pinch animation debug"""
        if not self.rect.collidepoint(pos):
            return "none"
        
        current_time = pygame.time.get_ticks()
        
        if button == 1:  # Left click
            self.dragging = True
            self.drag_offset_x = pos[0] - self.rect.x
            self.drag_offset_y = pos[1] - self.rect.y
            
            # Calculate relative mouse position for pinch animation
            self.mouse_relative_x = pos[0] - self.rect.centerx
            
            self.change_state(PetState.DRAGGING)
            
            # Update interaction stats
            self.stats.last_interaction = time.time()
            self.stats.total_interactions += 1
            self.stats.times_petted += 1
            self.stats.happiness = min(100, self.stats.happiness + 10)
            
            print(f"🤏 Started pinch drag: {self.pet_id} (offset: {self.mouse_relative_x:.0f})")
            return "drag_start"
        
        elif button == 3:  # Right click
            if current_time - self.last_click_time < AppConstants.DOUBLE_CLICK_TIMEOUT:
                return "kill"
            else:
                self.last_click_time = current_time
                if self.state != PetState.SITTING:
                    self.change_state(PetState.SITTING)
                else:
                    special_actions = [PetState.POSE, PetState.EAT_BERRY, PetState.WATCH, PetState.THROW_NEEDLE]
                    chosen_action = random.choice(special_actions)
                    self.change_state(chosen_action)
                return "sit"
        
        return "none"
    
    def handle_mouse_up(self, button: int, mouse_dx: float = 0.0, mouse_dy: float = 0.0) -> str:
        """Enhanced mouse up handling dengan throw physics"""
        if button == 1 and self.dragging:
            self.dragging = False
            self.pinch_animation_active = False  # Disable pinch animation
            
            # Apply throw velocity
            self.velocity_x = mouse_dx * self.DRAG_THROW_MULTIPLIER
            self.velocity_y = mouse_dy * self.DRAG_THROW_MULTIPLIER
            
            self.change_state(PetState.THROWN)
            self.on_ground = False
            self.gravity_enabled = True
            
            print(f"🚀 Pet {self.pet_id} thrown with velocity ({self.velocity_x:.1f}, {self.velocity_y:.1f})")
            return "drag_end"
        
        return "none"
    
    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Enhanced mouse motion handling dengan smooth pinch animation update"""
        if self.dragging:
            self.x = float(pos[0] - self.drag_offset_x) 
            self.y = float(pos[1] - self.drag_offset_y)
            
            # Update mouse relative position for smooth pinch animation
            old_relative_x = self.mouse_relative_x
            self.mouse_relative_x = pos[0] - (self.x + self.rect.width // 2)
            
            # Debug pinch changes jika signifikan
            if abs(self.mouse_relative_x - old_relative_x) > 5:
                print(f"🤏 Pinch offset updated: {self.mouse_relative_x:.0f}")
            
            self.target_x = self.x
            self.target_y = self.y
            
            # Update current monitor
            self.current_monitor = self._get_current_monitor()
    
    def handle_speech(self, text: str, duration: float = 10.0) -> None:
        """Handle speech bubble display"""
        print(f"Pet {self.pet_id} says: {text}")
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
        """Enhanced state information with pinch and behavior info"""
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
            'pinch_animation_active': self.pinch_animation_active,
            'mouse_relative_x': self.mouse_relative_x,
            'current_monitor': self.current_monitor,
            'next_behavior_time': self.next_behavior_time - self.behavior_timer,
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
            'velocity_x': self.velocity_x,
            'velocity_y': self.velocity_y,
            'on_ground': self.on_ground,
            'gravity_enabled': self.gravity_enabled,
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
        pet.velocity_x = state_data.get('velocity_x', 0.0)
        pet.velocity_y = state_data.get('velocity_y', 0.0)
        pet.on_ground = state_data.get('on_ground', True)
        pet.gravity_enabled = state_data.get('gravity_enabled', True)
        
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
        
        # Stats overlay (only in debug mode)
        if self.config.get('settings.debug_mode', False) and self.config.get('settings.show_stats', False):
            self._draw_stats_overlay(screen)
    
    def _draw_debug_info(self, screen: pygame.Surface) -> None:
        """Enhanced debug information dengan pinch dan behavior info"""
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
        
        # Draw pinch info
        if self.pinch_animation_active:
            pinch_text = font.render(f"Pinch: {self.mouse_relative_x:.0f}", True, (255, 255, 0))
            screen.blit(pinch_text, (self.rect.x, self.rect.y - 45))
        
        # Draw behavior timer
        next_behavior_in = max(0, self.next_behavior_time - self.behavior_timer)
        behavior_text = font.render(f"Next: {next_behavior_in:.1f}s", True, (0, 255, 255))
        screen.blit(behavior_text, (self.rect.x, self.rect.y - 65))
        
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
        
        # Display velocity values
        velocity_text = font.render(f"Vel: ({self.velocity_x:.0f}, {self.velocity_y:.0f})", True, (255, 255, 255))
        screen.blit(velocity_text, (self.rect.x, self.rect.y - 85))

    def _draw_stats_overlay(self, screen: pygame.Surface) -> None:
        """Draw stats overlay untuk monitoring"""
        font = pygame.font.Font(None, 16)
        y_offset = 0
        
        stats_info = [
            f"Health: {self.stats.health:.0f}",
            f"Happy: {self.stats.happiness:.0f}",
            f"Energy: {self.stats.energy:.0f}",
            f"State: {self.state.value}",
            f"Monitor: {len(self.monitors)}",
        ]
        
        # Add pinch info if active
        if self.pinch_animation_active:
            stats_info.append(f"Pinch: {self.mouse_relative_x:.0f}")
        
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
        return ["Stand", "Walk", "Sit", "Run"]
    
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
            'pinch_animation_available': len(self.pinch_sprites) > 0,
            'behavior_weights_loaded': len(self.behavior_weights),
            'multi_monitor_support': len(self.monitors) > 0,
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
        self.monitors.clear()
        self.behavior_weights.clear()
        self.pinch_sprites.clear()