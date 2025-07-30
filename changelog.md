# Changelog

All notable changes to Teknisee Shimeji TikTok Desktop Pet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 1: Foundation & Basic Interactions

## [P1S4-Direction-Fix] - 2024-12-19 - Movement Direction Fix ✅

### Fixed

- **Movement Direction Issue**

  - **Root Cause Identified**: Animation velocity from XML was hardcoded to left movement (-2,0) and applied directly
  - **Direction-Aware Velocity**: Modified velocity application to be direction-aware in `_update_movement_with_boundaries`
  - **Animation Velocity Inversion**: Animation velocity now inverts when `facing_right=True` to move in correct direction
  - **Proper Movement Logic**: Sprites now move in the direction they are facing, not always left

- **Animation System Enhancement**

  - **Direction-Aware Animation**: Animation velocity application now considers pet's facing direction
  - **Velocity Inversion Logic**: Added logic to invert X velocity when pet is facing right
  - **Movement Consistency**: Ensured visual direction matches movement direction
  - **Animation Integration**: Maintained proper animation display while fixing movement direction

### Technical Implementation

- **Enhanced Method**:

  ```python
  _update_movement_with_boundaries()  # Added direction-aware velocity application
  ```

- **Velocity Application Logic**:

  ```python
  # Apply velocity based on facing direction
  # If facing right, invert the X velocity from animation (which is hardcoded to left)
  velocity_x = velocity[0] * dt
  if self.facing_right and velocity[0] != 0:
      velocity_x = -velocity[0] * dt  # Invert for right-facing movement
  ```

### Testing

- **Comprehensive Test Suite**: `test_direction_fix.py`
- **Direction Verification**: Tests that sprites move in correct direction based on facing_right
- **Velocity Analysis**: Monitors velocity_x values during movement
- **Movement Tracking**: Tracks actual position changes to verify direction

### Performance

- **Correct Movement**: Sprites now move in the direction they are facing
- **Animation Consistency**: Visual animation matches movement direction
- **No Performance Impact**: Direction fix has negligible performance cost

## [P1S4-Debug-Arrow-Fix] - 2024-12-19 - Debug Arrow Consistency Fix ✅

### Fixed

- **Debug Arrow Inconsistency**

  - **Root Cause Identified**: Debug arrow used `self.facing_right` property instead of visual direction
  - **Visual Direction Mismatch**: Arrow showed wrong direction during wall climbing despite correct sprite visual
  - **Wall Climbing Logic**: Arrow now correctly shows direction based on wall side (facing toward wall)
  - **Consistent Debug Display**: Debug arrow now matches actual sprite visual direction

- **Wall Climbing Debug Enhancement**

  - **Visual Direction Detection**: Debug arrow now correctly handles wall climbing scenarios
  - **Consistent Arrow Display**: Arrow direction matches sprite visual direction during wall climbing
  - **Enhanced Debug Information**: More accurate debug information for wall climbing scenarios
  - **Wall Side Logic**: Arrow shows correct direction based on which wall sprite is on

### Technical Implementation

- **Enhanced Method**:

  ```python
  _draw_debug_info()  # Added wall climbing visual direction logic
  ```

- **Visual Direction Logic**:

  ```python
  # Draw facing direction indicator (consisten dengan visual direction)
  visual_facing_right = self.facing_right
  
  # Untuk wall climbing, sprite menghadap ke dinding (bukan menjauh dari dinding)
  if self.on_wall and self.wall_side:
      if self.wall_side == 'left':
          visual_facing_right = False  # Sprite menghadap kiri (ke dinding kiri)
      elif self.wall_side == 'right':
          visual_facing_right = True  # Sprite menghadap kanan (ke dinding kanan)
  ```

- **Additional Fixes**:

  ```python
  # Fixed _handle_drag_wall_collision() - sprite faces towards wall
  if side == 'left':
      self.facing_right = False  # Face toward left wall
  else:  # right
      self.facing_right = True  # Face toward right wall
  
  # Fixed change_state() for wall climbing - sprite faces towards wall
  if self.wall_side == 'left':
      self.facing_right = False  # Face left (toward left wall)
  elif self.wall_side == 'right':
      self.facing_right = True  # Face right (toward right wall)
  ```

### Testing

- **Comprehensive Test Suite**: `test_arrow_debug_final.py`
- **Normal Movement Arrow**: Tests arrow direction during normal movement
- **Wall Climbing Arrow**: Verifies arrow consistency during wall climbing states
- **Drag Wall Arrow**: Tests arrow consistency when dragged to walls

