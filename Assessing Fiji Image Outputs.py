import os
import cv2
import numpy as np
import pandas as pd

#Define paths
root_directory = "path-to-your-images-from-Fiji"  #Replace
output_excel_path = "path-to-your-excel"  #Replace

# Results list
all_results = []

for folder_name in os.listdir(root_directory):
    folder_path = os.path.join(root_directory, folder_name)
    if not os.path.isdir(folder_path):
        continue  # Skip if not a directory

    brown_image_path = os.path.join(folder_path, f"{folder_name} BrownTissue.jpg")
    blue_image_path = os.path.join(folder_path, f"{folder_name} BlueTissue.jpg")

    if not os.path.exists(brown_image_path) or not os.path.exists(blue_image_path):
        continue

    brown_results = {}
    blue_results = {}

    # Process BrownTissue image
    brown_image = cv2.imread(brown_image_path)
    if brown_image is None:
        continue

    gray_brown = cv2.cvtColor(brown_image, cv2.COLOR_BGR2GRAY)

    white_threshold_min = 250
    white_threshold_max = 255
    white_mask = (gray_brown >= white_threshold_min) & (gray_brown <= white_threshold_max)
    background_mask = np.all(brown_image > 215, axis=2) | np.all(brown_image == 0, axis=2)
    tissue_mask = (gray_brown < white_threshold_min) & ~white_mask & ~background_mask
    tissue_intensity = gray_brown[tissue_mask]

    brown_results = {
        "Average Intensity": 255 - np.mean(tissue_intensity),
        "SD Intensity": np.std(tissue_intensity),
        "Max Intensity": 255 - np.min(tissue_intensity),
        "75% Intensity": 255 - np.percentile(tissue_intensity, 25),
        "Median Intensity": 255 - np.percentile(tissue_intensity, 50),
        "25% Intensity": 255 - np.percentile(tissue_intensity, 75),
        "Min Intensity": 255 - np.max(tissue_intensity),
        "Brown Tissue Area": np.sum(tissue_mask)
    }

    #Process BlueTissue image
    blue_image = cv2.imread(blue_image_path)
    if blue_image is None:
        continue

    #Convert blue image to grayscale for thresholding
    gray_blue = cv2.cvtColor(blue_image, cv2.COLOR_BGR2GRAY)

    #Define the white background threshold range (since you mentioned it's white)
    white_threshold_min = 250
    white_threshold_max = 255
    white_mask = (gray_blue >= white_threshold_min) & (gray_blue <= white_threshold_max)

    #Create a mask for "black" pixels with intensity between 0 and 40 (to ignore them)
    black_threshold_min = 0
    black_threshold_max = 40
    black_mask = (gray_blue >= black_threshold_min) & (gray_blue <= black_threshold_max)

    #Remove the white background by masking it (set white pixels to black)
    processed_blue = blue_image.copy()
    processed_blue[white_mask] = [0, 0, 0]  # Set white background pixels to black

    #Set black pixels (intensity 0-40) to black in the processed image
    processed_blue[black_mask] = [0, 0, 0]  # Black pixels remain black (or ignore them)

    #Create a mask for blue tissue (non-background, excluding black pixels)
    tissue_mask_blue = np.all(processed_blue != [0, 0, 0], axis=2) & ~black_mask

    #Calculate tissue area in the blue image
    tissue_area_blue = np.sum(tissue_mask_blue)

    #Calculate total area of the blue image (total number of pixels)
    total_area_blue = blue_image.size // 3  # Dividing by 3 since it's a color image with 3 channels (BGR)

    #Store the results for the blue tissue
    blue_results = {
        "Blue Tissue Area": tissue_area_blue,
        "Total Image Pixels": total_area_blue
    }

    total_tissue_area = brown_results["Brown Tissue Area"] + blue_results["Blue Tissue Area"]
    quantity = (brown_results["Brown Tissue Area"] / total_tissue_area * 100) if total_tissue_area > 0 else 0

    combined_results = {"Image Name": folder_name}
    combined_results.update(brown_results)
    combined_results.update(blue_results)
    combined_results["Quantity"] = quantity

    all_results.append(combined_results)

    del brown_results, blue_results, brown_image, blue_image, gray_brown, gray_blue, tissue_mask, tissue_mask_blue, tissue_intensity

#Convert results to DataFrame and save to Excel
results_df = pd.DataFrame(all_results)
results_df.to_excel(output_excel_path, index=False, engine='openpyxl')
