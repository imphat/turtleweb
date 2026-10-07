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
.tw-keyfield{position:fixed;left:0;bottom:0;width:1px;height:1px;opacity:0;border:0;padding:0;font-size:16px}
.tw-pad{display:grid;grid-template-columns:repeat(3,3.6rem);grid-template-rows:repeat(2,3.2rem) 2.6rem;gap:.4rem;margin:.6rem 0;user-select:none;-webkit-user-select:none;touch-action:none}
.tw-pad button{padding:0;font-size:1.4rem;touch-action:none}
.tw-pad .tw-space{font-size:1rem}
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
    this.listening = false;
    if (this.pad) this.updatePad();
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
    this.kbdBtn = el("button", {className: "tw-kbd", type: "button", textContent: "⌨️ Teclado", hidden: true,
      title: "Abre o teclado do aparelho"});
    // The on-screen keyboard only opens for something that has focus: a tiny invisible text field.
    this.keyField = el("input", {className: "tw-keyfield", type: "text", autocomplete: "off", spellcheck: false,
      autocapitalize: "off", autocorrect: "off"});
    this.keyField.setAttribute("aria-label", "teclado do programa");
    let wasOpen = false;   // tapping the button may take the focus away before "click": remember how it was
    this.kbdBtn.addEventListener("pointerdown", () => { wasOpen = document.activeElement === this.keyField; });
    this.kbdBtn.onclick = () => { if (wasOpen) this.keyField.blur(); else this.keyField.focus(); wasOpen = false; };
    const bar = el("div", {className: "tw-bar"}, [this.stateEl, this.closeBtn, this.fastBtn, this.kbdBtn]);
    this.askForm = el("form", {className: "tw-ask", hidden: true});
    this.stage = el("div", {className: "tw-stage"}, [this.canvas]);
    this.pad = this.buildPad();
    this.root = el("div", {className: "tw"}, [bar, this.askForm, this.stage, this.pad, this.keyField]);
    root.append(this.root);
    this.fast = false;
    this.speedFactor = 1;
    // prefers-reduced-motion: no walking animation; the drawing itself is unchanged
    this.reduceMotion = this.opts.reduceMotion !== undefined ? !!this.opts.reduceMotion
      : !!(global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches);
    if (this.reduceMotion) { this.fast = true; this.speedFactor = INSTANT; this.fastBtn.textContent = "Velocidade normal"; }
    this.listening = false;
    this.outbox = [];
    this.sending = false;
    this.pressed = new Set();
    this.bindInput();
    this.setState("starting");
    this.layout();
    const frame = () => { if (this.dirty) { this.dirty = false; this.draw(); } requestAnimationFrame(frame); };
    requestAnimationFrame(frame);
  };

  const FAST = 8, INSTANT = 1000;

  TurtleWeb.prototype.setFast = function (on, factor) {
    this.fast = on;
    this.speedFactor = on ? (factor || FAST) : 1;
    this.fastBtn.textContent = on ? "Velocidade normal" : "Mais rápido";
    this.send({t: "speed", v: this.speedFactor});
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
    this.code = code;
    let text = STATES[s] || s;
    if (s === "error" && code != null) text += " (código " + code + ")";
    this.stateEl.textContent = text;
    this.closeBtn.disabled = !(s === "running" || s === "waiting");
    this.root.dataset.state = s;
    if (this.pad) this.updatePad();
    if (this.opts.onstate) this.opts.onstate(s, code);
  };

  // Messages go out one request at a time and in a batch, so their order is kept.
  TurtleWeb.prototype.send = function (msg) {
    if (!this.sid) return;
    const last = this.outbox[this.outbox.length - 1];
    if (msg.t === "mousemove" && last && last.t === "mousemove" && last.b === msg.b) this.outbox[this.outbox.length - 1] = msg;
    else this.outbox.push(msg);
    this.flushOut();
  };

  TurtleWeb.prototype.flushOut = function () {
    if (this.sending || !this.outbox.length) return;
    this.sending = true;
    const batch = this.outbox.splice(0);
    fetch(this.base + "/input/" + encodeURIComponent(this.sid), {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(batch),
    }).catch(() => {}).finally(() => { this.sending = false; this.flushOut(); });
  };

  TurtleWeb.prototype.attach = function (sid) {
    this.detach();
    this.sid = sid;
    this.lastId = null;
    this.outbox = [];
    this.pressed.clear();
    this.reset();
    this.layout();
    this.askForm.hidden = true;
    this.setState("starting");
    if (this.fast) this.send({t: "speed", v: this.speedFactor});
    this.open();
  };

  // (Re)open the event stream. `last` lets a new stream continue where the old one stopped.
  TurtleWeb.prototype.open = function () {
    if (this.es) { this.es.close(); this.es = null; }
    const url = this.base + "/events/" + encodeURIComponent(this.sid) + (this.lastId != null ? "?last=" + this.lastId : "");
    const es = this.es = new EventSource(url);
    es.onmessage = ev => { if (ev.lastEventId) this.lastId = ev.lastEventId; this.onMessage(JSON.parse(ev.data)); };
    es.onopen = () => this.setState(this.state, this.code);
    es.onerror = () => {            // the browser retries by itself and resumes from Last-Event-ID
      if (TERMINAL[this.state]) return;
      this.stateEl.textContent = es.readyState === 2 ? "sem conexão com o servidor" : "reconectando…";
      if (this.opts.onstate) this.opts.onstate("offline");
    };
  };

  // iOS may close or silently kill the stream while the screen is locked: reopen it, resuming after the last event.
  TurtleWeb.prototype.resume = function () {
    if (this.sid && this.es && !TERMINAL[this.state]) this.open();
  };

  TurtleWeb.prototype.detach = function () {
    if (this.es) { this.es.close(); this.es = null; }
  };

  TurtleWeb.prototype.onMessage = function (m) {
    switch (m.t) {
      case "ops":
        if (m.reset) { this.items.clear(); this.order = []; }   // a snapshot replaces what was drawn so far
        for (const op of m.ops) this.apply(op);
        this.dirty = true;
        break;
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
      case "listen": this.listening = true; this.updatePad(); this.canvas.focus({preventScroll: true}); break;
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

  function isPoint(p) {
    for (let i = 2; i < p.length; i += 2) if (p[i] !== p[0] || p[i + 1] !== p[1]) return false;
    return true;
  }

  TurtleWeb.prototype.draw = function () {
    const ctx = this.ctx, dpr = this.dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, this.w, this.h);
    ctx.translate(this.w / 2, this.h / 2);
    for (const id of this.order) {
      const it = this.items.get(id), p = it.coords, o = it.opts;
      if (it.kind === "line" && o.fill && p.length >= 4 && isPoint(p)) {
        // Zero-length line = Tk's round/square dot (turtle's dot() is forward(0)); Safari draws nothing for it.
        const r = (o.width || 1) / 2;
        ctx.fillStyle = o.fill;
        if (o.capstyle === "round") { ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, 2 * Math.PI); ctx.fill(); }
        else if (o.capstyle === "projecting") ctx.fillRect(p[0] - r, p[1] - r, 2 * r, 2 * r);
      } else if (it.kind === "line" && o.fill && p.length >= 4) {
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

  // ---- input: mouse, touch, keyboard, arrow buttons ----

  const KEYSYMS = {
    ArrowUp: "Up", ArrowDown: "Down", ArrowLeft: "Left", ArrowRight: "Right", " ": "space", Enter: "Return",
    Escape: "Escape", Backspace: "BackSpace", Tab: "Tab", Delete: "Delete", Home: "Home", End: "End",
    PageUp: "Prior", PageDown: "Next", Shift: "Shift_L", Control: "Control_L", Alt: "Alt_L",
    "+": "plus", "-": "minus", "*": "asterisk", "/": "slash", ".": "period", ",": "comma", ";": "semicolon",
    ":": "colon", "=": "equal", "!": "exclam", "?": "question", "(": "parenleft", ")": "parenright",
    "'": "apostrophe", '"': "quotedbl", "@": "at", "#": "numbersign", "$": "dollar", "%": "percent",
    "&": "ampersand", "_": "underscore", "<": "less", ">": "greater", "[": "bracketleft",
    "]": "bracketright", "\\": "backslash", "{": "braceleft", "}": "braceright", "|": "bar",
    "~": "asciitilde", "^": "asciicircum", "`": "grave",
  };
  const SCROLL_KEYS = {Up: 1, Down: 1, Left: 1, Right: 1, space: 1, Prior: 1, Next: 1, Home: 1, End: 1};

  function keysym(e) {
    if (KEYSYMS[e.key]) return KEYSYMS[e.key];
    if (/^F\d{1,2}$/.test(e.key)) return e.key;
    if (e.key.length === 1) return e.key;
    return null;
  }

  TurtleWeb.prototype.keyEvent = function (down, sym, ch) {
    if (down) this.pressed.add(sym); else this.pressed.delete(sym);
    this.send({t: down ? "keydown" : "keyup", k: sym, c: ch || ""});
  };

  TurtleWeb.prototype.point = function (ev) {
    const r = this.canvas.getBoundingClientRect();
    return {x: (ev.clientX - r.left) * this.w / r.width, y: (ev.clientY - r.top) * this.h / r.height};
  };

  TurtleWeb.prototype.bindInput = function () {
    const cv = this.canvas;
    let button = 0, moveEv = null, raf = 0;
    const tkButton = ev => ev.button === 0 ? 1 : ev.button === 1 ? 2 : 3;
    cv.addEventListener("contextmenu", ev => ev.preventDefault());
    cv.addEventListener("pointerdown", ev => {
      if (button) return;
      button = tkButton(ev);
      cv.focus({preventScroll: true});
      try { cv.setPointerCapture(ev.pointerId); } catch (e) { /* synthetic events */ }
      this.send(Object.assign({t: "mousedown", b: button}, this.point(ev)));
    });
    cv.addEventListener("pointermove", ev => {
      if (!button) return;
      moveEv = ev;
      if (!raf) raf = requestAnimationFrame(() => {
        raf = 0;
        if (moveEv) this.send(Object.assign({t: "mousemove", b: button}, this.point(moveEv)));
        moveEv = null;
      });
    });
    const up = ev => {
      if (!button) return;
      moveEv = null;
      this.send(Object.assign({t: "mouseup", b: button}, this.point(ev)));
      button = 0;
    };
    cv.addEventListener("pointerup", up);
    cv.addEventListener("pointercancel", up);

    const typing = ev => ev.target !== this.keyField && /^(INPUT|TEXTAREA|SELECT)$/.test((ev.target && ev.target.tagName) || "");
    // Soft keyboards sometimes send key "Unidentified" (composition): then the characters come in the input event.
    let composing = false;
    this.keyField.addEventListener("input", ev => {
      const text = this.keyField.value;
      this.keyField.value = "";
      if (!composing || !this.sid) return;
      composing = false;
      for (const c of text) { const sym = KEYSYMS[c] || c; this.keyEvent(true, sym, c); this.keyEvent(false, sym, c); }
    });
    document.addEventListener("keydown", ev => {
      if (typing(ev) || ev.ctrlKey || ev.metaKey || !this.sid) return;
      const sym = keysym(ev);
      if (!sym) { if (ev.target === this.keyField) composing = true; return; }
      if (this.listening && SCROLL_KEYS[sym]) ev.preventDefault();
      this.keyEvent(true, sym, ev.key.length === 1 ? ev.key : "");   // auto-repeat arrives as more presses, as in Tk
    });
    document.addEventListener("keyup", ev => {
      if (typing(ev) || !this.sid) return;
      const sym = keysym(ev);
      if (sym && this.pressed.has(sym)) this.keyEvent(false, sym, ev.key.length === 1 ? ev.key : "");
    });
    document.addEventListener("visibilitychange", () => { if (!document.hidden) this.resume(); });
    global.addEventListener("pageshow", ev => { if (ev.persisted) this.resume(); });
    global.addEventListener("online", () => this.resume());
    global.addEventListener("blur", () => { for (const k of Array.from(this.pressed)) this.keyEvent(false, k, ""); });
  };

  TurtleWeb.prototype.buildPad = function () {
    const pad = el("div", {className: "tw-pad", hidden: true});
    const mk = (label, sym, cls) => {
      const b = el("button", {type: "button", textContent: label, className: cls || "", title: sym});
      b.dataset.key = sym;
      let timer = 0;
      const ch = sym === "space" ? " " : "";
      const stop = () => { if (timer) { clearInterval(timer); timer = 0; this.keyEvent(false, sym, ch); } };
      b.addEventListener("pointerdown", ev => {
        ev.preventDefault();
        if (timer) return;
        this.keyEvent(true, sym, ch);
        // onkey() answers the key RELEASE, so a held button sends release+press per repeat (X11 autorepeat)
        timer = setInterval(() => { this.keyEvent(false, sym, ch); this.keyEvent(true, sym, ch); }, 120);
      });
      for (const n of ["pointerup", "pointercancel", "lostpointercapture"]) b.addEventListener(n, stop);
      b.addEventListener("contextmenu", ev => ev.preventDefault());
      return b;
    };
    const place = (btn, col, row) => { btn.style.gridColumn = col; btn.style.gridRow = row; pad.append(btn); };
    place(mk("▲", "Up"), 2, 1);
    place(mk("◀", "Left"), 1, 2);
    place(mk("▼", "Down"), 2, 2);
    place(mk("▶", "Right"), 3, 2);
    place(mk("espaço", "space", "tw-space"), "1 / span 3", 3);
    return pad;
  };

  TurtleWeb.prototype.updatePad = function () {
    const coarse = global.matchMedia && global.matchMedia("(pointer: coarse)").matches;
    const want = this.opts.pad === undefined ? coarse : !!this.opts.pad;
    const on = this.listening && want && !TERMINAL[this.state];
    this.pad.hidden = !on;
    this.kbdBtn.hidden = !(this.listening && (this.opts.keyboardButton === undefined ? coarse : !!this.opts.keyboardButton) &&
      !TERMINAL[this.state]);
    if (this.kbdBtn.hidden && document.activeElement === this.keyField) this.keyField.blur();
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
