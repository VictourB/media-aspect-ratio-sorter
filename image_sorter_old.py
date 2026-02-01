#! python3
# by Victour Bue
# This program will ask for a directory and for every image in that directory 
# it will copy the image into a seperate directory sorted by aspect ratio.

import pathlib, os
from PIL import Image

def prompt():
    print("""
    This program will ask for a directory and for every image in that directory 
    it will copy the image into a seperate directory sorted by aspect ratio.
    """)
    response = input("Would you like to do that? ")
    response = response.lower()
    if response == "yes" or response == "no":
        return response
    else:
        print("Please enter yes or no.")
        return prompt()


def gcd(a,b):
    # Greatest Common Denominator
    if b == 0:
        return a
    return gcd(b, a % b)


def aspect_ratio(val, lim):
    lower = [0,1]
    upper = [1,0]

    while True:
        mediant = [lower[0] + upper[0], lower[1] + upper[1]]

        if (val * mediant[1] > mediant[0]):
            if (lim < mediant[1]):
                return upper
            lower = mediant
        elif (val * mediant[1] == mediant[0]):
            if (lim >= mediant[1]):
                return mediant
            if (lower[1] < upper[1]):
                return lower
            return upper
        else:
            if (lim < mediant[1]):
                return lower
            upper = mediant


def get_directory():
    # Get Directory from User
    print("Which directory would you like to sort by aspect ratio?")
    response = input()

    #Search Computer's Hard Drive for matching directory
    if os.path.isdir(response):
        return response
    else:
        print("That is not a valid directory.")
        return get_directory()


def get_limiter():
    print("Please select a limiter. This will set how aggressively the algorithm will match aproximate ratios. lower = more aggressive. 0 to disable.")
    response = input()
    return int(response)


def load_and_sort_images(directory, limiter):
    # Load all images from directory
    images = pathlib.Path(directory)
    for path in images.iterdir():
        if not path.is_file():
            continue
        
        # Handle image decoding errors
        try:
            image = Image.open(path)
        except:
            print(f"Couldn't read file: {path} Is it an image file?")
            continue

        # Finds greatest common denominator and applies it to x and y 
        ratio = gcd(image.width,image.height)
        x = int(image.width /ratio)
        y = int(image.height/ratio)

        # Decide between a limited ratio or a raw ratio
        if limiter == 0:
            savepath = directory + f"\sorted_images\{x}x{y}"
        else:
            x, y = aspect_ratio(x/y, int(limiter))
            savepath = directory + f"\sorted_images\{x}x{y}"

        #Print and Save
        print(f"\nFrom: {path} \nTo: {savepath}")
        if not (os.path.isdir(savepath)):
            os.makedirs(savepath)
        image.save(f"{savepath}\{os.path.basename(image.filename)}")   


def main():
    if prompt() == "no":
        return

    path = get_directory()
    limiter = get_limiter()
    load_and_sort_images(path, limiter)
    
    return main()


main()