#!/usr/bin/env python3
import re
import util
from functools import reduce
from typing import Optional

import createImage
from patrones import \
        ancho_pattern, \
        bg_color_pattern, \
        newline_placeholder, \
        alfabeto


with open("pixelart.png", "w") as f:
    f.write("a")

with open("codigo.txt") as f:
    txt: str = f.read()



errores: set[int] = set()

f_color_elegido: Optional[util.ColorType] = (0, 0, 0)
color_elegido: util.ColorType = (0, 0, 0)

ancho_elegido: int = 0


# Verifica que el codigo tenga la estructura inicial correcta y extrae directamente los valores
verify: Optional[re.Match[str]] = re.fullmatch(fr"{ancho_pattern} *\n{bg_color_pattern} *\n *\n(?P<code>{alfabeto}*$)" , txt)

if verify == None: # El codigo no cumple con la estructura necesaria
    ancho_res: Optional[re.Match[str]] = re.search(ancho_pattern, txt)
    if ancho_res == None:
        # print("Error: Sintaxis incorrecta en la declaracion del ancho")
        errores.add(1)
    else:
        ancho_elegido = int(ancho_res.group("ancho"))
    codigo = "\n".join(txt.splitlines()[1:])


    bg_res = re.search(bg_color_pattern, txt)
    if bg_res == None:
        # print("Error: Sintaxis incorrecta en la declaracion del color de fondo")
        errores.add(2)
    else:
        f_color_elegido = util.parseColor(bg_res.group("bg_color"))
        if f_color_elegido == None:
            # print("Error: Color de fondo invalido")
            errores.add(2)
        else:
            color_elegido = f_color_elegido

    codigo = "\n".join(codigo.splitlines()[2:])

else:
    ancho_elegido = int(verify.group('ancho'))

    f_color_elegido = util.parseColor(verify.group('bg_color'))
    if f_color_elegido == None:
        # print("Error: Color de fondo invalido")
        errores.add(2)
    else:
        color_elegido = f_color_elegido

    codigo: str = verify.group('code')






# Agrega espacios antes y despues de los corchetes
codigo = re.sub(r"{", " { ", codigo)
codigo = re.sub(r"}", " } ", codigo)

codigo = re.sub(r"(\n)", f" {newline_placeholder} ", codigo) # Agrega un placeholder para los saltos de linea
codigo = re.sub(r"(\t)+", r" ", codigo) # Elimina tabs
codigo = re.sub(r"( )+", r" ", codigo) # Elimina espacios repetidos





bytecode = util.parseCode(errores, codigo)





with open("errores.txt", "w") as f:
    if len(errores) > 0:
        for error in errores:
            f.write(f"{error} {txt.splitlines()[error - 1]}\n")
        exit()
    f.write("No hay errores!\n")







initial_state: util.StateType = (
    [[color_elegido for _ in range(ancho_elegido)] for _ in range(ancho_elegido)], # Matriz inicial
    (0,0), # Posicion inicial
    0,     # Direccion [Derecha, Abajo, Izquierda, Arriba]
    txt    # Codigo original para mostrar errores en tiempo de ejecucion
    )


final_state: util.StateType = reduce(lambda s, f: f(s), bytecode, initial_state)


rMatrix: list[list[util.ColorType]] = final_state[0]
print(rMatrix)

createImage.MatrizAImagen(rMatrix)
