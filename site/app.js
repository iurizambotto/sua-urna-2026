(function () {
  "use strict";

  const DATA = "data";
  const TERCEIRA = ["55", "14", "70"];
  const LABELS = { flavio: "Flávio Bolsonaro", lula: "Lula", terceira: "Outros candidatos", branco: "Branco ou nulo", ausente: "Não foram votar" };
  const $ = (id) => document.getElementById(id);
  const sel = { uf: $("uf"), municipio: $("municipio"), zona: $("zona"), secao: $("secao") };
  const state = { uf: "", municipio: "", zona: "", secao: "", ufNome: "", mun: null, zonaData: null, brasil: null, last: null, kit: null, filtro: "todos" };
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fmt = (n) => new Intl.NumberFormat("pt-BR").format(Math.round(n));
  const fmt1 = (n) => new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(n);
  const fmt2 = (n) => new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
  const porNome = (a, b) => a.nm.localeCompare(b.nm, "pt-BR", { sensitivity: "base" });
  const porNumero = (a, b) => Number(a) - Number(b);

  async function getJson(path) {
    const r = await fetch(`${DATA}/${path}`);
    if (!r.ok) throw new Error(`sem dados em ${path}`);
    return r.json();
  }

  function toast(msg) {
    const t = $("toast");
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => t.classList.remove("on"), 2200);
  }

  function countUp(el, value, format) {
    if (reduced || value < 20) { el.textContent = format(value); return; }
    const start = performance.now(), dur = 700;
    const step = (now) => {
      const p = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = format(value * eased);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  /* ---------- math ---------- */
  function swingNeeded(flavio, lula) {
    const d = flavio - lula;
    if (d < 0) return [0, 0];
    return [Math.floor((d + 1) / 2), Math.floor(d / 2) + 1];
  }

  function umEmCada(base, needed) {
    if (needed <= 0) return null;
    if (base <= 0) return { k: 0, each: needed };
    const k = Math.floor(base / needed);
    if (k >= 2) return { k, each: 1 };
    return { k: 1, each: Math.ceil(needed / base) };
  }

  function fraseEsforco(base, needed, alvoSing, alvoPlur, prefixo) {
    const r = umEmCada(base, needed);
    if (!r || r.k === 0) return "";
    if (r.k >= 2) return `${prefixo} <strong>uma em cada ${fmt(r.k)}</strong> delas trouxer ${alvoSing}, vira.`;
    if (r.each === 1) return `${prefixo} <strong>cada uma</strong> delas trouxer ${alvoSing}, vira.`;
    return `${prefixo} cada uma delas trouxer <strong>${fmt(r.each)}</strong> ${alvoPlur}, vira.`;
  }

  function summarize(s) {
    const flavio = s.votos["22"] || 0, lula = s.votos["13"] || 0;
    const terceira = TERCEIRA.reduce((a, k) => a + (s.votos[k] || 0), 0);
    const outros = s.validos - flavio - lula - terceira;
    const brancoNulo = s.brancos + s.nulos;
    const [tie, win] = swingNeeded(flavio, lula);
    return { flavio, lula, terceira, outros, brancoNulo, ausentes: s.abstencao, aptos: s.aptos, tie, win, diff: flavio - lula };
  }

  /* ---------- dots ---------- */
  function dots(el, seq, animate) {
    let i = 0;
    el.innerHTML = seq.map(([k, q]) => {
      let out = "";
      for (let j = 0; j < q; j++, i++) out += `<i class="${k}" style="--c:var(--${k});--i:${animate ? i : 0}"></i>`;
      return out;
    }).join("");
  }

  function legend(el, seq) {
    el.innerHTML = seq.map(([k, q]) => `<li><i class="${k}" style="--c:var(--${k})"></i><b>${fmt(q)}</b> ${LABELS[k]}</li>`).join("");
  }

  /* ---------- national panel ---------- */
  function renderPainel(b) {
    const diff = b.votos["22"] - b.votos["13"];
    const porUrna = diff / b.secoes;
    const precisa = Math.floor(diff / 2) + 1;
    const kTroca = Math.floor(b.votos["13"] / precisa);
    const kNova = Math.floor(b.votos["13"] / (diff + 1));
    $("hero-num").textContent = `1 em ${fmt(kTroca)}`;
    $("hero-lab").textContent =
      `Se uma em cada ${fmt(kTroca)} pessoas que votaram no Lula convencer uma que votou no Flávio, o Brasil vira. ` +
      `Ou, se uma em cada ${fmt(kNova)} trouxer alguém que ficou em casa. Por urna, são ${fmt2(porUrna / 2)} pessoas mudando de ideia.`;
    const n = b.secoes;
    const terceira = TERCEIRA.reduce((a, k) => a + (b.votos[k] || 0), 0);
    const outros = b.validos - b.votos["22"] - b.votos["13"] - terceira;
    const r = (x) => Math.round(x / n);
    const seq = [["flavio", r(b.votos["22"])], ["lula", r(b.votos["13"])], ["terceira", r(terceira + outros)], ["branco", r(b.brancos + b.nulos)], ["ausente", r(b.abstencao)]];
    dots($("sala"), seq, true);
    legend($("sala-legenda"), seq);
    $("sala-texto").textContent =
      `${fmt(b.aptos / n)} eleitores por seção. A diferença entre os dois cabe em uma mão: ${fmt1(porUrna)} votos. As pessoas soltas enchem um ônibus.`;
    const tiles = [
      [porUrna, fmt1, "votos por urna de diferença"],
      [b.abstencao, fmt, "não foram votar"],
      [b.brancos + b.nulos, fmt, "votaram branco ou nulo"],
      [terceira, fmt, "votaram em Cury, Renan ou Caiado"],
    ];
    $("tiles").innerHTML = tiles.map(([, , l], i) => `<div class="tile"><div class="v" id="tile-${i}">0</div><div class="l">${l}</div></div>`).join("");
    tiles.forEach(([v, f], i) => countUp($(`tile-${i}`), v, f));
  }

  /* ---------- selects ---------- */
  function fill(select, items, placeholder) {
    select.innerHTML = "";
    const o = document.createElement("option");
    o.value = ""; o.textContent = placeholder; select.appendChild(o);
    for (const it of items) {
      const op = document.createElement("option");
      op.value = it.value;
      op.textContent = it.disabled ? `${it.label} (ainda sem dados)` : it.label;
      op.disabled = Boolean(it.disabled);
      select.appendChild(op);
    }
    select.disabled = items.length === 0;
  }

  function setStatus(msg) { $("status").textContent = msg || ""; }

  function parseHash() {
    const m = location.hash.match(/^#([a-z]{2})\/(\d{5})(?:\/(\d{4})\/(\d{4}))?$/);
    return m ? { uf: m[1], municipio: m[2], zona: m[3] || "", secao: m[4] || "" } : null;
  }

  const track = (name, props) => { try { if (window.track) window.track(name, props); } catch (e) { /* never break the page */ } };
  const onde3 = () => ({ uf: state.uf, municipio: state.municipio, zona: state.zona });

  function siteBase() { return location.href.split(/[?#]/)[0].replace(/index\.html$/, ""); }

  // Link that previews well in WhatsApp: the municipality page carries its own image.
  function shareUrl(origem) {
    const q = `?r=${origem}`;
    if (state.uf && state.municipio) {
      const tail = state.zona && state.secao ? `#${state.zona}/${state.secao}` : "";
      return `${siteBase()}m/${state.uf}/${state.municipio}.html${q}${tail}`;
    }
    return `${siteBase()}${q}`;
  }

  async function selectPath(p) {
    sel.uf.value = p.uf; await onUf();
    sel.municipio.value = p.municipio; await onMunicipio();
    if (!p.zona) { $("busca").scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" }); return; }
    sel.zona.value = p.zona; await onZona();
    sel.secao.value = p.secao; onSecao();
  }

  async function onUf() {
    state.uf = sel.uf.value;
    state.ufNome = sel.uf.options[sel.uf.selectedIndex]?.textContent || "";
    fill(sel.municipio, [], "Carregando"); fill(sel.zona, [], "Escolha o município"); fill(sel.secao, [], "Escolha a zona");
    $("resultado").hidden = true;
    if (!state.uf) { fill(sel.municipio, [], "Escolha o estado"); setStatus(""); return; }
    const idx = await getJson(`${state.uf}/index.json`);
    const prontos = idx.municipios.filter((m) => m.ok !== false).length;
    fill(sel.municipio, [...idx.municipios].sort(porNome).map((m) => ({ value: m.cd, label: m.nm, disabled: m.ok === false })), "Escolha");
    setStatus(prontos < idx.municipios.length ? `${fmt(prontos)} de ${fmt(idx.municipios.length)} municípios de ${state.ufNome} já coletados. Os demais estão na fila.` : "");
  }

  async function onMunicipio() {
    state.municipio = sel.municipio.value;
    fill(sel.zona, [], "Carregando"); fill(sel.secao, [], "Escolha a zona");
    $("resultado").hidden = true;
    if (!state.municipio) { fill(sel.zona, [], "Escolha o município"); return; }
    try {
      state.mun = await getJson(`${state.uf}/${state.municipio}.json`);
    } catch (e) {
      fill(sel.zona, [], "Município ainda não coletado");
      setStatus("Este município ainda não foi coletado. Volte mais tarde.");
      return;
    }
    fill(sel.zona, [...state.mun.zonas].sort((a, b) => porNumero(a.cd, b.cd)).map((z) => ({ value: z.cd, label: `Zona ${Number(z.cd)}` })), "Escolha");
  }

  async function onZona() {
    state.zona = sel.zona.value;
    fill(sel.secao, [], "Carregando");
    $("resultado").hidden = true;
    if (!state.zona) { fill(sel.secao, [], "Escolha a zona"); return; }
    state.zonaData = await getJson(`${state.uf}/${state.municipio}/${state.zona}.json`);
    fill(sel.secao, [...state.zonaData.secoes].sort((a, b) => porNumero(a.secao, b.secao)).map((s) => ({ value: s.secao, label: `Seção ${Number(s.secao)}` })), "Escolha");
  }

  function onSecao() {
    state.secao = sel.secao.value;
    if (!state.secao) { $("resultado").hidden = true; return; }
    const s = state.zonaData.secoes.find((x) => x.secao === state.secao);
    const hash = `${state.uf}/${state.municipio}/${state.zona}/${state.secao}`;
    if (location.hash.slice(1) !== hash) history.replaceState(null, "", `${location.search}#${hash}`);
    track("secao", onde3());
    render(s);
  }

  /* ---------- section result ---------- */
  function render(s) {
    const r = $("resultado");
    r.hidden = false;
    $("preview").classList.remove("on");
    const onde = `${state.mun.nm}, zona ${Number(state.zona)}, seção ${Number(state.secao)}`;
    if (s.status !== "ok") {
      $("onde").textContent = onde;
      $("sala-secao").innerHTML = ""; $("barra").innerHTML = ""; $("numeros").innerHTML = "";
      $("conta").textContent = "Esta seção não tem boletim próprio no TSE. Em geral isso acontece quando ela votou junto com outra seção, na mesma urna.";
      const t = state.mun.totais;
      $("soltos").textContent = `No município inteiro: ${fmt(t.aptos)} aptos, ${fmt(t.abstencao)} não foram votar, ${fmt(t.brancos + t.nulos)} votaram branco ou nulo. Flávio ${fmt(t.votos["22"] || 0)}, Lula ${fmt(t.votos["13"] || 0)}.`;
      $("copiar").hidden = true; $("imagem").hidden = true;
      r.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
      return;
    }
    $("copiar").hidden = false; $("imagem").hidden = false;
    const m = summarize(s);
    $("onde").textContent = `${onde}. ${fmt(m.aptos)} eleitores nesta sala.`;
    const seq = [["flavio", m.flavio], ["lula", m.lula], ["terceira", m.terceira + m.outros], ["branco", m.brancoNulo], ["ausente", m.ausentes]];
    dots($("sala-secao"), seq, true);
    $("barra").innerHTML = seq.map(([k, v]) => `<span title="${LABELS[k]}: ${fmt(v)}" style="--c:var(--${k});width:${(100 * v) / m.aptos}%"></span>`).join("");
    $("numeros").innerHTML = seq.map(([k, v]) =>
      `<li><i class="${k}" style="--c:var(--${k})"></i><b>${fmt(v)}</b><span>${LABELS[k]}${k === "terceira" ? ` <span class="muted small">(Cury ${fmt(s.votos["70"] || 0)}, Renan ${fmt(s.votos["14"] || 0)}, Caiado ${fmt(s.votos["55"] || 0)})</span>` : ""}</span></li>`
    ).join("");
    let conta;
    if (m.diff > 0) {
      const troca = fraseEsforco(m.lula, m.win, "uma pessoa que votou no Flávio", "pessoas que votaram no Flávio", "Se");
      const nova = fraseEsforco(m.lula, m.diff + 1, "alguém que ficou em casa ou votou em branco", "pessoas que ficaram em casa", "Ou, se");
      conta = m.lula > 0
        ? `Aqui Flávio ganhou por ${fmt(m.diff)} ${m.diff === 1 ? "voto" : "votos"}. Parece muito, mas ${fmt(m.lula)} pessoas desta sala já votaram no Lula. ${troca} ${nova}`
        : `Aqui Flávio ganhou por ${fmt(m.diff)} votos e ninguém votou no Lula. Esta sala é a mais difícil: o que rende é buscar quem ficou em casa, que são ${fmt(m.ausentes)}.`;
    } else if (m.diff < 0) {
      conta = `Aqui Lula ganhou por <strong>${fmt(-m.diff)}</strong> ${m.diff === -1 ? "voto" : "votos"}. Para Flávio virar, bastam ${fmt(Math.floor(-m.diff / 2) + 1)} pessoas daqui. Segurar quem veio e buscar quem faltou é o trabalho.`;
    } else {
      conta = "Empate nesta sala. <strong>Uma pessoa</strong> decide.";
    }
    $("conta").innerHTML = conta;
    const soltos = m.ausentes + m.brancoNulo + m.terceira;
    $("soltos").textContent = `${fmt(soltos)} pessoas desta sala não escolheram nenhum dos dois que estão no segundo turno: ${fmt(m.ausentes)} não apareceram, ${fmt(m.brancoNulo)} votaram branco ou nulo e ${fmt(m.terceira)} votaram em Cury, Renan ou Caiado. Você conhece alguma delas.`;
    state.last = { s, m, onde };
    if (state.kit) renderKit(state.kit);
    r.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
  }

  function manchete(m) {
    if (m.diff > 0) {
      const r = umEmCada(m.lula, m.win);
      if (r && r.k >= 2) return [`1 em cada ${fmt(r.k)}`, "pessoas que votaram no Lula aqui, trazendo uma pessoa, viram esta seção."];
      if (r && r.k === 1) return [`${fmt(m.win)} pessoas`, "mudando de ideia viram esta seção. Cada eleitor do Lula daqui precisa trazer alguém."];
      return [`${fmt(m.win)} pessoas`, "mudando de ideia viram esta seção."];
    }
    if (m.diff < 0) return [`Lula por ${fmt(-m.diff)}`, "nesta seção. Para segurar, buscar quem faltou."];
    return ["Empate", "nesta seção. Uma pessoa decide."];
  }

  function shareText() {
    const { m, onde } = state.last;
    const url = shareUrl("wa");
    const [titulo, sub] = manchete(m);
    return [
      `Na nossa seção (${onde}) tinham ${fmt(m.aptos)} eleitores.`,
      `Flávio ${fmt(m.flavio)}, Lula ${fmt(m.lula)}. ${fmt(m.ausentes)} não foram votar, ${fmt(m.brancoNulo)} votaram branco ou nulo, ${fmt(m.terceira)} votaram em Cury, Renan ou Caiado.`,
      `${titulo} ${sub}`,
      `Dia 25, das 8h às 17h. Veja a sua: ${url}`,
    ].join("\n");
  }

  async function copiar() {
    const text = shareText();
    try { await navigator.clipboard.writeText(text); }
    catch (e) {
      const ta = document.createElement("textarea");
      ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove();
    }
    track("copiar-texto", onde3());
    toast("Texto copiado. Cole no WhatsApp.");
  }

  /* ---------- share image ---------- */
  async function imagem() {
    try { await document.fonts.ready; } catch (e) { /* fonts optional */ }
    const { s, m, onde } = state.last;
    const W = 1080, H = 1350, PAD = 72;
    const c = document.createElement("canvas");
    c.width = W; c.height = H;
    const g = c.getContext("2d");
    const display = `"Bricolage Grotesque", system-ui, sans-serif`;
    const body = `"Public Sans", system-ui, sans-serif`;
    const col = { bg: "#0b0b0b", ink: "#f6f6f6", muted: "#b3b3b3", accent: "#ff3b4e", flavio: "#f6f6f6", lula: "#ff3b4e", terceira: "#8a8a8a", branco: "#4a4a4a", ausente: "#262626" };
    g.fillStyle = col.bg; g.fillRect(0, 0, W, H);
    g.fillStyle = col.accent; g.font = `700 26px ${display}`;
    g.fillText("SUA URNA  ·  SEGUNDO TURNO, 25 DE OUTUBRO", PAD, 96);
    const [titulo, sub] = manchete(m);
    g.fillStyle = col.accent; g.font = `800 ${titulo.length > 14 ? 96 : 120}px ${display}`;
    g.fillText(titulo, PAD - 4, 230);
    g.fillStyle = col.ink; g.font = `400 36px ${body}`;
    let y = wrap(g, sub, PAD, 292, W - 2 * PAD, 46);
    g.fillStyle = col.muted; g.font = `600 30px ${body}`;
    y = wrap(g, `${onde}. ${fmt(m.aptos)} eleitores.`, PAD, y + 26, W - 2 * PAD, 40);
    // dots: one per voter, same order as the page
    const seq = [["flavio", m.flavio], ["lula", m.lula], ["terceira", m.terceira + m.outros], ["branco", m.brancoNulo], ["ausente", m.ausentes]];
    const areaW = W - 2 * PAD, areaTop = y + 30, areaH = 520;
    const cols = Math.max(10, Math.ceil(Math.sqrt(m.aptos * areaW / areaH)));
    const rows = Math.ceil(m.aptos / cols);
    const cell = Math.min(areaW / cols, areaH / rows);
    const rad = cell * 0.4;
    let i = 0;
    for (const [k, q] of seq) {
      for (let j = 0; j < q; j++, i++) {
        const x = PAD + (i % cols) * cell + cell / 2, yy = areaTop + Math.floor(i / cols) * cell + cell / 2;
        g.beginPath(); g.arc(x, yy, rad, 0, Math.PI * 2);
        if (k === "ausente") { g.strokeStyle = col.branco; g.lineWidth = Math.max(1.5, rad * 0.22); g.stroke(); }
        else { g.fillStyle = col[k]; g.fill(); }
      }
    }
    // legend, two columns
    let ly = areaTop + rows * cell + 56;
    g.font = `600 30px ${body}`;
    seq.forEach(([k, q], idx) => {
      const lx = PAD + (idx % 2) * (areaW / 2), yy = ly + Math.floor(idx / 2) * 48;
      g.beginPath(); g.arc(lx + 12, yy - 10, 11, 0, Math.PI * 2);
      if (k === "ausente") { g.strokeStyle = col.branco; g.lineWidth = 3; g.stroke(); } else { g.fillStyle = col[k]; g.fill(); }
      g.fillStyle = col.ink; g.fillText(`${fmt(q)}  ${LABELS[k]}`, lx + 36, yy);
    });
    g.fillStyle = col.muted; g.font = `400 26px ${body}`;
    g.fillText("Fonte: boletim de urna oficial do TSE, 1º turno de 2026.", PAD, H - 108);
    g.fillText(`Dia 25, das 8h às 17h.  ${location.host && !/^(localhost|127\.)/.test(location.host) ? location.host : ""}`, PAD, H - 68);
    const url = c.toDataURL("image/png");
    $("preview-img").src = url;
    $("baixar").href = url;
    $("baixar").download = `sua-urna-${state.uf}-${state.municipio}-${state.zona}-${state.secao}.png`;
    $("preview").classList.add("on");
    track("gerar-imagem", onde3());
    toast("Imagem pronta.");
  }

  function wrap(g, text, x, y, maxW, lh) {
    const words = text.split(" ");
    let line = "";
    for (const w of words) {
      const t = line ? `${line} ${w}` : w;
      if (g.measureText(t).width > maxW && line) { g.fillText(line, x, y); line = w; y += lh; }
      else line = t;
    }
    if (line) { g.fillText(line, x, y); y += lh; }
    return y;
  }

  /* ---------- kits (personas) ---------- */
  function fato(id) { return window.FATOS.find((x) => x.id === id); }
  function dominio(url) { try { return new URL(url).host.replace(/^www\./, ""); } catch (e) { return ""; } }
  function tag(status) {
    const label = { comprovado: "comprovado", investigacao: "em investigação", arquivado: "arquivado", terceiro: "levantamento de terceiro" }[status] || status;
    return `<span class="tag ${status}">${label}</span>`;
  }

  function renderPersonas() {
    $("personas").innerHTML = window.KITS.map((k) => `
      <button type="button" class="pessoa" role="tab" data-kit="${k.id}" aria-pressed="false">
        <i class="${k.glifo}" style="--c:var(--${k.glifo})"></i>
        <span class="t">${k.titulo}</span>
        <span class="s">${k.stat}</span>
      </button>`).join("");
    $("personas").querySelectorAll(".pessoa").forEach((b) => b.addEventListener("click", () => { renderKit(b.dataset.kit); track("perfil", { perfil: b.dataset.kit }); $("kit").scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "nearest" }); }));
    renderKit(window.KITS[0].id);
  }

  function renderKit(id) {
    state.kit = id;
    const k = window.KITS.find((x) => x.id === id);
    $("personas").querySelectorAll(".pessoa").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.kit === id)));
    $("kit").innerHTML = `
      <p class="kicker">Falando com</p>
      <h3>${k.titulo}</h3>
      <p class="quem">${k.quem}</p>
      <h4>Para abrir</h4>
      <p class="fala">${k.abrir}</p>
      <h4>Três fatos, com fonte</h4>
      <div class="fatos-kit">${k.fatos.map((fid) => { const f = fato(fid); return f ? `<div class="fato-mini"><span>${f.texto}</span><span class="src"><a data-fato="${f.id}" href="${f.url}" target="_blank" rel="noopener">${f.fonte}</a>, ${f.data} ${tag(f.status)}</span></div>` : ""; }).join("")}</div>
      <h4>O que não dizer</h4>
      <ul class="nao">${k.naoDizer.map((t) => `<li>${t}</li>`).join("")}</ul>
      <h4>Para fechar</h4>
      <p class="fala">${k.fechar}</p>
      <div class="acoes">
        <a class="cta" id="whats-kit" target="_blank" rel="noopener" href="#">Mandar mensagem no WhatsApp</a>
        <button type="button" class="ghost" id="copiar-kit">Copiar este roteiro</button>
      </div>
      <p class="small muted">A mensagem abre no WhatsApp para você escolher a pessoa e editar antes de enviar.${state.last ? " O link leva aos números da sua seção." : " Escolha a sua seção acima e o link passa a levar aos números dela."}</p>`;
    const msg = `${k.mensagem} ${shareUrl(`wa-${k.id}`)}`;
    $("whats-kit").href = `https://wa.me/?text=${encodeURIComponent(msg)}`;
    $("whats-kit").addEventListener("click", () => track("whatsapp-roteiro", { perfil: k.id, ...onde3() }));
    $("copiar-kit").addEventListener("click", async () => {
      const text = [k.titulo, "", `Para abrir: ${k.abrir}`, "", ...k.fatos.map((fid) => { const f = fato(fid); return f ? `- ${f.texto} (${f.fonte}, ${f.data}: ${f.url})` : ""; }), "", `O que não dizer: ${k.naoDizer.join(" ")}`, "", `Para fechar: ${k.fechar}`].join("\n");
      try { await navigator.clipboard.writeText(text); } catch (e) { /* ignore */ }
      track("copiar-roteiro", { perfil: k.id });
      toast("Roteiro copiado.");
    });
  }

  /* ---------- facts ---------- */
  function renderFiltros() {
    const presentes = [...new Set(window.FATOS.map((f) => f.tema))];
    const chips = [["todos", "Todos"], ...presentes.map((t) => [t, window.TEMAS[t] || t])];
    $("filtros").innerHTML = chips.map(([v, l]) => `<button type="button" class="chip" data-tema="${v}" aria-pressed="${v === "todos"}">${l}</button>`).join("");
    $("filtros").querySelectorAll(".chip").forEach((b) => b.addEventListener("click", () => {
      state.filtro = b.dataset.tema;
      $("filtros").querySelectorAll(".chip").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      renderFatos();
    }));
  }

  function renderFatos() {
    $("lista-fatos").innerHTML = window.FATOS.map((f) => `
      <article class="fato" id="${f.id}" ${state.filtro !== "todos" && f.tema !== state.filtro ? "hidden" : ""}>
        <span class="tema">${window.TEMAS[f.tema] || f.tema}</span>
        <p>${f.texto}</p>
        <div class="rodape"><span><a data-fato="${f.id}" href="${f.url}" target="_blank" rel="noopener">${f.fonte}</a> · ${f.data} · ${dominio(f.url)}</span>${tag(f.status)}</div>
      </article>`).join("");
  }

  /* ---------- boot ---------- */
  async function init() {
    renderPersonas();
    renderFiltros();
    renderFatos();
    try { state.brasil = await getJson("brasil.json"); renderPainel(state.brasil); } catch (e) { /* optional */ }
    try {
      const ufs = await getJson("ufs.json");
      fill(sel.uf, [...ufs.ufs].sort(porNome).map((u) => ({ value: u.cd, label: u.nm })), "Escolha");
      const fromHash = parseHash();
      if (fromHash) await selectPath(fromHash);
      else if (ufs.ufs.length === 1) { sel.uf.value = ufs.ufs[0].cd; await onUf(); }
    } catch (e) {
      setStatus("Ainda não há dados publicados para nenhum estado.");
    }
  }

  window.addEventListener("hashchange", () => { const p = parseHash(); if (p && p.secao !== state.secao) selectPath(p); });
  sel.uf.addEventListener("change", onUf);
  sel.municipio.addEventListener("change", onMunicipio);
  sel.zona.addEventListener("change", onZona);
  sel.secao.addEventListener("change", onSecao);
  $("baixar").addEventListener("click", () => track("baixar-imagem", onde3()));
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a[data-fato]");
    if (a) track("fonte", { fato: a.dataset.fato });
  });
  $("copiar").addEventListener("click", copiar);
  $("imagem").addEventListener("click", imagem);
  init();
})();
