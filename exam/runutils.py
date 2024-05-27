# Import necessary functions from ocr_utils.py
from ocr_utils import pdf_to_images, detect_text_regions, extract_text_with_context

# Path to your PDF file
pdf_path = "C:\Users\USER\Documents\WebProjects\EssayGradingBE\EssayGrading\media\CamScanner 05-27-2024-CYB.pdf"

# Convert PDF to a list of images
images = pdf_to_images(pdf_path)

# Process each image
for idx, image in enumerate(images):
    # Detect text regions in the image
    boxes = detect_text_regions(image)

    # Extract text with context from the image using OCR
    results = extract_text_with_context(image, boxes)

    # Display the results
    print(f"Text extracted from page {idx + 1}:")
    for (startX, startY, endX, endY), text in results:
        print(f"Bounding box: ({startX}, {startY}, {endX}, {endY})")
        print("Text:", text)
