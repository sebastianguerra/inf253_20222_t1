import re

from functools import reduce
from patrones import \
    number_pattern, \
    statements_pattern, \
    repetir_statement_pattern, \
    pintar_statement_pattern, \
    girar_statement_pattern, \
    avanzar_statement_pattern, \
    newline_placeholder, \
    colores_predefinidos, \
    es_un_color_predefinido_pattern, \
    rgb_pattern, \
    alfabeto

from typing import Callable, Optional

ColorType = tuple[int, int, int]
StateType = tuple[list[list[ColorType]], tuple[int, int], int, str]

InstructionType = Callable[[StateType], StateType]


def parseColor(color: str) -> Optional[ColorType]:
    '''
    Parsea un color en formato RGB(d, d, d) o un color literal y devuelve una tupla de enteros.
    El color literal puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'
        Parametros:
                color (str): Color.
    '''
    if re.fullmatch(es_un_color_predefinido_pattern, color) != None:
        return colores_predefinidos[color] if color in colores_predefinidos else None
    else:
        extract_colors = re.fullmatch(rgb_pattern, color)
        if extract_colors == None:
            return None
        RGB: ColorType = tuple(map(int, extract_colors.groups()))
        return RGB if all(map(lambda x: 0 <= x <= 255, RGB)) else None


def sttmnt_advance(n: int, ln: int) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        dirList = [(0,1), (1,0), (0,-1), (-1,0)]
        pos = state[1]
        dir = state[2]
        for _ in range(n):
            pos = (pos[0]+dirList[dir][0], pos[1]+dirList[dir][1])

        matrix_len = len(state[0])
        if pos[0] < 0 or pos[0] >= matrix_len or pos[1] < 0 or pos[1] >= matrix_len:
            print(ln, state[3].splitlines()[ln-1])
            exit(1)

        return (state[0], pos, state[2], state[3])
    return ret
    
def sttmnt_rotate(n: int) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        dir = state[2]
        dir += n
        dir %= 4
        return (state[0], state[1], dir, state[3])
    return ret

def sttmnt_paint(color: ColorType) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        iMatrix = state[0]
        pos = state[1]
        iMatrix[pos[0]][pos[1]] = color
        return (iMatrix, state[1], state[2], state[3])
    return ret

def sttmnt_repeat(n: int, bcode: list[InstructionType]) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        for _ in range(int(n)):
            state = reduce(lambda x, y: y(x), bcode, state)
        return state
    return ret


def parseCode(errores: set[int], code: str, n: int = 0, iden: int = 0, ln: int = 4) -> tuple[set[int], list[InstructionType]]:
    '''
    Recibe un string con el codigo a ejecutar y ejecuta la primera sentencia. Luego ejecuta el resto de forma recursiva.
    Devuelve una lista ejecutable
    '''

    I_fn: Callable[[StateType], StateType] = lambda x: x # Funcion identidad


    code = re.sub(r"^ ", "", code) # Elimina el espacio al inicio


    # Si solo quedan espacios (caso base)
    if re.fullmatch(r" *", code) != None:
        return errores, []
    

    # Si se encuentra un salto de linea simplemente se continua con la 
    # siguiente declaracion
    if re.match(newline_placeholder, code) != None:
        longitud = len(newline_placeholder) + 1
        return parseCode(errores, code[longitud:], n, iden, ln+1)


    # Si encuntra un '{' sin antes haber coincidido con la declaracion 
    # 'Repetir' significa que es un error, pero se agrega una identacion para 
    # que luego coincida con el '}' en caso de haber
    if re.match(r"{", code) != None:
        errores.add(ln)
        return parseCode(errores, code[2:], n, iden+1, ln)

    if re.match(r"}", code) != None:
        # Si encuentra un '}' no estando en un bloque de codigo significa que 
        # esta desbalanceado
        if iden == 0:
            errores.add(ln)
            return errores, [ lambda x: x ]

        # Si encuentra un '}' y esta en un bloque de codigo, simplemente retorna (caso base)
        return errores, []


    match = re.fullmatch(r"(?P<head>{}) (?P<tail>{}*)".format(statements_pattern, alfabeto), code)
    if match == None: # No coincide con ninguna palabra del lenguaje
        errores.add(ln)

        # Se continua buscando la proxima sentencia para encontrar mas errores
        res = parseCode(errores, " ".join(code.split(" ")[1:]), n, iden, ln)
        errores.update(res[0])
        
        return errores, res[1]

    
    h = match.group('head')
    t = match.group('tail')


    repetir_resultado = re.match(repetir_statement_pattern, h)
    pintar_resultado = re.match(pintar_statement_pattern, h)
    girar_resultado = re.match(girar_statement_pattern, h)
    avanzar_resultado = re.match(avanzar_statement_pattern, h)


    # Repetir <n> veces {}
    if repetir_resultado != None:
        err, result = parseCode(errores, t, n+1, iden+1, ln)
        errores.update(err)
        I_fn = sttmnt_repeat(int(repetir_resultado.group("repetir_nveces")), result)
        b: int = 1
        while b > 0:
            if re.match(newline_placeholder, t) != None:
                ln += 1
            c = t[0]
            if c == "}":
                b -= 1
            elif c == "{":
                b += 1
            t = t[1:]

    # Pintar <color>
    elif pintar_resultado != None:
        color: str = pintar_resultado.group('pintar_color')

        f_chosen_color: Optional[ColorType] = parseColor(color)

        chosen_color: ColorType = (0, 0, 0)
        if f_chosen_color == None:
            errores.add(ln)
        else:
            chosen_color = f_chosen_color

        I_fn = sttmnt_paint(chosen_color)

    # Rotar Izquierda|Derecha
    elif girar_resultado != None:
        dir: int = 0
        if girar_resultado.group('izq') != None:
            dir = -1
        elif girar_resultado.group('der') != None:
            dir = 1
        I_fn = sttmnt_rotate(dir)

    # Avanzar <n>
    elif avanzar_resultado != None:
        m: Optional[str] = avanzar_resultado.group('avanzar_nveces')
        n: int = 1
        if m != None:
            n = int(m)
        I_fn = sttmnt_advance(n, ln)


    res: tuple[set[int], list[InstructionType]] = parseCode(errores, t, n+1, iden, ln)

    errores.update(res[0])
    I: list[InstructionType] = [I_fn]

    return errores, I + res[1]

