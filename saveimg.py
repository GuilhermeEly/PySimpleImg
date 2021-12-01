# Python program to explain cv2.imwrite() method

# importing cv2
import cv2

# importing os module
import os

# Image path
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
cap.set(cv2.CAP_PROP_FOCUS,60)
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
filename = 'image1.jpg'

# Using cv2.imwrite() method
# Saving the image
cv2.imwrite(filename, frame)

# List files and directories
# in 'C:/Users / Rajnish / Desktop / GeeksforGeeks'
print("After saving image:")
print(os.listdir(directory))

print('Successfully saved')
