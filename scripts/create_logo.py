from PIL import Image, ImageDraw
import os

target_dir = r"E:\aivideoyap\public\illustrations"
os.makedirs(target_dir, exist_ok=True)
target_path = os.path.join(target_dir, "logo.png")

img = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
# Draw stylish circular glowing logo
d.ellipse((20, 20, 280, 280), fill=(245, 158, 11, 230), outline=(255, 255, 255, 255), width=8)
d.ellipse((50, 50, 250, 250), fill=(16, 24, 39, 240))
img.save(target_path)
print(f"Created {target_path} - Exists: {os.path.exists(target_path)}")
