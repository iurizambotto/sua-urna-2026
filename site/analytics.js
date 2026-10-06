/* Anonymous, aggregated measurement. No cookies, no IP, nothing below the electoral zone.
   window.track(name, props) works with either provider and does nothing when none is set. */
(function () {
  "use strict";
  var cfg = window.SUA_URNA_ANALYTICS || {};
  var queue = [];
  var ready = false;
  var KEYS = ["origem", "perfil", "fato", "uf", "municipio", "zona"];

  function clean(props) {
    var out = {};
    KEYS.forEach(function (k) { if (props && props[k]) out[k] = String(props[k]).toLowerCase().replace(/[^a-z0-9-]/g, ""); });
    return out;
  }

  function send(name, props) {
    var p = clean(props);
    if (cfg.provider === "umami" && window.umami) {
      window.umami.track(name, p);
    } else if (cfg.provider === "goatcounter" && window.goatcounter && window.goatcounter.count) {
      var parts = [name].concat(KEYS.filter(function (k) { return p[k]; }).map(function (k) { return p[k]; }));
      window.goatcounter.count({ path: "evento/" + parts.join("/"), title: name, event: true });
    }
  }

  window.track = function (name, props) {
    if (!cfg.provider) return;
    if (ready) send(name, props); else queue.push([name, props]);
  };

  function flush() { ready = true; queue.splice(0).forEach(function (e) { send(e[0], e[1]); }); }

  function origem() {
    try { return new URLSearchParams(location.search).get("r") || ""; } catch (e) { return ""; }
  }

  var s = document.createElement("script");
  s.async = true;
  if (cfg.provider === "goatcounter" && cfg.goatcounter) {
    // Count the page without the hash: the hash carries the section, which we never record.
    window.goatcounter = { no_onload: true, allow_local: Boolean(cfg.allowLocal) };
    // Served from this site: blockers often list gc.zgo.at. ISC licensed copy of https://gc.zgo.at/count.js
    s.src = "vendor/goatcounter-count.js?v=20261006";
    s.setAttribute("data-goatcounter", "https://" + cfg.goatcounter + ".goatcounter.com/count");
    s.onload = function () {
      var r = origem();
      window.goatcounter.count({ path: location.pathname + (r ? "?r=" + r : "") });
      flush();
    };
  } else if (cfg.provider === "umami" && cfg.umamiWebsiteId) {
    s.src = "https://cloud.umami.is/script.js";
    s.setAttribute("data-website-id", cfg.umamiWebsiteId);
    s.setAttribute("data-exclude-hash", "true");
    s.onload = flush;
  } else {
    return;
  }
  document.head.appendChild(s);
  var r0 = origem();
  if (r0) window.track("origem", { origem: r0 });
})();
