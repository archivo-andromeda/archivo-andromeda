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
datos/autores.csv        ← pronombres, bio, país, enlaces y variantes de nombre de cada persona (opcional; a mano o desde el formulario para autores)
config.yml               ← nombre del sitio, enlace al formulario, créditos, biblioteca aliada
paginas/acerca.md        ← texto de la página «Acerca»
paginas/proponer.md      ← texto de la página «Proponer una obra»
estatico/portadas/       ← portadas, nombradas con el id de cada obra (opcional)
estatico/autores/        ← fotos de autores, nombradas con el id de cada persona (opcional)
plantillas/, estatico/   ← diseño (HTML, CSS, JS)
scripts/construir.py     ← genera el sitio a partir del CSV
scripts/importar_propuestas.py ← trae las propuestas aprobadas del formulario
scripts/importar_autores.py    ← trae las respuestas aprobadas del formulario para autores
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

Divide el formulario en **tres secciones** (botón **Add section**): «La obra» con las preguntas 1 a 8, «Datos de publicación (opcional)» con las preguntas 9 a 19 y «Para terminar» con la 20. Solo título y autore son obligatorias.

La primera sección reúne lo que más sirve que complete quien leyó la obra: el subgénero, las disidencias, los afectos, los temas y la descripción. Los datos de publicación casi siempre se pueden encontrar en línea después.

**Sección 1 · La obra**

| # | Título de la pregunta | Tipo | Obligatoria | Opciones o ayuda |
|---|---|---|---|---|
| 1 | Título de la obra | Respuesta corta | Sí | |
| 2 | Autore | Respuesta corta | Sí | *Ayuda: «Si son varias personas, sepáralas con punto y coma. Usa el nombre actual de cada persona.»* |
| 3 | Formato | Opción múltiple | | Novela · Novela corta · Libro de cuentos · Antología · Cuento · Microficción · Poemario narrativo · *Otro* |
| 4 | Subgénero especulativo | Casillas | | Ciencia ficción · Weird · Distopía · Utopía · Gótico · Ucronía · Fantasía · Horror · Ficción climática · Postapocalíptico · Poesía especulativa · *Otro* |
| 5 | Disidencias sexogenéricas representadas | Casillas | | Lésbica · Gay · Marica · Bisexual · Trans · Travesti · No binarie · Género fluido · Intersex · Asexual · Poliamor · Cuir · *Otro* |
| 6 | Afectos: ¿Qué te hizo sentir esta obra? | Casillas | | Esperanza · Agobio · Calentura · Congoja · Ternura · Mariposas · Rabia · Asco · Extrañeza · Curiosidad · Risa · *Otro* |
| 7 | Temas | Respuesta corta | | *Ayuda: «Algunas palabras clave, separadas por comas»* |
| 8 | Descripción breve | Párrafo | | |

**Sección 2 · Datos de publicación (opcional)**

| # | Título de la pregunta | Tipo | Opciones o ayuda |
|---|---|---|---|
| 9 | Publicado en | Respuesta corta | *Ayuda: «Si es un cuento o una microficción: el nombre del libro, antología, revista o sitio donde se publicó.»* |
| 10 | Año de publicación | Respuesta corta | |
| 11 | País | Respuesta corta | *Ayuda: «Si son varios, sepáralos con comas»* |
| 11b | Idioma original | Casillas | Español · Portugués · Francés · Mapudungun · Quechua · Aymara · Guaraní · Náhuatl · Maya · Creol haitiano · *Otro*. *Ayuda: «La lengua en que se escribió la obra. Si es una edición bilingüe, marca las dos.»* |
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
| 20 | Tu nombre o seudónimo (opcional) | Respuesta corta | *Ayuda: «Aparecerá en la ficha como quien propuso la obra»* |

En las preguntas de opciones, el orden de las opciones da lo mismo: el importador lee el texto. Lo que importa es que cada opción coincida con una etiqueta de `datos/vocabulario.yml` o con uno de sus alias, y que ninguna lleve comas (Google separa con comas las casillas marcadas).

