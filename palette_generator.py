from PIL import Image, ImageDraw, ImageFont
import os
from numpy import array
import numpy
from scipy.cluster.vq import vq, kmeans, whiten
import colorsys
import pickle
from shutil import copyfile
import math

INPUT_DIR = 'input_image_pool'
OUTPUT_DIR = 'output_palettes'
OUTPUT_IMAGES = 'copied_images'
# INDEX_TXT = 'index.txt'
os.makedirs(OUTPUT_DIR, exist_ok=True)
# STARTING_IMAGE = ''
# OUTPUT_PALETTE = 'output_palette.png'

# add the paths of all the folders you want to add to the image pool here
# 'C:\\Users\\Samson\\Desktop\\python projects\\palette generator reverse\\input_image_pool'
INPUT_DIRECTORIES = ["F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_EarthPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_wallpapers",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_WeatherPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_SkyPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_RoomPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_CityPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_OrganizationPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_ArchitecturePorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_DessertPorn",
    "F:\\Downloaders batch\\rip.rarchives.com client-side downloader\\rips\\reddit_sub_RoadPorn",
    "F:\\Downloaders batch\\ripme 1.4.18\\rips"]
# INPUT_DIRECTORIES = INPUT_DIRECTORIES [:1]

CENTROIDS = 5
assert CENTROIDS < 11
CANDIDATES = 20
assert CANDIDATES < 100

def list_image_paths():
    '''Return a list of all full image paths in the directories in INPUT DIRECTORIES.'''
    image_pool = []
    for directory in INPUT_DIRECTORIES:
        for dirname, dirnames, filenames in os.walk(directory):
            # print path to all subdirectories first.
            for subdirname in dirnames:
                # print(os.path.join(dirname, subdirname))
                pass
            # print path to all filenames.
            for filename in filenames:
                # print(filename[-3:])
                if filename[-3:] in ('png', 'jpg'):
                    image_pool.append(os.path.join(dirname, filename))
                    # print(os.path.join(dirname, filename))
    return image_pool


def filenames(directory):
    '''Given a directory, return a list of files in that directory.
        Assumes no folders and only images.'''
    filenames_list = [f for f in os.listdir(directory)]
    filenames_list.sort()
    return filenames_list
    
def produce_array(full_image_path):
    '''Given the full image path (dir + filename),
        resize it and return it as an array.'''
    im = Image.open(full_image_path)
    RESIZE_WIDTH = 128
    im = im.resize((RESIZE_WIDTH, RESIZE_WIDTH))

    temp = []
    for y in range(0 , im.size[1]):
        for x in range(0 , im.size[0]):
            color = im.getpixel((x, y))
            temp.append([color[0], color[1], color[2]])
    temp = array(temp)
    return temp
    
def generate_palette(array, centroids):
    '''Given an array and a number of centroids, returns a list of colors.'''
    palette = []
    result = kmeans(array.astype(float), centroids)
    for centroid in numpy.array(result[0]).tolist():
        centroid = (int(centroid[0]), int(centroid[1]), int(centroid[2]))
        palette.append(tuple(centroid))
    return palette
    
def generate_palettes(array, max_centroids):
    '''Given an array and number of centroids,
        returns all palettes from 1 to max centroids as a list.'''
    palettes = []
    for x in range(1, max_centroids + 1):
        palette = generate_palette(array, x)
        palettes.append(palette)
    return palettes
    
