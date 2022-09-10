#!/usr/bin/env python3
import re
from functools import reduce
from typing import Callable, Optional, Literal
import numpy as np  # pip install numpy
from PIL import Image  # pip install Pllow

ColorType = tuple[int, int, int]
StateType = tuple[list[list[ColorType]], tuple[int, int], int, str]

InstructionType = Callable[[StateType], StateType]

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
    img = img.resize((N * factor, N * factor), Image.Resampling.BOX)
    img.save(filename)




# Colores
colores_predefinidos = {
    "Rojo": (255, 0, 0),
    "Verde": (0, 255, 0),
    "Azul": (0, 0, 255),
    "Negro": (0, 0, 0),
    "Blanco": (255, 255, 255)
}



ancho_pattern = r"^Ancho (?P<ancho>\d+)"  # Captura el Ancho dado
n0_number_pattern = r"[1-9](?:0|[1-9])*"
number_pattern = fr"0+|{n0_number_pattern}"

es_un_color_predefinido_pattern = "|".join(colores_predefinidos.keys())
rgb_pattern = r"RGB *\( *({np}) *, *({np}) *, *({np}) *\)".format(
    np=number_pattern)
color_pattern = fr"({es_un_color_predefinido_pattern}|{rgb_pattern})"

# Background color
bg_color_pattern = fr"Color de fondo (?P<bg_color>{color_pattern})"

# Declaraciones
avanzar_statement_pattern = fr"Avanzar(?P<avanzar_nveces> {n0_number_pattern})?"
avanzar_statement_pattern = f"(?P<avanzar_sttmt>{avanzar_statement_pattern})"
girar_statement_pattern = r"(?P<izq>Izquierda)|(?P<der>Derecha)"
girar_statement_pattern = f"(?P<girar_sttmt>{girar_statement_pattern})"
pintar_statement_pattern = fr"Pintar (?P<pintar_color>{color_pattern})"
pintar_statement_pattern = f"(?P<pintar_sttmt>{pintar_statement_pattern})"
repetir_statement_pattern = fr"Repetir (?P<repetir_nveces>{n0_number_pattern}) veces " "{"
repetir_statement_pattern = f"(?P<repetir_sttmt>{repetir_statement_pattern})"

statements_pattern = "|".join([
    avanzar_statement_pattern, girar_statement_pattern,
    pintar_statement_pattern, repetir_statement_pattern
])

newline_placeholder = r"{newline}"
alfabeto = r"[a-zA-Z0-9{},() \n\t]"




def parseColor(color: str) -> Optional[ColorType]:
    '''
    Parsea un color en formato RGB(d, d, d) o un color literal y devuelve una tupla de enteros.
    El color literal puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'

        Parametros:
            color (str): string del color, puede ser un literal o un RGB con su tupla.

        Retorno:
            Optional[ColorType]: Devuelve una tupla de enteros en caso de ser un color valido, en otro caso devuelve None

    '''
    if re.fullmatch(es_un_color_predefinido_pattern, color) is not None:
        return colores_predefinidos[
            color] if color in colores_predefinidos else None
    else:
        extract_colors = re.fullmatch(rgb_pattern, color)

        if extract_colors is None:
            return None

        RGB: ColorType = tuple(map(int, extract_colors.groups()))
        return RGB if all(map(lambda x: 0 <= x <= 255, RGB)) else None


def sttmnt_advance(n: int, ln: int) -> Callable[[StateType], StateType]:
    '''
    Retorna una funcion que modifica un estado avanzando n pasos en la direccion actual.

    Parametros:
        n (int): Cantidad de pasos a avanzar
        ln (int): Linea en la que se encuentra la declaracion

    Retorno:
        Callable[[StateType], StateType]: Funcion que modifica un estado avanzando n pasos en la direccion actual.
    '''

    def ret(state: StateType) -> StateType:
        '''
        Avanza n pasos en la direccion actual, si se sale de la matriz, lo muestra por pantalla y termina el programa.

        Parametros:
            state (StateType): Tupla con la matriz, la posicion, la direccion y el codigo.

        Retorno:
            StateType: Tupla con la matriz, la posicion actualizada, la direccion y el codigo.
        '''
        dirList = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        pos: tuple[int, int] = state[1]
        dir: tuple[int, int] = dirList[state[2]]

        pos = (pos[0] + dir[0] * n, pos[1] + dir[1] * n)

        matrix_len = len(state[0])
        if max(pos) >= matrix_len or min(pos) < 0:
            print(ln, state[3].splitlines()[ln - 1])
            exit(1)

        return (state[0], pos, state[2], state[3])

    return ret


