#!/usr/bin/env python3
import re

import numpy as np
from PIL import Image

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


def parseColor(color):
    '''
    Parsea un color en formato RGB(d, d, d) y devuelve una tupla de enteros.
    Tambien puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'
        Parametros:
                color (str): Color.
    '''
    esUnColorPredefinido = re.compile(r"(Rojo)|(Verde)|(Azul)|(Negro)|(Blanco)")
    if esUnColorPredefinido.match(color) == None:
        extract_colors = re.compile(r"RGB\((\d+), (\d+), (\d+)\)")
        extract_colors = extract_colors.match(color)
        if extract_colors == None:
            pass # TODO: Error
            print("Error: Color no reconocido")
            exit()
        grupos = extract_colors.groups()
        R, G, B = grupos
        return (int(R), int(G), int(B))
    else:
        if color == 'Rojo':
            return (255, 0, 0)
        elif color == 'Verde':
            return (0, 255, 0)
        elif color == 'Azul':
            return (0, 0, 255)
        elif color == 'Negro':
            return (0, 0, 0)
        elif color == 'Blanco':
            return (255, 255, 255)
        else:
            pass # TODO Error
            print("Error: Nombre de color equivocado")
            exit()


codigo = '''Ancho 10
Color de fondo RGB(255, 0, 0)

Avanzar Derecha Avanzar
Repetir 4 veces {
	Repetir 8 veces { Pintar Negro Avanzar }
	Derecha Derecha Avanzar Derecha
}
'''



# Extract width
Ancho_Pattern = r"^Ancho (\d+)"


# Extract background color
Background_color = r"Color de fondo (.+)"
color_fondo = re.compile(r"^Color de fondo (.+)$", re.M)
color_fondo = color_fondo.search(codigo)
if color_fondo == None:
    pass # TODO Error
    print("Error: No se encontro el color de fondo")
    exit()
color_fondo = color_fondo.groups()[0]
color_fondo = parseColor(color_fondo)
print("Color de fondo:", color_fondo)


# Verify that the code is well formed
verify = re.compile(Ancho_Pattern+r"\nColor de fondo (.+)(?: *\n){2}([a-zA-Z0-9{} \n\t]*$)")
verify = verify.match(codigo)
if verify == None:
    pass # TODO Error
    print("Error: Codigo mal formado")
    exit()
command = verify.groups()

print()
print()
print("comandos:")
print(command)
print()
for comando in command:
    print(comando)







