
# Analizador Léxico de C - Guía de Ejecución

## 1. Requisitos previos

- Python 3.8 o superior
- `pip` disponible

## 2. Crear y activar entorno virtual

Desde la carpeta `python/` del proyecto:

```bash
cd python
python3 -m venv .venv
```

Activar el entorno virtual:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

Cuando esté activo, verás `(.venv)` al inicio de la terminal.

## 3. Instalar dependencias

Con el entorno virtual activo:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Dependencias requeridas por el proyecto:

- `pygments>=2.19.2`
- `colorama>=0.4.6`

## 4. Ejecutar el programa

El programa principal es `src/main.py`.

### Opción A: entrada por teclado

```bash
python src/main.py
```

Escribe el código C línea por línea. Para finalizar la captura, usa el símbolo `$`.

### Opción B: entrada por archivo

1. Coloca el archivo fuente dentro de `python/inputs/`.
2. Ejecuta:

```bash
python src/main.py <nombre_archivo>
```

Ejemplo:

```bash
python src/main.py code.c
```

## 5. Archivos de salida

Los resultados exportados se guardan en `python/outputs/` con el formato:

- `<nombre_archivo>_output.txt` para análisis por archivo
- `keyboard_output.txt` para análisis por teclado (si se exporta)

## 6. Errores comunes

Si aparece `ModuleNotFoundError` (por ejemplo, `pygments` o `colorama`):

1. Verifica que el entorno virtual esté activo.
2. Reinstala dependencias:

```bash
python -m pip install -r requirements.txt
```

3. Ejecuta siempre con el mismo `python` del entorno virtual:

```bash
python src/main.py
```

Para salir del entorno virtual:

```bash
deactivate
```