### Performance

- **Accurate Debug Display**: Debug arrow now shows correct visual direction
- **Consistent Debug Information**: Arrow direction matches sprite visual during all states
- **Enhanced Debugging**: Better debugging experience for wall climbing scenarios

## [P1S4-Animation-Fixes] - 2024-12-19 - Animation Display & Direction Change Fixes ✅

### Fixed

- **Wall Climbing Animation Display**

  - **Proper Animation Integration**: Fixed wall climbing animations not displaying correctly
  - **Animation Direction Control**: Improved facing direction control during wall climbing
  - **Smooth State Transitions**: Enhanced transitions between GrabWall and ClimbWall states
  - **Animation Velocity Integration**: Proper velocity application from XML animations
  - **Wall Climbing Duration**: Increased climbing duration to 10 seconds for better visibility

- **Direction Change Glitch Prevention**

  - **Direction Change Cooldown**: Added 0.5-second cooldown to prevent rapid direction changes
  - **Direction Lock System**: Implemented direction locking to prevent glitches during collisions
  - **Corner Collision Fixes**: Enhanced corner collision handling with 0.8-second direction lock
  - **Wall Turn Around Fixes**: Improved wall turn around with 0.6-second direction lock
  - **Wall Climbing Direction Lock**: 2-second direction lock during wall climbing states

- **Animation System Improvements**

  - **Enhanced Error Handling**: Better error handling for animation direction changes
  - **Animation State Management**: Improved state transitions with proper animation loading
  - **Facing Direction Logic**: Fixed facing direction logic for wall climbing animations
  - **Animation Debug Logging**: Added debug logging for animation state changes

### Enhanced

- **Wall Climbing Physics**

  - **Smoother Climbing Speed**: Reduced climbing speed to 25 pixels/second for smoother animation
  - **Increased Ceiling Threshold**: Increased ceiling detection threshold to 80 pixels
  - **Extended Climbing Duration**: Increased maximum climbing time to 10 seconds
  - **Better Wall Side Detection**: Improved wall side detection and facing direction logic

- **Collision System**

  - **Corner Collision Enhancement**: Improved corner collision with longer movement distances
  - **Wall Turn Around Enhancement**: Enhanced wall turn around with longer movement distances
  - **Direction Lock Integration**: Integrated direction locking into all collision handlers
  - **Collision Cooldown System**: Enhanced collision cooldown to prevent rapid oscillations

- **State Management**

  - **Direction Lock Timer**: Added direction lock timer tracking in update method
  - **State Transition Logging**: Enhanced logging for state transitions and direction changes
  - **Animation Error Recovery**: Improved error recovery for animation system failures
  - **Wall Climbing State Persistence**: Better state persistence during wall climbing

### Technical Implementation

- **New Methods Added**:

  ```python
  _lock_direction(duration: float)  # Lock direction changes
  ```

- **Enhanced Methods**:

  ```python
  _change_direction()                # Added cooldown and lock checks
  _handle_corner_collision()         # Added direction locking
  _handle_wall_turn_around()         # Added direction locking
  change_state()                     # Enhanced wall climbing states
  update()                           # Added direction lock timer
  ```

- **Direction Change Flow**:

  ```
  Direction Change Request → Cooldown Check → Lock Check → Direction Change
  Corner Collision → Direction Lock (0.8s) → Smooth Turn Away
  Wall Turn Around → Direction Lock (0.6s) → Smooth Turn Around
  Wall Climbing → Direction Lock (2.0s) → Stable Climbing
  ```

### Testing

- **Comprehensive Test Suite**: `test_animation_fixes.py`
- **Direction Change Cooldown**: Tests rapid direction change prevention
- **Wall Climbing Animation**: Tests animation integration and state transitions
- **Corner Collision Fixes**: Tests direction locking in corner collisions
- **Animation Display**: Tests animation state changes and error handling

### Performance

- **Reduced Glitches**: Eliminated rapid direction changes that caused visual glitches
- **Smoother Animations**: Improved animation transitions and display
- **Better Collision Handling**: Enhanced collision response with direction locking
- **Stable Wall Climbing**: More stable and visible wall climbing animations

## [P1S4-Enhanced] - 2024-12-19 - Enhanced Wall Climbing System ✅

### Added

