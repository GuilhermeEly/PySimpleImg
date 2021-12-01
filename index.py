#!/usr/bin/env python
from skimage.metrics import structural_similarity
import PySimpleGUI as sg
import cv2
import numpy as np
import time

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
        cap.set(cv2.CAP_PROP_FOCUS,50)
        
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

            ret, frame = cap.read()
            loadCompare = resizeImage(frame, framescale)

            result = compareImages(loadDefault, loadCompare)

            encodedDefault = cv2.imencode('.png', result[1])[1].tobytes()
            encodedCompared = cv2.imencode('.png', result[0])[1].tobytes()
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