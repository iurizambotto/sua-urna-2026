(function () {
  "use strict";
  const DATA = "data";
  const TAXA_PADRAO = 33; // sections per second measured on 2026-10-06 (28 to 35)
  const fmt = (n) => new Intl.NumberFormat("pt-BR").format(n);
  const $ = (id) => document.getElementById(id);

  async function getJson(path) {
    const r = await fetch(`${DATA}/${path}?t=${Date.now()}`);
    if (!r.ok) throw new Error(path);
    return r.json();
  }

  function tempo(seg) {
    if (seg <= 0) return "pronto";
    if (seg < 60) return "menos de 1 min";
    const h = Math.floor(seg / 3600), m = Math.round((seg % 3600) / 60);
    return h ? `${h} h ${m} min` : `${m} min`;
  }

  function quando(iso) {
    if (!iso) return "";
    return new Date(iso).toLocaleString("pt-BR", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" });
  }

  async function carregar() {
    const [plan, progress, rate] = await Promise.all([
      getJson("plan.json").catch(() => ({ order: [], ufs: {} })),
      getJson("progress.json").catch(() => ({ ufs: {} })),
      getJson("rate.json").catch(() => null),
    ]);
    const taxa = rate && rate.secoes_por_segundo > 5 ? rate.secoes_por_segundo : TAXA_PADRAO;
    const ordem = plan.order.length ? plan.order : Object.keys(progress.ufs);
    const linhas = [];
    let acumulado = 0, totalSec = 0, feitoSec = 0;
    for (const cd of ordem) {
      const pl = plan.ufs[cd] || {};
      const pr = progress.ufs[cd] || {};
      const secTotal = pl.secoes || pr.secoes_total || 0;
      const secOk = pr.secoes_ok || 0;
      const munTotal = pl.municipios || pr.municipios_total || 0;
      const munOk = pr.municipios_ok || 0;
      const falta = Math.max(secTotal - secOk, 0);
      acumulado += falta;
      totalSec += secTotal; feitoSec += secOk;
      const pct = secTotal ? Math.min(100, (100 * secOk) / secTotal) : 0;
      const estado = pct >= 99.9 ? "pronto" : (secOk > 0 ? "em andamento" : "na fila");
      linhas.push({ cd, nm: pl.nm || pr.nm || cd.toUpperCase(), munOk, munTotal, secOk, secTotal, pct, estado, eta: estado === "pronto" ? 0 : acumulado / taxa, nomes: pr.municipios_ok_nomes || [] });
    }
    const tbody = $("tabela").querySelector("tbody");
    tbody.innerHTML = linhas.map((l) => `
      <tr data-cd="${l.cd}">
        <td><b>${l.nm}</b><br><span class="ajuda">${l.estado}</span></td>
        <td class="num">${fmt(l.munOk)} / ${fmt(l.munTotal)}</td>
        <td class="num">${fmt(l.secOk)} / ${fmt(l.secTotal)}</td>
        <td><div class="meter ${l.pct >= 99.9 ? "done" : ""}"><span style="width:${l.pct.toFixed(1)}%"></span></div><span class="ajuda">${l.pct.toFixed(1)}%</span></td>
        <td class="num">${l.estado === "pronto" ? "pronto" : `~${tempo(l.eta)}`}</td>
      </tr>`).join("");
    const pctGeral = totalSec ? (100 * feitoSec) / totalSec : 0;
    const restante = Math.max(totalSec - feitoSec, 0) / taxa;
    $("resumo").textContent =
      `${fmt(feitoSec)} de ${fmt(totalSec)} seções coletadas (${pctGeral.toFixed(1)}%). ` +
      `Velocidade: ${taxa.toFixed(0)} seções por segundo. Falta cerca de ${tempo(restante)} para a fila inteira. ` +
      `Último reindex: ${quando(progress.generated_at) || "nunca"}.`;
    tbody.querySelectorAll("tr").forEach((tr) => tr.addEventListener("click", () => detalhe(linhas.find((l) => l.cd === tr.dataset.cd))));
    const emAndamento = linhas.find((l) => l.estado === "em andamento");
    if (emAndamento) detalhe(emAndamento);
  }

  function detalhe(l) {
    if (!l) return;
    $("detalhe").hidden = false;
    $("detalhe-titulo").textContent = `${l.nm}: ${fmt(l.munOk)} municípios prontos de ${fmt(l.munTotal)}`;
    $("detalhe-lista").innerHTML = l.nomes.map((n) => `<li>${n}</li>`).join("") || "<li>nenhum ainda</li>";
  }

  carregar();
  setInterval(carregar, 60000);
})();
