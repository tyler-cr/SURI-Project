#!/usr/bin/env python3
from PIL import Image, ImageChops
from pathlib import Path

def image_diff(image1_path: str = "test1.png", image2_path: str = "test2.png", new_image_path: str = "image_diff.png"):
    img1 = Image.open(image1_path).convert("RGB")
    img2 = Image.open(image2_path).convert("RGB")

    diff_img = ImageChops.difference(img1, img2)

    # 3. Save or display the result
    diff_img.save(new_image_path)


def image_compare(image1_path: str = "test1.png", image2_path: str = "test2.png", layout: str = "vertical", new_image_path: str = "image_compare.png"):
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

if __name__ == "__main__":
    print("testing image compare")
    large_image_compare(image1_path="WAV_files/InvertPhase_vs_Stereo/Spectrograms/100Hz10Vpp_mixed_PI_sample1.png", image2_path="WAV_files/InvertPhase_vs_Stereo/Spectrograms/100Hz10Vpp_mixed_Stereo_sample1.png",new_image_path="doubletest.png")