La pregunta «Idioma original» (11b) se agregó después: si tu formulario ya existe, súmala con **Add question** en la sección 2, de tipo **Checkboxes**, con la opción **Other**. Su título tiene que empezar con «Idioma» (o «Lengua»).

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

### 3.4 Formulario para autores

Un segundo formulario, para que cada autore complete su propia ficha. Sus preguntas, en este orden (columnas de la hoja de respuestas):

| Col. | Pregunta | Qué pasa con la respuesta |
|---|---|---|
| A | Timestamp | Se usa para no importar dos veces la misma respuesta. |
| B | Nombre con el que quieres aparecer en el archivo | Tiene que coincidir con una autoría o editorx de `obras.csv` (o con un nombre o variante de `autores.csv`). Si solo cambian tildes o mayúsculas, se usa como la persona lo escribió. |
| C | Pronombres con los que quieres aparecer en el archivo | Columna `pronombres`. Se muestran en su página y deciden la palabra de arriba: «Autora» (ella), «Autor» (él) o «Autore» (elle, varios o ninguno). |
| D | Correo de contacto | **Nunca se publica ni llega al repositorio.** |
| E | País | Columna `pais`. |
| F | Bio breve | Columna `bio`. |
| G | Enlaces | Columna `enlaces`. |
| H | Foto para tu ficha (archivo) | Queda privada en tu Drive: el importador avisa que hay que bajarla y subirla a mano a `estatico/autores/`. |
| I | Enlace de la foto | Se descarga sola a `estatico/autores/<id>.webp`. |
| J | Crédito de la foto | Columna `foto_credito`. |
| K–M | Correcciones, otras obras, recomendaciones | **No se publican.** Léelas en la hoja. |
| N | ¿Autorizas la publicación…? | Solo se importa si la respuesta empieza con «Sí». |
| O | `Aprobada` (la agregas tú) | Solo se importa si escribes `sí`. |

**Preparar la hoja (una sola vez):**

1. En el formulario: **Responses** → **Link to Sheets** → **Create a new spreadsheet**.
2. En la hoja, escribe `Aprobada` en la celda **O1**.
3. Crea una pestaña nueva (botón **+** abajo a la izquierda) y llámala `publicar`. En su celda **A1** pega:

   ```
   =QUERY('Form Responses 1'!A:O, "select A, B, C, E, F, G, H, I, J, N, O where lower(N) starts with 's' and lower(O) matches 's[ií]'", 1)
   ```

   Esa pestaña tiene solo las columnas públicas y solo las filas autorizadas y aprobadas: **el correo y los comentarios nunca salen de la hoja**. Si más adelante agregas o cambias de lugar preguntas del formulario, revisa las letras de la fórmula.
4. Publica **solo esa pestaña**: **File → Share → Publish to web** → en lugar de **Entire document** elige `publicar` → en lugar de **Web page** elige **Comma-separated values (.csv)** → **Publish**. Copia el enlace.
5. En GitHub: **Settings → Secrets and variables → Actions → Variables → New repository variable**, con **Name** `AUTORES_CSV_URL` y el enlace como **Value**.

**Cada vez que lleguen respuestas:** revísalas en la hoja (puedes corregir erratas ahí mismo), escribe `sí` en **Aprobada** y ve a **Actions → Importar autores → Run workflow**. Lo que no se pudo importar (un nombre que no está en el archivo, una foto que hay que subir a mano) aparece como aviso ⚠ en el registro de esa ejecución.

Cada respuesta se importa una sola vez (la columna `formulario` de `autores.csv` guarda su marca temporal; no la edites). Así, lo que corrijas a mano en `autores.csv` no se pisa al volver a ejecutar el importador. Si la persona responde de nuevo, vale su respuesta más reciente, y solo en los campos que contestó.

---

## 4. El día a día: curar y publicar

### Aprobar propuestas del formulario

1. Abre la hoja de respuestas y revisa las propuestas nuevas.
2. Para aprobar una, escribe `sí` en su columna **Aprobada**. Si quieres, corrige ahí mismo errores de tipeo.
3. En GitHub, ve a **Actions → Importar propuestas → Run workflow → Run workflow**.
4. En uno o dos minutos las obras aprobadas aparecen en `datos/obras.csv` y en el sitio, como fichas **nuevas** (con el sello **«en revisión»**).

