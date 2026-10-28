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

try:  # Pillow es opcional: sin él, las portadas se publican sin achicar.
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "_site"
LIMPIAS = "--limpias" in sys.argv

# Dimensiones de etiquetas: clave interna → (columna del CSV, nombre visible, parámetro de URL)
DIMENSIONES = {
    "subgeneros": ("subgeneros", "Subgénero", "sub"),
    "disidencias": ("disidencias", "Disidencia", "dis"),
    "afectos": ("afectos", "Afecto", "afe"),
    "formato": ("formato", "Formato", "for"),
    "medio": ("medio", "Medio", "med"),
    "pais": ("pais", "País", "pai"),
    "decada": (None, "Década", "dec"),
    "temas": ("temas", "Temas", "tem"),
}
CONTROLADAS = {"subgeneros", "disidencias", "afectos", "formato", "medio"}
VOCAB_CLAVE = {"subgeneros": "subgeneros", "disidencias": "disidencias", "afectos": "afectos", "formato": "formatos",
               "medio": "medios", "temas": "temas"}
PARAM_PUBLICACION = "pub"  # ?pub=… muestra lo publicado en una misma antología, revista o web

# Bases de datos de libros que se reconocen en la columna «referencias»
BASES = {
    "goodreads.com": "Goodreads",
    "tercerafundacion.net": "Tercera Fundación",
    "isfdb.org": "ISFDB",
    "thestorygraph.com": "StoryGraph",
    "openlibrary.org": "Open Library",
    "librarything.com": "LibraryThing",
    "sf-encyclopedia.com": "SF Encyclopedia",
    "wikidata.org": "Wikidata",
}

# Obras relacionadas: puntos por cada coincidencia, cuántas mostrar y puntaje mínimo
PESOS_RELACION = {"autoria": 5, "disidencias": 3, "subgeneros": 2, "temas": 2, "afectos": 1, "pais": 1, "decada": 1}
RELACIONADAS_MAX = 3
RELACIONADAS_MINIMO = 4

# Ancho máximo (en píxeles) de las portadas publicadas
PORTADA_ANCHO = 600

# Colores de tela para las portadas provisorias
TELAS = ["#3a1f4d", "#1f2a4f", "#4a1d3f", "#22344a", "#2d2350", "#173b45", "#3d2140", "#26264a"]

avisos: list[str] = []


def clave(texto: str) -> str:
    """Normaliza para comparar: minúsculas, sin tildes, espacios simples."""
    t = unicodedata.normalize("NFD", (texto or "").strip().lower())
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
    """Etiquetas: separadas por «;» o «,»."""
    return [p.strip() for p in re.split(r"[;,]", valor or "") if p.strip()]


def separar_pc(valor: str) -> list[str]:
    """Personas y enlaces: separados solo por «;»."""
    return [p.strip() for p in (valor or "").split(";") if p.strip()]


def unir_personas(nombres: list[str]) -> str:
    if len(nombres) <= 1:
        return "".join(nombres)
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


def normalizar(dim: str, valores: list[str], mapas, titulo: str) -> list[str]:
    salida = []
    for v in valores:
        canon = mapas.get(dim, {}).get(clave(v))
        if canon is None:
            canon = v.strip() if dim == "pais" else v.strip().lower()
            if dim in CONTROLADAS:
                avisos.append(f"«{titulo}»: la etiqueta «{v}» ({DIMENSIONES[dim][1]}) no está en el vocabulario.")
        if canon not in salida:
            salida.append(canon)
    return salida


def color_tela(ident: str) -> str:
    return TELAS[int(hashlib.md5(ident.encode()).hexdigest(), 16) % len(TELAS)]


def dominio(url: str) -> str:
    partes = url.split("/")
    return partes[2].lower().removeprefix("www.") if len(partes) > 2 else url


def enlaces(valor: str, titulo: str, columna: str, nombrar_bases: bool = False) -> list[dict]:
    """Lista de enlaces separados por «;» → [{url, etiqueta}]."""
    salida = []
    for url in separar_pc(valor):
        if not url.startswith(("http://", "https://")):
            avisos.append(f"«{titulo}»: en «{columna}», «{url}» no parece un enlace (debe empezar con https://).")
            continue
        dom = dominio(url)
        etiqueta = dom
        if nombrar_bases:
            etiqueta = next((n for d, n in BASES.items() if dom == d or dom.endswith("." + d)), dom)
        salida.append({"url": url, "etiqueta": etiqueta})
    return salida


