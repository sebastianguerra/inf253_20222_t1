# Extract width
ancho_pattern = r"^Ancho (?P<ancho>\d+)" # Captura el Ancho dado
number_pattern = r"0|[1-9](?:0|[1-9])*"

# Colores
color_pattern = r"Rojo|Verde|Azul|Negro|Blanco|RGB *\( *(?:{np}) *, *(?:{np}) *, *(?:{np}) *\)".format(np = number_pattern)

# Background color
bg_color_pattern = r"Color de fondo (?P<bg_color>{})".format(color_pattern) # Captura el color de fondo

# declaraciones
avanzar_statement_pattern = r"Avanzar(?P<avanzar_nveces> [1-9][0-9]*)?".format(number_pattern)
girar_statement_pattern = r"Izquierda|Derecha"
pintar_statement_pattern = r"Pintar (?P<pintar_color> {})".format(color_pattern)
repetir_statement_pattern = r"Repetir (?P<repetir_nveces>[1-9][0-9]*) veces {"

statements_pattern = "|".join([
    avanzar_statement_pattern,
    girar_statement_pattern,
    pintar_statement_pattern,
    repetir_statement_pattern
])


newline_placeholder = r"{newline}"
