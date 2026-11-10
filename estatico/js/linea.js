/* Línea de tiempo: rótulos de las portadas.
   Con mouse, el rótulo aparece al pasar por encima (CSS) y el clic abre la ficha.
   En pantallas táctiles, el primer toque muestra el rótulo y el segundo abre la ficha.
   Además, corre el rótulo hacia adentro si se saldría de la pantalla. */
(function () {
  "use strict";
  var obras = document.querySelectorAll(".linea-obra");
  if (!obras.length) return;
  var tocada = null;
  var ultimoToque = false;

  function acomodar(a) {
    var info = a.querySelector(".linea-info");
    if (!info) return;
    info.style.setProperty("--correr", "0px");
    var r = info.getBoundingClientRect();
    var margen = 8, ancho = document.documentElement.clientWidth;
    var correr = 0;
    if (r.right > ancho - margen) correr = ancho - margen - r.right;
    if (r.left + correr < margen) correr = margen - r.left;
    info.style.setProperty("--correr", Math.round(correr) + "px");
  }

  function soltar() {
    if (tocada) tocada.classList.remove("linea-tocada");
    tocada = null;
  }

  obras.forEach(function (a) {
    a.addEventListener("pointerenter", function () { acomodar(a); });
    a.addEventListener("focus", function () { acomodar(a); });
    a.addEventListener("pointerdown", function (e) { ultimoToque = e.pointerType === "touch" || e.pointerType === "pen"; });
    a.addEventListener("click", function (e) {
      if (!ultimoToque) return;           // mouse o teclado: se abre la ficha
      if (tocada === a) return;           // segundo toque: se abre la ficha
      e.preventDefault();                 // primer toque: solo se muestra el rótulo
      soltar();
      tocada = a;
      a.classList.add("linea-tocada");
      acomodar(a);
    });
  });

  document.addEventListener("click", function (e) {
    if (tocada && !tocada.contains(e.target)) soltar();
  });
  window.addEventListener("resize", function () { if (tocada) acomodar(tocada); });
})();
