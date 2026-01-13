
import os
from PIL import Image

def convert_webp_to_jpg(file_path, quality=90, delete_original=False):
    """
    将 WebP 图片转换为 JPG。
    returns: new_file_path or None if failed
    """
    if not file_path.lower().endswith('.webp'):
        return None
        
    try:
        dir_name = os.path.dirname(file_path)
        name = os.path.splitext(os.path.basename(file_path))[0]
        new_path = os.path.join(dir_name, f"{name}.jpg")
        
        with Image.open(file_path) as img:
            rgb_im = img.convert('RGB')
            rgb_im.save(new_path, quality=quality)
            
        if delete_original:
            os.remove(file_path)
            
        return new_path
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return None
