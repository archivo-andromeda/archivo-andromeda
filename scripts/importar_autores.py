#!/usr/bin/env python3
"""
Importa a datos/autores.csv las respuestas APROBADAS del formulario para autores.

Lee la pestaña publicada de la hoja de respuestas (o un .csv descargado). Solo usa
las filas en que la persona autorizó la publicación («¿Autorizas…?» empieza con «Sí»)
y que tú aprobaste (columna «Aprobada» = sí). De cada fila toma únicamente:

    nombre, pronombres, país, bio, enlaces, enlace de la foto y crédito de la foto.

El correo y las respuestas para la curaduría (correcciones, otras obras,
recomendaciones) nunca se leen ni se guardan: el repositorio es público.

· La persona tiene que estar en el archivo: su nombre debe coincidir (sin contar
  mayúsculas ni tildes) con una autoría o editorx de obras.csv, o con un nombre o una
  variante de autores.csv. Si no coincide, la fila se salta con un aviso.
· Si escribió su nombre con otras tildes o mayúsculas, se usa como lo escribió.
· Si una persona respondió varias veces, vale su última respuesta aprobada.
· Cada respuesta se importa una sola vez: la columna «formulario» de autores.csv guarda
  la marca temporal de la última respuesta importada. Así, lo que corrijas a mano en
  autores.csv no se pisa al volver a ejecutar el importador; solo una respuesta nueva
  de esa persona lo actualiza (y únicamente en los campos que respondió).
· Si la columna «id» de una persona está vacía, se escribe a partir de su nombre
  («Andrés Urrutia Ruiz» → andres-urrutia-ruiz). Es el nombre que debe tener su foto.
· La foto del enlace se descarga, se achica y queda en estatico/autores/<id>.webp.
  Las fotos subidas como archivo al formulario quedan privadas en tu Drive: el
  importador avisa cuáles hay que bajar y subir a mano.

Uso:
    python scripts/importar_autores.py "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&output=csv"
    python scripts/importar_autores.py respuestas_autores.csv
"""
from __future__ import annotations

import csv
import io
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

RAIZ = Path(__file__).resolve().parent.parent
OBRAS = RAIZ / "datos" / "obras.csv"
AUTORES = RAIZ / "datos" / "autores.csv"
FOTOS = RAIZ / "estatico" / "autores"
COLUMNAS = ["id", "nombre", "variantes", "pronombres", "pais", "bio", "enlaces", "foto_credito", "formulario"]
EXTENSIONES = (".webp", ".jpg", ".jpeg", ".png")
FOTO_ANCHO = 600
FOTO_MAX_BYTES = 15 * 1024 * 1024
SI = ("si", "s", "x", "1", "true", "verdadero", "aprobada")

# Cómo reconocer cada pregunta (por el comienzo de su texto, sin tildes ni mayúsculas).
# El orden importa: gana la primera coincidencia. Lo que no esté aquí se ignora.
PREGUNTAS = [
    ("marca", ["timestamp", "marca temporal"]),
    ("aprobada", ["aprobada"]),
    ("autoriza", ["autorizas", "autorizo", "autorizacion"]),
    ("nombre", ["nombre"]),
    ("pronombres", ["pronombre"]),
    ("pais", ["pais"]),
    ("bio", ["bio"]),
    ("foto_url", ["enlace de la foto", "enlace a la foto", "link de la foto"]),
    ("foto_credito", ["credito"]),
    ("foto_subida", ["foto"]),
    ("enlaces", ["enlaces", "redes", "links"]),
]


def clave(t: str) -> str:
    t = unicodedata.normalize("NFD", (t or "").strip().lower())
    return re.sub(r"\s+", " ", "".join(c for c in t if unicodedata.category(c) != "Mn"))


def slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", clave(t)).strip("-")


def leer_fuente(fuente: str) -> list[dict]:
    if fuente.startswith(("http://", "https://")):
        with urllib.request.urlopen(fuente, timeout=30) as r:
            texto = r.read().decode("utf-8-sig")
    else:
        texto = Path(fuente).read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(texto)))


def mapear_cabeceras(cabeceras: list[str]) -> dict[str, str]:
    mapa = {}
    for cab in cabeceras:
        c = re.sub(r"^[^a-z0-9]+", "", clave(cab))  # sin «¿» ni comillas al comienzo
        for campo, prefijos in PREGUNTAS:
            if campo in mapa.values():
                continue
            if any(c.startswith(clave(p)) for p in prefijos):
                mapa[cab] = campo
                break
    return mapa


