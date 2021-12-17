#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
from app.Controller.imageController import ImageProcessing as imgProc
from app.Controller.cameraController import CameraController as cam
import time
import matplotlib.pyplot as plt

def alignImages(defaultAlign, ComparedImage):
    # Converte imagens para escala de cinza
    im1_gray = cv2.cvtColor(defaultAlign,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(ComparedImage,cv2.COLOR_BGR2GRAY)

    # Retorna o tamanho da imagem
    sz = defaultAlign.shape

    # Define o algoritmo de alinhamento
    warp_mode = cv2.MOTION_HOMOGRAPHY

    # Define a matriz inicial de alinhamento conforme a necessidade do algoritmo escolhido
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
        warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Número de iteracoes para o algoritmo de alinhamento
    number_of_iterations = 4000
    
    # Limite de incremento entre duas iteracoes
    termination_eps = (1e-10)
    
    # Definição de critérios
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

    # Roda o algoritmo, retornando a matriz de alinhamento em warp_matrix
    start = time.time()
    (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)
    print("--- %s seconds ---" % (time.time() - start))

    start = time.time()
    #Realinha a imagem original conforme a matriz de alinhamento
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        # Usa warpPerspective para Homography
        im2_aligned = cv2.warpPerspective (ComparedImage, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
        # Usa warpAffine para Translation, Euclidean and Affine
        im2_aligned = cv2.warpAffine(ComparedImage, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    #Converte o resultado de BGR para RGB
    aligned_gray = cv2.cvtColor(im2_aligned,cv2.COLOR_BGR2RGB)

    return aligned_gray, defaultAlign

def main():

    sg.theme('DarkAmber')

    imgProcess = imgProc()
    camController = cam()

    availableCam = camController.get_camera_info()

    for camera in availableCam:
        if camera['camera_name'] == 'HD Pro Webcam C920':
            indexCam = camera['camera_index']
            break
    
    try:
        imgProcess.loadConfigs()
    except:
        print('Configs not found, using default')

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
                sg.Button('Editar', size=(10, 1), font='Any 14')
            ]])
        ]
    ]

    # Crio a janela do programa e passo a localização que ela será exibida no monitor ao abrir
    window = sg.Window('Image Processing', layout, location=(10, 10))

    #Atualizo a câmera que está sendo usada
    cap = cv2.VideoCapture(indexCam, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    #Desligo o foco automático
    cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -5)
    print(cap.get(cv2.CAP_PROP_FPS))

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
            
            result = []
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

            #loadCompare = imgProcess.CropImage(loadCompare)
            #Default = imgProcess.CropImage(Default)

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

            #loadDefaulttest = imgProcess.addCornerSquare(loadDefaulttest)

            encodedDefaulttest = cv2.imencode('.png', loadDefaulttest)[1].tobytes()
            window['image'].update(data=encodedDefaulttest)

        elif event == 'Editar':

            layoutEdit = [
                [
                    sg.Frame("Edit", layout= [
                    [
                        sg.Image(filename='', key='editImage')
                    ]]),
                    sg.Frame("Opções", layout= [
                    [
                        sg.Column(layout=[
                            [sg.Text("Origem")],
                            [sg.Text("X"), sg.Slider(range=(0, 10000), orientation='h', key='originX', size=(30, 20), default_value=0)],
                            [sg.Text("Y"), sg.Slider(range=(0, 10000), orientation='h', key='originY', size=(30, 20), default_value=0)],
                            [sg.Text("Tamanho")],
                            [sg.Text("X"), sg.Slider(range=(0, 10000), orientation='h', key='sizeX', size=(30, 20), default_value=50)],
                            [sg.Text("Y"), sg.Slider(range=(0, 10000), orientation='h', key='sizeY', size=(30, 20), default_value=50)],
                            [sg.Text("Foco")],
                            [sg.Text("F:"), sg.Slider(range=(0, 255), tick_interval=51, resolution=5,  orientation='h', key='editFocus', size=(30, 20), default_value=50)],
                            [sg.Text("Brilho")],
                            [sg.Text("B:"), sg.Slider(range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editBrightness', size=(30, 15), default_value=50)],
                            [sg.Text("Contraste")],
                            [sg.Text("C:"), sg.Slider(range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editContrast', size=(30, 15), default_value=50)],
                            [sg.Text("Saturação")],
                            [sg.Text("S:"), sg.Slider(range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editSaturation', size=(30, 15), default_value=50)],
                        ], size=(300, 650)),
                        
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

                #frame = imgProcess.addCornerSquare(frame)
                frame = imgProcess.addCropRectangle(frame)

                frame = cv2.imencode('.png', frame)[1].tobytes()
                windowEdit['editImage'].update(data=frame)

            windowEdit.close()

        if recording:
            #Captura de imagem
            ret, frame = cap.read()

            #Redimensiona a imagem
            frame = imgProcess.resizeImage(frame, imgProcess.imageProcessScale)

            #frame = imgProcess.addCornerSquare(frame)

            frame = imgProcess.addCropRectangle(frame)

            #Faz o encode da image para PNG, devido ao PySimpleGUI
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()

            #Atualiza a imagem na tela
            window['image3'].update(data=imgbytes)


main()