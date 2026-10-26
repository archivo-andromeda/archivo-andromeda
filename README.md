# Archivo Andrómeda

Catálogo comunitario de literatura especulativa LGBTQ+ latinoamericana.

Todo el catálogo vive en un solo archivo, **`datos/obras.csv`**. Cada vez que lo modificas en GitHub, el sitio se reconstruye y se publica solo en un par de minutos.

---

## Índice

1. [Cómo está organizado](#1-cómo-está-organizado)
2. [Puesta en marcha (una sola vez)](#2-puesta-en-marcha-una-sola-vez)
3. [Conectar el Google Form](#3-conectar-el-google-form)
4. [El día a día: curar y publicar](#4-el-día-a-día-curar-y-publicar)
5. [Referencia de columnas de `obras.csv`](#5-referencia-de-columnas-de-obrascsv)
6. [Preguntas frecuentes](#6-preguntas-frecuentes)

---

## 1. Cómo está organizado

```
datos/obras.csv          ← EL CATÁLOGO: una fila por obra
datos/vocabulario.yml    ← etiquetas permitidas, sus descripciones y sinónimos
datos/autores.csv        ← datos de autoras y autores (opcional, se llena a mano)
config.yml               ← nombre del sitio, enlace al formulario, créditos
paginas/acerca.md        ← texto de la página «Acerca»
paginas/proponer.md      ← texto de la página «Proponer una obra»
estatico/portadas/       ← imágenes de portada (opcional)
plantillas/, estatico/   ← diseño (HTML, CSS, JS)
scripts/construir.py     ← genera el sitio a partir del CSV
scripts/importar_propuestas.py ← trae las propuestas aprobadas del formulario
.github/workflows/       ← automatizaciones de GitHub (publicar e importar)
```

Lo único que vas a tocar normalmente es `datos/obras.csv`. A veces también `config.yml`, `vocabulario.yml` o los textos de `paginas/`.

---

## 2. Puesta en marcha (una sola vez)

### 2.1 Crear la cuenta de GitHub

1. Entra a <https://github.com/signup> y crea una cuenta gratuita. Tu **nombre de usuaria** aparecerá en la dirección del sitio (`https://USUARIA.github.io/archivo-andromeda`), así que elígelo con cuidado.
2. Confirma tu correo.

### 2.2 Crear el repositorio

1. Arriba a la derecha, pulsa **+** → **New repository**.
2. **Repository name:** `archivo-andromeda`.
3. Márcalo como **Public** (GitHub Pages es gratis solo para repositorios públicos).
4. **No** marques ninguna casilla de README, .gitignore ni licencia.
5. Pulsa **Create repository**.

### 2.3 Subir los archivos

1. Descomprime el `.zip` del archivo en tu computador.
2. **Importante:** la carpeta `.github` está oculta porque su nombre empieza con un punto.
   - **Mac:** en el Finder, abre la carpeta y presiona `Cmd + Shift + .` para ver los archivos ocultos.
   - **Windows:** en el Explorador, ve a *Vista → Mostrar → Elementos ocultos*.
3. En la página del repositorio recién creado, pulsa **uploading an existing file**.
4. Selecciona **todo el contenido** de la carpeta (no la carpeta misma), incluida `.github`, y arrástralo a la ventana.
5. Abajo, pulsa **Commit changes**.
6. Comprueba que en el repositorio aparezca la carpeta `.github`. Si no aparece, revisa la sección [«No se subió la carpeta .github»](#no-se-subió-la-carpeta-github).

### 2.4 Activar GitHub Pages

1. En el repositorio, ve a **Settings** → **Pages** (en el menú de la izquierda).
2. En **Build and deployment → Source**, elige **GitHub Actions**.
3. Ve a la pestaña **Actions**. Si ves «Publicar sitio» con un círculo amarillo, espera; con una ✓ verde, ya está. Si no se ejecutó, entra en «Publicar sitio» y pulsa **Run workflow**.
4. Tu sitio queda en `https://USUARIA.github.io/archivo-andromeda/`.

### 2.5 Ajustar la configuración

Abre `config.yml` en GitHub, pulsa el lápiz ✏️ y completa:

```yaml
url_sitio: "https://USUARIA.github.io/archivo-andromeda"
```

Pulsa **Commit changes**. El sitio se vuelve a publicar solo.

---

## 3. Conectar el Google Form

### 3.1 Crear el formulario

En <https://forms.google.com> crea un formulario nuevo. **Usa estos títulos de pregunta**: el importador las reconoce por el comienzo del texto, así que puedes agregar una aclaración al final del título, pero no cambiar el principio. El orden no importa.

Divide el formulario en **tres secciones** (botón *Agregar sección*): «La obra» con las preguntas 1 a 8, «Datos de publicación (opcional)» con las preguntas 9 a 18 y «Para terminar» con la 19. Solo título y autore son obligatorias.

La primera sección reúne lo que más sirve que complete quien leyó la obra: el subgénero, las disidencias, los afectos, los temas y la descripción. Los datos de publicación casi siempre se pueden encontrar en línea después.

**Sección 1 · La obra**

| # | Título de la pregunta | Tipo | Obligatoria | Opciones o ayuda |
|---|---|---|---|---|
| 1 | Título de la obra | Respuesta corta | Sí | |
| 2 | Autore | Respuesta corta | Sí | *Ayuda: «Si son varias personas, sepáralas con punto y coma. Usa el nombre actual de cada persona.»* |
| 3 | Formato | Opción múltiple | | Novela · Novela corta · Libro de cuentos · Antología · Cuento · Microficción · Poemario narrativo · *Otro* |
| 4 | Subgénero especulativo | Casillas | | Ciencia ficción · Weird · Distopía · Utopía · Gótico · Ucronía · Fantasía · Horror · Ficción climática · Postapocalíptico · Poesía especulativa · *Otro* |
| 5 | Disidencias sexogenéricas representadas | Casillas | | Lésbica · Gay · Marica · Bisexual · Trans · Travesti · No binarie · Género fluido · Intersex · Asexual · Poliamor · Cuir · *Otro* |
| 6 | Afectos: ¿Qué te hizo sentir esta obra? | Casillas | | Esperanza · Agobio · Calentura · Congoja · Ternura · Mariposas · Rabia · Asco · Extrañeza · Curiosidad · *Otro* |
| 7 | Temas | Respuesta corta | | *Ayuda: «Algunas palabras clave, separadas por comas»* |
| 8 | Descripción breve | Párrafo | | |

**Sección 2 · Datos de publicación (opcional)**

| # | Título de la pregunta | Tipo | Opciones o ayuda |
|---|---|---|---|
| 9 | Publicado en | Respuesta corta | *Ayuda: «Si es un cuento o una microficción: el nombre del libro, antología, revista o sitio donde se publicó.»* |
| 10 | Año de publicación | Respuesta corta | |
| 11 | País | Respuesta corta | *Ayuda: «Si son varios, sepáralos con comas»* |
| 12 | Medio | Opción múltiple | Editorial · Autopublicación · Editorial cartonera · Fanzine · Plaquette · Revista impresa · Revista en línea · Blog o web personal · Redes sociales · *Otro* |
| 13 | Editorial | Respuesta corta | |
| 14 | Editorx o compilación | Respuesta corta | *Ayuda: «Quién editó o compiló la antología o revista, si corresponde.»* |
| 15 | Dónde conseguirla o leerla en línea | Respuesta corta | *Ayuda: «Un enlace: la página de la editorial o, si se publicó en internet, el texto mismo.»* |
| 16 | Referencias: Goodreads, Tercera Fundación u otras bases | Respuesta corta | *Ayuda: «Enlaces a la ficha de la obra en bases de datos de libros.»* |
| 17 | Otros enlaces: reseñas, entrevistas | Respuesta corta | |
| 18 | Enlace a la imagen de portada | Respuesta corta | *Ayuda: «Un enlace directo a la imagen. También sirve un enlace de Google Drive compartido.»* |

**Sección 3 · Para terminar**

| # | Título de la pregunta | Tipo | Opciones o ayuda |
|---|---|---|---|
| 19 | Tu nombre o seudónimo (opcional) | Respuesta corta | *Ayuda: «Aparecerá en la ficha como quien propuso la obra»* |

En las preguntas de opciones, el orden de las opciones da lo mismo: el importador lee el texto. Lo que importa es que cada opción coincida con una etiqueta de `datos/vocabulario.yml` o con uno de sus alias, y que ninguna lleve comas (Google separa con comas las casillas marcadas).

Al importar, el enlace de la pregunta 15 se guarda como **lectura en línea** si el medio es revista en línea, blog o redes sociales, y como **dónde conseguirla** en los demás casos.

> En **Configuración** del formulario, deja **desactivada** la opción de recopilar correos electrónicos: la hoja con las propuestas aprobadas será pública.

Copia el enlace del formulario (**Enviar → 🔗 → Acortar URL**) y pégalo en `config.yml`:

```yaml
formulario_url: "https://forms.gle/xxxxxxxx"
```

### 3.2 Preparar la hoja de respuestas

1. En el formulario, pestaña **Respuestas** → **Vincular con Hojas de cálculo** → crear una hoja nueva.
2. En la hoja, la columna **A** es la marca temporal y después vienen las preguntas. En la **primera columna vacía** de la fila 1, escribe: `Aprobada`.
3. Crea una **segunda pestaña** (botón **+** abajo a la izquierda) llamada `aprobadas`. En su celda **A1** pega esta fórmula:

   ```
   =QUERY({'Respuestas de formulario 1'!A:AD}; "select * where lower(Col" & MATCH("Aprobada"; 'Respuestas de formulario 1'!1:1; 0) & ") matches 's[ií]'"; 1)
   ```

   La fórmula busca sola la columna «Aprobada», así que sigue funcionando aunque agregues preguntas al formulario más adelante. (Si tu hoja usa coma como separador, cambia los `;` por `,`. Si la pestaña de respuestas tiene otro nombre, ajústalo en los dos lugares.)

4. Publica **solo esa pestaña**: **Archivo → Compartir → Publicar en la web** → elige la pestaña `aprobadas` → formato **Valores separados por comas (.csv)** → **Publicar**. Copia el enlace que aparece.

Así, las propuestas que no aprobaste nunca se hacen públicas.

### 3.3 Guardar el enlace en GitHub

1. En el repositorio: **Settings → Secrets and variables → Actions → pestaña Variables → New repository variable**.
2. **Name:** `PROPUESTAS_CSV_URL`
3. **Value:** el enlace CSV que copiaste.
4. **Add variable**.

---

## 4. El día a día: curar y publicar

### Aprobar propuestas del formulario

1. Abre la hoja de respuestas y revisa las propuestas nuevas.
2. Para aprobar una, escribe `sí` en su columna **Aprobada**. Si quieres, corrige ahí mismo errores de tipeo.
3. En GitHub, ve a **Actions → Importar propuestas → Run workflow → Run workflow**.
4. En uno o dos minutos las obras aprobadas aparecen en `datos/obras.csv` y en el sitio, con el sello **«en revisión»**.

El importador nunca duplica: si una obra ya está en el catálogo (mismo título y autoría), la salta. Ten en cuenta que Google puede tardar unos 5 minutos en actualizar la hoja publicada.

### Editar el catálogo directamente

**Opción A, en GitHub (cambios pequeños):** abre `datos/obras.csv`, pulsa el lápiz ✏️, edita y guarda con **Commit changes**. Los textos que tengan comas deben ir entre comillas: `"La lesbiana, el oso y el ponqué"`.

**Opción B, en una planilla (cambios grandes):** descarga `obras.csv` (botón ⬇️), ábrelo en Google Sheets, LibreOffice o Excel, edítalo y expórtalo como **CSV UTF-8**. Luego súbelo al repositorio en la carpeta `datos/` (**Add file → Upload files**) reemplazando el anterior.

> En Excel, usa *Guardar como → CSV UTF-8 (delimitado por comas)*. El «CSV» común puede romper las tildes.

### Confirmar una ficha

Cuando hayas revisado una obra, borra el texto de su columna `revision` y desaparece el sello «en revisión».

Solo las fichas confirmadas participan en la **obra del día** de la portada. El sitio elige una cada día (a medianoche, hora de Chile) y la muestra igual a todo el mundo; si todavía no hay ninguna ficha confirmada, el bloque no aparece.

### Obras relacionadas

Cada ficha muestra hasta 3 obras relacionadas, calculadas solas al publicar. Suman puntos la misma autoría (5), cada disidencia compartida (3), cada subgénero y cada tema compartido (2), cada afecto compartido (1), el mismo país (1) y la misma década (1); se muestran las que tienen 4 puntos o más, con lo que comparten. Los pesos se cambian al comienzo de `scripts/construir.py` (`PESOS_RELACION`, `RELACIONADAS_MAX`, `RELACIONADAS_MINIMO`).

### Agregar portadas

- **Desde el formulario:** si la propuesta trae un enlace a la imagen, el importador la descarga, la achica y la guarda sola en `estatico/portadas/<id>.webp`. Si no puede, lo anota en la columna `revision`.
- **Imagen propia:** súbela a `estatico/portadas/` (**Add file → Upload files**; por ejemplo `las-indignas.jpg`) y escribe ese nombre en la columna `portada`. No importa si es grande: al publicar, el sitio la achica a 600 px de ancho (el archivo original no se toca).
- **Imagen en internet:** se puede pegar una URL completa en `portada`, pero no es recomendable: si la otra página cambia, la imagen desaparece.
- **Sin imagen:** deja la columna vacía y el sitio dibuja una portada provisoria. Un cuento sin portada usa la del libro donde se publicó, si está en el archivo.

### Cuentos sueltos y «publicado en»

Un cuento o una microficción se cataloga como cualquier obra, con formato `cuento` o `microficción` y la columna `publicado_en`:

- Si `publicado_en` es el **`id` o el título de una ficha del archivo** (por ejemplo, `ciencia-ficcion-travesti`), el cuento y el libro se enlazan en ambos sentidos: la ficha del libro muestra «Cuentos de este libro en el archivo». Esos cuentos **no aparecen en el catálogo por defecto**; se ven al filtrar por formato «cuento», al buscar su título o desde la ficha del libro.
- Si es **otro nombre** (una antología que no está entera en el archivo, una revista, un blog), el cuento aparece en el catálogo como cualquier obra. Al hacer clic en ese nombre se ven todas las obras publicadas en el mismo lugar.

### Autoras, autores y nombres

- Varias personas en `autoria` o `editorx` se separan con `;`.
- Usa siempre el **nombre actual** de cada persona. Si una obra se publicó con otro nombre, o una persona aparece escrita de formas distintas, agrégala a `datos/autores.csv` con sus `variantes` (separadas por `;`): el sitio agrupa todo bajo el nombre actual y **nunca muestra las variantes** ni las usa en el buscador.
- `autores.csv` es opcional. Columnas: `id`, `nombre`, `variantes`, `pais`, `bio`, `enlaces`. Las fichas de autores usarán estos datos más adelante.

### Agregar o cambiar etiquetas del vocabulario

Edita `datos/vocabulario.yml`. Cada etiqueta puede tener `alias`: otras formas de escribirla que se convierten automáticamente (por ejemplo, `cf` y `sci-fi` → *ciencia ficción*). Si una obra usa una etiqueta que no está en el vocabulario, el sitio igual la muestra, y el registro de **Actions → Publicar sitio** lo avisa.

---

## 5. Referencia de columnas de `obras.csv`

| Columna | Qué va | Ejemplo |
|---|---|---|
| `id` | Identificador para la dirección de la ficha. Si lo dejas vacío, se crea solo a partir del título. | `las-indignas` |
| `titulo` | **Obligatorio.** | `Las indignas` |
| `autoria` | **Obligatorio.** Una o varias personas, separadas por `;` | `Agustina Bazterrica` |
| `editorx` | Quien edita o compila, separado por `;` | |
| `anio` | Año de primera publicación | `2023` |
| `pais` | Uno o varios, separados por `;` | `Argentina` |
| `formato` | Del vocabulario: novela, novela corta, libro de cuentos, antología, cuento, microficción, poemario narrativo | `novela` |
| `medio` | Del vocabulario: editorial, autopublicación, editorial cartonera, fanzine, plaquette, revista impresa, revista en línea, blog o web personal, redes sociales | `editorial` |
| `publicado_en` | Para cuentos: el `id` o título de un libro del archivo, o el nombre de la antología, revista o web | `ciencia-ficcion-travesti` |
| `subgeneros` | Varios, separados por `;` | `distopía; gótico` |
| `disidencias` | Varios, separados por `;` | `lésbica` |
| `afectos` | Del vocabulario: lo que la obra le hizo sentir a quien la leyó. Varios, separados por `;` | `ternura; rabia` |
| `temas` | Libres, separados por `;` | `religión; cuerpo; memoria` |
| `editorial` | | `Alfaguara` |
| `descripcion` | Texto de la ficha | |
| `portada` | Nombre de archivo en `estatico/portadas/` (o una URL) | `las-indignas.jpg` |
| `conseguir` | Dónde conseguirla, de preferencia la página de la editorial. Varios, separados por `;` | `https://…` |
| `leer_en_linea` | Enlace para leerla gratis en internet. Aparece como botón destacado | `https://…` |
| `referencias` | Fichas en bases de datos de libros, separadas por `;`. Goodreads, Tercera Fundación, ISFDB, StoryGraph y otras aparecen con su nombre | `https://www.goodreads.com/…` |
| `enlace` | Más información: reseñas, entrevistas. Varios, separados por `;` | `https://…` |
| `propuesta_por` | Quién la propuso (opcional) | |
| `revision` | Si tiene texto, la ficha muestra el sello «en revisión» y ese texto aparece al pasar el cursor. | |

---

## 6. Preguntas frecuentes

### No se subió la carpeta `.github`

Créala a mano: en el repositorio, **Add file → Create new file**. En el nombre escribe `.github/workflows/publicar.yml` (las barras crean las carpetas), pega el contenido de ese archivo desde tu computador y guarda con **Commit changes**. Repite con `.github/workflows/importar.yml`.

### Cambié algo y no aparece en el sitio

Revisa la pestaña **Actions**. Una ✗ roja significa que algo falló: entra en la ejecución y lee el mensaje. Lo más común es una coma sin comillas en el CSV. Si todo está en verde, recarga la página con `Ctrl + Shift + R` (o `Cmd + Shift + R` en Mac).

### ¿Cómo cambio el nombre del archivo?

En `config.yml`, edita `nombre` y `lema`. Si además quieres cambiar la dirección, cambia el nombre del repositorio en **Settings → General** y actualiza `url_sitio`.

### ¿Puedo ver el sitio en mi computador antes de publicarlo?

Sí, si tienes Python instalado:

```bash
pip install -r requirements.txt
python scripts/construir.py
```

Luego abre `_site/index.html` en el navegador.

### ¿Puedo usar un dominio propio?

Sí. En **Settings → Pages → Custom domain**. Después, actualiza `url_sitio` en `config.yml`.
