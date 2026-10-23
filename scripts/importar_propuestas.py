#!/usr/bin/env python3
"""
Importa al catálogo las propuestas APROBADAS del Google Form.

Lee la hoja de respuestas (publicada como CSV, o un archivo .csv descargado),
toma solo las filas con la columna «Aprobada» = sí, y las agrega al final de
datos/obras.csv. Las obras que ya están en el catálogo (mismo título y autoría)
se saltan, así que puedes ejecutarlo varias veces sin duplicar nada.

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

RAIZ = Path(__file__).resolve().parent.parent
OBRAS = RAIZ / "datos" / "obras.csv"
COLUMNAS = ["id", "titulo", "autoria", "anio", "pais", "formato", "subgeneros", "disidencias",
            "temas", "editorial", "descripcion", "portada", "enlace", "propuesta_por", "revision"]
MULTIPLES = {"pais", "subgeneros", "disidencias", "temas", "formato"}

# Cómo reconocer cada pregunta del formulario (por el comienzo de su texto, sin tildes).
# El orden importa: «enlace a la portada» debe revisarse antes que «enlace».
PREGUNTAS = [
    ("aprobada", ["aprobada"]),
    ("titulo", ["titulo"]),
    ("autoria", ["autor"]),
    ("anio", ["ano", "año"]),
    ("pais", ["pais"]),
    ("formato", ["formato"]),
    ("subgeneros", ["subgenero"]),
    ("disidencias", ["disidencia"]),
    ("temas", ["tema"]),
    ("editorial", ["editorial"]),
    ("descripcion", ["descripcion", "resena"]),
    ("portada", ["enlace a la imagen", "enlace a la portada", "portada", "imagen"]),
    ("enlace", ["enlace", "link"]),
    ("propuesta_por", ["tu nombre", "nombre o seudonimo", "seudonimo"]),
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
        c = clave(cab)
        for campo, prefijos in PREGUNTAS:
            if campo in mapa.values():
                continue
            if any(c.startswith(clave(p)) for p in prefijos):
                mapa[cab] = campo
                break
    return mapa


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

    with open(OBRAS, encoding="utf-8-sig", newline="") as f:
        existentes = list(csv.DictReader(f))
    ya = {(clave(o["titulo"]), clave(o["autoria"])) for o in existentes}
    ids = {o["id"] for o in existentes}

    nuevas = []
    for fila in filas:
        o = {campo: (fila.get(cab) or "").strip() for cab, campo in mapa.items()}
        if tiene_aprobada and clave(o.get("aprobada", "")) not in ("si", "sí", "s", "x", "1", "true", "verdadero", "aprobada"):
            continue
        if not o.get("titulo") or not o.get("autoria"):
            continue
        if (clave(o["titulo"]), clave(o["autoria"])) in ya:
            print(f"  · ya estaba: {o['titulo']}")
            continue
        for campo in MULTIPLES:
            o[campo] = "; ".join(p.strip() for p in re.split(r"[;,]", o.get(campo, "")) if p.strip())
        base = slug(o["titulo"])
        ident, i = base, 2
        while ident in ids:
            ident, i = f"{base}-{i}", i + 1
        ids.add(ident)
        ya.add((clave(o["titulo"]), clave(o["autoria"])))
        o["id"] = ident
        o["revision"] = "Propuesta comunitaria; etiquetas por revisar."
        nuevas.append({c: o.get(c, "") for c in COLUMNAS})
        print(f"  + nueva: {o['titulo']} — {o['autoria']}")

    if not nuevas:
        print("\nNo hay obras nuevas para agregar.")
        return 0
    cabecera = list(existentes[0].keys()) if existentes else COLUMNAS
    with open(OBRAS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cabecera, extrasaction="ignore")
        w.writeheader()
        w.writerows(existentes)
        w.writerows(nuevas)
    print(f"\n✓ {len(nuevas)} obra(s) agregada(s) a datos/obras.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