def draw_palettes(full_image_path, palettes, min_dimensions, output_directory):
    '''Given a list of palettes and the (dimensions) of the smallest division,
        draw the palette to an PNG with the corresponding filename.'''
    output_filename = '_palette - ' + os.path.splitext(os.path.basename(full_image_path))[0] + '.png'

    canvas = Image.new('RGB', (min_dimensions[0] * CENTROIDS, min_dimensions[1] * CENTROIDS), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for p, palette in enumerate(palettes):
        for c, color in enumerate(palette):
            # print(len(palette), CENTROIDS, CENTROIDS / len(palette))
            # draw.rectangle((c * 50, p * 100, (c + 1) * 50 - 1, (p + 1) * 100 - 1), color)
            swatch_width = min_dimensions[0] * CENTROIDS / len(palette)
            draw.rectangle((c * swatch_width, p * 100, (c + 1) * swatch_width - 1, (p + 1) * 100 - 1), color)
            color_string = '%02x%02x%02x'.upper() % color      # '#%02x%02x%02x' if you want the # in front
            font = ImageFont.truetype("arial.ttf", 12)
            draw.text((c * swatch_width + 2, p * 100 + 3), color_string, (255, 255, 255), font=font)
            draw.text((c * swatch_width + 2, p * 100 + 15), color_string, (0, 0, 0), font=font)
    canvas.save(os.path.join(output_directory, output_filename), 'PNG')
    print('Finished drawing: ' + output_filename)

def image_to_palette(full_image_path, output_directory):
    '''Given a full image path,
        generate a palette image and save it in the output_directory.'''
    temp = produce_array(full_image_path)
    palettes = generate_palettes(temp, CENTROIDS)
    draw_palettes(full_image_path, palettes, (50, 100), output_directory)

###########
    
def pregenerate_palettes():
    '''Given a directory of images,
        return a dictionary of pregenerated palettes, organized by number of centroids.
        buckets = {1: [((HSV), filename), ], 2: [((HSV, HSV), filename), ]}
        '''
    if os.path.isfile('palettes_buckets.p') == True:
        loaded_buckets = pickle.load(open('palettes_buckets.p', 'rb'))
        buckets = {}
        for number in loaded_buckets:
            buckets[number] = []
            for palette in loaded_buckets[number]:
                if os.path.isfile(palette[1]):
                    buckets[number].append(palette)
    else:
        buckets = {}
        for x in range(1, CENTROIDS + 1):
            buckets[x] = []

    for bucket in buckets:
        for pair in buckets[bucket]:
            if len(pair) == 1:
                print(pair)

    new_count = 0
    for image_path in list_image_paths():
        try:
            already_generated = False
            for bucket in buckets:
                for palette_pair in buckets[bucket]:
                    if palette_pair[1] == image_path:
                        already_generated = True
            if already_generated == False:
                temp = produce_array(image_path)
                palettes = generate_palettes(temp, CENTROIDS)
                for palette in palettes:
                    buckets[len(palette)].append((palette, image_path))
                print('Pregenerated palette for: ' + image_path)
                # print((palette, image_path))
                new_count += 1
            else:
                # print('Already generated for: ' + image_path)
                pass
            if new_count >= 100:
                pickle.dump(buckets, open('palettes_buckets.p', 'wb'))
                new_count = 0
        except:
            pass

    # return buckets
    pickle.dump(buckets, open('palettes_buckets.p', 'wb'))
    print('Images in bucket: ' + str(len(buckets[1])))

#####

def rgb_to_hsv(color):
    '''Given an RGB color (255, 255, 255),
        return an HSV color (360, 100, 100).'''
    color = list(color)
    color = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]
    color = list(colorsys.rgb_to_hsv(color[0], color[1], color[2]))
    color = [color[0] * 360.0, color[1] * 100.0, color[2] * 100.0]
    return color

def polar_difference(coord1, coord2):
    '''Each coord is (angle, radius, height) = HSV.
        Returns the length connecting the two coords.'''
    level_distance = (coord1[1] ** 2 + coord2[1] ** 2 - (2 * coord1[1] * coord2[1] * math.cos(math.radians(coord1[0]) - math.radians(coord2[0])))) * 0.5
    height = abs(coord2[2] - coord1[2])
    return (level_distance ** 2 + height ** 2) ** 0.5

def close_enough(color1, color2, threshhold):
    '''If color1 (HSV) is within threshhold distance to color2,
        return True.'''
    color1, color2 = rgb_to_hsv(color1), rgb_to_hsv(color2)
    if polar_difference(color1, color2) < threshhold:
        return True
        
def compare_palettes(palette1, palette2, threshold):
    all_match = []
    for n, color1 in enumerate(palette1):
        match = False
        for color2 in palette2:
            if close_enough(color1, color2, threshold):
                match = True
        all_match.append(match)
    assert len(all_match) == len(palette1)
    if False in all_match:
        return False
    else:
        return True

'''
# this is for producing images of the palettes
input_images = list_image_paths()
for input_image in input_images:
    image_to_palette(input_image)
'''

'''
# this is for pregenerating the palettes and storing them in a pickle
buckets = pregenerate_palettes()
# idea: be able to load and add to a pickle that already exists, check for moved files or that generated palettes still have their originating images existing
    # add and save the pickle as the palettes are being generated since there are many images to go through
    # handling errors? ignoring and skipping errors?
'''

