# Extract width
ancho_pattern = r"^Ancho (?P<ancho>\d+)"  # Captura el Ancho dado
n0_number_pattern = r"[1-9](?:0|[1-9])*"
number_pattern = fr"0|{n0_number_pattern}"

# Colores
colores_predefinidos = {
    "Rojo": (255, 0, 0),
    "Verde": (0, 255, 0),
    "Azul": (0, 0, 255),
    "Negro": (0, 0, 0),
    "Blanco": (255, 255, 255)
}
es_un_color_predefinido_pattern = "|".join(colores_predefinidos.keys())
rgb_pattern = r"RGB *\( *({np}) *, *({np}) *, *({np}) *\)".format(
    np=number_pattern)
color_pattern = '|'.join([es_un_color_predefinido_pattern, rgb_pattern])

# Background color
bg_color_pattern = fr"Color de fondo (?P<bg_color>{color_pattern})"

# Declaraciones
# Captura el numero de veces que se avanza
avanzar_statement_pattern = fr"Avanzar(?P<avanzar_nveces> {n0_number_pattern})?"
girar_statement_pattern = r"(?P<izq>Izquierda)|(?P<der>Derecha)"
pintar_statement_pattern = fr"Pintar (?P<pintar_color>{color_pattern})"
repetir_statement_pattern = r"Repetir (?P<repetir_nveces>[1-9][0-9]*) veces {"
statements_pattern = "|".join([
    avanzar_statement_pattern, girar_statement_pattern,
    pintar_statement_pattern, repetir_statement_pattern
])

newline_placeholder = r"{newline}"
alfabeto = r"[a-zA-Z0-9{},() \n\t]"
