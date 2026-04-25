# Grammar Suite

Conjunto de pruebas para la gramática implementada en `compiler/grammar.py`.

Conjunto de Pruebas para validar solo estas reglas semánticas:
- Variables declaradas antes de usarse.
- Compatibilidad de tipos en asignación.
- Operandos válidos en expresiones aritméticas y lógicas.
- Reglas de printf y scanf (cantidad y tipo de argumentos/formato).
- Condiciones evaluables en if/while/for.

## Casos válidos (esperado: Sintaxis=SI, SDT=SI)
- `ok_reglas_semanticas.c` (caso integrado válido para todas las reglas)

## Casos con error semántico (esperado: Sintaxis=SI, SDT=NO)
- `sem_variable_no_declarada.c` (uso de variable no declarada)
- `sem_asignacion_incompatible.c` (asignación de tipo incompatible)
- `sem_operadores_invalidos.c` (operandos inválidos en expresión lógica/relacional)
- `sem_printf_argumentos_invalidos.c` (cantidad/tipo de argumentos en printf)
- `sem_scanf_formato_incompatible.c` (formato incompatible en scanf)
- `sem_condicion_no_evaluable.c` (condición no evaluable en if)

## Casos con error sintáctico (esperado: Sintaxis=NO, SDT=NO)
- `syn_sintaxis_invalida.c` (sentencia inválida)
- `syn_if_sin_parentesis.c` (if con sintaxis inválida)