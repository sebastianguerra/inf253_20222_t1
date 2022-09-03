#!/usr/bin/env python3
import re

import createImage
import util
from functools import reduce
from patrones import \
        ancho_pattern, \
        bg_color_pattern, \
        newline_placeholder


with open("codigo.txt") as f:
    txt: str = f.read()


# Verifica que el codigo tenga la estructura inicial correcta y extrae directamente los valores
verify: re.Match[str]|None = re.match(''.join([ ancho_pattern, r" *\n", bg_color_pattern, r" *\n *\n(?P<code>[a-zA-Z0-9{}(), \n\t]*$)" ]), txt)
if verify == None: # El codigo no cumple con la estructura necesaria
    pass # TODO: Encontrar el error y mostrarlo
    print("Error: Codigo mal formado")
    exit()


ancho_elegido: int            =             int(verify.group('ancho'))
color_elegido: util.ColorType = util.parseColor(verify.group('bg_color'))
codigo       : str            =                 verify.group('code')


# Agrega espacios antes y despues de los corchetes
codigo = re.sub(r"{", " { ", codigo)
codigo = re.sub(r"}", " } ", codigo)

codigo = re.sub(r"(\n)", " {} ".format(newline_placeholder), codigo) # Agrega un placeholder para los saltos de linea
codigo = re.sub(r"(\t)+", r" ", codigo) # Elimina tabs
codigo = re.sub(r"( )+", r" ", codigo) # Elimina espacios repetidos


res: tuple[ set[int], list[util.InstructionType] ] = util.parseCode(set(), codigo)
errores, bytecode = res[0], res[1]

if len(errores) > 0:
    # TODO: Mover errores a 'errores.txt'
    for error in errores:
        print(error, txt.splitlines()[error-1]) # > errores.txt
    exit()
print("No hay errores!") # > errores.txt


iMatrix: list[list[util.ColorType]] = [[color_elegido for _ in range(ancho_elegido)] for _ in range(ancho_elegido)]
pos: tuple[int, int] = (0,0)
dir: int = 0

initial_state: util.StateType = (iMatrix, pos, dir)


final_state: util.StateType = reduce(lambda x, y: y[1](x), bytecode, initial_state)

rMatrix: list[list[util.ColorType]] = final_state[0]
createImage.MatrizAImagen(rMatrix)