El importador nunca duplica: si una obra ya está en el catálogo (mismo título y autoría), la salta. Ten en cuenta que Google puede tardar unos 5 minutos en actualizar la hoja publicada.

Por eso las respuestas que llegan desde el botón **«Ayúdanos a completarla»** de las fichas (ver «Estados de las fichas») no crean fichas repetidas: llegan a la misma hoja con el título y le autore de una obra que ya existe, y el importador las salta. Revísalas en la hoja y pasa a mano a `obras.csv` lo que sirva (por ejemplo, los afectos o una descripción).

### Editar el catálogo directamente

**Opción A, en GitHub (cambios pequeños):** abre `datos/obras.csv`, pulsa el lápiz ✏️, edita y guarda con **Commit changes**. Los textos que tengan comas deben ir entre comillas: `"La lesbiana, el oso y el ponqué"`.

**Opción B, en una planilla (cambios grandes):** descarga `obras.csv` (botón ⬇️), ábrelo en Google Sheets, LibreOffice o Excel, edítalo y expórtalo como **CSV UTF-8**. Luego súbelo al repositorio en la carpeta `datos/` (**Add file → Upload files**) reemplazando el anterior.

> En Excel, usa *Guardar como → CSV UTF-8 (delimitado por comas)*. El «CSV» común puede romper las tildes.

### Estados de las fichas

Cada ficha tiene uno de tres estados, que escribes en la columna `estado`:

| Estado | Qué significa | Qué pide como mínimo | Qué se ve en el sitio |
|---|---|---|---|
| `nueva` (o vacío) | Recién ingresada: los datos vienen de la propuesta, de la editorial o de reseñas. | Nada | Sello **«en revisión»** en la ficha y en la tarjeta del catálogo, y la invitación a completarla |
| `revisada` | Ya la revisaste tú: datos de publicación, portada, sinopsis y etiquetas en orden. | Autore, portada, sinopsis o descripción (a cuentos y microficciones no se les pide), formato, año, país, al menos un subgénero y al menos una disidencia | La invitación a completarla |
| `completa` | Tiene además la mirada de alguien que la leyó. | Lo de «revisada», más una descripción propia del archivo y al menos un afecto | Nada extra |

- Si marcas una ficha como `revisada` o `completa` y le falta algo de lo mínimo, el sitio te avisa en **Actions → Publicar sitio** (la ficha igual se publica).
- La **invitación a completarla** aparece al final de las fichas nuevas y revisadas, dice qué le falta (lo calcula el sitio) y lleva al formulario con el título y le autore ya escritos. Ese enlace está en `config.yml` (`completar_url`).
- La columna `revision` queda para tus notas de trabajo: en las fichas nuevas aparecen al pasar el cursor sobre el sello «en revisión»; en las demás no se muestran.
- El catálogo tiene el filtro **«Estado de la ficha»**, útil para quien quiera ayudar a completar fichas.

Solo las fichas revisadas y completas participan en la **obra del día** de la portada. El sitio elige una cada día (a medianoche, hora de Chile) y la muestra igual a todo el mundo; si no hay ninguna, el bloque no aparece.

### Obras relacionadas

Cada ficha muestra hasta 3 obras relacionadas, calculadas solas al publicar. Suman puntos la misma autoría (5), cada disidencia compartida (3), cada subgénero y cada tema compartido (2), cada afecto compartido (1), el mismo país (1) y la misma década (1); se muestran las que tienen 4 puntos o más, con lo que comparten. Los pesos se cambian al comienzo de `scripts/construir.py` (`PESOS_RELACION`, `RELACIONADAS_MAX`, `RELACIONADAS_MINIMO`).

### Agregar portadas

La portada de cada obra es la imagen de `estatico/portadas/` que se llama como su `id`: la de `las-indignas` es `estatico/portadas/las-indignas.webp` (también sirven `.jpg`, `.jpeg` y `.png`). **No hay que anotarla en `obras.csv`:** si el archivo existe, aparece en la ficha y en el catálogo al publicar.

