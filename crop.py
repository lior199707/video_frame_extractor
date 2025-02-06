import os
from PIL import Image

def crop_images_in_folder(folder_path, output_folder, crop_box):
    """
    Crops all images in the specified folder.

    Args:
        folder_path (str): Path to the folder containing images.
        output_folder (str): Path to save the cropped images.
        crop_box (tuple): The crop rectangle, as a (left, upper, right, lower)-tuple.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif')):
            file_path = os.path.join(folder_path, filename)

            try:
                with Image.open(file_path) as img:
                    # Crop the image
                    cropped_img = img.crop(crop_box)

                    # Save the cropped image to the output folder
                    output_path = os.path.join(output_folder, filename)
                    cropped_img.save(output_path)

                    print(f"Cropped and saved: {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
print(5)

if __name__ == "__main__":
    # Input folder containing images
    folder_path = "path/to/your/image/folder"
    folder_path = "ex7_11mm_10perc_15012025"
    print(5)

    # Output folder for cropped images
    output_folder = "ex7_11mm_10perc_15012025_cropped"

    # Crop dimensions: (left, upper, right, lower)
    crop_box = (582, 143, 1600, 670)  # Example crop dimensions

    crop_images_in_folder(folder_path, output_folder, crop_box)