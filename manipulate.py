import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps

# Define manipulation types
MANIPULATION_TYPES = {
    'a': 'crop_20',
    'b': 'rotate_10',
    'c': 'flip_h',
    'd': 'brightness_1.3',
    'e': 'contrast_0.7',
    'f': 'gaussian_blur',
    'g': 'noise_saltpepper',
    'h': 'color_filter',
    'i': 'watermark',
    'j': 'canvas_expand',
    'k': 'jpeg_compression',
    'l': 'collage',
    'm': 'text_obfuscation',
    'n': 'invert_colors'
}

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # adjust if needed

def apply_manipulation(img, manipulation, originals_dir):
    if manipulation.startswith("crop"):
        percent = int(manipulation.split('_')[1])
        w, h = img.size
        crop_w = int(w * percent / 100)
        crop_h = int(h * percent / 100)
        return img.crop((crop_w, crop_h, w - crop_w, h - crop_h))

    elif manipulation.startswith("rotate"):
        angle = int(manipulation.split('_')[1])
        return img.rotate(angle, expand=True)

    elif manipulation == "flip_h":
        return img.transpose(Image.FLIP_LEFT_RIGHT)

    elif manipulation.startswith("brightness"):
        factor = float(manipulation.split('_')[1])
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)

    elif manipulation.startswith("contrast"):
        factor = float(manipulation.split('_')[1])
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)

    elif manipulation == "gaussian_blur":
        arr = np.array(img)
        blurred = cv2.GaussianBlur(arr, (7, 7), 0)
        return Image.fromarray(blurred)

    elif manipulation == "noise_saltpepper":
        arr = np.array(img)
        noise = np.copy(arr)
        num_salt = np.ceil(0.02 * arr.size)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in arr.shape]
        noise[tuple(coords)] = 255
        num_pepper = np.ceil(0.02 * arr.size)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in arr.shape]
        noise[tuple(coords)] = 0
        return Image.fromarray(noise)

    elif manipulation == "color_filter":
        arr = np.array(img).astype(np.float32)
        arr[..., 0] *= 1.2  # boost red
        arr[..., 1] *= 0.9  # lower green
        arr[..., 2] *= 1.1  # boost blue
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    elif manipulation == "watermark":
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        font = ImageFont.truetype(FONT_PATH, 36)
        text = "FAKE CLAIM"
        draw.text((10, 10), text, fill=(255, 0, 0, 128), font=font)
        return img_copy

    elif manipulation == "canvas_expand":
        return ImageOps.expand(img, border=50, fill="white")

    elif manipulation == "jpeg_compression":
        tmp_path = "temp.jpg"
        img.save(tmp_path, quality=20)  # low quality
        return Image.open(tmp_path)

    elif manipulation == "collage":
        files = [f for f in os.listdir(originals_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        chosen = np.random.choice(files, 3, replace=False)
        imgs = [Image.open(os.path.join(originals_dir, c)).resize(img.size) for c in chosen]
        new_w, new_h = img.size[0] * 2, img.size[1] * 2
        collage = Image.new("RGB", (new_w, new_h), (255, 255, 255))
        collage.paste(img, (0, 0))
        collage.paste(imgs[0], (img.size[0], 0))
        collage.paste(imgs[1], (0, img.size[1]))
        collage.paste(imgs[2], (img.size[0], img.size[1]))
        return collage

    elif manipulation == "text_obfuscation":
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        font = ImageFont.truetype(FONT_PATH, 50)
        draw.text((img.size[0]//4, img.size[1]//2), "😎", fill=(0, 0, 0), font=font)
        return img_copy

    elif manipulation == "invert_colors":
        arr = np.array(img)
        return Image.fromarray(255 - arr)

    return img

def apply_manipulations():
    originals_dir = "originals"
    output_dir = "manipulated"
    os.makedirs(output_dir, exist_ok=True)

    original_files = sorted([f for f in os.listdir(originals_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
    total_images = len(original_files)

    for i, filename in enumerate(original_files):
        img_path = os.path.join(originals_dir, filename)
        img = Image.open(img_path).convert("RGB")
        name = os.path.splitext(filename)[0]

        for letter, manipulation in MANIPULATION_TYPES.items():
            output_filename = f"{name}{letter}.jpg"
            output_path = os.path.join(output_dir, output_filename)
            manipulated_img = apply_manipulation(img, manipulation, originals_dir)
            manipulated_img.save(output_path)

        print(f"Processed {filename} ({i+1}/{total_images}) with {len(MANIPULATION_TYPES)} manipulations")

if __name__ == "__main__":
    apply_manipulations()