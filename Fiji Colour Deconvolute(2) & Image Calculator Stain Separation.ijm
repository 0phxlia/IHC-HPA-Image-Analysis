//Input & Output File Paths
inputDirectory = "path-to-your-input-folder-of-images";
outputDirectory = "path-to-your-processed-folder";

// Get a list of all files in the input directory
fileList = getFileList(inputDirectory);

//Loop through each file
for (i = 0; i < fileList.length; i++) {
    fileName = fileList[i];
    filePath = inputDirectory + fileName;

    // Check if the file is an image (JPG format)
    if (endsWith(fileName, ".jpg")) {
        print("Processing file: " + fileName);

        //OPEN
        open(filePath);

        originalTitle = getTitle();
        originalTitleWithoutJPG = substring(originalTitle, 0, lengthOf(originalTitle) - 4);  // Remove ".jpg"

        //Clear results between each image
        run("Clear Results");

        //Duplicate orig image
        run("Duplicate...", "title=MaskImage");
        run("8-bit");

        // Threshold to identify white background areas (pixel intensity > 215)
        setThreshold(215, 255);
        run("Convert to Mask");

        imageCalculator("Add create", originalTitle, "MaskImage");
        
        //Close windows we've finished with
        selectWindow(originalTitle);
        close();
        selectWindow("MaskImage");
        close();

        // Run colour deconvolution(2) on background removed image
        run("Colour Deconvolution2", "vectors=[H DAB] output=8bit_Transmittance simulated cross hide");

        //Close green window (we don't need)
        selectWindow("Result of " + originalTitle + "-(Colour_3)");
        close();

        //Subtract blue from brown (Haematoxylin - DAB)
        imageCalculator("Subtract create", "Result of " + originalTitle + "-(Colour_1)", "Result of " + originalTitle + "-(Colour_2)");

        //Threshold
        setAutoThreshold("Li no-reset");
        run("Convert to Mask");

        // Close windows we have finished with 
        selectWindow("Result of " + originalTitle + "-(Colour_2)");
        close();
        selectWindow("Result of " + originalTitle + "-(Colour_1)");
        close();

        //Brown tissue image pull-through
        imageCalculator("Add create", "Result of " + originalTitle, "Result of Result of " + originalTitle + "-(Colour_1)");
        selectWindow("Result of Result of " + originalTitle);
        rename("BrownTissue");

        selectWindow("Result of Result of " + originalTitle + "-(Colour_1)");
        run("Invert LUT");

        //Blue tissue image pull-through 
        imageCalculator("Add create", "Result of " + originalTitle, "Result of Result of " + originalTitle + "-(Colour_1)");

        //Folder name in new directory
        imageFolder = outputDirectory + originalTitleWithoutJPG + "/";
        File.makeDirectory(imageFolder);

        // Save "BrownTissue" image
        selectWindow("BrownTissue");
        brownTissuePath = imageFolder + originalTitleWithoutJPG + " BrownTissue.jpg";
        saveAs("JPG", brownTissuePath);

        // Save "BlueTissue" image
        selectWindow("Result of Result of " + originalTitle);  // Make sure this is the correct window for blue tissue
        blueTissuePath = imageFolder + originalTitleWithoutJPG + " BlueTissue.jpg";
        saveAs("JPG", blueTissuePath);

        // Export the measurements
        resultsFile = imageFolder + originalTitleWithoutJPG + "_Measurements.csv";
        saveAs("Results", resultsFile);  // Save the results table as CSV in the same folder

        // Close all open windows to prepare for the next image
        while (nImages > 0) {
            selectImage(nImages);  // Select the last image
            close();  // Close it
        }
    } else {
        print("Skipping non-JPG file: " + fileName);
    }
}

close("*");
