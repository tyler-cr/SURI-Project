#!/usr/bin/env python3
from PIL import Image, ImageChops, ImageOps
from pathlib import Path
import sys
import random
import numpy as np

sys.path.insert(1, "/Users/tylercrimando/SURI-Project/utils")

import tutils

def image_diff(image1_path: str = "test1.png", image2_path: str = "test2.png", new_image_path: str = "image_diff.png"):
    """
    Compare two images and highlight their differences.
    
    Loads two images, finds where they don't match, and saves the result as a 
    difference image (bright pixels = different areas). Perfect for spotting 
    changes between spectrograms or version comparisons!
    
    Args:
        image1_path: Path to the first image. Defaults to 'test1.png'.
        image2_path: Path to the second image. Defaults to 'test2.png'.
        new_image_path: Where to save the difference image. Defaults to 'image_diff.png'.
        
    Returns:
        None. Just drops the diff image on your disk.
    """

    img1 = Image.open(image1_path).convert("RGB")
    img2 = Image.open(image2_path).convert("RGB")

    diff_img = ImageChops.difference(img1, img2)

    # 3. Save or display the result
    diff_img.save(new_image_path)


def image_compare(image1_path: str = "test1.png", image2_path: str = "test2.png", layout: str = "vertical", new_image_path: str = "image_compare.png"):
    """
    Stack two images together for easy visual comparison.
    
    Paste your images side-by-side or top-to-bottom on a clean white background.
    Great for putting spectrograms next to each other to spot differences!
    
    Args:
        image1_path: Path to the first image. Defaults to 'test1.png'.
        image2_path: Path to the second image. Defaults to 'test2.png'.
        layout: How to arrange them—'vertical' (stacked) or 'horizontal' (side-by-side).
        new_image_path: Where to save the combined image. Defaults to 'image_compare.png'.
        
    Returns:
        None. Drops the combined image on disk for you to inspect.
        
    Note:
        Images of different sizes are fine—they'll get padded with white space 
        so everything lines up nicely.
    """    
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)

    
    if layout == "vertical":

        new_width  = max(img1.width, img2.width)
        new_height = img1.height + img2.height

        combined_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        combined_img.paste(img1, (0,0))
        combined_img.paste(img2, (0,img1.height))

    elif layout == "horizontal":

        new_width  = img1.width  + img2.width
        new_height = max(img1.height, img2.height)

        combined_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        combined_img.paste(img1, (0,0))
        combined_img.paste(img2, (img1.width,0))

    else: raise ValueError(f"layout must be string 'vertical' or 'horizontal'. Recieved: {layout}")

    combined_img.save(new_image_path)


def large_image_compare(image1_path: str = "test1.png", image2_path: str = "test2.png", new_image_path: str = "large_image_compare.png"):
    """
    Generate a composite comparison image showing two views side-by-side.
    
    The output layout includes:
    1. The original images stacked vertically on the left.
    2. A pixel-level difference map (highlights variations) on the right.
    
    This function creates temporary intermediate files to assemble the final result
    and automatically cleans them up upon completion. Useful for analyzing subtle
    differences in spectrograms or sensor data outputs.
    
    Args:
        image1_path: Path to the first image. Defaults to 'test1.png'.
        image2_path: Path to the second image. Defaults to 'test2.png'.
        new_image_path: Destination path for the final composite image. Defaults to 'large_image_compare.png'.
        
    Returns:
        None. Saves the combined image and removes temporary files.
    """    
    
    image_compare(image1_path=image1_path, image2_path=image2_path, new_image_path="temp_comp.png")
    image_diff(image1_path=image1_path, image2_path=image2_path, new_image_path="temp_diff.png")
    image_compare(image1_path="temp_comp.png", image2_path="temp_diff.png" , layout="horizontal", new_image_path=new_image_path)

    diff_path = Path("temp_diff.png")
    comp_path = Path("temp_comp.png")
    diff_path.unlink(missing_ok=True)
    comp_path.unlink(missing_ok=True)


def batch_image_crop(image_dir: str = None, crop: list | tuple | int = None):
    """
    Batch crops all images in a directory by specified margin amounts.

    Args:
        image_dir: Path to directory containing source images (.png, .jpg, .jpeg)
        crop: Crop dimensions as either:
              • int: Applies equal margin to all 4 sides
              • list/tuple: [left_margin, top_margin, right_margin, bottom_margin]

    Returns:
        None (images saved directly to <image_dir>/cropped/)

    Notes:
        • Output files named: {original_stem}_cropped.{ext}
        • Creates 'cropped' subdirectory automatically
        • Supports extensions: .png, .jpg, .jpeg
        • Uses margin-based indexing (removes pixels from edges)
    
    Raises:
        FileNotFoundError: If image_dir doesn't exist
        ValueError: If crop parameters exceed image dimensions
        TypeError: If crop has wrong type
    """

    #this looks goofy if you don't know programming
    if type(crop) == int: crop = [crop, crop, crop, crop]

    if image_dir[-1] == "/": image_dir = image_dir[:-1]

    cropped_dir = f"{image_dir}/cropped"

    tutils.create_directory(f"{image_dir}/cropped")
    
    #No need to handle other file extensions... this should be fine!
    all_images = [f for f in Path(image_dir).iterdir() if f.suffix in [".png", ".jpg", ".jpeg"]]

    for image_file in all_images:
        img = Image.open(image_file)

        crop = [crop[0], crop[1], img.width-crop[2], img.height-crop[3]]

        img = img.crop(crop)

        print(cropped_dir)
        print(image_file)

        new_image_file_path = f"{cropped_dir}/{image_file.stem}_cropped{image_file.suffix}"

        print(f"New Cropped Image saved at: {new_image_file_path}")
        img.save(new_image_file_path)
        


#TODO: This is tremendously rudementary... make better (later)
def convert_image_monochrome(image_file: str, color: tuple = None):
    """
    Converts an image to monochrome with optional custom color mapping.

    Args:
        image_file: Path to input image file (.png, .jpg, .jpeg)
        color: RGB tuple for tinting grayscale image (e.g., (255, 128, 0))
               If None, saves as standard black-and-white

    Returns:
        None (images saved directly to same directory as source)

    Notes:
        • Grayscale conversion via PIL 'L' mode
        • Custom colors use ImageOps.colorize() mapping: 
          Black → Color ← White
        • Output filenames:
          - No color: {original_stem}_monochrome_bw.{ext}
          - With color: {original_stem}_monochrome_{R}{G}{B}.{ext}
        • Colored versions auto-display after saving
    
    Raises:
        FileNotFoundError: If image_file doesn't exist
        TypeError: If color has wrong type or length ≠ 3
        OSError: If file cannot be written
    """

    if color is None:
        print(f"NOTE: No color passed in for {image_file} monochrome convert. Defaulting to BnW!")

    img = Image.open(image_file).convert('L')

    if color is None: 
        img.save(f"{image_file[:-4]}_monochrome_bw{image_file.split('.')[0]}")
        return
    
    newimg = ImageOps.colorize(img, mid = color, black="black", white="white")
    newimg.save(f"{image_file[:-4]}_monochrome_{color[0]}{color[1]}{color[2]}{image_file[-4:]}")
    newimg.show()



if __name__ == "__main__":

    image_dir="/Users/tylercrimando/SURI-Project/test_images/test_image.png"

    convert_image_monochrome(image_file=image_dir, color=(255,255,0))
    exit()

    crop_arr = np.random.randint(25, size=4)
    print(crop_arr)

    batch_image_crop(image_dir="/Users/tylercrimando/SURI-Project/test_images", crop=crop_arr)
    
