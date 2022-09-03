import re

from patrones import \
    number_pattern, \
    statements_pattern, \
    repetir_statement_pattern, \
    pintar_statement_pattern, \
    girar_statement_pattern, \
    avanzar_statement_pattern, \
    newline_placeholder


def parseColor(color):
    '''
    Parsea un color en formato RGB(d, d, d) y devuelve una tupla de enteros.
    Tambien puede ser 'Rojo', 'Verde', 'Azul', 'Negro' o 'Blanco'
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

def parseCode(txt, code, n=0, iden=0, ln=4):
    '''
    Recibe un string con el codigo a ejecutar y ejecuta la primera sentencia. Luego ejecuta el resto de forma recursiva.
    Devuelve una lista ejecutable
    '''
    I = [(n, ln), "", []]
    code = re.sub(r"^ ", "", code)


    if re.match(r"^ *$", code) != None:
        return set(), []
    
    if re.match(r"}", code) != None:
        if iden == 0:
            return {ln}, [(n, ln), "E", []]
        return set(), []

    if re.match(newline_placeholder, code)!= None:
        longitud = len(newline_placeholder) + 1
        return parseCode(txt, code[longitud:], n, iden, ln+1)

    match = re.match(r"(?P<head>{})(?P<tail>[a-zA-Z0-9{},() \n\t]*)".format(statements_pattern, "{}"), code)
    if match == None:
        print("No coincide: \"" + code + "\"")
        return set(), []
    
    h = match.group('head')
    t = match.group('tail')
    t = re.sub(r"^ ", "", t)

    
    # Repetir <n> veces {}
    if re.match(repetir_statement_pattern, h) != None:
        I[1] = "R"
        cantidad = re.match(repetir_statement_pattern, h)
        I[1] = "R"
        err, result = parseCode(txt, t, n+1, iden+1, ln)
        txt.update(err)
        I[2] = (cantidad.group("repetir_nveces") , result)
        m = 1
        while m > 0:
            if re.match(newline_placeholder, t) != None:
                ln += 1
            # print(t)
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
        chosen_color = parseColor(color)
        I[1] = "P"
        I[2] = chosen_color

    # Rotar Izquierda|Derecha
    elif re.match(girar_statement_pattern, h) != None:
        I[1] = "G"
        if re.match(r"Izquierda", h) != None:
            I[2] = -1
        elif re.match(r"Derecha", h) != None:
            I[2] = 1

    # Avanzar <n>
    elif re.match(avanzar_statement_pattern, h) != None:
        I[1] = "A"

        m = re.match(r"Avanzar(?P<avanzar_nveces> [1-9][0-9]*)", h)
        if m == None:
            I[2] = 1
        else:
            I[2] = int(m.group("avanzar_nveces"))

    else:
        # TODO: Error
        pass

    err, res = parseCode(txt, t, n+1, iden, ln)
    txt.update(err)
    return txt, [I] + res


def sttmnt_advance(state, n):
    dirList = [(0,1), (1,0), (0,-1), (-1,0)]
    pos = state[1]
    dir = state[2]
    for i in range(n):
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


def run(bcode, state, codigo=""):
    '''
    Ejecuta el codigo en el estado actual
    '''
    if bcode == []:
        return state
    h = bcode[0]
    t = bcode[1:]
    if h[1] == "A":
        state2 = sttmnt_advance(state, h[2])
    elif h[1] == "G":
        state2 = sttmnt_rotate(state, h[2])
    elif h[1] == "P":
        state2 = sttmnt_paint(state, h[2])
    elif h[1] == "R":
        state2 = sttmnt_repeat(state, h[2][0], h[2][1])

    return run(t, state2, codigo)

