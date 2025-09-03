import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
if not PIXABAY_API_KEY:
    raise ValueError("PIXABAY_API_KEY not found in .env file")

SEARCH_QUERY = "art"  # You can change this to different search terms
IMAGES_TO_DOWNLOAD = 600
ORIGINALS_FOLDER = "originals"

def fetch_images_from_pixabay():
    # Create originals directory if it doesn't exist
    if not os.path.exists(ORIGINALS_FOLDER):
        os.makedirs(ORIGINALS_FOLDER)
        print(f"Created directory: {ORIGINALS_FOLDER}")
    
    # Check if we already have enough images
    existing_images = len([name for name in os.listdir(ORIGINALS_FOLDER) 
                          if name.startswith("art_") and name.endswith((".jpg", ".jpeg", ".png"))])
    
    if existing_images >= IMAGES_TO_DOWNLOAD:
        print(f"Already have {existing_images} images. No need to download more.")
        return
    
    print(f"Downloading {IMAGES_TO_DOWNLOAD - existing_images} images from Pixabay...")
    
    # Pixabay API endpoint
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={SEARCH_QUERY}&image_type=photo&per_page=200"
    
    downloaded_count = existing_images
    page = 1
    
    while downloaded_count < IMAGES_TO_DOWNLOAD:
        # Make API request
        response = requests.get(f"{url}&page={page}")
        
        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            break
        
        data = response.json()
        
        # Check if we have any hits
        if 'hits' not in data or len(data['hits']) == 0:
            print("No more images available from Pixabay.")
            break
        
        # Process each image in the results
        for image_data in data['hits']:
            if downloaded_count >= IMAGES_TO_DOWNLOAD:
                break
                
            try:
                # Get the image URL (prefer large image if available)
                image_url = image_data.get('largeImageURL') or image_data.get('webformatURL')
                
                if not image_url:
                    continue
                
                # Download the image
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code != 200:
                    continue
                
                # Open the image and convert to RGB if necessary
                img = Image.open(BytesIO(img_response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to a manageable size while maintaining aspect ratio
                max_size = (1024, 1024)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save the image with the required naming pattern
                img_filename = f"art_{downloaded_count + 1}.jpg"
                img_path = os.path.join(ORIGINALS_FOLDER, img_filename)
                img.save(img_path, "JPEG", quality=85)
                
                downloaded_count += 1
                print(f"Downloaded and saved: {img_filename}")
                
            except Exception as e:
                print(f"Error processing image: {e}")
                continue
        
        page += 1
        
        # Safety check to avoid infinite loops
        if page > 50:  # Pixabay has a limit of pages anyway
            print("Reached maximum page limit.")
            break
    
    print(f"Download completed. Total images: {downloaded_count}")

if __name__ == "__main__":
    fetch_images_from_pixabay()