def sttmnt_rotate(n: Literal[1, -1]) -> Callable[[StateType], StateType]:
    '''
    Retorna una funcion que modifica un estado rotando a la derecha (1) o a la izquierda (-1).

    Parametros:
        n (int): 1 para derecha, -1 para izquierda.

    Retorno:
        Callable[[StateType], StateType]: Funcion que modifica un estado rotando a la derecha (1) o a la izquierda (-1).
    '''

    def ret(state: StateType) -> StateType:
        '''
        Rota a la derecha (1) o a la izquierda (-1).

        Parametros:
            state (StateType): Tupla con la matriz, la posicion, la direccion y el codigo.

        Retorno:
            StateType: Tupla con la matriz, la posicion, la direccion actualizada y el codigo.
        '''
        dir = state[2]

        dir += n  # 1 o -1 dependiendo de si era Izquierda o derecha (se mueve en la
        # lista de direcciones)

        dir %= 4
        return (state[0], state[1], dir, state[3])

    return ret


def sttmnt_paint(color: ColorType) -> Callable[[StateType], StateType]:
    '''
    Retorna una funcion que modifica un estado pintando el bloque actual con el color dado.

    Parametros:
        color (ColorType): Color a pintar.

    Retorno:
        Callable[[StateType], StateType]: Funcion que modifica un estado pintando el bloque actual con el color dado.
    '''

    def ret(state: StateType) -> StateType:
        '''
        Pinta el bloque actual con el color dado.

        Parametros:
            state (StateType): Tupla con la matriz, la posicion, la direccion y el codigo.

        Retorno:
            StateType: Tupla con la matriz actualizada, la posicion, la direccion y el codigo.
        '''
        iMatrix = state[0]  # Matriz
        x, y = state[1]  # Posicion
        iMatrix[x][y] = color
        return (iMatrix, state[1], state[2], state[3])

    return ret


def sttmnt_repeat(n: int, bcode: list[InstructionType]) -> Callable[[StateType], StateType]:
    '''
    Retorna una funcion que modifica un estado repitiendo n veces el codigo dado.

    Parametros:
        n (int): Cantidad de veces a repetir el codigo.
        bcode (list[InstructionType]): Codigo a repetir.

    Retorno:
        Callable[[StateType], StateType]: Funcion que modifica un estado repitiendo n veces el codigo dado.
    '''

    def ret(state: StateType) -> StateType:
        '''
        Repite n veces el codigo dado.

        Parametros:
            state (StateType): Tupla con la matriz, la posicion, la direccion y el codigo.

        Retorno:
            StateType: Estado nuevo luego de aplicar n veces las transformaciones.
        '''
        for _ in range(n):
            state = reduce(lambda s, f: f(s), bcode, state)
        return state

    return ret


def parseCode(errores: set[int],
              code: str,
              n: int = 0,
              iden: int = 0,
              ln: int = 4) -> list[InstructionType]:
    '''
    Recibe un string con el codigo a ejecutar y ejecuta la primera sentencia. Luego ejecuta el resto de forma recursiva.
    Devuelve una lista ejecutable

    Parametros:
        errores (set[int]): Set de lineas que contienen errores.
        code (str): Codigo al que se le realizara el parsing.
        n (int): numero de instrucciones que se han parseado hasta el momento.
        iden (int): identacion actual.
        ln (int): linea actual.

    Retorno:
        list[InstructionType]: Lista de funciones que realizan una transformacion a un estado.
    '''

    I_fn: Callable[[StateType], StateType] = lambda x: x  # Funcion identidad

    code = re.sub(r"^ ", "", code)  # Elimina el espacio al inicio

    # Si solo quedan espacios (caso base)
    if re.fullmatch(r" *", code) is not None:
        return []

    # Si se encuentra un salto de linea simplemente se continua con la
    # siguiente declaracion
    if re.match(newline_placeholder, code) is not None:
        longitud = len(newline_placeholder) + 1
        return parseCode(errores, code[longitud:], n, iden, ln + 1)

    # Si encuntra un '{' sin antes haber coincidido con la declaracion
    # 'Repetir' significa que es un error, pero se agrega una identacion para
    # que luego coincida con el '}' en caso de haber
    if re.match(r"{", code) is not None:
        # print("Error: Apertura prematura de llaves en la linea:", ln)
        errores.add(ln)
        return parseCode(errores, code[2:], n, iden + 1, ln)

    if re.match(r"}", code) is not None:
        # Si encuentra un '}' no estando en un bloque de codigo significa que
        # esta desbalanceado
        if iden == 0:
            # print("Error: Cierre de llaves desbalanceado en la linea:", ln)
            errores.add(ln)
            return parseCode(errores, code[2:], n, iden, ln)

        # Si encuentra un '}' y esta en un bloque de codigo, simplemente
        # retorna (caso base)
        return []


    match = re.fullmatch(f"(?P<head>{statements_pattern})(?P<tail>.*)", code)
    if match is None:
        # print("Error: Sentencia no reconocida en la linea:", ln)
        errores.add(ln)
        return parseCode(errores, " ".join(code.split(" ")[1:]), n, iden, ln)

    h = match.group('head')
    t = match.group('tail')

    # Repetir <n> veces {}
    if match.group('repetir_sttmt') is not None:
        result = parseCode(errores, t, n + 1, iden + 1, ln)
        I_fn = sttmnt_repeat(int(match.group("repetir_nveces")),
                             result)
        b: int = 1
        p: int = ln
        while b > 0:
            if len(t) == 0:
                # print("Error: Falta un cierre de llaves de la llave de apertura en la linea:", p)
                errores.add(p)
                return [lambda x: x]

            if re.match(newline_placeholder, t) is not None:
                ln += 1
                t = t[len(newline_placeholder):]

            c = t[0]
            if c == "}":
                b -= 1
            elif c == "{":
                b += 1
            t = t[1:]

    # Pintar <color>
    elif match.group('pintar_sttmt') is not None:
        f_chosen_color: Optional[ColorType] = parseColor(
            match.group("pintar_color"))

        chosen_color: ColorType = (0, 0, 0)
        if f_chosen_color is None:
            # print("Error: Color no reconocido en la linea:", ln)
            errores.add(ln)
        else:
            chosen_color = f_chosen_color

        I_fn = sttmnt_paint(chosen_color)

    # Rotar Izquierda|Derecha
    elif match.group('girar_sttmt') is not None:
        if match.group('izq') is not None:
            I_fn = sttmnt_rotate(-1)
        elif match.group('der') is not None:
            I_fn = sttmnt_rotate(1)

    # Avanzar <n>
    elif match.group('avanzar_sttmt') is not None:
        m: Optional[str] = match.group('avanzar_nveces')
        nveces: int = 1
        if m is not None:
            nveces = int(m)
        I_fn = sttmnt_advance(nveces, ln)

    res: list[InstructionType] = parseCode(errores, t, n + 1, iden, ln)

    I: list[InstructionType] = [I_fn]

    return I + res



