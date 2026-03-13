# Proyecto de Compiladores: Analizador Léxico (Lexer)

Este contiene la entrega del primer proyecto de **Compiladores** , reporte de un **Analizador Léxico**.

---

##  Estructura del Proyecto

El proyecto está organizado en diferentes directorios para separar el código fuente, la documentación en LaTeX.

```text
 Compiladores
 ┣  bibliografias/    # Archivos para gestionar la bibliografía (.bib)
 ┣  FrontPage/        # Almacena el código LaTeX dedicado exclusivamente a la portada
 ┣  img/              # Recursos gráficos: capturas de pantalla, logos institucionales (UNAM, FI)
 ┣  python/           # Código fuente del proyecto (Analizador Léxico y dependencias en Python)
 ┣  main.tex          # Archivo LaTeX principal que une el reporte (preámbulo y contenido)
 ┣  .gitignore        # Archivos/carpetas ignorados por el control de versiones (Git)
 ┗  README.md         # Documentación sobre el proyecto y comandos de Git
```

### Explicación de los Archivos Principales
1. **`main.tex`**: Es el esqueleto del reporte. Aquí se importan las bibliotecas, se configura el esquema visual de las páginas (encabezados con logos y líneas divisoras, márgenes, coloración de hipervínculos) e incluye estructurada y ordenadamente las secciones del reporte (Introducción, Desarrollo, Resultados, etc.).
2. **`FrontPage/portada.tex`** (o equivalente de portada): Documento LaTeX aislado dedicado estrictamente al diseño de la portada (para facilitar su edición). El archivo `main.tex` lo incluye de manera automática y limpia.
3. **`bibliografias/referencias.bib`**: Contiene todas la bibliografía estructurada según las reglas de `biblatex` (estilo APA).
4. **`python/`**: Código o rutinas usadas para leer la entrada de datos, analizar los tokens y general las salidas propias del Lexer.

---

##  Configuración 

Si usas un editor como Visual Studio Code (con la extensión *LaTeX Workshop*), basta con presionar el botón de "Build" (o usar `Ctrl+Alt+B`). Si prefieres la terminal:
```bash
pdflatex main.tex
biber main          # Para compilar las bibliografías
pdflatex main.tex
```

---

##  Guía Rápida de Git (Colaboración)

Para trabajar colaborativamente sin sobreescribir el trabajo de los demás, se recomienda encarecidamente utilizar y moverse entre **Ramas (Branches)**. A continuación, las instrucciones esenciales:

### Crear tu propia rama y moverte a ella
Lo ideal es que cada miembro del equipo tenga su propia rama para hacer cambios (por ejemplo, alguien programa el lexer y otro edita el LaTeX).
```bash
# Crea una nueva rama y te cambia automáticamente a ella
git checkout -b nombre-de-ti-rama

# (Alternativa más moderna):
git switch -c nombre-de-tu-rama
```
> *Ejemplo:* `git switch -c feature/codigo-python`

### Moverse entre ramas existentes
Si el equipo ya creó la rama y necesitas cambiar a ella (o volver a *main*):
```bash
# Moverte a la rama "main" (o "master")
git switch main

# Moverte a la rama de un compañero
git switch nombre-de-la-rama-existente
```

### Subir y publicar tus cambios a GitHub
Una vez que has editado tus archivos y quieres guardarlos en el repositorio de la nube, sigue estos 3 pasos:

**1. Preparar los cambios (ADD)**
Agrega todos los archivos nuevos y modificados a la fase de preparación de Git:
```bash
git add .
```

**2. Empaquetar los cambios (COMMIT)**
Guarda los archivos con un mensaje descriptivo para que el equipo sepa qué hiciste:
```bash
git commit -m "Se agregaron tokens base y se corrigió el LaTeX de resultados"
```

**3. Publicar los cambios (PUSH)**
Sube tu rama y los commits a la nube (si es la primera vez que subes esa rama específica a GitHub):
```bash
git push -u origin nombre-de-tu-rama
```
*Nota: Si la rama ya fue publicada antes, simplemente escribe `git push`.*

### Obtener los cambios del equipo (PULL)
Antes de empezar a trabajar, es fundamental descargar el progreso que los demás integraron a la rama principal para evitar conflictos:
```bash
git pull origin main
```