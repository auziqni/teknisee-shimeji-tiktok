import pygame
pygame.init()
info = pygame.display.Info()
print(f"Driver: {pygame.display.get_driver()}")
print(f"Depth: {info.bitsize}")
print(f"Masks: {info.masks}")

# Test surface creation
try:
    s = pygame.display.set_mode((100, 100), pygame.SRCALPHA, 32)
    print(f"SRCALPHA flags: {s.get_flags()}")
    print(f"Has alpha: {s.get_flags() & pygame.SRCALPHA}")
except Exception as e:
    print(f"SRCALPHA failed: {e}")