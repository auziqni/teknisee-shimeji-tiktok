#!/usr/bin/env python3
"""
Test script to verify direction fix
"""

import sys
import os
import time
import pygame

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet_behavior import DesktopPet
from config import get_config

def test_direction_fix():
    """Test that sprites move in the correct direction based on facing_right"""
    print("Testing direction fix...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create a pet
    config = get_config()
    pet = DesktopPet("Hornet", 400, 300)

    # Test scenarios
    test_scenarios = [
        ("LEFT", False, "should move left"),
        ("RIGHT", True, "should move right"),
    ]

    print("Testing movement directions:")
    for direction_name, facing_right, description in test_scenarios:
        print(f"  Testing {direction_name} movement ({description})...")

        # Set the pet's facing direction
        pet.facing_right = facing_right
        if pet.animation_manager:
            try:
                pet.animation_manager.set_facing_direction(not facing_right)
            except Exception as e:
                print(f"    Error setting animation direction: {e}")

        # Start walking
        pet.change_state(pet.state.__class__.WALKING)
        pet.target_x = pet.x + (100 if facing_right else -100)
        pet.walk_duration = 2.0
        pet.walk_start_time = 0.0

        # Track initial position
        initial_x = pet.x
        initial_velocity = pet.velocity_x

        # Update for a few frames to see movement
        for i in range(60):  # 60 frames = ~1 second at 60fps
            dt = 1/60.0
            pet.update(dt, (800, 600))

            # Check if velocity is in the correct direction
            if i > 10:  # Wait a few frames for animation to start
                if facing_right and pet.velocity_x < 0:
                    print(f"    ERROR: Facing right but moving left (velocity_x: {pet.velocity_x:.2f})")
                    return False
                elif not facing_right and pet.velocity_x > 0:
                    print(f"    ERROR: Facing left but moving right (velocity_x: {pet.velocity_x:.2f})")
                    return False

            if i % 20 == 0:  # Log every 20 frames
                print(f"    Frame {i+1}: x={pet.x:.1f}, velocity_x={pet.velocity_x:.2f}, facing_right={pet.facing_right}")

        # Check final position
        final_x = pet.x
        movement = final_x - initial_x
        
        if facing_right and movement < 0:
            print(f"    ERROR: Facing right but moved left (movement: {movement:.1f})")
            return False
        elif not facing_right and movement > 0:
            print(f"    ERROR: Facing left but moved right (movement: {movement:.1f})")
            return False

        print(f"    ✓ {direction_name} movement working correctly (movement: {movement:.1f})")

    print("✓ All direction tests passed!")
    return True

if __name__ == "__main__":
    success = test_direction_fix()
    if success:
        print("\n🎉 Direction fix verified!")
    else:
        print("\n❌ Direction fix failed!")
        sys.exit(1) 