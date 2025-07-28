# Teknisee Shimeji TikTok

A desktop pet application inspired by Shimeji with TikTok Live integration capabilities. Features interactive desktop pets that can respond to TikTok Live chat in real-time.

## Features

- 🐾 Interactive desktop pets with various animations
- 🎮 Window interaction (climb, sit on windows)
- 💬 TikTok Live chat integration (coming soon)
- 🎨 Support for custom sprite packs from DeviantArt
- ⚙️ Control panel for pet management
- 🖱️ Mouse interactions (drag, double-click to remove)

## Requirements

- Python 3.8+
- Windows OS (primary target)

## Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/teknisee-shimeji-tiktok.git
cd teknisee-shimeji-tiktok
```

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows:
source env/Scripts/activate
# Mac/Linux:
# source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

## Controls

- **Left-click + Drag**: Move pet around
- **Double right-click**: Remove pet
- **Control Panel**: Spawn new pets and adjust settings

## Development Status

🚧 **This project is in active development**

- ✅ Phase 1: Basic desktop pet with sprite rendering
- 🔄 Phase 2: Enhanced interactions and behaviors
- ⏳ Phase 3: TikTok Live integration

## Project Structure

```
teknisee-shimeji-tiktok/
├── main.py              # Main application
├── assets/              # Sprite packs and resources
│   └── test_sprite/     # Default test sprites
├── requirements.txt     # Dependencies
├── config.json         # User settings (auto-generated)
└── README.md
```

## Contributing

This project follows MVP (Minimum Viable Product) development approach. Each phase focuses on core functionality before adding advanced features.

## License

MIT License - feel free to use and modify for your projects.

---

**Note**: TikTok Live features are planned for Phase 3. Current version focuses on core desktop pet functionality.
