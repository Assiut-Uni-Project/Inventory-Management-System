import os
# 'barcode' library is used to generate/create new barcodes
from barcode import Code128
from barcode.writer import ImageWriter
# 'barcode' library is used to generate/create new barcodes
from pyzbar.pyzbar import decode
from PIL import Image

# 1. SETUP: Define where we will save the generated images
# We create a specific folder to keep the project organized.
BARCODE_DIR = "barcodes_images"

# Check if the folder exists. If not, create it immediately.
if not os.path.exists(BARCODE_DIR):
    os.makedirs(BARCODE_DIR)


def generate_barcode(product_code):
    """
    Function Purpose: Creates a barcode image for a specific product.
    
    Why Code128? 
    - It is the standard for retail and inventory.
    - It supports both Numbers (0-9) and Letters (A-Z), unlike EAN-13 which only supports numbers.
    """
    try:
        # Step 1: Create the Barcode Object
        # We pass the 'product_code' (data) and 'ImageWriter()' (to tell python we want an image, not SVG)
        my_barcode_obj = Code128(product_code, writer=ImageWriter())
        
        # Step 2: Define the full path where the image will be saved
        # e.g., "barcodes_images/PROD-100"
        # Note: We do NOT add '.png' extension here because the library adds it automatically.
        save_path = os.path.join(BARCODE_DIR, product_code)
        
        # Step 3: Save the file to the disk
        # The .save() method returns the full filename including the extension (e.g., "PROD-100.png")
        fullname = my_barcode_obj.save(save_path)
        
        print(f"✅ Barcode generated successfully at: {fullname}")
        return fullname
        
    except Exception as e:
        # If anything goes wrong (e.g., disk full, invalid characters), print the error
        print(f"❌ Error generating barcode: {e}")
        return None
    

def read_barcode_from_image(image_path):
    """
    Function Purpose: Scans an image file and extracts the barcode data (numbers/text) from it.
    Useful if you want to upload a photo of a product instead of using a USB scanner.
    """
    try:
        # Step 1: Validation - Check if the file actually exists
        if not os.path.exists(image_path):
            print(f"❌ Error: Image file not found at {image_path}")
            return []

        # Step 2: Open the image using Pillow (PIL) library
        # We need to load the image into memory before scanning it
        img = Image.open(image_path)
        
        # Step 3: Decode the image using pyzbar
        # This function scans the pixels and looks for barcode patterns
        decoded_objects = decode(img)
        
        results = []
        # Step 4: Loop through findings (an image might contain multiple barcodes)
        for obj in decoded_objects:
            # IMPORTANT: The library returns data in 'bytes' format (computer raw data).
            # We must convert (decode) it to 'utf-8' string to be readable by humans.
            # Example: b'12345' -> "12345"
            barcode_data = obj.data.decode("utf-8")
            results.append(barcode_data)
            
        return results # Returns a list of strings, e.g., ['PROD-100']
    
    except Exception as e:
        print(f"❌ Error reading image: {e}")
        return []
    
