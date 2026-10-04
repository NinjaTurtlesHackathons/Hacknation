"use strict";
(async () => {
  const { $, esc, AGENTS, AGENT_NAME } = P;
  P.header(""); P.footer();
  const qs = new URLSearchParams(location.search);
  let s, R;
  try {
    s = await P.site();
    const id = qs.get("run") || s.runs[s.runs.length - 1].id;
    R = await P.json(`data/runs/${encodeURIComponent(id)}.json`);
  } catch (e) {
    P.fail($("#events"), e, "Pick a run from the list on the start page, or rebuild the data with python frontend/build_data.py.");
    return;
  }
  const M = R.meta, EV = R.events;
  document.title = `Run ${M.id} · Probatum Lab`;
  $("#title").textContent = `Run ${M.id}`;
  $("#task").textContent = M.task || "";
  $("#meta").innerHTML = `Project ${esc(M.project)}, Omnigent session <span class="mono">${esc(M.session)}</span>, ${M.duration_min} minutes, ${M.events} events. Sources: ${M.sources.map(P.srcLink).join(", ")}.`;

  // ---------- rounds ----------
  $("#rounds").innerHTML = R.rounds.map((r, i) => `<li data-id="${esc(r.id)}" class="future">
      <h3 class="small">Round ${i + 1}, question ${esc(r.id)}</h3>
      <p class="q"${r.lang === "de" ? ' lang="de"' : ""}>${esc(r.text)}</p>
      <p class="small muted">${esc(r.start_t)} to ${esc(r.end_t)} UTC. ${r.experiments} experiment${r.experiments === 1 ? "" : "s"}, ${r.confirmed} confirmed, ${r.rejected} rejected.${r.source && r.source.startsWith("agent:") ? ` Proposed by the ${esc(r.source.slice(6))}.` : ""}</p></li>`).join("")
    || `<li class="empty">This run logged no questions.</li>`;
  P.math($("#rounds"));

  // ---------- lanes ----------
  const used = AGENTS.filter((a) => M.agents.includes(a));
  const lanesW = used.length * 12;
  document.documentElement.style.setProperty("--lanes-w", lanesW + "px");
  $("#lane-head").style.setProperty("--n", used.length);
  $("#lane-head").innerHTML = `<span></span><div class="lane-names" style="--n:${used.length}" aria-hidden="true">${used.map((a) => `<span>${AGENT_NAME[a]}</span>`).join("")}</div><span class="sr-only">Agent lanes from left to right: ${used.map((a) => AGENT_NAME[a]).join(", ")}</span><span></span>`;
  // agent is "active" in its lane between its first and last event
  const span = {}; EV.forEach((e, i) => [e.agent, e.to].filter(Boolean).forEach((a) => { span[a] = span[a] || [i, i]; span[a][1] = i; }));
  const activeAt = (i) => new Set(used.filter((a) => span[a] && span[a][0] <= i && i <= span[a][1]));
  P.AGENTS.splice(0, P.AGENTS.length, ...used);   // lanes render only the agents of this run

  // ---------- claims ----------
  const claims = Object.fromEntries(R.claims.map((c) => [c.id, c]));
  let selected = qs.get("claim");
  function registerRow(c, animate) {
    const li = document.createElement("li");
    li.innerHTML = `<button type="button" aria-pressed="false" data-id="${esc(c.id)}"><span class="m"></span><span>${c.verdict ? esc(c.id) : "Rejected submission"}<br><span class="small muted">${esc(c.verdict ? c.level : c.reason.slice(0, 64) + (c.reason.length > 64 ? "…" : ""))}</span></span><span class="small muted">${esc(c.t)}</span></button>`;
    const m = li.querySelector(".m");
    if (c.verdict) { if (animate) P.appearQed(m).style.fontSize = "var(--s21)"; else { const q = P.qedMark(false); m.appendChild(q); } }
    else m.innerHTML = P.noMark();
    li.querySelector("button").addEventListener("click", () => select(c.id, true));
    $("#register").appendChild(li);
  }
  function select(id, user) {
    selected = id; const c = claims[id]; if (!c) return;
    document.querySelectorAll("#register button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.id === id)));
    const box = $("#claim");
    const cmd = c.certificate ? `cd projects/${M.project}/certificates/${c.id} && python3 check.py` : `python -m asd.recheck proofreading --projekt ${M.project} --claim ${c.id}`;
    box.innerHTML = `<div class="claim-block ${c.verdict ? "ok" : "no"}">
        <div class="claim-head"><span class="small muted">${c.verdict ? esc(c.id) : "Rejected submission"}, verifier verdict at ${esc(c.t)} UTC</span></div>
        <p class="claim">${esc(c.text)}</p>
        <div class="verdict-line"><span class="mark"></span><span class="tag ${c.verdict ? "ok" : "no"}">${c.verdict ? `Confirmed, ${esc(c.level)}` : "Rejected, stays a hypothesis"}</span></div>
        <p class="small muted">Verifier: ${esc(c.reason)}</p>
        ${c.surprise ? `<p class="small" style="margin-top:8px">Contradicts the preregistered assumption: ${esc(c.surprise)}</p>` : ""}
        ${c.red_team && c.red_team.length ? `<p class="small" style="margin-top:8px">Red team: ${c.red_team.length} counter-check${c.red_team.length === 1 ? "" : "s"}, ${c.red_team.filter((r) => r.contradiction).length} contradictions.</p><ul class="redteam">${c.red_team.map((r) => `<li>${esc(r.text)}</li>`).join("")}</ul>` : ""}
      </div>
      ${c.verdict ? `<div class="cert" style="margin-top:16px">
        <h3>Certificate</h3>
        ${c.certificate ? `<p class="small muted">certificate.json holds every exact rational rate; check.py uses only the Python standard library and imports nothing from the lab. It runs here unmodified.</p>
          <div class="row" style="margin-top:8px"><button type="button" id="cv">Re-verify</button><button type="button" id="ct">Tamper and re-verify</button><button type="button" class="ghost" id="cc">Copy command</button></div>
          <div class="result" id="cr" aria-live="polite"></div><div class="out" id="co"></div>`
          : `<p class="small muted">${esc(c.standalone_note)}.</p><div class="row" style="margin-top:8px"><button type="button" class="ghost" id="cc">Copy command</button></div>`}
      </div>` : ""}`;
    const m = box.querySelector(".mark");
    if (c.verdict) m.appendChild(P.qedMark(true)); else m.innerHTML = `<span class="qed-big no-mark" role="img" aria-label="Rejected by the verifier">✕</span>`;
    const cc = box.querySelector("#cc"); if (cc) cc.addEventListener("click", () => P.copy(cmd));
    if (c.certificate) {
      const run = async (tamper) => {
        const res = $("#cr"), out = $("#co"); const btns = box.querySelectorAll(".cert button"); btns.forEach((b) => (b.disabled = true));
        out.textContent = ""; res.innerHTML = `<span class="small muted">Starting</span>`;
        try {
          const r = await P.verifyCert(c.id, { tamper, status: (t) => (res.innerHTML = `<span class="small muted">${esc(t)}</span>`) });
          res.innerHTML = "";
          if (r.pass) { const q = P.appearQed(res); q.style.fontSize = "var(--s21)"; res.insertAdjacentHTML("beforeend", `<span class="tag ok">PASS for all ${r.cases} cases, recomputed in your browser in ${(r.ms / 1000).toFixed(1)} s</span>`); }
          else res.innerHTML = `${P.noMark()}<span class="tag no">FAIL${r.changed ? " after tampering" : ""}</span>`;
          out.textContent = (r.changed ? `Changed: ${r.changed}\n` : "") + r.out;
        } catch (e) { res.innerHTML = `<span class="tag no">${esc(e.message || e)}</span>`; out.textContent = `Run it locally instead:\n${cmd}`; }
        btns.forEach((b) => (b.disabled = false));
      };
      $("#cv").addEventListener("click", () => run(false));
      $("#ct").addEventListener("click", () => run(true));
    }
    if (user && window.matchMedia("(max-width: 1099px)").matches) box.scrollIntoView({ block: "start", behavior: P.reduced() ? "auto" : "smooth" });
  }
  function emptyClaim() { $("#claim").innerHTML = `<p class="empty">No verifier verdict yet. Replay the run, or choose Show all events.</p>`; }

  // ---------- hash chain ----------
  const ch = M.chain;
  const recLine = EV.find((e) => e.kind === "ok" && e.line != null)?.line ?? 0;
  $("#chain").innerHTML = `<h3>Hash chain</h3>
    <p class="small muted">Every record line, the decisions log, the preregistration, the lab state and each session export are chained: each link is sha256 of the previous link and the content. Sealed ${esc(ch.sealed)} UTC, ${ch.links} links.</p>
    <p class="hash" style="margin-top:8px">head ${esc(ch.head)}</p>
    <div class="row" style="margin-top:8px"><button type="button" id="hv">Re-verify</button><button type="button" id="ht">Tamper and re-verify</button><button type="button" class="ghost" id="hc">Copy command</button></div>
    <div class="result" id="hr" aria-live="polite"></div>`;
  const chainRun = async (tamper) => {
    const res = $("#hr"); const b = $("#chain").querySelectorAll("button"); b.forEach((x) => (x.disabled = true));
    try {
      const r = await P.verifyChain(M.id, { tamper: tamper ? recLine : null, progress: (k, n) => (res.innerHTML = `<span class="small muted">Hashing link ${k} of ${n}</span>`) });
      res.innerHTML = "";
      if (r.ok) { const q = P.appearQed(res); q.style.fontSize = "var(--s21)"; res.insertAdjacentHTML("beforeend", `<span class="tag ok">Intact: ${r.links} links recomputed in ${Math.round(r.ms)} ms, head matches</span>`); }
      else res.innerHTML = `${P.noMark()}<span class="tag no">Broken at link ${r.link} of ${r.links} (${esc(r.name)})${tamper ? `: record line ${recLine + 1} had one character changed` : ""}</span>`;
    } catch (e) { res.innerHTML = `<span class="tag no">${esc(e.message || e)}. Run the command locally instead.</span>`; }
    b.forEach((x) => (x.disabled = false));
  };
  $("#hv").addEventListener("click", () => chainRun(false));
  $("#ht").addEventListener("click", () => chainRun(true));
  $("#hc").addEventListener("click", () => P.copy(`python -m asd.chain verify runs/omnigent/${M.id}`));

  // ---------- playback ----------
  const list = $("#events"), scroll = $("#scroll");
  let follow = true;
  scroll.addEventListener("scroll", () => { follow = scroll.scrollTop + scroll.clientHeight >= scroll.scrollHeight - 24; });
  const roundIds = R.rounds.map((r) => r.id);
  function setRound(rid) {
    const k = rid ? roundIds.indexOf(rid) : -1;
    document.querySelectorAll("#rounds li").forEach((li, j) => { li.classList.toggle("active", j === k); li.classList.toggle("future", j > k); });
  }
  let seen = new Set(), lastSeen = null;
  function afterSeek() {
    if (selected && seen.has(selected)) select(selected, false);
    else if (lastSeen) select(lastSeen, false); else emptyClaim();
    scroll.scrollTop = scroll.scrollHeight;
  }
  const pl = P.player({
    events: EV, target: 75,
    onReset: () => { list.innerHTML = ""; $("#register").innerHTML = ""; emptyClaim(); setRound(null); seen = new Set(); lastSeen = null; },
    onEvent: (e, i, instant) => {
      list.querySelector(".current")?.classList.remove("current");
      const row = P.eventRow(e, { lanes: true, active: activeAt(i) }); if (!instant) row.classList.add("current");
      list.appendChild(row);
      if (e.claim_ref && claims[e.claim_ref]) {
        registerRow(claims[e.claim_ref], !instant); seen.add(e.claim_ref); lastSeen = e.claim_ref;
        if (!instant) select(e.claim_ref, false);
      }
      if (e.round) setRound(e.round);
      if (follow && !instant) scroll.scrollTop = scroll.scrollHeight;
    },
    onTick: (i, playing) => {
      $("#play").textContent = playing ? "Pause" : (i >= EV.length ? "Replay run" : (i ? "Resume" : "Replay run"));
      $("#scrub").value = i; const e = EV[Math.max(0, i - 1)];
      $("#pos").textContent = i ? `Event ${i} of ${EV.length}, ${e.t} UTC` : `${EV.length} events`;
    },
  });
  $("#scrub").max = EV.length;
  $("#play").addEventListener("click", () => (pl.playing ? pl.pause() : pl.play()));
  const seek = (n) => { pl.seek(n); afterSeek(); };
  $("#end").addEventListener("click", () => seek(EV.length));
  $("#speed").addEventListener("change", (e) => pl.setSpeed(parseFloat(e.target.value)));
  $("#scrub").addEventListener("input", (e) => seek(parseInt(e.target.value, 10)));
  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, select, textarea, button")) return;
    if (e.key === " ") { e.preventDefault(); pl.playing ? pl.pause() : pl.play(); }
    if (e.key === "ArrowRight") seek(Math.min(EV.length, pl.index + 1));
    if (e.key === "ArrowLeft") seek(Math.max(0, pl.index - 1));
  });

  // a deep link to a claim shows the finished run; otherwise the run plays
  if (qs.has("at")) seek(Math.min(EV.length, parseInt(qs.get("at"), 10)));
  else if (selected || P.reduced() || qs.has("end")) { seek(EV.length); if (location.hash === "#evidence") $("#evidence").scrollIntoView(); }
  else { pl.reset(); pl.play(); }
})();
