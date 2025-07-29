# Changelog

All notable changes to Teknisee Shimeji TikTok Desktop Pet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 1: Foundation & Basic Interactions

#### [P1S2] - Control Panel Foundation - In Progress

- TODO: Enhanced control panel with tabs
- TODO: JSON config save/load system
- TODO: Settings persistence

#### [P1S3] - XML Parser & Animation System - Planned

- TODO: XML parser for actions.xml and behaviors.xml
- TODO: Animation frame management system
- TODO: Multi-frame sprite animations

#### [P1S4] - Desktop Boundaries & Physics - Planned

- TODO: Screen boundary detection
- TODO: Gravity and collision system
- TODO: Random behavior selection

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
