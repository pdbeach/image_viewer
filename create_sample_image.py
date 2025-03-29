#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image(filename="sample_image.png", size=(800, 600), bg_color=(50, 120, 200)):
    """Create a sample image for testing the image viewer."""
    # Create a new image with the given background color
    image = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw some shapes
    # Rectangle
    draw.rectangle([(50, 50), (300, 200)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    
    # Circle
    draw.ellipse([(500, 100), (700, 300)], fill=(255, 200, 0), outline=(0, 0, 0), width=2)
    
    # Line
    draw.line([(100, 400), (700, 500)], fill=(255, 0, 0), width=5)
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    draw.text((250, 300), "Sample Image", fill=(255, 255, 255), font=font)
    
    # Save the image
    image.save(filename)
    print(f"Sample image created: {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_sample_image()
