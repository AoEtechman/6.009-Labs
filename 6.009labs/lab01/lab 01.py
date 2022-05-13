#!/usr/bin/env python3

from json import load
import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


    
def get_pixel(image, x, y, edge_effects = None):
    """
    this function gets and returns a pixel with an x(horizontal) and y(vertical) value
    from the image dictionary pixel list. This function should also take into account
    the different edge_effects zero, extend, and wrap when returning the pixel

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    
    #initialize the image dictionary values
    pixels = image["pixels"]
    width = image["width"]
    height = image["height"]
    
    # if x and y values are within image bounds
    if 0 <= y and y < height and 0 <= x and x < width:
        return pixels[width*y +x]
    
    # if x or y is out of bounds, apply one of the different edge effects
    # and return the corresponding pixel value
    else:
        if x >= width or x < 0:
            if edge_effects == "zero":
                return 0
            elif edge_effects == "wrap":
                if x >= width:
                    while x>= width:
                        x = x -width
                elif x < 0:
                    while x < 0:
                        x = x + width 
            elif edge_effects == "extend":
                if x >= width:
                    x = width -1
                elif x < 0:
                    x = 0
        if y >= height or y < 0:
            if edge_effects == "zero":
                return 0
            elif edge_effects == "wrap":
                if y >= height:
                    while y >= height:
                        y = y - height
                elif y < 0:
                    while y < 0:
                        y = y + height 
            elif edge_effects == "extend":
                if y >= height:
                    y = height-1
                elif y < 0:
                    y = 0
        return pixels[width*y + x]
    

def set_pixel(image, x, y, c):
    """
    this function takes a pixel of value x, y and sets said pixel to 
    whatever value c is

    function does not return any value
    """
    pixels = image["pixels"]
    width = image["width"]
    pixel = get_pixel(image, x, y)
    pixels[width*y+x] = c


def apply_per_pixel(image, func):
    """
    this function takes an imput of an image dictonary and a function that is to be applied to the function.
    The function is applied to every pixel in the image, and then a image dictionary is returned with 
    the new pixels

    This process should not mutate the input image but rather, it should create a
    separate structure to represent the output.
    """
    
    # create copy of image dict
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image["pixels"][:],
    }
    
    # iterate through each pixel, get pixel value, update pixel value
    # return image dict
    for y in range(image['height']):
        for x in range(image['width']):
            pixel = get_pixel(result, x, y)
            newpixel = func(pixel)
            set_pixel(result, x, y, newpixel)
    return result


def inverted(image):
    """
    apply the inverted funtion to every pixel in the image. The inverted
    function takes the each pixel and subtracts 255 by the pixel. A new image dictionary is returned.

    This process should not mutate the input image but rather, it should create a
    separate structure to represent the output.
    """
    return apply_per_pixel(image, lambda c: 255 - c )


# HELPER FUNCTIONS
def create_2d_array(kernel_list, width):
    """
    Takes an input of kernel list, and the width of the kernel list.
    returns a 2D array of the kernel list.
    """
    array = []
    for i in range(0, len(kernel_list), width):
        array.append(kernel_list[i: i+width])
    return array

def box_blur_kernel(n):
    """
    This function takes in an input n and returns a box blur kernel.
    A box blur kernel is a kernel where each individual value is the same
    and they all add up to one.
    """
    value = 1/n**2   # value of each element in kernel
    lst = [value]*(n**2)  # create kernel list
    array = create_2d_array(lst, n)  #turn into a 2d array
    return array

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    Kernels are represented by a list of the kernel values.
    Both height and width of the kernel must be odd and must be the same value
    """
    
    im = {"height": image["height"], "width": image["width"], "pixels": image["pixels"][:]} # create copy of image dict
    #initialize kernel height and width
    kernel_height = len(kernel) 
    kernel_width = kernel_height
    
    # find search radius for neighbors
    search_distance = int((kernel_height - 1)/2)
    
    pixels = im["pixels"]
    for y in range(image["height"]): # iterate through each pixel
        for x in range(image["width"]):
            
            # iterate through each neighbor, get pixel and append to neighbor list
            neighbor_array = []
            for j in range(y - search_distance, y + search_distance+1): 
                for i in range(x - search_distance, x + search_distance+1):
                    neighbor_array.append(get_pixel(image,i,j,boundary_behavior))
            new_pixel_value = 0
            
            # iterate through each neighbor and get new pixel value with the kernel applied
            for yval in range(kernel_height):
                for xval in range(kernel_width):
                    new_pixel_value += kernel[yval][xval]*neighbor_array[yval*kernel_width+xval]
            set_pixel(im, x, y, new_pixel_value)#set pixel to new pixel value
    return {"height": image["height"], "width": image["width"], "pixels": im["pixels"]} # return image dict with new pixel values


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    pixels = image["pixels"]
    rounded_pixel_list = [round(pixel) for pixel in pixels]
    #iterate through each pixel and make sure they are all within the boundaries of 0 and 255
    for i in range(len(rounded_pixel_list)):  
        if rounded_pixel_list[i] > 255:
            rounded_pixel_list[i] = 255
        elif rounded_pixel_list[i] < 0:
            rounded_pixel_list[i] = 0
    return {"height": image["height"], "width": image["width"], "pixels": rounded_pixel_list} # return image dict

    

    


# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    kernel = box_blur_kernel(n) # get blur kernel
    img = round_and_clip_image(correlate(image, kernel, "extend")) # apply blur filter to image and make sure within boundaries
    return img

def sharpened(image,n):
    """
    Return a new image representing the result of applying an image sharpening filter.
    This is done by creating a new sharpened filter that is the result of multiplying the original 
    pixel by 2 and then subtracting the new value by the corresponding blur image filter

    This should not mutate the input image but rather create a seperate structure to 
    represent the image.
    """
    
    B = blurred(image,n)["pixels"]
    pixels = image["pixels"][:]
    
 
    sharpened = [2*pixels[i] - B[i] for i in range(len(pixels))] # create list of sharpened pixel values

    return round_and_clip_image({"height": image["height"], "width": image["width"], "pixels": sharpened}) # return image dict with blurred pixels

def edges(image):
    """
    Return a new image representing the result of applying an edge detection filter.
    This is done by utilizing two kernels that are applies to the original image. The output
    pixels are a result of squaring the two pixels that are a result of correlating the image with
    both kernels, adding them together, taking the square root, and then rounding this value to produce the 
    desired pixel.

    This should not mutate the input image but rather create a seperate structure to 
    represent the image.
    """
    
    # create x and y kernels and apply these kernels to the image
    kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    Ox = correlate(image, kx, "extend")["pixels"]
    Oy = correlate(image, ky, "extend")["pixels"]
        
    #perform edges function to pixel values
    output = [round(math.sqrt(Oy[i]**2+Ox[i]**2)) for i in range(len(Oy))]
    im = {"height": image["height"], "width": image["width"], "pixels": output }
    return round_and_clip_image(im) # make sure returned pixel values are within boundaries

def emboss(image):
    k = [[0,1,0],[0,0,0],[0,-1,0]]
    emboss_image = correlate(image,k, "extend")
    return round_and_clip_image(emboss_image)
            


    

# COLOR FILTERS
def split_color_image(image):
    """
    This function takes a color image input, and splits it 
    into a red pixel image, a green pixel image, and a blue pixel image.

    returns a list with the threee image dictionaries
    """
    # get list of red, green, and blue pixels
    red_pixels = [pixel[0] for pixel in image["pixels"]]
    green_pixels = [pixel[1] for pixel in image["pixels"]]
    blue_pixels = [pixel[2] for pixel in image["pixels"]]
    
    #create red, green, and blue image dictionaries
    green_image = {"width": image["width"], "height": image["height"], "pixels": green_pixels}
    red_image = {"width": image["width"], "height": image["height"], "pixels": red_pixels}
    blue_image = {"width": image["width"], "height": image["height"], "pixels": blue_pixels}
    return [red_image, green_image, blue_image]

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    # create color filter function 
    def color_filter(image):
        """
        this function takes in a color image input and splits it up into red, green, and blue images.
        It then applies the filter individualy to each color image pixel list, and then adds them back together in a tuple.
        A image dictionary is then returned with the new colored pixel list.
        """
        color_image_list = split_color_image(image)
        grey_green = filt(color_image_list[1])
        grey_red = filt(color_image_list[0])
        grey_blue = filt(color_image_list[2])
        filtered_colored_pixels = []
        for i in range(len(grey_green["pixels"])):
            filtered_colored_pixels.append((grey_red["pixels"][i], grey_green["pixels"][i], grey_blue["pixels"][i]))
        return {"height": image["height"], "width": image["width"], "pixels": filtered_colored_pixels}
    return color_filter




    


def make_blur_filter(n):
    """
    This function takes in an input n and makes a blur filter.
    Returns a blur filter function.
    
    """
    def blured_func(image):
        """
        takes in a image input and returns a blurred image 
        """
        return blurred(image, n)
    return blured_func
    


def make_sharpen_filter(n):
    """
    This function takes input n and returns a sharpened function. 
    """
    def sharpened_func(image):
        """
        This function takes in input image and returns a sharpened image.
        """
        return sharpened(image,n)
    return sharpened_func

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def combined_filters(image):
        """
        This function takes in an input image. It then performs a cascade of funtions on the 
        image input and returns a new filtered image
        """
        first_filter_image = filters[0](image) # get image after first filter
        for i in range(1, len(filters)): #iterate through filters
            if i == 1:
                new_filter_image = filters[i](first_filter_image) # if second filter, apply second filter on the image from the first filter
            else:
                new_filter_image = filters[i](new_filter_image) #if 3rd filter and on, apply current filter on previous filters result image
        return new_filter_image # return image with all filters applied
    return combined_filters
            


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass
   

