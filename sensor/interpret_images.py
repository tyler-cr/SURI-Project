#!/usr/bin/env python3
from PIL import Image, ImageChops
from pathlib import Path
import sys

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



#TODO
def crop_image():
    a=5

#TODO
def convert_image_monochrome(color: tuple = ()):
    print("TODO")

if __name__ == "__main__":

    file_path = "/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/Spliced/averaged/spectrograms"

    all_spectros = [f.name for f in Path(file_path).iterdir() if f.is_file()]

    noise_spectros = [noise for noise in all_spectros if "noise" in noise]
    data_spectros = [data for data in all_spectros if "data" in data]

    noise_spectros.sort()
    data_spectros.sort()

    tutils.create_directory(f"{file_path}/compares")

    for i in range(len(noise_spectros)):
        print(f"creating image #{i+1} out of {len(noise_spectros)}")
        spectro_name = f"{noise_spectros[i][6:-4]}_noise_vs_data.png"
        large_image_compare(f"{file_path}/{data_spectros[i]}", f"{file_path}/{noise_spectros[i]}", f"{file_path}/compares/{spectro_name}")
    
