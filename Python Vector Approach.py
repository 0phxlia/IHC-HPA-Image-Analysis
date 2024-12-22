import cv2
import numpy as np
import pandas as pd
import os

#Define your input & output paths
input_folder = "path-to-your-input-folder-of-images"
output_folder = "path-to-your-output-folder-of-processed-images"
excel_output_path = "path-to-your-xlsx-file-output

#Create output folder if it doesn't already exist
os.makedirs(output_folder, exist_ok=True)

#Empty Data Frame to store the results,
all_results = []

#Create a loop through your input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and not filename.startswith('._'):
        image_path = os.path.join(input_folder, filename)
        output_image_path_processed = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_processed{os.path.splitext(filename)[1]}")

        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Warning: Skipping file {filename}, unable to read.")
            continue

        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue = hsv[:, :, 0] / 179.0  # Normalize hue to range 0 to 1
        saturation = hsv[:, :, 1]

        # Initialize masks for background and blue-stained areas
        background_mask = np.all(image > 215, axis=2) | np.all(image == 0, axis=2)  # White or black background
        blue_mask = (hue > 0.232) & (hue < 0.956)  # Blue hue range

        # Count the number of blue pixels
        blue_pixel_count = np.sum(blue_mask)

        # Combine masks for non-tissue areas
        non_tissue_mask = background_mask | blue_mask

        # Process the image to remove non-tissue areas
        processed_image = image.copy()
        processed_image[non_tissue_mask] = [255, 255, 255]  # Set non-tissue pixels to white

        # Convert the processed image to grayscale for intensity analysis
        gray_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # Find non-white pixels (brown tissue areas)
        brown_indices = np.where(gray_image != 255)
        brown_intensity = gray_image[brown_indices]

        # Calculate metrics
        average_intensity = 255 - np.mean(brown_intensity)
        sd_intensity = np.std(brown_intensity)
        percentiles = np.percentile(brown_intensity, [25, 50, 75])
        min_intensity = 255 - np.max(brown_intensity)
        max_intensity = 255 - np.min(brown_intensity)
        intensity_25 = 255 - percentiles[2]  # 75th percentile
        median_intensity = 255 - percentiles[1]  # Median intensity
        intensity_75 = 255 - percentiles[0]  # 25th percentile

        # Calculate areas
        brown_area = len(brown_intensity)  # Number of brown tissue pixels
        total_tissue_area = brown_area + blue_pixel_count  # Total tissue area = brown + blue pixels
        total_area = gray_image.size  # Total number of pixels in the image
        non_tissue_area = total_area - total_tissue_area  # Non-tissue area = total pixels - total tissue area
        brown_percentage = (
                                       brown_area / total_tissue_area) * 100 if total_tissue_area > 0 else 0  # Brown tissue percentage

        # Save the processed image
        cv2.imwrite(output_image_path_processed, processed_image)

        # Append results for this image to the Data Frame
        all_results.append({
            "Image Name": filename,
            "Average Intensity": average_intensity,
            "SD Intensity": sd_intensity,
            "Max Intensity": max_intensity,
            "75% Intensity": intensity_75,
            "Median Intensity": median_intensity,
            "25% Intensity": intensity_25,
            "Min Intensity": min_intensity,
            "Brown Area": brown_area,
            "Total Tissue Area": total_tissue_area,
            "Non-Tissue Area": non_tissue_area,
            "Blue Pixel Area": blue_pixel_count,
            "Brown Percentage": brown_percentage
        })

# Convert all results to a DataFrame
results_df = pd.DataFrame(all_results)

# Save results to Excel
results_df.to_excel(excel_output_path, index=False, engine='openpyxl')

print(f"Processed all images. Results saved in Excel at {excel_output_path}.")
