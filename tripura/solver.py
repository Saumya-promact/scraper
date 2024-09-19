import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import tempfile
import glob

def preprocess_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Apply dilation to remove noise
    kernel = np.ones((1, 1), np.uint8)
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    # Apply erosion to remove noise
    gray = cv2.erode(gray, kernel, iterations=1)
    
    # Apply median blur to remove noise
    gray = cv2.medianBlur(gray, 3)
    
    # Save the preprocessed image in a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        cv2.imwrite(temp_file.name, gray)
        temp_filename = temp_file.name
    
    return temp_filename

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path):
    # Preprocess the image
    preprocessed_image_path = preprocess_image(image_path)
    
    # Extract text from the image
    text = pytesseract.image_to_string(Image.open(preprocessed_image_path), lang='eng', config='--psm 6')
    
    # Remove the temporary file
    os.unlink(preprocessed_image_path)
    
    return text

def get_desktop_path():
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def get_image_files(directory):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    return image_files

def main():
    desktop_path = get_desktop_path()
    image_files = get_image_files(desktop_path)
    
    if not image_files:
        print("No image files found on the desktop.")
        return
    
    print("Found the following image files on your desktop:")
    for i, file in enumerate(image_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    while True:
        try:
            choice = int(input("Enter the number of the image you want to process (or 0 to exit): "))
            if choice == 0:
                print("Exiting the program.")
                return
            if 1 <= choice <= len(image_files):
                selected_image = image_files[choice - 1]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    print(f"Processing image: {os.path.basename(selected_image)}")
    extracted_text = extract_text(selected_image)
    print("\nExtracted Text:")
    print(extracted_text)

if __name__ == "__main__":
    main()