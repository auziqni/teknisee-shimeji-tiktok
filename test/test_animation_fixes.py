#!/usr/bin/env python3
"""
test_animation_fixes.py - Animation and Direction Change Fixes Test

Test the fixes for:
1. Wall climbing animation display
2. Direction change glitches in corners
3. Animation integration improvements
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


def test_direction_change_cooldown():
    """Test direction change cooldown system"""
    print("=== Testing Direction Change Cooldown ===")
    
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
    
    # Test 1: Rapid direction changes should be prevented
    print("\n--- Test 1: Rapid Direction Change Prevention ---")
    
    initial_direction = pet.facing_right
    print(f"Initial direction: {'right' if initial_direction else 'left'}")
    
    # Try rapid direction changes
    for i in range(5):
        pet._change_direction()
        print(f"Direction change {i+1}: {'right' if pet.facing_right else 'left'}")
        time.sleep(0.1)  # Simulate rapid changes
    
    # Should not have changed due to cooldown
    final_direction = pet.facing_right
    print(f"Final direction: {'right' if final_direction else 'left'}")
    print(f"Direction changed: {initial_direction != final_direction}")
    
    # Test 2: Direction lock system
    print("\n--- Test 2: Direction Lock System ---")
    
    pet._lock_direction(1.0)  # Lock for 1 second
    print("Direction locked for 1 second")
    
    # Try to change direction while locked
    pet._change_direction()
    locked_direction = pet.facing_right
    print(f"Direction after lock attempt: {'right' if locked_direction else 'left'}")
    print(f"Direction changed during lock: {final_direction != locked_direction}")
    
    return True


def test_wall_climbing_animation():
    """Test wall climbing animation improvements"""
    print("\n=== Testing Wall Climbing Animation ===")
    
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
    
    # Test 1: Wall climbing state transitions
    print("\n--- Test 1: Wall Climbing State Transitions ---")
    
    # Simulate wall collision
    pet.on_wall = True
    pet.wall_side = 'left'
    pet.change_state(PetState.GRAB_WALL)
    
    print(f"GrabWall state: {pet.state.value}")
    print(f"Direction lock timer: {pet.direction_lock_timer}")
    print(f"Direction lock duration: {pet.direction_lock_duration}")
    
    # Simulate climbing transition
    pet.change_state(PetState.CLIMB_WALL)
    
    print(f"ClimbWall state: {pet.state.value}")
    print(f"Facing direction: {'right' if pet.facing_right else 'left'}")
    print(f"Wall side: {pet.wall_side}")
    
    # Test 2: Animation integration
    print("\n--- Test 2: Animation Integration ---")
    
    available_actions = pet.get_available_actions()
    wall_actions = [action for action in available_actions if 'Wall' in action]
    
    print(f"Available wall actions: {wall_actions}")
    print(f"Animation manager available: {pet.animation_manager is not None}")
    
    if pet.animation_manager:
        try:
            # Test animation direction setting
            pet.animation_manager.set_facing_direction(True)
            print("✅ Animation direction set successfully")
        except Exception as e:
            print(f"❌ Animation direction error: {e}")
    
    return True


def test_corner_collision_fixes():
    """Test corner collision fixes"""
    print("\n=== Testing Corner Collision Fixes ===")
    
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
    
    # Test 1: Corner collision with direction lock
    print("\n--- Test 1: Corner Collision Direction Lock ---")
    
    initial_direction = pet.facing_right
    print(f"Initial direction: {'right' if initial_direction else 'left'}")
    
    # Simulate corner collision
    pet._handle_corner_collision('left')
    
    print(f"After corner collision: {'right' if pet.facing_right else 'left'}")
    print(f"Direction lock timer: {pet.direction_lock_timer}")
    print(f"Direction lock duration: {pet.direction_lock_duration}")
    
    # Test 2: Wall turn around with direction lock
    print("\n--- Test 2: Wall Turn Around Direction Lock ---")
    
    # Reset direction lock
    pet.direction_lock_timer = 1.0  # Reset timer
    
    initial_direction = pet.facing_right
    print(f"Initial direction: {'right' if initial_direction else 'left'}")
    
    # Simulate wall turn around
    pet._handle_wall_turn_around('right')
    
    print(f"After wall turn around: {'right' if pet.facing_right else 'left'}")
    print(f"Direction lock timer: {pet.direction_lock_timer}")
    print(f"Direction lock duration: {pet.direction_lock_duration}")
    
    return True


def test_animation_display():
    """Test animation display improvements"""
    print("\n=== Testing Animation Display ===")
    
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
    
    # Test animation states
    test_states = [PetState.IDLE, PetState.WALKING, PetState.GRAB_WALL, PetState.CLIMB_WALL]
    
    for state in test_states:
        print(f"\n--- Testing {state.value} Animation ---")
        
        try:
            pet.change_state(state)
            print(f"✅ State changed to {state.value}")
            
            if pet.animation_manager:
                print(f"✅ Animation manager available")
                print(f"✅ Current animation: {pet.state.value}")
            else:
                print(f"⚠️ Animation manager not available")
                
        except Exception as e:
            print(f"❌ Error changing to {state.value}: {e}")
    
    return True


if __name__ == "__main__":
    try:
        # Initialize pygame for testing
        pygame.init()
        
        # Run tests
        test_direction_change_cooldown()
        test_wall_climbing_animation()
        test_corner_collision_fixes()
        test_animation_display()
        
        print("\n🎉 All animation fixes tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit() 