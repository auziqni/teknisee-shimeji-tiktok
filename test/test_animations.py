#!/usr/bin/env python3
"""
test/test_animations.py - Script untuk testing sistem animasi XML

Script ini memungkinkan testing animasi sistem secara terpisah
untuk memastikan XML parsing dan animation loading berfungsi dengan baik.
"""

import pygame
import sys
import os
from typing import Dict, Any, Optional

# Tambahkan project root ke path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import basic modules first
    from config import init_config, AppConstants
    from utils.xml_parser import XMLParser
    
    # Import sprite discovery only (avoid circular import)
    import sprite_loader
    SpriteDiscovery = sprite_loader.SpriteDiscovery
    
    # Try import animation system
    try:
        from utils.animation import create_animation_manager, validate_animation_system
        ANIMATION_SYSTEM_AVAILABLE = True
    except ImportError:
        print("Warning: Animation system not available")
        ANIMATION_SYSTEM_AVAILABLE = False
        create_animation_manager = None
        validate_animation_system = None
        
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run this script from the project root directory")
    sys.exit(1)


class AnimationTester:
    """Class untuk testing animation system"""
    
    def __init__(self):
        try:
            self.config = init_config()
            # Initialize sprite loader manually to avoid circular import
            self.sprite_loader = sprite_loader.SpriteLoader()
            
            # Initialize Pygame
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Animation System Tester")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 24)
            
            # Test variables
            self.current_sprite = None
            self.animation_manager = None
            self.current_action = "Stand"
            self.available_actions = []
            self.action_index = 0
            
            print("Animation Tester initialized")
        except Exception as e:
            print(f"Error initializing tester: {e}")
            raise
    
    def test_xml_parsing(self, sprite_name: str) -> Dict[str, Any]:
        """Test XML parsing untuk sprite pack"""
        print(f"\n=== Testing XML Parsing for {sprite_name} ===")
        
        try:
            xml_parser = XMLParser()
            success = xml_parser.parse_sprite_pack(sprite_name)
            
            if success:
                actions = xml_parser.get_all_actions()
                behaviors = xml_parser.get_all_behaviors()
                
                print(f"✅ Successfully parsed XML files")
                print(f"📋 Found {len(actions)} actions:")
                for action_name in sorted(actions.keys()):
                    action_data = actions[action_name]
                    print(f"   - {action_name} ({action_data.action_type}) - {len(action_data.animations)} animations")
                
                print(f"🎯 Found {len(behaviors)} behaviors:")
                for behavior_name in sorted(behaviors.keys()):
                    behavior_data = behaviors[behavior_name]
                    hidden_str = " (hidden)" if behavior_data.hidden else ""
                    print(f"   - {behavior_name} (freq: {behavior_data.frequency}){hidden_str}")
                
                return {
                    'success': True,
                    'actions': len(actions),
                    'behaviors': len(behaviors),
                    'action_names': list(actions.keys())
                }
            else:
                print("❌ Failed to parse XML files")
                return {'success': False, 'error': 'Parsing failed'}
                
        except Exception as e:
            print(f"❌ Error during XML parsing: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_animation_creation(self, sprite_name: str) -> bool:
        """Test animation manager creation"""
        print(f"\n=== Testing Animation Creation for {sprite_name} ===")
        
        if not ANIMATION_SYSTEM_AVAILABLE:
            print("❌ Animation system not available")
            return False
        
        try:
            self.animation_manager = create_animation_manager(sprite_name)
            if self.animation_manager:
                self.available_actions = self.animation_manager.get_available_actions()
                print(f"✅ Animation manager created successfully")
                print(f"🎬 Available animations: {len(self.available_actions)}")
                for action in sorted(self.available_actions):
                    print(f"   - {action}")
                return True
            else:
                print("❌ Failed to create animation manager")
                return False
                
        except Exception as e:
            print(f"❌ Error creating animation manager: {e}")
            return False
    
    def test_sprite_loading(self, sprite_name: str) -> Dict[str, Any]:
        """Test sprite loading dari XML references"""
        print(f"\n=== Testing Sprite Loading for {sprite_name} ===")
        
        try:
            validation_results = self.sprite_loader.validate_sprite_references(sprite_name)
            
            total_sprites = len(validation_results)
            missing_sprites = [sprite for sprite, exists in validation_results.items() if not exists]
            loaded_sprites = total_sprites - len(missing_sprites)
            
            print(f"📁 Total sprite references: {total_sprites}")
            print(f"✅ Successfully loaded: {loaded_sprites}")
            print(f"❌ Missing sprites: {len(missing_sprites)}")
            
            if missing_sprites:
                print("Missing files:")
                for sprite in missing_sprites:
                    print(f"   - {sprite}")
            
            return {
                'total': total_sprites,
                'loaded': loaded_sprites,
                'missing': missing_sprites
            }
            
        except Exception as e:
            print(f"❌ Error testing sprite loading: {e}")
            return {
                'total': 0,
                'loaded': 0,
                'missing': [],
                'error': str(e)
            }
    
    def run_interactive_test(self, sprite_name: str):
        """Run interactive animation test"""
        print(f"\n=== Interactive Animation Test for {sprite_name} ===")
        print("Controls:")
        print("  LEFT/RIGHT arrows: Switch animations")
        print("  SPACE: Restart current animation")
        print("  ESC: Exit")
        print("  F1: Print current animation info")
        
        if not self.animation_manager:
            print("❌ Animation manager not available")
            return
        
        if not self.available_actions:
            print("❌ No animations available")
            return
        
        try:
            # Start dengan action pertama
            self.current_action = self.available_actions[0]
            self.animation_manager.play_action(self.current_action, loop=True)
            
            running = True
            while running:
                dt = self.clock.tick(30) / 1000.0  # 30 FPS
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_LEFT:
                            self._previous_animation()
                        elif event.key == pygame.K_RIGHT:
                            self._next_animation()
                        elif event.key == pygame.K_SPACE:
                            self._restart_animation()
                        elif event.key == pygame.K_F1:
                            self._print_animation_info()
                
                # Update animation
                if self.animation_manager:
                    try:
                        sprite, velocity = self.animation_manager.update(dt)
                        if sprite:
                            self.current_sprite = sprite
                    except Exception as e:
                        print(f"Error updating animation: {e}")
                
                # Draw
                self._draw_test_screen()
                
        except Exception as e:
            print(f"Error during interactive test: {e}")
    
    def _next_animation(self):
        """Switch ke animasi berikutnya"""
        try:
            self.action_index = (self.action_index + 1) % len(self.available_actions)
            self.current_action = self.available_actions[self.action_index]
            self.animation_manager.play_action(self.current_action, loop=True)
            print(f"Switched to: {self.current_action}")
        except Exception as e:
            print(f"Error switching animation: {e}")
    
    def _previous_animation(self):
        """Switch ke animasi sebelumnya"""
        try:
            self.action_index = (self.action_index - 1) % len(self.available_actions)
            self.current_action = self.available_actions[self.action_index]
            self.animation_manager.play_action(self.current_action, loop=True)
            print(f"Switched to: {self.current_action}")
        except Exception as e:
            print(f"Error switching animation: {e}")
    
    def _restart_animation(self):
        """Restart animasi saat ini"""
        try:
            self.animation_manager.play_action(self.current_action, loop=True)
            print(f"Restarted: {self.current_action}")
        except Exception as e:
            print(f"Error restarting animation: {e}")
    
    def _print_animation_info(self):
        """Print informasi animasi saat ini"""
        try:
            if self.animation_manager:
                info = self.animation_manager.get_current_animation_info()
                print(f"\n=== Current Animation Info ===")
                for key, value in info.items():
                    print(f"{key}: {value}")
                print("==============================\n")
        except Exception as e:
            print(f"Error getting animation info: {e}")
    
    def _draw_test_screen(self):
        """Draw test screen"""
        try:
            # Clear screen
            self.screen.fill((50, 50, 50))
            
            # Draw sprite di tengah
            if self.current_sprite:
                sprite_rect = self.current_sprite.get_rect()
                sprite_rect.center = (400, 300)
                self.screen.blit(self.current_sprite, sprite_rect)
            
            # Draw UI info
            y_offset = 10
            ui_texts = [
                f"Current Animation: {self.current_action}",
                f"Animation {self.action_index + 1}/{len(self.available_actions)}",
                f"Use LEFT/RIGHT arrows to switch",
                f"Press SPACE to restart, F1 for info",
            ]
            
            for text in ui_texts:
                text_surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 25
            
            # Draw available actions list
            y_offset = 200
            list_title = self.font.render("Available Actions:", True, (200, 200, 255))
            self.screen.blit(list_title, (10, y_offset))
            y_offset += 25
            
            small_font = pygame.font.Font(None, 18)
            for i, action in enumerate(self.available_actions[:15]):  # Limit to 15 untuk screen space
                color = (255, 255, 0) if i == self.action_index else (180, 180, 180)
                action_text = small_font.render(f"{i+1}. {action}", True, color)
                self.screen.blit(action_text, (10, y_offset))
                y_offset += 18
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error drawing screen: {e}")
    
    def run_full_test_suite(self, sprite_name: str):
        """Run full test suite"""
        print(f"\n{'='*60}")
        print(f"🧪 FULL ANIMATION SYSTEM TEST SUITE")
        print(f"📦 Sprite Pack: {sprite_name}")
        print(f"{'='*60}")
        
        # Test 1: XML Parsing
        xml_results = self.test_xml_parsing(sprite_name)
        
        # Test 2: Animation Creation
        animation_created = self.test_animation_creation(sprite_name)
        
        # Test 3: Sprite Loading
        sprite_results = self.test_sprite_loading(sprite_name)
        
        # Test 4: Validation (if available)
        validation_results = {}
        if ANIMATION_SYSTEM_AVAILABLE and validate_animation_system:
            try:
                validation_results = validate_animation_system(sprite_name)
            except Exception as e:
                validation_results = {'error': str(e)}
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"XML Parsing: {'✅ PASS' if xml_results.get('success') else '❌ FAIL'}")
        print(f"Animation Manager: {'✅ PASS' if animation_created else '❌ FAIL'}")
        print(f"Sprite Loading: {sprite_results['loaded']}/{sprite_results['total']} loaded")
        print(f"Animation System: {'✅ AVAILABLE' if ANIMATION_SYSTEM_AVAILABLE else '❌ NOT AVAILABLE'}")
        print(f"Overall Status: {'✅ READY FOR USE' if animation_created and sprite_results['loaded'] > 0 else '❌ NEEDS ATTENTION'}")
        
        if validation_results.get('errors'):
            print(f"\n⚠️  Errors found:")
            for error in validation_results['errors']:
                print(f"   - {error}")
        
        return {
            'xml_parsing': xml_results.get('success', False),
            'animation_creation': animation_created,
            'sprites_loaded': sprite_results['loaded'],
            'total_sprites': sprite_results['total'],
            'validation': validation_results,
            'animation_system_available': ANIMATION_SYSTEM_AVAILABLE
        }


