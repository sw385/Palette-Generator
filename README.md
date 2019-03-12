# Palette Generator

Given an image, this script can be used to generate a palette using the colors from that image. It is run on a directory of images, creating one palette for each individual image.

![Example](https://raw.githubusercontent.com/sw385/Palette-Generator/master/example.png)
(https://www.pexels.com/photo/mountains-and-river-during-daytime-151523/)

This program utilizes the k-means clustering algorithm provided in scipy to group the colors of the pixels in the input image by similarity. The program increases the number of centroids from 1 to 6, generating palettes of colors numbering from 1 to 6 colors. It then outputs these colors to an output image, saved in the corresponding directory.

## Prerequisites

In addition to the Python Standard Library, this program requires numpy, scipy, and the Python Image Library (PIL) packages to work.

## Usage:

Run the .py once to create the input and output directories 'input_directories' and 'output_directories'.

Place a folder containing images (ending in '.jpg', 'jpeg', or '.png') into 'input_directories'.

Run palette_generator.py. The palettes will be saved into a folder in 'output_directories'.

If the program is run again, it will ignore any input directories that already exist in 'output_directories'.

## To do:

Be able to generate one overarching palette for multiple input images.
