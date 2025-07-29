#!/usr/bin/env python3
"""
utils/animation.py - Enhanced Animation System (Clean Version)

Mengelola animasi pet berdasarkan data XML dengan frame timing,
state transitions, dan sprite flipping yang akurat.
Fixed all circular import issues.
"""

import pygame
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from config import get_config
from utils.xml_parser import XMLParser, ActionData, AnimationData, PoseData


class AnimationState(Enum):
    """Status animasi saat ini"""
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


@dataclass
class AnimationFrame:
    """Data frame animasi individual"""
    sprite_surface: pygame.Surface
    duration: float  # dalam detik
    velocity: Tuple[float, float]
    anchor_point: Tuple[int, int]
    sound_file: Optional[str] = None
    volume: Optional[int] = None


class Animation:
    """Kelas untuk mengelola sequence animasi tunggal"""
    
    def __init__(self, animation_data: AnimationData, sprite_name: str):
        self.animation_data = animation_data
        self.sprite_name = sprite_name
        self.frames: List[AnimationFrame] = []
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.state = AnimationState.STOPPED
        self.loop = True
        self.facing_right = True
        
        # Create sprite loader instance directly
        self.sprite_loader = self._create_sprite_loader()
        self.config = get_config()
        
        # Build frames dari pose data
        self._build_frames()
    
    def _create_sprite_loader(self):
        """Create sprite loader instance safely"""
        try:
            from sprite_loader import SpriteLoader
            return SpriteLoader()
        except Exception as e:
            print(f"Error creating sprite loader: {e}")
            return None
    
    def _build_frames(self) -> None:
        """Membangun frame animasi dari pose data"""
        self.frames.clear()
        
        if not self.sprite_loader:
            print("Warning: No sprite loader available, creating fallback frame")
            self._create_fallback_frame()
            return
        
        for pose in self.animation_data.poses:
            try:
                # Load sprite surface
                sprite_surface = self.sprite_loader.load_sprite(
                    self.sprite_name, pose.image
                )
                
                # Convert duration dari frame count ke detik (asumsi 30 FPS)
                duration_seconds = pose.duration / 30.0
                
                # Convert velocity dari pixels/frame ke pixels/second
                velocity = (pose.velocity[0] * 30, pose.velocity[1] * 30)
                
                frame = AnimationFrame(
                    sprite_surface=sprite_surface,
                    duration=duration_seconds,
                    velocity=velocity,
                    anchor_point=pose.image_anchor,
                    sound_file=pose.sound,
                    volume=pose.volume
                )
                
                self.frames.append(frame)
                
            except Exception as e:
                print(f"Error loading frame for pose {pose.image}: {e}")
                continue
        
        if len(self.frames) > 0:
            print(f"Built {len(self.frames)} frames for animation")
        else:
            print(f"Warning: No frames built for animation, creating fallback")
            self._create_fallback_frame()
    
    def _create_fallback_frame(self):
        """Create fallback frame when sprite loading fails"""
        fallback_surface = pygame.Surface((128, 128), pygame.SRCALPHA)
        fallback_surface.fill((255, 100, 100, 200))
        fallback_frame = AnimationFrame(
            sprite_surface=fallback_surface,
            duration=1.0,
            velocity=(0, 0),
            anchor_point=(64, 128)
        )
        self.frames.append(fallback_frame)
    
    def start(self, loop: bool = True) -> None:
        """Mulai animasi"""
        self.loop = loop
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.state = AnimationState.PLAYING
    
    def stop(self) -> None:
        """Stop animasi"""
        self.state = AnimationState.STOPPED
        self.current_frame_index = 0
        self.frame_timer = 0.0
    
    def pause(self) -> None:
        """Pause animasi"""
        if self.state == AnimationState.PLAYING:
            self.state = AnimationState.PAUSED
    
    def resume(self) -> None:
        """Resume animasi"""
        if self.state == AnimationState.PAUSED:
            self.state = AnimationState.PLAYING
    
    def update(self, dt: float) -> Tuple[pygame.Surface, Tuple[float, float]]:
        """Update animasi dan return current sprite + velocity"""
        if self.state != AnimationState.PLAYING or not self.frames:
            # Return first frame sebagai default
            if self.frames:
                frame = self.frames[0]
                sprite = self._get_flipped_sprite(frame.sprite_surface)
                return sprite, frame.velocity
            else:
                # Ultimate fallback sprite
                fallback = pygame.Surface((128, 128), pygame.SRCALPHA)
                fallback.fill((255, 100, 100, 200))
                return fallback, (0, 0)
        
        # Update frame timer
        self.frame_timer += dt
        current_frame = self.frames[self.current_frame_index]
        
        # Check if current frame duration completed
        if self.frame_timer >= current_frame.duration:
            self.frame_timer = 0.0
            self.current_frame_index += 1
            
            # Check if animation completed
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.state = AnimationState.COMPLETED
            
            # Play sound if frame has one
            if current_frame.sound_file:
                self._play_sound(current_frame.sound_file, current_frame.volume)
        
        # Return current frame data
        current_frame = self.frames[self.current_frame_index]
        sprite = self._get_flipped_sprite(current_frame.sprite_surface)
        return sprite, current_frame.velocity
    
    def _get_flipped_sprite(self, sprite: pygame.Surface) -> pygame.Surface:
        """Get sprite dengan flip horizontal jika facing left"""
        if not self.facing_right:
            return pygame.transform.flip(sprite, True, False)
        return sprite
    
    def _play_sound(self, sound_file: str, volume: Optional[int]) -> None:
        """Play sound effect using sound manager"""
        try:
            from utils.sound_manager import get_sound_manager
            sound_manager = get_sound_manager()
            sound_manager.play_sound(self.sprite_name, sound_file, volume)
        except Exception as e:
            print(f"Error playing sound {sound_file}: {e}")
    
    def set_facing_direction(self, facing_right: bool) -> None:
        """Set arah menghadap pet"""
        self.facing_right = facing_right
    
    def get_current_frame_info(self) -> Dict[str, Any]:
        """Get informasi frame saat ini"""
        if not self.frames or self.current_frame_index >= len(self.frames):
            return {}
        
        current_frame = self.frames[self.current_frame_index]
        return {
            'frame_index': self.current_frame_index,
            'total_frames': len(self.frames),
            'frame_timer': self.frame_timer,
            'frame_duration': current_frame.duration,
            'velocity': current_frame.velocity,
            'anchor_point': current_frame.anchor_point,
            'state': self.state.value
        }


