import cv2
import numpy as np
from skimage.metrics import structural_similarity
import json


class ImageProcessing():

    #Default Values
    minArea = 10
    imageProcessScale = 50
    imageShowScale = 100
    iterationNumbers = 4000 # Número de iteracoes para o algoritmo de alinhamento
    iterationStep = (1e-10) # Limite de incremento entre duas iteracoes
    scoreLimit = 0.99       # Limite de score para definir o filtro de comparação
    rectangleLimitOriginX = 0
    rectangleLimitOriginY = 0


    def init(self):
        pass    

    def CropImage(self, image, percentX, percentY):
        x = int((image.shape[1])*percentX/100)-2
        y = int((image.shape[0])*percentY/100)-2
        w = image.shape[1] - x
        h = image.shape[0] - y

        return image[y:h, x:w]
    
    def addCropRectangle(self, image, percentX, percentY):
        x = int((image.shape[1])*percentX/100)-2
        y = int((image.shape[0])*percentY/100)-2
        w = image.shape[1]
        h = image.shape[0]

        cv2.line(image,(int(w/2)-15,int(h/2)),(int(w/2)+15,int(h/2)),(0,255,255),1)
        cv2.line(image,(int(w/2),int(h/2)-15),(int(w/2),int(h/2)+15),(0,255,255),1)
        
        return cv2.rectangle(image, (x, y), (-x + w, -y + h), (0,255,255), 2)

    def addCornerSquare(self, image, percentX, percentY, squareSize):
        color = [0,0,0] # black

        x = int((image.shape[1])*percentX/100)-2
        y = int((image.shape[0])*percentY/100)-2
        w = (int((image.shape[1])*percentX/100)-2) + squareSize
        h = (int((image.shape[0])*percentY/100)-2) + squareSize

        return cv2.rectangle(image, (x, y), (w, h), color, -1)

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