#!/usr/bin/env python3
"""
Importa al catálogo las propuestas APROBADAS del Google Form.

Lee la hoja de respuestas (publicada como CSV, o un archivo .csv descargado),
toma solo las filas con la columna «Aprobada» = sí, y las agrega al final de
datos/obras.csv. Las obras que ya están en el catálogo (mismo título y autoría)
se saltan, así que puedes ejecutarlo varias veces sin duplicar nada.

Si la propuesta trae un enlace a la imagen de portada, la descarga, la achica
y la guarda en estatico/portadas/<id>.webp, donde el sitio la encuentra sola.
Si no puede, anota el enlace en la columna «revision» de la obra.

Uso:
    python scripts/importar_propuestas.py "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv"
    python scripts/importar_propuestas.py respuestas.csv
"""
from __future__ import annotations

import csv
import io
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

import yaml

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

RAIZ = Path(__file__).resolve().parent.parent
OBRAS = RAIZ / "datos" / "obras.csv"
PORTADAS = RAIZ / "estatico" / "portadas"
COLUMNAS = ["id", "titulo", "autoria", "editorx", "anio", "pais", "formato", "medio", "publicado_en",
            "subgeneros", "disidencias", "afectos", "temas", "editorial", "descripcion",
            "conseguir", "leer_en_linea", "referencias", "enlace", "propuesta_por", "revision"]
MULTIPLES = {"pais", "subgeneros", "disidencias", "afectos", "temas", "formato", "medio"}   # separados por ; o ,
PERSONAS = {"autoria", "editorx"}                                                 # separados por ; o ,
ENLACES = {"donde", "referencias", "enlace"}                                     # separados por ; , o espacios

PORTADA_ANCHO = 600
PORTADA_MAX_BYTES = 15 * 1024 * 1024

# Cómo reconocer cada pregunta del formulario (por el comienzo de su texto, sin tildes).
# El orden importa: se revisa de arriba hacia abajo y gana la primera coincidencia.
PREGUNTAS = [
    ("aprobada", ["aprobada"]),
    ("titulo", ["titulo"]),
    ("autoria", ["autor"]),
    ("editorx", ["editorx", "edicion o compil", "compil"]),
    ("anio", ["ano", "año"]),
    ("pais", ["pais"]),
    ("formato", ["formato"]),
    ("medio", ["medio"]),
    ("publicado_en", ["publicado en", "publicada en", "publicado"]),
    ("subgeneros", ["subgenero"]),
    ("disidencias", ["disidencia"]),
    ("afectos", ["afecto", "que te hizo sentir"]),
    ("temas", ["tema"]),
    ("editorial", ["editorial"]),
    ("descripcion", ["descripcion", "resena"]),
    ("portada", ["enlace a la imagen", "enlace a la portada", "portada", "imagen"]),
    ("donde", ["donde conseguir", "donde leer", "donde"]),
    ("referencias", ["referencias", "goodreads", "fichas en"]),
    ("enlace", ["otros enlaces", "enlace", "link"]),
    ("propuesta_por", ["tu nombre", "nombre o seudonimo", "seudonimo"]),
]


def clave(t: str) -> str:
    t = unicodedata.normalize("NFD", (t or "").strip().lower())
    return re.sub(r"\s+", " ", "".join(c for c in t if unicodedata.category(c) != "Mn"))


def slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", clave(t)).strip("-")


def medios_en_linea() -> set[str]:
    """Medios marcados con «en_linea: true» en el vocabulario (con sus alias)."""
    with open(RAIZ / "datos" / "vocabulario.yml", encoding="utf-8") as f:
        vocab = yaml.safe_load(f) or {}
    salida = set()
    for nombre, info in (vocab.get("medios") or {}).items():
        info = info or {}
        if info.get("en_linea"):
            salida.add(clave(nombre))
            salida.update(clave(str(a)) for a in info.get("alias", []) or [])
    return salida


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
        c = clave(cab)
        for campo, prefijos in PREGUNTAS:
            if campo in mapa.values():
                continue
            if any(c.startswith(clave(p)) for p in prefijos):
                mapa[cab] = campo
                break
    return mapa


def url_descargable(url: str) -> str:
    """Convierte enlaces para compartir de Google Drive en enlaces de descarga directa."""
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=)([\w-]+)", url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return url


