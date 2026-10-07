/* turtleweb.js: draws what a Python turtle program sends (docs/contrato.md). No framework, no CDN.
 *
 *   const tw = TurtleWeb.mount(document.getElementById("area"), {base: "/turtleweb"});
 *   tw.attach(sid);            // follow a run; call again for a new run (the page is cleared)
 */
(function (global) {
  "use strict";

  const STATES = {
    starting: "conectando…", running: "rodando", waiting: "esperando você fechar a janela",
    ended: "terminou", error: "terminou com erro", stopped: "parado",
  };
  const TERMINAL = {ended: 1, error: 1, stopped: 1};

  const CSS = `
.tw{font-family:system-ui,sans-serif;max-width:100%}
.tw-bar{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:0 0 .5rem}
.tw-state{font-weight:600;min-width:12rem}
.tw button{font:inherit;padding:.4rem .8rem;border:1px solid #888;border-radius:.4rem;background:#f4f4f4;cursor:pointer}
.tw button:disabled{opacity:.5;cursor:default}
.tw-stage{display:inline-block;max-width:100%;border:1px solid #888;background:#fff;line-height:0}
.tw-stage canvas{max-width:100%;height:auto;touch-action:none;outline:none}
.tw-ask{margin:.5rem 0;padding:.6rem;border:1px solid #4a7;border-radius:.4rem;background:#f2fbf5}
.tw-ask input{font:inherit;padding:.3rem;min-width:12rem}
.tw-ask .tw-err{color:#b00;margin:.3rem 0 0}
.tw [hidden]{display:none!important}
@media (prefers-color-scheme:dark){.tw button{background:#333;color:#eee;border-color:#777}.tw-ask{background:#1c2b22}}
`;

  function el(tag, attrs, children) {
    const e = document.createElement(tag);
    Object.assign(e, attrs || {});
    (children || []).forEach(c => e.append(c));
    return e;
  }

  function TurtleWeb(root, opts) {
    this.base = ((opts && opts.base) || "").replace(/\/$/, "");
    this.opts = opts || {};
    this.sid = null;
    this.es = null;
    this.state = "starting";
    this.reset();
    this.build(root);
  }

  TurtleWeb.prototype.reset = function () {
    this.items = new Map();   // id -> {kind, coords, opts}
    this.order = [];          // z-order, bottom first
    this.bg = "#ffffff";
    this.w = 640; this.h = 600;
    this.dirty = true;
  };

  TurtleWeb.prototype.build = function (root) {
    if (!document.getElementById("tw-css")) {
      const st = el("style", {id: "tw-css", textContent: CSS});
      document.head.append(st);
    }
    this.canvas = el("canvas", {tabIndex: 0});
    this.ctx = this.canvas.getContext("2d");
    this.stateEl = el("span", {className: "tw-state"});
    this.closeBtn = el("button", {className: "tw-close", type: "button", textContent: "Fechar a janela", disabled: true});
    this.closeBtn.onclick = () => this.send({t: "close"});
    this.fastBtn = el("button", {className: "tw-fast", type: "button", textContent: "Mais rápido", title: "Acelera a animação sem mudar o desenho"});
    this.fastBtn.onclick = () => this.setFast(!this.fast);
    const bar = el("div", {className: "tw-bar"}, [this.stateEl, this.closeBtn, this.fastBtn]);
    this.askForm = el("form", {className: "tw-ask", hidden: true});
    this.stage = el("div", {className: "tw-stage"}, [this.canvas]);
    this.root = el("div", {className: "tw"}, [bar, this.askForm, this.stage]);
    root.append(this.root);
    this.fast = false;
    this.setState("starting");
    this.layout();
    const frame = () => { if (this.dirty) { this.dirty = false; this.draw(); } requestAnimationFrame(frame); };
    requestAnimationFrame(frame);
  };

  TurtleWeb.prototype.setFast = function (on) {
    this.fast = on;
    this.fastBtn.textContent = on ? "Velocidade normal" : "Mais rápido";
    this.send({t: "speed", v: on ? 8 : 1});
  };

  TurtleWeb.prototype.layout = function () {
    const dpr = global.devicePixelRatio || 1;
    this.canvas.width = Math.round(this.w * dpr);
    this.canvas.height = Math.round(this.h * dpr);
    this.canvas.style.width = this.w + "px";
    this.dpr = dpr;
    this.dirty = true;
  };

  TurtleWeb.prototype.setState = function (s, code) {
    this.state = s;
    let text = STATES[s] || s;
    if (s === "error" && code != null) text += " (código " + code + ")";
    this.stateEl.textContent = text;
    this.closeBtn.disabled = !(s === "running" || s === "waiting");
    this.root.dataset.state = s;
    if (this.opts.onstate) this.opts.onstate(s, code);
  };

  TurtleWeb.prototype.send = function (msg) {
    if (!this.sid) return Promise.resolve();
    return fetch(this.base + "/input/" + encodeURIComponent(this.sid), {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(msg),
    }).catch(() => {});
  };

  TurtleWeb.prototype.attach = function (sid) {
    this.detach();
    this.sid = sid;
    this.reset();
    this.layout();
    this.askForm.hidden = true;
    this.setState("starting");
    this.es = new EventSource(this.base + "/events/" + encodeURIComponent(sid));
    this.es.onmessage = ev => this.onMessage(JSON.parse(ev.data));
  };

  TurtleWeb.prototype.detach = function () {
    if (this.es) { this.es.close(); this.es = null; }
  };

  TurtleWeb.prototype.onMessage = function (m) {
    switch (m.t) {
      case "ops": for (const op of m.ops) this.apply(op); this.dirty = true; break;
      case "state":
        this.setState(m.s, m.code);
        if (TERMINAL[m.s]) { this.askForm.hidden = true; this.detach(); }
        break;
      case "ask": this.showAsk(m); break;
      case "out": if (this.opts.onoutput) this.opts.onoutput(m.s, m.text); break;
    }
  };

  TurtleWeb.prototype.apply = function (op) {
    const [name, a, b, c, d] = op;
    switch (name) {
      case "create": this.items.set(a, {kind: b, coords: c, opts: d}); this.order.push(a); break;
      case "coords": { const it = this.items.get(a); if (it) it.coords = b; break; }
      case "config": { const it = this.items.get(a); if (it) Object.assign(it.opts, b); break; }
      case "raise": this.order = this.order.filter(x => x !== a); this.order.push(a); break;
      case "lower": this.order = this.order.filter(x => x !== a); this.order.unshift(a); break;
      case "delete":
        if (a === "all") { this.items.clear(); this.order = []; }
        else { this.items.delete(a); this.order = this.order.filter(x => x !== a); }
        break;
      case "bg": this.bg = a; break;
      case "geometry": this.w = a; this.h = b; this.layout(); break;
      case "title": if (this.opts.title !== false && a) document.title = a; break;
    }
  };

  function fontCss(f) {
    if (!f) return "10.7px Arial, Helvetica, sans-serif";
    const family = f[0] || "Arial", size = Number(f[1]) || 8, style = String(f[2] || "");
    const px = size < 0 ? -size : size * 4 / 3;   // Tk: points, or pixels when negative
    return (/italic/.test(style) ? "italic " : "") + (/bold/.test(style) ? "bold " : "") +
      px + 'px "' + family + '", Arial, Helvetica, sans-serif';
  }

  TurtleWeb.prototype.draw = function () {
    const ctx = this.ctx, dpr = this.dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, this.w, this.h);
    ctx.translate(this.w / 2, this.h / 2);
    for (const id of this.order) {
      const it = this.items.get(id), p = it.coords, o = it.opts;
      if (it.kind === "line" && o.fill && p.length >= 4) {
        ctx.beginPath(); ctx.moveTo(p[0], p[1]);
        for (let i = 2; i < p.length; i += 2) ctx.lineTo(p[i], p[i + 1]);
        ctx.strokeStyle = o.fill; ctx.lineWidth = o.width || 1;
        ctx.lineCap = o.capstyle === "round" ? "round" : o.capstyle === "projecting" ? "square" : "butt";
        ctx.lineJoin = o.joinstyle || "round";
        ctx.stroke();
      } else if (it.kind === "polygon" && p.length >= 6 && (o.fill || o.outline)) {
        ctx.beginPath(); ctx.moveTo(p[0], p[1]);
        for (let i = 2; i < p.length; i += 2) ctx.lineTo(p[i], p[i + 1]);
        ctx.closePath();
        if (o.fill) { ctx.fillStyle = o.fill; ctx.fill(); }
        if (o.outline) { ctx.strokeStyle = o.outline; ctx.lineWidth = o.width || 1; ctx.lineJoin = "round"; ctx.stroke(); }
      } else if (it.kind === "text") {
        ctx.font = fontCss(o.font); ctx.fillStyle = o.fill || "#000";
        ctx.textAlign = {sw: "left", s: "center", se: "right"}[o.anchor] || "left";
        ctx.textBaseline = "bottom";
        ctx.fillText(o.text || "", p[0], p[1]);
      }
    }
  };

  TurtleWeb.prototype.showAsk = function (m) {
    const f = this.askForm;
    f.textContent = "";
    const input = el("input", {type: "text", value: m.initial == null ? "" : String(m.initial), autocomplete: "off"});
    if (m.kind === "float") input.inputMode = "decimal";
    const label = el("label", {}, [el("strong", {textContent: m.title || ""}), el("br"), (m.prompt || "") + " ", input]);
    const ok = el("button", {type: "submit", textContent: "OK"});
    const cancel = el("button", {type: "button", textContent: "Cancelar"});
    f.append(label, " ", ok, " ", cancel);
    if (m.error) f.append(el("p", {className: "tw-err", textContent: m.error}));
    f.hidden = false;
    const done = v => { f.hidden = true; this.send({t: "answer", id: m.id, v: v}); this.canvas.focus(); };
    f.onsubmit = ev => { ev.preventDefault(); done(input.value); };
    cancel.onclick = () => done(null);
    input.focus();
  };

  global.TurtleWeb = {
    mount: (root, opts) => new TurtleWeb(root, opts),
  };
})(window);
