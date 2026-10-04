// 40 s cinematic replay of a real Omnigent run. Every text, time and verdict comes from data/runs/<run>.json
// (built from runs/omnigent/<run>/ by frontend/build_data.py); only the pacing and camera are staged.
"use strict";
(async () => {
  const qs = new URLSearchParams(location.search), RUN = qs.get("run") || "2026-10-04b";
  if (qs.has("rec")) document.body.classList.add("rec");
  const $ = (s) => document.querySelector(s), frame = $("#frame"), cam = $("#cam");
  const fit = () => { const s = Math.min(innerWidth / 1920, innerHeight / 1080); frame.style.transform = `scale(${s})`;
    frame.style.position = "absolute"; frame.style.left = (innerWidth - 1920 * s) / 2 + "px"; frame.style.top = (innerHeight - 1080 * s) / 2 + "px"; };
  addEventListener("resize", fit); fit();
  const R = await (await fetch(`data/runs/${RUN}.json`)).json();
  const E = R.events, M = R.meta, C = Object.fromEntries(R.claims.map((c) => [c.id, c]));
  const find = (pred, from = 0) => E.findIndex((e, i) => i >= from && pred(e));
  const math = (t) => String(t || "").replace(/\$\\eta < e\^\{-2\\Delta\} = 10\^\{-4\}\$/g, "η < e^(−2Δ) = 10⁻⁴").replace(/\$\\eta \\ge 1\/D\^2\$/g, "η ≥ 1/D²")
    .replace(/\$\\eta \\le e\^\{-2\\Delta\} = 10\^\{-4\}\$/g, "η ≤ e^(−2Δ) = 10⁻⁴").replace(/\$/g, "");
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // ---------- agents ----------
  const POS = { lead: [300, 560], scout: [180, 330], planner: [480, 300], researcherA: [820, 430], researcherB: [820, 650], redteam: [560, 770], learner: [170, 790] };
  const NAME = { lead: ["Lead", "Omnigent"], scout: ["Scout", "policy check"], planner: ["Planner", "chooses experiments"], researcherA: ["Researcher", "option O1"],
                 researcherB: ["Researcher", "option O2"], redteam: ["Red team", "attacks results"], learner: ["Learner", "follow-up questions"] };
  const nodes = {};
  for (const [k, [x, y]] of Object.entries(POS)) {
    const d = document.createElement("div"); d.className = "node" + (k === "lead" ? " lead" : ""); d.style.left = x + "px"; d.style.top = y + "px";
    d.innerHTML = `<div><div class="nm">${NAME[k][0]}</div><div class="rl">${NAME[k][1]}</div></div><span class="badge">DENIED</span>`;
    $("#agents").appendChild(d); nodes[k] = d;
  }
  const svg = $("#wires"), NS = "http://www.w3.org/2000/svg";
  function wire(to) {
    const [x1, y1] = POS.lead, [x2, y2] = POS[to], p = document.createElementNS(NS, "path");
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - 40;
    p.setAttribute("d", `M${x1},${y1} Q${mx},${my} ${x2},${y2}`); p.setAttribute("class", "wire"); svg.appendChild(p);
    const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L;
    p.animate([{ strokeDashoffset: L }, { strokeDashoffset: 0 }], { duration: 700, easing: "cubic-bezier(.6,0,.2,1)", fill: "forwards" });
    const dot = document.createElementNS(NS, "circle"); dot.setAttribute("r", 8); dot.setAttribute("class", "pulse"); svg.appendChild(dot);
    const t0 = performance.now();
    (function mv(t) { const k = Math.min(1, (t - t0) / 700), pt = p.getPointAtLength(L * k); dot.setAttribute("cx", pt.x); dot.setAttribute("cy", pt.y);
      if (k < 1) requestAnimationFrame(mv); else { dot.remove(); setTimeout(() => p.classList.add("dim"), 900); } })(t0);
    nodes[to].classList.add("on"); hot(to);
  }
  function hot(k, ms = 1300) { nodes[k].classList.add("hot", "on"); setTimeout(() => nodes[k].classList.remove("hot"), ms); }
  function deny(k) { nodes[k].classList.add("deny", "on"); setTimeout(() => nodes[k].classList.remove("deny"), 1500); }

  // ---------- ticker, clock, camera ----------
  const tick = (i) => { if (i < 0) return; const e = E[i], d = document.createElement("div"); d.className = "k-" + e.kind;
    d.innerHTML = `<time>${e.t}</time><b>${esc({ redteam: "Red team" }[e.agent] || e.agent[0].toUpperCase() + e.agent.slice(1))}</b><span>${esc(e.text)}</span>`;
    const T = $("#ticker"); T.appendChild(d); while (T.children.length > 4) T.firstChild.remove(); $("#clock").innerHTML = `${e.t}<small>UTC</small>`; };
  const camera = (s, x = 0, y = 0) => { cam.style.transform = `translate(${x}px,${y}px) scale(${s})`; };
  const banner = (html, cls = "", ms = 2600) => { const b = $("#banner"); b.className = cls; b.innerHTML = html; void b.offsetWidth; b.classList.add("on"); setTimeout(() => b.classList.remove("on"), ms); };
  const shake = () => { frame.classList.remove("shake"); void frame.offsetWidth; frame.classList.add("shake"); };
  function typeQ(label, text, ms = 2400) {
    const q = $("#q"); q.innerHTML = `<span class="lab">${esc(label)}</span><span class="tx"></span><span class="caret"></span>`;
    const tx = q.querySelector(".tx"), t0 = performance.now();
    (function ty(t) { const k = Math.min(1, (t - t0) / ms); tx.textContent = text.slice(0, Math.round(text.length * k)); if (k < 1) requestAnimationFrame(ty); else q.querySelector(".caret").remove(); })(t0);
  }

  // ---------- lanes and claims ----------
  function lane(id, who, sub) { const d = document.createElement("div"); d.className = "lane"; d.id = id;
    d.innerHTML = `<div class="ln">${esc(who)}<small>${esc(sub)}</small></div><div class="bar"><i></i></div><div class="ex">waiting</div>`; $("#lanes").appendChild(d);
    requestAnimationFrame(() => d.classList.add("on")); return d; }
  const laneSet = (id, i, pct) => { const d = $("#" + id); if (!d || i < 0) return; d.querySelector(".ex").textContent = E[i].text.replace(/ for F\d+, option O\d/, "");
    d.querySelector(".bar i").style.width = pct + "%"; tick(i); };
  const cards = {};
  function card(cid, i) {
    const c = C[cid] || {}, e = E[i], d = document.createElement("div"); d.className = "card";
    d.innerHTML = `<div class="cid">${esc(c.verdict ? cid : "submitted claim")} · ${e.t} UTC</div><div class="ct">${esc(c.text)}</div>
      <span class="verdict"></span><div class="cr"></div><span class="slash"></span><span class="xmark">✕</span><span class="stamp">∎</span><span class="shield"></span>`;
    const box = $("#claims"); box.appendChild(d); while (box.querySelectorAll(".card").length > 3) box.querySelector(".card").remove();
    requestAnimationFrame(() => d.classList.add("in")); cards[cid] = d;
    setTimeout(() => {
      d.classList.add(c.verdict ? "ok" : "no"); tick(i);
      d.querySelector(".verdict").textContent = c.verdict ? `Confirmed by the verifier · ${c.level}` : "Rejected by the verifier";
      d.querySelector(".cr").textContent = c.reason;
      if (!c.verdict) shake();
    }, 900);
  }
  const shield = (cid, i) => { const d = cards[cid]; if (d && i >= 0) { d.querySelector(".shield").textContent = "red team: claim stands"; d.classList.add("rt"); } tick(i); };

  // ---------- the real events this replay shows ----------
  const ix = {
    hScout: find((e) => e.kind === "handoff" && e.to === "scout"), hPlan: find((e) => e.kind === "handoff" && e.to === "planner"),
    deny1: find((e) => e.kind === "deny" && e.agent === "planner"),
    o2: find((e) => /^Chooses O2/.test(e.text)), o1: find((e) => /^Chooses O1/.test(e.text)),
    hR1: find((e) => e.kind === "handoff" && /O1$/.test(e.text)), hR2: find((e) => e.kind === "handoff" && /researcher O2$/.test(e.text)),
  };
  ix.exA = find((e) => /Runs experiment/.test(e.text) && /O1$/.test(e.text)); ix.exB = find((e) => /Runs experiment/.test(e.text) && /O2$/.test(e.text));
  ix.exA2 = find((e) => /Runs experiment/.test(e.text) && /O1$/.test(e.text), ix.exA + 1); ix.exB2 = find((e) => /Runs experiment/.test(e.text) && /O2$/.test(e.text), ix.exB + 1);
  ix.exB3 = find((e) => /Runs experiment/.test(e.text) && /O2$/.test(e.text), ix.exB2 + 1);
  ix.rej = find((e) => e.kind === "no"); ix.ok1 = find((e) => e.kind === "ok"); ix.ok2 = find((e) => e.kind === "ok", ix.ok1 + 1);
  ix.reopen = find((e) => e.kind === "policy" && /Reopens/.test(e.text)); ix.next = find((e) => /recommends F\d/.test(e.text), ix.reopen);
  ix.hRT1 = find((e) => e.kind === "handoff" && e.to === "redteam"); ix.hRT2 = find((e) => e.kind === "handoff" && e.to === "redteam", ix.hRT1 + 1);
  ix.vote1 = find((e) => /Red-team vote on/.test(e.text) && /[1-9]\d* counter-checks/.test(e.text));
  ix.vote2 = find((e) => /Red-team vote on/.test(e.text) && /[1-9]\d* counter-checks/.test(e.text), ix.vote1 + 1);
  ix.hLearn = find((e) => e.kind === "handoff" && e.to === "learner"); ix.ok3 = find((e) => e.kind === "ok", ix.ok2 + 1);
  const r1 = R.rounds[0], r2 = R.rounds[1];
  const claimOf = (i) => E[i] && E[i].claim_ref;
  const voteClaim = (i) => (E[i] && (E[i].text.match(/vote on (\S+):/) || [])[1]);

  const TL = [
    [0, () => { $("#runlab").textContent = `run ${M.id} · project ${M.project}`; camera(1); typeQ(`Round 1 · question ${r1.id}`, math(r1.text), 2600); }],
    [3300, () => { camera(1.1, 120, -10); wire("scout"); tick(ix.hScout); }],
    [3900, () => { wire("planner"); tick(ix.hPlan); }],
    [5000, () => { deny("planner"); tick(ix.deny1); }],
    [6600, () => { hot("planner", 2400); tick(ix.o2); banner(`Planner: two rival experiments, in parallel<small>${esc(E[ix.o2].text.split(": ").slice(1).join(": "))}</small>`, "blue", 2800); }],
    [8400, () => tick(ix.o1)],
    [10000, () => { camera(1.02, 0, -30); wire("researcherA"); tick(ix.hR1); lane("la", "Researcher", "option O1 · broad scan"); }],
    [10500, () => { wire("researcherB"); tick(ix.hR2); lane("lb", "Researcher", "option O2 · deep computation"); }],
    [11400, () => { laneSet("la", ix.exA, 45); laneSet("lb", ix.exB, 40); }],
    [12800, () => { laneSet("la", ix.exA2, 90); laneSet("lb", ix.exB2, 70); }],
    [14000, () => laneSet("lb", ix.exB3, 100)],
    [15200, () => { camera(1.14, -270, 30); card(claimOf(ix.rej), ix.rej); }],
    [18600, () => { card(claimOf(ix.ok1), ix.ok1); }],
    [21300, () => { card(claimOf(ix.ok2), ix.ok2); }],
    [24400, () => { camera(1.1, 150, 40); hot("planner", 3600); tick(ix.reopen);
      banner(`Surprise: ${esc(claimOf(ix.ok2))} contradicts the preregistered assumption A1<small>${esc((E[ix.reopen].text.split(": ").slice(1).join(": ")))}</small>`, "", 3400); }],
    [27200, () => { tick(ix.next); if (r2) typeQ(`Plan changed · round 2 · question ${r2.id}`, math(r2.text), 1600); }],
    [29000, () => { camera(1.04, 40, -40); wire("redteam"); tick(ix.hRT1); }],
    [29600, () => { wire("redteam"); tick(ix.hRT2); }],
    [31000, () => shield(voteClaim(ix.vote1), ix.vote1)],
    [32200, () => shield(voteClaim(ix.vote2), ix.vote2)],
    [33300, () => { camera(1.1, -250, 20); wire("learner"); tick(ix.hLearn); card(claimOf(ix.ok3), ix.ok3); }],
    [36200, () => { camera(1); const ch = $("#chain"); ch.innerHTML = Array.from({ length: M.chain.links }, () => "<i></i>").join(""); ch.classList.add("on");
      const L = $("#chainlab"); L.textContent = `hash chain · ${M.chain.links} links · every record line, decision and session export`; L.classList.add("on");
      [...ch.children].forEach((b, k) => setTimeout(() => b.classList.add("lit"), k * 26));
      setTimeout(() => { L.textContent = `hash chain intact · ${M.chain.links} links · head ${M.chain.head.slice(0, 12)} · sealed ${M.chain.sealed.replace("T", " ")} UTC`; }, M.chain.links * 26 + 100); }],
    [38400, () => { const d = $("#end"); d.innerHTML = `<div class="big">∎</div>
      <div class="stats"><div class="ok"><b>${M.confirmed}</b>confirmed</div><div class="no"><b>${M.rejected}</b>rejected</div><div class="pol"><b>${M.deny}</b>policy denials</div><div><b>${M.chain.links}</b>chain links</div></div>
      <div class="src">real run ${M.id} · ${M.duration_min} min compressed to 40 s · source runs/omnigent/${M.id}/</div>`; d.classList.add("on"); }],
  ];
  let timers = [], t0 = 0;
  function reset() {
    timers.forEach(clearTimeout); timers = []; svg.innerHTML = ""; $("#lanes").innerHTML = ""; $("#ticker").innerHTML = "";
    document.querySelectorAll(".card").forEach((c) => c.remove()); Object.values(nodes).forEach((n) => (n.className = n.className.replace(/ (on|hot|deny)/g, "")));
    ["#chain", "#chainlab", "#end", "#banner"].forEach((s) => $(s).classList.remove("on")); $("#chain").innerHTML = ""; $("#q").innerHTML = ""; $("#clock").textContent = "";
  }
  function play() {
    reset(); t0 = performance.now();
    TL.forEach(([t, fn]) => timers.push(setTimeout(() => { try { fn(); } catch (e) { console.error(e); } }, t)));
    (function pr(t) { const k = Math.min(1, (t - t0) / 40000); $("#prog").style.width = k * 100 + "%"; if (k < 1) requestAnimationFrame(pr); })(t0);
  }
  $("#play").addEventListener("click", play);
  document.fonts && document.fonts.ready.then(() => setTimeout(play, qs.has("rec") ? 600 : 300));
})();
