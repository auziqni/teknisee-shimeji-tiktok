# Shimeji Desktop Pet - Development Roadmap

## Project Overview

**Goal**: Create a desktop pet application similar to Shimeji with TikTok Live integration and window interaction capabilities.

**Target Platform**: Windows  
**Development Approach**: MVP (Minimum Viable Product) for each phase and step  
**Frame Rate**: 30 FPS  
**Sprite Size**: 128x128 px with transparency

## Core Features

### Essential Features

- Desktop pet with various animations and behaviors
- Speech bubble system (text display for 10 seconds)
- TikTok Live integration for real-time chat interaction
- Multiple sprite support from DeviantArt format
- XML-based configuration system
- Panel control for settings and management
- Window interaction capabilities

### User Interactions

- **Left-click + Drag**: Move sprite
- **Double right-click**: Kill individual sprite
- **Panel control**: Spawn new pets, adjust settings, TikTok connection

### TikTok Integration

- **Standalone Operation**: Application runs independently without TikTok
- **Optional Connection**: Username input through control panel for TikTok Live
- **Automatic Persistence**: Successful usernames saved to config.json
- **Error Handling**: Connection failures logged without breaking functionality
- **Real-time Response**: Chat messages trigger pet behaviors and speech bubbles

## Technical Stack

### Core Technologies

- **Python** with virtual environment
- **Pygame** for sprite rendering and animation
- **PyQt5** for control panel UI
- **TikTokLive library** for chat integration
- **XML parsing** for sprite configurations
- **JSON** for settings storage
- **Windows API** for window interaction

### Dependencies

```python
pygame
PyQt5
TikTokLive  # https://github.com/isaackogan/TikTokLive
win32gui (pywin32)  # for window interaction
```

## File Structure

```
shimeji_desktop/
├── main.py                 # Main application entry
├── config.py              # Hardcoded settings and constants
├── sprite_loader.py       # XML parsing and sprite loading
├── pet_behavior.py        # Behavior logic and state management
├── tiktok_integration.py  # TikTok Live connection and events
├── gui_manager.py         # Pygame window and rendering
├── control_panel.py       # PyQt5 settings window
├── window_manager.py      # Window interaction and detection
├── utils/
│   ├── xml_parser.py      # XML configuration parser
│   ├── animation.py       # Animation system
│   └── speech_bubble.py   # Text bubble rendering
├── assets/
│   ├── sprite_pack_1/
│   │   ├── conf/
│   │   │   ├── actions.xml
│   │   │   └── behaviors.xml
│   │   ├── shime1.png
│   │   ├── shime2.png
│   │   └── ...
│   └── sprite_pack_2/...
├── config.json           # User settings storage
└── README.md
```

## Sprite System

### DeviantArt Format Support

```
sprite_pack/
├── conf/
│   ├── actions.xml        # Animation definitions
│   └── behaviors.xml      # Behavior logic and conditions
├── shime1.png            # Sprite images
├── shime2.png
└── ...
```

### XML Structure Understanding

#### actions.xml Components

- **ActionList**: Animation definitions
- **Animation sequences**: Multiple Pose elements with timing
- **Pose attributes**:
  - `Image`: Sprite file path
  - `ImageAnchor`: Pivot point (e.g., "64,128")
  - `Velocity`: Movement speed
  - `Duration`: Frame duration
- **Action types**: Stay, Move, Animate, Sequence, Select
- **BorderType**: Floor, Wall, Ceiling (collision detection)

#### behaviors.xml Components

- **BehaviorList**: Behavior definitions with frequency
- **Conditions**: Desktop environment-based logic
- **NextBehaviorList**: Behavior chaining
- **Hidden behaviors**: Required system behaviors (Fall, Dragged, Thrown)
- **Frequency system**: Probability-based behavior selection

## Development Phases

### Phase 1: Foundation & Basic Interactions

#### Step 1: Core Infrastructure

**Goal**: Basic window, sprite display, and user interactions

- [x] Project structure setup
- [ ] Pygame transparent window creation (always on top)
- [ ] Single sprite loading and display (shime1.png)
- [ ] Basic mouse event handling
- [ ] Left-click drag implementation
- [ ] Double right-click kill functionality

**Deliverable**: Interactive sprite that can be moved and removed

#### Step 2: Control Panel Foundation

**Goal**: Basic management interface

- [ ] PyQt5 control panel window
- [ ] Spawn new pet functionality
- [ ] Kill all pets functionality
- [ ] Basic settings UI structure
- [ ] JSON config save/load system

**Deliverable**: Working control panel for pet management

#### Step 3: XML Parser & Animation System

**Goal**: Sprite animation and configuration

- [ ] XML parser for actions.xml and behaviors.xml
- [ ] Animation frame management system
- [ ] Basic animations (Stand, Walk, Sit) implementation
- [ ] Sprite positioning and anchor points
- [ ] Error handling for missing files

**Deliverable**: Animated sprite with XML-driven behaviors

#### Step 4: Desktop Boundaries & Physics

**Goal**: Screen interaction and basic physics

- [ ] Screen boundary detection
- [ ] Gravity and floor collision system
- [ ] Basic state machine (idle, walking, sitting)
- [ ] Random behavior selection (simplified)
- [ ] Multi-pet management system

**Deliverable**: Pet that moves naturally within desktop bounds

### Phase 2: Advanced Features & Window Interaction

