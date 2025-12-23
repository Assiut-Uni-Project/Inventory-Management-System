import os
# barcode library is used to generate(create) new barcodes
from barcode import Code128
from barcode.writer import ImageWriter
# pyzbar library is used to read(scan) existing barcodes
from pyzbar.pyzbar import decode
from PIL import Image

# First: Define where we will save the generated images
# We create a specific folder to keep the project organized.
current_script_dir = os.path.dirname(os.path.abspath(__file__))
BARCODE_DIR = os.path.join(current_script_dir, "barcodes_images")

# Check if the folder exists. If not, create it.
if not os.path.exists(BARCODE_DIR):
    os.makedirs(BARCODE_DIR)


def generate_barcode(product_code):
    """
    Function Purpose is to create a barcode image for a specific product.

    Why we used Code128?
    - Because it supports both Numbers (0-9) and Letters (A-Z), unlike EAN-13 which only supports numbers.
    """
    try:
        # Step 1: Create the Barcode Object
        my_barcode_obj = Code128(product_code, writer=ImageWriter())
        
        # Step 2: Define the full path where the image will be saved
        save_path = os.path.join(BARCODE_DIR, product_code)
        
        # Step 3: Save the file to the disk
        fullname = my_barcode_obj.save(save_path)
        
        print(f"Barcode generated successfully at: {fullname}")
        return fullname
        
    except Exception as e:
        # If anything goes wrong (e.g., disk full, invalid characters), print the error
        print(f"Error generating barcode: {e}")
        return None
    

def read_barcode_from_image(image_path):
    """
    Function Purpose is to scan an image file and extracts the barcode data from it.
    (you upload a photo of a product instead of using a USB scanner).
    """
    try:
        # Step 1: Check if the file exists
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return []

        # Step 2: Open the image using Pillow (PIL) library (We need to load the image into memory before scanning it)
        img = Image.open(image_path)
        
        # Step 3: Decode the image using pyzbar
        decoded_objects = decode(img)
        
        results = []

        # Step 4: Loop through findings (an image might contain multiple barcodes)
        for obj in decoded_objects:
            # The library returns data in 'bytes' format (computer raw data). So,We must convert (decode) it to 'utf-8' string to be readable by humans.
            barcode_data = obj.data.decode("utf-8")
            results.append(barcode_data)
            
        return results # Returns a list of strings
    
    except Exception as e:
        print(f"Error reading image: {e}")
        return []
    

