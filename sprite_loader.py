#!/usr/bin/env python3
"""
sprite_loader.py - Sprite discovery and loading system

Handles auto-discovery of sprite packs and loading of sprite images
with validation and error handling. Fixed circular import issues.
"""

import os
import pygame
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from config import AppConstants, get_config


@dataclass
class SpritePackInfo:
    """Information about a sprite pack"""
    name: str
    path: str
    has_xml: bool
    sprite_count: int
    valid: bool


class SpriteDiscovery:
    """Auto-discovery system for sprite packs"""
    
    @staticmethod
    def discover_sprite_packs() -> List[str]:
        """Scan assets folder and return list of valid sprite packs"""
        sprite_packs = []
        assets_dir = AppConstants.ASSETS_DIR
        
        if not os.path.exists(assets_dir):
            print(f"Warning: {assets_dir} directory not found")
            return sprite_packs
        
        try:
            for folder in os.listdir(assets_dir):
                sprite_path = os.path.join(assets_dir, folder)
                
                if os.path.isdir(sprite_path):
                    if AppConstants.validate_sprite_pack(folder):
                        sprite_packs.append(folder)
                        print(f"Found sprite pack: {folder}")
                    else:
                        print(f"Invalid sprite pack (missing {AppConstants.SPRITE_REQUIRED_FILE}): {folder}")
        
        except OSError as e:
            print(f"Error scanning assets directory: {e}")
        
        return sprite_packs
    
    @staticmethod
    def get_sprite_pack_info(sprite_name: str) -> Optional[SpritePackInfo]:
        """Get detailed information about a sprite pack"""
        sprite_path = os.path.join(AppConstants.ASSETS_DIR, sprite_name)
        
        if not os.path.isdir(sprite_path):
            return None
        
        # Check for required sprite file
        has_required_sprite = os.path.exists(
            os.path.join(sprite_path, AppConstants.SPRITE_REQUIRED_FILE)
        )
        
        # Check for XML files (without importing xml_parser to avoid circular import)
        has_xml = False
        try:
            xml_dir = os.path.join(sprite_path, AppConstants.XML_CONFIG_DIR)
            if os.path.exists(xml_dir):
                actions_xml = os.path.join(xml_dir, AppConstants.ACTIONS_XML)
                behaviors_xml = os.path.join(xml_dir, AppConstants.BEHAVIORS_XML)
                has_xml = os.path.exists(actions_xml) and os.path.exists(behaviors_xml)
        except:
            has_xml = False
        
        # Count sprite files
        sprite_count = 0
        try:
            for file in os.listdir(sprite_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    sprite_count += 1
        except OSError:
            sprite_count = 0
        
        return SpritePackInfo(
            name=sprite_name,
            path=sprite_path,
            has_xml=has_xml,
            sprite_count=sprite_count,
            valid=has_required_sprite
        )
    
    @staticmethod
    def validate_all_sprite_packs() -> Dict[str, bool]:
        """Validate all discovered sprite packs"""
        sprite_packs = SpriteDiscovery.discover_sprite_packs()
        validation_results = {}
        
        for pack_name in sprite_packs:
            pack_info = SpriteDiscovery.get_sprite_pack_info(pack_name)
            validation_results[pack_name] = pack_info.valid if pack_info else False
        
        return validation_results


class SpriteLoader:
    """Sprite loading and caching system"""
    
    def __init__(self):
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._fallback_sprite: Optional[pygame.Surface] = None
    
    def load_sprite(self, sprite_name: str, filename: str) -> pygame.Surface:
        """Load a sprite image with caching"""
        cache_key = f"{sprite_name}:{filename}"
        
        # Check cache first
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        # Load sprite from file
        sprite_path = AppConstants.get_sprite_path(sprite_name, filename)
        
        try:
            if os.path.exists(sprite_path):
                # Load image without convert first (to avoid display init error)
                surface = pygame.image.load(sprite_path)
                
                # Try to convert with alpha if display is initialized
                try:
                    if pygame.get_init():
                        surface = surface.convert_alpha()
                except pygame.error:
                    # Display not initialized yet, use as-is
                    pass
                
                self._sprite_cache[cache_key] = surface
                return surface
            else:
                print(f"Sprite file not found: {sprite_path}")
                return self._get_fallback_sprite()
                
        except pygame.error as e:
            print(f"Error loading sprite {sprite_path}: {e}")
            return self._get_fallback_sprite()
    
    def _get_fallback_sprite(self) -> pygame.Surface:
        """Get fallback sprite for missing images"""
        if self._fallback_sprite is None:
            self._fallback_sprite = pygame.Surface(AppConstants.DEFAULT_SPRITE_SIZE, pygame.SRCALPHA)
            self._fallback_sprite.fill((255, 100, 100, 200))  # Semi-transparent red
        
        return self._fallback_sprite
    
    def preload_sprite_pack(self, sprite_name: str) -> bool:
        """Preload all sprites for a sprite pack"""
        try:
            # Parse XML to get list of required sprites (with lazy import)
            try:
                from utils.xml_parser import XMLParser
                xml_parser = XMLParser()
                if not xml_parser.parse_sprite_pack(sprite_name):
                    print(f"Failed to parse XML for sprite pack: {sprite_name}")
                    return False
                
                # Load all sprites referenced in actions
                loaded_count = 0
                actions = xml_parser.get_all_actions()
                
                for action_data in actions.values():
                    for animation in action_data.animations:
                        for pose in animation.poses:
                            if pose.image:
                                self.load_sprite(sprite_name, pose.image)
                                loaded_count += 1
                
                print(f"Preloaded {loaded_count} sprites for pack: {sprite_name}")
                return True
                
            except ImportError:
                # Fallback: load common sprite files
                print(f"XML parser not available, loading common sprites for {sprite_name}")
                common_sprites = [
                    "shime1.png", "shime1a.png",  # Idle
                    "shime2.png", "shime3.png",   # Walk
                    "shime11.png", "shime11a.png" # Sit
                ]
                
                loaded_count = 0
                for sprite_file in common_sprites:
                    try:
                        self.load_sprite(sprite_name, sprite_file)
                        loaded_count += 1
                    except:
                        pass
                
                print(f"Preloaded {loaded_count} common sprites for pack: {sprite_name}")
                return loaded_count > 0
            
        except Exception as e:
            print(f"Error preloading sprite pack {sprite_name}: {e}")
            return False
    
    def get_sprite_size(self, sprite_name: str, filename: str) -> Tuple[int, int]:
        """Get size of a sprite image"""
        sprite = self.load_sprite(sprite_name, filename)
        return sprite.get_size()
    
    def clear_cache(self) -> None:
        """Clear sprite cache to free memory"""
        self._sprite_cache.clear()
        print("Sprite cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get information about sprite cache"""
        total_size = sum(
            sprite.get_width() * sprite.get_height() * 4  # Assume 32-bit RGBA
            for sprite in self._sprite_cache.values()
        )
        
        return {
            'cached_sprites': len(self._sprite_cache),
            'estimated_memory_bytes': total_size,
            'estimated_memory_mb': total_size / (1024 * 1024)
        }
    
    def list_available_sprites(self, sprite_name: str) -> List[str]:
        """List all available sprite files for a sprite pack"""
        sprite_path = os.path.join(AppConstants.ASSETS_DIR, sprite_name)
        sprite_files = []
        
        if not os.path.isdir(sprite_path):
            return sprite_files
        
        try:
            for file in os.listdir(sprite_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    sprite_files.append(file)
            
            sprite_files.sort()  # Sort alphabetically
            
        except OSError as e:
            print(f"Error listing sprites for {sprite_name}: {e}")
        
        return sprite_files
    
    def validate_sprite_references(self, sprite_name: str) -> Dict[str, bool]:
        """Validate that all XML-referenced sprites exist"""
        try:
            # Lazy import to avoid circular dependency
            from utils.xml_parser import XMLParser
            xml_parser = XMLParser()
            
            if not xml_parser.parse_sprite_pack(sprite_name):
                return {}
            
            validation_results = {}
            actions = xml_parser.get_all_actions()
            
            for action_data in actions.values():
                for animation in action_data.animations:
                    for pose in animation.poses:
                        if pose.image:
                            sprite_path = AppConstants.get_sprite_path(sprite_name, pose.image)
                            validation_results[pose.image] = os.path.exists(sprite_path)
            
            return validation_results
            
        except ImportError:
            # Fallback: check common sprites
            print("XML parser not available, checking common sprites")
            common_sprites = [
                "shime1.png", "shime1a.png",
                "shime2.png", "shime3.png", 
                "shime11.png", "shime11a.png"
            ]
            
            validation_results = {}
            for sprite_file in common_sprites:
                sprite_path = AppConstants.get_sprite_path(sprite_name, sprite_file)
                validation_results[sprite_file] = os.path.exists(sprite_path)
            
            return validation_results
        
        except Exception as e:
            print(f"Error validating sprite references: {e}")
            return {}


# Global sprite loader instance
_sprite_loader: Optional[SpriteLoader] = None

def get_sprite_loader() -> SpriteLoader:
    """Get global sprite loader instance"""
    global _sprite_loader
    if _sprite_loader is None:
        _sprite_loader = SpriteLoader()
    return _sprite_loader

def init_sprite_loader() -> SpriteLoader:
    """Initialize global sprite loader"""
    global _sprite_loader
    _sprite_loader = SpriteLoader()
    return _sprite_loader