#### Step 1: Professional Logging System

**Goal**: Comprehensive logging and debugging

- [ ] Professional logging framework (time, type, content)
- [ ] Log levels: INFO, WARNING, ERROR
- [ ] Log panel integration in control panel (bottom section)
- [ ] Log file output (.log format)
- [ ] Log filtering and search functionality

**Deliverable**: Complete logging system for debugging and monitoring

#### Step 2: Window Interaction System

**Goal**: Desktop window awareness and interaction

- [ ] Windows API integration (win32gui)
- [ ] Active window detection and boundaries
- [ ] Window state monitoring (minimized, maximized)
- [ ] Basic window positioning (sit on titlebar)
- [ ] Window edge detection and climbing

**Deliverable**: Pet that interacts with desktop windows

#### Step 3: Enhanced Behavior System

**Goal**: Rich behavior implementation

- [ ] Frequency-based behavior selection
- [ ] Simplified condition system
- [ ] Behavior chaining (NextBehaviorList)
- [ ] Random vs triggered behaviors
- [ ] Advanced window interactions (climb edges, jump between windows)

**Deliverable**: Sophisticated pet behavior system

#### Step 4: Speech Bubble System

**Goal**: Text communication system

- [ ] Speech bubble rendering system
- [ ] Text formatting and wrapping
- [ ] 10-second display timer
- [ ] Positioning relative to sprite
- [ ] Multiple bubble management

**Deliverable**: Pet communication system ready for TikTok integration

### Phase 3: TikTok Integration & Advanced Features

#### Step 1: TikTok Connection Infrastructure

**Goal**: Optional TikTok Live integration

- [ ] TikTokLive library integration
- [ ] Username input in control panel
- [ ] Connection validation on-submit
- [ ] Config persistence for successful usernames
- [ ] Error handling with log-only feedback
- [ ] Standalone operation without TikTok

**Deliverable**: Optional TikTok Live connection system

#### Step 2: Chat Event Processing

**Goal**: Real-time chat interaction

- [ ] Chat message capture and parsing
- [ ] Command recognition system
- [ ] Behavior trigger from chat events
- [ ] User interaction response system
- [ ] Connection status monitoring and auto-reconnect

**Deliverable**: Real-time chat-to-behavior mapping

#### Step 3: Advanced Features

**Goal**: Audio, cloning, and polish

- [ ] Sound system implementation (.wav support)
- [ ] Volume control integration
- [ ] Clone/spawn system from behaviors
- [ ] Gift/donation reaction system
- [ ] Multi-pet coordination for chat events
- [ ] Performance optimization for multiple pets

**Deliverable**: Full-featured desktop pets with complete TikTok Live integration

## Technical Implementation Details

### State Management Structure

```python
pet_state = {
    "current_action": "idle",
    "position": {"x": 0, "y": 0},
    "direction": "right",  # for sprite flipping
    "is_dragging": False,
    "speech_bubble": {"text": "", "timer": 0},
    "health": 100,
    "active_window": None
}
```

### Threading Architecture

- **Main Thread**: GUI animation loop (30 FPS)
- **Background Thread**: TikTok Live listener
- **Background Thread**: Behavior timer/scheduler
- **Background Thread**: Window state monitoring

### Configuration System

```json
{
  "settings": {
    "volume": 70,
    "behavior_frequency": 50,
    "screen_boundaries": true,
    "auto_save": true
  },
  "tiktok": {
    "enabled": false,
    "last_successful_username": "",
    "auto_connect": false
  },
  "sprite_packs": ["assets/test_sprite"],
  "logging": {
    "level": "INFO",
    "save_to_file": true,
    "max_log_size": "10MB"
  },
  "active_pets": []
}
```

### Error Handling Requirements

- Missing sprite files
- Malformed XML configurations
- TikTok connection failures
- Windows API errors
- Audio system failures

## Testing Strategy

### Unit Testing

- XML parser validation
- Animation frame calculations
- Behavior probability system
- Window boundary detection

### Integration Testing

- Sprite loading with XML configs
- TikTok Live connection
- Multi-pet interaction
- Control panel functionality

### Performance Testing

- 30 FPS maintenance with multiple pets
- Memory usage optimization
- CPU usage monitoring
- Long-running stability

## Documentation Requirements

### User Documentation

- Installation guide
- Basic usage instructions
- TikTok Live setup guide
- Sprite pack installation
- Troubleshooting guide

### Developer Documentation

- Code architecture overview
- XML configuration format
- Adding new behaviors
- Creating sprite packs
- API integration guide

## Future Considerations

### Potential Enhancements

- Multiple monitor support
- Custom sprite pack creator
- Advanced AI behavior
- Cloud sprite pack sharing
- Mobile companion app

### Scalability

- Plugin system architecture
- External behavior scripting
- Community sprite marketplace
- Advanced animation editor

## Success Metrics

### MVP Success Criteria

- Stable desktop pet with basic behaviors
- Working XML sprite loading system
- Functional control panel
- Basic TikTok Live integration

### Full Success Criteria

- Rich window interaction system
- Robust multi-pet management
- Seamless TikTok Live integration
- Community-friendly sprite format
- Performance optimization for 5+ pets

---

**Note**: This roadmap follows MVP principles - each step should produce a working, testable version before moving to the next step. Regular testing and user feedback should guide development priorities.
