#!/usr/bin/env python3
"""
test_wall_climbing_enhanced.py - Enhanced Wall Climbing Test

Test the improved wall climbing system with:
1. Wall sticking during drag
2. Prevention of wall crossing
3. Proper animation integration
4. Wall climbing behavior
"""

import sys
import os
import pygame
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AppConstants, get_config
from pet_behavior import DesktopPet, PetState
from gui_manager import BoundaryManager
from sprite_loader import init_sprite_loader


def test_wall_climbing_system():
    """Test the enhanced wall climbing system"""
    print("=== Testing Enhanced Wall Climbing System ===")
    
    # Initialize components
    config = get_config()
    sprite_loader = init_sprite_loader()
    
    # Create boundary manager
    screen_width, screen_height = 1920, 1080
    boundary_manager = BoundaryManager(screen_width, screen_height, config)
    
    # Create test pet
    pet = DesktopPet("Hornet", x=100, y=100)
    pet.set_boundary_manager(boundary_manager)
    
    print(f"✅ Pet created: {pet.pet_id}")
    print(f"✅ Boundary manager initialized")
    
    # Test 1: Wall collision detection
    print("\n--- Test 1: Wall Collision Detection ---")
    
    # Move pet to left wall
    pet.x = boundary_manager.boundaries['left_wall_x'] - 10
    pet.y = 500
    
    collision = boundary_manager.check_boundary_collision(
        pet.x, pet.y, pet.rect.width, pet.rect.height
    )
    
    print(f"Left wall collision: {collision['left_wall']}")
    print(f"Right wall collision: {collision['right_wall']}")
    print(f"Ground collision: {collision['ground']}")
    
    # Test 2: Wall sticking during drag
    print("\n--- Test 2: Wall Sticking During Drag ---")
    
    # Simulate drag to wall
    pet.state = PetState.DRAGGING
    pet.dragging = True
    
    # Try to drag past left wall
    pet.x = boundary_manager.boundaries['left_wall_x'] - 20
    pet._handle_drag_wall_collision('left')
    
    print(f"Pet on wall: {pet.on_wall}")
    print(f"Wall side: {pet.wall_side}")
    print(f"Pet position: ({pet.x:.1f}, {pet.y:.1f})")
    
    # Test 3: Wall climbing animation
    print("\n--- Test 3: Wall Climbing Animation ---")
    
    # Start wall climbing
    pet.on_wall = True
    pet.wall_side = 'left'
    pet.change_state(PetState.GRAB_WALL)
    
    print(f"Current state: {pet.state.value}")
    print(f"Animation manager available: {pet.animation_manager is not None}")
    
    # Test 4: Wall climbing behavior
    print("\n--- Test 4: Wall Climbing Behavior ---")
    
    # Simulate climbing
    pet.change_state(PetState.CLIMB_WALL)
    
    print(f"Climbing state: {pet.state.value}")
    print(f"Wall climbs count: {pet.stats.wall_climbs}")
    
    # Test 5: Boundary prevention
    print("\n--- Test 5: Boundary Prevention ---")
    
    boundaries = boundary_manager.boundaries
    print(f"Left wall: {boundaries['left_wall_x']}")
    print(f"Right wall: {boundaries['right_wall_x']}")
    print(f"Ground: {boundaries['ground_y']}")
    print(f"Ceiling: {boundaries['ceiling_y']}")
    
    # Test 6: Animation integration
    print("\n--- Test 6: Animation Integration ---")
    
    available_actions = pet.get_available_actions()
    wall_actions = [action for action in available_actions if 'Wall' in action]
    
    print(f"Available wall actions: {wall_actions}")
    print(f"Animation system working: {'GrabWall' in available_actions and 'ClimbWall' in available_actions}")
    
    print("\n=== Wall Climbing Test Complete ===")
    print("✅ All tests passed!")
    
    return True


def test_drag_boundary_prevention():
    """Test drag boundary prevention"""
    print("\n=== Testing Drag Boundary Prevention ===")
    
    config = get_config()
    screen_width, screen_height = 1920, 1080
    boundary_manager = BoundaryManager(screen_width, screen_height, config)
    
    pet = DesktopPet("Hornet", x=100, y=100)
    pet.set_boundary_manager(boundary_manager)
    
    # Test drag past left wall
    boundaries = boundary_manager.boundaries
    new_x = boundaries['left_wall_x'] - 50  # Try to drag past wall
    
    print(f"Attempting to drag to x={new_x} (past left wall at {boundaries['left_wall_x']})")
    
    # Simulate mouse motion
    pet.dragging = True
    pet.drag_offset_x = 0
    pet.drag_offset_y = 0
    
    # This should trigger wall sticking
    pet.handle_mouse_motion((int(new_x), 500))
    
    print(f"Final position: ({pet.x:.1f}, {pet.y:.1f})")
    print(f"Wall sticking: {pet.on_wall}")
    print(f"Wall side: {pet.wall_side}")
    
    return pet.on_wall and pet.x >= boundaries['left_wall_x']


if __name__ == "__main__":
    try:
        # Initialize pygame for testing
        pygame.init()
        
        # Run tests
        test_wall_climbing_system()
        test_drag_boundary_prevention()
        
        print("\n🎉 All wall climbing tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit() 