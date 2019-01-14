import os
from PIL import Image, ImageDraw, ImageFont
from numpy import array
from scipy.cluster.vq import kmeans
import numpy


INPUT_DIR = 'input_directories'
OUTPUT_DIR = 'output_directories'
MAX_COLORS = 6  # 6 colors in a palette is plenty, no need for more.

def dirs_to_process():
    '''Return a list of paths of directories in INPUT_DIR that do not exist in OUTPUT_DIR.
        Do NOT create the corresponding output directories yet.'''
    input_dirs = os.listdir(INPUT_DIR)
    output_dirs = os.listdir(OUTPUT_DIR)
    new_dirs = [f for f in input_dirs if f not in output_dirs]
    return new_dirs
    
def images_to_process(directory):
    '''Given a path to a directory, return a list of paths of images in that directory.'''
    contents = os.listdir(os.path.join(INPUT_DIR, directory))
    images = []
    for file in contents:
        if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
            images.append(file)
    return images
    
def image_to_array(full_image_path):
    '''Given the full image path (dir + filename),
        resize it and return it as an array.'''
    im = Image.open(full_image_path)
    RESIZE_WIDTH = 128  # 256 makes the program run really slow and doesn't really seem all that necessary anyway.
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
    output_filename = os.path.splitext(os.path.basename(full_image_path))[0] + ' palette .png'

    canvas = Image.new('RGB', (min_dimensions[0] * MAX_COLORS, min_dimensions[1] * MAX_COLORS), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for p, palette in enumerate(palettes):
        for c, color in enumerate(palette):
            # print(len(palette), CENTROIDS, CENTROIDS / len(palette))
            # draw.rectangle((c * 50, p * 100, (c + 1) * 50 - 1, (p + 1) * 100 - 1), color)
            swatch_width = min_dimensions[0] * MAX_COLORS / len(palette)
            draw.rectangle((c * swatch_width, p * 100, (c + 1) * swatch_width - 1, (p + 1) * 100 - 1), color)
            color_string = '%02x%02x%02x'.upper() % color      # '#%02x%02x%02x' if you want the # in front
            font = ImageFont.truetype("arial.ttf", 12)
            draw.text((c * swatch_width + 2, p * 100 + 3), color_string, (255, 255, 255), font=font)
            draw.text((c * swatch_width + 2, p * 100 + 15), color_string, (0, 0, 0), font=font)
    canvas.save(os.path.join(output_directory, output_filename), 'PNG')
    print('Finished drawing: ' + output_filename)

def image_to_palette(image_filename, directory):
    '''Given an image_filename and the name of the containing directory,
        generate and save the palette in the corresponding output directory.'''
    full_image_path = os.path.join(directory, image_filename)
    full_image_path = os.path.join(INPUT_DIR, full_image_path)
    image_array = image_to_array(full_image_path)
    
    palettes = generate_palettes(image_array, MAX_COLORS)
    
    output_directory = os.path.join(OUTPUT_DIR, directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    draw_palettes(full_image_path, palettes, (50, 100), output_directory)

def process_dir(directory):
    '''Given a path to a directory, process all the images in that directory.'''
    pass






if __name__ == "__main__":
    input_dirs = dirs_to_process()
    for dir in input_dirs:
        input_images = images_to_process(dir)
        for image in input_images:
            image_to_palette(image, dir)
