#!/usr/bin/env python3
import re

import createImage
import util
from patrones import \
        ancho_pattern, \
        bg_color_pattern, \
        newline_placeholder


# txt = '''Ancho 13
# Color de fondo Rojo

# Avanzar Derecha Avanzar 2
# Pintar Blanco Avanzar
# Repetir 2 veces {Pintar Negro Izquierda Avanzar }
# Pintar Negro
# Derecha Avanzar 3
# Pintar Negro Avanzar
# Repetir 2 veces { Pintar Negro Repetir 3 veces {Avanzar} Derecha Avanzar }
# Pintar Negro
# Izquierda Avanzar
# Repetir 3 veces { Avanzar Pintar Negro }
# Derecha Avanzar 3 Derecha
# Repetir 3 veces { Pintar Negro Avanzar}
# Derecha Avanzar
# Repetir 3 veces {
# Pintar Azul Avanzar
# Pintar Negro Derecha Avanzar
# Derecha Avanzar Derecha Derecha
# }'''
# txt = '''Ancho 3
# Color de fondo Blanco

# Avanzar Pintar Negro
# '''

### Crea la imagen de un Creeper
txt = '''Ancho 8
Color de fondo RGB(0,200,0)

Derecha Avanzar Izquierda Avanzar
Repetir 4 veces {
        Pintar Negro Avanzar Derecha
        }
Avanzar 4
Repetir 4 veces {
        Pintar Negro Avanzar Derecha
        }
Derecha Avanzar 2 Derecha Avanzar 2 Derecha Derecha
Repetir 4 veces {
        Pintar Negro Avanzar Derecha
        }
Derecha Derecha Avanzar Izquierda Avanzar Repetir 3 veces {Pintar Negro Avanzar}
Izquierda Avanzar 3 Izquierda Avanzar Repetir 3 veces {Pintar Negro Avanzar}
Izquierda Izquierda Avanzar 2 Derecha Repetir 2 veces {Avanzar Pintar Negro}

'''
print(txt)


# Verify that the code is well formed
verify = re.compile(''.join([ ancho_pattern, r"\n", bg_color_pattern, r"(?: *\n){2}(?P<code>[a-zA-Z0-9{} \n\t]*$)" ]))
verify = verify.match(txt)
if verify == None:
    pass # TODO Error
    print("Error: Codigo mal formado")
    exit()

ancho_elegido = int(verify.group('ancho'))

color_elegido = util.parseColor(verify.group('bg_color'))

codigo = verify.group('code')
# Agrega espacios a los lados de los {}
codigo = re.sub(r"(?! ){", " {", codigo)
codigo = re.sub(r"{(?! )", "{ ", codigo)
codigo = re.sub(r"(?! )}", " }", codigo)
codigo = re.sub(r"}(?! )", "}" , codigo)
codigo = re.sub(r"(\n)+", " {} ".format(newline_placeholder), codigo)
codigo = re.sub(r"(\t)+", r" ", codigo) # Elimina saltos de linea y tabs
codigo = re.sub(r"( )+", r" ", codigo) # Elimina espacios repetidos

print("Ancho:")
print(ancho_elegido)
print("Color:")
print(color_elegido)
print("Codigo:")
print(codigo)
print()

bytecode = util.parseCode(codigo)
print("Bytecode:")
print(bytecode)
def printBytecode(bytecode, ident=0):
    for i in bytecode:
        if i[0] < 10:
            print("0", end="")
        print(i[0], end=' ')
        if i[1] == "R":
            print("\t"*ident, end="")
            print(i[1], i[2][0])
            printBytecode(i[2][1], ident+1)
        else:
            print("\t"*ident, end="")
            print(i[1], i[2])
printBytecode(bytecode)

# dirList = [(1,0), (0,1), (-1,0), (0,-1)]
iMatrix = [[color_elegido for i in range(ancho_elegido)] for j in range(ancho_elegido)]
pos = (0,0)
dir = 0

state = (iMatrix, pos, dir)

state = util.run(bytecode, state, codigo)

# print(state[0])
rMatrix = state[0]
createImage.MatrizAImagen(rMatrix)