def main():
    """Main function"""
    try:
        if len(sys.argv) > 1:
            sprite_name = sys.argv[1]
        else:
            # Auto-detect available sprite packs
            sprite_packs = SpriteDiscovery.discover_sprite_packs()
            
            if not sprite_packs:
                print("❌ No sprite packs found in assets/ directory")
                print(f"Please add sprite packs to {AppConstants.ASSETS_DIR}/")
                return 1
            
            print(f"📦 Available sprite packs: {sprite_packs}")
            sprite_name = sprite_packs[0]  # Use first available
            print(f"🎯 Testing with: {sprite_name}")
        
        # Create tester
        tester = AnimationTester()
        
        # Run tests
        results = tester.run_full_test_suite(sprite_name)
        
        # Ask for interactive test
        if results['animation_creation'] and ANIMATION_SYSTEM_AVAILABLE:
            print(f"\n🎮 Run interactive animation test? (y/n): ", end="")
            try:
                response = input().lower().strip()
                if response in ['y', 'yes']:
                    tester.run_interactive_test(sprite_name)
            except KeyboardInterrupt:
                print("\nTest interrupted by user")
        elif not ANIMATION_SYSTEM_AVAILABLE:
            print("\n⚠️  Interactive test not available - animation system not loaded")
        
        pygame.quit()
        
        # Return exit code
        return 0 if results['xml_parsing'] else 1
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())