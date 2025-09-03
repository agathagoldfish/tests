import os
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps
from imagehash import phash
import pandas as pd
import cv2

# Updated manipulation types (a–n)
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

# --- Feature extraction and matching ---
def extract_features(img, method='phash'):
    if method == 'phash':
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        hash_value = phash(img)
        return hash_value, None
    return None, None

def match_features(desc1, desc2, method='phash'):
    if desc1 is None or desc2 is None:
        return []
    if method == 'phash':
        distance = desc1 - desc2
        class MockMatch:
            def __init__(self, dist):
                self.distance = dist
        return [MockMatch(distance)]
    return []

def calculate_match_score(matches, method='phash', threshold=0.75):
    if not matches:
        return 0
    if method == 'phash':
        distance = matches[0].distance
        return (64 - distance) / 64 * 100
    return 0

def detect_matches(original_path, manipulated_path, method='phash'):
    try:
        img1 = Image.open(original_path)
        img2 = Image.open(manipulated_path)
    except (IOError, FileNotFoundError):
        return 0
    img1_gray = img1.convert('L')
    img2_gray = img2.convert('L')
    hash1, _ = extract_features(img1_gray, method)
    hash2, _ = extract_features(img2_gray, method)
    matches = match_features(hash1, hash2, method)
    return calculate_match_score(matches, method)

# --- Manipulation helpers ---
def get_manipulation_name(letter_code):
    return MANIPULATION_TYPES.get(letter_code, 'unknown')

def get_all_manipulation_types():
    return list(MANIPULATION_TYPES.values())

def get_manipulation_letter_code(manip_name):
    for letter, name in MANIPULATION_TYPES.items():
        if name == manip_name:
            return letter
    return None

def create_results_dataframe():
    columns = ['image_id'] + get_all_manipulation_types() + ['method', 'avg_score']
    return pd.DataFrame(columns=columns)

def analyze_results(df, method):
    summary = {}
    manipulation_types = get_all_manipulation_types()
    for manip in manipulation_types:
        if manip in df.columns:
            summary[manip] = {
                'mean': df[manip].mean(),
                'median': df[manip].median(),
                'std': df[manip].std(),
                'min': df[manip].min(),
                'max': df[manip].max()
            }
    hardest_manip = min(summary.items(), key=lambda x: x[1]['mean'])
    return summary, hardest_manip

def save_visualization(df, method, output_path):
    import matplotlib.pyplot as plt
    import seaborn as sns
    manipulation_types = get_all_manipulation_types()
    plt.figure(figsize=(14, 8))
    plt.subplot(1, 2, 1)
    sns.boxplot(data=df[manipulation_types])
    plt.title(f'Match Scores by Manipulation Type ({method.upper()})')
    plt.xticks(rotation=45)
    plt.subplot(1, 2, 2)
    means = [df[manip].mean() for manip in manipulation_types]
    plt.bar(range(len(manipulation_types)), means)
    plt.xticks(range(len(manipulation_types)), manipulation_types, rotation=45)
    plt.title('Average Match Scores')
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f'{method}_results_analysis.png'))
    plt.close()

# --- Apply manipulations ---
def apply_manipulation(image, manipulation_code, originals_dir=None):
    if manipulation_code == 'a':  # crop_20
        w, h = image.size
        crop_w, crop_h = int(w * 0.2), int(h * 0.2)
        return image.crop((crop_w, crop_h, w - crop_w, h - crop_h))

    elif manipulation_code == 'b':  # rotate_10
        return image.rotate(10, expand=True)

    elif manipulation_code == 'c':  # flip_h
        return image.transpose(Image.FLIP_LEFT_RIGHT)

    elif manipulation_code == 'd':  # brightness_1.3
        return ImageEnhance.Brightness(image).enhance(1.3)

    elif manipulation_code == 'e':  # contrast_0.7
        return ImageEnhance.Contrast(image).enhance(0.7)

    elif manipulation_code == 'f':  # gaussian_blur
        arr = np.array(image)
        blurred = cv2.GaussianBlur(arr, (7, 7), 0)
        return Image.fromarray(blurred)

    elif manipulation_code == 'g':  # noise_saltpepper
        arr = np.array(image)
        noise = arr.copy()
        num_salt = np.ceil(0.02 * arr.size)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in arr.shape]
        noise[tuple(coords)] = 255
        num_pepper = np.ceil(0.02 * arr.size)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in arr.shape]
        noise[tuple(coords)] = 0
        return Image.fromarray(noise)

    elif manipulation_code == 'h':  # color_filter
        arr = np.array(image).astype(np.float32)
        arr[..., 0] *= 1.2
        arr[..., 1] *= 0.9
        arr[..., 2] *= 1.1
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    elif manipulation_code == 'i':  # watermark
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        font = ImageFont.truetype(FONT_PATH, 36)
        draw.text((10, 10), "FAKE CLAIM", fill=(255, 0, 0, 128), font=font)
        return img_copy

    elif manipulation_code == 'j':  # canvas_expand
        return ImageOps.expand(image, border=50, fill="white")

    elif manipulation_code == 'k':  # jpeg_compression
        tmp_path = "temp.jpg"
        image.save(tmp_path, quality=20)
        return Image.open(tmp_path)

    elif manipulation_code == 'l':  # collage
        if originals_dir is None:
            return image
        files = [f for f in os.listdir(originals_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        chosen = np.random.choice(files, 3, replace=False)
        imgs = [Image.open(os.path.join(originals_dir, c)).resize(image.size) for c in chosen]
        new_w, new_h = image.size[0]*2, image.size[1]*2
        collage = Image.new("RGB", (new_w, new_h), (255, 255, 255))
        collage.paste(image, (0, 0))
        collage.paste(imgs[0], (image.size[0], 0))
        collage.paste(imgs[1], (0, image.size[1]))
        collage.paste(imgs[2], (image.size[0], image.size[1]))
        return collage

    elif manipulation_code == 'm':  # text_obfuscation
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        font = ImageFont.truetype(FONT_PATH, 50)
        draw.text((image.size[0]//4, image.size[1]//2), "😎", fill=(0, 0, 0), font=font)
        return img_copy

    elif manipulation_code == 'n':  # invert_colors
        arr = np.array(image)
        return Image.fromarray(255 - arr)

    return image