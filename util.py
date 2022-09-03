import re

from patrones import \
    number_pattern, \
    statements_pattern, \
    repetir_statement_pattern, \
    pintar_statement_pattern, \
    girar_statement_pattern, \
    avanzar_statement_pattern, \
    newline_placeholder

from typing import Literal

ColorType = tuple[int, int, int]

ArgsType = tuple[int, list['InstructionType']] | int | ColorType | None
InstructionType = tuple[tuple[int, int], Literal["E", "R", "A", "G", "P"], ArgsType]

StateType = tuple[list[list[ColorType]], tuple[int, int], int]

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


def parseCode(errores: set[int], code: str, n: int = 0, iden: int = 0, ln: int = 4) -> tuple[set[int], list[InstructionType]]:
    '''
    Recibe un string con el codigo a ejecutar y ejecuta la primera sentencia. Luego ejecuta el resto de forma recursiva.
    Devuelve una lista ejecutable
    '''

    I_data: tuple[int, int] = (n, ln)
    I_type: str = "E"
    I_args: ArgsType = None


    code = re.sub(r"^ ", "", code) # Elimina el espacio al inicio

    if re.fullmatch(r" *", code) != None:
        return set(), []
    
    if re.match(r"}", code) != None:
        if iden == 0:
            return {ln}, [ ((n, ln), "E", None) ]
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
        I_type = "R"
        err, result = parseCode(errores, t, n+1, iden+1, ln)
        errores.update(err)
        I_args = (int(repetir_result.group("repetir_nveces")), result)
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
        I_type = "P"
        I_args = chosen_color

    # Rotar Izquierda|Derecha
    elif re.match(girar_statement_pattern, h) != None:
        I_type = "G"
        if re.match(r"Izquierda", h) != None:
            I_args = -1
        elif re.match(r"Derecha", h) != None:
            I_args = 1

    # Avanzar <n>
    elif re.match(avanzar_statement_pattern, h) != None:
        I_type = "A"

        m = re.match(r"Avanzar(?P<avanzar_nveces> [1-9][0-9]*)", h)
        if m == None:
            I_args = 1
        else:
            I_args = int(m.group("avanzar_nveces"))

    else:
        # TODO: Error
        pass

    res: tuple[set[int], list[InstructionType]] = parseCode(errores, t, n+1, iden, ln)
    errores.update(res[0])
    I: list[InstructionType] = [(I_data, I_type, I_args)]
    return errores, I + res[1]



def sttmnt_advance(state, n):
    dirList = [(0,1), (1,0), (0,-1), (-1,0)]
    pos = state[1]
    dir = state[2]
    for _ in range(n):
        pos = (pos[0]+dirList[dir][0], pos[1]+dirList[dir][1])
    return (state[0], pos, state[2])
    
def sttmnt_rotate(state, n):
    dir = state[2]
    dir += n
    dir %= 4
    return (state[0], state[1], dir)

def sttmnt_paint(state, color):
    iMatrix = state[0]
    pos = state[1]
    iMatrix[pos[0]][pos[1]] = color
    return (iMatrix, state[1], state[2])

def sttmnt_repeat(state, n, bcode):
    for _ in range(int(n)):
        state = run(bcode, state)
    return state


def run(bcode: list[InstructionType], state: StateType, codigo: str = "") -> StateType:
    '''
    Ejecuta el codigo en el estado actual
    '''
    if bcode == []:
        return state

    h:      InstructionType  = bcode[0]
    t: list[InstructionType] = bcode[1:]

    if h[1] == "A":
        state2 = sttmnt_advance(state, h[2])
    elif h[1] == "G":
        state2 = sttmnt_rotate(state, h[2])
    elif h[1] == "P":
        state2 = sttmnt_paint(state, h[2])
    elif h[1] == "R":
        state2 = sttmnt_repeat(state, h[2][0], h[2][1])
    else:
        print("Error: Instruccion no reconocida")
        exit()

    return run(t, state2, codigo)