# ── Personas ─────────────────────────────────────────────────

def cargar_autores() -> tuple[dict[str, str], dict[str, dict]]:
    """Lee datos/autores.csv (opcional).

    Devuelve (nombre_actual_por_clave, ficha_por_nombre). Las variantes sirven solo
    para agrupar obras bajo el nombre actual: nunca se muestran ni se usan en el buscador.
    """
    ruta = RAIZ / "datos" / "autores.csv"
    actual, fichas = {}, {}
    if not ruta.exists():
        return actual, fichas
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f):
            fila = {k.strip(): (v or "").strip() for k, v in fila.items() if k}
            nombre = fila.get("nombre", "")
            if not nombre:
                continue
            actual[clave(nombre)] = nombre
            for v in separar_pc(fila.get("variantes", "")):
                actual[clave(v)] = nombre
            fichas[nombre] = {
                "id": slug(fila.get("id") or nombre),
                "nombre": nombre,
                "pais": separar(fila.get("pais", "")),
                "bio": fila.get("bio", ""),
                "enlaces": enlaces(fila.get("enlaces", ""), nombre, "enlaces"),
            }
    return actual, fichas


def personas(valor: str, actual: dict[str, str]) -> list[dict]:
    salida = []
    for n in separar_pc(valor):
        nombre = actual.get(clave(n), n)
        if nombre not in (p["nombre"] for p in salida):
            salida.append({"nombre": nombre, "id": slug(nombre)})
    return salida


# ── Obras ────────────────────────────────────────────────────

def cargar_obras(mapas, actual) -> list[dict]:
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
            portada = fila.get("portada", "")
            if portada and not portada.startswith(("http://", "https://")):
                if not (RAIZ / "estatico" / "portadas" / portada).exists():
                    avisos.append(f"«{titulo}»: no encontré la imagen estatico/portadas/{portada}.")
                portada = f"estatico/portadas/{portada}"

            autoras = personas(fila.get("autoria", ""), actual)
            editorxs = personas(fila.get("editorx", ""), actual)
            obra = {
                "id": ident,
                "titulo": titulo,
                "autoras": autoras,
                "autoria": unir_personas([p["nombre"] for p in autoras]),
                "editorxs": editorxs,
                "editorx": unir_personas([p["nombre"] for p in editorxs]),
                "anio": anio,
                "editorial": fila.get("editorial", ""),
                "descripcion": fila.get("descripcion", ""),
                "publicado_en": fila.get("publicado_en", ""),
                "conseguir": enlaces(fila.get("conseguir", ""), titulo, "conseguir"),
                "leer_en_linea": enlaces(fila.get("leer_en_linea", ""), titulo, "leer_en_linea"),
                "referencias": enlaces(fila.get("referencias", ""), titulo, "referencias", nombrar_bases=True),
                "enlace": enlaces(fila.get("enlace", ""), titulo, "enlace"),
                "propuesta_por": fila.get("propuesta_por", ""),
                "revision": fila.get("revision", ""),
                "portada": portada,
                "portada_externa": portada.startswith("http"),
                "portada_heredada": False,
                "tela": color_tela(ident),
                "subgeneros": normalizar("subgeneros", separar(fila.get("subgeneros", "")), mapas, titulo),
                "disidencias": normalizar("disidencias", separar(fila.get("disidencias", "")), mapas, titulo),
                "afectos": normalizar("afectos", separar(fila.get("afectos", "")), mapas, titulo),
                "formato": normalizar("formato", separar(fila.get("formato", "")), mapas, titulo),
                "medio": normalizar("medio", separar(fila.get("medio", "")), mapas, titulo),
                "temas": normalizar("temas", separar(fila.get("temas", "")), mapas, titulo),
                "pais": normalizar("pais", separar(fila.get("pais", "")), mapas, titulo),
                "decada": [decada] if decada else [],
                # Se completan en enlazar_publicaciones()
                "contenedor": None, "contenidos": [], "oculta": False,
                "pub": "", "pub_nombre": "",
            }
            obras.append(obra)
    obras.sort(key=lambda o: clave(o["titulo"]))
    return obras