class AnimationManager:
    """Manager untuk mengelola multiple animasi dan transisi state"""
    
    def __init__(self, sprite_name: str):
        self.sprite_name = sprite_name
        self.xml_parser = XMLParser()
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.current_action_name = ""
        
        # Load XML data
        self._load_animations()
    
    def _load_animations(self) -> None:
        """Load semua animasi dari XML"""
        success = self.xml_parser.parse_sprite_pack(self.sprite_name)
        if not success:
            print(f"Failed to parse XML for sprite pack: {self.sprite_name}")
            return
        
        # Build animations dari action data
        actions = self.xml_parser.get_all_actions()
        for action_name, action_data in actions.items():
            for i, animation_data in enumerate(action_data.animations):
                # Create unique key untuk setiap animasi dalam action
                anim_key = f"{action_name}_{i}" if len(action_data.animations) > 1 else action_name
                animation = Animation(animation_data, self.sprite_name)
                self.animations[anim_key] = animation
        
        print(f"Loaded {len(self.animations)} animations for {self.sprite_name}")
    
    def play_action(self, action_name: str, loop: bool = True) -> bool:
        """Play animasi berdasarkan action name"""
        if action_name not in self.animations:
            print(f"Animation not found: {action_name}")
            return False
        
        # Stop current animation
        if self.current_animation:
            self.current_animation.stop()
        
        # Start new animation
        self.current_animation = self.animations[action_name]
        self.current_action_name = action_name
        self.current_animation.start(loop)
        
        return True
    
    def update(self, dt: float) -> Tuple[pygame.Surface, Tuple[float, float]]:
        """Update current animation"""
        if self.current_animation:
            return self.current_animation.update(dt)
        else:
            # No animation playing, return fallback
            fallback = pygame.Surface((128, 128), pygame.SRCALPHA)
            fallback.fill((100, 255, 100, 200))  # Green fallback
            return fallback, (0, 0)
    
    def set_facing_direction(self, facing_right: bool) -> None:
        """Set facing direction untuk semua animasi"""
        for animation in self.animations.values():
            animation.set_facing_direction(facing_right)
    
    def get_available_actions(self) -> List[str]:
        """Get list action yang tersedia"""
        return list(self.animations.keys())
    
    def is_animation_completed(self) -> bool:
        """Check apakah animasi saat ini sudah selesai"""
        if self.current_animation:
            return self.current_animation.state == AnimationState.COMPLETED
        return True
    
    def get_current_animation_info(self) -> Dict[str, Any]:
        """Get informasi animasi saat ini"""
        if not self.current_animation:
            return {'action_name': 'none', 'status': 'no_animation'}
        
        frame_info = self.current_animation.get_current_frame_info()
        frame_info['action_name'] = self.current_action_name
        return frame_info
    
    def stop_current_animation(self) -> None:
        """Stop animasi saat ini"""
        if self.current_animation:
            self.current_animation.stop()
    
    def pause_current_animation(self) -> None:
        """Pause animasi saat ini"""
        if self.current_animation:
            self.current_animation.pause()
    
    def resume_current_animation(self) -> None:
        """Resume animasi saat ini"""
        if self.current_animation:
            self.current_animation.resume()


# Helper functions
def create_animation_manager(sprite_name: str) -> Optional[AnimationManager]:
    """Factory function untuk membuat AnimationManager"""
    try:
        return AnimationManager(sprite_name)
    except Exception as e:
        print(f"Error creating animation manager for {sprite_name}: {e}")
        return None


def validate_animation_system(sprite_name: str) -> Dict[str, Any]:
    """Validate animation system untuk sprite pack"""
    validation_result = {
        'sprite_name': sprite_name,
        'xml_valid': False,
        'animations_loaded': 0,
        'missing_sprites': [],
        'errors': []
    }
    
    try:
        # Test XML parsing
        xml_parser = XMLParser()
        if xml_parser.parse_sprite_pack(sprite_name):
            validation_result['xml_valid'] = True
            
            # Test animation creation
            anim_manager = AnimationManager(sprite_name)
            validation_result['animations_loaded'] = len(anim_manager.animations)
            
            # Check for missing sprites using direct SpriteLoader instance
            try:
                from sprite_loader import SpriteLoader
                sprite_loader = SpriteLoader()
                sprite_refs = sprite_loader.validate_sprite_references(sprite_name)
                validation_result['missing_sprites'] = [
                    sprite for sprite, exists in sprite_refs.items() if not exists
                ]
            except Exception as e:
                print(f"Error validating sprites: {e}")
        
    except Exception as e:
        validation_result['errors'].append(str(e))
    
    return validation_result