def es_si(valor: str) -> bool:
    v = clave(valor)
    return v in SI or v.startswith("si ") or v.startswith("si,")


# Pronombres: el formulario tiene casillas «él», «ella», «elle» y «Other». Google junta las
# casillas marcadas con comas («él, elle»); aquí se unen con «/» («él/elle»). Algunas
# palabras comunes se traducen a su pronombre; lo demás (escrito en «Other») queda como vino.
PRONOMBRES = {
    "el": "él", "ella": "ella", "elle": "elle",
    "masculino": "él", "masculinos": "él",
    "femenino": "ella", "femeninos": "ella",
    "neutro": "elle", "neutros": "elle", "no binario": "elle", "no binarios": "elle",
}


def pronombres(valor: str) -> str:
    salida = []
    for p in re.split(r"[,;/]| y ", valor or ""):
        p = re.sub(r"(?i)^pronombres?\s+", "", p.strip())  # «Pronombres masculinos» → «masculinos»
        if p:
            p = PRONOMBRES.get(clave(p), p)
            if p not in salida:
                salida.append(p)
    return "/".join(salida)


def lista(valor: str, separadores: str) -> str:
    return "; ".join(p.strip() for p in re.split(separadores, valor or "") if p.strip())


def personas_del_archivo(filas_autores: list[dict]) -> dict[str, dict]:
    """{clave de nombre o variante: fila de autores.csv (existente o nueva)}."""
    indice: dict[str, dict] = {}
    for f in filas_autores:
        for n in [f.get("nombre", "")] + (f.get("variantes") or "").split(";"):
            if n.strip():
                indice[clave(n)] = f
    with open(OBRAS, encoding="utf-8-sig", newline="") as fh:
        for o in csv.DictReader(fh):
            for col in ("autoria", "editorx"):
                for n in (o.get(col) or "").split(";"):
                    if n.strip() and clave(n) not in indice:
                        indice[clave(n)] = {"nombre": n.strip(), "_nueva": True}
    return indice


def url_descargable(url: str) -> str:
    """Convierte enlaces para compartir de Google Drive en enlaces de descarga directa."""
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?(?:export=\w+&)?id=)([\w-]+)", url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return url


def foto_actual(ident: str) -> Path | None:
    return next((FOTOS / f"{ident}{e}" for e in EXTENSIONES if (FOTOS / f"{ident}{e}").exists()), None)


