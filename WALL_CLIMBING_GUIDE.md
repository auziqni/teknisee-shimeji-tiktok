# Wall Climbing System Guide

## Overview

The enhanced wall climbing system allows pets to climb walls and stick to them during drag operations. This system integrates with the existing XML animation system and provides realistic physics behavior.

## Features

### 🧗‍♂️ Wall Climbing
- **Automatic Wall Detection**: Pets detect when they hit walls
- **GrabWall Animation**: Pets grab walls before climbing (1 second delay)
- **ClimbWall Animation**: Pets climb walls using XML animations
- **Climbing Duration**: Maximum 8 seconds before getting tired
- **Ceiling Detection**: Pets stop climbing when reaching ceiling

### 🖱️ Drag Wall Interaction
- **Wall Sticking**: Pets stick to walls when dragged past boundaries
- **Boundary Prevention**: Pets cannot be dragged past wall boundaries
- **Wall Release**: Pets release from walls when drag ends
- **Position Clamping**: Automatic position adjustment to stay within bounds

### 🎭 Animation Integration
- **XML Animations**: Uses GrabWall and ClimbWall from actions.xml
- **Proper Facing**: Pets face away from walls during climbing
- **Smooth Transitions**: Seamless state transitions with animations
- **Velocity Integration**: Animation velocity applied during climbing

## How It Works

### Wall Climbing Flow
```
1. Pet hits wall → GrabWall state (1 second)
2. GrabWall → ClimbWall state (8 seconds max)
3. ClimbWall → Fall state (when tired or reaching ceiling)
```

### Drag Wall Interaction Flow
```
1. User drags pet → Mouse motion detection
2. Pet approaches wall → Boundary collision check
3. Pet hits wall → Wall sticking activation
4. User releases drag → Wall release + throw physics
```

## Configuration

### Wall Climbing Settings
```json
{
  "boundaries": {
    "wall_climbing_enabled": true,
    "left_wall_percent": 5,
    "right_wall_percent": 95,
    "ground_percent": 90
  }
}
```

### Physics Parameters
```python
# Wall climbing physics
climb_speed = 30  # pixels per second
max_climb_time = 8.0  # seconds
grab_delay = 1.0  # seconds
```

## User Interactions

### Mouse Controls
- **Left Click + Drag**: Move pet (with wall boundary respect)
- **Right Click**: Trigger special actions (including wall climbing)
- **Double Right Click**: Kill pet

### Wall Climbing Triggers
- **Automatic**: When pet hits wall while not on ground
- **Manual**: Right-click to trigger GrabWall action
- **Drag**: When dragging pet to wall boundary

## Technical Details

### Key Methods
```python
_handle_drag_wall_collision(side)    # Wall sticking during drag
_handle_wall_collision(side, enabled) # Wall collision with climbing
_handle_ground_collision()           # Ground collision handling
handle_mouse_motion(pos)             # Boundary prevention
```

### State Management
```python
PetState.GRAB_WALL   # Grabbing wall (1 second)
PetState.CLIMB_WALL  # Climbing wall (8 seconds max)
```

### Animation Integration
```python
# XML animations used
"GrabWall"  # Wall grabbing animation
"ClimbWall" # Wall climbing animation
```

## Testing

Run the wall climbing test suite:
```bash
python test/test_wall_climbing_enhanced.py
```

## Troubleshooting

### Common Issues

1. **Pets not climbing walls**
   - Check `wall_climbing_enabled` in config
   - Verify XML animations are loaded
   - Ensure pet is not on ground

2. **Drag not respecting boundaries**
   - Verify boundary manager is initialized
   - Check boundary percentages in config
   - Ensure mouse motion handler is working

3. **Animation not playing**
   - Check XML files exist in sprite pack
   - Verify animation manager is loaded
   - Check for animation errors in console

### Debug Information

Enable debug mode to see wall climbing information:
```json
{
  "settings": {
    "debug_mode": true,
    "show_stats": true
  }
}
```

## Performance Notes

- **Collision Detection**: Optimized boundary checking
- **Animation Caching**: Wall climbing animations are cached
- **State Management**: Efficient state transitions
- **Memory Usage**: Proper cleanup of wall climbing states

## Future Enhancements

- **Multi-wall Climbing**: Climb between different walls
- **Wall Jumping**: Jump from one wall to another
- **Ceiling Climbing**: Climb on ceilings
- **Wall Sliding**: Slide down walls
- **Wall Interaction**: Interact with wall-mounted objects 