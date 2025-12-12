from PIL import Image
import os
import math

def distance(c1, c2):
    return math.sqrt(sum((a-b)**2 for a, b in zip(c1, c2)))

def process_icon_v3(input_path, output_path):
    print(f"Processing {input_path}...")
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # Analyze background color from the top-left corner
    bg_color = img.getpixel((0, 0))[:3] # Ignore alpha if present for now
    print(f"Detected background color: {bg_color}")
    
    # Create new image data with transparency
    datas = img.getdata()
    newData = []
    
    # 1. Determine content pixels (for cropping)
    # 2. Build transparent pixel list
    
    content_xs = []
    content_ys = []
    
    tolerance = 50 # Increase tolerance to catch shadows/rims that should be transparent
    
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            item = datas[idx]
            
            # Check similarity to background
            dist = distance(item[:3], bg_color)
            
            if dist < tolerance:
                # Top-left corner color match -> Transparent
                newData.append((255, 255, 255, 0))
            else:
                # Check for "pure white" as well just in case corners are slightly gray but background is white
                # (Handle the user's specific complaint about white squares)
                if item[0] > 250 and item[1] > 250 and item[2] > 250:
                     newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
                    content_xs.append(x)
                    content_ys.append(y)
    
    # Create the transparent image first (full size)
    temp_img = Image.new("RGBA", (width, height))
    temp_img.putdata(newData)
    
    if not content_xs:
        print("Warning: Image seems empty after removing background!")
        bbox = (0, 0, width, height)
    else:
        # Crop
        margin = 0 # No margin, user wants it BIG
        min_x = max(0, min(content_xs) - margin)
        max_x = min(width, max(content_xs) + margin)
        min_y = max(0, min(content_ys) - margin)
        max_y = min(height, max(content_ys) + margin)
        bbox = (min_x, min_y, max_x+1, max_y+1)
    
    print(f"Cropping to content: {bbox}")
    img_cropped = temp_img.crop(bbox)
    
    # Resize to 256x256
    target_size = (256, 256)
    
    # Scale to fit maximal dimension while preserving aspect ratio
    cw, ch = img_cropped.size
    scale = min(target_size[0]/cw, target_size[1]/ch)
    new_w = int(cw * scale)
    new_h = int(ch * scale)
    
    print(f"Resizing to {new_w}x{new_h}")
    img_resized = img_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Place on 256x256 canvas
    final_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
    paste_x = (target_size[0] - new_w) // 2
    paste_y = (target_size[1] - new_h) // 2
    final_img.paste(img_resized, (paste_x, paste_y))
    
    final_img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Saved {output_path}")

artifact_dir = r"C:\Users\R2401-022\.gemini\antigravity\brain\7e8f1a67-9e34-4b68-ac6b-79aa07f54ba2"
img_i = os.path.join(artifact_dir, "sales_checker_icon_v9_gold_1765498401092.png")
img_ii = os.path.join(artifact_dir, "sales_checker_icon_v9_gold_ii_1765498416940.png")

process_icon_v3(img_i, "icon_I.ico")
process_icon_v3(img_ii, "icon_II.ico")
