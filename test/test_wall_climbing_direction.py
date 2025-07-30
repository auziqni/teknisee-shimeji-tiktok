#!/usr/bin/env python3
"""
Test script to verify wall climbing direction fix
"""
import sys
import os
import time
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet_behavior import DesktopPet
from config import get_config

def test_wall_climbing_direction():
    """Test that sprites face the correct direction when climbing walls"""
    print("Testing wall climbing direction fix...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config = get_config()
    
    # Test scenarios: (wall_side, expected_facing_right, description)
    test_scenarios = [
        ("left", True, "should face right when on left wall"),
        ("right", False, "should face left when on right wall"),
    ]
    
    print("Testing wall climbing directions:")
    
    for wall_side, expected_facing_right, description in test_scenarios:
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
        
        # Check if facing direction is correct
        if pet.facing_right == expected_facing_right:
            print(f"    ✓ {wall_side} wall direction correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ {wall_side} wall direction wrong (facing_right: {pet.facing_right}, expected: {expected_facing_right})")
            return False
        
        # Test CLIMB_WALL state
        pet.change_state(pet.state.__class__.CLIMB_WALL)
        
        # Wait a bit for state to settle
        for i in range(10):
            dt = 1/60.0
            pet.update(dt, (800, 600))
        
        # Check if facing direction is still correct
        if pet.facing_right == expected_facing_right:
            print(f"    ✓ {wall_side} wall climbing direction correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ {wall_side} wall climbing direction wrong (facing_right: {pet.facing_right}, expected: {expected_facing_right})")
            return False
    
    print("✓ All wall climbing direction tests passed!")
    return True

def test_drag_wall_collision_direction():
    """Test that sprites face correct direction when dragged to walls"""
    print("\nTesting drag wall collision direction...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config = get_config()
    
    # Test scenarios: (wall_side, expected_facing_right, description)
    test_scenarios = [
        ("left", True, "should face right when dragged to left wall"),
        ("right", False, "should face left when dragged to right wall"),
    ]
    
    print("Testing drag wall collision directions:")
    
    for wall_side, expected_facing_right, description in test_scenarios:
        print(f"  Testing {wall_side} wall drag collision ({description})...")
        
        # Create pet and simulate drag wall collision
        pet = DesktopPet("Hornet", 400, 300)
        
        # Simulate drag wall collision
        pet._handle_drag_wall_collision(wall_side)
        
        # Check if facing direction is correct
        if pet.facing_right == expected_facing_right:
            print(f"    ✓ {wall_side} wall drag direction correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ {wall_side} wall drag direction wrong (facing_right: {pet.facing_right}, expected: {expected_facing_right})")
            return False
    
    print("✓ All drag wall collision direction tests passed!")
    return True

if __name__ == "__main__":
    success1 = test_wall_climbing_direction()
    success2 = test_drag_wall_collision_direction()
    
    if success1 and success2:
        print("\n🎉 Wall climbing direction fix verified!")
    else:
        print("\n❌ Wall climbing direction fix failed!")
        sys.exit(1) 