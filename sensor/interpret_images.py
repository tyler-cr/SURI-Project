#!/usr/bin/env python3
from PIL import Image, ImageChops

def image_diff(image1_path: str = "diff_test1.png", image2_path: str = "diff_test2.png", new_image_path: str = "image_diff.png"):
    img1 = Image.open(image1_path).convert("RGB")
    img2 = Image.open(image2_path).convert("RGB")

    print(img1.mode)
    print(img2.mode)

    diff_img = ImageChops.difference(img1, img2)

    # 3. Save or display the result
    diff_img.save(new_image_path)
    diff_img.show()

#TODO
def image_compare(image1_path: str, image2_path: str, layout: str = "vertical", new_image_path: str = "image_compare.png"):
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)

    new_width  = img1.width  + img2.width
    new_height = img1.height + img2.height

    combined_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))
    
    if layout == "vertical":
        combined_img.paste(img1, (0,0))
        combined_img.paste(img2, (0,img1.height))

    elif layout == "horizontal":
        combined_img.paste(img1, (0,0))
        combined_img.paste(img2, (img1.width,0))

    else: raise ValueError(f"layout must be string 'vertical' or 'horizontal'. Recieved: {layout}")

    



#TODO
def crop_image():
    a=5

if __name__ == "__main__":
    print("testing image diff")
    image_diff()