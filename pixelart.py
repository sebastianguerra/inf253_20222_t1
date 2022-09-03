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
verify: re.Match[str]|None = re.match(''.join([ ancho_pattern, r" *\n", bg_color_pattern, r" *\n *\n(?P<code>[a-zA-Z0-9{}(), \n\t]*$)" ]), txt)
if verify == None: # El codigo no cumple con la estructura necesaria
    pass # TODO: Encontrar el error y mostrarlo
    print("Error: Codigo mal formado")
    exit()

ancho_elegido: int            =             int(verify.group('ancho'))
color_elegido: util.ColorType = util.parseColor(verify.group('bg_color'))
codigo       : str            =                 verify.group('code')


codigo = re.sub(r"(?! ){", " {", codigo) # Agrega un espacio antes de {
codigo = re.sub(r"{(?! )", "{ ", codigo) # Agrega un espacio despues de {
codigo = re.sub(r"(?! )}", " }", codigo) # Agrega un espacio antes de }
codigo = re.sub(r"}(?! )", "} " , codigo) # Agrega un espacio despues de }

codigo = re.sub(r"(\n)", " {} ".format(newline_placeholder), codigo) # Agrega un placeholder para los saltos de linea
codigo = re.sub(r"(\t)+", r" ", codigo) # Elimina tabs
codigo = re.sub(r"( )+", r" ", codigo) # Elimina espacios repetidos


res: tuple[ set[int], list[util.InstructionType] ] = util.parseCode(set(), codigo)
errores, bytecode = res[0], res[1]

if len(errores) > 0:
    # TODO: Mover errores a 'errores.txt'
    for error in errores:
        print(error, txt.splitlines()[error-1])
    exit()
else:
    print("No hay errores!") # > errores.txt

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

iMatrix: list[list[util.ColorType]] = [[color_elegido for _ in range(ancho_elegido)] for _ in range(ancho_elegido)]
pos: tuple[int, int] = (0,0)
dir: int = 0

initial_state: util.StateType = (iMatrix, pos, dir)

final_state: util.StateType = util.run(bytecode, initial_state, codigo)

rMatrix: list[list[util.ColorType]] = final_state[0]
createImage.MatrizAImagen(rMatrix)