if __name__ == "__main__":

    with open("codigo.txt") as f:
        txt: str = f.read()
    codigo = txt


    errores: set[int] = set()
    linea_actual = 1


    ancho_elegido: int = 0
    color_elegido: ColorType = (0, 0, 0)



    ancho_res = re.match(ancho_pattern, codigo)
    if ancho_res is None:
        # print("Error: Sintaxis incorrecta en la declaracion del ancho")
        errores.add(1)
    else:
        ancho_elegido = int(ancho_res.group("ancho"))
    codigo = "\n".join(codigo.splitlines()[1:])
    linea_actual += 1

    bg_res = re.match(bg_color_pattern, codigo)
    if bg_res is None:
        # print("Error: Sintaxis incorrecta en la declaracion del color de fondo")
        errores.add(2)
    else:
        f_color_elegido = parseColor(bg_res.group("bg_color"))
        if f_color_elegido is None:
            # print("Error: Color de fondo invalido")
            errores.add(2)
        else:
            color_elegido = f_color_elegido
    codigo = "\n".join(codigo.splitlines()[1:])
    linea_actual += 1

    if re.match(r"\n", codigo) is None:
        # print("Error: Falta una linea en blanco despues del color de fondo")
        errores.add(3)
    else:
        codigo = "\n".join(codigo.splitlines()[1:])
        linea_actual += 1



    # Agrega espacios antes y despues de los corchetes
    codigo = re.sub(r"{", " { ", codigo)
    codigo = re.sub(r"}", " } ", codigo)

    # Agrega un placeholder para los saltos de linea
    codigo = re.sub(r"(\n)", f" {newline_placeholder} ", codigo)
    codigo = re.sub(r"(\t)+", r" ", codigo)  # Elimina tabs
    codigo = re.sub(r"( )+", r" ", codigo)  # Elimina espacios repetidos



    bytecode = parseCode(errores, codigo, ln=linea_actual)


    with open("errores.txt", "w") as f:
        if len(errores) > 0:
            for error in sorted(errores):
                f.write(f"{error} {txt.splitlines()[error - 1]}\n")
            exit()
        f.write("No hay errores!\n")


    initial_state: StateType = (
        [[color_elegido for _ in range(ancho_elegido)]
         for _ in range(ancho_elegido)],  # Matriz inicial
        (0, 0),  # Posicion inicial
        0,  # Direccion [Derecha, Abajo, Izquierda, Arriba]
        txt  # Codigo original para mostrar errores en tiempo de ejecucion
    )

    final_state: StateType = reduce(lambda s, f: f(s), bytecode,
                                         initial_state)

    rMatrix: list[list[ColorType]] = final_state[0]
    print(rMatrix)

    MatrizAImagen(rMatrix)
