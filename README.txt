Nombre: Sebastian Guerra Espinoza
ROL: 202173563-1

# Instrucciones de uso

Ejecutar

`$ python pixelart.py`

teniendo las instrucciones para crear la imagen en un archivo "codigo.txt" en el mismo directorio y al mismo nivel que el programa "pixelart.py".

## Formato instrucciones

Las primeras 3 lineas deben tener un orden fijo siendo:
1. "Ancho <ancho del area a dibujar el pixelart>"
2. "Color de fondo <color>"
3. linea en blanco

Luego de esas 3 lineas sigue la serie de instrucciones a realizar para
crear el pixelart.

### Lista instrucciones aceptadas
- `Avanzar[ <nro de bloques>]`
- `Derecha`|`Izquierda`
- `Repetir <n> veces {<serie de instrucciones (se pueden usar repetir anidados)>}`
- `Pintar <color>`

Mientras se respeten las 3 primeras lineas, las instrucciones no tienen una 
estructura fija. Se pueden insertar saltos de lineas en cualquier momento,
excepto dentro de unica instruccion (luego de la apertura de la llave del 
repetir si se aceptan saltos de lineas). Ejemplo: entre la instruccion `Avanzar` y el numero que le corresponde no puede ir un salto de linea. Lo mismo con la instruccion `Pintar` y su respectivo color.

### Formato de colores aceptados

Para especificar un color se usa el formato "RGB(<rojo>, <verde>, <azul>)" siendo cada numero un entero entre 0 y 255 inclusivos. Tambien se permiten espacios entre los parentesis y las comas pero no saltos de linea.

Tambien hay una lista de colores predefinidos:
- "Rojo"
- "Verde"
- "Azul"
- "Negro"
- "Blanco"


Tanto las instrucciones como los colores son sensibles a las mayusculas.

En caso de encontrarse algun error de sintaxis, se indicara el numero de linea y la linea en donde se encontro el error en el archivo "codigo.txt" y no se ejecutaran las instrucciones.

En caso de encontrarse un error en tiempo de ejecucion (que el personaje se salga del espacio destinado al pixelart), se indicara el numero de linea y la linea en donde se produjo el error por salida estandar y se detendra la ejecucion.


## Detalles de la implementacion