def enlazar_publicaciones(obras: list[dict]) -> None:
    """Conecta cada cuento con el libro, revista o web donde se publicó.

    Si «publicado_en» coincide con el id o el título de una ficha del archivo,
    se enlazan en ambos sentidos y el cuento se oculta del catálogo por defecto
    (aparece al filtrar por su formato y en la ficha del libro).

    Excepción: si el libro no tiene disidencias propias y alguno de sus cuentos sí
    (un libro con un solo cuento LGBTQ+, por ejemplo), se rota: se esconde el libro
    y se muestran sus cuentos.
    """
    por_id = {o["id"]: o for o in obras}
    por_titulo = {clave(o["titulo"]): o for o in obras}
    for o in obras:
        valor = o["publicado_en"]
        if not valor:
            continue
        cont = por_id.get(slug(valor)) or por_titulo.get(clave(valor))
        if cont is o:
            avisos.append(f"«{o['titulo']}»: «publicado_en» apunta a la misma obra.")
            cont = None
        if cont:
            o["contenedor"] = cont
            o["oculta"] = True
            o["pub"], o["pub_nombre"] = cont["id"], cont["titulo"]
            cont["contenidos"].append(o)
            if not o["portada"] and cont["portada"]:
                o.update(portada=cont["portada"], portada_externa=cont["portada_externa"],
                         portada_heredada=True)
        else:
            o["pub"], o["pub_nombre"] = slug(valor), valor

    for o in obras:
        if o["contenidos"] and not o["disidencias"] and any(c["disidencias"] for c in o["contenidos"]):
            o["oculta"] = True
            for c in o["contenidos"]:
                c["oculta"] = False

    for o in obras:
        o["contenidos"].sort(key=lambda c: (c["anio"] or "9999", clave(c["titulo"])))
        breves = all(set(c["formato"]) & {"cuento", "microficción"} for c in o["contenidos"])
        o["contenidos_nombre"] = "Cuentos" if breves else "Textos"
        # Etiquetas que aportan sus cuentos y que el libro no tiene ya
        o["etiquetas_contenidos"] = {
            d: [v for v in dict.fromkeys(v for c in o["contenidos"] for v in c[d]) if v not in o[d]]
            for d in ("disidencias", "subgeneros")
        }
        o["texto"] = clave(" ".join([
            o["titulo"], o["autoria"], o["editorx"], o["editorial"], o["descripcion"], o["anio"],
            o["pub_nombre"], *o["pais"], *o["temas"], *o["subgeneros"], *o["disidencias"], *o["afectos"],
            *o["formato"], *o["medio"],
        ]))
        # Lo que basta para encontrar una obra oculta escribiendo su nombre
        o["texto_corto"] = clave(" ".join([o["titulo"], o["autoria"]]))


def relacionar(obras: list[dict]) -> None:
    """Calcula hasta RELACIONADAS_MAX obras relacionadas para cada ficha.

    Suma puntos por autoría, disidencias, subgéneros, temas y afectos compartidos, país y década.
    No relaciona un cuento con su propio libro ni cuentos del mismo libro entre sí
    (eso ya aparece en «Cuentos de este libro»).
    """
    def familia(o):
        return o["contenedor"]["id"] if o["contenedor"] else o["id"]

    for o in obras:
        personas_o = {p["id"] for p in o["autoras"]}
        candidatas = []
        for c in obras:
            if c is o or familia(c) == familia(o):
                continue
            comparte, puntos = [], 0
            if personas_o & {p["id"] for p in c["autoras"]}:
                puntos += PESOS_RELACION["autoria"]
                comparte.append("autore")
            for d in ("disidencias", "subgeneros", "temas", "afectos"):
                comunes = [v for v in o[d] if v in c[d]]
                puntos += PESOS_RELACION[d] * len(comunes)
                comparte += comunes
            for d in ("pais", "decada"):
                comunes = [v for v in o[d] if v in c[d]]
                if comunes:
                    puntos += PESOS_RELACION[d]
                    comparte += [f"años {v[:4]}" if d == "decada" else v for v in comunes]
            if puntos >= RELACIONADAS_MINIMO:
                cercania = abs(int(o["anio"] or 0) - int(c["anio"] or 0)) if (o["anio"] + c["anio"]).isdigit() else 999
                candidatas.append((-puntos, cercania, clave(c["titulo"]), c, comparte))
        candidatas.sort(key=lambda x: x[:3])
        o["relacionadas"] = [{"obra": c, "comparte": comparte}
                             for *_, c, comparte in candidatas[:RELACIONADAS_MAX]]


def facetas(obras) -> list[dict]:
    salida = []
    for dim, (_, nombre, param) in DIMENSIONES.items():
        c = Counter(v for o in obras if not o["oculta"] or dim == "formato" for v in o[dim])
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


