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

        