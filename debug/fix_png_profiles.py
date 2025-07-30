# fix_png_profiles.py
from PIL import Image
import os

def fix_png_metadata(sprite_pack_name):
    """Remove iCCP profiles from PNG files"""
    sprite_dir = f"assets/{sprite_pack_name}"
    
    if not os.path.exists(sprite_dir):
        print(f"Directory not found: {sprite_dir}")
        return
    
    fixed_count = 0
    for filename in os.listdir(sprite_dir):
        if filename.lower().endswith('.png'):
            filepath = os.path.join(sprite_dir, filename)
            try:
                # Open and re-save without color profile
                with Image.open(filepath) as img:
                    # Convert to RGBA to preserve transparency
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Save without ICC profile
                    img.save(filepath, 'PNG', optimize=True)
                
                print(f"✅ Fixed: {filename}")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error fixing {filename}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} PNG files in {sprite_pack_name}")

# Run untuk semua sprite packs
if __name__ == "__main__":
    # Fix Hornet sprites
    fix_png_metadata("Hornet")
    
    # Fix sprite packs lain jika ada
    # fix_png_metadata("OtherSpritePack")