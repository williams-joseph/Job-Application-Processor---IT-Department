from PIL import Image
import os
import sys

def create_assets():
    """
    Generates icon.ico and logo_square.png from a source logo.png.
    Useful for updating brand assets on any OS.
    """
    logo_path = "logo.png"
    if not os.path.exists(logo_path):
        print(f"Error: {logo_path} not found. Please ensure logo.png exists in this folder.")
        return

    print(f"Processing {logo_path}...")
    img = Image.open(logo_path)
    
    # Create square version with padding to avoid stretching
    width, height = img.size
    new_size = max(width, height)
    
    # Create a new transparent square image
    square_img = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))
    
    # Paste the original image into the center
    offset = ((new_size - width) // 2, (new_size - height) // 2)
    square_img.paste(img, offset)
    
    # Save logo_square.png
    square_img.save("logo_square.png")
    print("Successfully created logo_square.png")
    
    # Save icon.ico (includes multiple standard sizes for Windows)
    # Typical Windows icon sizes: 16, 32, 48, 64, 128, 256
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    # Filter sizes so we don't upscale the original too much
    valid_sizes = [s for s in icon_sizes if s[0] <= new_size]
    if not valid_sizes:
        valid_sizes = [(32, 32)] 
        
    try:
        square_img.save("icon.ico", sizes=valid_sizes)
        print("Successfully created icon.ico")
    except Exception as e:
        print(f"Error creating icon.ico: {e}")

if __name__ == "__main__":
    create_assets()
