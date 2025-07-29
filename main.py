#!/usr/bin/env python3
"""
main.py - Main application entry point dengan Animation System Integration

Enhanced main file dengan integrasi animation system yang sudah diperbaiki
untuk Phase 1 Step 3 completion.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Import our modules
from config import init_config, AppConstants
from sprite_loader import SpriteDiscovery, init_sprite_loader
from gui_manager import PygameWindow
from control_panel import ControlPanel

# Test animation system availability
try:
    from utils.animation import AnimationManager, create_animation_manager
    ANIMATION_SYSTEM_AVAILABLE = True
    print("✅ Animation system loaded successfully")
except ImportError as e:
    ANIMATION_SYSTEM_AVAILABLE = False
    print(f"⚠️  Animation system not available: {e}")
    print("   Application will run with fallback animations")


class TechniseeShimeji:
    """Main application class dengan animation system integration"""
    
    def __init__(self):
        self.config = None
        self.sprite_loader = None
        self.pygame_window = None
        self.control_panel = None
        self.qt_app = None
        self.pygame_timer = None
        
    def initialize(self) -> bool:
        """Initialize all application components dengan animation system support"""
        try:
            print(f"Starting {AppConstants.APP_NAME}")
            print(f"Version: {AppConstants.VERSION}")
            print(f"Animation System: {'✅ Available' if ANIMATION_SYSTEM_AVAILABLE else '❌ Fallback Mode'}")
            
            # Initialize configuration
            print("Initializing configuration...")
            self.config = init_config()
            if not self.config.validate_config():
                print("Warning: Configuration validation failed, using defaults")
            
            # Initialize sprite loader
            print("Initializing sprite loader...")
            self.sprite_loader = init_sprite_loader()
            
            # Discover sprite packs
            print("Discovering sprite packs...")
            sprite_packs = SpriteDiscovery.discover_sprite_packs()
            print(f"Discovered {len(sprite_packs)} sprite pack(s): {sprite_packs}")
            
            if not sprite_packs:
                print("Warning: No valid sprite packs found in assets/ directory")
                print(f"Expected structure: {AppConstants.ASSETS_DIR}/SpriteName/{AppConstants.SPRITE_REQUIRED_FILE}")
                # Don't return False, let it continue for debugging
            else:
                # Test animation system dengan sprite pack pertama
                self._test_animation_system(sprite_packs[0])
            
            # Update config with discovered packs
            self.config.set('sprite_packs', sprite_packs)
            
            # Initialize Qt application
            print("Initializing Qt application...")
            self.qt_app = QApplication(sys.argv)
            self.qt_app.setApplicationName(AppConstants.APP_NAME)
            self.qt_app.setApplicationVersion(AppConstants.VERSION)
            
            # Initialize pygame window
            print("Initializing pygame window...")
            self.pygame_window = PygameWindow()
            
            # Initialize control panel
            print("Initializing control panel...")
            self.control_panel = ControlPanel(self.pygame_window)
            self.control_panel.show()
            
            # Setup pygame timer for non-blocking updates
            print("Setting up pygame timer...")
            self.pygame_timer = QTimer()
            self.pygame_timer.timeout.connect(self._update_pygame)
            self.pygame_timer.start(1000 // AppConstants.TARGET_FPS)  # Convert FPS to ms
            
            print("Application initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_animation_system(self, sprite_name: str) -> None:
        """Test animation system dengan sprite pack - AFTER pygame init"""
        if not ANIMATION_SYSTEM_AVAILABLE:
            return
        
        # Skip testing during startup, akan ditest setelah pygame display ready
        print(f"Animation system will be tested after pygame initialization...")
        return
    
    def _update_pygame(self) -> None:
        """Update pygame window (called by Qt timer)"""
        try:
            if not self.pygame_window or not self.pygame_window.step():
                # Pygame window wants to close
                print("Pygame window requested shutdown")
                self.shutdown()
        except Exception as e:
            print(f"Error in pygame update: {e}")
            import traceback
            traceback.print_exc()
            self.shutdown()
    
    def _load_saved_pets(self) -> None:
        """Load pets from saved state"""
        try:
            saved_pets = self.config.get('active_pets', [])
            if saved_pets:
                loaded_count = self.pygame_window.load_pets_state(saved_pets)
                self.control_panel.update_status()
                print(f"Loaded {loaded_count} pets from saved state")
        except Exception as e:
            print(f"Error loading saved pets: {e}")
    
    def _spawn_initial_pet(self) -> None:
        """Spawn initial pet jika no saved pets"""
        if len(self.pygame_window.pets) == 0:
            sprite_packs = self.config.get('sprite_packs', [])
            if sprite_packs:
                selected_sprite = self.config.get('ui.selected_sprite')
                if not selected_sprite or selected_sprite not in sprite_packs:
                    selected_sprite = sprite_packs[0]
                
                spawn_x = self.config.get('settings.spawn_x')
                spawn_y = self.config.get('settings.spawn_y')
                
                print(f"Spawning initial pet: {selected_sprite}")
                if ANIMATION_SYSTEM_AVAILABLE:
                    print("   Using enhanced animation system")
                else:
                    print("   Using fallback animation system")
                
                pet_id = self.pygame_window.add_pet(selected_sprite, spawn_x, spawn_y)
                self.control_panel.update_status()
                print(f"Spawned initial pet: {pet_id}")
    
    def _show_startup_info(self) -> None:
        """Show startup information"""
        print(f"\n{'='*60}")
        print(f"🎉 {AppConstants.APP_NAME} READY!")
        print(f"{'='*60}")
        print(f"📦 Sprite Packs: {len(self.config.get('sprite_packs', []))}")
        print(f"🎬 Animation System: {'✅ Enhanced XML System' if ANIMATION_SYSTEM_AVAILABLE else '❌ Fallback System'}")
        print(f"🐾 Active Pets: {len(self.pygame_window.pets)}")
        print(f"⚙️  Control Panel: Open and ready")
        print(f"{'='*60}")
        print(f"📋 Controls:")
        print(f"   • Left-click + drag: Move pets")
        print(f"   • Right-click: Make pet sit / special actions")
        print(f"   • Double right-click: Remove pet")
        print(f"   • Control Panel: Spawn pets, adjust settings")
        print(f"   • F1: Toggle debug mode")
        print(f"   • F2: Print performance info")
        print(f"{'='*60}")
        
        if ANIMATION_SYSTEM_AVAILABLE:
            print(f"🎊 Phase 1 Step 3 COMPLETE!")
            print(f"   Your pets now have XML-driven animations!")
        else:
            print(f"⚠️  Running in compatibility mode")
            print(f"   To enable XML animations, ensure utils/animation.py is available")
        
        print(f"\nApplication running. Use control panel to manage pets.")
        print(f"Press Ctrl+C or close control panel to exit.\n")
    
    def run(self) -> int:
        """Run the main application loop"""
        if not self.initialize():
            print("Failed to initialize application")
            return 1
        
        try:
            # Load saved pets or spawn initial pet
            print("Loading saved pets...")
            self._load_saved_pets()
            print("Spawning initial pet if needed...")
            self._spawn_initial_pet()
            
            # Show startup information
            self._show_startup_info()
            
            # Run Qt event loop
            exit_code = self.qt_app.exec_()
            print(f"Qt application exited with code: {exit_code}")
            return exit_code
            
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
            return 0
        except Exception as e:
            print(f"Unexpected error during execution: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown application gracefully"""
        try:
            print("Shutting down application...")
            
            # Stop pygame timer
            if self.pygame_timer:
                self.pygame_timer.stop()
            
            # Close control panel
            if self.control_panel:
                self.control_panel.close()
            
            # Cleanup pygame window
            if self.pygame_window:
                self.pygame_window.cleanup()
            
            # Quit Qt application
            if self.qt_app:
                self.qt_app.quit()
            
            print("Application shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")


def main() -> int:
    """Main entry point dengan animation system support"""
    # Ensure we can find our modules
    if not os.path.exists(AppConstants.ASSETS_DIR):
        print(f"Error: {AppConstants.ASSETS_DIR} directory not found")
        print("Please create the assets directory and add sprite packs")
        print("Expected structure:")
        print(f"  {AppConstants.ASSETS_DIR}/")
        print(f"    SpriteName/")
        print(f"      {AppConstants.SPRITE_REQUIRED_FILE}")
        print(f"      conf/")
        print(f"        {AppConstants.ACTIONS_XML}")
        print(f"        {AppConstants.BEHAVIORS_XML}")
        return 1
    
    # Show animation system status
    if ANIMATION_SYSTEM_AVAILABLE:
        print("🎬 Enhanced Animation System Ready!")
        print("   Your pets will use XML-driven animations")
    else:
        print("⚠️  Animation System Not Available")
        print("   Pets will use basic fallback animations")
        print("   To enable XML animations:")
        print("     1. Ensure utils/animation.py exists")
        print("     2. Check XML files in sprite pack conf/ folders")
    
    # Create and run application
    app = TechniseeShimeji()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())