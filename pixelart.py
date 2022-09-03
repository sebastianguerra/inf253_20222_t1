#!/usr/bin/env python3
import re

import createImage
import util
from patrones import \
        ancho_pattern, \
        bg_color_pattern, \
        newline_placeholder

DEBUG: bool = False

with open("codigo.txt") as f:
    txt: str = f.read()
if DEBUG:
    print(txt)


# Verifica que el codigo tenga la estructura inicial correcta y extrae directamente los valores
verify = re.match(''.join([ ancho_pattern, r" *\n", bg_color_pattern, r" *\n *\n(?P<code>[a-zA-Z0-9{}(), \n\t]*$)" ]), txt)
if verify == None: # El codigo no cumple con la estructura necesaria
    pass # TODO Error
    print("Error: Codigo mal formado")
    exit()

ancho_elegido = int(verify.group('ancho'))

color_elegido = util.parseColor(verify.group('bg_color'))

codigo = verify.group('code')

codigo = re.sub(r"(?! ){", " {", codigo) # Agrega un espacio antes de {
codigo = re.sub(r"{(?! )", "{ ", codigo) # Agrega un espacio despues de {
codigo = re.sub(r"(?! )}", " }", codigo) # Agrega un espacio antes de }
codigo = re.sub(r"}(?! )", "} " , codigo) # Agrega un espacio despues de }

codigo = re.sub(r"(\n)", " {} ".format(newline_placeholder), codigo) # Agrega un placeholder para los saltos de linea
codigo = re.sub(r"(\t)+", r" ", codigo) # Elimina tabs
codigo = re.sub(r"( )+", r" ", codigo) # Elimina espacios repetidos

if DEBUG:
    print("Ancho:")
    print(ancho_elegido)
    print("Color:")
    print(color_elegido)
    print("Codigo:")
    print(codigo)
    print()

errors, bytecode = util.parseCode(set(), codigo)
print(errors)
if errors != set():
    print("Ocurrio un error")
    exit()
if DEBUG:
    print("Bytecode:")
    print(bytecode)
    def printBytecode(bytecode, ident=0):
        for i in bytecode:
            if i[0][0] < 10:
                print("0", end="")
            print(i[0][0], end=' ')

            if i[0][1] < 10:
                print("0", end="")
            print(i[0][1], end=' ')
            if i[1] == "R":
                print("\t"*ident, end="")
                print(i[1], i[2][0])
                printBytecode(i[2][1], ident+1)
            else:
                print("\t"*ident, end="")
                print(i[1], i[2])
    printBytecode(bytecode)

iMatrix = [[color_elegido for _ in range(ancho_elegido)] for _ in range(ancho_elegido)]
pos = (0,0)
dir = 0

state = (iMatrix, pos, dir)

state = util.run(bytecode, state, codigo)

rMatrix = state[0]
createImage.MatrizAImagen(rMatrix)

