// Motion layer: scroll reveal, word reveal, count-up. Everything degrades to the final state under prefers-reduced-motion.
"use strict";
const Motion = (() => {
  const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let io = null;
  function observer() {
    if (io || !("IntersectionObserver" in window)) return io;
    io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in"); io.unobserve(e.target);
      e.target.dispatchEvent(new CustomEvent("reveal"));
    }), { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    return io;
  }
  // elements with [data-reveal] fade and rise in when they enter the viewport; children with [data-stagger] get --i
  function reveal(root = document) {
    root.querySelectorAll("[data-stagger]").forEach((p) => [...p.children].forEach((c, i) => c.style.setProperty("--i", i)));
    root.querySelectorAll("[data-reveal]:not(.in)").forEach((el) => {
      if (reduced() || !observer()) { el.classList.add("in"); el.dispatchEvent(new CustomEvent("reveal")); }
      else io.observe(el);
    });
  }
  function onReveal(el, fn) {
    if (el.classList.contains("in")) fn(); else el.addEventListener("reveal", fn, { once: true });
  }
  function words(el) {
    const txt = el.textContent; el.setAttribute("aria-label", txt);
    el.innerHTML = txt.split(/(\s+)/).map((w, i) => /^\s+$/.test(w) ? w : `<span class="w" aria-hidden="true" style="--i:${i / 2}"><span>${w}</span></span>`).join("");
    el.classList.add("split");
  }
  // wraps every number in `el` and counts it up from 0 once revealed (keeps decimals and the text around it)
  function countUp(el, ms = 1100) {
    el.innerHTML = el.innerHTML.replace(/(?<![\w.#\/-])(\d+(?:\.\d+)?)(?![\w\/-])/g, (m) => `<span class="cnt" data-to="${m}">${m}</span>`);
    const run = () => el.querySelectorAll(".cnt").forEach((s) => {
      const to = parseFloat(s.dataset.to), dec = (s.dataset.to.split(".")[1] || "").length;
      if (reduced()) return;
      const t0 = performance.now();
      const step = (t) => {
        const k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3);
        s.textContent = (to * e).toFixed(dec); if (k < 1) requestAnimationFrame(step); else s.textContent = s.dataset.to;
      };
      s.textContent = (0).toFixed(dec); requestAnimationFrame(step);
    });
    onReveal(el.closest("[data-reveal]") || el, run);
  }
  return { reveal, onReveal, words, countUp, reduced };
})();
