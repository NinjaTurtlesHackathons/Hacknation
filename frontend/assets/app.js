// Probatum Lab: shared code. Every number on the site comes from data/*.json, written by frontend/build_data.py.
"use strict";
const P = (() => {
  const AGENTS = ["lead", "scout", "planner", "researcher", "redteam", "learner", "scribe"];
  const AGENT_NAME = { lead: "Lead", scout: "Scout", planner: "Planner", researcher: "Researcher", redteam: "Red team", learner: "Learner", scribe: "Scribe" };
  const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  let SITE = null;

  async function json(path) {
    const r = await fetch(path, { cache: "no-cache" });
    if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
    return r.json();
  }
  async function site() { return SITE || (SITE = await json("data/site.json")); }
  function srcLink(path) {
    const repo = SITE?.repo, c = SITE?.commit;
    return repo && c ? `<a href="${repo}/blob/${c}/${esc(path)}">${esc(path)}</a>` : esc(path);
  }

  // ---------- theme ----------
  function theme() {
    let saved = null; try { saved = localStorage.getItem("probatum-theme"); } catch (e) {}
    if (saved) document.documentElement.dataset.theme = saved;
    const b = $("#theme"); if (!b) return;
    const isDark = () => (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
    const label = () => { b.textContent = isDark() ? "Light theme" : "Dark theme"; b.setAttribute("aria-pressed", String(isDark())); };
    label();
    b.addEventListener("click", () => {
      const next = isDark() ? "light" : "dark"; document.documentElement.dataset.theme = next;
      try { localStorage.setItem("probatum-theme", next); } catch (e) {}
      label(); document.dispatchEvent(new CustomEvent("themechange"));
    });
  }

  // ---------- small helpers ----------
  function toast(msg) {
    const t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); t.textContent = msg;
    document.body.appendChild(t); setTimeout(() => t.remove(), 2200);
  }
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); toast("Command copied"); }
    catch (e) { window.prompt("Copy this command:", text); }
  }
  function math(el) {
    if (window.renderMathInElement) renderMathInElement(el, { delimiters: [{ left: "$", right: "$", display: false }], throwOnError: false });
    else document.addEventListener("katex-ready", () => math(el), { once: true });
  }
  function qedMark(big) {
    const s = document.createElement("span"); s.className = big ? "qed-big" : "qed-mark"; s.textContent = "∎";
    s.setAttribute("role", "img"); s.setAttribute("aria-label", "Confirmed by the verifier"); return s;
  }
  function appearQed(container) {
    container.innerHTML = ""; const q = qedMark(true); container.appendChild(q);
    if (!reduced()) { void q.offsetWidth; q.classList.add("appear"); }
    return q;
  }
  const noMark = () => `<span class="no-mark" role="img" aria-label="Rejected by the verifier">✕</span>`;
  const fmtT = (t) => `${t} UTC`;

  // ---------- event rows ----------
  const KIND_LABEL = { ok: "Verifier confirmed", no: "Verifier rejected", deny: "Policy denied", ask: "Policy asked a human", allow: "Human approved", policy: "Assumption reopened", handoff: "Handoff", lead: "Lead note", tool: "Harness call" };
  function laneSpans(e, active) {
    const n = AGENTS.length, i = AGENTS.indexOf(e.agent), j = e.to ? AGENTS.indexOf(e.to) : -1;
    let h = "";
    AGENTS.forEach((a, k) => { h += `<span class="${active.has(a) ? "on" : ""} ${k === i || k === j ? "dot" : ""}"></span>`; });
    if (j >= 0 && i >= 0) { const a = Math.min(i, j), b = Math.max(i, j); h += `<i class="hand" style="left:${a * 12 + 5}px;width:${(b - a) * 12}px"></i>`; }
    return `<div class="lanes" aria-hidden="true" style="--n:${n}">${h}</div>`;
  }
  function eventRow(e, opts = {}) {
    const li = document.createElement("li");
    li.className = `ev ${e.kind}`; li.dataset.s = e.s;
    const who = AGENT_NAME[e.agent] || e.agent;
    const detail = [
      `<span class="sr-only">${esc(KIND_LABEL[e.kind] || "")}. </span>`,
      e.cmd ? `<code>${esc(e.cmd)}</code>` : "",
      e.hash ? `Message sha256 <code>${esc(e.hash.slice(0, 16))}…</code>` : "",
      e.surprise ? `<span>Contradicts the preregistered assumption: ${esc(e.surprise)}</span>` : "",
      e.line != null ? `<span>record.jsonl line ${e.line + 1}${e.dauer_s != null ? `, ${e.dauer_s} s in the harness` : ""}</span>` : "",
    ].filter(Boolean).join("<br>");
    li.innerHTML = `<time>${esc(e.t)}</time>${opts.lanes ? laneSpans(e, opts.active || new Set()) : "<span></span>"}
      <button class="exp" aria-expanded="false"><span class="line1"><span class="who">${esc(who)}</span>${esc(e.text)}</span><span class="detail">${detail}</span></button>`;
    const b = li.querySelector("button.exp");
    b.addEventListener("click", () => { const o = li.classList.toggle("open"); b.setAttribute("aria-expanded", String(o)); });
    return li;
  }

  // ---------- playback: real gaps between log timestamps, compressed ----------
  function player({ events, onEvent, onReset, onDone, onTick, target = 60 }) {
    let i = 0, timer = null, playing = false, speed = 1;
    const total = events.length ? events[events.length - 1].s - events[0].s : 0;
    const scale = total > 0 ? target / total : 1;          // whole run in about `target` seconds at speed 1
    const gap = (k) => (k === 0 || k >= events.length) ? 0 : Math.min(2600, Math.max(180, (events[k].s - events[k - 1].s) * scale * 1000)) / speed;
    function step() {
      if (i >= events.length) { playing = false; onDone && onDone(); onTick && onTick(i, playing); return; }
      onEvent(events[i], i); i++; onTick && onTick(i, playing);
      timer = setTimeout(step, gap(i));
    }
    return {
      play() { if (playing) return; if (i >= events.length) this.reset(); playing = true; onTick && onTick(i, playing); timer = setTimeout(step, i === 0 ? 300 : gap(i)); },
      pause() { playing = false; clearTimeout(timer); onTick && onTick(i, playing); },
      reset() { this.pause(); i = 0; onReset && onReset(); onTick && onTick(i, playing); },
      seek(n) { const was = playing; this.pause(); onReset && onReset(); i = 0; while (i < n && i < events.length) { onEvent(events[i], i, true); i++; } onTick && onTick(i, playing); if (was && i < events.length) this.play(); },
      setSpeed(s) { speed = s; },
      get index() { return i; }, get playing() { return playing; }, length: events.length,
    };
  }

  // ---------- verification in the browser ----------
  async function sha256hex(bytes) {
    const d = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(d), (b) => b.toString(16).padStart(2, "0")).join("");
  }
  const enc = new TextEncoder();
  const rawCache = {};
  async function rawFile(run, f) {
    const k = run + "/" + f;
    if (!rawCache[k]) { const r = await fetch(`data/raw/${run}/${f}`); if (!r.ok) throw new Error(`data/raw/${run}/${f}: HTTP ${r.status}`); rawCache[k] = new Uint8Array(await r.arrayBuffer()); }
    return rawCache[k];
  }
  // Recompute h_i = sha256(h_{i-1} || content_i) exactly like asd/chain.py; `tamper` = record line whose first byte is changed
  async function verifyChain(run, { tamper = null, progress } = {}) {
    const t0 = performance.now();
    const chain = JSON.parse(new TextDecoder().decode(await rawFile(run, "CHAIN.json")));
    const parts = [];
    const files = [...new Set(chain.kette.map(([n]) => n.split("#")[0]))];
    for (const f of files) {
      const b = await rawFile(run, f);
      if (f === "record.jsonl") {
        const lines = new TextDecoder().decode(b).split(/\r?\n/); if (lines[lines.length - 1] === "") lines.pop();
        lines.forEach((l, i) => {
          let s = l; if (tamper === i) s = (s[0] === "{" ? "[" : "{") + s.slice(1);
          parts.push([`record.jsonl#${i}`, enc.encode(s)]);
        });
      } else parts.push([f, b]);
    }
    let h = "0".repeat(64);
    for (let k = 0; k < parts.length; k++) {
      const [name, data] = parts[k];
      const buf = new Uint8Array(64 + data.length); buf.set(enc.encode(h)); buf.set(data, 64);
      h = await sha256hex(buf);
      progress && progress(k + 1, parts.length);
      const want = chain.kette[k];
      if (!want || want[0] !== name || want[1] !== h)
        return { ok: false, link: k + 1, name, links: chain.glieder, ms: performance.now() - t0, got: h, want: want && want[1] };
    }
    if (parts.length !== chain.glieder) return { ok: false, link: parts.length, name: "link count", links: chain.glieder, ms: performance.now() - t0 };
    return { ok: true, links: parts.length, head: h, ms: performance.now() - t0 };
  }

  let pyodide = null;
  async function loadPy(status) {
    if (pyodide) return pyodide;
    status && status("Loading Python (Pyodide, about 10 MB, once per visit)");
    await new Promise((res, rej) => { const s = document.createElement("script"); s.src = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"; s.onload = res; s.onerror = () => rej(new Error("Pyodide could not be loaded. Check the network connection, or run the command below locally.")); document.head.appendChild(s); });
    pyodide = await loadPyodide();
    return pyodide;
  }
  // Runs the unmodified check.py from the certificate folder on certificate.json; `tamper` multiplies one rate by 1001/1000
  async function verifyCert(claim, { tamper = false, status } = {}) {
    const py = await loadPy(status);
    status && status("Fetching certificate.json and check.py");
    const [code, certTxt] = await Promise.all([fetch(`data/certs/${claim}/check.py`).then((r) => r.text()), fetch(`data/certs/${claim}/certificate.json`).then((r) => r.text())]);
    let cert = certTxt, changed = null;
    if (tamper) {
      const c = JSON.parse(certTxt); const k = c.faelle[0].kanten[0];
      const [n, d] = k.f.split("/").map(BigInt); const nn = n * 1001n, dd = (d || 1n) * 1000n;
      changed = `${c.faelle[0].topologie}, edge ${k.id}: forward rate ${k.f} multiplied by 1.001`;
      k.f = `${nn}/${dd}`; cert = JSON.stringify(c);
    }
    py.FS.writeFile("/home/pyodide/certificate.json", cert);
    status && status("Running check.py on exact rational arithmetic");
    const t0 = performance.now();
    py.runPython(`import sys, io, os\nos.chdir("/home/pyodide")\nsys.argv=["check.py","certificate.json"]\n_out=io.StringIO(); _old=sys.stdout; sys.stdout=_out`);
    try { await py.runPythonAsync(code); } catch (e) { if (!String(e).includes("SystemExit")) { py.runPython("sys.stdout=_old"); throw e; } }
    const out = py.runPython("sys.stdout=_old\n_out.getvalue()").trim();
    return { pass: out.startsWith("PASS"), out, ms: performance.now() - t0, changed, cases: JSON.parse(certTxt).faelle.length };
  }

  function header(active) {
    const h = $("#top"); if (!h) return;
    const nav = [["index.html", "Runs"], ["results.html", "Results"]];
    h.innerHTML = `<a class="brand" href="index.html"><span class="qed" aria-hidden="true">∎</span>Probatum</a>
      <nav class="nav" aria-label="Main">${nav.map(([u, t]) => `<a href="${u}"${active === u ? ' aria-current="page"' : ""}>${t}</a>`).join("")}
      <a href="https://github.com/alizema700/HackNation-Ninja-Turtles">Source</a><button id="theme" class="ghost" type="button">Dark theme</button></nav>`;
    theme();
  }
  async function footer() {
    const f = $("#foot"); if (!f) return;
    try {
      const s = await site();
      f.innerHTML = `<span>Built from commit ${srcLink("frontend/build_data.py").replace(">frontend/build_data.py<", `>${esc(s.commit)}<`)} at ${esc(s.generated)} by frontend/build_data.py.</span>`;
    } catch (e) { f.textContent = ""; }
  }
  function fail(el, err, next) {
    el.innerHTML = `<p class="empty">${esc(err.message || err)}. ${next}</p>`;
  }

  return { AGENTS, AGENT_NAME, $, esc, json, site, srcLink, header, footer, toast, copy, math, qedMark, appearQed, noMark, fmtT, eventRow, player, verifyChain, verifyCert, reduced, fail };
})();