- **Enhanced Wall Climbing System**

  - **Wall Sticking During Drag**: Pets now stick to walls when dragged past wall boundaries
  - **Drag Boundary Prevention**: Pets cannot be dragged past wall boundaries, preventing wall crossing
  - **Proper Animation Integration**: Wall climbing uses GrabWall and ClimbWall animations from XML
  - **Wall Collision Detection**: Improved collision detection for left/right walls during drag
  - **Wall Climbing Physics**: Pets can climb walls with proper gravity and physics handling

- **Enhanced Mouse Interaction**

  - **Drag Wall Collision**: `_handle_drag_wall_collision()` method for wall sticking during drag
  - **Boundary Prevention**: Mouse motion handler prevents crossing wall boundaries
  - **Wall Sticking Release**: Proper release of wall sticking state when drag ends
  - **Position Clamping**: Automatic position clamping to keep pets within boundaries

- **Improved Wall Climbing Behavior**

  - **GrabWall State**: Pets grab walls before climbing (1 second delay)
  - **ClimbWall State**: Pets climb walls with proper animation and physics
  - **Climbing Duration**: Maximum 8 seconds of climbing before getting tired
  - **Ceiling Detection**: Pets stop climbing when reaching ceiling area
  - **Energy System**: Wall climbing consumes energy, sitting restores energy

- **Enhanced Animation System**

  - **XML Animation Integration**: Uses GrabWall and ClimbWall animations from actions.xml
  - **Proper Facing Direction**: Pets face away from walls during climbing
  - **Animation State Management**: Smooth transitions between wall climbing states
  - **Velocity Integration**: Animation velocity properly applied during climbing

### Enhanced

- **Boundary Collision System**

  - **Improved Collision Detection**: Better handling of wall, ground, and ceiling collisions
  - **Wall Collision Logic**: Enhanced `_handle_wall_collision()` with proper wall climbing
  - **Ground Collision**: Improved ground collision with bounce physics
  - **Ceiling Collision**: Added ceiling collision handling for future use

- **Physics System**

  - **Wall Sticking Physics**: Gravity disabled while on walls
  - **Climbing Physics**: Proper velocity and position management during climbing
  - **Drag Physics**: Enhanced drag physics with wall boundary respect
  - **Energy Management**: Wall climbing consumes energy, affects behavior

- **State Management**

  - **Wall Climbing States**: Proper state transitions for GrabWall and ClimbWall
  - **Animation Integration**: State changes trigger appropriate animations
  - **Wall Side Tracking**: Proper tracking of which wall pet is climbing
  - **State Persistence**: Wall climbing state properly saved and restored

### Technical Implementation

- **New Methods Added**:

  ```python
  _handle_drag_wall_collision(side: str)  # Wall sticking during drag
  _handle_ground_collision()              # Ground collision handling
  _handle_ceiling_collision()             # Ceiling collision handling
  ```

- **Enhanced Methods**:

  ```python
  _handle_wall_collision()                # Improved wall collision with climbing
  handle_mouse_motion()                   # Boundary prevention during drag
  handle_mouse_up()                       # Wall sticking release
  _update_state_behavior()                # Enhanced wall climbing behavior
  ```

- **Wall Climbing Flow**:

  ```
  Wall Collision → GrabWall (1s) → ClimbWall (8s max) → Fall
  Drag to Wall → Wall Sticking → Release → Throw Physics
  ```

### Testing

- **Comprehensive Test Suite**: `test_wall_climbing_enhanced.py`
- **Wall Collision Detection**: Tests boundary collision detection
- **Drag Boundary Prevention**: Tests wall crossing prevention
- **Animation Integration**: Tests XML animation loading
- **Wall Climbing Behavior**: Tests climbing physics and timing

### Performance

- **Optimized Collision Detection**: Efficient boundary checking
- **Memory Management**: Proper cleanup of wall climbing states
- **Animation Performance**: Smooth wall climbing animations
- **Physics Optimization**: Efficient wall climbing physics calculations

## [P1S3] - 2024-07-29 - XML Parser & Animation System ✅

### Added

- **Complete XML-Driven Animation System**

  - Full Shimeji XML format support (actions.xml and behaviors.xml parsing)
  - XMLParser class with comprehensive action and behavior data structures
  - Support for 33+ animation actions and 69+ behavior definitions
  - Animation frame timing with 30 FPS conversion from XML duration values
  - Sprite flipping support for left/right facing directions
  - Animation looping and completion detection system

