__author__ = "Melissa A. Klocke"
__email__ = "klocke@ucr.edu"
__version__ = "1.0"


'''This script contains the entire workflow for getting length measurements from raw 16-bit .tif images of nanotubes.
The process is inspired by the previous method used by Franco lab to measure lengths, including a script written by 
Dr. Vahid Mardanlou in Matlab which took in thresholded binary .tif image of nanotubes, removed branching or intersecting
features, and measured the length of the remaining features in the image. The script by Dr. Mardanlou was called "TubeRemove_Vahid3.m
The "subtractBackground" function can be bypassed if the images are high quality - no background, consistent lighting across field of view, 
bright nanotubes compared to background, etc. The script does run more slowly with this function in use, but allows for processing images
with some of the issues mention in the previous sentence.

Call the script with "python nanotube_threshold.py $nd2_filename" where $nd2_filename is your file. 
Call the script on multiple images in a folder with "bash run_nanotubeThreshold_allFilesInDirectory.sh". 
Must have both files in the same directory as the .nd2 files.'''


import sys
import os
import numpy as np
import pandas as pd
import imageio as io
import scipy.ndimage as ndi
from nd2reader import ND2Reader
import matplotlib.pyplot as plt

from skimage import (filters, morphology, measure, exposure)
from skimage.util import img_as_int, img_as_ubyte, img_as_uint


def main():
	if len(sys.argv)==1:
		print("Need to specify file to process as a parameter.")
		print("   Exiting")
		exit()

	fn = sys.argv[1] 
	median_size = 20	#Recommend 10. Can try 15, 20 for images with bad backgrounds. Increased values caused the code to run noticeably more slowly
	sigma_val = 3	#can be adjusted from 0.5-4 depending on the quality of the images. Larger values result in more smoothing
	removeSmallerThan = 3	# removed objects shorter than 3 pixels. Adopted from the previus code. Rationale: anything 3 pix or smaller may not be a tube
	thresh = 'yen' ## or 'yen' or 'otsu' or 'tri'
	pix_micron = 0.070556640625 ## for 60x img, must be updated to your 

	os.system("mkdir _figs")
	print("\nOpening file: ", fn)

	fname, img = tif_read(fn) 
	noBG = subtractBackground(img, median_size, sigma_val, fname)
	thresh_img = threshold(noBG, sigma_val, thresh, fname)
	thin_img = skeletonize(thresh_img, removeSmallerThan, fname)
	noBranches = removeBranches(thin_img, fname)
	lengths, len_df = getLengths(noBranches, pix_micron, fname)

	# io.imwrite('_figs/%s.png' % fname, exposure.equalize_adapthist(img), format = 'png') 
	saveRunValues(fn, fname, sigma_val, median_size, thresh, removeSmallerThan, pix_micron)

	
def tif_read(fn):
	'''Reads in the .tif file associated with the filename called with the script. 
	Returns the filename without the extension and the image as a numpy array.'''
	basdir, basename = os.path.split(fn)
	fname, fext = os.path.splitext(basename)
	img = img_as_uint(io.imread(fn))
	return fname, img


def subtractBackground(img, med_size, sigma, fn):
	'''Accepts the image as numpy array, the median smoothing selem size, the gaussian sigma smoothing parameter, and the filename.
	First the image is smoothed with a Gaussian filter and converted to integer image format. The G filter smoothes out the noise 
	in the image brightness values, so that those arbitrary small noise of image isn"t amplified when subtracting the background.
	Then the original image (without G smoothing) is smoothed using the median filter. The median filter smooths out very 
	small/bright objects without loosing larger features, thus creating a "background" image.'''
	gauss_filtered_img = filters.gaussian(img, sigma=sigma)
	img = img_as_int(gauss_filtered_img)
	bg_img = filters.median(img, morphology.disk(med_size))
	noBG_img = img - bg_img
	noBG_img = img_as_uint(noBG_img)

	## to save images for script diagnostic purposes
	# io.imwrite('_figs/%s.png' % fn, img_as_int(img), format = 'png') 
	# io.imwrite('_figs/%s_bg.png' % fn, bg_img, format = 'png')
	# io.imwrite('_figs/%s_noBG.png' % fn, noBG_img, format = 'png')
	return noBG_img


def threshold(img, sigma, thresh, fn):
	'''Applies a threshold to the image following background subtraction. The ideal threshold for the sample should be
	decided by visual confirmation with the raw image.'''

	gauss_filtered_img = filters.gaussian(img, sigma=sigma)
	if thresh == 'otsu':
		thresh_val = filters.threshold_otsu(gauss_filtered_img)
	elif thresh =='yen':
		thresh_val = filters.threshold_yen(gauss_filtered_img)
	elif thresh == 'tri':
		thresh_val = filters.threshold_triangle(edges)
	masked_img = gauss_filtered_img > thresh_val
	final_img = img_as_uint(masked_img)

	## to save image for script diagnostic purposes
	# io.imwrite('_figs/%s_thresh.png' % fn, final_img, format = 'png')
	return final_img

