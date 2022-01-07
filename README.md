# DNA-Nanotube-Lengths
The goal of this project is to automate length measurements of fluorescently labeled filaments, in this case DNA nanotubes, from epifluorescence micrographs using Python, and sort the resulting output files with bash. While the process of measuring filament characteristics is automated in this script, I recommend working in parallel with visual inspection of the images being processed using [FIJI](https://imagej.net/software/fiji/) [1], or an equivalent software. This allows for both confirmation that the results are representative of the images being processed, and for tuning of the input-parameters to optimize results. The script “nanotube_threshold.py” may but run on individual files one at a time, or run on all files in a given directory using the additional bash script “run_nanotubeThreshold_allFilesInDirectory.sh”. Further instruction on running the code is included below the project description and in “suggestedProjectProtocol.pdf”.

The main script in this repository, "nanotube_threshold.py", allows the user to extract length measurements from fluorescence micrographs. This Python script is adaptable to process images even in the case of minor issues, such as uneven illumination across the image, small fluorescent smears, etc. Of course, I advocate for taking the highest quality images as possible during data acquisition, but sometimes stuff happens. The general protocol of the script is as follows: generate an approximation of the background for the image, subtract the background from the image, threshold and thin the result and remove any intersecting objects before measuring lengths. Further explanations can be found within the python file itself.

This script may also be applied to other types of microscopy images in which filaments are brighter than the background, or is easily modified for images in which the filaments are darker than the background. Please feel free to reach out to the author for advice on this if needed. The “nanotube_threshold.py” is written to read Nikon .nd2 files, which include metadata for microns per pixel of the image. For users working with tifs, I’ve included versions of the script which will read in 16-bit tif images in the “forTifs” folder. The user will have to input the pixel to micron conversion based on their microscopy system as the parameter “pix_micron” in units of micron/pixel.

I’ve included a “suggestedProjectProtocol.pdf” with more detailed instructions for organizing a project, running the scripts, and doing visual confirmation with FIJI during processing. For simple command instructions and input/output files see below.

This project relies on a number of Python packages, including [scikit-image](https://scikit-image.org) [2] and [pandas](https://pandas.pydata.org) [3] [4]. 
Dependencies are listed in the ".dependencies" file. This project also uses ND2Reader from [nd2reader](https://github.com/rbnvrw/nd2reader). 

If you find this repository helpful or use it to generate published data, please cite it using the DOI certificate under "Releases" on the right-hand side menu. Questions can be sent to the author by email at klocke@ucr.edu

### Additional packages to install before running
ND2Reader from [nd2reader](https://github.com/rbnvrw/nd2reader)

### Processing individual images
How to process individual microscopy files, such as during input-parameter optimization or initial exploration of the script. The “nanotube_threshold.py” file must be in the same directory as the image being processed. Running the “nanotube_threshold.py” script will generate a new directory “\_figs” in which output files will be stored. The script generates 3 output files per image. A $fn_lengths.csv file contains the lengths of all detected filaments in an image. A $fn_runvalues.csv file contains a list of the user-input parameter settings for the run. A binary $fn_noBranches_dilate.png image of the measured filaments is generated for visual confirmation with the original micrograph. Note, the lengths are measured from thinned, 1-pixel wide filaments, but the diagnostic $fn_noBranches_dilate.png image has been binary dilated to make the filaments easier to see. Instructions are for processing nd2 files. When processing tif files, substitute “nd2” for “tif” in the below instructions and use the “tif_nanotube_threshold.py” script instead.

**Input files in project directory:** nanotube_threshold.py, $fn.nd2 where "$fn" is your filename

**Output files in project/\_figs directory:** $fn_lengths.csv, $fn_runvalues.csv, $fn_noBranches_dilate.png

**Commands:**
```
    python nanotube_threshold.py $fn.nd2 
```
### Processing all images in a directory
To process all microscopy files within the same directory as the “nanotube_threshold.py” script. I recommend running only a single time-point and condition at a time, as the scripts for sorting the output files (see below) will combine all lengths files in the output “\_figs” directory into a single csv. If this is done with multiple time-points or conditions, you will not be able to sort which measurements came from which condition after they’ve been combined. For more detailed instructions and suggestions, see “suggestedProjectProtocol.pdf”. Instructions are for processing nd2 files. When processing tif files, substitute “nd2” for “tif” in the below instructions and use the “runt_nanotubeThreshold_allFilesInDirectory.sh” and “tif_nanotube_threshold.py” scripts instead.

**Input files in project directory:** nanotube_threshold.py, run_nanotubeThreshold_allFilesInDirectory.sh, $fn.nd2 where "$fn" is your filename(s)

**Output files in project/\_figs directory:** $fn_lengths.csv, $fn_runvalues.csv, $fn_noBranches_dilate.png for all files in project directory

**Commands:**
```
    bash run_nanotubeThreshold_allFilesInDirectory.sh 
```
### Sorting output files and combining all length measurements for an experimental condition
Once the image(s) have been processed, there will be 3 output files per image in the “\_figs” directory, a $fn_lengths.csv file, a $fn_runvalues.csv file, and a binary $fn_noBranches_dilate.png image. If multiple images from a single time-point and condition have been run, it is beneficial to combine all the lengths measurements into a single csv file for the time/condition, and to sort the 3 types of output files into subfolders. This is done with the “sortData.sh” and “concatData.py” files in the “\_figs” directory. The user only needs to run the “sortData.sh” file, as the “concatData.py” script is called within the bash script. Once “sortData.sh” has been run, I recommend putting all results into a new folder labeled with the time-point or condition. For further information, please see “suggestedProjectProtocol.pdf”. This process is the same when processing either nd2 or tif files.

**Input files in project/\_figs directory:** sortData.sh, concatData.py, $fn_lengths.csv, $fn_runvalues.csv, $fn_noBranches_dilate.png where "$fn" is your filename(s)

**Output files in project/\_figs directory:** $fn_allLengths.csv

**Output files in project/\_figs/lengths directory:** $fn_lengths.csv

**Output files in project/\_figs/finalMeasuredImage_dilated directory:** $fn_noBranches_dilate.png

**Output files in project/\_figs/runvalues directory:** $fn_runvalues.csv

**Commands:**
```
    bash sortData.sh 
```

### References
[1] Schindelin, J., Arganda-Carreras, I., Frise, E., Kaynig, V., Longair, M., Pietzsch, T., … Cardona, A. (2012). Fiji: an open-source platform for biological-image analysis. Nature Methods, 9(7), 676–682. doi:10.1038/nmeth.2019

[2] Stéfan van der Walt, Johannes L. Schönberger, Juan Nunez-Iglesias, François Boulogne, Joshua D. Warner, Neil Yager, Emmanuelle Gouillart, Tony Yu and the scikit-image contributors. scikit-image: Image processing in Python. PeerJ 2:e453 (2014) https://doi.org/10.7717/peerj.453

[3] Reback, Jeff, jbrockmendel, Wes McKinney, Joris Van den Bossche, Tom Augspurger, Phillip Cloud, Simon Hawkins, et al. 2021. Pandas-Dev/pandas: Pandas 1.2.4. Zenodo. https://doi.org/10.5281/ZENODO.3509134.

[4] McKinney, Wes. 2010. “Data Structures for Statistical Computing in Python.” Proceedings of the 9th Python in Science Conference. https://doi.org/10.25080/majora-92bf1922-00a.
