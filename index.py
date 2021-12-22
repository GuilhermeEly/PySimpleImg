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

def main():

    sg.theme('DarkAmber')

    imgProcess = imgProc()
    camController = cam()

    indexCam = camController.get_camera_info()
    
    try:
        imgProcess.loadConfigs()
    except:
        print('Configs not found, using default')

    init = True

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
                sg.Button('Editar', size=(10, 1), font='Any 14')
            ]])
        ]
    ]

    # Crio a janela do programa e passo a localização que ela será exibida no monitor ao abrir
    window = sg.Window('Image Processing', layout, location=(10, 10))

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

            #Faz a conversão para PNG devido ao formato do PySimpleGUI
            encoded = cv2.imencode('.png', loadDefaulttest)[1].tobytes()

            #Atualiza a imagem do padrão
            window['image'].update(data=encoded)

            #Passo uma cópia do padrão para realizar a comparação sem alterar o padrão original
            patternImage = loadDefault.copy()
            start_time = time.time()
            patternImage = imgProcess.CropImage(patternImage)
            loadCompare = imgProcess.CropImage(loadCompare)
            loadCompare, Default = imgProcess.alignImages(patternImage, loadCompare)
            print("Alinhamento--- %s seconds ---" % (time.time() - start_time))

            start_time = time.time()
            #Realizo a comparacao da imagem capturada com o padrão	
            encodedCompared, encodedDefault, encodedUpFilled, encodedDiff, encodedMask = imgProcess.compareImages(Default, loadCompare)
            print("Comparação--- %s seconds ---" % (time.time() - start_time))
            #Atualizo a imagem de resultado e a imagem de diferenças
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
            sliderSize = (30, 5)
            textSize = (10, 1)
            textConf = 'Helvetica 8 italic'
            titleTextConfig = 'Helvetica 8 bold'

            layoutEdit = [
                [
                    sg.Frame("Edit", layout= [
                    [
                        sg.Image(filename='', key='editImage')
                    ]]),
                    sg.Frame("Opções", layout= [
                    [
                        sg.Column(layout=
                        [
                            [
                                sg.Text("Área válida", font = titleTextConfig)
                            ],
                            [
                                sg.Text("X0:", font = textConf, s = textSize),
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='originX', size = sliderSize, default_value=0),
                                sg.Text("X1:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='sizeX', size = sliderSize, default_value=50),
                            ],
                            [
                                sg.Text("Y0:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='originY', size = sliderSize, default_value=0),
                                sg.Text("Y1:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='sizeY', size = sliderSize, default_value=50),
                            ],
                            [
                                sg.Text("Configurações", font = titleTextConfig)
                            ],
                            [
                                sg.Text("Foco:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=5,  orientation='h', key='editFocus', size = sliderSize, default_value=50),
                                sg.Text("Brilho:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editBrightness', size = sliderSize, default_value=50)
                            ],
                            [
                                sg.Text("Contraste:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editContrast', size = sliderSize, default_value=50),
                                sg.Text("Saturação:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editSaturation', size = sliderSize, default_value=50)
                            ],
                            [
                                sg.Text("Erro:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 100), tick_interval=20, orientation='h', key='editArea', size = sliderSize, default_value=50)
                            ],
                        ], size=(600, 280)),
                        
                    ]]),
                ],
                [
                    sg.Frame("", layout= [
                    [
                        sg.Button('Salvar', size=(10, 1), font='Helvetica 14'),
                    ]])
                ]
            ]
            windowEdit = sg.Window("Edit Window", layoutEdit, modal=True, location=(10, 10))

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