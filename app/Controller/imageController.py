from tkinter.constants import X
import cv2
import numpy as np
from skimage.metrics import structural_similarity
import json


class ImageProcessing():

    #Default Values
    minArea = 10
    imageProcessScale = 50
    imageShowScale = 300
    iterationNumbers = 4000 # Número de iteracoes para o algoritmo de alinhamento
    iterationStep = (1e-10) # Limite de incremento entre duas iteracoes
    scoreLimit = 0.99       # Limite de score para definir o filtro de comparação
    rectangleLimitOriginX = 0
    rectangleLimitOriginY = 0
    rectangleLimitSizeX = 100
    rectangleLimitSizeY = 100
    focusPercentage = 50
    sqrSize = 8


    def init(self):
        pass    

    def setFocusPercentage(self, percentage):
        self.focusPercentage = percentage

    def setRectangleLimitOriginX(self, x):
        self.rectangleLimitOriginX = x

    def setRectangleLimitOriginY(self, y):
        self.rectangleLimitOriginY = y

    def setRecatangleSizeX(self, x):
        self.rectangleLimitSizeX = x

    def setRecatangleSizeY(self, y):
        self.rectangleLimitSizeY = y

    def setSqrSize(self, size):
        self.sqrSize = size

    def saveConfigs(self):
        data = {}

        data['config'] = []

        data['config'].append({
            'minArea':                  self.minArea,
            'imageProcessScale':        self.imageProcessScale,
            'imageShowScale':           self.imageShowScale,
            'iterationNumbers':         self.iterationNumbers,
            'iterationStep':            self.iterationStep,
            'scoreLimit':               self.scoreLimit,
            'rectangleLimitOriginX':    self.rectangleLimitOriginX,
            'rectangleLimitOriginY':    self.rectangleLimitOriginY,
            'rectangleLimitSizeX':      self.rectangleLimitSizeX,
            'rectangleLimitSizeY':      self.rectangleLimitSizeY,
            'focusPercentage':          self.focusPercentage,
            'sqrSize':                  self.sqrSize
        })

        with open('config\imageProcessingConfig.json', 'w') as f:
            json.dump(data, f)

    def loadConfigs(self):
        with open('config\imageProcessingConfig.json', 'r') as f:
            data = json.load(f)

        try:
            for config in data['config']:
                self.minArea =                  config['minArea']
                self.imageProcessScale =        config['imageProcessScale']
                self.imageShowScale =           config['imageShowScale']
                self.iterationNumbers =         config['iterationNumbers']
                self.iterationStep =            config['iterationStep']
                self.scoreLimit =               config['scoreLimit']
                self.rectangleLimitOriginX =    config['rectangleLimitOriginX']
                self.rectangleLimitOriginY =    config['rectangleLimitOriginY']
                self.rectangleLimitSizeX =      config['rectangleLimitSizeX']
                self.rectangleLimitSizeY =      config['rectangleLimitSizeY']
                self.focusPercentage =          config['focusPercentage']
                self.sqrSize =                  config['sqrSize']

        except Exception as e:
            print("Não foi possível carregar as configurações salvas, usando as padrões\n" + str(e))
    

    def CropImage(self, image):
        x0 = self.rectangleLimitOriginX
        y0 = self.rectangleLimitOriginY
        x1 = self.rectangleLimitSizeX
        y1 = self.rectangleLimitSizeY

        return image[y0:y1, x0:x1]


    def addCropRectangle(self, image):
        x0 = self.rectangleLimitOriginX
        y0 = self.rectangleLimitOriginY
        x1 = self.rectangleLimitSizeX
        y1 = self.rectangleLimitSizeY

        centerX = int((x1-x0)/2) + x0
        centerY = int((y1-y0)/2) + y0

        markSize = 15

        cv2.line(image,(centerX-markSize,centerY),(centerX+markSize,centerY),(0,255,255),1)
        cv2.line(image,(centerX,centerY-markSize),(centerX,centerY+markSize),(0,255,255),1)
        
        return cv2.rectangle(image, (x0, y0), (x1, y1), (0,255,255), 2)

    def addCornerSquare(self, image):
        color = [0,0,0]

        x0 = self.rectangleLimitOriginX
        y0 = self.rectangleLimitOriginY
        x1 = self.rectangleLimitOriginX + self.sqrSize
        y1 = self.rectangleLimitOriginY + self.sqrSize

        return cv2.rectangle(image, (x0, y0), (x1, y1), color, -1)

    def resizeImage(self, image, percent):
        width = int(image.shape[1] * percent / 100)
        height = int(image.shape[0] * percent / 100)
        dim = (width, height)
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    def alignImages(self, defaultAlign, ComparedImage):
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

        # Definição de critérios
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.iterationNumbers,  self.iterationStep)

        # Roda o algoritmo, retornando a matriz de alinhamento em warp_matrix
        (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)

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

    def compareImages(self, DefaultImage, ComparedImage):

        DefaultImageHolder = DefaultImage

        # Aplica um filtro gaussiano nas imagens para diminuir a quantidade de detalhes
        DefaultBlured = cv2.GaussianBlur(DefaultImage, (5, 5), 0)
        ComparedBlured = cv2.GaussianBlur(ComparedImage, (5, 5), 0)

        # Converte as imagens para escala de cinza
        DefaultGray = cv2.cvtColor(DefaultBlured, cv2.COLOR_BGR2GRAY)
        ComparedGray = cv2.cvtColor(ComparedBlured, cv2.COLOR_BGR2GRAY)

        # Calcula a similaridade entre as imagens
        (score, diff) = structural_similarity(DefaultGray, ComparedGray, full=True)
        print("Image similarity", score)

        # Converte a matriz de 0 e 1 para uma de 0 e 255
        diff = (diff * 255).astype("uint8")

        # Retorna uma imagem baseada nos limites estabelecidos
        # Quando a similaridade é muito alta, o threshold OTSU apresenta resultados ruins 
        if score > self.scoreLimit:
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV)[1]
        else:
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
            if area > self.minArea:
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(DefaultImage, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.rectangle(ComparedImage, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.drawContours(mask, [c], 0, (0,255,0), -1)
                cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)

        scaleup_percent = self.imageShowScale # percent of original size

        resultCompared = self.resizeImage(ComparedImage, scaleup_percent)

        upfilled = self.resizeImage(filled_after, scaleup_percent)

        resultCompared = cv2.cvtColor(resultCompared, cv2.COLOR_BGR2RGB)

        resultCompared = cv2.imencode('.png', resultCompared)[1].tobytes()
        DefaultImageHolder = cv2.imencode('.png', DefaultImageHolder)[1].tobytes()
        upfilled = cv2.imencode('.png', upfilled)[1].tobytes()
        diff = cv2.imencode('.png', diff)[1].tobytes()
        mask = cv2.imencode('.png', mask)[1].tobytes()

        return resultCompared, DefaultImageHolder, upfilled, diff, mask

    def delete(self):
        pass