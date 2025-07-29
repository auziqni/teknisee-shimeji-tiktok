#!/usr/bin/env python3
"""
config.py - Configuration management and constants

Handles JSON configuration management and application constants
following best practices for settings persistence.
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """JSON configuration management system with auto-save and validation"""
    
    # Application constants
    DEFAULT_CONFIG_FILE = "config.json"
    DEFAULT_FPS = 30
    DEFAULT_SPAWN_OFFSET = 50
    DOUBLE_CLICK_WINDOW = 500  # milliseconds
    
    def __init__(self, config_file: str = DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        self.config = self.load_config()
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
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
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file with error handling"""
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
    
    def save_config(self) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Recursively update nested dictionaries"""
        for key, value in update_dict.items():
            if (key in base_dict and 
                isinstance(base_dict[key], dict) and 
                isinstance(value, dict)):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'settings.volume')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
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
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.default_config.copy()
        self.save_config()
        print("Configuration reset to defaults")
    
    def validate_config(self) -> bool:
        """Validate configuration structure and values"""
        try:
            # Check required sections exist
            required_sections = ['settings', 'tiktok', 'sprite_packs', 'logging', 'ui']
            for section in required_sections:
                if section not in self.config:
                    print(f"Missing config section: {section}")
                    return False
            
            # Validate value ranges
            volume = self.get('settings.volume', 70)
            if not (0 <= volume <= 100):
                print(f"Invalid volume value: {volume}")
                return False
            
            freq = self.get('settings.behavior_frequency', 50)
            if not (10 <= freq <= 100):
                print(f"Invalid behavior frequency: {freq}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Config validation error: {e}")
            return False


# Application Constants
class AppConstants:
    """Application-wide constants and settings"""
    
    # Version information
    VERSION = "Phase 1 Step 2"
    APP_NAME = "Teknisee Shimeji TikTok"
    
    # File paths
    ASSETS_DIR = "assets"
    SPRITE_REQUIRED_FILE = "shime1.png"
    XML_CONFIG_DIR = "conf"
    ACTIONS_XML = "actions.xml"
    BEHAVIORS_XML = "behaviors.xml"
    
    # Display settings
    DEFAULT_SPRITE_SIZE = (128, 128)
    SPAWN_OFFSET = 50
    SCREEN_MARGIN = 200
    
    # Performance settings
    TARGET_FPS = 30
    PYGAME_FLAGS = "NOFRAME | SRCALPHA"
    
    # Mouse interaction
    DOUBLE_CLICK_TIMEOUT = 500  # milliseconds
    DRAG_THRESHOLD = 5  # pixels
    
    # UI dimensions
    CONTROL_PANEL_DEFAULT_SIZE = (450, 600)
    CONTROL_PANEL_MIN_SIZE = (400, 500)
    
    # Logging
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def get_sprite_path(cls, sprite_name: str, filename: str) -> str:
        """Get full path to sprite file"""
        return os.path.join(cls.ASSETS_DIR, sprite_name, filename)
    
    @classmethod
    def get_xml_path(cls, sprite_name: str, xml_file: str) -> str:
        """Get full path to XML configuration file"""
        return os.path.join(cls.ASSETS_DIR, sprite_name, cls.XML_CONFIG_DIR, xml_file)
    
    @classmethod
    def validate_sprite_pack(cls, sprite_name: str) -> bool:
        """Validate sprite pack has required files"""
        sprite_dir = os.path.join(cls.ASSETS_DIR, sprite_name)
        if not os.path.isdir(sprite_dir):
            return False
        
        # Check for required sprite file
        sprite_file = os.path.join(sprite_dir, cls.SPRITE_REQUIRED_FILE)
        if not os.path.exists(sprite_file):
            return False
        
        return True


# Global configuration instance
_config_manager: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def init_config(config_file: str = ConfigManager.DEFAULT_CONFIG_FILE) -> ConfigManager:
    """Initialize global configuration manager"""
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager