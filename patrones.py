# Extract width
ancho_pattern = r"^Ancho (?P<ancho>\d+)" # Captura el Ancho dado
n0_number_pattern = r"[1-9](?:0|[1-9])*"
number_pattern = r"0|"+n0_number_pattern

# Colores
colores_predefinidos = {
    "Rojo"  : (255,   0,   0),
    "Verde" : (  0, 255,   0),
    "Azul"  : (  0,   0, 255),
    "Negro" : (  0,   0,   0),
    "Blanco": (255, 255, 255)
}
## Patron para detectar si es un color predefinido
es_un_color_predefinido_pattern = "|".join(colores_predefinidos.keys())
rgb_pattern = r"RGB *\( *({np}) *, *({np}) *, *({np}) *\)".format(np = number_pattern)
color_pattern = '|'.join([es_un_color_predefinido_pattern, rgb_pattern])

# Background color
bg_color_pattern = r"Color de fondo (?P<bg_color>{})".format(color_pattern)

# declaraciones
avanzar_statement_pattern = r"Avanzar(?P<avanzar_nveces> {n0np})?".format(n0np = n0_number_pattern) # Captura el numero de veces que se avanza
girar_statement_pattern = r"Izquierda|Derecha"
pintar_statement_pattern = r"Pintar (?P<pintar_color>{})".format(color_pattern)
repetir_statement_pattern = r"Repetir (?P<repetir_nveces>[1-9][0-9]*) veces {"

statements_pattern = "|".join([
    avanzar_statement_pattern,
    girar_statement_pattern,
    pintar_statement_pattern,
    repetir_statement_pattern
])


newline_placeholder = r"{newline}"
alfabeto = r"[a-zA-Z0-9{},() \n\t]"
