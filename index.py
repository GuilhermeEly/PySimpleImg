#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
from app.Controller.imageController import ImageProcessing as imgProc

def main():

    print(cv2.__file__)
    sg.theme('Black')

    imgProcess = imgProc()

    init = True
    framescale = 50
    color = [0,0,0] # black

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
            sg.Frame("Diff", layout = [ 
            [
                sg.Image(filename='', key='image4')
            ]]),
            sg.Frame("Mask", layout = [ 
            [
                sg.Image(filename='', key='image5')
            ]])
            
        ],
        [
            sg.Frame("", layout= [
            [
                sg.Button('Camera', size=(10, 1), font='Helvetica 14'),
                sg.Button('Salvar', size=(10, 1), font='Any 14'),
                sg.Button('Comparar', size=(10, 1), font='Any 14'),
                sg.Button('Sair', size=(10, 1), font='Helvetica 14'),
                sg.Slider(range=(1, 100), orientation='h', key='Focus', size=(20, 20), default_value=framescale)
            ]])
        ]
    ]

    # Crio a janela do programa e passo a localização que ela será exibida no monitor ao abrir
    window = sg.Window('Image Processing', layout, location=(10, 10))

    #Atualizo a câmera que está sendo usada
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    #Desligo o foco automático e seto para 50%
    cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
    #cap.set(cv2.CAP_PROP_FOCUS,50)
    recording = False

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    while True:
        
        #Verifico os eventos do GUI
        event, values = window.read(timeout=20)

        #Controle de foco pelo slider, caso seja necessário
        cap.set(cv2.CAP_PROP_FOCUS,values['Focus'])
        
        if event == 'Sair' or event == sg.WIN_CLOSED:
            return

        elif event == 'Camera':
            recording = True

        elif init:
            recording = False
            init = False
            #Faço a população de uma imagem preta genérica em todas as janelas
            img = np.full((150, 150), 0)
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)
            window['image2'].update(data=imgbytes)
            window['image3'].update(data=imgbytes)
            window['image4'].update(data=imgbytes)
            window['image5'].update(data=imgbytes)

        #Compara o padrão com a imagem capturada
        elif event == 'Comparar':
            
            result = []
            ret, frame = cap.read()

            #Redimensiona a imagem para facilitar a comparação
            loadCompare = imgProcess.resizeImage(frame, framescale)

            #Faz a conversão para PNG devido ao formato do PySimpleGUI
            encoded = cv2.imencode('.png', loadDefault)[1].tobytes()

            #Atualiza a imagem do padrão
            window['image'].update(data=encoded)

            #Passo uma cópia do padrão para realizar a comparação sem alterar o padrão original
            patternImage = loadDefault.copy()

            loadCompare, Default = imgProcess.alignImages(patternImage, loadCompare)

            loadCompare = imgProcess.CropImage(loadCompare, 10, 10)
            Default = imgProcess.CropImage(Default, 10, 10)

            #Realizo a comparacao da imagem capturada com o padrão	
            encodedCompared, encodedDefault, encodedUpFilled, encodedDiff, encodedMask = imgProcess.compareImages(Default, loadCompare)

            #Atualizo a imagem de resultado e a imagem de diferenças
            window['image2'].update(data=encodedCompared)
            window['image4'].update(data=encodedDiff)
            window['image5'].update(data=encodedMask)

        #Salva a imagem padrão
        elif event == 'Salvar':
            ret, frame = cap.read()
            
            loadDefault = imgProcess.resizeImage(frame, framescale)

            loadDefault = imgProcess.addCornerSquare(loadDefault, 10, 10, 10)

            encodedDefault = cv2.imencode('.png', loadDefault)[1].tobytes()
            window['image'].update(data=encodedDefault)

        if recording:
            #Captura de imagem
            ret, frame = cap.read()

            #Redimensiona a imagem
            frame = imgProcess.resizeImage(frame, framescale)

            frame = imgProcess.addCornerSquare(frame, 10, 10, 10)

            frame = imgProcess.addCropRectangle(frame, 10, 10)

            #Faz o encode da image para PNG, devido ao PySimpleGUI
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()

            #Atualiza a imagem na tela
            window['image3'].update(data=imgbytes)


main()