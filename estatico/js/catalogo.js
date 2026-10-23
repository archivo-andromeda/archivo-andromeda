/* Archivo Andrómeda — buscador y filtros del catálogo.
   Dentro de una misma dimensión las etiquetas se suman (O);
   entre dimensiones distintas se cruzan (Y).
   El estado vive en la URL para poder compartir búsquedas. */
(function () {
  "use strict";

  const datos = JSON.parse(document.getElementById("datos-obras").textContent);
  const PARAMS = window.ANDROMEDA_PARAMS; // { subgeneros: "sub", ... }
  const DIMS = Object.keys(PARAMS);
  const porId = new Map(datos.map((o) => [o.id, o]));

  const fichero = document.getElementById("fichero");
  const items = Array.from(fichero.children);
  const q = document.getElementById("q");
  const orden = document.getElementById("orden");
  const contador = document.getElementById("contador");
  const activos = document.getElementById("activos");
  const vacio = document.getElementById("vacio");
  const botones = Array.from(document.querySelectorAll(".sello-boton"));

  const normalizar = (t) =>
    (t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim();

  // Estado
  const sel = Object.fromEntries(DIMS.map((d) => [d, new Set()]));

  function leerURL() {
    const p = new URLSearchParams(location.search);
    DIMS.forEach((d) => {
      sel[d].clear();
      const v = p.get(PARAMS[d]);
      if (v) v.split("|").forEach((x) => x && sel[d].add(x));
    });
    q.value = p.get("q") || "";
    if (p.get("orden")) orden.value = p.get("orden");
  }

  function escribirURL() {
    const p = new URLSearchParams();
    if (q.value.trim()) p.set("q", q.value.trim());
    DIMS.forEach((d) => sel[d].size && p.set(PARAMS[d], Array.from(sel[d]).join("|")));
    if (orden.value !== "titulo") p.set("orden", orden.value);
    const s = p.toString();
    history.replaceState(null, "", s ? "?" + s : location.pathname);
  }

  function cumple(o, ignorar) {
    const terminos = normalizar(q.value).split(" ").filter(Boolean);
    if (terminos.some((t) => !o.texto.includes(t))) return false;
    return DIMS.every((d) => d === ignorar || !sel[d].size || o[d].some((v) => sel[d].has(v)));
  }

  const comparar = {
    titulo: (a, b) => a.titulo.localeCompare(b.titulo, "es"),
    autoria: (a, b) => a.autoria.localeCompare(b.autoria, "es") || comparar.titulo(a, b),
    reciente: (a, b) => (b.anio || "0").localeCompare(a.anio || "0") || comparar.titulo(a, b),
    antigua: (a, b) => (a.anio || "9999").localeCompare(b.anio || "9999") || comparar.titulo(a, b),
  };

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
      const c = datos.filter((o) => cumple(o, d) && o[d].includes(v)).length;
      b.querySelector(".sello-n").textContent = c;
      b.classList.toggle("sello-cero", !c && !on);
    });

    contador.textContent = n === 1 ? "1 obra" : `${n} obras`;
    vacio.hidden = n > 0;

    // Etiquetas activas (para quitarlas con un clic)
    activos.replaceChildren();
    DIMS.forEach((d) =>
      sel[d].forEach((v) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "sello activo";
        b.textContent = v;
        b.setAttribute("aria-label", `Quitar filtro ${v}`);
        b.onclick = () => { sel[d].delete(v); actualizar(); };
        activos.appendChild(b);
      })
    );
    if (DIMS.some((d) => sel[d].size) || q.value) {
      const l = document.createElement("button");
      l.type = "button";
      l.className = "boton-texto";
      l.textContent = "limpiar todo";
      l.onclick = limpiar;
      activos.appendChild(l);
    }
  }

  function actualizar() { aplicar(); escribirURL(); }
  function limpiar() { DIMS.forEach((d) => sel[d].clear()); q.value = ""; actualizar(); q.focus(); }

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

  // En pantallas chicas, los filtros empiezan cerrados (salvo que haya alguno activo)
  leerURL();
  const plegable = document.querySelector(".filtros-plegable");
  if (window.matchMedia("(max-width: 900px)").matches && !DIMS.some((d) => sel[d].size)) plegable.open = false;
  aplicar();
})();
