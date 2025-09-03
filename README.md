# tests

1. First, let's set up a virtual environment:
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

2. Install the dependencies
pip install --upgrade pip
pip install -r requirements.txt

3. Set up environment file:
Create/edit your .env file:
nano .env

Add your Pixabay API key:
PIXABAY_API_KEY=your_actual_api_key_here

Save and exit (Ctrl+X, then Y, then Enter)

4. Run these commands:

python fetch_images.py

sudo apt-get update
sudo apt-get install -y libgl1

python manipulate.py

python detect.py