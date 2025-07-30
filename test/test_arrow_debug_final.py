#!/usr/bin/env python3
"""
Test script to verify final arrow debug fix
"""
import sys
import os
import time
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet_behavior import DesktopPet
from config import get_config

def test_normal_movement_arrow():
    """Test that arrow shows correct direction during normal movement"""
    print("Testing normal movement arrow direction...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config = get_config()
    
    # Test scenarios: (facing_right, expected_arrow_right, description)
    test_scenarios = [
        (True, True, "arrow should point right when sprite faces right"),
        (False, False, "arrow should point left when sprite faces left"),
    ]
    
    print("Testing normal movement arrow directions:")
    
    for facing_right, expected_arrow_right, description in test_scenarios:
        print(f"  Testing {description}...")
        
        # Create pet
        pet = DesktopPet("Hornet", 400, 300)
        pet.facing_right = facing_right
        
        # Simulate normal movement state
        pet.change_state(pet.state.__class__.WALKING)
        
        # Wait a bit for state to settle
        for i in range(10):
            dt = 1/60.0
            pet.update(dt, (800, 600))
        
        # Check if arrow direction is correct
        # For normal movement, arrow should match facing_right
        if pet.facing_right == expected_arrow_right:
            print(f"    ✓ Normal movement arrow correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ Normal movement arrow wrong (facing_right: {pet.facing_right}, expected: {expected_arrow_right})")
            return False
    
    print("✓ All normal movement arrow tests passed!")
    return True

def test_wall_climbing_arrow():
    """Test that arrow shows correct direction during wall climbing"""
    print("\nTesting wall climbing arrow direction...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config_manager = get_config()
    
    # Test scenarios: (wall_side, expected_arrow_right, description)
    test_scenarios = [
        ("left", False, "arrow should point left when on left wall (facing toward wall)"),
        ("right", True, "arrow should point right when on right wall (facing toward wall)"),
    ]
    
    print("Testing wall climbing arrow directions:")
    
    for wall_side, expected_arrow_right, description in test_scenarios:
        print(f"  Testing {wall_side} wall climbing ({description})...")
        
        # Create pet and simulate wall collision
        pet = DesktopPet("Hornet", 400, 300)
        
        # Create a mock boundary manager for testing
        from gui_manager import BoundaryManager
        boundary_manager = BoundaryManager(800, 600, config_manager)
        pet.set_boundary_manager(boundary_manager)
        
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
        
        # Check if arrow direction is correct for wall climbing
        # For wall climbing, sprite should face toward wall
        if wall_side == 'left' and pet.facing_right == False:
            print(f"    ✓ {wall_side} wall arrow correct (facing_right: {pet.facing_right})")
        elif wall_side == 'right' and pet.facing_right == True:
            print(f"    ✓ {wall_side} wall arrow correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ {wall_side} wall arrow wrong (facing_right: {pet.facing_right}, expected: {expected_arrow_right})")
            return False
        
        # Test CLIMB_WALL state
        pet.change_state(pet.state.__class__.CLIMB_WALL)
        
        # Wait a bit for state to settle
        for i in range(10):
            dt = 1/60.0
            pet.update(dt, (800, 600))
        
        # Check if arrow direction is still correct
        if wall_side == 'left' and pet.facing_right == False:
            print(f"    ✓ {wall_side} wall climbing arrow correct (facing_right: {pet.facing_right})")
        elif wall_side == 'right' and pet.facing_right == True:
            print(f"    ✓ {wall_side} wall climbing arrow correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ {wall_side} wall climbing arrow wrong (facing_right: {pet.facing_right}, expected: {expected_arrow_right})")
            return False
    
    print("✓ All wall climbing arrow tests passed!")
    return True

def test_drag_wall_arrow():
    """Test that arrow shows correct direction when dragged to walls"""
    print("\nTesting drag wall arrow direction...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    config_manager = get_config()
    
    # Test scenarios: (wall_side, expected_arrow_right, description)
    test_scenarios = [
        ("left", False, "arrow should point left when dragged to left wall (facing toward wall)"),
        ("right", True, "arrow should point right when dragged to right wall (facing toward wall)"),
    ]
    
    print("Testing drag wall arrow directions:")
    
    for wall_side, expected_arrow_right, description in test_scenarios:
        print(f"  Testing {wall_side} wall drag ({description})...")
        
        # Create pet and simulate drag wall collision
        pet = DesktopPet("Hornet", 400, 300)
        
        # Create a mock boundary manager for testing
        from gui_manager import BoundaryManager
        boundary_manager = BoundaryManager(800, 600, config_manager)
        pet.set_boundary_manager(boundary_manager)
        
        # Simulate drag wall collision
        pet._handle_drag_wall_collision(wall_side)
        
        # Check if arrow direction is correct for drag wall
        if wall_side == 'left' and pet.facing_right == False:
            print(f"    ✓ {wall_side} wall drag arrow correct (facing_right: {pet.facing_right})")
        elif wall_side == 'right' and pet.facing_right == True:
            print(f"    ✓ {wall_side} wall drag arrow correct (facing_right: {pet.facing_right})")
        else:
            print(f"    ❌ {wall_side} wall drag arrow wrong (facing_right: {pet.facing_right}, expected: {expected_arrow_right})")
            return False
    
    print("✓ All drag wall arrow tests passed!")
    return True

if __name__ == "__main__":
    success1 = test_normal_movement_arrow()
    success2 = test_wall_climbing_arrow()
    success3 = test_drag_wall_arrow()
    
    if success1 and success2 and success3:
        print("\n🎉 Arrow debug fix verified!")
    else:
        print("\n❌ Arrow debug fix failed!")
        sys.exit(1) 