# DNA-Nanotube-Lengths
**In progress** The goal of this project is to automate length measurements of fluorescently labeled filaments, in this case DNA nanotubes, from epifluorescence micrographs. The main script in this repository, "nanotube_threshold.py", allows the user to consistently extract length measurements from fluorescent micrographs for varying image quality. A common issue with fluorescence micrographs is interference of background [finish sentence]. This is achieved by first separating background features (such as uneven illumination, small fluorescent smears, etc) from the image, followed by thresholding to isolate the DNA nanotubes [finish]. [description of project scope and goals].

Dependencies are listed in the ".dependencies" file. This project uses ND2Reader from nd2reader, found <a href="https://github.com/rbnvrw/nd2reader">here.</a>.

### Processing individual images

**Input files in project directory:** $fn_nd2, fn.tif where "$fn" is your filename(s)

**Output files in project/_figs directory:** $fn_lengths.csv, $fn_runvalues.csv, $fn_noBranches_dilate.png

**Commands:**

    python nanotube_threshold.py $fn.nd2 

### Processing all images in a directory

**Input files in project directory:** nanotube_threshold.py, $fn_nd2, fn.tif where "$fn" is your filename(s)

**Output files in project/_figs directory:** $fn_lengths.csv, $fn_runvalues.csv, $fn_noBranches_dilate.png for all files in project directory

**Commands:**

    bash run_nanotubeThreshold_allFilesInDirectory.sh 

### Sorting output files and combining all length measurements for an experimental condition

**Input files in project/_figs directory:** concatData.py, $fn_lengths.csv, $fn_runvalues.csv, $fn_noBranches_dilate.png, $fn_allLengths.csv where "$fn" is your filename(s)

**Output files in project/_figs/lengths directory:** $fn_lengths.csv, $fn_allLengths.csv

**Output files in project/_figs/finalMeasuredImage_dilated directory:** $fn_noBranches_dilate.png

**Output files in project/_figs/runvalues directory:** $fn_runvalues.csv

**Commands:**

    bash sortData.sh 
