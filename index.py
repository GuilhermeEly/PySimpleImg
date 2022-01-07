#!/usr/bin/env python
import os
#Para usar o backend da microsoft sem que demore para abrir o software
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import PySimpleGUI as sg
import cv2
import numpy as np
from app.Controller.imageController import ImageProcessing as imgProc
from app.Controller.cameraController import CameraController as cam
import time
from app.Views.editView import EditView as edtView
from app.Views.mainView import MainView as mView

def main():

    sg.theme('DarkAmber')

    imgProcess = imgProc()
    camController = cam()
    editView = edtView()
    mainView = mView()

    indexCam = camController.get_camera_info()
    
    try:
        imgProcess.loadConfigs()
    except:
        print('Configs not found, using default')

    init = True

    # Crio a janela do programa e passo a localização que ela será exibida no monitor ao abrir
    window = mainView.create_window()

    #Atualizo a câmera que está sendo usada
    #CAP_MSMF consegue 30 fps e ajustar white balance
    cap = cv2.VideoCapture(indexCam, cv2.CAP_MSMF)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    #Por algum motivo especifico, a câmera nao ajusta as configurações sem que antes 
    #seja realizada uma captura, portanto:
    cap.read()
    #Desligo o foco automático
    cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
    #Desligo a exposição automática
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25)
    #Seto para menor exposição possível 10e-7
    cap.set(cv2.CAP_PROP_EXPOSURE, -5)
    #Seto a temperatura da imagem para um valor fixo, forçando sair do automático
    cap.set(cv2.CAP_PROP_TEMPERATURE, 3333)

    recording = False

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    while True:
        #Verifico os eventos do GUI
        event, values = window.read(timeout=20)

        #Controle de foco pelo slider, caso seja necessário
        cap.set(cv2.CAP_PROP_FOCUS,imgProcess.focusPercentage)
        
        if event == 'Sair' or event == sg.WIN_CLOSED:
            imgProcess.saveConfigs()
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
            
            ret, frame = cap.read()

            #Redimensiona a imagem para facilitar a comparação
            loadCompare = frame

            encodedCompared, encodedDiff, encodedMask = imgProcess.executeComparison(loadDefault.copy(), loadCompare.copy())

            window['image2'].update(data=encodedCompared)
            window['image4'].update(data=encodedDiff)
            window['image5'].update(data=encodedMask)

        #Salva a imagem padrão
        elif event == 'Salvar':
            ret, frame = cap.read()

            loadDefault = imgProcess.addCornerSquare(frame)

            loadDefaulttest = imgProcess.resizeImage(frame, imgProcess.imageProcessScale)

            encodedDefaulttest = cv2.imencode('.png', loadDefaulttest)[1].tobytes()
            window['image'].update(data=encodedDefaulttest)

        elif event == 'Editar':
            
            windowEdit = editView.create_window()

            first = True

            while True:

                event, values = windowEdit.read(timeout=20)

                if first:
                    first = False
                    windowEdit['sizeX'].update(imgProcess.rectangleLimitSizeX)
                    windowEdit['sizeY'].update(imgProcess.rectangleLimitSizeY)
                    windowEdit['originX'].update(imgProcess.rectangleLimitOriginX)
                    windowEdit['originY'].update(imgProcess.rectangleLimitOriginY)
                    windowEdit['editFocus'].update(imgProcess.focusPercentage)
                    windowEdit['editBrightness'].update(imgProcess.brightness)
                    windowEdit['editContrast'].update(imgProcess.contrast)
                    windowEdit['editSaturation'].update(imgProcess.saturation)
                    windowEdit['editArea'].update(imgProcess.minArea)
                    

                if event == "Salvar" or event == sg.WIN_CLOSED:
                    imgProcess.saveConfigs()
                    windowEdit.close()
                    break
                
                imgProcess.setRecatangleSizeX(int(values['sizeX']))
                imgProcess.setRecatangleSizeY(int(values['sizeY']))
                imgProcess.setRectangleLimitOriginX(int(values['originX']))
                imgProcess.setRectangleLimitOriginY(int(values['originY']))
                
                ret, frame = cap.read()
                frame = imgProcess.resizeImage(frame, imgProcess.imageProcessScale)

                sliderSizeX = windowEdit['sizeX']
                sliderSizeY = windowEdit['sizeY']
                sliderOriginX = windowEdit['originX']
                sliderOriginY = windowEdit['originY']

                if values['originX'] >= values['sizeX']:
                    windowEdit['originX'].update(values['sizeX']-1)

                if values['originY'] >= values['sizeY']:
                    windowEdit['originY'].update(values['sizeY']-1)

                sliderSizeX.Update(range=(0, frame.shape[1]))
                sliderSizeY.Update(range=(0, frame.shape[0]))
                sliderOriginX.Update(range=(0, (frame.shape[1]-10)))
                sliderOriginY.Update(range=(0, frame.shape[0]))

                cap.set(cv2.CAP_PROP_FOCUS,values['editFocus'])
                imgProcess.setFocusPercentage(values['editFocus'])
                cap.set(cv2.CAP_PROP_BRIGHTNESS,values['editBrightness'])
                imgProcess.setBrightness(values['editBrightness'])
                cap.set(cv2.CAP_PROP_CONTRAST,values['editContrast'])
                imgProcess.setContrast(values['editContrast'])
                cap.set(cv2.CAP_PROP_SATURATION,values['editSaturation'])
                imgProcess.setSaturation(values['editSaturation'])
                imgProcess.setMinArea(values['editArea'])

                frame = imgProcess.addCropRectangle(frame)

                frame = cv2.imencode('.png', frame)[1].tobytes()
                windowEdit['editImage'].update(data=frame)

            windowEdit.close()

        if recording:
            #Captura de imagem
            ret, frame = cap.read()

            #Redimensiona a imagem
            frame = imgProcess.resizeImage(frame, imgProcess.imageProcessScale)

            frame = imgProcess.addCropRectangle(frame)

            #Faz o encode da image para PNG, devido ao PySimpleGUI
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()

            #Atualiza a imagem na tela
            window['image3'].update(data=imgbytes)


main()