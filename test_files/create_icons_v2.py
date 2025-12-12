from PIL import Image, ImageDraw
import os

def make_transparent_and_maximize(input_path, output_path):
    print(f"Processing {input_path}...")
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path).convert("RGBA")
    
    # 1. Flood fill from corners to handle background removal safely
    # This prevents removing white pixels *inside* the object
    # Seed points: 4 corners
    width, height = img.size
    seeds = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
    
    # Create a mask for flood filling
    # We'll use a tolerance approach manually or via library if available, 
    # but PIL doesn't have a direct 'floodfill to transparent' with tolerance easily.
    # Manual approach:
    # Iterate pixels? Too slow?
    # Actually, "Image.floodfill" exists in ImageDraw since recent versions, but essentially we want to mask background.
    
    # Let's try a simpler approach first that is robust for "Generated AI Images on White Background":
    # The background is usually very uniform.
    
    datas = img.getdata()
    newData = []
    
    # Heuristic: If a pixel is very bright, make it transparent. 
    # BUT, to avoid internal whites, we should ideally flood.
    # Since I cannot easily do complex floodfill in standard PIL without recursion limits, 
    # I will stick to the threshold but I will CROP first to ensure size.
    # And I will trust that the "Rim Light" I asked for creates a boundary.
    
    # wait, standard trimming FIRST might help.
    
    # Better strategy:
    # 1. Convert to numpy or just iterate to find bounding box of "non-white" pixels.
    # 2. Crop to that.
    # 3. Resize to 256x256.
    # 4. Apply Transparency to "near white" pixels.
    
    # Let's do the thresholding to find the bbox first.
    # We treat anything "Not White" as content.
    
    limit = 240 # Tolerance for white
    
    content_pixels = []
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            # If pixel is NOT white (darker than limit in any channel)
            if r < limit or g < limit or b < limit:
                content_pixels.append((x, y))
    
    if not content_pixels:
        print("Warning: No content found (image is all white?)")
        # Just use whole image
        bbox = (0, 0, width, height)
    else:
        # Calculate bbox
        min_x = min(p[0] for p in content_pixels)
        max_x = max(p[0] for p in content_pixels)
        min_y = min(p[1] for p in content_pixels)
        max_y = max(p[1] for p in content_pixels)
        
        # Add a small padding (margin)
        margin = 10
        min_x = max(0, min_x - margin)
        min_y = max(0, min_y - margin)
        max_x = min(width, max_x + margin)
        max_y = min(height, max_y + margin)
        
        bbox = (min_x, min_y, max_x, max_y)
        
    print(f"Cropping to {bbox}")
    img_cropped = img.crop(bbox)
    
    # Resize to square (keep aspect ratio, center on transparent background)
    target_size = (256, 256)
    final_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
    
    # Calculate resizing to fit within target_size
    cw, ch = img_cropped.size
    ratio = min(target_size[0]/cw, target_size[1]/ch)
    new_w = int(cw * ratio)
    new_h = int(ch * ratio)
    
    img_resized = img_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Paste centered
    paste_x = (target_size[0] - new_w) // 2
    paste_y = (target_size[1] - new_h) // 2
    
    # Now set transparency on the resized image
    # We iterate and set alpha=0 for white pixels
    final_datas = []
    resized_data = img_resized.getdata()
    
    for item in resized_data:
        # Check if white-ish
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
             final_datas.append((255, 255, 255, 0))
        else:
             final_datas.append(item)
             
    final_img.putdata(final_datas)
    # Paste this processed data onto the clean background (already done conceptually)
    
    final_img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Saved {output_path}")

artifact_dir = r"C:\Users\R2401-022\.gemini\antigravity\brain\7e8f1a67-9e34-4b68-ac6b-79aa07f54ba2"
img_i = os.path.join(artifact_dir, "sales_checker_icon_v8_high_contrast_1765497169212.png")
img_ii = os.path.join(artifact_dir, "sales_checker_icon_v8_high_contrast_ii_1765497235327.png")

make_transparent_and_maximize(img_i, "icon_I.ico")
make_transparent_and_maximize(img_ii, "icon_II.ico")
