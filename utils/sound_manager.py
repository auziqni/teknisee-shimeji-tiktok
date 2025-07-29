#!/usr/bin/env python3
"""
utils/sound_manager.py - Sound System Management

Handles loading, caching, and playing sound effects untuk desktop pets
with volume control and error handling.
"""

import pygame
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass

from config import AppConstants, get_config


@dataclass
class SoundInfo:
    """Information about a sound file"""
    name: str
    file_path: str
    volume: float = 1.0  # 0.0 to 1.0
    loaded: bool = False
    sound_object: Optional[pygame.mixer.Sound] = None


class SoundManager:
    """Manages sound loading, caching, and playback"""
    
    def __init__(self):
        self.config = get_config()
        self.sound_cache: Dict[str, SoundInfo] = {}
        self.master_volume = 1.0
        self.sound_enabled = True
        
        # Initialize pygame mixer
        self._initialize_mixer()
    
    def _initialize_mixer(self) -> bool:
        """Initialize pygame mixer for sound"""
        try:
            # Initialize mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            
            # Get volume from config
            config_volume = self.config.get('settings.volume', 70)
            self.master_volume = config_volume / 100.0
            
            print(f"Sound system initialized at volume {config_volume}%")
            return True
            
        except pygame.error as e:
            print(f"Failed to initialize sound system: {e}")
            self.sound_enabled = False
            return False
    
    def load_sound(self, sprite_name: str, sound_file: str) -> bool:
        """Load a sound file dengan caching"""
        if not self.sound_enabled:
            return False
        
        # Create cache key
        cache_key = f"{sprite_name}:{sound_file}"
        
        # Check if already cached
        if cache_key in self.sound_cache and self.sound_cache[cache_key].loaded:
            return True
        
        # Build file path
        sound_path = self._get_sound_path(sprite_name, sound_file)
        
        try:
            if os.path.exists(sound_path):
                # Load sound
                sound_obj = pygame.mixer.Sound(sound_path)
                
                # Create sound info
                sound_info = SoundInfo(
                    name=sound_file,
                    file_path=sound_path,
                    loaded=True,
                    sound_object=sound_obj
                )
                
                # Cache it
                self.sound_cache[cache_key] = sound_info
                print(f"Loaded sound: {sound_file}")
                return True
            else:
                print(f"Sound file not found: {sound_path}")
                return False
                
        except pygame.error as e:
            print(f"Error loading sound {sound_path}: {e}")
            return False
    
    def play_sound(self, sprite_name: str, sound_file: str, volume_db: Optional[int] = None) -> bool:
        """Play a sound dengan volume control"""
        if not self.sound_enabled:
            return False
        
        cache_key = f"{sprite_name}:{sound_file}"
        
        # Load sound if not cached
        if cache_key not in self.sound_cache:
            if not self.load_sound(sprite_name, sound_file):
                return False
        
        sound_info = self.sound_cache[cache_key]
        if not sound_info.loaded or not sound_info.sound_object:
            return False
        
        try:
            # Calculate volume
            final_volume = self.master_volume
            
            if volume_db is not None:
                # Convert dB to linear scale (volume_db is usually negative)
                # -11 dB ≈ 0.28, -14 dB ≈ 0.20
                db_volume = 10 ** (volume_db / 20.0)
                final_volume *= db_volume
            
            # Clamp volume
            final_volume = max(0.0, min(1.0, final_volume))
            
            # Set volume and play
            sound_info.sound_object.set_volume(final_volume)
            sound_info.sound_object.play()
            
            return True
            
        except pygame.error as e:
            print(f"Error playing sound {sound_file}: {e}")
            return False
    
    def _get_sound_path(self, sprite_name: str, sound_file: str) -> str:
        """Get full path to sound file"""
        # Remove leading slash if present
        clean_filename = sound_file.lstrip('/')
        
        # Try different possible locations
        possible_paths = [
            # In sounds subdirectory (recommended)
            os.path.join(AppConstants.ASSETS_DIR, sprite_name, "sounds", clean_filename),
            # In root sprite directory
            os.path.join(AppConstants.ASSETS_DIR, sprite_name, clean_filename),
            # In audio subdirectory
            os.path.join(AppConstants.ASSETS_DIR, sprite_name, "audio", clean_filename),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return first path as default (for error reporting)
        return possible_paths[0]
    
    def set_master_volume(self, volume_percent: int) -> None:
        """Set master volume (0-100)"""
        self.master_volume = max(0.0, min(1.0, volume_percent / 100.0))
        print(f"Master volume set to {volume_percent}%")
    
    def enable_sound(self, enabled: bool) -> None:
        """Enable or disable sound system"""
        self.sound_enabled = enabled
        print(f"Sound system {'enabled' if enabled else 'disabled'}")
    
    def preload_sprite_sounds(self, sprite_name: str) -> int:
        """Preload all sounds referenced in XML untuk sprite pack"""
        if not self.sound_enabled:
            return 0
        
        loaded_count = 0
        
        try:
            # Parse XML to get sound references
            from utils.xml_parser import XMLParser
            xml_parser = XMLParser()
            
            if xml_parser.parse_sprite_pack(sprite_name):
                actions = xml_parser.get_all_actions()
                
                for action_data in actions.values():
                    for animation in action_data.animations:
                        for pose in animation.poses:
                            if pose.sound_file:
                                if self.load_sound(sprite_name, pose.sound_file):
                                    loaded_count += 1
                
                print(f"Preloaded {loaded_count} sounds for {sprite_name}")
            
        except Exception as e:
            print(f"Error preloading sounds for {sprite_name}: {e}")
        
        return loaded_count
    
    def get_sound_info(self) -> Dict[str, Any]:
        """Get information tentang sound system"""
        return {
            'sound_enabled': self.sound_enabled,
            'master_volume': self.master_volume,
            'cached_sounds': len(self.sound_cache),
            'mixer_initialized': pygame.mixer.get_init() is not None,
            'mixer_info': pygame.mixer.get_init() if pygame.mixer.get_init() else None
        }
    
    def list_missing_sounds(self, sprite_name: str) -> list:
        """List sounds yang di-reference di XML tapi file tidak ada"""
        missing_sounds = []
        
        try:
            from utils.xml_parser import XMLParser
            xml_parser = XMLParser()
            
            if xml_parser.parse_sprite_pack(sprite_name):
                actions = xml_parser.get_all_actions()
                
                for action_data in actions.values():
                    for animation in action_data.animations:
                        for pose in animation.poses:
                            if pose.sound_file:
                                sound_path = self._get_sound_path(sprite_name, pose.sound_file)
                                if not os.path.exists(sound_path):
                                    missing_sounds.append(pose.sound_file)
        
        except Exception as e:
            print(f"Error checking missing sounds: {e}")
        
        return list(set(missing_sounds))  # Remove duplicates
    
    def clear_cache(self) -> None:
        """Clear sound cache"""
        self.sound_cache.clear()
        print("Sound cache cleared")
    
    def cleanup(self) -> None:
        """Cleanup sound system"""
        self.clear_cache()
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        print("Sound system cleaned up")


# Global sound manager instance
_sound_manager: Optional[SoundManager] = None

def get_sound_manager() -> SoundManager:
    """Get global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager

def init_sound_manager() -> SoundManager:
    """Initialize global sound manager"""
    global _sound_manager
    _sound_manager = SoundManager()
    return _sound_manager
