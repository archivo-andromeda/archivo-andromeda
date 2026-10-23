#!/usr/bin/env python3
"""
Construye el Archivo Andrómeda a partir de datos/obras.csv.

Uso:
    python scripts/construir.py            # enlaces que funcionan abriendo los archivos localmente
    python scripts/construir.py --limpias  # enlaces "limpios" para GitHub Pages (sin index.html)

El resultado queda en la carpeta _site/.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "_site"
LIMPIAS = "--limpias" in sys.argv

# Dimensiones de etiquetas: clave interna → (columna del CSV, nombre visible, parámetro de URL)
DIMENSIONES = {
    "subgeneros": ("subgeneros", "Subgénero", "sub"),
    "disidencias": ("disidencias", "Disidencia", "dis"),
    "formato": ("formato", "Formato", "for"),
    "pais": ("pais", "País", "pai"),
    "decada": (None, "Década", "dec"),
    "temas": ("temas", "Temas", "tem"),
}
CONTROLADAS = {"subgeneros", "disidencias", "formato"}
VOCAB_CLAVE = {"subgeneros": "subgeneros", "disidencias": "disidencias", "formato": "formatos", "temas": "temas"}

# Colores de tela para las portadas provisorias
TELAS = ["#5c1f27", "#2f4032", "#27324a", "#6b4a1f", "#4a2a44", "#23403f", "#3b2a20", "#51302a"]

avisos: list[str] = []


def clave(texto: str) -> str:
    """Normaliza para comparar: minúsculas, sin tildes, espacios simples."""
    t = unicodedata.normalize("NFD", texto.strip().lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t)


def slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", clave(texto)).strip("-")


def cargar_yaml(ruta: Path) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def mapa_alias(vocab: dict) -> dict[str, dict[str, str]]:
    """Para cada dimensión, mapea clave normalizada → forma canónica."""
    mapas = {}
    for dim, vclave in VOCAB_CLAVE.items():
        m = {}
        for canonica, info in (vocab.get(vclave) or {}).items():
            m[clave(canonica)] = canonica
            for a in (info or {}).get("alias", []) or []:
                m[clave(str(a))] = canonica
        mapas[dim] = m
    return mapas


def separar(valor: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;,]", valor or "") if p.strip()]


def normalizar(dim: str, valores: list[str], mapas, titulo: str) -> list[str]:
    salida = []
    for v in valores:
        canon = mapas.get(dim, {}).get(clave(v))
        if canon is None:
            canon = v.strip().lower() if dim in ("subgeneros", "disidencias", "temas", "formato") else v.strip()
            if dim in CONTROLADAS:
                avisos.append(f"«{titulo}»: la etiqueta «{v}» ({DIMENSIONES[dim][1]}) no está en el vocabulario.")
        if canon not in salida:
            salida.append(canon)
    return salida


def color_tela(ident: str) -> str:
    return TELAS[int(hashlib.md5(ident.encode()).hexdigest(), 16) % len(TELAS)]


def cargar_obras(mapas) -> list[dict]:
    obras, vistos = [], set()
    with open(RAIZ / "datos" / "obras.csv", encoding="utf-8-sig", newline="") as f:
        for n, fila in enumerate(csv.DictReader(f), start=2):
            fila = {k.strip(): (v or "").strip() for k, v in fila.items() if k}
            titulo = fila.get("titulo", "")
            if not titulo or not fila.get("autoria"):
                avisos.append(f"Fila {n}: falta título o autoría; se omitió.")
                continue
            ident = slug(fila.get("id") or titulo)
            base, i = ident, 2
            while ident in vistos:
                ident, i = f"{base}-{i}", i + 1
            vistos.add(ident)

            anio = fila.get("anio", "")
            decada = f"{anio[:3]}0s" if re.fullmatch(r"\d{4}", anio) else ""
            pais = separar(fila.get("pais", ""))
            portada = fila.get("portada", "")
            if portada and not portada.startswith(("http://", "https://")):
                if not (RAIZ / "estatico" / "portadas" / portada).exists():
                    avisos.append(f"«{titulo}»: no encontré la imagen estatico/portadas/{portada}.")
                portada = f"estatico/portadas/{portada}"

            obra = {
                "id": ident,
                "titulo": titulo,
                "autoria": fila.get("autoria", ""),
                "anio": anio,
                "editorial": fila.get("editorial", ""),
                "descripcion": fila.get("descripcion", ""),
                "enlace": fila.get("enlace", ""),
                "propuesta_por": fila.get("propuesta_por", ""),
                "revision": fila.get("revision", ""),
                "portada": portada,
                "portada_externa": portada.startswith("http"),
                "tela": color_tela(ident),
                "subgeneros": normalizar("subgeneros", separar(fila.get("subgeneros", "")), mapas, titulo),
                "disidencias": normalizar("disidencias", separar(fila.get("disidencias", "")), mapas, titulo),
                "formato": normalizar("formato", separar(fila.get("formato", "")), mapas, titulo),
                "temas": normalizar("temas", separar(fila.get("temas", "")), mapas, titulo),
                "pais": pais,
                "decada": [decada] if decada else [],
            }
            obra["texto"] = clave(" ".join([
                titulo, obra["autoria"], obra["editorial"], obra["descripcion"], anio,
                *obra["pais"], *obra["temas"], *obra["subgeneros"], *obra["disidencias"], *obra["formato"],
            ]))
            obras.append(obra)
    obras.sort(key=lambda o: clave(o["titulo"]))
    return obras


def facetas(obras) -> list[dict]:
    salida = []
    for dim, (_, nombre, param) in DIMENSIONES.items():
        c = Counter(v for o in obras for v in o[dim])
        if dim == "decada":
            valores = sorted(c.items(), reverse=True)
        else:
            valores = sorted(c.items(), key=lambda kv: (-kv[1], clave(kv[0])))
        salida.append({"dim": dim, "nombre": nombre, "param": param, "valores": valores})
    return salida


def leer_pagina(ruta: Path) -> tuple[dict, str]:
    texto = ruta.read_text(encoding="utf-8")
    meta = {}
    if texto.startswith("---"):
        _, cabecera, texto = texto.split("---", 2)
        meta = yaml.safe_load(cabecera) or {}
    html = markdown.markdown(texto, extensions=["extra", "smarty"])
    return meta, html


def main() -> int:
    config = cargar_yaml(RAIZ / "config.yml")
    vocab = cargar_yaml(RAIZ / "datos" / "vocabulario.yml")
    mapas = mapa_alias(vocab)
    obras = cargar_obras(mapas)
    fac = facetas(obras)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    shutil.copytree(RAIZ / "estatico", SALIDA / "estatico")
    (SALIDA / ".nojekyll").write_text("")

    env = Environment(
        loader=FileSystemLoader(RAIZ / "plantillas"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def escribir(destino: str, plantilla: str, **ctx):
        profundidad = destino.count("/")
        raiz = "../" * profundidad
        if destino == "404.html" and config.get("url_sitio"):
            # La página 404 puede aparecer en cualquier ruta: usa enlaces absolutos.
            raiz = config["url_sitio"].rstrip("/") + "/"

        def enlace(ruta: str = "") -> str:
            """Ruta relativa a una página del sitio. '' = inicio; 'obras/x/' = una ficha."""
            if ruta.startswith(("http://", "https://", "#")):
                return ruta
            ruta, _, consulta = ruta.partition("?")
            if not LIMPIAS and (ruta == "" or ruta.endswith("/")):
                ruta += "index.html"
            if LIMPIAS and ruta == "":
                ruta = "./" if not raiz else ""
            final = raiz + ruta
            return final + ("?" + consulta if consulta else "")

        def recurso(ruta: str) -> str:
            return ruta if ruta.startswith("http") else raiz + ruta

        html = env.get_template(plantilla).render(
            sitio=config, enlace=enlace, recurso=recurso, dims=DIMENSIONES,
            destino=destino, total=len(obras), **ctx,
        )
        archivo = SALIDA / destino
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(html, encoding="utf-8")

    datos_js = [
        {k: o[k] for k in ("id", "titulo", "autoria", "anio", "texto", *DIMENSIONES.keys())}
        for o in obras
    ]
    a_js = lambda d: json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    escribir("index.html", "catalogo.html", obras=obras, facetas=fac,
             datos_json=a_js(datos_js),
             params_json=a_js({d: p for d, (_, _, p) in DIMENSIONES.items()}))

    for i, o in enumerate(obras):
        anterior = obras[i - 1] if i > 0 else None
        siguiente = obras[i + 1] if i < len(obras) - 1 else None
        escribir(f"obras/{o['id']}/index.html", "ficha.html", obra=o,
                 anterior=anterior, siguiente=siguiente)

    conteos = {f["dim"]: dict(f["valores"]) for f in fac}
    escribir("vocabulario/index.html", "vocabulario.html", vocab=vocab, conteos=conteos,
             facetas=fac)

    for md in sorted((RAIZ / "paginas").glob("*.md")):
        meta, html = leer_pagina(md)
        escribir(f"{md.stem}/index.html", "pagina.html", meta=meta, contenido=html, pagina=md.stem)

    escribir("404.html", "404.html")

    print(f"✓ Sitio construido en _site/ con {len(obras)} obras.")
    if avisos:
        print(f"\n⚠ {len(avisos)} aviso(s) para revisar:")
        for a in avisos:
            print("  ·", a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
