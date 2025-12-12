from PIL import Image
import os

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    # Simple thresholding for white background
    # This assumes the background is very close to pure white and the object doesn't have such white on edges
    for item in datas:
        if item[0] > 245 and item[1] > 245 and item[2] > 245:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    
    # Save as ICO containing multiple sizes for best scaling in Windows
    img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Successfully created {output_path}")

artifact_dir = r"C:\Users\R2401-022\.gemini\antigravity\brain\7e8f1a67-9e34-4b68-ac6b-79aa07f54ba2"
# Filenames obtained from previous turns
img_i = os.path.join(artifact_dir, "sales_checker_icon_v8_high_contrast_1765497169212.png")
img_ii = os.path.join(artifact_dir, "sales_checker_icon_v8_high_contrast_ii_1765497235327.png")

process_image(img_i, "icon_I.ico")
process_image(img_ii, "icon_II.ico")