def descargar_portada(url: str, ident: str) -> str:
    """Descarga y achica una portada en estatico/portadas/<id>.webp. Devuelve un aviso si falla."""
    if Image is None:
        return f"No se pudo procesar la portada (falta Pillow); súbela a mano desde {url}"
    try:
        pedido = urllib.request.Request(url_descargable(url), headers={"User-Agent": "Mozilla/5.0 (Archivo Andromeda)"})
        with urllib.request.urlopen(pedido, timeout=30) as r:
            datos = r.read(PORTADA_MAX_BYTES + 1)
        if len(datos) > PORTADA_MAX_BYTES:
            raise ValueError("la imagen pesa más de 15 MB")
        with Image.open(io.BytesIO(datos)) as im:
            im.load()
            if im.width > PORTADA_ANCHO:
                im = im.resize((PORTADA_ANCHO, round(im.height * PORTADA_ANCHO / im.width)), Image.LANCZOS)
            im = im.convert("RGB")
            PORTADAS.mkdir(parents=True, exist_ok=True)
            im.save(PORTADAS / f"{ident}.webp", "WEBP", quality=82)
        return ""
    except Exception as e:
        return f"No se pudo descargar la portada ({e}); revisa el enlace: {url}"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    filas = leer_fuente(sys.argv[1].strip())
    if not filas:
        print("La hoja está vacía.")
        return 0
    mapa = mapear_cabeceras(list(filas[0].keys()))
    print("Columnas reconocidas:")
    for cab, campo in mapa.items():
        print(f"  {cab!r:55} → {campo}")
    tiene_aprobada = "aprobada" in mapa.values()
    if not tiene_aprobada:
        print("\n⚠ No encontré la columna «Aprobada». Se importarán TODAS las filas.")
    en_linea = medios_en_linea()

    with open(OBRAS, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        existentes = list(lector)
        cabecera = list(lector.fieldnames or [])
    # Columnas nuevas que el CSV todavía no tenga se agregan al final
    cabecera += [c for c in COLUMNAS if c not in cabecera]
    ya = {(clave(o["titulo"]), clave(o["autoria"])) for o in existentes}
    ids = {o["id"] for o in existentes}

    nuevas = []
    for fila in filas:
        o = {campo: (fila.get(cab) or "").strip() for cab, campo in mapa.items()}
        if tiene_aprobada and clave(o.get("aprobada", "")) not in ("si", "s", "x", "1", "true", "verdadero", "aprobada"):
            continue
        if not o.get("titulo") or not o.get("autoria"):
            continue
        for campo in MULTIPLES | PERSONAS:
            o[campo] = "; ".join(p.strip() for p in re.split(r"[;,]", o.get(campo, "")) if p.strip())
        for campo in ENLACES:
            o[campo] = "; ".join(p for p in re.split(r"[;,\s]+", o.get(campo, "")) if p)
        if (clave(o["titulo"]), clave(o["autoria"])) in ya:
            print(f"  · ya estaba: {o['titulo']}")
            continue

        # «Dónde conseguirla o leerla»: si el medio es en línea, es lectura en línea
        donde = o.pop("donde", "")
        if donde:
            if any(clave(m) in en_linea for m in o.get("medio", "").split(";")):
                o["leer_en_linea"] = donde
            else:
                o["conseguir"] = donde

        base = slug(o["titulo"])
        ident, i = base, 2
        while ident in ids:
            ident, i = f"{base}-{i}", i + 1
        ids.add(ident)
        ya.add((clave(o["titulo"]), clave(o["autoria"])))
        o["id"] = ident

        notas = ["Propuesta comunitaria; etiquetas por revisar."]
        portada = ""
        url_portada = o.pop("portada", "")
        if url_portada.startswith(("http://", "https://")):
            aviso = descargar_portada(url_portada, ident)
            if aviso:
                notas.append(aviso)
            else:
                portada = f"{ident}.webp"
        o["revision"] = " ".join(notas)
        nuevas.append({c: o.get(c, "") for c in cabecera})
        print(f"  + nueva: {o['titulo']} — {o['autoria']}" + (f"  (portada: {portada})" if portada else ""))

    if not nuevas:
        print("\nNo hay obras nuevas para agregar.")
        return 0
    with open(OBRAS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cabecera, extrasaction="ignore")
        w.writeheader()
        w.writerows(existentes)
        w.writerows(nuevas)
    print(f"\n✓ {len(nuevas)} obra(s) agregada(s) a datos/obras.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
