#!/usr/bin/env python3
"""
utils package - Enhanced utility modules untuk Teknisee Shimeji TikTok

Package ini berisi utility modules untuk XML parsing, sprite discovery,
animation management, dan helper functions lainnya yang digunakan di seluruh aplikasi.

Version: Phase 1 Step 3 - XML Parser & Animation System
"""

# Import XML parser first (no dependencies)
from .xml_parser import XMLParser

# Animation system akan di-import secara lazy untuk avoid circular imports
# Import animation system functions akan dilakukan oleh modules yang membutuhkan

__all__ = [
    'XMLParser'
]

__version__ = '1.3.0'
__status__ = 'Phase 1 Step 3 - XML Parser & Animation System'

# Lazy import function untuk animation system
def get_animation_system():
    """Lazy import animation system untuk avoid circular imports"""
    try:
        from .animation import Animation, AnimationManager, create_animation_manager, validate_animation_system
        return {
            'Animation': Animation,
            'AnimationManager': AnimationManager,
            'create_animation_manager': create_animation_manager,
            'validate_animation_system': validate_animation_system,
            'available': True
        }
    except ImportError as e:
        return {
            'available': False,
            'error': str(e)
        }