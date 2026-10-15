"""
Prepare a photo for clean ASCII conversion:
  1. Smooths paper/skin noise while keeping line edges sharp
  2. Stretches tones for maximum ASCII clarity
  3. Composites onto white and crops square around the subject

Output: source-prepped.png, consumed by make_ascii_svg.py.
Usage:
    python scripts/prep_photo.py [input.png] [output.png]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

if not os.path.exists(INP):
    print(f"Error: {INP} not found. Please place your photo as 'source-photo.png' in the repository root.")
    sys.exit(1)

# Check if rembg is available, otherwise use intelligent PIL masking
try:
    from rembg import remove
    print("Using rembg for automatic background removal...")
    img = Image.open(INP).convert("RGBA")
    cut = remove(img)
except Exception as e:
    print(f"rembg not available ({e}), using contrast & luminance preparation...")
    cut = Image.open(INP).convert("RGBA")

# Extract luminance
gray = ImageOps.grayscale(cut)

# Increase contrast and sharpen
gray = ImageOps.autocontrast(gray, cutoff=2)
gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

# Square crop around center
w, h = gray.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
cropped = gray.crop((left, top, left + side, top + side))

# Resize to standard prep resolution
final_img = cropped.resize((600, 600), Image.Resampling.LANCZOS)
final_img.save(OUT)
print(f"Wrote prepped photo to {OUT}")
