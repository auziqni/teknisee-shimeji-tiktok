#!/usr/bin/env python3
"""
Test script to verify debug arrow fix for wall climbing
"""
import sys
import os
import time
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet_behavior import DesktopPet
from config import get_config

def test_debug_arrow_consistency():
    """Test that debug arrow shows correct visual direction during wall climbing"""
    print("Testing debug arrow consistency with visual direction...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config = get_config()
    
    # Test scenarios: (wall_side, expected_arrow_right, description)
    test_scenarios = [
        ("left", True, "arrow should point right when on left wall"),
        ("right", False, "arrow should point left when on right wall"),
    ]
    
    print("Testing debug arrow directions:")
    
    for wall_side, expected_arrow_right, description in test_scenarios:
        print(f"  Testing {wall_side} wall climbing ({description})...")
        
        # Create pet and simulate wall collision
        pet = DesktopPet("Hornet", 400, 300)
        
        # Simulate wall collision
        pet.on_wall = True
        pet.wall_side = wall_side
        pet.gravity_enabled = False
        pet.velocity_x = 0
        pet.velocity_y = 0
        
        # Change to wall climbing state
        pet.change_state(pet.state.__class__.GRAB_WALL)
        
        # Wait a bit for state to settle
        for i in range(10):
            dt = 1/60.0
            pet.update(dt, (800, 600))
        
        # Check if visual direction is correct
        visual_facing_right = pet.facing_right
        
        # If animation manager exists, check its visual direction
        if pet.animation_manager and hasattr(pet.animation_manager, 'current_animation'):
            if pet.animation_manager.current_animation:
                visual_facing_right = pet.animation_manager.current_animation.facing_right
        
        if visual_facing_right == expected_arrow_right:
            print(f"    ✓ {wall_side} wall visual direction correct (arrow_right: {visual_facing_right})")
        else:
            print(f"    ❌ {wall_side} wall visual direction wrong (arrow_right: {visual_facing_right}, expected: {expected_arrow_right})")
            return False
        
        # Test CLIMB_WALL state
        pet.change_state(pet.state.__class__.CLIMB_WALL)
        
        # Wait a bit for state to settle
        for i in range(10):
            dt = 1/60.0
            pet.update(dt, (800, 600))
        
        # Check if visual direction is still correct
        visual_facing_right = pet.facing_right
        
        # If animation manager exists, check its visual direction
        if pet.animation_manager and hasattr(pet.animation_manager, 'current_animation'):
            if pet.animation_manager.current_animation:
                visual_facing_right = pet.animation_manager.current_animation.facing_right
        
        if visual_facing_right == expected_arrow_right:
            print(f"    ✓ {wall_side} wall climbing visual direction correct (arrow_right: {visual_facing_right})")
        else:
            print(f"    ❌ {wall_side} wall climbing visual direction wrong (arrow_right: {visual_facing_right}, expected: {expected_arrow_right})")
            return False
    
    print("✓ All debug arrow consistency tests passed!")
    return True

def test_drag_wall_arrow_consistency():
    """Test that debug arrow shows correct visual direction when dragged to walls"""
    print("\nTesting drag wall arrow consistency...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config = get_config()
    
    # Test scenarios: (wall_side, expected_arrow_right, description)
    test_scenarios = [
        ("left", True, "arrow should point right when dragged to left wall"),
        ("right", False, "arrow should point left when dragged to right wall"),
    ]
    
    print("Testing drag wall arrow directions:")
    
    for wall_side, expected_arrow_right, description in test_scenarios:
        print(f"  Testing {wall_side} wall drag ({description})...")
        
        # Create pet and simulate drag wall collision
        pet = DesktopPet("Hornet", 400, 300)
        
        # Simulate drag wall collision
        pet._handle_drag_wall_collision(wall_side)
        
        # Check if visual direction is correct
        visual_facing_right = pet.facing_right
        
        # If animation manager exists, check its visual direction
        if pet.animation_manager and hasattr(pet.animation_manager, 'current_animation'):
            if pet.animation_manager.current_animation:
                visual_facing_right = pet.animation_manager.current_animation.facing_right
        
        if visual_facing_right == expected_arrow_right:
            print(f"    ✓ {wall_side} wall drag visual direction correct (arrow_right: {visual_facing_right})")
        else:
            print(f"    ❌ {wall_side} wall drag visual direction wrong (arrow_right: {visual_facing_right}, expected: {expected_arrow_right})")
            return False
    
    print("✓ All drag wall arrow consistency tests passed!")
    return True

if __name__ == "__main__":
    success1 = test_debug_arrow_consistency()
    success2 = test_drag_wall_arrow_consistency()
    
    if success1 and success2:
        print("\n🎉 Debug arrow fix verified!")
    else:
        print("\n❌ Debug arrow fix failed!")
        sys.exit(1) 