def achicar_portadas(carpeta: Path) -> None:
    """Reduce en _site/ las portadas más anchas que PORTADA_ANCHO (el original no se toca)."""
    if Image is None or not carpeta.exists():
        return
    for ruta in carpeta.iterdir():
        if ruta.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        try:
            with Image.open(ruta) as im:
                if im.width <= PORTADA_ANCHO:
                    continue
                alto = round(im.height * PORTADA_ANCHO / im.width)
                chica = im.resize((PORTADA_ANCHO, alto), Image.LANCZOS)
                if ruta.suffix.lower() in (".jpg", ".jpeg"):
                    chica.convert("RGB").save(ruta, quality=85, optimize=True, progressive=True)
                elif ruta.suffix.lower() == ".webp":
                    chica.save(ruta, quality=82)
                else:
                    chica.save(ruta, optimize=True)
        except Exception as e:  # una imagen dañada no debe detener la publicación
            avisos.append(f"No pude achicar la portada {ruta.name}: {e}")


def main() -> int:
    config = cargar_yaml(RAIZ / "config.yml")
    vocab = cargar_yaml(RAIZ / "datos" / "vocabulario.yml")
    mapas = mapa_alias(vocab)
    actual, _fichas_autores = cargar_autores()  # las fichas de autores vendrán después
    obras = cargar_obras(mapas, actual)
    enlazar_publicaciones(obras)
    relacionar(obras)
    fac = facetas(obras)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    shutil.copytree(RAIZ / "estatico", SALIDA / "estatico", ignore=shutil.ignore_patterns(".gitkeep"))
    achicar_portadas(SALIDA / "estatico" / "portadas")
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
            param_pub=PARAM_PUBLICACION, destino=destino, total=len(obras), **ctx,
        )
        archivo = SALIDA / destino
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(html, encoding="utf-8")

    datos_js = [
        {k: o[k] for k in ("id", "titulo", "autoria", "anio", "texto", "texto_corto",
                           "oculta", "pub", "pub_nombre", *DIMENSIONES.keys())}
        | {"es_libro": bool(o["contenidos"])}
        for o in obras
    ]
    a_js = lambda d: json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    params = {d: p for d, (_, _, p) in DIMENSIONES.items()}
    # Obra del día: solo fichas revisadas (sin texto en «revision») y visibles en el catálogo.
    # El navegador elige una según la fecha en Chile; si no hay ninguna, el bloque no aparece.
    del_dia = sorted((o for o in obras if not o["revision"] and not o["oculta"]), key=lambda o: o["id"])
    escribir("index.html", "catalogo.html", obras=obras, facetas=fac, del_dia=del_dia,
             datos_json=a_js(datos_js),
             params_json=a_js({"dims": params, "pub": PARAM_PUBLICACION}))

    visibles = [o for o in obras if not o["oculta"]]
    for o in obras:
        if not o["oculta"]:
            serie = visibles
        elif o["contenedor"]:
            serie = o["contenedor"]["contenidos"]
        else:
            serie = [o]  # libro escondido porque se muestran sus cuentos: sin anterior/siguiente
        i = serie.index(o)
        anterior = serie[i - 1] if i > 0 else None
        siguiente = serie[i + 1] if i < len(serie) - 1 else None
        escribir(f"obras/{o['id']}/index.html", "ficha.html", obra=o,
                 anterior=anterior, siguiente=siguiente)

    conteos = {d: Counter(v for o in obras for v in o[d]) for d in DIMENSIONES}
    escribir("vocabulario/index.html", "vocabulario.html", vocab=vocab, conteos=conteos,
             facetas=fac)

    for md in sorted((RAIZ / "paginas").glob("*.md")):
        meta, html = leer_pagina(md)
        escribir(f"{md.stem}/index.html", "pagina.html", meta=meta, contenido=html, pagina=md.stem)

    escribir("404.html", "404.html")

    ocultas = sum(o["oculta"] for o in obras)
    print(f"✓ Sitio construido en _site/ con {len(obras)} obras"
          + (f" ({ocultas} {'escondida' if ocultas == 1 else 'escondidas'} por defecto en el catálogo)." if ocultas else "."))
    if Image is None:
        print("  (Pillow no está instalado: las portadas se publicaron sin achicar.)")
    if avisos:
        print(f"\n⚠ {len(avisos)} aviso(s) para revisar:")
        for a in avisos:
            print("  ·", a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
