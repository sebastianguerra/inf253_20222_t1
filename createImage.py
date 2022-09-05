#!/usr/bin/env python3

import numpy as np # pip install numpy
from PIL import Image # pip install Pllow

# data = [
#     [(255, 255, 255), (0, 0, 0), (0, 0  , 255)],
#     [(0  , 0  , 0  ), (0, 0, 0), (0, 0  , 0  )],
#     [(255, 255, 255), (0, 0, 0), (0, 255, 0  )],  
# ]

def MatrizAImagen(matriz, filename='pixelart.png', factor=10):
    '''
    Convierte una matriz de valores RGB en una imagen y la guarda como un archivo png.
    Las imagenes son escaladas por un factor ya que con los ejemplos se producirian imagenes muy pequeñas.
        Parametros:
                matriz (lista de lista de tuplas de enteros): Matriz que representa la imagen en rgb.
                filename (str): Nombre del archivo en que se guardara la imagen.
                factor (int): Factor por el cual se escala el tamaño de las imagenes.
    '''
    matriz = np.array(matriz, dtype=np.uint8)
    np.swapaxes(matriz, 0, -1)

    N = np.shape(matriz)[0]

    img = Image.fromarray(matriz, 'RGB')
    img = img.resize((N*factor, N*factor), Image.Resampling.BOX)
    img.save(filename)

# MatrizAImagen(data)
