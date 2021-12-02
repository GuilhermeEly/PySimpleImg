#!/usr/bin/env python
from skimage.metrics import structural_similarity
import PySimpleGUI as sg
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

def alignImages(defaultAlign, ComparedImage):
    # Convert images to grayscale
    im1_gray = cv2.cvtColor(defaultAlign,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(ComparedImage,cv2.COLOR_BGR2GRAY)

    # Find size of image1
    sz = defaultAlign.shape

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
        im2_aligned = cv2.warpPerspective (ComparedImage, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
        # Use warpAffine for Translation, Euclidean and Affine
        im2_aligned = cv2.warpAffine(ComparedImage, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    aligned_gray = cv2.cvtColor(im2_aligned,cv2.COLOR_BGR2RGB)

    return aligned_gray, defaultAlign

def compareImages(DefaultImage, ComparedImage):
    scaledown_percent = 100

    DefaultImageHolder = DefaultImage

    #DefaultImage = resizeImage(DefaultImage, scaledown_percent)
    #ComparedImage = resizeImage(ComparedImage, scaledown_percent)

    DefaultBlured = cv2.GaussianBlur(DefaultImage, (5, 5), 0)
    ComparedBlured = cv2.GaussianBlur(ComparedImage, (5, 5), 0)

    print(DefaultBlured.shape)
    print(ComparedBlured.shape)

    DefaultGray = cv2.cvtColor(DefaultBlured, cv2.COLOR_BGR2GRAY)
    ComparedGray = cv2.cvtColor(ComparedBlured, cv2.COLOR_BGR2GRAY)

    #DefaultGray = DefaultBlured
    #ComparedGray = ComparedBlured

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
        if area > 30:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(DefaultImage, (x, y), (x + w, y + h), (36,255,12), 2)
            cv2.rectangle(ComparedImage, (x, y), (x + w, y + h), (36,255,12), 2)
            cv2.drawContours(mask, [c], 0, (0,255,0), -1)
            cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)

    scaleup_percent = 100 # percent of original size

    resultCompared = resizeImage(ComparedImage, scaleup_percent)

    upfilled = resizeImage(filled_after, scaleup_percent)

    return resultCompared, DefaultImageHolder, upfilled, diff

def resizeImage(image, percent):
    width = int(image.shape[1] * percent / 100)
    height = int(image.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def main():

    print(cv2.__file__)
    sg.theme('Black')

    init = True
    framescale = 50

    layout = [
        [
            sg.Frame("Padrão", layout= [
            [
                sg.Image(filename='', key='image')
            ]]),
            sg.Frame("Feedback", layout = [ 
            [
                sg.Image(filename='', key='image3')
            ]])      
        ],
        [
            sg.Frame("Diferenças", layout = [ 
            [
                sg.Image(filename='', key='image2')
            ]]),
            sg.Frame("Mask", layout = [ 
            [
                sg.Image(filename='', key='image4')
            ]])
        ],
        [
            sg.Frame("", layout= [
            [
                sg.Button('Camera', size=(10, 1), font='Helvetica 14'),
                sg.Button('Salvar', size=(10, 1), font='Any 14'),
                sg.Button('Comparar', size=(10, 1), font='Any 14'),
                sg.Button('Parar', size=(10, 1), font='Any 14'),
                sg.Button('Sair', size=(10, 1), font='Helvetica 14'),
                sg.Slider(range=(1, 100), orientation='h', key='Focus', size=(20, 20), default_value=framescale)
            ]])
        ]
    ]

    # create the window and show it without the plot
    window = sg.Window('Image Processing', layout, location=(10, 10))

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
    cap.set(cv2.CAP_PROP_FOCUS,50)
    recording = False

    while True:
        
        event, values = window.read(timeout=20)

        #Controle de foco pelo slider, caso seja necessário
        #cap.set(cv2.CAP_PROP_FOCUS,values['Focus'])
        cap.set(cv2.CAP_PROP_FOCUS,80)
        
        if event == 'Sair' or event == sg.WIN_CLOSED:
            return

        elif event == 'Camera':
            recording = True

        elif event == 'Parar' or init:
            recording = False
            init = False
            img = np.full((150, 150), 0)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)
            window['image2'].update(data=imgbytes)
            window['image3'].update(data=imgbytes)
            window['image4'].update(data=imgbytes)

        elif event == 'Comparar':
            
            result = []
            ret, frame = cap.read()
            loadCompare = resizeImage(frame, framescale)

            encoded = cv2.imencode('.png', loadDefault)[1].tobytes()
            window['image'].update(data=encoded)
            patternImage = loadDefault.copy()
            aligned = alignImages(patternImage, loadCompare)#LoadDefault atualizando sem necessidade, verificar

            loadCompare = aligned[0]
            Default = aligned[1]

            result = compareImages(Default, loadCompare)

            comparedResult = cv2.cvtColor(result[0], cv2.COLOR_BGR2RGB)

            encodedDefault = cv2.imencode('.png', result[1])[1].tobytes()
            encodedCompared = cv2.imencode('.png', comparedResult)[1].tobytes()
            encodedTest = cv2.imencode('.png', result[3])[1].tobytes()

            window['image2'].update(data=encodedCompared)
            window['image4'].update(data=encodedTest)

        elif event == 'Salvar':
            ret, frame = cap.read()
            loadDefault = resizeImage(frame, framescale)
            encodedDefault = cv2.imencode('.png', loadDefault)[1].tobytes()
            window['image'].update(data=encodedDefault)

        if recording:
            ret, frame = cap.read()
            frame = resizeImage(frame, framescale)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image3'].update(data=imgbytes)


main()