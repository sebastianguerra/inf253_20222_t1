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




# Extract width
ancho_pattern = r"^Ancho (?P<ancho>\d+)" # Captura el Ancho dado

number_pattern = r"0|[1-9](?:0|[1-9])*"

# Colores
color_pattern = r"Rojo|Verde|Azul|Negro|Blanco|RGB *\( *(?:{np}) *, *(?:{np}) *, *(?:{np}) *\)".format(np = number_pattern)

# Background color
bg_color_pattern = r"Color de fondo (?P<bg_color>{})".format(color_pattern) # Captura el color de fondo

# declaraciones
avanzar_statement_pattern = r"Avanzar(?: [1-9][0-9]*)?".format(number_pattern)
girar_statement_pattern = r"Izquierda|Derecha"
pintar_statement_pattern = r"Pintar (?: {})".format(color_pattern)
repetir_statement_pattern = r"Repetir [1-9][0-9]* veces {"

statements_pattern = "|".join([avanzar_statement_pattern, girar_statement_pattern, pintar_statement_pattern, repetir_statement_pattern])


def parseColor(color):
    '''
    Parsea un color en formato RGB(d, d, d) y devuelve una tupla de enteros.
    Tambien puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'
        Parametros:
                color (str): Color.
    '''
    esUnColorPredefinido = re.compile(r"(Rojo)|(Verde)|(Azul)|(Negro)|(Blanco)")
    if esUnColorPredefinido.match(color) == None:
        extract_colors = re.compile(r"RGB *\( *({np}) *, *({np}) *, *({np}) *\)".format(np = number_pattern))
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

def run(code, state = [0, 0]):
    '''
    Recibe un string con el codigo a ejecutar y ejecuta la primera sentencia. Luego ejecuta el resto de forma recursiva.
    Devuelve una tupla con el estado final
    '''
    closed = re.match(r"}", code)
    if closed != None:
        state[1] -= 1
        print("}")
        run(code[2:], state)
    match = re.match(r"({})([a-zA-Z0-9{} \n\t]*)".format(statements_pattern, "{}"), code)
    if match == None:
        return None
    
    h, t = match.groups()
    t = re.sub(r"^ ", "", t)
    print("\t"*state[1]+h)
    if re.match(repetir_statement_pattern, h) != None:
        state[1] += 1
    run(t, [state[0]+1, state[1]])

        



codigo = '''Ancho 8
Color de fondo RGB(13,181,13)

Avanzar Derecha Avanzar 2
Pintar Negro Avanzar
Repetir 2 veces { Pintar Negro Izquierda Avanzar }
Pintar Negro
Derecha Avanzar 3
Pintar Negro Avanzar
Repetir 2 veces { Pintar Negro Derecha Avanzar }
Pintar Negro
Izquierda Avanzar
Repetir 3 veces { Avanzar Pintar Negro }
Derecha Avanzar 3 Derecha
Repetir 3 veces { Pintar Negro Avanzar}
Derecha Avanzar
Repetir 3 veces {
Pintar Negro Avanzar
Pintar Negro Derecha Avanzar
Derecha Avanzar Derecha Derecha
}'''




# Verify that the code is well formed
verify = re.compile(''.join([ ancho_pattern, r"\n", bg_color_pattern, r"(?: *\n){2}(?P<code>[a-zA-Z0-9{} \n\t]*$)" ]))
verify = verify.match(codigo)
if verify == None:
    pass # TODO Error
    print("Error: Codigo mal formado")
    exit()

ancho_elegido = int(verify.group('ancho'))
color_elegido = parseColor(verify.group('bg_color'))
comandos = verify.group('code')
comandos = re.sub(r"(\n)+|(\t)+", r" ", comandos) # Elimina saltos de linea y tabs
comandos = re.sub(r"( )+", r" ", comandos) # Elimina espacios repetidos

print("Ancho:")
print(ancho_elegido)
print("Color:")
print(color_elegido)
print("Comandos:")
print(comandos)

run(comandos)






