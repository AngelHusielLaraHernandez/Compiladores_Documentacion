# ¿Cómo ejecutar el proyecto?

Crear y activiar un entorno virtual (opcional pero recomendado):
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```
Instalar las dependencias:
```bash
pip install -r requirements.txt
``` 
**EJECUCIÓN VERSION UI**
```bash
python -m streamlit run ui/app.py
```
**EJECUCIÓN VERSION CONSOLA**
```bash
python .\compiler\main.py
```


# Arquitectura del Proyecto

El proyecto se estructurará de la siguiente manera:
~~~
📁 Proyecto_Parser_SDT/
│
├── 📁 compiler/               # CAPA LÓGICA (Backend del compilador)
│   ├── __init__.py
│   ├── lexer.py               # Tokenización con Pygments
│   ├── adapter.py             # Puente entre Pygments y PLY
│   ├── grammar.py             # Reglas gramaticales (PLY/YACC)
│   ├── ast_nodes.py           # Estructuras del AST
│   ├── semantic.py            # Reglas de validación semántica
│   ├── parser_engine.py       # Orquestación parseo + semántica
│   ├── parser_sdt.py          # Modulo Auxiliar para la importación de otros módulos
│   └── main.py                # Ejecución Modo Principal
│
├── 📁 ui/                     # CAPA DE PRESENTACIÓN (Frontend)
│   ├── app.py                 # Aplicación principal de Streamlit
│   └── 📁 assets/             
│       └── styles.css         # Archivos de estilo para la UI
│
├── 📁 utils/                  # CAPA DE UTILIDADES (Modo Terminal)
│   ├── __init__.py
│   ├── formatter.py           # Funciones de impresión y color
│   └── file_handler.py        # Lectura y escritura de archivos
│
├── 📁 inputs/                 # Archivos de prueba
│   ├── Ejemplos probados
│
├── 📁 outputs/                # Resultados
│   ├── Salidas que genera el programa terminal
│
├── 📄 README.md               # Documentación principal
└── 📄 requirements.txt        # Dependencias
~~~


# Modificaciones Realizadas al lexer

## Adaptación del Lexer para PLY.YACC (adapter.py) [TIENE QUE VER CON EL REPORTE]

Apartir del código del lexer que ya se tiene, se realizaron las siguientes modificaciones para adaptarlo a las necesidades del proyecto:

Como se va acerr usdo de PLY.YACC para el análisis sintáctico, se hizo necesario modificar la salida del lexer para que sea compatible con las entradas que PLY espera. Se debe de pasar a clase que tenga un metodo token().Este método debe retornar un objeto con los atributos .type y .value cada vez que se le llame, y retornar None cuando ya no haya más tokens. 

Es por esto que se creo el archivo adapter.py, que contiene la clase adaptadora que transforma la lista de tuplas generada por el lexer actual (Pygments) en los objetos dinámicos que el analizador sintáctico (PLY) exige para funcionar.

Se crea una clase llamada PlyLexerAdapter donde se recibe la lista de tokens generada por el Lexer donde se normalizan los tokens para que tengan el formato esperado por PLY. Luego, se implementa el método token() que devuelve un token a la vez, con los atributos .type y .value, y maneja el final de la lista de tokens devolviendo None.

## Modulo auxiliar para la importacion de otros modulos (parser_sdt.py) [Consideración Técnica]

Debido a que se tiene una estructura modularizada del proyecto, con varios archivos para diferentes responsabilidades (ast_nodes.py, grammar.py, semantic.py, parser_engine.py), se creó un módulo adicional llamado parser_sdt.py que actúa como una fachada de compatibilidad. Este módulo mantiene la superficie de importación antigua intacta mientras delega la implementación en los módulos enfocados. Esto permite que el código que depende de parser_sdt.py no tenga que cambiar sus importaciones

## Producciones Gramaticales (gramatica.md) [TIENE QUE VER CON EL REPORTE MUUY IMPORTATE]

Dado que se va a usar PLY.YACC para el análisis sintáctico, fue necesario realizar las modificaciones a la primera grámatica que se tenía para que esta sea compatible con el formato de producciones que PLY.YACC, principalemennte cuando se creo la primera grámatica fue opensando en una forma de Parsers Top-Down, lo que llevó a escribir las producciones de forma recursiva a la derecha. Sin embargo, De acuerdo a la documentación de PLY.YACC el parseo se realiza de Bottom Up LALR(1), por lo que relizaron las siguientes modificaciiones.


De acuerdo a la documentación de PLY.YACC, se recomienda ampliamente que en caso de tener recursividad en una regla de producción, esta se debe de escribir en forma izquierda para evitar problemas de ambigüedad. Por lo tanto, **se modificaron las producciones para que sean recursivas a la izquierda en lugar de a la derecha**.

Uno de los cambios mas significantes es que se **elimino la precedencia de operadores directamente en la grámatica** esto ya que PLY.YACC tiene un mecanismo específico para manejar la precedencia de operadores a través de la declaración de precedencia y asociatividad, lo que permite un manejo más claro y eficiente de las expresiones aritméticas, de forma que las reglas de producción relacionadas con operaciones aritméticas se simplificaron y se delegó el manejo de la precedencia a las declaraciones específicas de PLY.YACC.

De acuerdo a lo visto en clase siempre se prefieren grámaticas donde no se tengas reglas epsilón, sin embargo debido a las intrucciones que se quieren implementar en lenguaje C, se hizo necesario incluir algunas reglas epsilón para manejar ciertos casos, no obstante **se eliminaron reglas de producción epsilon intermedias** con la finalidad de tener el menor número de reglas posibles con epsilón. Esto se logró reestructurando las reglas de producción , dividiendo en caminos para casos especirficos a partir de esa regla. De igual forma se añadio la regla de producción vacía (empty) para representar explícitamente las producciones epsilon, ya que yYACC no tiene una notación special para las producciones epsilon, y se necesita una forma de representarlas en la gramática. 

La ultima modificación fue realizar **correcciones necesarias a las producciones** epecificamente las sentencias relacionadas con las declaraciones de variables(puto y coma, etc.)

### Nueva Grámatica

~~~
program -> stmt_list

stmt_list -> stmt_list stmt | stmt

stmt -> decl_num
      | decl_char
      | assign_stmt
      | if_stmt
      | while_stmt
      | for_stmt
      | print_stmt
      | scan_stmt
      | unary_stmt

decl_num -> type_num IDENTIFIER ;
          | type_num IDENTIFIER = math_expr ;

decl_char -> type_char IDENTIFIER ;
           | type_char IDENTIFIER = VALUE_CHAR ;

assign_stmt -> IDENTIFIER assign_expr_op math_expr ;
            | IDENTIFIER = VALUE_CHAR ;

type_num -> INT | FLOAT | DOUBLE

type_char -> CHAR

if_stmt -> IF ( cond ) { stmt_list }

while_stmt -> WHILE ( cond ) { stmt_list }

for_stmt -> FOR ( for_init ; for_cond ; for_step ) { stmt_list }

for_init -> type_num IDENTIFIER
         | type_num IDENTIFIER = math_expr
         | IDENTIFIER assign_expr_op math_expr
         | empty

for_cond -> cond | empty

for_step -> inc_dec_op IDENTIFIER
         | IDENTIFIER inc_dec_op
         | IDENTIFIER assign_expr_op math_expr
         | empty

print_stmt -> PRINTF ( print_args ) ;

print_args -> TEXT_STRING
          | TEXT_STRING , id_list

scan_stmt -> SCANF ( TEXT_STRING , & IDENTIFIER ) ;

id_list -> id_list , IDENTIFIER
        | IDENTIFIER

unary_stmt -> inc_dec_op IDENTIFIER ;
            | IDENTIFIER inc_dec_op ;

inc_dec_op -> ++ | --

assign_expr_op -> = | += | -= | /=

math_expr -> math_expr + math_expr
          | math_expr - math_expr
          | math_expr * math_expr
          | math_expr / math_expr
          | math_expr % math_expr
          | IDENTIFIER
          | VALUE_NUM
          | ( math_expr )

cond -> cond || cond
     | cond && cond
     | math_expr rel_op math_expr
     | ! cond
     | ( cond )
     | math_expr
     | VALUE_CHAR

rel_op -> == | != | < | > | <= | >=

empty -> epsilon
~~~

Sin  embargo para que la gramatica anterior sea completamente compatible con PLY.YACC, se deben realizar modificaciones adicionales para poder implementar la gramatica a nivel de código.

PLY.YACC requiere que las reglas de producción se definan como funciones en el código, donde el nombre de la función corresponde al nombre de la regla de producción dichas funciones deben empezar con el prefijo `p_` seguido del nombre de la regla de producción. Además, las reglas de producción deben estar definidas en un formato específico que PLY.YACC pueda interpretar correctamente. Esto implica que se deben seguir ciertas convenciones en la forma en que se escriben las reglas de producción en el código, como el uso de docstrings para definir la estructura de la regla y el manejo adecuado de los tokens y símbolos no terminales. Por otro lado la función debe reciben un argumento `p` que es una lista donde `p[0]` representa el resultado de la producción y `p[1]`, `p[2]`, etc., representan los componentes de la producción. Otro aspecto de suma importancia es declarar la tupla de tokens que se va a usar en el análisis sintáctico, esta tupla debe contener los nombres de los tokens que se van a utilizar en las reglas de producción, y estos nombres deben coincidir exactamente con los nombres de los tokens definidos en el lexer. 

De igual forma en este archivo `grammar.py` se implementa la precedncia de operadores a través de la declaración de precedencia y asociatividad, lo que permite un manejo más claro y eficiente de las expresiones aritméticas. Esto se logra mediante la declaración de una tupla llamada `precedence` donde se especifica el orden de los operadores y su asociatividad (izquierda, derecha o no asociativo). Esta declaración es crucial para que PLY.YACC pueda resolver correctamente las ambigüedades en las expresiones aritméticas y garantizar que se evalúen en el orden correcto según las reglas de precedencia establecidas.

Finalmente se definen las reglas de producciones adicionales, una ya se menciono incluso se incluyo al definir la grámartica, que es la regla de producción vacía (empty) para representar explícitamente las producciones epsilon, ya que yYACC no tiene una notación special para las producciones epsilon, y se necesita una forma de representarlas en la gramática. La segunda regla de producción adicional es la regla de producción obligatoria que solicita PLY.YACC `p_error` que se define para manejar los errores de sintaxis durante el análisis sintáctico. Esta función se llama automáticamente cuando PLY.YACC encuentra un error de sintaxis en el código fuente que está analizando. La función `p_error` recibe un argumento `p` que representa el token donde ocurrió el error, y dentro de esta función se pueden implementar las acciones necesarias para manejar el error, como imprimir un mensaje de error detallado, registrar el error en un archivo de log o realizar cualquier otra acción que se considere apropiada para informar al usuario sobre el error de sintaxis encontrado.

Al final de cada función que corresponde de una regla de producción, se debe construir el nodo del AST utilizando la función `make_node` importada desde `ast_nodes.py`. Esta función toma como argumentos el tipo de nodo que se está construyendo y los componentes de la producción que corresponden a ese nodo. Esto permite construir el árbol de sintaxis abstracta (AST) de manera estructurada y organizada, facilitando posteriormente la realización del análisis semántico y otras fases del compilador.

Donde cada nodo del arbol se alamcena con la información relevante de la producción
- kind: el tipo de nodo que se está construyendo (por ejemplo, "assign_stmt", "if_stmt", etc.)
- children: una lista de los componentes de la producción que corresponden a ese nodo, que pueden ser otros nodos del AST o tokens terminales.
- lineno: el número de línea en el código fuente donde se encuentra la producción, lo que es útil para la generación de mensajes de error y para el análisis semántico posterior.
- value: el valor del token terminal si el nodo corresponde a un token, o None si el nodo es un símbolo no terminal. Esto permite almacenar información adicional sobre los tokens en el AST, lo que puede ser útil para la generación de código o para otras fases del compilador.

## AST (Árbol de Sintaxis Abstracta) [TIENE QUE VER CON EL REPORTE]
El AST (Árbol de Sintaxis Abstracta) es una representación estructurada del código fuente que captura la estructura sintáctica del programa de manera abstracta, sin incluir detalles específicos de la sintaxis. Para esto se creo el archivo `ast_nodes.py` donde se define la clase `ASTNode` que representa un nodo en el AST. SDe implementan funciones auxiliares para convertir el arbol a un formato diccionario (`to_dict`) y `to_tree_lines` genera una representación visual del árbol en forma de texto, lo que facilita la comprensión de la estructura del programa. Además, se implementa la función `make_node` que actúa como una fábrica para crear nodos del AST de manera consistente y estructurada, lo que simplifica la construcción del AST durante el análisis sintáctico. Esta función toma como argumentos el tipo de nodo que se está construyendo, los componentes de la producción que corresponden a ese nodo, el número de línea en el código fuente y el valor del token si es un nodo terminal. Esto permite construir el AST de manera organizada y con toda la información relevante para las fases posteriores del compilador, como el análisis semántico.

## Validación Semántica [TIENE QUE VER CON EL REPORTE MUUY IMPORTANTE (ANALISIS SEMANTICO)]

Reglas semanticas que se buscan a implementadar son las siguientes:

1. Variables declaradas antes de usarse.
2. Compatibilidad de tipos en asignación.
3. Operandos válidos en expresiones aritméticas y lógicas.
4. Reglas de printf y scanf (cantidad y tipo de argumentos/formato).
5. Condiciones evaluables en if/while/for.

Para esto es se implementa el archivo `semantic.py` donde recibe el AST generado por el análisis sintáctico y realiza la validación semántica de acuerdo a las reglas mencionadas. Se implementa una tabla de símbolos para llevar un registro de las variables declaradas y sus tipos, lo que permite verificar que las variables se declaren antes de usarse y que las asignaciones sean compatibles con los tipos declarados. 

Se definen funciones auxiliares para evaluar el tipo de las expresiones y para manejar la tabla de símbolos, lo que facilita la implementación de las reglas semánticas.
- `enter_scope` y `exit_scope` para manejar los ámbitos de las variables, es decir cuando entra a un bucle de código se quedan separadas del ambito exterior, de forma que solo existen dentrio de ese ámbito. Exit Scope es para elimionar el ambito actual cuidando que no se eliminen variables de ambitos exteriores.
- `declare` para declarar una variable en la tabla de símbolos, lo que permite verificar si una variable ya ha sido declarada y evitar redeclaraciones.
- `lookup` para buscar una variable en la tabla de símbolos, lo que permite verificar si una variable ha sido declarada antes de usarse y obtener su tipo para verificar la compatibilidad en las asignaciones y expresiones.
- `snapshot` crea una vista combinada de todas las variables declaradas en los ámbitos actuales, lo que facilita la generación de mensajes de error detallados en caso de violaciones semánticas, ya que se puede mostrar el estado completo de la tabla de símbolos en el momento del error.

Posteriormente se procede a implementar las reglas semanticas a nivel de código, las reglas necesarias para validar cada una de las reglas semánticas mencionadas

(PASARLAS A LA FORMA (PSEUDOCODIGO COMO LO VIMOS EN CLASE) PARA QUE SE ENTIENDA MEJOR Y SE VEA LA LOGICA DE CADA REGLA SEMANTICA LO PIDE EN EL REPORTE, NO SOLO PONERLAS EN FORMA DE FUNCIONES)

~~~python
def _infer_literal_type(value: str) -> str:
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        return "char"
    if value.startswith('"') and value.endswith('"'):
        return "string"
    return "string"


def _infer_constant_type(value: str) -> str:
    return "float" if "." in str(value) else "int"


def _is_numeric(t: str) -> bool:
    return t in {"int", "float", "double", "char"}


def _is_logical_evaluable(t: str) -> bool:
    return t in {"bool", "int", "float", "double", "char"}


def _compatible_assign(target: str, source: str) -> bool:
    if target == source:
        return True
    if target == "double" and source in {"float", "int", "char"}:
        return True
    if target == "float" and source in {"int", "char"}:
        return True
    if target == "int" and source == "char":
        return True
    return False


def _extract_format_specifiers(raw_literal: str) -> List[str]:
    text = raw_literal.strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]

    specs: List[str] = []
    i = 0
    while i < len(text):
        if text[i] == "%":
            if i + 1 < len(text) and text[i + 1] == "%":
                i += 2
                continue
            if i + 1 < len(text):
                spec = text[i + 1]
                if spec in {"d", "i", "f", "c", "s"}:
                    specs.append(spec)
                i += 2
                continue
        i += 1
    return specs


def _format_compatible(var_type: str, spec: str) -> bool:
    if spec in {"d", "i"}:
        return var_type == "int"
    if spec == "f":
        return var_type in {"float", "double"}
    if spec == "c":
        return var_type == "char"
    if spec == "s":
        return var_type == "string"
    return False
~~~

Posteriormentes se implemento el metodo de `analyze_semantics` que es donde realiza la validación semántica de acuerdo a las reglas mencionadas. Dodne se inicializa una tabla de símbolos, lista de errores, traza SDT paso a paso. En la traza s eguarda el (paso, nodo, linea, estado y snapshot) La funcuón `expr_type` es la encargada de aplicar las reglas semánticas a cada nodo del AST, verificando el tipo de cada expresión y asegurando que se cumplan las reglas de compatibilidad de tipos, declaración de variables, y otras reglas semánticas definidas. En caso de encontrar un error, devuelve un mensaje de error detallado que incluye la línea del código donde ocurrió el error (Se configuraron los mensajes de error que se pueden enconrtrar en compiladores de C), el tipo de error y el estado actual de la tabla de símbolos para facilitar la depuración. Como se tiene un arbol por medio de la función recursiva `walk` se puede recorrer todo el AST y aplicar las reglas semánticas a cada nodo, lo que permite validar todo el programa de manera exhaustiva y generar una traza detallada del proceso de validación semántica.

## Modulo que junta todo el proceso de análisis sintáctico y semántico (parser_engine.py) [tecnico]
Este modula junta la logica de los demas archivos para pipeline completo de análisis sintáctico y semántico. Hereda de la clase `grammar.py` para tener acceso a las reglas de producción, precedenncia, y posteriormente crea el objeto parser LALR(1) de PLY.YACC utilizando las reglas de producción definidas en `grammar.py`.

Se procede a ejecutar el analisis lexico, donde se obtiene la lista de tokens a partir del código fuente, luego se crea una instancia del adaptador `PlyLexerAdapter` para convertir la lista de tokens (`adapter.py`) en el formato esperado por PLY.YACC. Posteriormente se ejecuta el análisis sintáctico utilizando el parser LALR(1) creado, donde si la sintaxis es valida se obtiene  AST `ast_nodes.py`, de igual manera si la sintaxis es valida se llama a la funcion de análisis semántico `analyze_semantics` definida en `semantic.py` para validar las reglas semánticas del programa. Finalmente se devuelve un resultado que incluye el AST generado, la traza del análisis semántico, y cualquier error semántico encontrado durante el proceso de validación.

## Visualización del Programa (Terminal y UI) [tecnico]

Debido a que el lexer se implemento por linea de comandos, se decidió implementar dos formas de ejecutar el programa por medio de linea de comandos y por medio de una interfaz gráfica utilizando Streamlit.

### Modo Terminal

Se adapto el programa inicial por linea de comandos, ahora tiene un menu interaactivo dodne se pregunta al usuario si desea ingresar el código por teclado o cargar un archivo, luego se procesa el análisis sintáctico y semántico, y finalmente se muestra un reporte detallado del análisis realizado, incluyendo los errores encontrados y la traza del análisis semántico. El programa también permite ejecutar múltiples análisis de manera consecutiva sin tener que reiniciar la aplicación, lo que facilita la prueba de diferentes fragmentos de código de manera rápida y eficiente.

En caso de que haya un error sintactico no se genera el JSON (analisis semantico)

### Modo UI

Lo mismo para la UI, solo que es más interactiva y cada analisis se puede visualizar de forma más clara, ademas de que se pueden cargar archivos directamente desde la interfaz y se muestra el resultado del análisis de manera organizada, con colores y formatos que facilitan la lectura y comprensión de los resultados. La UI también permite ejecutar múltiples análisis de manera consecutiva sin tener que recargar la página, lo que facilita la prueba de diferentes fragmentos de código de manera rápida y eficiente. El grafo del AST se PUEDE HACER GRANDE, en realidad todo elemtno se le puede hacer zoom.

Consideración para operaciones de if, while y for, se ve un nodo vacio, pero esto es por la regla de producción vacía (empty) que se implemento para manejar los casos donde no hay una condición en el for o while, o en el caso del if, esto es completamente normal y esperado, ya que la regla de producción vacía permite representar explícitamente la ausencia de una condición en estas estructuras de control, lo que es común en ciertos casos de uso en el lenguaje C. 
