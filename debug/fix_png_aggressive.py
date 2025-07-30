# aggressive_png_fix.py
from PIL import Image
import os

def aggressive_png_fix(sprite_pack_name):
    """More aggressive PNG cleaning"""
    sprite_dir = f"assets/{sprite_pack_name}"
    
    fixed_count = 0
    total_files = 0
    
    for filename in os.listdir(sprite_dir):
        if filename.lower().endswith('.png'):
            total_files += 1
            filepath = os.path.join(sprite_dir, filename)
            try:
                with Image.open(filepath) as img:
                    # Force convert to RGBA
                    rgba_img = img.convert('RGBA')
                    
                    # Save with NO metadata whatsoever
                    rgba_img.save(
                        filepath, 
                        'PNG', 
                        optimize=True,
                        icc_profile=None,
                        pnginfo=None,  # Remove all PNG metadata
                        compress_level=6  # Good compression
                    )
                
                print(f"✅ Aggressively fixed: {filename}")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error fixing {filename}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count}/{total_files} PNG files")

# Run aggressive fix
if __name__ == "__main__":
    aggressive_png_fix("Hornet")