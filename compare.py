from skimage.metrics import structural_similarity
import PySimpleGUI as sg
import cv2
import numpy as np
import matplotlib.pyplot as plt

def resizeImage(image, percent):
    width = int(image.shape[1] * percent / 100)
    height = int(image.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def compareImages(DefaultImage, ComparedImage):
    scaledown_percent = 100

    DefaultImageResized = resizeImage(DefaultImage, scaledown_percent)

    DefaultImage = resizeImage(DefaultImage, scaledown_percent)
    ComparedImage = resizeImage(ComparedImage, scaledown_percent)

    DefaultBlured = cv2.GaussianBlur(DefaultImage, (5, 5), 0)
    ComparedBlured = cv2.GaussianBlur(ComparedImage, (5, 5), 0)

    DefaultGray = cv2.cvtColor(DefaultBlured, cv2.COLOR_BGR2GRAY)
    ComparedGray = cv2.cvtColor(ComparedBlured, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(DefaultGray, ComparedGray, full=True)
    print("Image similarity", score)

    diff = (diff * 255).astype("uint8")

    if(score>0.994):
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV)[1]

    else:
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = contours[0] if len(contours) == 2 else contours[1]
    mask = np.zeros(DefaultBlured.shape, dtype='uint8')
    filled_after = ComparedBlured.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if area > 250:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(DefaultImage, (x, y), (x + w, y + h), (36,255,12), 2)
            cv2.rectangle(ComparedImage, (x, y), (x + w, y + h), (36,255,12), 2)
            cv2.drawContours(mask, [c], 0, (0,255,0), -1)
            cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)

    scaleup_percent = 100 # percent of original size

    resultCompared = resizeImage(ComparedImage, scaleup_percent)

    upfilled = resizeImage(filled_after, scaleup_percent)

    DefaultImageResized = resizeImage(DefaultImageResized, scaleup_percent)

    return resultCompared, DefaultImageResized, upfilled, diff

pattern = cv2.imread(r'C:\Users\gely\Desktop\Desenvolvimento\Python\SimplePyImg\images\image1.jpg')
aligned = cv2.imread(r'C:\Users\gely\Desktop\Desenvolvimento\Python\SimplePyImg\images\aligned.jpg') 

result = compareImages(pattern, aligned)

plt.imshow(result[3], cmap='gray')
plt.show()