import re

from patrones import \
    number_pattern, \
    statements_pattern, \
    repetir_statement_pattern, \
    pintar_statement_pattern, \
    girar_statement_pattern, \
    avanzar_statement_pattern, \
    newline_placeholder

from typing import Callable

ColorType = tuple[int, int, int]
StateType = tuple[list[list[ColorType]], tuple[int, int], int]

InstructionType = tuple[tuple[int, int], Callable[[StateType], StateType]|None]


def parseColor(color: str) -> ColorType:
    '''
    Parsea un color en formato RGB(d, d, d) o un color literal y devuelve una tupla de enteros.
    El color literal puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'
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
        # TODO: usar re.match
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
            pass # TODO: Error
            print("Error: Nombre de color equivocado")
            exit()



def sttmnt_advance(n: int) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        dirList = [(0,1), (1,0), (0,-1), (-1,0)]
        pos = state[1]
        dir = state[2]
        for _ in range(n):
            pos = (pos[0]+dirList[dir][0], pos[1]+dirList[dir][1])
        return (state[0], pos, state[2])
    return ret
    
def sttmnt_rotate(n: int) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        dir = state[2]
        dir += n
        dir %= 4
        return (state[0], state[1], dir)
    return ret

def sttmnt_paint(color: ColorType) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        iMatrix = state[0]
        pos = state[1]
        iMatrix[pos[0]][pos[1]] = color
        return (iMatrix, state[1], state[2])
    return ret

def sttmnt_repeat(n: int, bcode: list[InstructionType]) -> Callable[[StateType], StateType]:
    def ret(state: StateType) -> StateType:
        for _ in range(int(n)):
            state = run(bcode, state)
        return state
    return ret


def parseCode(errores: set[int], code: str, n: int = 0, iden: int = 0, ln: int = 4) -> tuple[set[int], list[InstructionType]]:
    '''
    Recibe un string con el codigo a ejecutar y ejecuta la primera sentencia. Luego ejecuta el resto de forma recursiva.
    Devuelve una lista ejecutable
    '''

    I_data: tuple[int, int] = (n, ln)
    I_fn: Callable[[StateType], StateType]|None = None


    code = re.sub(r"^ ", "", code) # Elimina el espacio al inicio

    if re.fullmatch(r" *", code) != None:
        return set(), []
    
    if re.match(r"}", code) != None:
        if iden == 0:
            return {ln}, [ ((n, ln), None) ]
        return set(), []

    if re.match(newline_placeholder, code)!= None:
        longitud = len(newline_placeholder) + 1
        return parseCode(errores, code[longitud:], n, iden, ln+1)

    match = re.fullmatch(r"(?P<head>{})(?P<tail>[a-zA-Z0-9{},() \n\t]*)".format(statements_pattern, "{}"), code)
    if match == None:
        print("No coincide: \"" + code + "\"") # TODO: manejar error
        return set(), [] # TODO: Seguir analizando el resto del codigo
    
    h = match.group('head')
    t = match.group('tail')

    
    # Repetir <n> veces {}
    repetir_result = re.match(repetir_statement_pattern, h)
    if repetir_result != None:
        err, result = parseCode(errores, t, n+1, iden+1, ln)
        errores.update(err)
        I_fn = sttmnt_repeat(int(repetir_result.group("repetir_nveces")), result)
        m = 1
        while m > 0:
            if re.match(newline_placeholder, t) != None:
                ln += 1
            c = t[0]
            if c == "}":
                m -= 1
                if m == -1:
                    print("Error: Cierre de bloque sin apertura")
                    pass # TODO: Error: Cierre de bloque sin apertura
            elif c == "{":
                m += 1
            t = t[1:]

    # Pintar <color>
    elif re.match(pintar_statement_pattern, h) != None:
        color = re.match(r"^Pintar (.*)$", h)
        if color == None:
            print("Error: Color no reconocido")
            exit()
            # TODO: Error
        color = color.groups()[0]
        chosen_color: ColorType = parseColor(color)
        I_fn = sttmnt_paint(chosen_color)

    # Rotar Izquierda|Derecha
    elif re.match(girar_statement_pattern, h) != None:
        dir: int = 0
        if re.match(r"Izquierda", h) != None:
            dir = -1
        elif re.match(r"Derecha", h) != None:
            dir = 1
        I_fn = sttmnt_rotate(dir)

    # Avanzar <n>
    elif re.match(avanzar_statement_pattern, h) != None:
        m = re.match(r"Avanzar(?P<avanzar_nveces> [1-9][0-9]*)", h)
        if m == None:
            n = 1
        else:
            n = int(m.group("avanzar_nveces"))
        I_fn = sttmnt_advance(n)

    else:
        # TODO: Error
        pass

    res: tuple[set[int], list[InstructionType]] = parseCode(errores, t, n+1, iden, ln)
    errores.update(res[0])
    I: list[InstructionType] = [(I_data, I_fn)]
    return errores, I + res[1]





def run(bcode: list[InstructionType], state: StateType, codigo: str = "") -> StateType:
    '''
    Ejecuta el codigo en el estado actual
    '''
    if bcode == []:
        return state

    h:      InstructionType  = bcode[0]
    t: list[InstructionType] = bcode[1:]

    if h[1] == None:
        exit()
    state2: StateType = h[1](state)

    return run(t, state2, codigo)