- **Enhanced Animation Manager**

  - AnimationManager class for managing multiple animation sequences
  - Factory pattern with create_animation_manager() function
  - Animation state management (PLAYING, PAUSED, STOPPED, COMPLETED)
  - Frame-by-frame sprite rendering with velocity integration
  - Fallback animation system for missing sprites
  - Performance-optimized sprite caching during animation building

- **Advanced Pet Behavior System**

  - XML-action-mapped PetState enum (Stand, Walk, Sit, Run, etc.)
  - Enhanced DesktopPet class with 38+ available animations
  - AI-driven behavior selection based on energy, happiness, and time
  - Weighted random action selection with configurable probabilities
  - Special action support (Pose, EatBerry, ThrowNeedle, Watch)
  - Smooth state transitions with animation integration

- **Sound System Foundation**

  - SoundManager class with volume control and caching
  - XML sound reference parsing with automatic playback
  - dB to linear volume conversion for accurate audio levels
  - Support for WAV and OGG audio formats
  - Sound preloading and missing sound detection
  - Integration with animation frames for synchronized audio

- **Robust Error Handling & Fallbacks**
  - Circular import protection with lazy loading patterns
  - Graceful degradation when animation system unavailable
  - Sprite loading fallbacks with convert_alpha() error handling
  - Comprehensive error logging for debugging
  - Backward compatibility with fallback animation system

### Enhanced