# this is for loading the last pickle generated containing the palettes
input_buckets = pickle.load(open('palettes_buckets - Copy (3).p', 'rb'))
# print(len(input_buckets[1]))
#for element in input_buckets:
#    print(input_buckets[element][-3])

STARTING_IMAGE = "C:\\Users\\Samson\\Desktop\\david-noren-david-noren.jpg"
CENTROIDS_NUMBER = 3    # this is the number of centroids we want to match; 2 seems to work best
OUTPUT_NUMBER = 40  # this is the number of images we want to end up with, in order
assert CENTROIDS_NUMBER in input_buckets
bucket = input_buckets[CENTROIDS_NUMBER]  # = [(palette, filename), (palette, filename)]
assert len(bucket) > OUTPUT_NUMBER
for n, palette in enumerate(bucket):
    if palette[1] == STARTING_IMAGE:
        bucket.remove(n)

# this creates an image containing the palette and saves it so you can view it
image_to_palette(STARTING_IMAGE, OUTPUT_DIR)
# this is repeated, so a way to only do it once? separate generating the image from saving the image in multiple places, so you don't have to generate it every time you want to make a copy of it somewhere

temp = produce_array(STARTING_IMAGE)
starting_palette = generate_palette(temp, CENTROIDS_NUMBER)
print(starting_palette)
        
distances = []
print('Calculating distances...')
for image in bucket: # image = ([palette], filename)
    largest = []
    for candidate_centroid in image[0]:
        smallest = []
        for starting_centroid in starting_palette:
            smallest.append(polar_difference(rgb_to_hsv(candidate_centroid), rgb_to_hsv(starting_centroid)))
        largest.append(min(smallest))
    distances.append((max(largest), image[1]))

output_filenames = []   # needs to be in order starting from closest match
threshold = 0
while len(output_filenames) < OUTPUT_NUMBER and threshold < 128:
    for candidate in distances:
        if candidate[1] not in output_filenames:
            if candidate[0] < threshold:
                output_filenames.append(candidate[1])
                print(str(len(output_filenames)) + ' image' + 's' * (len(output_filenames) != 1) + ' found so far.')
    threshold += 1
print('Threshold ends up being: ' + str(threshold))

'''
# THIS IS THE OLD VERSION that calculates the distances every single freaking time
#for threshold in range(0, 128):
    for candidate in bucket:
        if candidate[1] not in output_filenames:
            if compare_palettes(starting_palette, candidate[0], threshold) == True:
                output_filenames.append(candidate[1])
                print(str(len(output_filenames)) + ' image' + 's' * (len(output_filenames) != 1) + ' found so far.')
    threshold += 1
print('Threshold ends up being: ' + str(threshold))
'''

# removes images from the previous run so you don't have to do it manually
for old_file in os.listdir(OUTPUT_IMAGES):
    file_path = os.path.join(OUTPUT_IMAGES, old_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)
# copies the images over to the OUTPUT_IMAGES directory
for n, filename in enumerate(output_filenames):
    count = (2 - len(str(n))) * '0' + str(n) + ' - '
    copyfile(filename, os.path.join(OUTPUT_IMAGES, count + os.path.basename(filename)))

# save the starting image and its palette into the output directory
copyfile(STARTING_IMAGE, os.path.join(OUTPUT_IMAGES, '_' + os.path.basename(STARTING_IMAGE)))
# this creates an image containing the palette and saves it so you can view it
image_to_palette(STARTING_IMAGE, OUTPUT_IMAGES)
# a place to indicate the number of centroids? centroids=3 or something

# a way to force every starting centroid to be represented in the candidate image?

# be able to choose two or three starting images
    # so you can hide pornographic images or WTF/gore images in plane sight using their color palette! wouldn't that be funny
    # or simply including pornographic images in the image pools
# being able to quickly select your image pools
    # tagging each folder with their subjects so you can filter them out as you wish
# once you have your images, combine them to form a new palette slightly different from the palette for only the first starting image

# a way to store the distances instead of calculating it every time
    # on the first pass: for each starting centroid, compare with the centroids of the candidate image
    # find the smallest distance to a centroid and save it
    # then out of the three centroids, find the one with the largest distance to its partner, and save it while discarding all the other ones
    # then use this number for comparing to the threshold
    # and if you have lots of images in your image pool, you can now increment the threshold by 0.5 without slowing down the program too much

# make sure the extension of canvas.save 'PNG' IS actually .png instead of whatever the original image had