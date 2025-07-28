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
- **Panel control**: Spawn new pets, adjust settings

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

### Phase 1: Core Desktop Pet

#### Step 1: Foundation Setup

**Goal**: Basic window and XML parsing

- [x] Project structure setup
- [ ] Pygame transparent window creation
- [ ] Basic XML parser for actions.xml and behaviors.xml
- [ ] Simple sprite loading system
- [ ] Error handling for missing files

**Deliverable**: Window that can load and display a single sprite

#### Step 2: Basic Animation System

**Goal**: Sprite animation and movement

- [ ] Animation frame management
- [ ] Basic animations (Stand, Walk, Sit)
- [ ] Sprite positioning and anchor points
- [ ] Simple movement velocity system

**Deliverable**: Animated sprite that can walk and change states

#### Step 3: Desktop Integration

**Goal**: Screen interaction and boundaries

- [ ] Screen boundary detection
- [ ] Gravity and floor collision
- [ ] Random behavior selection (simplified)
- [ ] Basic state machine (idle, walking, sitting)

**Deliverable**: Pet that moves around desktop within screen bounds

#### Step 4: Control Panel

**Goal**: Basic management interface

- [ ] PyQt5 control panel window
- [ ] Spawn new pet functionality
- [ ] Basic settings (volume, behavior frequency)
- [ ] JSON config save/load system

**Deliverable**: Working control panel for pet management

### Phase 1.5: Window Interaction

#### Step 1: Window Detection

**Goal**: Active window awareness

- [ ] Windows API integration (win32gui)
- [ ] Active window detection and boundaries
- [ ] Window state monitoring (minimized, maximized)
- [ ] Multi-monitor support consideration

#### Step 2: Window-Based Positioning

**Goal**: Basic window interaction

- [ ] Sit on window titlebar
- [ ] Window edge detection
- [ ] Positioning relative to windows
- [ ] Window change event handling

#### Step 3: Advanced Window Behaviors

**Goal**: Complex window interactions

- [ ] Climb window edges
- [ ] Walk along window bottom/top
- [ ] Jump between windows
- [ ] React to window minimize/maximize

**Deliverable**: Pet that interacts naturally with desktop windows

### Phase 2: Enhanced Interactions

#### Step 1: User Interactions

**Goal**: Direct sprite interaction

- [ ] Mouse event handling
- [ ] Left-click drag implementation
- [ ] Double right-click kill functionality
- [ ] Visual feedback for interactions

#### Step 2: Behavior System Enhancement

**Goal**: Rich behavior implementation

- [ ] Frequency-based behavior selection
- [ ] Simplified condition system
- [ ] Behavior chaining (NextBehaviorList)
- [ ] Random vs triggered behaviors

#### Step 3: Speech Bubble System

**Goal**: Text communication

- [ ] Bubble rendering system
- [ ] Text formatting and wrapping
- [ ] 10-second display timer
- [ ] Positioning relative to sprite

**Deliverable**: Interactive pets with speech capabilities

### Phase 3: TikTok Integration & Advanced Features

#### Step 1: TikTok Live Connection

**Goal**: Real-time chat integration

- [ ] TikTokLive library integration
- [ ] Connection testing and error handling
- [ ] Basic chat message capture
- [ ] Connection status monitoring

#### Step 2: Event Mapping System

**Goal**: Chat-to-behavior mapping

- [ ] Chat command recognition
- [ ] Behavior trigger from chat events
- [ ] User interaction response system
- [ ] Gift/donation reaction system

#### Step 3: Sound & Clone System

**Goal**: Audio and multi-pet features

- [ ] Sound system implementation (.wav support)
- [ ] Volume control integration
- [ ] Clone/spawn system from behaviors
- [ ] Multi-pet management

**Deliverable**: Full-featured desktop pets with TikTok Live integration

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
    "spawn_rate": 5,
    "behavior_frequency": 50,
    "screen_boundaries": true,
    "tiktok_enabled": false
  },
  "sprite_packs": ["assets/sprite_pack_1", "assets/sprite_pack_2"],
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