- **Prepárala antes de subirla.** Todo lo que se sube queda para siempre en el historial del repositorio, aunque después se borre. Con [Squoosh](https://squoosh.app): arrastra la imagen; si mide más de 600 px de ancho, activa **Resize** y escribe `600` en **Width** (si mide menos, déjala así: agrandarla no agrega detalle); elige **WebP** con **Quality** en 80, descárgala y renómbrala con el `id`.
- **Desde la web:** entra a `estatico/portadas/`, pulsa **Add file → Upload files**, arrastra las imágenes y pulsa **Commit changes**.
- **Con GitHub Desktop:** pulsa **Fetch origin** (y **Pull origin**, si aparece). Abre tu copia con **Repository → Show in Finder** (o **Show in Explorer**), copia las imágenes en `estatico/portadas/`, revisa la lista en **Changes**, escribe un resumen en **Summary** y pulsa **Commit to main** y después **Push origin**.
- **Para cambiarla,** sube otra con el mismo nombre: reemplaza a la anterior. Si cambias el `id` de una obra, cambia también el nombre de su imagen.
- **Desde el formulario:** si la propuesta trae un enlace a la imagen, el importador la descarga, la achica y la guarda sola como `estatico/portadas/<id>.webp`. Si no puede, anota el enlace en la columna `revision` para que la subas a mano.
- **Sin imagen,** el sitio dibuja una portada provisoria. Un cuento sin portada usa la del libro donde se publicó, si está en el archivo.

Al publicar, el registro de **Actions → Publicar sitio** avisa si alguna imagen no coincide con ninguna obra (por ejemplo, por un error de tipeo en el nombre). Las imágenes de más de 600 px de ancho se achican en el sitio publicado; el archivo del repositorio no se toca.

### Cuentos sueltos y «publicado en»

Un cuento o una microficción se cataloga como cualquier obra, con formato `cuento` o `microficción` y la columna `publicado_en`:

- Si `publicado_en` es el **`id` o el título de una ficha del archivo** (por ejemplo, `ciencia-ficcion-travesti`), el cuento y el libro se enlazan en ambos sentidos: la ficha del libro muestra «Cuentos de este libro en el archivo». Esos cuentos **no aparecen en el catálogo por defecto**; se ven al filtrar por formato «cuento», al buscar su título o desde la ficha del libro.
- Si es **otro nombre** (una antología que no está entera en el archivo, una revista, un blog), el cuento aparece en el catálogo como cualquier obra. Al hacer clic en ese nombre se ven todas las obras publicadas en el mismo lugar.

### Autoras, autores y nombres

- Varias personas en `autoria` o `editorx` se separan con `;`.
- Usa siempre el **nombre actual** de cada persona. Si una obra se publicó con otro nombre, o una persona aparece escrita de formas distintas, agrégala a `datos/autores.csv` con sus `variantes` (separadas por `;`): el sitio agrupa todo bajo el nombre actual y **nunca muestra las variantes** ni las usa en el buscador.
- Cada persona que aparece en `autoria` o `editorx` tiene su página en `autores/<id>/`, con sus obras (los cuentos de un libro suyo van dentro del bloque del libro), lo que hizo como editorx y las disidencias, subgéneros y afectos que recorren su obra. Su nombre en la ficha de una obra enlaza a esa página. La página `autores/` (menú «Autores») las reúne todas en orden alfabético por nombre de pila.
- `autores.csv` es opcional: sirve para completar esas páginas, a mano o con el formulario para autores (ver 3.4). Columnas: `id`, `nombre`, `variantes`, `pronombres`, `pais`, `bio`, `enlaces`, `foto_credito`, `formulario`.
  - `pronombres`: como la persona los escribe (`ella`, `él/lo`, `elle`…). Se muestran en su página; con «ella» dice «Autora», con «él» dice «Autor» y en los demás casos «Autore».
  - `formulario`: la llena el importador; no la edites.
  - `id`: déjalo vacío para que se cree a partir del nombre (`Andrea Chapela` → `andrea-chapela`).
  - `pais`: el de la persona (no se toma de sus obras). Si está vacío, no se muestra.
  - `bio`: cada salto de línea dentro de la celda es un párrafo nuevo. Se puede usar `*cursiva*` para los títulos. Si está vacía, la página dice «Bio por completar».
  - `enlaces`: web, redes, entrevistas, separados por `;`.
- **Fotos:** la foto de cada persona es la imagen de `estatico/autores/` que se llama como su `id` (`estatico/autores/andrea-chapela.webp`), igual que las portadas, y se prepara de la misma forma con Squoosh. Pídela a la persona o a su editorial, y anota quién la tomó en `foto_credito` (se muestra como «Foto: …»). Sin foto, la página muestra sus iniciales.

### Biblioteca aliada (Centro RARA)

- En `obras.csv`, la columna `biblioteca` marca las obras que tiene la biblioteca. Lleva el **enlace a la ficha de la obra** en el sitio de la biblioteca o, si todavía no tiene ficha, **`sí`** (entonces el botón usa el enlace general de `config.yml`). Vacía = no la tiene.
- Las obras marcadas muestran el botón **«Pedir copia en Centro RARA»** junto al título, y el catálogo suma el filtro **Biblioteca RARA** (disponible / no disponible). El filtro aparece solo cuando hay al menos una obra marcada.
- El nombre, el texto del botón, la nota bajo el botón y el enlace general están en la sección `biblioteca` de `config.yml`. Si se borra esa sección, el botón y el filtro desaparecen.

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
| `idioma` | Del vocabulario: la lengua en que se escribió la obra (en la ficha, «Idioma original»). Si es bilingüe, las dos, separadas por `;`. El filtro del catálogo aparece cuando hay al menos dos idiomas | `español` |
| `formato` | Del vocabulario: novela, novela corta, libro de cuentos, antología, cuento, microficción, poemario narrativo | `novela` |
| `medio` | Del vocabulario: editorial, autopublicación, editorial cartonera, fanzine, plaquette, revista impresa, revista en línea, blog o web personal, redes sociales | `editorial` |
| `publicado_en` | Para cuentos: el `id` o título de un libro del archivo, o el nombre de la antología, revista o web | `ciencia-ficcion-travesti` |
| `subgeneros` | Varios, separados por `;` | `distopía; gótico` |
| `disidencias` | Varios, separados por `;` | `lésbica` |
| `afectos` | Del vocabulario: lo que la obra le hizo sentir a quien la leyó. Varios, separados por `;` | `ternura; rabia` |
| `temas` | Libres, separados por `;` | `religión; cuerpo; memoria` |
| `editorial` | | `Alfaguara` |
| `descripcion` | Texto propio del archivo sobre la obra. Cada salto de línea es un párrafo | |
| `sinopsis` | La sinopsis de la contraportada, copiada tal cual. Aparece bajo la descripción, con el nombre de la editorial como fuente | |
| `conseguir` | Dónde conseguirla, de preferencia la página de la editorial. Varios, separados por `;` | `https://…` |
| `leer_en_linea` | Enlace para leerla gratis en internet. Aparece como botón destacado | `https://…` |
| `biblioteca` | Si la tiene la biblioteca aliada: el enlace a su ficha allá, o `sí` (ver «Biblioteca aliada») | `sí` |
| `referencias` | Fichas en bases de datos de libros, separadas por `;`. Goodreads, Tercera Fundación, ISFDB, StoryGraph y otras aparecen con su nombre | `https://www.goodreads.com/…` |
| `enlace` | Más información: reseñas, entrevistas. Varios, separados por `;` | `https://…` |
| `propuesta_por` | Quién la propuso (opcional). Aparece al final de la ficha: «Obra propuesta por…» | |
| `estado` | `nueva` (o vacío), `revisada` o `completa` (ver «Estados de las fichas») | `revisada` |
| `revision` | Notas de trabajo. En las fichas nuevas aparecen al pasar el cursor sobre el sello «en revisión» | `Año según la prensa` |

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
