"use strict";
(async () => {
  const { $, esc } = P;
  P.header("index.html"); P.footer();
  let s;
  try { s = await P.site(); }
  catch (e) { P.fail($("#ex-events"), e, "Run python frontend/build_data.py and serve the frontend folder over HTTP (python -m http.server -d frontend)."); return; }

  // key figures
  $("#figs").innerHTML = s.figures.map((f) => `<li>${esc(f.text)}<span class="src">Source: ${P.srcLink(f.source)}, <a href="${f.href}">details</a></span></li>`).join("")
    || `<li class="empty">No frozen results yet. Run make freeze to create results/FROZEN.json.</li>`;

  // runs
  $("#runs tbody").innerHTML = s.runs.slice().reverse().map((r) => `<tr>
      <td><a href="run.html?run=${encodeURIComponent(r.id)}">${esc(r.id)}</a></td><td>${esc(r.project)}</td>
      <td class="num">${r.duration_min} min</td><td class="num">${r.confirmed}</td><td class="num">${r.rejected}</td><td class="num">${r.deny ?? ""}</td>
      <td>${r.chain.links} links, head <span class="mono">${esc(r.chain.head.slice(0, 12))}</span></td></tr>`).join("");

  // live excerpt
  const ex = s.excerpt;
  if (!ex) { $("#ex-events").innerHTML = `<li class="empty">No run with a rejected and a confirmed claim yet. Start one with python -m asd.cli and re-run build_data.py.</li>`; return; }
  $("#ex-src").innerHTML = `Run <a href="run.html?run=${encodeURIComponent(ex.run)}">${esc(ex.run)}</a>, project ${esc(ex.project)}. Rows come from ${P.srcLink(ex.source)}; times in UTC.`;
  const claims = Object.fromEntries(ex.claims.map((c) => [c.id, c]));
  const list = $("#ex-events"), box = $("#ex-claims");

  function claimBlock(c, animate) {
    const d = document.createElement("div");
    d.className = `claim-block ${c.verdict ? "ok" : "no"}`;
    d.innerHTML = `<div class="claim-head"><span class="small muted">${c.verdict ? esc(c.id) : "Submitted claim"}, ${esc(c.t)} UTC</span></div>
      <p class="claim">${esc(c.text)}</p>
      <div class="verdict-line"><span class="mark"></span><span class="tag ${c.verdict ? "ok" : "no"}">${c.verdict ? `Confirmed, ${esc(c.level)}` : "Rejected"}</span></div>
      <p class="small muted">${esc(c.reason)}</p>
      ${c.verdict && c.certificate ? `<p class="small" style="margin-top:8px"><a href="run.html?run=${encodeURIComponent(ex.run)}&claim=${encodeURIComponent(c.id)}#evidence">Re-verify this certificate in your browser</a></p>` : ""}`;
    const m = d.querySelector(".mark");
    if (c.verdict) { if (animate) P.appearQed(m); else m.appendChild(P.qedMark(true)); }
    else m.innerHTML = `<span class="qed-big no-mark" role="img" aria-label="Rejected by the verifier">✕</span>`;
    return d;
  }
  // only the latest rejection and the confirmation stay visible: one claim rejected with its reason, the next confirmed
  function showClaim(id, animate) {
    const c = claims[id]; if (!c) return;
    const blocks = [...box.children];
    if (!c.verdict) box.innerHTML = "";
    else if (blocks.length > 1) blocks.slice(0, -1).forEach((b) => b.remove());
    box.appendChild(claimBlock(c, animate));
  }
  const pl = P.player({
    events: ex.events, target: 14,
    onReset: () => { list.innerHTML = ""; box.innerHTML = `<p class="empty">Waiting for the verifier.</p>`; },
    onEvent: (e, i, instant) => {
      if (box.querySelector(".empty")) box.innerHTML = "";
      list.appendChild(P.eventRow(e));
      if (e.claim_ref) showClaim(e.claim_ref, !instant);
    },
    onTick: (i, playing) => { $("#replay").textContent = playing ? "Pause" : (i >= ex.events.length ? "Replay run" : (i ? "Resume" : "Replay run")); },
  });
  $("#replay").addEventListener("click", () => pl.playing ? pl.pause() : pl.play());
  if (P.reduced()) pl.seek(ex.events.length); else pl.play();
})();
