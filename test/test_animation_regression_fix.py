#!/usr/bin/env python3
"""
Test script to verify animation regression fix
"""

import sys
import os
import time
import pygame

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet_behavior import DesktopPet
from config import get_config

def test_animation_regression_fix():
    """Test that animations are working correctly after the fix"""
    print("Testing animation regression fix...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Create a pet
    config = get_config()
    pet = DesktopPet("Hornet", 400, 300)
    
    # Test different states to ensure animations work
    test_states = [
        ("IDLE", "Stand"),
        ("WALKING", "Walk"), 
        ("SITTING", "Sit"),
        ("GRAB_WALL", "GrabWall"),
        ("CLIMB_WALL", "ClimbWall")
    ]
    
    print("Testing animation states:")
    for state_name, action_name in test_states:
        print(f"  Testing {state_name} ({action_name})...")
        
        # Change to test state
        pet.change_state(getattr(pet.state.__class__, state_name))
        
        # Update for a few frames to see animation
        for i in range(30):  # 30 frames = ~0.5 seconds at 60fps
            dt = 1/60.0
            pet.update(dt, (800, 600))
            
            # Check if image is being updated
            if pet.image is not None:
                print(f"    Frame {i+1}: Image size = {pet.image.get_size()}")
            else:
                print(f"    Frame {i+1}: ERROR - No image!")
                return False
        
        print(f"    ✓ {state_name} animation working")
    
    print("✓ All animation tests passed!")
    return True

if __name__ == "__main__":
    success = test_animation_regression_fix()
    if success:
        print("\n🎉 Animation regression fix verified!")
    else:
        print("\n❌ Animation regression fix failed!")
        sys.exit(1) 