#!/usr/bin/env python3
"""
sprite_diagnostic.py - Diagnostic tool untuk sprite packs

Tool untuk menganalisis sprite packs dan mengidentifikasi
masalah dengan pinch animation sprites dan physics testing.
"""

import os
import sys
from typing import Dict, List, Any

# Add project root ke path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import AppConstants
    from sprite_loader import SpriteDiscovery, get_sprite_loader
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class SpriteDiagnostic:
    """Diagnostic tool untuk sprite pack analysis"""
    
    def __init__(self):
        self.sprite_loader = get_sprite_loader()
        
    def analyze_sprite_pack(self, sprite_name: str) -> Dict[str, Any]:
        """Comprehensive analysis of sprite pack"""
        print(f"🔍 Analyzing Sprite Pack: {sprite_name}")
        print("=" * 50)
        
        analysis = {
            'sprite_name': sprite_name,
            'basic_files': self._check_basic_files(sprite_name),
            'pinch_sprites': self._check_pinch_sprites(sprite_name),
            'physics_sprites': self._check_physics_sprites(sprite_name),
            'xml_files': self._check_xml_files(sprite_name),
            'all_sprites': self._list_all_sprites(sprite_name),
            'recommendations': []
        }
        
        self._generate_recommendations(analysis)
        self._print_analysis_summary(analysis)
        
        return analysis
    
    def _check_basic_files(self, sprite_name: str) -> Dict[str, bool]:
        """Check basic required files"""
        print("\n📁 Basic Files Check:")
        
        sprite_dir = os.path.join(AppConstants.ASSETS_DIR, sprite_name)
        basic_files = {
            'directory_exists': os.path.exists(sprite_dir),
            'shime1.png': False,  # Required
            'shime1a.png': False,  # Common
        }
        
        if basic_files['directory_exists']:
            print(f"   ✅ Directory exists: {sprite_dir}")
            
            for filename in ['shime1.png', 'shime1a.png']:
                filepath = os.path.join(sprite_dir, filename)
                exists = os.path.exists(filepath)
                basic_files[filename] = exists
                
                status = "✅" if exists else "❌"
                required = " (REQUIRED)" if filename == 'shime1.png' else ""
                print(f"   {status} {filename}{required}")
        else:
            print(f"   ❌ Directory not found: {sprite_dir}")
        
        return basic_files
    
    def _check_pinch_sprites(self, sprite_name: str) -> Dict[str, Any]:
        """Check pinch animation sprites"""
        print("\n🤏 Pinch Animation Sprites:")
        
        # Expected pinch sprites based on XML logic
        pinch_sprites = {
            'shime5.png': 'Near left',
            'shime5a.png': 'Center (main)',
            'shime6.png': 'Near right', 
            'shime7.png': 'Medium left',
            'shime8.png': 'Medium right',
            'shime9.png': 'Far left',
            'shime10.png': 'Far right',
        }
        
        results = {
            'total_expected': len(pinch_sprites),
            'found': 0,
            'missing': [],
            'available': [],
            'loadable': []
        }
        
        for sprite_file, description in pinch_sprites.items():
            filepath = os.path.join(AppConstants.ASSETS_DIR, sprite_name, sprite_file)
            exists = os.path.exists(filepath)
            
            if exists:
                results['found'] += 1
                results['available'].append(sprite_file)
                
                # Test if sprite can be loaded
                try:
                    sprite_surface = self.sprite_loader.load_sprite(sprite_name, sprite_file)
                    if sprite_surface:
                        results['loadable'].append(sprite_file)
                        print(f"   ✅ {sprite_file} - {description} (loadable)")
                    else:
                        print(f"   ⚠️ {sprite_file} - {description} (exists but load failed)")
                except Exception as e:
                    print(f"   ⚠️ {sprite_file} - {description} (load error: {e})")
            else:
                results['missing'].append(sprite_file)
                print(f"   ❌ {sprite_file} - {description} (missing)")
        
        coverage = (results['found'] / results['total_expected']) * 100
        print(f"\n   📊 Pinch Sprite Coverage: {results['found']}/{results['total_expected']} ({coverage:.1f}%)")
        
        return results
    
    def _check_physics_sprites(self, sprite_name: str) -> Dict[str, Any]:
        """Check physics-related sprites"""
        print("\n⚡ Physics Animation Sprites:")
        
        physics_sprites = {
            'shime4.png': 'Falling',
            'shime18.png': 'Bouncing 1',
            'shime19.png': 'Bouncing 2',
            'shime22.png': 'Jumping',
            'shime11.png': 'Sitting',
            'shime2.png': 'Walking 1',
            'shime3.png': 'Walking 2',
        }
        
        results = {
            'total_expected': len(physics_sprites),
            'found': 0,
            'missing': [],
            'available': []
        }
        
        for sprite_file, description in physics_sprites.items():
            filepath = os.path.join(AppConstants.ASSETS_DIR, sprite_name, sprite_file)
            exists = os.path.exists(filepath)
            
            if exists:
                results['found'] += 1
                results['available'].append(sprite_file)
                print(f"   ✅ {sprite_file} - {description}")
            else:
                results['missing'].append(sprite_file)
                print(f"   ❌ {sprite_file} - {description}")
        
        coverage = (results['found'] / results['total_expected']) * 100
        print(f"\n   📊 Physics Sprite Coverage: {results['found']}/{results['total_expected']} ({coverage:.1f}%)")
        
        return results
    
    def _check_xml_files(self, sprite_name: str) -> Dict[str, Any]:
        """Check XML configuration files"""
        print("\n📋 XML Configuration Files:")
        
        conf_dir = os.path.join(AppConstants.ASSETS_DIR, sprite_name, 'conf')
        xml_files = {
            'conf_directory': os.path.exists(conf_dir),
            'actions.xml': False,
            'behaviors.xml': False
        }
        
        if xml_files['conf_directory']:
            print(f"   ✅ conf/ directory exists")
            
            for xml_file in ['actions.xml', 'behaviors.xml']:
                xml_path = os.path.join(conf_dir, xml_file)
                exists = os.path.exists(xml_path)
                xml_files[xml_file] = exists
                
                if exists:
                    print(f"   ✅ {xml_file}")
                    # Try to parse XML
                    try:
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        print(f"      📄 XML is parseable, root: {root.tag}")
                    except Exception as e:
                        print(f"      ⚠️ XML parse error: {e}")
                else:
                    print(f"   ❌ {xml_file}")
        else:
            print(f"   ❌ conf/ directory missing")
        
        return xml_files
    
    def _list_all_sprites(self, sprite_name: str) -> List[str]:
        """List all available sprite files"""
        print("\n📂 All Available Sprites:")
        
        sprite_dir = os.path.join(AppConstants.ASSETS_DIR, sprite_name)
        all_sprites = []
        
        if os.path.exists(sprite_dir):
            for filename in sorted(os.listdir(sprite_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    all_sprites.append(filename)
                    print(f"   📄 {filename}")
            
            print(f"\n   📊 Total sprites found: {len(all_sprites)}")
        else:
            print("   ❌ Sprite directory not found")
        
        return all_sprites
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> None:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Basic file recommendations
        if not analysis['basic_files']['shime1.png']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Basic Files',
                'issue': 'Missing shime1.png',
                'solution': 'Add shime1.png to sprite pack directory - this is required for basic functionality'
            })
        
        # Pinch sprite recommendations
        pinch_data = analysis['pinch_sprites']
        if pinch_data['found'] < pinch_data['total_expected'] * 0.6:  # Less than 60%
            missing_critical = [s for s in pinch_data['missing'] if s in ['shime5.png', 'shime5a.png', 'shime6.png']]
            if missing_critical:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Pinch Animation',
                    'issue': f'Missing critical pinch sprites: {", ".join(missing_critical)}',
                    'solution': 'Add missing pinch sprites for smooth drag animation. These are essential for pinch animation test to pass.'
                })
        
        # Physics sprite recommendations
        physics_data = analysis['physics_sprites']
        if physics_data['found'] < physics_data['total_expected'] * 0.5:  # Less than 50%
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Physics Animation',
                'issue': f'Low physics sprite coverage: {physics_data["found"]}/{physics_data["total_expected"]}',
                'solution': 'Add missing physics sprites (shime4.png for falling, shime18/19.png for bouncing, etc.)'
            })
        
        # XML recommendations
        xml_data = analysis['xml_files']
        if not xml_data['actions.xml'] or not xml_data['behaviors.xml']:
            recommendations.append({
                'priority': 'LOW',
                'category': 'XML Configuration',
                'issue': 'Missing XML files',
                'solution': 'Add actions.xml and behaviors.xml to conf/ directory for full Shimeji compatibility (optional)'
            })
        
        analysis['recommendations'] = recommendations
    
    def _print_analysis_summary(self, analysis: Dict[str, Any]) -> None:
        """Print comprehensive analysis summary"""
        print(f"\n{'='*60}")
        print(f"📊 SPRITE PACK ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"Sprite Pack: {analysis['sprite_name']}")
        
        # Overall health score
        score = 0
        max_score = 0
        
        # Basic files (30 points)
        if analysis['basic_files']['shime1.png']:
            score += 30
        max_score += 30
        
        # Pinch sprites (40 points)
        pinch_ratio = analysis['pinch_sprites']['found'] / analysis['pinch_sprites']['total_expected']
        score += int(40 * pinch_ratio)
        max_score += 40
        
        # Physics sprites (20 points)
        physics_ratio = analysis['physics_sprites']['found'] / analysis['physics_sprites']['total_expected']
        score += int(20 * physics_ratio)
        max_score += 20
        
        # XML files (10 points)
        xml_score = sum([
            analysis['xml_files']['actions.xml'],
            analysis['xml_files']['behaviors.xml']
        ]) * 5
        score += xml_score
        max_score += 10
        
        health_percentage = (score / max_score) * 100
        
        print(f"\n🏥 Health Score: {score}/{max_score} ({health_percentage:.1f}%)")
        
        if health_percentage >= 80:
            print("   ✅ EXCELLENT - Sprite pack is well-equipped for all tests")
        elif health_percentage >= 60:
            print("   ⚠️  GOOD - Most features should work, some tests may fail")
        elif health_percentage >= 40:
            print("   ⚠️  FAIR - Basic functionality available, many tests will fail")
        else:
            print("   ❌ POOR - Significant issues, most tests will fail")
        
        # Print recommendations
        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                priority_color = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
                color = priority_color.get(rec['priority'], '⚪')
                print(f"   {i}. {color} {rec['priority']} - {rec['category']}")
                print(f"      Issue: {rec['issue']}")
                print(f"      Solution: {rec['solution']}")
        
        # Test predictions
        print(f"\n🔮 Test Predictions:")
        pinch_success = analysis['pinch_sprites']['found'] >= 4  # At least 4 pinch sprites
        physics_success = analysis['physics_sprites']['found'] >= 3  # At least 3 physics sprites
        
        print(f"   Pinch Animation Test: {'✅ LIKELY PASS' if pinch_success else '❌ LIKELY FAIL'}")
        print(f"   Physics Engine Test: {'✅ LIKELY PASS' if physics_success else '❌ LIKELY FAIL'}")
        print(f"   Throw System Test: ✅ LIKELY PASS (physics-based)")
        print(f"   Integration Test: {'✅ LIKELY PASS' if pinch_success and physics_success else '❌ LIKELY FAIL'}")


def main():
    """Main diagnostic function"""
    if len(sys.argv) > 1:
        sprite_name = sys.argv[1]
    else:
        # Auto-detect sprite packs
        sprite_packs = SpriteDiscovery.discover_sprite_packs()
        
        if not sprite_packs:
            print("❌ No sprite packs found in assets/ directory")
            return 1
        
        print(f"Available sprite packs: {sprite_packs}")
        sprite_name = sprite_packs[0]
        print(f"Analyzing: {sprite_name}")
    
    # Run diagnostic
    diagnostic = SpriteDiagnostic()
    analysis = diagnostic.analyze_sprite_pack(sprite_name)
    
    # Suggest next steps
    print(f"\n🚀 Next Steps:")
    if analysis['recommendations']:
        print("   1. Address the recommendations above")
        print("   2. Re-run diagnostic: python sprite_diagnostic.py")
        print("   3. Run physics tests: python test/test_physics.py")
    else:
        print("   1. Run physics tests: python test/test_physics.py")
        print("   2. Run main application: python main.py")
    
    # Return status based on health
    basic_ok = analysis['basic_files']['shime1.png']
    return 0 if basic_ok else 1


if __name__ == "__main__":
    sys.exit(main())