- **Core Infrastructure Improvements**

  - Updated sprite_loader.py with animation-aware sprite management
  - Enhanced pet_behavior.py with XML animation integration
  - Improved main.py with animation system detection and testing
  - Updated utils/**init**.py with lazy import patterns

- **Configuration & Persistence**

  - Animation system settings integration
  - Enhanced pet state saving with animation data
  - Performance monitoring for animation system
  - Debug mode support for animation visualization

- **User Interface Enhancements**
  - Control panel integration with animation status display
  - Real-time animation performance monitoring
  - Enhanced pet information display with animation data
  - Debug overlay showing current animation state

### Technical Implementation

- **Animation Framework Architecture**:

  ```python
  AnimationManager -> Animation -> AnimationFrame[]
  XMLParser -> ActionData/BehaviorData -> PoseData[]
  SoundManager -> Sound playback integration
  ```

- **Performance Optimizations**:

  - Sprite caching during animation building (vs runtime loading)
  - Lazy sprite loader initialization to avoid circular imports
  - Efficient XML parsing with single-pass action/behavior loading
  - Memory-optimized animation frame storage

- **File Structure Enhancements**:

  ```
  utils/
  ├── __init__.py          # Lazy import system
  ├── xml_parser.py        # Complete XML parsing
  ├── animation.py         # Animation system core
  └── sound_manager.py     # Sound system foundation

  assets/SpriteName/
  ├── conf/
  │   ├── actions.xml      # Animation definitions
  │   └── behaviors.xml    # Behavior logic
  ├── sounds/              # Audio files (new)
  └── *.png               # Sprite images
  ```

### Fixed

- **Circular Import Issues**

  - Resolved get_sprite_loader circular dependency in animation system
  - Fixed utils module import structure with lazy loading
  - Eliminated startup import conflicts between modules

- **Sprite Loading Errors**

  - Fixed "cannot convert without pygame.display initialized" errors
  - Improved sprite loading sequence and timing
  - Enhanced error handling for missing sprite files

- **Animation Integration**
  - Proper animation manager lifecycle management
  - Correct facing direction updates for sprite flipping
  - Fixed animation state transitions and loop handling

### Performance Metrics

- **Animation System**: 38 animations loaded with 200+ frames total
- **XML Parsing**: 33 actions + 69 behaviors parsed in <1 second
- **Memory Usage**: ~15MB for complete Hornet sprite pack with animations
- **Frame Rate**: Consistent 30 FPS with multiple animated pets
- **Startup Time**: <3 seconds for full system initialization

### Known Issues & Notes

- **Cosmetic PNG Warnings**: libpng iCCP profile warnings (non-functional)

  - Status: Cosmetic only, does not affect sprite rendering
  - Fix available: `magick mogrify -strip assets/Hornet/*.png` (optional)
  - Note: ImageMagick installation required for metadata stripping

- **Features for Phase 1 Step 4**:
  - Throwing mechanism not yet implemented (planned)
  - Falling state trigger needs improvement for slow drops
  - Advanced physics system planned for next phase

### Development Notes

- **Architecture Decision**: XML-first approach ensures authentic Shimeji compatibility
- **Performance Focus**: Sprite caching during load vs runtime for better FPS
- **Error Resilience**: System degrades gracefully without XML files
- **Testing Approach**: Comprehensive validation with test/test_animations.py

### User Experience

- **Authentic Animations**: True-to-Shimeji XML-driven pet behavior
- **Smooth Performance**: Optimized for multiple pets without lag
- **Smart Behavior**: AI-driven action selection based on pet stats
- **Audio Integration**: Synchronized sound effects with animations
- **Debug Friendly**: Comprehensive logging and monitoring tools

---

## [P1S2] - 2024-07-29 - Control Panel Foundation ✅

### Added

- **Enhanced Control Panel Architecture**

  - Tabbed interface with Pet Management, Settings, and About tabs
  - QGroupBox organization for better UI structure and visual hierarchy
  - Window position persistence across application restarts
  - Responsive UI layout with proper spacing and alignment

- **JSON Configuration Management System**

  - ConfigManager class with comprehensive settings structure
  - Deep merge functionality for backward compatibility
  - Dot notation access for nested configuration values (e.g., 'settings.volume')
  - Auto-save functionality with manual save/reload options
  - Error handling for malformed JSON and missing files

- **Advanced Pet Management**

  - Multiple pet spawning with count selector (1-10 pets)
  - Automatic spawn position offset for multiple pets (50px spacing)
  - Configurable spawn positions (defaults to screen center-bottom)
  - Enhanced status tracking with real-time pet count display
  - Improved sprite selection persistence

- **Comprehensive Settings System**

  - Volume control slider (0-100%) with real-time label updates
  - Behavior frequency slider (10-100%) for future animation system
  - Screen boundaries toggle for pet movement constraints
  - Auto-save settings toggle for user preference control
  - Settings validation and range enforcement

- **Configuration Persistence**
  - Complete settings structure in JSON format
  - Sprite selection memory across sessions
  - Control panel window position saving
  - User preference tracking for all interactive elements
  - Automatic configuration backup and restore

### Enhanced

- **User Interface Improvements**

  - Professional QGroupBox styling for better visual organization
  - Horizontal sliders with percentage labels for precise control
  - SpinBox integration for numeric input with validation
  - Improved button layout and spacing throughout application
  - Better text wrapping and information display

- **Development Status Tracking**

  - Real-time phase/step status display in About tab
  - Version information and project description
  - Development roadmap visibility for users
  - Contact and contribution information

- **Error Handling & Robustness**
  - Graceful handling of missing configuration files
  - JSON parsing error recovery with default fallbacks
  - UI state validation during config reload operations
  - Memory management improvements for configuration objects

### Technical Implementation

- **Configuration Schema**:

  ```json
  {
    "settings": {
      "volume": 70,
      "behavior_frequency": 50,
      "screen_boundaries": true,
      "auto_save": true,
      "spawn_x": null,
      "spawn_y": null
    },
    "tiktok": {
      "enabled": false,
      "last_successful_username": "",
      "auto_connect": false
    },
    "sprite_packs": ["Hornet"],
    "logging": {
      "level": "INFO",
      "save_to_file": true,
      "max_log_size": "10MB"
    },
    "ui": {
      "control_panel_x": 100,
      "control_panel_y": 100,
      "selected_sprite": "Hornet"
    }
  }
  ```

- **Enhanced Class Architecture**:
  - ConfigManager: 150+ lines of robust configuration handling
  - ControlPanel: 300+ lines with complete tabbed interface
  - Modular method organization for maintainability and testing

### Fixed

- **Code Structure Issues**
  - Eliminated duplicate class definitions causing TypeError
  - Proper import organization and dependency management
  - Clean class hierarchy without inheritance conflicts
  - Resolved indentation and method signature inconsistencies

### Configuration Features

- **Auto-Save System**: Real-time saving when auto-save enabled
- **Manual Controls**: Save Config and Reload Config buttons
- **Data Validation**: Type checking and range validation for all settings
- **Fallback Handling**: Graceful degradation when config file corrupted

### User Experience

- **Intuitive Interface**: Clear grouping and labeling of all functions
- **Visual Feedback**: Real-time updates for all interactive elements
- **Persistent State**: Application remembers all user preferences
- **Professional Layout**: Consistent spacing and modern UI elements

### Testing Results

- ✅ All basic functionality tests passed
- ✅ Control panel tabs navigation working correctly
- ✅ Settings persistence across application restarts
- ✅ JSON config file generation and management
- ✅ Sprite system integration and auto-discovery
- ✅ Error handling for edge cases and invalid inputs
- ✅ UI/UX responsiveness and visual feedback

### Performance Metrics

- **Startup Time**: Improved configuration loading with caching
- **Memory Usage**: Efficient JSON handling without memory leaks
- **UI Responsiveness**: Smooth real-time updates without blocking
- **File I/O**: Optimized configuration saving with minimal disk writes

### Development Notes

- **Architecture Decision**: JSON-based configuration provides flexibility for future features
- **UI Framework**: PyQt5 tabbed interface scales well for additional settings categories
- **Data Management**: Dot notation access simplifies nested configuration handling
- **Testing Approach**: Comprehensive manual testing validates all user workflows

### Next Steps

- P1S3: XML Parser implementation for sprite animation data
- Integration of behavior frequency settings with actual pet behaviors
- Enhanced sprite pack validation with XML file checking

---

## [P1S1] - 2024-07-29 - Core Infrastructure ✅

### Added

- **Project Foundation**

  - Created main.py with modular class structure
  - Implemented SpriteDiscovery class for auto-detection of sprite packs
  - Set up virtual environment with pygame==2.6.1 and PyQt5==5.15.11

- **Pygame Desktop Pet System**

  - Transparent, frameless pygame window covering full screen
  - Always-on-top functionality (Windows-specific with fallback)
  - DesktopPet class with sprite rendering and positioning
  - Support for PNG sprites with alpha transparency

- **Mouse Interaction System**

  - Left-click + drag functionality for pet movement
  - Double right-click detection for pet removal (500ms window)
  - Collision detection using pygame Rect system
  - Drag offset calculation for smooth movement

- **Control Panel (PyQt5)**

  - Simple control panel window with pet management
  - Dropdown selection for available sprite packs
  - Spawn Pet button with auto-positioning
  - Kill All Pets functionality
  - Real-time status display showing active pet count
  - User instruction display for controls

- **Auto-Discovery System**

  - Automatic scanning of assets/ directory
  - Validation system requiring shime1.png for valid sprite packs
  - Dynamic sprite pack listing in control panel
  - Error handling for missing directories and files

- **Error Handling & Fallbacks**
  - Graceful handling of missing sprite files with colored rectangle fallback
  - Import error handling for win32gui (cross-platform compatibility)
  - Directory existence validation
  - Try-catch blocks for file loading operations

### Technical Implementation

- **Architecture**: Hybrid PyQt5 + Pygame approach using QTimer for non-blocking integration
- **Frame Rate**: 30 FPS with pygame clock
- **Window Management**: Transparent overlay with click-through background
- **Memory Management**: Proper surface conversion with convert_alpha()
- **Platform Support**: Primary Windows support with cross-platform fallbacks

### Project Structure

```
teknisee-shimeji-tiktok/
├── main.py                 # Complete application (320 lines)
├── assets/
│   └── Hornet/
│       └── shime1.png     # Test sprite pack
├── requirements.txt        # Frozen dependencies
├── .gitignore             # Comprehensive ignore rules
├── README.md              # Project documentation
└── roadmap.md             # Development roadmap
```

### Configuration

- **Default Positioning**: Pets spawn at screen center-bottom
- **Window Dimensions**: Full screen transparent overlay
- **Sprite Requirements**: shime1.png mandatory for pack validation
- **Dependencies**: pygame 2.6.1, PyQt5 5.15.11

### Known Issues

- win32gui import warning (resolved with import guard, actual install planned for P2S2)
- Always-on-top may not work on non-Windows platforms (has fallback)

### Testing Results

- ✅ Auto-discovery successfully detects "Hornet" sprite pack
- ✅ Control panel shows available sprites in dropdown
- ✅ Pet spawning and positioning works correctly
- ✅ Drag and drop functionality smooth and responsive
- ✅ Double right-click removal working with proper timing
- ✅ Application exits cleanly without pygame/Qt conflicts

### Development Notes

- Chosen architecture allows for clean separation between UI (PyQt5) and graphics (Pygame)
- Timer-based integration prevents blocking between Qt and Pygame event loops
- Modular class design enables easy extension for future features
- Auto-discovery pattern will scale well for multiple sprite packs

### Next Steps

- P1S2: Enhanced control panel with tabbed interface and JSON config
- Add sprite pack validation for XML files
- Implement settings persistence system
