import re
from functools import reduce

from patrones import \
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

from typing import Callable, Optional, Literal

ColorType = tuple[int, int, int]
StateType = tuple[list[list[ColorType]], tuple[int, int], int, str]

InstructionType = Callable[[StateType], StateType]


def parseColor(color: str) -> Optional[ColorType]:
    '''
    Parsea un color en formato RGB(d, d, d) o un color literal y devuelve una tupla de enteros.
    El color literal puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'

        Parametros:
            color (str): string del color, puede ser un literal o un RGB con su tupla.

        Retorno:
            Optional[ColorType]: Devuelve una tupla de enteros en caso de ser un color valido, en otro caso devuelve None

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
        dirList = [(0,1), (1,0), (0,-1), (-1,0)]
        pos: tuple[int, int] = state[1]
        dir: tuple[int, int] = dirList[state[2]]

        pos = (
            pos[0]+dir[0]*n,
            pos[1]+dir[1]*n
        )

        matrix_len = len(state[0])
        if max(pos) >= matrix_len or min(pos) < 0:
            print(ln, state[3].splitlines()[ln-1])
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
        dir += n # 1 o -1 dependiendo de si era Izquierda o derecha (se mueve en la lista de direcciones)
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
        iMatrix = state[0] # Matriz
        x, y = state[1]    # Posicion
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


    match = re.fullmatch(fr"(?P<head>{statements_pattern}) (?P<tail>{alfabeto}*)", code)
    if match == None: # No coincide con ninguna palabra del lenguaje
        errores.add(ln)

        # Se continua buscando la proxima sentencia para encontrar mas errores
        res = parseCode(errores, " ".join(code.split(" ")[1:]), n, iden, ln)
        errores.update(res[0])
        
        return errores, res[1]

    
    h = match.group('head')
    t = match.group('tail')


    repetir_resultado = re.match(repetir_statement_pattern, h)
    pintar_resultado  = re.match(pintar_statement_pattern , h)
    girar_resultado   = re.match(girar_statement_pattern  , h)
    avanzar_resultado = re.match(avanzar_statement_pattern, h)


    # Repetir <n> veces {}
    if repetir_resultado != None:
        err, result = parseCode(errores, t, n+1, iden+1, ln)
        errores.update(err)
        I_fn = sttmnt_repeat(int(repetir_resultado.group("repetir_nveces")), result)
        b: int = 1
        p: int = ln
        while b > 0:
            if len(t) == 0:
                errores.add(p)
                return errores, [ lambda x: x ]

            if re.match(newline_placeholder, t) != None:
                ln += 1
                t = t[len(newline_placeholder):]

            c = t[0]
            if c == "}":
                b -= 1
            elif c == "{":
                b += 1
            t = t[1:]

    # Pintar <color>
    elif pintar_resultado != None:
        f_chosen_color: Optional[ColorType] = parseColor(pintar_resultado.group("pintar_color"))

        chosen_color: ColorType = (0, 0, 0)
        if f_chosen_color == None:
            errores.add(ln)
        else:
            chosen_color = f_chosen_color

        I_fn = sttmnt_paint(chosen_color)

    # Rotar Izquierda|Derecha
    elif girar_resultado != None:
        if girar_resultado.group('izq') != None:
            I_fn = sttmnt_rotate(-1)
        elif girar_resultado.group('der') != None:
            I_fn = sttmnt_rotate(1)

    # Avanzar <n>
    elif avanzar_resultado != None:
        m: Optional[str] = avanzar_resultado.group('avanzar_nveces')
        nveces: int = 1
        if m != None:
            nveces = int(m)
        I_fn = sttmnt_advance(nveces, ln)


    res: tuple[set[int], list[InstructionType]] = parseCode(errores, t, n+1, iden, ln)

    errores.update(res[0])
    I: list[InstructionType] = [I_fn]

    return errores, I + res[1]

