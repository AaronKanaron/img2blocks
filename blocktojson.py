import math
import os
from PIL import Image
import numpy as np
dir_path = os.path.dirname(os.path.realpath(__file__))


# defines the directory path to the image that will be used.
image_to_use = dir_path + "\\skolfoto.png"
# image_to_use = ""

# Creates a tuple for width and height
# If the tuple is empty, the user is prompted to input the width and height of an image.
# The inputs are then turned into integers and added to the tuple.
result_size = (150, 80)
if result_size == None or result_size == ():
    width = input("How wide should your image be (X)")
    height = input("How tall should your image be (Y)")
    result_size = (int(width), int(height))

# Debugs to the console; for development purposes.
debug = False

# Don't change these unless you know what you're doing.
mcfunction = "D:\Programmering\Python\Learning\minecraft\\result.mcfunction"
blockpath = "D:\Programmering\Python\Learning\minecraft\\blocks"
result = []
block_names = []
block_colors = []

# temporary functions used at beginning

# Removes a specified file path.


def remove(rempath):
    print(rempath)
    os.remove(rempath)


# Takes in an image file path as input, and returns a boolean value indicating whether or not the image is transparent
def find_transparancy(path):
    img = Image.open(path)
    # If the image has a transparency info attribute,
    # then the image is considered transparent and return True.
    if img.info.get("transparency", None) is not None:
        img.close()
        remove(path)
        return True
    # If the image is in "P" mode (8-bit paletted), the function checks if any of the colors in the
    # image's color palette is transparent. If so, it returns True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                img.close()
                remove(path)
                return True
    # If the image is in "RGBA" mode (32-bit RGBA), the function checks if the minimum alpha value
    # is less than 255. If so, it returns True.
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            img.close()
            remove(path)
            return True
    return False

# Opens an image file and gets its width and height.
# If the width and height are not both 16, remove it.


def size_cleanup(path):
    img = Image.open(path)
    width, height = img.size
    if width != 16 or height != 16:
        img.close()
        remove(path)

# Converts an image to the RGB color space.


def toRGB(path):
    Image.open(path).convert("RGB").save(path)

# Finds the average color of an image, given the path to the image.
# loops through each pixel in the image and retrieves the red, green and blue values for each pixel.
# It then finds the average of all these values and writes them into a list.


def averageColor(path):
    img = Image.open(path)
    width, height = img.size
    colors = [0, 0, 0]

    for x in range(width):

        for y in range(height):

            colors[0] += img.getpixel((x, y))[0]
            colors[1] += img.getpixel((x, y))[1]
            colors[2] += img.getpixel((x, y))[2]

    colors[0] = math.floor(colors[0] / (width * height))
    colors[1] = math.floor(colors[1] / (width * height))
    colors[2] = math.floor(colors[2] / (width * height))

    block_colors.append([colors[0], colors[1], colors[2]])
    print(f"Res: ({colors[0]}, {colors[1]}, {colors[2]})") if debug else None


# Calculates the color closest to the given color.
# This is done by calculating the Euclidean distance between the given color and all colors in the array colors.
# The color with the smallest distance is then returned.
def closest(colors, color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2, axis=1))
    index_of_smallest = np.where(distances == np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    return [smallest_distance, block_names[index_of_smallest[0][0]]]


# Opens an image from a given path,
# resizes the image to fit the result_size,
# and then appends the result with the closest color from the block_colors.
def imageToUse(path):
    if path == None or path == "":
        path = input("Drag and drop your image to convert to blocks\n")
    img = Image.open(path)
    resized = img.resize(result_size)
    for xP in range(result_size[0]):
        for yP in range(result_size[1]):
            result.append(closest(block_colors, (resized.getpixel((xP, yP)))))
            print(
                f"Image pixel ({xP+1}, {yP+1}): {resized.getpixel((xP, yP))}") if debug else None


# Iterates through the files in a directory and appends the filenames to a list.
# If the file is a png, it calculates the average color of the image.
def open_images(path):
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename.endswith(".png"):
            fullpath = path + "\\" + filename
            block_names.append(filename[:-4])
            averageColor(fullpath)

            # *Used for cleaning up blocks directory files for blocks that can't be used.
            # find_transparancy(fullpath)
            # size_cleanup(fullpath)
            # torgb(fullpath)


# Convert the results of a two-dimensional array into minecraft commands.
# Loops through each row and column in the array,
# and then prints out the minecraft command for each block in the array
#!! Problem med hur indexet väljs, xd + yd fungerar inte !!#
def to_minecraft_commands():
    pixels = Image.new("RGB", (result_size[0], result_size[1]))

    xC = 0
    yC = 0

    block_index = 0
    with open(mcfunction, "a+") as mc:
        mc.truncate(0)
        for yD in range(result_size[1]):
            for xD in range(result_size[0]):
                eq = result[xD]

                print(
                    f"Row: {xD+1}, Coloum: {yD+1}, Block: {eq[1]}, Color: {eq[0]}") if debug else None
                # Preview
                pixels.putpixel((xD, yD), (result[block_index][0][0][0], result[block_index]
                                [0][0][1], result[block_index][0][0][2]))
                mc.write(
                    f"setblock ~{'' if xD == 0 else xD} ~{'' if yD == 0 else yD} ~ minecraft:{result[block_index][1]}\n")
                block_index += 1
        mc.close()
        pixels.show()
    os.system(mcfunction)
# This function takes the path of an image directory and calculates the average color of each image in the directory.
# It then creates a new image in a different size and determines
# the closest color from the given list of colors for each pixel in the image.
# Finally, it prints the coordinates and block type of each block in the result array.


def main():
    # takes a path and then adds the file names of all the images in the directory to a list.
    # It then calculates the average colour of each image and adds it to a list.
    open_images(blockpath)
    # responsible for creating a version of an image in a different size and then
    # determining the closest color from a given list of colors for each pixel in the image.
    imageToUse(image_to_use)
    # prints the coordinates and block type of each block in the result array
    to_minecraft_commands()


# main() contains the code that will be executed when the program is run.
if __name__ == '__main__':
    main()
