"use strict";
(async () => {
  const { $, esc } = P;
  P.header("results.html"); P.footer();
  let s, X;
  try { [s, X] = await Promise.all([P.site(), P.json("data/results.json")]); }
  catch (e) { P.fail($("#a-body"), e, "Rebuild the data with python frontend/build_data.py."); return; }
  const copyBtn = (cmd) => `<button type="button" class="link" data-copy="${esc(cmd)}">Copy command</button>`;
  const src = (path, cmd) => `<p class="src">Source: ${P.srcLink(path)}${cmd ? `. Regenerate: <code>${esc(cmd)}</code> ${copyBtn(cmd)}` : ""}</p>`;
  const fmt = (x, d = 1) => (x == null ? "" : Number(x).toFixed(d));
  const fmtP = (p) => (p == null ? "" : p < 0.001 ? "< 0.001" : p.toFixed(3));
  $("#frozen").innerHTML = X.frozen_at ? `Numbers frozen at ${esc(X.frozen_at)} from commit ${esc(X.commit)} by asd.freeze; nothing on this page is typed by hand.` : "No frozen snapshot yet. Run make freeze.";

  // ---------- acceleration: dot plot of verifier calls until the target claim ----------
  const rp = X.replay;
  if (rp) {
    const conds = rp.conditions; const W = 760, rowH = 44, L = 210, Rm = 24, top = 16, H = top + conds.length * rowH + 40;
    const maxN = rp.budget; const x = (n) => L + (Math.log(n) / Math.log(maxN)) * (W - L - Rm);
    let g = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="a-cap"><title id="a-cap">Verifier calls until the target claim, per seed and condition (log scale, budget ${maxN})</title>`;
    [1, 2, 5, 10, 20, maxN].forEach((t) => { g += `<line class="axis" x1="${x(t)}" x2="${x(t)}" y1="${top}" y2="${H - 32}"/><text x="${x(t)}" y="${H - 14}" text-anchor="middle">${t}</text>`; });
    g += `<text x="${W - Rm}" y="${H - 1}" text-anchor="end">verifier calls until the target claim (log scale)</text>`;
    conds.forEach((c, k) => {
      const y = top + k * rowH + rowH / 2;
      g += `<text class="lbl" x="0" y="${y + 4}">${esc(c.name)}</text>`;
      const cnt = {};
      c.N.forEach((n) => { const j = (cnt[n] = (cnt[n] || 0) + 1) - 1; const dy = ((j % 5) - 2) * 4; g += `<circle class="dot ${c.key === "LAB" ? "" : "base"}" cx="${x(n)}" cy="${y + dy}" r="4"><title>${esc(c.name)}: ${n} calls</title></circle>`; });
      if (c.median != null) g += `<line class="med" x1="${x(c.median)}" x2="${x(c.median)}" y1="${y - 14}" y2="${y + 14}"><title>median ${c.median}</title></line>`;
    });
    g += `</svg>`;
    const tests = rp.tests.map((t) => `<tr><td>${esc(t.id)}</td><td>${esc(t.vs)}</td><td class="num">${fmt(t.speedup, 2)}×</td><td class="num">${fmt(t.ci[0], 2)} to ${fmt(t.ci[1], 2)}</td><td class="num">${fmtP(t.p)}</td><td class="num">${fmtP(t.p_bh)}</td><td class="num">${t.n}</td><td>${t.supported ? `<span class="tag ok">supported</span>` : `<span class="tag no">not supported</span>`}</td></tr>`).join("");
    const lab = conds.find((c) => c.key === "LAB");
    $("#a-body").innerHTML = `<p class="measure">Replay benchmark preregistered in ${esc(rp.prereg)}: the same lattice question, ${rp.seeds.length} seeds (${rp.seeds[0]} to ${rp.seeds[rp.seeds.length - 1]}), at most ${rp.budget} verifier calls. Each dot is one seed; the bar is the median. ${lab ? `The lab reached the target claim in ${lab.hits} of ${lab.N.length} seeds.` : ""} The oracle is an analytic bound, not a run.</p>
      ${g}
      <div class="tablewrap" style="margin-top:16px"><table><thead><tr><th>Test</th><th>Lab against</th><th class="num">Speedup</th><th class="num">95% CI</th><th class="num">p</th><th class="num">p (Benjamini-Hochberg)</th><th class="num">Seeds</th><th>Outcome</th></tr></thead><tbody>${tests}</tbody></table></div>
      <p class="small muted measure" style="margin-top:8px">Speedup is the ratio of mean verifier calls; the interval is a paired bootstrap, p a paired permutation test. A hypothesis counts as supported only if p &lt; 0.05 after correction and the interval excludes 1.</p>
      ${src(rp.source, "python -m benchmarks.replay_lattice --nur-auswertung")}`;
  } else $("#a-body").innerHTML = `<p class="empty">No replay benchmark yet. Run python -m benchmarks.replay_lattice --seeds 10.</p>`;

  // ---------- trust: share of wrong answers with 95% CI ----------
  const tr = X.trust;
  if (tr) {
    const W = 760, L = 210, Rm = 24, rowH = 40, top = 8, H = top + tr.conditions.length * rowH + 40; const x = (v) => L + (v / 100) * (W - L - Rm);
    let g = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="t-cap"><title id="t-cap">Share of wrong answers per condition with 95% Clopper-Pearson interval</title>`;
    [0, 25, 50, 75, 100].forEach((t) => { g += `<line class="axis" x1="${x(t)}" x2="${x(t)}" y1="${top}" y2="${H - 32}"/><text x="${x(t)}" y="${H - 14}" text-anchor="middle">${t}%</text>`; });
    tr.conditions.forEach((c, k) => {
      const y = top + k * rowH + rowH / 2;
      g += `<text class="lbl" x="0" y="${y + 4}">${esc(c.name)}</text><line class="ci" x1="${x(c.wrong_ci[0])}" x2="${x(c.wrong_ci[1])}" y1="${y}" y2="${y}"/><circle class="pt" cx="${x(c.wrong_pct)}" cy="${y}" r="5"><title>${esc(c.name)}: ${c.wrong_pct}% wrong</title></circle>`;
    });
    g += `<text x="${W - Rm}" y="${H - 1}" text-anchor="end">wrong answers, share of all answers</text></svg>`;
    $("#t-body").innerHTML = `<p class="measure">${esc(tr.question_source)}. An answer counts as wrong when it is stated and false; unknown answers are counted separately.</p>${g}
      <div class="tablewrap"><table><thead><tr><th>Condition</th><th class="num">Answers</th><th class="num">Right</th><th class="num">Wrong</th><th class="num">Unknown</th><th class="num">Wrong, 95% CI</th></tr></thead><tbody>
      ${tr.conditions.map((c) => `<tr><td>${esc(c.name)}</td><td class="num">${c.n}</td><td class="num">${c.right}</td><td class="num">${c.wrong}</td><td class="num">${c.unknown ?? ""}</td><td class="num">${fmt(c.wrong_pct)}% (${fmt(c.wrong_ci[0])} to ${fmt(c.wrong_ci[1])})</td></tr>`).join("")}</tbody></table></div>
      ${src(tr.source, "python -m asd.freeze")}`;
  }

  // ---------- stress ----------
  const st = X.stress;
  if (st && st.blind_claims != null) {
    const sc = st.selbsttest_faelle || {};
    $("#st-body").innerHTML = `<ul class="figs">
      <li>${st.blind_claims - st.blind_akzeptiert} of ${st.blind_claims} random or constant claim submissions, sent blind to the frozen harness, were rejected.</li>
      <li>${st.redteam_fallen_abgelehnt} of ${st.redteam_fallen} traps planted for the red team were caught.</li>
      <li>The selftest runs ${Object.entries(sc).map(([k, v]) => `${v} known cases in the ${esc(k)} domain`).join(" and ")} before every run; a single failure stops the lab.</li></ul>
      ${src(st.source, "python -m benchmarks.blind_claims")}`;
  }

  // ---------- classification ----------
  const kl = X.classification;
  if (kl) {
    const viol = new Set(kl.verletzungen || []); const cells = [];
    for (let i = 0; i < kl.bewiesen; i++) cells.push(`<span class="proved" title="proved"></span>`);
    (kl.verletzungen || []).forEach((v) => cells.push(`<span class="violated" title="${esc(v)}: certified counterexample"></span>`));
    for (let i = 0; i < kl.offen; i++) cells.push(`<span title="open"></span>`);
    $("#c-body").innerHTML = `<p class="measure serif">Of the ${kl.topologien} proofreading topologies with at most two bound states, ${kl.bewiesen} provably obey $\\eta \\ge e^{-2\\Delta}$, ${kl.verletzt} violate it with an exact rational counterexample, and ${kl.offen} remain open. The smallest certified error is $\\eta = ${Number(kl.eta_min).toExponential(3).replace(/e([+-])(\d+)/, (m, sg, d) => ` \\times 10^{${sg === "-" ? "-" : ""}${d}}`)}$.</p>
      <div class="cells" role="img" aria-label="${kl.bewiesen} proved, ${kl.verletzt} violated, ${kl.offen} open">${cells.join("")}</div>
      <div class="legend"><span><i class="proved"></i>proved (${kl.bewiesen})</span><span><i class="violated"></i>counterexample (${kl.verletzt})</span><span><i></i>open (${kl.offen})</span></div>
      ${src(kl.source, "python -m asd.klassifikation --projekt " + kl.projekt)}`;
    P.math($("#c-body"));
  }

  // ---------- metrics ----------
  const m = X.metrics;
  if (m && m.latenz_median_s != null) {
    const rows = [["Run", esc(m.lauf)], ["Median verifier latency", `${m.latenz_median_s} s (n = ${m.latenz_n}, ${m.latenz_min_s} to ${m.latenz_max_s} s)`],
      ["Median time from question to certificate", `${m.frage_zu_zertifikat_median_s} s (n = ${m.frage_zu_zertifikat_n})`], ["Certified claims", `${m.zertifizierte_claims} (${m.zertifiziert_pro_h} per hour)`],
      ["Rejected submissions", m.abgelehnte_behauptungen], ["Run time", `${m.laufzeit_min} min, of which waiting for a human ${m.mensch_warten_min} min`],
      ["Speedup against a human with a stopwatch", m.speedup_manuell && m.speedup_manuell.status ? "pending: needs at least 3 stopwatch measurements in baselines/manual.jsonl" : esc(JSON.stringify(m.speedup_manuell))]];
    $("#m-body").innerHTML = `<div class="tablewrap"><table><tbody>${rows.map(([k, v]) => `<tr><th scope="row">${k}</th><td>${v}</td></tr>`).join("")}</tbody></table></div>${src(m.source, "python -m asd.metrics proofreading")}`;
  }
  document.querySelectorAll("[data-copy]").forEach((b) => b.addEventListener("click", () => P.copy(b.dataset.copy)));
})();
