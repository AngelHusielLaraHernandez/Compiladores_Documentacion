
# ¿Cómo Ejecutar el Programa?

Se deben instalar las dependencias necesarias para la ejeción del programa

## Usando requirements
~~~
pip install -r requirements.txt
~~~
## Usando pip install

~~~
pip install Pygments
pip install colorama
~~~

# ¿Cómo USAR el Programa?

Cambiarse al directorio src.

El programa para leer tiene dos modos por **teclado** y haciendo uso de **archivos**

## Por medio del teclado

Si se quiere realizar por telclado se debe de ejecutar el programa sin ningun argumento (recordar cambiarse a la carpeta **src**)
~~~
python main.py
~~~

El programa permite escribir por teclado liena a linea código de C.
Cuando se quiere que deje de leer por teclado se debe de ingresar el simbolo **$**

## Por medio del archivos

Para leer un archivo se debe de colocar primero el archivo dentro de la carpeta **inputs** para posteriormente ejecutar el programa con el nombre del archivo como argumento
~~~
python main.py <nombre_programa>
~~~