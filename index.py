#!/usr/bin/env python
from skimage.metrics import structural_similarity
import PySimpleGUI as sg
import cv2
import numpy as np
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

def compareImages(DefaultImage, ComparedImage):
    scaledown_percent = 100

    DefaultImageHolder = DefaultImage

    #DefaultImage = resizeImage(DefaultImage, scaledown_percent)
    #ComparedImage = resizeImage(ComparedImage, scaledown_percent)

    # Aplica um filtro gaussiano nas imagens para diminuir a quantidade de detalhes
    DefaultBlured = cv2.GaussianBlur(DefaultImage, (5, 5), 0)
    ComparedBlured = cv2.GaussianBlur(ComparedImage, (5, 5), 0)

    # Converte as imagens para escala de cinza
    DefaultGray = cv2.cvtColor(DefaultBlured, cv2.COLOR_BGR2GRAY)
    ComparedGray = cv2.cvtColor(ComparedBlured, cv2.COLOR_BGR2GRAY)

    #DefaultGray = DefaultBlured
    #ComparedGray = ComparedBlured

    # Calcula a similaridade entre as imagens
    (score, diff) = structural_similarity(DefaultGray, ComparedGray, full=True)
    print("Image similarity", score)

    # Converte a matriz de 0 e 1 para uma de 0 e 255
    diff = (diff * 255).astype("uint8")

    # Retorna uma imagem baseada nos limites estabelecidos
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Encontra os contornos na imagem
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Cria a máscara de diferenças
    contours = contours[0] if len(contours) == 2 else contours[1]
    mask = np.zeros(DefaultBlured.shape, dtype='uint8')
    filled_after = ComparedBlured.copy()

    # Desenha os contornos das diferenças nas images originais
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
                sg.Button('Sair', size=(10, 1), font='Helvetica 14'),
                sg.Slider(range=(1, 100), orientation='h', key='Focus', size=(20, 20), default_value=framescale)
            ]])
        ]
    ]

    # Crio a janela do programa e passo a localização que ela será exibida no monitor ao abrir
    window = sg.Window('Image Processing', layout, location=(10, 10))

    #Atualizo a câmera que está sendo usada
    cap = cv2.VideoCapture(1)

    #Desligo o foco automático e seto para 50%
    cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
    cap.set(cv2.CAP_PROP_FOCUS,50)
    recording = False

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    while True:
        
        #Verifico os eventos do GUI
        event, values = window.read(timeout=20)

        #Controle de foco pelo slider, caso seja necessário
        #cap.set(cv2.CAP_PROP_FOCUS,values['Focus'])
        #Seto o foco para 80%
        cap.set(cv2.CAP_PROP_FOCUS,80)
        
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

        #Compara o padrão com a imagem capturada
        elif event == 'Comparar':
            
            result = []
            ret, frame = cap.read()

            #Redimensiona a imagem para facilitar a comparação
            loadCompare = resizeImage(frame, framescale)

            #Faz a conversão para PNG devido ao formato do PySimpleGUI
            encoded = cv2.imencode('.png', loadDefault)[1].tobytes()

            #Atualiza a imagem do padrão
            window['image'].update(data=encoded)

            #Passo uma cópia do padrão para realizar a comparação sem alterar o padrão original
            patternImage = loadDefault.copy()
            #aligned = alignImages(patternImage, loadCompare)
            loadCompare, Default = alignImages(patternImage, loadCompare)
            #loadCompare = aligned[0]
            #Default = aligned[1]
            
            #Pega valores de referencia da imagem, para as próximas etapas
            x = 0
            y = 0
            w = loadCompare.shape[1]
            h = loadCompare.shape[0]
            thickness = int((Default.shape[1])*0.1)*2

            #Quando a imagem é alinhada, ela gera distorções nas bordas
            #Para ocultar essas distorções eu adiciono uma "moldura" em cima destas distorções
            #Tanto no padrão quanto na imagem a ser comparada
            loadCompare = cv2.rectangle(loadCompare, (x, y), (x + w, y + h), color, thickness)
            w = Default.shape[1]
            h = Default.shape[0]
            Default = cv2.rectangle(Default, (x, y), (x + w, y + h), color, thickness)

            #Realizo a comparacao da imagem capturada com o padrão	
            result = compareImages(Default, loadCompare)

            #Converto de BGR para RGB
            comparedResult = cv2.cvtColor(result[0], cv2.COLOR_BGR2RGB)

            #Faço a conversão para PNG devido ao formato do PySimpleGUI
            encodedDefault = cv2.imencode('.png', result[1])[1].tobytes()
            encodedCompared = cv2.imencode('.png', comparedResult)[1].tobytes()
            encodedTest = cv2.imencode('.png', result[3])[1].tobytes()

            #Atualizo a imagem de resultado e a imagem de diferenças
            window['image2'].update(data=encodedCompared)
            window['image4'].update(data=encodedTest)

        #Salva a imagem padrão
        elif event == 'Salvar':
            ret, frame = cap.read()
            loadDefault = resizeImage(frame, framescale)
            encodedDefault = cv2.imencode('.png', loadDefault)[1].tobytes()
            window['image'].update(data=encodedDefault)

        if recording:
            #Captura de imagem
            ret, frame = cap.read()

            #Redimensiona a imagem
            frame = resizeImage(frame, framescale)

            #Pega os valores de referência para as próximas etapas
            x = int((frame.shape[1])*0.1)-2
            y = int((frame.shape[1])*0.1)-2
            w = frame.shape[1]
            h = frame.shape[0]

            #Cria um retângulo na região válida da imagem
            cv2.rectangle(frame, (x, y), (-x + w, -y + h), (0,255,255), 2)

            #Cria um X no centro da imagem
            cv2.line(frame,(int(w/2)-15,int(h/2)),(int(w/2)+15,int(h/2)),(0,255,255),1)
            cv2.line(frame,(int(w/2),int(h/2)-15),(int(w/2),int(h/2)+15),(0,255,255),1)

            #Faz o encode da image para PNG, devido ao PySimpleGUI
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            
            #Atualiza a imagem na tela
            window['image3'].update(data=imgbytes)


main()