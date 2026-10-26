/* Archivo Andrómeda — buscador y filtros del catálogo.
   Dentro de una misma dimensión las etiquetas se suman (O);
   entre dimensiones distintas se cruzan (Y).
   El estado vive en la URL para poder compartir búsquedas.

   Cuentos dentro de libros del archivo («ocultas»): no aparecen por defecto.
   Se muestran al filtrar por su formato, al filtrar por su publicación (?pub=)
   o al buscar su título o autoría. */
(function () {
  "use strict";

  const datos = JSON.parse(document.getElementById("datos-obras").textContent);
  const CONFIG = window.ANDROMEDA_PARAMS; // { dims: { subgeneros: "sub", ... }, pub: "pub" }
  const PARAMS = CONFIG.dims;
  const P_PUB = CONFIG.pub;
  const DIMS = Object.keys(PARAMS);
  const porId = new Map(datos.map((o) => [o.id, o]));
  const nombrePub = new Map(datos.filter((o) => o.pub).map((o) => [o.pub, o.pub_nombre]));

  const fichero = document.getElementById("fichero");
  const items = Array.from(fichero.children);
  const q = document.getElementById("q");
  const orden = document.getElementById("orden");
  const contador = document.getElementById("contador");
  const activos = document.getElementById("activos");
  const vacio = document.getElementById("vacio");
  const avisoOcultas = document.getElementById("aviso-ocultas");
  const botones = Array.from(document.querySelectorAll(".sello-boton"));

  const normalizar = (t) =>
    (t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, " ").trim();

  // Estado
  const sel = Object.fromEntries(DIMS.map((d) => [d, new Set()]));
  const pubs = new Set();

  function leerURL() {
    const p = new URLSearchParams(location.search);
    DIMS.forEach((d) => {
      sel[d].clear();
      const v = p.get(PARAMS[d]);
      if (v) v.split("|").forEach((x) => x && sel[d].add(x));
    });
    pubs.clear();
    (p.get(P_PUB) || "").split("|").forEach((x) => x && pubs.add(x));
    q.value = p.get("q") || "";
    if (p.get("orden")) orden.value = p.get("orden");
  }

  function escribirURL() {
    const p = new URLSearchParams();
    if (q.value.trim()) p.set("q", q.value.trim());
    DIMS.forEach((d) => sel[d].size && p.set(PARAMS[d], Array.from(sel[d]).join("|")));
    if (pubs.size) p.set(P_PUB, Array.from(pubs).join("|"));
    if (orden.value !== "titulo") p.set("orden", orden.value);
    const s = p.toString();
    history.replaceState(null, "", s ? "?" + s : location.pathname);
  }

  const terminos = () => normalizar(q.value).split(" ").filter(Boolean);

  // ¿La obra cumple la búsqueda y las etiquetas? (sin mirar si está oculta)
  // «ignorar» deja fuera una dimensión, para calcular los conteos de sus botones.
  function cumpleFiltros(o, ignorar) {
    if (terminos().some((t) => !o.texto.includes(t))) return false;
    if (pubs.size && !pubs.has(o.pub)) return false;
    return DIMS.every((d) => d === ignorar || !sel[d].size || o[d].some((v) => sel[d].has(v)));
  }

  // Una obra oculta se muestra si se pide su formato o su publicación, o si se busca su nombre.
  // «formatoExtra» simula que se suma un formato más (para los conteos).
  function visible(o, formatoExtra) {
    if (!o.oculta) return true;
    if (o.formato.some((f) => sel.formato.has(f) || f === formatoExtra)) return true;
    if (pubs.has(o.pub)) return true;
    const t = terminos();
    return t.length > 0 && t.every((x) => o.texto_corto.includes(x));
  }

  const cumple = (o) => cumpleFiltros(o) && visible(o);

  const comparar = {
    titulo: (a, b) => a.titulo.localeCompare(b.titulo, "es"),
    autoria: (a, b) => a.autoria.localeCompare(b.autoria, "es") || comparar.titulo(a, b),
    reciente: (a, b) => (b.anio || "0").localeCompare(a.anio || "0") || comparar.titulo(a, b),
    antigua: (a, b) => (a.anio || "9999").localeCompare(b.anio || "9999") || comparar.titulo(a, b),
  };

  function chip(texto, etiqueta, quitar) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "sello activo";
    b.textContent = texto;
    b.setAttribute("aria-label", `Quitar filtro ${etiqueta}`);
    b.onclick = () => { quitar(); actualizar(); };
    activos.appendChild(b);
  }

  function aplicar() {
    let n = 0;
    items.forEach((li) => {
      const ok = cumple(porId.get(li.dataset.id));
      li.hidden = !ok;
      if (ok) n++;
    });

    // Orden
    const fn = comparar[orden.value] || comparar.titulo;
    items
      .slice()
      .sort((a, b) => fn(porId.get(a.dataset.id), porId.get(b.dataset.id)))
      .forEach((li) => fichero.appendChild(li));

    // Conteos dinámicos: cuántas obras habría al sumar cada etiqueta
    botones.forEach((b) => {
      const d = b.dataset.dim, v = b.dataset.valor;
      const on = sel[d].has(v);
      b.setAttribute("aria-pressed", on);
      const c = datos.filter(
        (o) => cumpleFiltros(o, d) && o[d].includes(v) && visible(o, d === "formato" ? v : undefined)
      ).length;
      b.querySelector(".sello-n").textContent = c;
      b.classList.toggle("sello-cero", !c && !on);
    });

    contador.textContent = n === 1 ? "1 obra" : `${n} obras`;
    vacio.hidden = n > 0;

    // Aviso: cuentos que coinciden pero están dentro de libros del archivo
    const escondidas = datos.filter((o) => o.oculta && cumpleFiltros(o) && !visible(o));
    avisoOcultas.replaceChildren();
    avisoOcultas.hidden = !escondidas.length;
    if (escondidas.length) {
      const formatos = new Set(escondidas.flatMap((o) => o.formato));
      avisoOcultas.append(
        escondidas.length === 1
          ? "Hay 1 cuento más dentro de un libro del archivo. "
          : `Hay ${escondidas.length} cuentos más dentro de libros del archivo. `
      );
      const ver = document.createElement("button");
      ver.type = "button";
      ver.className = "boton-texto";
      ver.textContent = escondidas.length === 1 ? "Verlo" : "Verlos";
      ver.onclick = () => { formatos.forEach((f) => sel.formato.add(f)); actualizar(); };
      avisoOcultas.appendChild(ver);
    }

    // Etiquetas activas (para quitarlas con un clic)
    activos.replaceChildren();
    pubs.forEach((p) => {
      const nombre = nombrePub.get(p) || p;
      chip(`en: ${nombre}`, nombre, () => pubs.delete(p));
    });
    DIMS.forEach((d) => sel[d].forEach((v) => chip(v, v, () => sel[d].delete(v))));
    if (DIMS.some((d) => sel[d].size) || pubs.size || q.value) {
      const l = document.createElement("button");
      l.type = "button";
      l.className = "boton-texto";
      l.textContent = "limpiar todo";
      l.onclick = limpiar;
      activos.appendChild(l);
    }
  }

  function actualizar() { aplicar(); escribirURL(); }
  function limpiar() { DIMS.forEach((d) => sel[d].clear()); pubs.clear(); q.value = ""; actualizar(); q.focus(); }

  botones.forEach((b) =>
    b.addEventListener("click", () => {
      const s = sel[b.dataset.dim];
      s.has(b.dataset.valor) ? s.delete(b.dataset.valor) : s.add(b.dataset.valor);
      actualizar();
    })
  );
  let espera;
  q.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(actualizar, 120); });
  orden.addEventListener("change", actualizar);
  document.getElementById("limpiar-vacio").addEventListener("click", limpiar);

  // Facetas largas: plegar con "ver todas"
  document.querySelectorAll(".faceta").forEach((f) => {
    const cont = f.querySelector(".faceta-larga");
    const btn = f.querySelector(".ver-mas");
    if (!cont || !btn) return;
    cont.classList.add("plegada");
    btn.hidden = false;
    btn.onclick = () => {
      const plegada = cont.classList.toggle("plegada");
      btn.textContent = plegada ? "ver todas" : "ver menos";
    };
  });

  // Obra del día: la misma para todo el mundo durante un día (hora de Chile)
  const bloqueDia = document.getElementById("obra-dia");
  if (bloqueDia) {
    const opciones = bloqueDia.querySelectorAll("[data-dia]");
    const hoy = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Santiago" }).format(new Date());
    const dia = Math.floor(Date.parse(hoy + "T00:00:00Z") / 86400000);
    if (opciones.length && !isNaN(dia)) {
      opciones[dia % opciones.length].hidden = false;
      bloqueDia.hidden = false;
    }
  }

  // En pantallas chicas, los filtros empiezan cerrados (salvo que haya alguno activo)
  leerURL();
  const plegable = document.querySelector(".filtros-plegable");
  if (window.matchMedia("(max-width: 900px)").matches && !DIMS.some((d) => sel[d].size)) plegable.open = false;
  aplicar();
})();
