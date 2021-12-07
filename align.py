#!/usr/bin/python

'''
    OpenCV Image Alignment  Example
    
    Copyright 2015 by Satya Mallick <spmallick@learnopencv.com>
    
'''

import cv2
import numpy as np
import time
import os


if __name__ == '__main__':

    # Read the images to be aligned
    im1 =  cv2.imread("images/image1.jpg")
    im2 =  cv2.imread("images/image2.jpg")
    
    # Convert images to grayscale
    im1_gray = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)

    # Find size of image1
    sz = im1.shape

    # Define the motion model
    warp_mode = cv2.MOTION_HOMOGRAPHY

    # Define 2x3 or 3x3 matrices and initialize the matrix to identity
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
        warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Specify the number of iterations.
    number_of_iterations = 4000
    
    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = (1e-10)
    
    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

    # Run the ECC algorithm. The results are stored in warp_matrix.
    start = time.time()
    (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)
    print("--- %s seconds ---" % (time.time() - start))

    start = time.time()
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        # Use warpPerspective for Homography
        im2_aligned = cv2.warpPerspective (im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
        # Use warpAffine for Translation, Euclidean and Affine
        im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    print("--- %s seconds ---" % (time.time() - start))
    # Show final results
    start = time.time()
    cv2.imshow("Image 1", im1)
    cv2.imshow("Image 2", im2)
    cv2.imshow("Aligned Image 2", im2_aligned)
    print("--- %s seconds ---" % (time.time() - start))

    directory = r'C:\Users\gely\Desktop\Desenvolvimento\Python\SimplePyImg\images'
    os.chdir(directory)
    filename = 'aligned.jpg'
    cv2.imwrite(filename, im2_aligned)
    cv2.waitKey(0)