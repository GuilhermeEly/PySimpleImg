# Python program to explain cv2.imwrite() method

# importing cv2
import cv2

# importing os module
import os
import time
from app.Controller.cameraController import CameraController as cam

camController = cam()

availableCam = camController.get_camera_info()

for camera in availableCam:
    if camera['camera_name'] == 'HD Pro Webcam C920':
        indexCam = camera['camera_index']
        break
# Image path
cap = cv2.VideoCapture(indexCam, cv2.CAP_DSHOW)




cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
cap.set(cv2.CAP_PROP_FOCUS,30)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

ret, frame = cap.read()
# Image directory
directory = r'C:\Users\gely\Desktop\Desenvolvimento\Python\SimplePyImg\images'


# Change the current directory
# to specified directory
os.chdir(directory)

# List files and directories
# in 'C:/Users/Rajnish/Desktop/GeeksforGeeks'
print("Before saving image:")
print(os.listdir(directory))

# Filename
filename = 'image2.jpg'

# Using cv2.imwrite() method
# Saving the image
start = time.time()
cv2.imwrite(filename, frame)
print("--- %s seconds ---" % (time.time() - start))

# List files and directories
# in 'C:/Users / Rajnish / Desktop / GeeksforGeeks'
print("After saving image:")
print(os.listdir(directory))

print('Successfully saved')

w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(w,h)
