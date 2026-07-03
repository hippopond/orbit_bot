from PIL import Image, ImageFilter
import os

def clean_map():
    filepath = 'maze.pgm'
    try:
        img = Image.open(filepath)
    except IOError:
        print("Error: Could not load maze.pgm")
        return

    # A Median Filter is mathematically designed to completely erase "salt and pepper" noise
    # (tiny black dots) while perfectly preserving large solid shapes (walls).
    # We use a size of 5 pixels to aggressively erase all LiDAR dust.
    cleaned_img = img.filter(ImageFilter.MedianFilter(size=5))
    
    cleaned_img.save(filepath)
    print("Successfully erased LiDAR dust speckles using PIL Median Filter!")

if __name__ == '__main__':
    clean_map()
