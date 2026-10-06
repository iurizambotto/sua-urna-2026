(function () {
  "use strict";
  var root = document.documentElement, btn = document.getElementById("tema");
  if (!btn) return;
  function atual() { var t = root.getAttribute("data-theme"); if (t) return t; return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"; }
  function aplicar(t) { root.setAttribute("data-theme", t); try { localStorage.setItem("tema", t); } catch (e) {} btn.setAttribute("aria-pressed", String(t === "dark")); }
  btn.setAttribute("aria-pressed", String(atual() === "dark"));
  btn.addEventListener("click", function () { aplicar(atual() === "dark" ? "light" : "dark"); });
})();