def descargar_foto(url: str, ident: str) -> str:
    """Descarga y achica la foto en estatico/autores/<id>.webp. Devuelve un aviso si falla."""
    if Image is None:
        return "falta Pillow para procesar la foto"
    try:
        pedido = urllib.request.Request(url_descargable(url), headers={"User-Agent": "Mozilla/5.0 (Archivo Andromeda)"})
        with urllib.request.urlopen(pedido, timeout=30) as r:
            datos = r.read(FOTO_MAX_BYTES + 1)
        if len(datos) > FOTO_MAX_BYTES:
            raise ValueError("la imagen pesa más de 15 MB")
        with Image.open(io.BytesIO(datos)) as im:
            im.load()
            if im.width > FOTO_ANCHO:
                im = im.resize((FOTO_ANCHO, round(im.height * FOTO_ANCHO / im.width)), Image.LANCZOS)
            im = im.convert("RGB")
            FOTOS.mkdir(parents=True, exist_ok=True)
            for e in EXTENSIONES:  # la foto nueva reemplaza a la anterior, tenga la extensión que tenga
                (FOTOS / f"{ident}{e}").unlink(missing_ok=True)
            im.save(FOTOS / f"{ident}.webp", "WEBP", quality=82)
        return ""
    except Exception as e:
        return f"no se pudo descargar la foto ({e}); revisa que el enlace sea público"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    respuestas = leer_fuente(sys.argv[1].strip())
    if not respuestas:
        print("La hoja está vacía.")
        return 0
    mapa = mapear_cabeceras(list(respuestas[0].keys()))
    print("Columnas reconocidas:")
    for cab, campo in mapa.items():
        print(f"  {cab[:55]!r:58} → {campo}")
    for falta in ("nombre", "autoriza"):
        if falta not in mapa.values():
            print(f"\n✗ No encontré la pregunta de «{falta}» en la hoja; no importo nada.")
            return 1
    if "aprobada" not in mapa.values():
        print("\n⚠ No encontré la columna «Aprobada». Se importarán TODAS las respuestas autorizadas.")

    if AUTORES.exists():
        with open(AUTORES, encoding="utf-8-sig", newline="") as f:
            lector = csv.reader(f)
            # Nombres de columna sin espacios alrededor (al pegar en GitHub a veces se cuelan)
            cabecera = [c.strip() for c in next(lector, [])]
            filas = [{k: (v or "").strip() for k, v in zip(cabecera, fila) if k} for fila in lector if any(fila)]
            cabecera = list(dict.fromkeys(c for c in cabecera if c))
    else:
        filas, cabecera = [], []
    cabecera += [c for c in COLUMNAS if c not in cabecera]
    indice = personas_del_archivo(filas)

    # Última respuesta aprobada de cada persona (la hoja está en orden de llegada)
    ultimas: dict[int, tuple[dict, dict]] = {}
    for r in respuestas:
        r = {campo: (r.get(cab) or "").strip() for cab, campo in mapa.items()}
        if not r.get("nombre"):
            continue
        if not es_si(r.get("autoriza", "")):
            continue
        if "aprobada" in mapa.values() and not es_si(r.get("aprobada", "")):
            continue
        persona = indice.get(clave(r["nombre"]))
        if persona is None:
            print(f"  ⚠ «{r['nombre']}» no aparece en ninguna obra del archivo: se saltó. "
                  "Si es un nombre nuevo de alguien del archivo, agrégalo en autores.csv (columna «variantes»).")
            continue
        ultimas[id(persona)] = (persona, r)

    cambios = 0
    for persona, r in ultimas.values():
        if r.get("marca") and persona.get("formulario") == r["marca"]:
            continue  # esta respuesta ya se importó antes
        if persona.pop("_nueva", False):
            filas.append(persona)
        # El nombre como la persona lo escribió, si solo cambian tildes o mayúsculas
        if clave(r["nombre"]) == clave(persona["nombre"]):
            persona["nombre"] = r["nombre"]
        ident = slug(persona.get("id") or persona["nombre"])
        hecho = []
        valores = {
            "pronombres": pronombres(r.get("pronombres", "")),
            "pais": lista(r.get("pais", ""), r"[;,]"),
            "bio": r.get("bio", ""),
            "enlaces": lista(r.get("enlaces", ""), r"[;,\s]+"),
            "foto_credito": r.get("foto_credito", ""),
        }
        for campo, valor in valores.items():
            if valor and valor != persona.get(campo, ""):
                persona[campo] = valor
                hecho.append(campo)
        foto_url = r.get("foto_url", "")
        if foto_url.startswith(("http://", "https://")):
            aviso = descargar_foto(foto_url, ident)
            if aviso:
                print(f"  ⚠ {persona['nombre']}: {aviso}.")
            else:
                hecho.append("foto")
        elif r.get("foto_subida") and not foto_actual(ident):
            print(f"  ⚠ {persona['nombre']} subió una foto al formulario: descárgala de tu Drive, "
                  f"prepárala y súbela como estatico/autores/{ident}.webp")
        persona["formulario"] = r.get("marca", "")
        cambios += 1
        print(f"  + {persona['nombre']}: " + (", ".join(hecho) if hecho else "sin datos nuevos"))

    # La id de cada persona queda escrita (como en obras.csv), para saber cómo nombrar su foto:
    # estatico/autores/<id>.webp. Una id ya escrita no se cambia, aunque cambie el nombre.
    ids_nuevas = 0
    for f in filas:
        if not f.get("id") and f.get("nombre"):
            f["id"] = slug(f["nombre"])
            ids_nuevas += 1
    if not cambios and not ids_nuevas:
        print("\nNo hay respuestas nuevas para importar.")
        return 0
    filas.sort(key=lambda f: clave(f.get("nombre", "")))
    with open(AUTORES, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cabecera, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    print(f"\n✓ {cambios} ficha(s) de autores actualizada(s) en datos/autores.csv"
          + (f"; se escribió la id de {ids_nuevas} persona(s)" if ids_nuevas else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
