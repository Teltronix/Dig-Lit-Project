from PIL import Image
import os

# Set the folder containing your frame images
folder = "ezgif-split"  # Replace with your folder name
files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])

# Load all images
images = [Image.open(os.path.join(folder, f)) for f in files]
width, height = images[0].size

# Create a new blank sprite sheet
sheet = Image.new('RGBA', (width * len(images), height))

# Paste each frame into the sprite sheet
for index, image in enumerate(images):
    sheet.paste(image, (index * width, 0))  # Horizontally

# Save the sprite sheet
sheet.save('Person.png')