def skeletonize(img, minSize, fn):
	'''Thins the features in the thresholded image to 1-pixel width. Removes features less than 3-pixels long.
	features can be connected vertically, horizontally, or diagonally.'''
	thin_img = morphology.thin(img)
	bool_thin = thin_img > 0
	cleaned = morphology.remove_small_objects(bool_thin, min_size=minSize, connectivity=8)
	dilated_img = morphology.binary_dilation(cleaned)

	cleaned = img_as_ubyte(cleaned)
	dilated_img = img_as_ubyte(dilated_img)

	## to save images for script diagnostic purposes
	# io.imwrite('_figs/%s_thin.png' % fn, cleaned, format = 'png')
	# io.imwrite('_figs/%s_dilate.png' % fn, dilated_img, format = 'png')
	return cleaned


def branchpoints(skeleton, fn):
	'''Create a boolean array with the branch points of the image indicated. This was adapted from an answer on stackoverflow
	by R. Schleutker for the "How to find branch point from binary skeletonize image" question found here:
	https://stackoverflow.com/questions/43037692/how-to-find-branch-point-from-binary-skeletonize-image
	The idea is to mimic the mwmorph('branchpoints') command from Matlab to combine the image processing steps from ImageJ 
	with Vahid's Matlab script into one neat python script. The function applies the hit_or_mis function from scipy.ndimage using 
	selems which represent different kinds of branches.'''

	selems = list()
	selems.append(np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]]))
	selems.append(np.array([[1, 0, 1], [0, 1, 0], [1, 0, 0]]))
	selems.append(np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0]]))
	selems.append(np.array([[0, 1, 0], [1, 1, 0], [0, 0, 1]]))
	selems.append(np.array([[0, 0, 1], [1, 1, 1], [0, 1, 0]]))
	selems.append(np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]]))
	selems = [np.rot90(selems[i], k=j) for i in range(5) for j in range(4)]

	selems.append(np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
	selems.append(np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
	selems.append(np.array([[1, 0, 0], [0, 1, 1], [1, 1, 0]]))

	branches = np.zeros_like(skeleton, dtype=bool)

	for selem in selems:
		branches |= ndi.binary_hit_or_miss(skeleton, selem)

	## to save image for script diagnostic purposes
	# io.imwrite('_figs/%s_branches.png' % fn, img_as_ubyte(branches), format = 'png')
	return branches


def removeBranches(skeleton, fn):
	'''Use the branchpoints to label and remove intersecting features in the thinned image. A copy of the image without
	intersecting features is binary dilated and saved as a png for visual confirmation with original image. An image
	may also be saved without binary dilation for finer diagnostics of an intersection of features.'''
	branches = branchpoints(skeleton, fn)
	[y, x] = np.where(branches)
	markers = measure.label(skeleton, connectivity=2)
	
	labelsToRemove = np.empty(shape=(len(x),1))
	for i in range(len(x)):
		labelsToRemove[i] = markers[y[i], x[i]]

	labelsToRemove = labelsToRemove.astype(int)

	for i in range(len(labelsToRemove)):
		markers = np.where(markers != labelsToRemove[i], markers, 0) ## makes any pixel matching the current label 0

	mask = markers > 0 
	skeleton = skeleton * mask
	# skeleton = skeleton > 0
	dilated_img = morphology.binary_dilation(skeleton)

	## to save image for script diagnostic purposes
	# io.imwrite('_figs/%s_noBranches.png' % fn, img_as_ubyte(skeleton), format = 'png') ## for visual confirmation
	io.imwrite('_figs/%s_noBranches_dilate.png' % fn, img_as_ubyte(dilated_img), format = 'png') ## for visual confirmation
	return skeleton


def getLengths(img, pix_micron, fname):
	'''Measure the lengths of the remaining features. Saves the lengths to a csv with the filename grabbed from the 
	original image in nd2_read function.'''
	labeled = measure.label(img, connectivity=2)
	props = measure.regionprops(labeled)
	lengths = np.array([r.perimeter for r in props])
	lengths = (lengths * pix_micron)
	dict_vals = {'lengths (micron)': lengths}
	df = pd.DataFrame(dict_vals)
	df.to_csv('_figs/%s_lengths.csv' % fname)
	return lengths, df

def saveRunValues(fn, fname, sigma, med, thresh, minSize, pix_micron):
	'''Saves the user-input parameters to a csv file for reproducibility and diagnostic purposes.'''
	dict_vals = {'filename': [fn], 'smoothing sigma value': [sigma], 'median smoothing val': [med], 'threshold type': [thresh], 
	'objects smaller then n (pix) removed': minSize, 'pixels to microns': pix_micron}
	temp_df = pd.DataFrame(dict_vals)
	temp_df.to_csv('_figs/%s_runvalues.csv' % fname)






if __name__ == '__main__':
    main()