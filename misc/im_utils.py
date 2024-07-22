from cmath import sin
import numpy as np
import cv2
import os
import math
from os import listdir
from os.path import isfile, join
import time

def Circular_mask(h, w, center=None, radius=None):
    '''
    Creates a mask of dimentions, height = h, width = x, with a circle marked true, 
    located at the center and having radius  = radius
    center: (x,y) tuple
    '''
    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])
    
    #Compute square of the radius to avoid computing sqrt on every step
    radius_sq = radius**2

    Y, X = np.ogrid[:h, :w]
    dist_from_center_sq = (X - center[0])**2 + (Y-center[1])**2

    mask = dist_from_center_sq <= radius_sq

    return mask

def ScaleImage (image, width = 1512, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def EnhanceContrast(input_img, brightness = 0, contrast = 0):

    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
    return buf


def DrawCircles(circle_array, target):
    im_toreturn = target
    '''
    Draws green circles with red centers on the "target" image. Assumes an array of circles "circle_array"
     to have center_x at indx 0, center y ant index 1 and radius at index 2.
    If some circles do not have radius defined, draws them as red circls radius 500
    '''
    #Draw circles and their centers
    for i in circle_array:

        if len(i) ==2:
            # draw the center of the circle
            cv2.circle(im_toreturn ,(i[0],i[1]),4,(0,0,255),4)
            # Draw the outer circle in red
            cv2.circle(im_toreturn ,(i[0],i[1]),500,(0,0,255),8)


        if len(i) ==3:
            # draw the center of the circle
            cv2.circle(im_toreturn ,(i[0],i[1]),4,(0,0,255),4)
            # draw the outer circle
            cv2.circle(im_toreturn ,(i[0],i[1]),i[2],(0,255,0),4)
            #Print the radius at the center
            radius_txt = str(i[2])
            cv2.putText(im_toreturn, radius_txt, (i[0],i[1]), cv2.FONT_HERSHEY_PLAIN, 5, (128, 128, 0), 4)
                #Print number of circles

    num_cir = str(len(circle_array))
    cv2.putText(im_toreturn, num_cir, (100,200), cv2.FONT_HERSHEY_PLAIN, 8, (150, 150, 0), 12)
    return im_toreturn 
def resize_to_size(img, size):
    '''
    Resizes the image, so that the shorter side is eqaul to given size,
    keeps the aspect ratio.
    :param img: The image to be resized.
    :param size: The size to resize the image to.
    :return: The resized image.
    '''
    h, w = img.shape[:2]
    if h > w:
        width = size
        dim = (width, int(size* h / w)) 
    else:
        height = size
        dim = (int(size* w/h), height)
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return img

def crop_to_square(img):
    '''
    Crops the image to perfect square centered around the center of the original image
    keeps the aspect ratio.
    :param img: The image to be resized.
    :return: The resized image.
    '''
    h, w = img.shape[:2]
    if h > w:
        img = img[(h-w)//2:(h-w)//2 + w, :, :]
    else:
        img = img[:, (w-h)//2:(w-h)//2 + h, :]

    return img

def rotate_image(image, angle):
    """
    Rotates an OpenCV 2 / NumPy image about it's centre by the given angle
    (in degrees). The returned image will be large enough to hold the entire
    new image, with a black background
    """

    # Get the image size
    # No that's not an error - NumPy stores image matricies backwards
    image_size = (image.shape[1], image.shape[0])
    image_center = tuple(np.array(image_size) / 2)

    # Convert the OpenCV 3x2 rotation matrix to 3x3
    rot_mat = np.vstack(
        [cv2.getRotationMatrix2D(image_center, angle, 1.0), [0, 0, 1]]
    )

    rot_mat_notranslate = np.matrix(rot_mat[0:2, 0:2])

    # Shorthand for below calcs
    image_w2 = image_size[0] * 0.5
    image_h2 = image_size[1] * 0.5

    # Obtain the rotated coordinates of the image corners
    rotated_coords = [
        (np.array([-image_w2,  image_h2]) * rot_mat_notranslate).A[0],
        (np.array([ image_w2,  image_h2]) * rot_mat_notranslate).A[0],
        (np.array([-image_w2, -image_h2]) * rot_mat_notranslate).A[0],
        (np.array([ image_w2, -image_h2]) * rot_mat_notranslate).A[0]
    ]

    # Find the size of the new image
    x_coords = [pt[0] for pt in rotated_coords]
    x_pos = [x for x in x_coords if x > 0]
    x_neg = [x for x in x_coords if x < 0]

    y_coords = [pt[1] for pt in rotated_coords]
    y_pos = [y for y in y_coords if y > 0]
    y_neg = [y for y in y_coords if y < 0]

    right_bound = max(x_pos)
    left_bound = min(x_neg)
    top_bound = max(y_pos)
    bot_bound = min(y_neg)

    new_w = int(abs(right_bound - left_bound))
    new_h = int(abs(top_bound - bot_bound))

    # We require a translation matrix to keep the image centred
    trans_mat = np.matrix([
        [1, 0, int(new_w * 0.5 - image_w2)],
        [0, 1, int(new_h * 0.5 - image_h2)],
        [0, 0, 1]
    ])

    # Compute the tranform for the combined rotation and translation
    affine_mat = (np.matrix(trans_mat) * np.matrix(rot_mat))[0:2, :]

    # Apply the transform
    result = cv2.warpAffine(
        image,
        affine_mat,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR
    )

    return result

def rotatedRectWithMaxArea(w, h, angle_degrees):
  angle = math.radians(angle_degrees)
  """
  Given a rectangle of size wxh that has been rotated by 'angle_degrees',
  computes the width and height of the largest possible
  axis-aligned rectangle (maximal area) within the rotated rectangle.
  """
  if w <= 0 or h <= 0:
    return 0,0

  width_is_longer = w >= h
  side_long, side_short = (w,h) if width_is_longer else (h,w)

  # since the solutions for angle, -angle and 180-angle are all the same,
  # if suffices to look at the first quadrant and the absolute values of sin,cos:
  sin_a, cos_a = abs(math.sin(angle)), abs(math.cos(angle))
  if side_short <= 2.*sin_a*cos_a*side_long or abs(sin_a-cos_a) < 1e-10:
    # half constrained case: two crop corners touch the longer side,
    #   the other two corners are on the mid-line parallel to the longer line
    x = 0.5*side_short
    wr,hr = (x/sin_a,x/cos_a) if width_is_longer else (x/cos_a,x/sin_a)
  else:
    # fully constrained case: crop touches all 4 sides
    cos_2a = cos_a*cos_a - sin_a*sin_a
    wr,hr = (w*cos_a - h*sin_a)/cos_2a, (h*cos_a - w*sin_a)/cos_2a

  return wr,hr

def crop_around_center(image, width, height):
    """
    Given a NumPy / OpenCV 2 image, crops it to the given width and height,
    around it's centre point
    """

    image_size = (image.shape[1], image.shape[0])
    image_center = (int(image_size[0] * 0.5), int(image_size[1] * 0.5))

    if(width > image_size[0]):
        width = image_size[0]

    if(height > image_size[1]):
        height = image_size[1]

    x1 = int(image_center[0] - width * 0.5)
    x2 = int(image_center[0] + width * 0.5)
    y1 = int(image_center[1] - height * 0.5)
    y2 = int(image_center[1] + height * 0.5)

    return image[y1:y2, x1:x2]

def rotate_and_crop(img, deg):

    w, h = img.shape[1], img.shape[0]
    # print(w, h)
    img = rotate_image(img, deg)
    new_w, new_h = rotatedRectWithMaxArea(w, h, deg)
    new_w, new_h = int(new_w), int(new_h)
    #print(new_w, new_h)
    img = crop_around_center(img, new_w, new_h)
    #print(f'after crop_around_center {img.shape}')
    img = crop_to_square(img)
    #print(f'after crop_to_square {img.shape}')
    img = cv2.resize(img, (254, 254))
    return img

def jitter_brightness (img, brightness):
    if brightness > 0: 
        shadow = brightness 
        max = 255
    else: 

        shadow = 0
        max = 255 + brightness 

    al_pha = (max - shadow) / 255
    ga_mma = shadow 

    # The function addWeighted calculates 
    # the weighted sum of two arrays 
    cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma)
    return cal       