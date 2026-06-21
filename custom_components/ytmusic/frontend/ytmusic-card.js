/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const R = globalThis, et = R.ShadowRoot && (R.ShadyCSS === void 0 || R.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, it = Symbol(), at = /* @__PURE__ */ new WeakMap();
let yt = class {
  constructor(t, e, i) {
    if (this._$cssResult$ = !0, i !== it) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = t, this.t = e;
  }
  get styleSheet() {
    let t = this.o;
    const e = this.t;
    if (et && t === void 0) {
      const i = e !== void 0 && e.length === 1;
      i && (t = at.get(e)), t === void 0 && ((this.o = t = new CSSStyleSheet()).replaceSync(this.cssText), i && at.set(e, t));
    }
    return t;
  }
  toString() {
    return this.cssText;
  }
};
const At = (r) => new yt(typeof r == "string" ? r : r + "", void 0, it), q = (r, ...t) => {
  const e = r.length === 1 ? r[0] : t.reduce((i, s, a) => i + ((n) => {
    if (n._$cssResult$ === !0) return n.cssText;
    if (typeof n == "number") return n;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + n + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(s) + r[a + 1], r[0]);
  return new yt(e, r, it);
}, St = (r, t) => {
  if (et) r.adoptedStyleSheets = t.map((e) => e instanceof CSSStyleSheet ? e : e.styleSheet);
  else for (const e of t) {
    const i = document.createElement("style"), s = R.litNonce;
    s !== void 0 && i.setAttribute("nonce", s), i.textContent = e.cssText, r.appendChild(i);
  }
}, nt = et ? (r) => r : (r) => r instanceof CSSStyleSheet ? ((t) => {
  let e = "";
  for (const i of t.cssRules) e += i.cssText;
  return At(e);
})(r) : r;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const { is: Et, defineProperty: Ct, getOwnPropertyDescriptor: zt, getOwnPropertyNames: Mt, getOwnPropertySymbols: Pt, getPrototypeOf: Tt } = Object, _ = globalThis, ot = _.trustedTypes, Nt = ot ? ot.emptyScript : "", V = _.reactiveElementPolyfillSupport, E = (r, t) => r, J = { toAttribute(r, t) {
  switch (t) {
    case Boolean:
      r = r ? Nt : null;
      break;
    case Object:
    case Array:
      r = r == null ? r : JSON.stringify(r);
  }
  return r;
}, fromAttribute(r, t) {
  let e = r;
  switch (t) {
    case Boolean:
      e = r !== null;
      break;
    case Number:
      e = r === null ? null : Number(r);
      break;
    case Object:
    case Array:
      try {
        e = JSON.parse(r);
      } catch {
        e = null;
      }
  }
  return e;
} }, vt = (r, t) => !Et(r, t), lt = { attribute: !0, type: String, converter: J, reflect: !1, useDefault: !1, hasChanged: vt };
Symbol.metadata ?? (Symbol.metadata = Symbol("metadata")), _.litPropertyMetadata ?? (_.litPropertyMetadata = /* @__PURE__ */ new WeakMap());
let w = class extends HTMLElement {
  static addInitializer(t) {
    this._$Ei(), (this.l ?? (this.l = [])).push(t);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(t, e = lt) {
    if (e.state && (e.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(t) && ((e = Object.create(e)).wrapped = !0), this.elementProperties.set(t, e), !e.noAccessor) {
      const i = Symbol(), s = this.getPropertyDescriptor(t, i, e);
      s !== void 0 && Ct(this.prototype, t, s);
    }
  }
  static getPropertyDescriptor(t, e, i) {
    const { get: s, set: a } = zt(this.prototype, t) ?? { get() {
      return this[e];
    }, set(n) {
      this[e] = n;
    } };
    return { get: s, set(n) {
      const c = s == null ? void 0 : s.call(this);
      a == null || a.call(this, n), this.requestUpdate(t, c, i);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(t) {
    return this.elementProperties.get(t) ?? lt;
  }
  static _$Ei() {
    if (this.hasOwnProperty(E("elementProperties"))) return;
    const t = Tt(this);
    t.finalize(), t.l !== void 0 && (this.l = [...t.l]), this.elementProperties = new Map(t.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(E("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(E("properties"))) {
      const e = this.properties, i = [...Mt(e), ...Pt(e)];
      for (const s of i) this.createProperty(s, e[s]);
    }
    const t = this[Symbol.metadata];
    if (t !== null) {
      const e = litPropertyMetadata.get(t);
      if (e !== void 0) for (const [i, s] of e) this.elementProperties.set(i, s);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [e, i] of this.elementProperties) {
      const s = this._$Eu(e, i);
      s !== void 0 && this._$Eh.set(s, e);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(t) {
    const e = [];
    if (Array.isArray(t)) {
      const i = new Set(t.flat(1 / 0).reverse());
      for (const s of i) e.unshift(nt(s));
    } else t !== void 0 && e.push(nt(t));
    return e;
  }
  static _$Eu(t, e) {
    const i = e.attribute;
    return i === !1 ? void 0 : typeof i == "string" ? i : typeof t == "string" ? t.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    var t;
    this._$ES = new Promise((e) => this.enableUpdating = e), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), (t = this.constructor.l) == null || t.forEach((e) => e(this));
  }
  addController(t) {
    var e;
    (this._$EO ?? (this._$EO = /* @__PURE__ */ new Set())).add(t), this.renderRoot !== void 0 && this.isConnected && ((e = t.hostConnected) == null || e.call(t));
  }
  removeController(t) {
    var e;
    (e = this._$EO) == null || e.delete(t);
  }
  _$E_() {
    const t = /* @__PURE__ */ new Map(), e = this.constructor.elementProperties;
    for (const i of e.keys()) this.hasOwnProperty(i) && (t.set(i, this[i]), delete this[i]);
    t.size > 0 && (this._$Ep = t);
  }
  createRenderRoot() {
    const t = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return St(t, this.constructor.elementStyles), t;
  }
  connectedCallback() {
    var t;
    this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (t = this._$EO) == null || t.forEach((e) => {
      var i;
      return (i = e.hostConnected) == null ? void 0 : i.call(e);
    });
  }
  enableUpdating(t) {
  }
  disconnectedCallback() {
    var t;
    (t = this._$EO) == null || t.forEach((e) => {
      var i;
      return (i = e.hostDisconnected) == null ? void 0 : i.call(e);
    });
  }
  attributeChangedCallback(t, e, i) {
    this._$AK(t, i);
  }
  _$ET(t, e) {
    var a;
    const i = this.constructor.elementProperties.get(t), s = this.constructor._$Eu(t, i);
    if (s !== void 0 && i.reflect === !0) {
      const n = (((a = i.converter) == null ? void 0 : a.toAttribute) !== void 0 ? i.converter : J).toAttribute(e, i.type);
      this._$Em = t, n == null ? this.removeAttribute(s) : this.setAttribute(s, n), this._$Em = null;
    }
  }
  _$AK(t, e) {
    var a, n;
    const i = this.constructor, s = i._$Eh.get(t);
    if (s !== void 0 && this._$Em !== s) {
      const c = i.getPropertyOptions(s), o = typeof c.converter == "function" ? { fromAttribute: c.converter } : ((a = c.converter) == null ? void 0 : a.fromAttribute) !== void 0 ? c.converter : J;
      this._$Em = s;
      const h = o.fromAttribute(e, c.type);
      this[s] = h ?? ((n = this._$Ej) == null ? void 0 : n.get(s)) ?? h, this._$Em = null;
    }
  }
  requestUpdate(t, e, i, s = !1, a) {
    var n;
    if (t !== void 0) {
      const c = this.constructor;
      if (s === !1 && (a = this[t]), i ?? (i = c.getPropertyOptions(t)), !((i.hasChanged ?? vt)(a, e) || i.useDefault && i.reflect && a === ((n = this._$Ej) == null ? void 0 : n.get(t)) && !this.hasAttribute(c._$Eu(t, i)))) return;
      this.C(t, e, i);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(t, e, { useDefault: i, reflect: s, wrapped: a }, n) {
    i && !(this._$Ej ?? (this._$Ej = /* @__PURE__ */ new Map())).has(t) && (this._$Ej.set(t, n ?? e ?? this[t]), a !== !0 || n !== void 0) || (this._$AL.has(t) || (this.hasUpdated || i || (e = void 0), this._$AL.set(t, e)), s === !0 && this._$Em !== t && (this._$Eq ?? (this._$Eq = /* @__PURE__ */ new Set())).add(t));
  }
  async _$EP() {
    this.isUpdatePending = !0;
    try {
      await this._$ES;
    } catch (e) {
      Promise.reject(e);
    }
    const t = this.scheduleUpdate();
    return t != null && await t, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    var i;
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this._$Ep) {
        for (const [a, n] of this._$Ep) this[a] = n;
        this._$Ep = void 0;
      }
      const s = this.constructor.elementProperties;
      if (s.size > 0) for (const [a, n] of s) {
        const { wrapped: c } = n, o = this[a];
        c !== !0 || this._$AL.has(a) || o === void 0 || this.C(a, void 0, n, o);
      }
    }
    let t = !1;
    const e = this._$AL;
    try {
      t = this.shouldUpdate(e), t ? (this.willUpdate(e), (i = this._$EO) == null || i.forEach((s) => {
        var a;
        return (a = s.hostUpdate) == null ? void 0 : a.call(s);
      }), this.update(e)) : this._$EM();
    } catch (s) {
      throw t = !1, this._$EM(), s;
    }
    t && this._$AE(e);
  }
  willUpdate(t) {
  }
  _$AE(t) {
    var e;
    (e = this._$EO) == null || e.forEach((i) => {
      var s;
      return (s = i.hostUpdated) == null ? void 0 : s.call(i);
    }), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(t)), this.updated(t);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(t) {
    return !0;
  }
  update(t) {
    this._$Eq && (this._$Eq = this._$Eq.forEach((e) => this._$ET(e, this[e]))), this._$EM();
  }
  updated(t) {
  }
  firstUpdated(t) {
  }
};
w.elementStyles = [], w.shadowRootOptions = { mode: "open" }, w[E("elementProperties")] = /* @__PURE__ */ new Map(), w[E("finalized")] = /* @__PURE__ */ new Map(), V == null || V({ ReactiveElement: w }), (_.reactiveElementVersions ?? (_.reactiveElementVersions = [])).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const C = globalThis, ct = (r) => r, L = C.trustedTypes, dt = L ? L.createPolicy("lit-html", { createHTML: (r) => r }) : void 0, xt = "$lit$", b = `lit$${Math.random().toFixed(9).slice(2)}$`, $t = "?" + b, qt = `<${$t}>`, $ = document, P = () => $.createComment(""), T = (r) => r === null || typeof r != "object" && typeof r != "function", st = Array.isArray, Ut = (r) => st(r) || typeof (r == null ? void 0 : r[Symbol.iterator]) == "function", Y = `[ 	
\f\r]`, S = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, pt = /-->/g, ht = />/g, y = RegExp(`>|${Y}(?:([^\\s"'>=/]+)(${Y}*=${Y}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), ut = /'/g, mt = /"/g, wt = /^(?:script|style|textarea|title)$/i, Ot = (r) => (t, ...e) => ({ _$litType$: r, strings: t, values: e }), l = Ot(1), k = Symbol.for("lit-noChange"), d = Symbol.for("lit-nothing"), ft = /* @__PURE__ */ new WeakMap(), v = $.createTreeWalker($, 129);
function kt(r, t) {
  if (!st(r) || !r.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return dt !== void 0 ? dt.createHTML(t) : t;
}
const Rt = (r, t) => {
  const e = r.length - 1, i = [];
  let s, a = t === 2 ? "<svg>" : t === 3 ? "<math>" : "", n = S;
  for (let c = 0; c < e; c++) {
    const o = r[c];
    let h, u, p = -1, f = 0;
    for (; f < o.length && (n.lastIndex = f, u = n.exec(o), u !== null); ) f = n.lastIndex, n === S ? u[1] === "!--" ? n = pt : u[1] !== void 0 ? n = ht : u[2] !== void 0 ? (wt.test(u[2]) && (s = RegExp("</" + u[2], "g")), n = y) : u[3] !== void 0 && (n = y) : n === y ? u[0] === ">" ? (n = s ?? S, p = -1) : u[1] === void 0 ? p = -2 : (p = n.lastIndex - u[2].length, h = u[1], n = u[3] === void 0 ? y : u[3] === '"' ? mt : ut) : n === mt || n === ut ? n = y : n === pt || n === ht ? n = S : (n = y, s = void 0);
    const g = n === y && r[c + 1].startsWith("/>") ? " " : "";
    a += n === S ? o + qt : p >= 0 ? (i.push(h), o.slice(0, p) + xt + o.slice(p) + b + g) : o + b + (p === -2 ? c : g);
  }
  return [kt(r, a + (r[e] || "<?>") + (t === 2 ? "</svg>" : t === 3 ? "</math>" : "")), i];
};
class N {
  constructor({ strings: t, _$litType$: e }, i) {
    let s;
    this.parts = [];
    let a = 0, n = 0;
    const c = t.length - 1, o = this.parts, [h, u] = Rt(t, e);
    if (this.el = N.createElement(h, i), v.currentNode = this.el.content, e === 2 || e === 3) {
      const p = this.el.content.firstChild;
      p.replaceWith(...p.childNodes);
    }
    for (; (s = v.nextNode()) !== null && o.length < c; ) {
      if (s.nodeType === 1) {
        if (s.hasAttributes()) for (const p of s.getAttributeNames()) if (p.endsWith(xt)) {
          const f = u[n++], g = s.getAttribute(p).split(b), O = /([.?@])?(.*)/.exec(f);
          o.push({ type: 1, index: a, name: O[2], strings: g, ctor: O[1] === "." ? Ht : O[1] === "?" ? It : O[1] === "@" ? Dt : B }), s.removeAttribute(p);
        } else p.startsWith(b) && (o.push({ type: 6, index: a }), s.removeAttribute(p));
        if (wt.test(s.tagName)) {
          const p = s.textContent.split(b), f = p.length - 1;
          if (f > 0) {
            s.textContent = L ? L.emptyScript : "";
            for (let g = 0; g < f; g++) s.append(p[g], P()), v.nextNode(), o.push({ type: 2, index: ++a });
            s.append(p[f], P());
          }
        }
      } else if (s.nodeType === 8) if (s.data === $t) o.push({ type: 2, index: a });
      else {
        let p = -1;
        for (; (p = s.data.indexOf(b, p + 1)) !== -1; ) o.push({ type: 7, index: a }), p += b.length - 1;
      }
      a++;
    }
  }
  static createElement(t, e) {
    const i = $.createElement("template");
    return i.innerHTML = t, i;
  }
}
function A(r, t, e = r, i) {
  var n, c;
  if (t === k) return t;
  let s = i !== void 0 ? (n = e._$Co) == null ? void 0 : n[i] : e._$Cl;
  const a = T(t) ? void 0 : t._$litDirective$;
  return (s == null ? void 0 : s.constructor) !== a && ((c = s == null ? void 0 : s._$AO) == null || c.call(s, !1), a === void 0 ? s = void 0 : (s = new a(r), s._$AT(r, e, i)), i !== void 0 ? (e._$Co ?? (e._$Co = []))[i] = s : e._$Cl = s), s !== void 0 && (t = A(r, s._$AS(r, t.values), s, i)), t;
}
class Lt {
  constructor(t, e) {
    this._$AV = [], this._$AN = void 0, this._$AD = t, this._$AM = e;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(t) {
    const { el: { content: e }, parts: i } = this._$AD, s = ((t == null ? void 0 : t.creationScope) ?? $).importNode(e, !0);
    v.currentNode = s;
    let a = v.nextNode(), n = 0, c = 0, o = i[0];
    for (; o !== void 0; ) {
      if (n === o.index) {
        let h;
        o.type === 2 ? h = new U(a, a.nextSibling, this, t) : o.type === 1 ? h = new o.ctor(a, o.name, o.strings, this, t) : o.type === 6 && (h = new jt(a, this, t)), this._$AV.push(h), o = i[++c];
      }
      n !== (o == null ? void 0 : o.index) && (a = v.nextNode(), n++);
    }
    return v.currentNode = $, s;
  }
  p(t) {
    let e = 0;
    for (const i of this._$AV) i !== void 0 && (i.strings !== void 0 ? (i._$AI(t, i, e), e += i.strings.length - 2) : i._$AI(t[e])), e++;
  }
}
class U {
  get _$AU() {
    var t;
    return ((t = this._$AM) == null ? void 0 : t._$AU) ?? this._$Cv;
  }
  constructor(t, e, i, s) {
    this.type = 2, this._$AH = d, this._$AN = void 0, this._$AA = t, this._$AB = e, this._$AM = i, this.options = s, this._$Cv = (s == null ? void 0 : s.isConnected) ?? !0;
  }
  get parentNode() {
    let t = this._$AA.parentNode;
    const e = this._$AM;
    return e !== void 0 && (t == null ? void 0 : t.nodeType) === 11 && (t = e.parentNode), t;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(t, e = this) {
    t = A(this, t, e), T(t) ? t === d || t == null || t === "" ? (this._$AH !== d && this._$AR(), this._$AH = d) : t !== this._$AH && t !== k && this._(t) : t._$litType$ !== void 0 ? this.$(t) : t.nodeType !== void 0 ? this.T(t) : Ut(t) ? this.k(t) : this._(t);
  }
  O(t) {
    return this._$AA.parentNode.insertBefore(t, this._$AB);
  }
  T(t) {
    this._$AH !== t && (this._$AR(), this._$AH = this.O(t));
  }
  _(t) {
    this._$AH !== d && T(this._$AH) ? this._$AA.nextSibling.data = t : this.T($.createTextNode(t)), this._$AH = t;
  }
  $(t) {
    var a;
    const { values: e, _$litType$: i } = t, s = typeof i == "number" ? this._$AC(t) : (i.el === void 0 && (i.el = N.createElement(kt(i.h, i.h[0]), this.options)), i);
    if (((a = this._$AH) == null ? void 0 : a._$AD) === s) this._$AH.p(e);
    else {
      const n = new Lt(s, this), c = n.u(this.options);
      n.p(e), this.T(c), this._$AH = n;
    }
  }
  _$AC(t) {
    let e = ft.get(t.strings);
    return e === void 0 && ft.set(t.strings, e = new N(t)), e;
  }
  k(t) {
    st(this._$AH) || (this._$AH = [], this._$AR());
    const e = this._$AH;
    let i, s = 0;
    for (const a of t) s === e.length ? e.push(i = new U(this.O(P()), this.O(P()), this, this.options)) : i = e[s], i._$AI(a), s++;
    s < e.length && (this._$AR(i && i._$AB.nextSibling, s), e.length = s);
  }
  _$AR(t = this._$AA.nextSibling, e) {
    var i;
    for ((i = this._$AP) == null ? void 0 : i.call(this, !1, !0, e); t !== this._$AB; ) {
      const s = ct(t).nextSibling;
      ct(t).remove(), t = s;
    }
  }
  setConnected(t) {
    var e;
    this._$AM === void 0 && (this._$Cv = t, (e = this._$AP) == null || e.call(this, t));
  }
}
class B {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(t, e, i, s, a) {
    this.type = 1, this._$AH = d, this._$AN = void 0, this.element = t, this.name = e, this._$AM = s, this.options = a, i.length > 2 || i[0] !== "" || i[1] !== "" ? (this._$AH = Array(i.length - 1).fill(new String()), this.strings = i) : this._$AH = d;
  }
  _$AI(t, e = this, i, s) {
    const a = this.strings;
    let n = !1;
    if (a === void 0) t = A(this, t, e, 0), n = !T(t) || t !== this._$AH && t !== k, n && (this._$AH = t);
    else {
      const c = t;
      let o, h;
      for (t = a[0], o = 0; o < a.length - 1; o++) h = A(this, c[i + o], e, o), h === k && (h = this._$AH[o]), n || (n = !T(h) || h !== this._$AH[o]), h === d ? t = d : t !== d && (t += (h ?? "") + a[o + 1]), this._$AH[o] = h;
    }
    n && !s && this.j(t);
  }
  j(t) {
    t === d ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, t ?? "");
  }
}
class Ht extends B {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(t) {
    this.element[this.name] = t === d ? void 0 : t;
  }
}
class It extends B {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(t) {
    this.element.toggleAttribute(this.name, !!t && t !== d);
  }
}
class Dt extends B {
  constructor(t, e, i, s, a) {
    super(t, e, i, s, a), this.type = 5;
  }
  _$AI(t, e = this) {
    if ((t = A(this, t, e, 0) ?? d) === k) return;
    const i = this._$AH, s = t === d && i !== d || t.capture !== i.capture || t.once !== i.once || t.passive !== i.passive, a = t !== d && (i === d || s);
    s && this.element.removeEventListener(this.name, this, i), a && this.element.addEventListener(this.name, this, t), this._$AH = t;
  }
  handleEvent(t) {
    var e;
    typeof this._$AH == "function" ? this._$AH.call(((e = this.options) == null ? void 0 : e.host) ?? this.element, t) : this._$AH.handleEvent(t);
  }
}
class jt {
  constructor(t, e, i) {
    this.element = t, this.type = 6, this._$AN = void 0, this._$AM = e, this.options = i;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(t) {
    A(this, t);
  }
}
const F = C.litHtmlPolyfillSupport;
F == null || F(N, U), (C.litHtmlVersions ?? (C.litHtmlVersions = [])).push("3.3.3");
const Bt = (r, t, e) => {
  const i = (e == null ? void 0 : e.renderBefore) ?? t;
  let s = i._$litPart$;
  if (s === void 0) {
    const a = (e == null ? void 0 : e.renderBefore) ?? null;
    i._$litPart$ = s = new U(t.insertBefore(P(), a), a, void 0, e ?? {});
  }
  return s._$AI(r), s;
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const x = globalThis;
class z extends w {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    var e;
    const t = super.createRenderRoot();
    return (e = this.renderOptions).renderBefore ?? (e.renderBefore = t.firstChild), t;
  }
  update(t) {
    const e = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(t), this._$Do = Bt(e, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    var t;
    super.connectedCallback(), (t = this._$Do) == null || t.setConnected(!0);
  }
  disconnectedCallback() {
    var t;
    super.disconnectedCallback(), (t = this._$Do) == null || t.setConnected(!1);
  }
  render() {
    return k;
  }
}
var _t;
z._$litElement$ = !0, z.finalized = !0, (_t = x.litElementHydrateSupport) == null || _t.call(x, { LitElement: z });
const K = x.litElementPolyfillSupport;
K == null || K({ LitElement: z });
(x.litElementVersions ?? (x.litElementVersions = [])).push("4.2.2");
function Wt(r, t) {
  if (t.entity) return t.entity;
  const e = r.entities ?? {}, i = Object.values(e).filter((a) => a.platform === "ytmusic" && a.entity_id.startsWith("media_player."));
  if (i.length === 1 || i.length > 1) return i[0].entity_id;
  const s = Object.keys(r.states).filter((a) => a.startsWith("media_player.ytmusic_"));
  return s.length ? s[0] : null;
}
const Vt = "#ff2d55";
function Yt(r) {
  return (r == null ? void 0 : r.accent) || Vt;
}
const rt = class rt extends z {
  setConfig(t) {
    if (!t) throw new Error("Invalid configuration");
    this._config = t;
  }
  getCardSize() {
    return 3;
  }
  get entityId() {
    return this.hass && this._config ? Wt(this.hass, this._config) : null;
  }
  get stateObj() {
    var e, i;
    const t = this.entityId;
    return t ? (i = (e = this.hass) == null ? void 0 : e.states) == null ? void 0 : i[t] : void 0;
  }
  get accent() {
    return Yt(this._config ?? {});
  }
  updated(t) {
    super.updated(t), this.style.setProperty("--ytm-accent", this.accent);
  }
  callService(t, e, i = {}) {
    const s = this.entityId;
    s && this.hass.callService(t, e, { entity_id: s, ...i });
  }
};
rt.properties = { hass: { attribute: !1 }, _config: { state: !0 } };
let m = rt;
const W = q`
  :host {
    display: block;
    --ytm-accent: #ff3358;
    --ytm-accent-2: #ff7a93;
    --ytm-text: #f4f5f8;
    --ytm-dim: #99a0ad;
    --ytm-hairline: rgba(255, 255, 255, 0.08);
    --ytm-radius: 20px;
    color: var(--ytm-text);
    font-family: var(--ha-card-header-font-family, var(--paper-font-body1_-_font-family, inherit));
  }

  /* Let the card's own surface show — HA's opaque ha-card would flatten it. */
  ha-card {
    background: transparent;
    border: none;
    box-shadow: none;
    overflow: visible;
  }

  .glass {
    position: relative;
    border-radius: var(--ytm-radius);
    background:
      radial-gradient(135% 105% at 0% 0%, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0) 55%),
      linear-gradient(180deg, #1c2028 0%, #131519 100%);
    border: 1px solid var(--ytm-hairline);
    box-shadow: 0 16px 40px -16px rgba(0, 0, 0, 0.75), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(10px);
    overflow: hidden;
  }
  /* Faint accent glow in the corner for atmosphere. */
  .glass::after {
    content: "";
    position: absolute;
    top: -45%;
    right: -25%;
    width: 70%;
    height: 90%;
    background: radial-gradient(closest-side, var(--ytm-accent), transparent);
    opacity: 0.12;
    pointer-events: none;
  }
  .glass > * { position: relative; z-index: 1; }

  .sub { color: var(--ytm-dim); }
  .ttl { color: var(--ytm-text); font-weight: 650; letter-spacing: -0.01em; }
  .label {
    color: var(--ytm-dim);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    white-space: nowrap;
  }

  .ic {
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    color: #fff;
    cursor: pointer;
    transition: transform 0.13s ease, background 0.13s ease, color 0.13s ease, box-shadow 0.13s ease;
  }
  .ic:hover { background: rgba(255, 255, 255, 0.17); transform: translateY(-1px); }
  .ic.solid { background: #fff; color: #111; box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.7); }
  .ic.solid:hover { box-shadow: 0 10px 26px -6px var(--ytm-accent); transform: translateY(-1px) scale(1.03); }
  .ic.active { background: var(--ytm-accent); color: #fff; box-shadow: 0 0 16px -2px var(--ytm-accent); }
  button.ic { border: none; padding: 0; }

  .bar { height: 5px; border-radius: 99px; background: rgba(255, 255, 255, 0.14); position: relative; cursor: pointer; }
  .bar > i {
    position: absolute;
    inset: 0 auto 0 0;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--ytm-accent), var(--ytm-accent-2));
  }

  .empty { color: var(--ytm-dim); text-align: center; padding: 26px 14px; font-size: 13px; }
`;
function Ft(r, t) {
  const e = (r == null ? void 0 : r.attributes) ?? {};
  if (e.media_position == null) return null;
  let i = Number(e.media_position);
  if (r.state === "playing" && e.media_position_updated_at) {
    const s = Date.parse(e.media_position_updated_at);
    isNaN(s) || (i += Math.max(0, (t - s) / 1e3));
  }
  return e.media_duration != null && (i = Math.min(i, Number(e.media_duration))), Math.max(0, i);
}
function Z(r) {
  if (r == null || !isFinite(r) || r < 0) return "0:00";
  const t = Math.floor(r), e = Math.floor(t / 3600), i = Math.floor(t % 3600 / 60), s = String(t % 60).padStart(2, "0");
  return e > 0 ? `${e}:${String(i).padStart(2, "0")}:${s}` : `${i}:${s}`;
}
function M(r) {
  return r ? Array.isArray(r) ? r.filter(Boolean).join(", ") : r : "";
}
async function Kt(r, t, e, i) {
  const s = { type: "ytmusic/search", entity_id: t, query: e };
  return i && (s.filter = i), (await r.callWS(s)).results ?? [];
}
async function gt(r, t, e, i) {
  const s = { type: "ytmusic/browse", entity_id: t };
  return e && (s.item_type = e), i && (s.item_id = i), (await r.callWS(s)).items ?? [];
}
async function Zt(r, t, e) {
  return r.callWS({ type: "ytmusic/lyrics", entity_id: t, video_id: e });
}
const Jt = { off: "all", all: "one", one: "off" }, H = class H extends m {
  connectedCallback() {
    super.connectedCallback(), this._timer = window.setInterval(() => {
      this._tick = Date.now();
    }, 1e3);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._timer && clearInterval(this._timer);
  }
  setConfig(t) {
    super.setConfig(t);
  }
  getCardSize() {
    return 6;
  }
  get a() {
    var t;
    return ((t = this.stateObj) == null ? void 0 : t.attributes) ?? {};
  }
  _toggleLyrics() {
    var t;
    if (this._showLyrics = !this._showLyrics, this._showLyrics && this.entityId) {
      const e = (t = (this.a.queue ?? [])[this.a.queue_position]) == null ? void 0 : t.video_id;
      e && Zt(this.hass, this.entityId, e).then((i) => this._lyrics = i).catch(() => this._lyrics = { lines: null, synced: !1 });
    }
  }
  _seek(t) {
    const i = t.currentTarget.getBoundingClientRect(), s = Math.min(1, Math.max(0, (t.clientX - i.left) / i.width)), a = Number(this.a.media_duration) || 0;
    a && this.callService("media_player", "media_seek", { seek_position: s * a });
  }
  _sleep(t) {
    this.callService("ytmusic", "set_sleep_timer", t), this._sleepMenu = !1;
  }
  render() {
    const t = this.stateObj;
    if (!t) return l`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
    const e = this.a;
    if (!e.source)
      return l`<ha-card><div class="card">
        <div class="inner">
          <div class="speaker-prompt">
            <div class="empty">Select a speaker to start playback</div>
            <select @change=${(o) => this.callService("media_player", "select_source", { source: o.target.value })}>
              <option value="">Choose speaker…</option>
              ${(e.source_list ?? []).map((o) => l`<option value=${o}>${o}</option>`)}
            </select>
          </div>
        </div>
      </div></ha-card>`;
    const i = e.entity_picture ? `url(${e.entity_picture})` : "none", s = t.state === "playing", a = Ft(t, this._tick || Date.now()) ?? 0, n = Number(e.media_duration) || 0, c = n ? Math.min(100, a / n * 100) : 0;
    return l`<ha-card>
      <div class="card">
        <div class="bg" style="background-image:${i}"></div>
        <div class="veil"></div>
        <div class="inner">
          ${this._showLyrics ? this._renderLyrics(a) : d}
          <div class="cover ${e.entity_picture ? "has-art" : ""}"
               style=${e.entity_picture ? `background-image:url(${e.entity_picture})` : ""}
               @click=${() => e.lyrics_supported && this._toggleLyrics()}>
            ${e.entity_picture ? d : l`<span class="ph">♫</span>`}
          </div>
          <div class="meta">
            <div class="ttl">${e.media_title ?? "Nothing playing"}</div>
            <div class="sub">${M(e.media_artist)}</div>
          </div>
          <div class="ctl">
            <div class="bar" @click=${this._seek}><i style="width:${c}%"></i></div>
            <div class="times"><span>${Z(a)}</span><span>${Z(n)}</span></div>
            <div class="trans">
              <button class="ic" data-test="prev"
                      @click=${() => this.callService("media_player", "media_previous_track")}>⏮</button>
              <button class="ic solid big" data-test="playpause"
                      @click=${() => this.callService("media_player", s ? "media_pause" : "media_play")}>
                ${s ? "⏸" : "▶"}
              </button>
              <button class="ic" data-test="next"
                      @click=${() => this.callService("media_player", "media_next_track")}>⏭</button>
            </div>
            <div class="secrow">
              <button class="ic sm" data-test="shuffle"
                      @click=${() => this.callService("media_player", "shuffle_set", { shuffle: !e.shuffle })}
                      style=${e.shuffle ? "color:var(--ytm-accent)" : ""}>🔀</button>
              <button class="ic sm" data-test="repeat"
                      @click=${() => this.callService("media_player", "repeat_set", { repeat: Jt[e.repeat ?? "off"] })}>
                ${e.repeat === "one" ? "🔂" : "🔁"}
              </button>
              <button class="ic sm" data-test="mute"
                      @click=${() => this.callService("media_player", "volume_mute", { is_volume_muted: !e.is_volume_muted })}>
                ${e.is_volume_muted ? "🔇" : "🔊"}
              </button>
              <input data-test="volume" type="range" min="0" max="1" step="0.01"
                     .value=${String(e.volume_level ?? 0)}
                     @change=${(o) => this.callService("media_player", "volume_set", { volume_level: Number(o.target.value) })} />
              ${this._config.show_sleep_timer === !1 ? d : l`
                <button class="ic sm" data-test="sleep"
                        @click=${() => this._sleepMenu = !this._sleepMenu}>⏲</button>`}
              ${e.lyrics_supported && this._config.show_lyrics !== !1 ? l`
                <button class="ic sm" data-test="lyrics" @click=${this._toggleLyrics}>💬</button>` : d}
              <select class="chip"
                      @change=${(o) => this.callService("media_player", "select_source", { source: o.target.value })}>
                ${(e.source_list ?? []).map((o) => l`<option value=${o} ?selected=${o === e.source}>${o}</option>`)}
              </select>
            </div>
            ${this._sleepCountdown()}
            ${this._sleepMenu ? this._renderSleepMenu() : d}
          </div>
        </div>
      </div>
    </ha-card>`;
  }
  _sleepCountdown() {
    const t = this.a;
    if (t.sleep_timer_end_of_track)
      return l`<div class="secrow"><span class="chip active">⏲ stops after this track</span></div>`;
    if (!t.sleep_timer_ends_at) return d;
    const e = Math.max(0, Date.parse(t.sleep_timer_ends_at) - (this._tick || Date.now()));
    return l`<div class="secrow"><span class="chip active">⏲ ${Z(e / 1e3)} left</span></div>`;
  }
  _renderSleepMenu() {
    return l`<div class="menu glass">
      <div class="menu-title">Sleep timer</div>
      ${[15, 30, 45].map((t) => l`<div class="mi" @click=${() => this._sleep({ minutes: t })}>${t} min</div>`)}
      <div class="mi" @click=${() => this._sleep({ end_of_track: !0 })}>End of track</div>
      <div class="mi" @click=${() => this._sleep({ minutes: 0 })}>Off</div>
    </div>`;
  }
  _renderLyrics(t) {
    var i;
    const e = (i = this._lyrics) == null ? void 0 : i.lines;
    return l`<div class="lyr" @click=${() => this._showLyrics = !1}>
      <div class="lyr-header">
        <span class="sub" style="text-align:left">${this.a.media_title ?? ""}</span>
        <button class="ic sm" style="flex-shrink:0">✕</button>
      </div>
      <div class="lyr-body">
        ${e ? e.map((s, a) => {
      var o;
      const n = e[a + 1], c = ((o = this._lyrics) == null ? void 0 : o.synced) && s.start_ms != null && t * 1e3 >= s.start_ms && (!n || n.start_ms == null || t * 1e3 < n.start_ms);
      return l`<p class=${c ? "on" : ""}>${s.text}</p>`;
    }) : l`<div class="empty">No lyrics</div>`}
      </div>
    </div>`;
  }
  static getConfigElement() {
    return document.createElement("ytmusic-now-playing-editor");
  }
  static getStubConfig() {
    return { entity: "" };
  }
};
H.properties = { ...m.properties, _tick: { state: !0 }, _showLyrics: { state: !0 }, _lyrics: { state: !0 }, _sleepMenu: { state: !0 } }, H.styles = [W, q`
    /* Immersive (direction A): blurred entity_picture backdrop + dark veil; centered cover/title; bottom controls */
    .card { position: relative; border-radius: 20px; overflow: hidden; min-height: 400px; padding: 0; display: flex; flex-direction: column;
      background: radial-gradient(120% 80% at 50% -10%, rgba(255,255,255,.07), transparent 55%), linear-gradient(180deg, #1c2028, #111317);
      border: 1px solid var(--ytm-hairline);
      box-shadow: 0 18px 44px -16px rgba(0,0,0,.78), inset 0 1px 0 rgba(255,255,255,.07); }
    .bg { position: absolute; inset: 0; background-size: cover; background-position: center; filter: blur(26px) saturate(1.45) brightness(1.05); transform: scale(1.4); opacity: 1; }
    .veil { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,8,12,.35), rgba(8,8,12,.5) 42%, rgba(8,8,12,.88)); }
    .inner { position: relative; height: 100%; padding: 18px; display: flex; flex-direction: column; flex: 1; }
    .cover { width: 138px; height: 138px; border-radius: 16px; margin: 14px auto 16px; background-size: cover; background-position: center; box-shadow: 0 20px 50px -10px rgba(0,0,0,.7); cursor: pointer; flex-shrink: 0; display: grid; place-items: center; background-color: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.10); }
    .cover .ph { font-size: 46px; line-height: 1; color: var(--ytm-accent); opacity: .6; }
    .meta { text-align: center; }
    .ttl { font-size: 18px; }
    .sub { font-size: 13px; margin-top: 2px; }
    .ctl { margin-top: auto; }
    .bar { margin: 14px 0 6px; }
    .bar > i::after { content: ''; position: absolute; right: -5px; top: 50%; transform: translateY(-50%); width: 11px; height: 11px; border-radius: 50%; background: #fff; }
    .times { display: flex; justify-content: space-between; color: #aeb4c0; font-size: 11px; font-variant-numeric: tabular-nums; }
    .trans { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 12px; }
    .ic { width: 38px; height: 38px; font-size: 14px; }
    .ic.big { width: 52px; height: 52px; font-size: 20px; }
    .ic.sm { width: 32px; height: 32px; font-size: 12px; }
    .secrow { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
    .chip { display: inline-flex; gap: 6px; align-items: center; padding: 5px 10px; border-radius: 99px; background: rgba(255,255,255,.10); font-size: 12px; color: #dfe3ea; }
    .chip.active { background: var(--ytm-accent); color: #fff; }
    .lyr { position: absolute; inset: 0; padding: 18px; overflow: auto; display: flex; flex-direction: column; background: rgba(8,8,12,.92); }
    .lyr-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .lyr-body { flex: 1; overflow: hidden auto; }
    .lyr-body p { margin: 7px 0; color: rgba(255,255,255,.45); font-size: 14px; }
    .lyr-body p.on { color: #fff; font-weight: 600; font-size: 16px; }
    .menu { position: absolute; right: 16px; bottom: 64px; background: rgba(20,22,28,.96); border: 1px solid rgba(255,255,255,.16); border-radius: 12px; padding: 7px; width: 150px; z-index: 10; }
    .menu .menu-title { color: #8a909c; font-size: 10px; text-transform: uppercase; letter-spacing: .05em; padding: 4px 10px; }
    .menu .mi { color: #dfe3ea; font-size: 12.5px; padding: 7px 10px; border-radius: 7px; cursor: pointer; }
    .menu .mi:hover { background: rgba(255,255,255,.08); }
    select { background: rgba(255,255,255,.10); color: #fff; border: none; border-radius: 8px; padding: 5px 9px; font-size: 12px; cursor: pointer; max-width: 100%; box-sizing: border-box; }
    input[type=range] { -webkit-appearance: none; appearance: none; width: 96px; height: 4px; border-radius: 99px; background: rgba(255,255,255,.18); cursor: pointer; vertical-align: middle; }
    input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 12px; height: 12px; border-radius: 50%; background: #fff; }
    input[type=range]::-moz-range-thumb { width: 12px; height: 12px; border: none; border-radius: 50%; background: #fff; }
    input[type=range]::-moz-range-progress { height: 4px; border-radius: 99px; background: var(--ytm-accent); }
    .speaker-prompt { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 24px 18px; }
  `];
let X = H;
customElements.define("ytmusic-now-playing", X);
class Xt extends m {
  constructor() {
    super(...arguments), this._schema = [
      { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
      { name: "accent", selector: { text: {} } },
      { name: "show_lyrics", selector: { boolean: {} } },
      { name: "show_sleep_timer", selector: { boolean: {} } }
    ];
  }
  setConfig(t) {
    this._config = t;
  }
  render() {
    return !this.hass || !this._config ? l`` : l`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema}
      .computeLabel=${(t) => t.name} @value-changed=${this._vc}></ha-form>`;
  }
  _vc(t) {
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: t.detail.value }, bubbles: !0, composed: !0 }));
  }
}
customElements.define("ytmusic-now-playing-editor", Xt);
window.customCards = window.customCards ?? [];
window.customCards.push({ type: "ytmusic-now-playing", name: "YouTube Music — Now Playing", description: "Immersive now-playing + transport for the ytmusic player", preview: !0 });
const Qt = { song: "music", video: "music", playlist: "playlist", album: "album", artist: "artist" }, bt = [
  { key: "all", label: "All" },
  { key: "songs", label: "Songs", filter: "songs" },
  { key: "albums", label: "Albums", filter: "albums" },
  { key: "artists", label: "Artists", filter: "artists" },
  { key: "playlists", label: "Playlists", filter: "playlists" }
], I = class I extends m {
  constructor() {
    super(), this._seq = 0, this._q = "", this._tab = "all", this._results = null, this._loading = !1;
  }
  setConfig(t) {
    super.setConfig(t);
  }
  getCardSize() {
    return 6;
  }
  get typed() {
    var t, e;
    return !!((e = (t = this.stateObj) == null ? void 0 : t.attributes) != null && e.typed_search);
  }
  _onInput(t) {
    this._q = t.target.value, this._debounce && clearTimeout(this._debounce), this._debounce = window.setTimeout(() => this.runSearch(this._q), 300);
  }
  async runSearch(t) {
    var a;
    const e = t.trim();
    if (!e || !this.entityId) {
      this._results = null;
      return;
    }
    const i = ++this._seq;
    this._loading = !0;
    const s = this.typed && this._tab !== "all" ? (a = bt.find((n) => n.key === this._tab)) == null ? void 0 : a.filter : void 0;
    try {
      const n = await Kt(this.hass, this.entityId, e, s);
      i === this._seq && (this._results = n);
    } finally {
      i === this._seq && (this._loading = !1);
    }
  }
  _play(t) {
    this.callService("media_player", "play_media", {
      media_content_type: Qt[t.kind] ?? "music",
      media_content_id: t.id,
      extra: { metadata: { title: t.title, artist: t.subtitle, thumbnail: t.thumbnail } }
    });
  }
  _enqueue(t) {
    t.kind === "song" || t.kind === "video" ? this.callService("ytmusic", "enqueue", { video_id: t.id, title: t.title, artist: t.subtitle }) : this._play(t);
  }
  _more(t) {
    t.kind === "song" || t.kind === "video" ? this.callService("ytmusic", "play_next", { video_id: t.id, title: t.title, artist: t.subtitle }) : this.callService("ytmusic", "start_radio", { video_id: t.id });
  }
  render() {
    return this.stateObj ? l`<ha-card><div class="glass" style="padding:14px">
      <div class="box">🔎 <input .value=${this._q} placeholder="Search YouTube Music" @input=${this._onInput} />
        ${this._q ? l`<span @click=${() => {
      this._q = "", this._results = null;
    }} style="cursor:pointer">✕</span>` : d}</div>
      ${this.typed ? l`<div class="tabs" data-test="tabs">${bt.map((t) => l`<button class="tab ${this._tab === t.key ? "on" : ""}" @click=${() => {
      this._tab = t.key, this.runSearch(this._q);
    }}>${t.label}</button>`)}</div>` : d}
      ${this._renderResults()}
    </div></ha-card>` : l`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
  }
  _renderResults() {
    return this._loading ? l`<div class="empty">Searching…</div>` : this._results == null ? l`<div class="empty">Search for songs, albums, artists…</div>` : this._results.length ? this._results.map((t) => l`<div class="row">
      <div class="cov" style=${t.thumbnail ? `background-image:url(${t.thumbnail})` : ""}></div>
      <div class="meta"><div class="n ttl">${t.title}<span class="badge">${t.kind}</span></div><div class="n sub">${t.subtitle}</div></div>
      <div class="acts">
        <button class="ic solid" data-test="play" @click=${() => this._play(t)}>▶</button>
        <button class="ic" data-test="enqueue" @click=${() => this._enqueue(t)}>＋</button>
        <button class="ic" data-test="more" @click=${() => this._more(t)}>⋯</button>
      </div></div>`) : l`<div class="empty">No results</div>`;
  }
  static getConfigElement() {
    return document.createElement("ytmusic-search-editor");
  }
  static getStubConfig() {
    return { entity: "" };
  }
};
I.properties = { ...m.properties, _q: { state: !0 }, _tab: { state: !0 }, _results: { state: !0 }, _loading: { state: !0 } }, I.styles = [W, q`
    /* Layout B — action list. Ported from docs/superpowers/mockups/search-layout.html */
    .box { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,.25); border: 1px solid rgba(255,255,255,.10); border-radius: 14px; padding: 11px 14px; transition: border-color .15s ease; }
    .box:focus-within { border-color: var(--ytm-accent); }
    .box input { flex: 1; background: transparent; border: none; color: #fff; outline: none; font-size: 14px; }
    .box input::placeholder { color: var(--ytm-dim); }
    .clear-btn { cursor: pointer; color: var(--ytm-dim); }
    .tabs { display: flex; gap: 7px; margin: 14px 0 6px; flex-wrap: wrap; }
    .tab { font-size: 12px; padding: 6px 12px; border-radius: 99px; background: rgba(255,255,255,.07); color: var(--ytm-dim); cursor: pointer; border: none; transition: background .12s ease, color .12s ease; }
    .tab:hover { background: rgba(255,255,255,.13); color: #fff; }
    .tab.on { background: #fff; color: #111; font-weight: 650; }
    .row { display: flex; align-items: center; gap: 12px; padding: 9px 8px; border-radius: 12px; transition: background .12s ease; }
    .row:hover { background: rgba(255,255,255,.06); }
    .cov { width: 48px; height: 48px; border-radius: 10px; background-size: cover; background-color: rgba(255,255,255,.06); flex-shrink: 0; box-shadow: 0 4px 12px -4px rgba(0,0,0,.6); }
    .meta { flex: 1; min-width: 0; }
    .n { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .acts { display: flex; gap: 7px; flex-shrink: 0; }
    .acts .ic { width: 32px; height: 32px; font-size: 13px; }
    .badge { font-size: 9px; letter-spacing: .04em; text-transform: uppercase; background: rgba(255,255,255,.14); color: var(--ytm-dim); padding: 2px 6px; border-radius: 6px; margin-left: 8px; vertical-align: middle; }
    .empty { text-align: center; padding: 28px 0; color: var(--ytm-dim); font-size: 14px; }
  `];
let Q = I;
customElements.define("ytmusic-search", Q);
class Gt extends m {
  constructor() {
    super(...arguments), this._schema = [
      { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
      { name: "accent", selector: { text: {} } }
    ];
  }
  setConfig(t) {
    this._config = t;
  }
  render() {
    return !this.hass || !this._config ? l`` : l`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema} .computeLabel=${(t) => t.name}
      @value-changed=${(t) => this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: t.detail.value }, bubbles: !0, composed: !0 }))}></ha-form>`;
  }
}
customElements.define("ytmusic-search-editor", Gt);
window.customCards = window.customCards ?? [];
window.customCards.push({ type: "ytmusic-search", name: "YouTube Music — Search", description: "Search + queue tracks for the ytmusic player", preview: !0 });
const D = class D extends m {
  constructor() {
    super(), this._drag = null;
  }
  setConfig(t) {
    super.setConfig(t);
  }
  getCardSize() {
    return 5;
  }
  _move(t, e) {
    t !== e && this.callService("ytmusic", "move", { from_index: t, to_index: e }), this._drag = null;
  }
  render() {
    var s;
    const t = (s = this.stateObj) == null ? void 0 : s.attributes;
    if (!t) return l`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
    const e = t.queue ?? [], i = t.queue_position ?? 0;
    return l`<ha-card><div class="glass" style="padding:16px">
      <div class="hdr">
        <span class="label">Up Next</span>
        <span class="count">${e.length}</span>
        <div class="tools">
          <button class="tool" data-test="shuffle" @click=${() => this.callService("media_player", "shuffle_set", { shuffle: !t.shuffle })}>🔀 Shuffle</button>
          <button class="tool" data-test="clear" @click=${() => this.callService("ytmusic", "clear_queue")}>Clear</button>
        </div>
      </div>
      ${e.length ? e.map((a, n) => l`
        <div class="qrow ${n === i ? "now" : ""}" data-test="qrow" draggable="true"
             @click=${() => this.callService("ytmusic", "jump", { index: n })}
             @dragstart=${() => this._drag = n}
             @dragover=${(c) => c.preventDefault()}
             @drop=${(c) => {
      c.preventDefault(), this._drag != null && this._move(this._drag, n);
    }}>
          ${n === i ? l`<span class="eq">▮▮</span>` : l`<span class="handle" @click=${(c) => c.stopPropagation()}>≡</span>`}
          <div class="cov" style=${a.thumbnail ? `background-image:url(${a.thumbnail})` : ""}></div>
          <div class="meta"><div class="n ttl" style="font-size:13px">${a.title}</div><div class="n sub" style="font-size:11.5px">${M(a.artists)}</div></div>
          ${n === i ? d : l`<button class="x" data-test="remove" @click=${(c) => {
      c.stopPropagation(), this.callService("ytmusic", "remove", { index: n });
    }}>✕</button>`}
        </div>`) : l`<div class="empty">Queue is empty</div>`}
    </div></ha-card>`;
  }
  static getConfigElement() {
    return document.createElement("ytmusic-queue-editor");
  }
  static getStubConfig() {
    return { entity: "" };
  }
};
D.properties = { ...m.properties, _drag: { state: !0 } }, D.styles = [W, q`
    .hdr { display: flex; align-items: center; gap: 8px 10px; margin-bottom: 12px; flex-wrap: wrap; }
    .count { font-size: 11px; font-weight: 700; color: var(--ytm-dim); background: rgba(255,255,255,.08); border-radius: 99px; padding: 2px 8px; }
    .tools { margin-left: auto; display: flex; gap: 8px; }
    .tool { font-size: 12px; padding: 5px 11px; border-radius: 99px; background: rgba(255,255,255,.08); color: var(--ytm-text); border: none; cursor: pointer; white-space: nowrap; transition: background .12s ease; }
    .tool:hover { background: rgba(255,255,255,.16); }
    .qrow { position: relative; display: flex; align-items: center; gap: 11px; padding: 8px; border-radius: 12px; cursor: pointer; transition: background .12s ease; }
    .qrow:hover { background: rgba(255,255,255,.06); }
    .qrow.now { background: linear-gradient(90deg, rgba(255,51,88,.20), rgba(255,51,88,.05)); }
    .qrow.now::before { content: ''; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px; border-radius: 99px; background: var(--ytm-accent); }
    .handle { color: #7e8593; cursor: grab; font-size: 16px; width: 16px; text-align: center; flex-shrink: 0; }
    .cov { width: 42px; height: 42px; border-radius: 9px; background-size: cover; background-color: rgba(255,255,255,.06); flex-shrink: 0; box-shadow: 0 4px 12px -4px rgba(0,0,0,.6); }
    .meta { flex: 1; min-width: 0; } .n { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .x { color: #9aa0ab; background: rgba(255,255,255,.06); width: 26px; height: 26px; border-radius: 50%; border: none; cursor: pointer; flex-shrink: 0; transition: background .12s ease, color .12s ease; }
    .x:hover { background: rgba(255,51,88,.28); color: #fff; }
    .eq { color: var(--ytm-accent); width: 16px; text-align: center; font-size: 13px; flex-shrink: 0; }
  `];
let G = D;
customElements.define("ytmusic-queue", G);
class te extends m {
  constructor() {
    super(...arguments), this._schema = [
      { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
      { name: "accent", selector: { text: {} } },
      { name: "max_visible", selector: { number: { min: 0, mode: "box" } } }
    ];
  }
  setConfig(t) {
    this._config = t;
  }
  render() {
    return !this.hass || !this._config ? l`` : l`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema} .computeLabel=${(t) => t.name}
      @value-changed=${(t) => this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: t.detail.value }, bubbles: !0, composed: !0 }))}></ha-form>`;
  }
}
customElements.define("ytmusic-queue-editor", te);
window.customCards = window.customCards ?? [];
window.customCards.push({ type: "ytmusic-queue", name: "YouTube Music — Queue", description: "Queue with reorder/remove for the ytmusic player", preview: !0 });
const j = class j extends m {
  constructor() {
    super(), this._root = null, this._open = null, this._tracks = null, this._loading = !1;
  }
  setConfig(t) {
    super.setConfig(t);
  }
  getCardSize() {
    return 6;
  }
  updated(t) {
    super.updated(t), t.has("hass") && this._root == null && this.entityId && this.loadRoot();
  }
  async loadRoot() {
    if (this.entityId) {
      this._loading = !0;
      try {
        this._root = await gt(this.hass, this.entityId);
      } finally {
        this._loading = !1;
      }
    }
  }
  async openItem(t) {
    if (!(!this.entityId || !t.id)) {
      this._open = t, this._tracks = null, this._loading = !0;
      try {
        this._tracks = await gt(this.hass, this.entityId, "playlist", t.id);
      } finally {
        this._loading = !1;
      }
    }
  }
  _playAll() {
    var t;
    (t = this._open) != null && t.id && this.callService("media_player", "play_media", { media_content_type: "playlist", media_content_id: this._open.id });
  }
  _playTrack(t) {
    this.callService("media_player", "play_media", {
      media_content_type: "music",
      media_content_id: t.video_id,
      extra: { metadata: { title: t.title, artist: M(t.artists), album: t.album, thumbnail: t.thumbnail, duration: t.duration } }
    });
  }
  _enqueue(t) {
    this.callService("ytmusic", "enqueue", { video_id: t.video_id, title: t.title, artist: M(t.artists) });
  }
  render() {
    return this.stateObj ? l`<ha-card><div class="glass" style="padding:14px">${this._open ? this._renderDrill() : this._renderRoot()}</div></ha-card>` : l`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
  }
  _renderRoot() {
    if (this._loading && !this._root) return l`<div class="empty">Loading library…</div>`;
    const t = this._root ?? [];
    return t.length ? l`<div class="grid">${t.map((e) => l`<div class="tile" @click=${() => this.openItem(e)}>
      <div class="cov" style=${e.thumbnail ? `background-image:url(${e.thumbnail})` : ""}></div>
      <div class="n ttl">${e.title}</div></div>`)}</div>` : l`<div class="empty">Library is empty</div>`;
  }
  _renderDrill() {
    var t;
    return l`
      <div class="back" @click=${() => {
      this._open = null, this._tracks = null;
    }}>‹ Library</div>
      <div class="head"><div class="ttl">${(t = this._open) == null ? void 0 : t.title}</div>
        <button class="playall" data-test="playall" @click=${this._playAll}>▶ Play all</button></div>
      ${this._loading && !this._tracks ? l`<div class="empty">Loading…</div>` : (this._tracks ?? []).map((e, i) => l`
        <div class="trow"><span class="num">${i + 1}</span>
          <div class="cov2" style=${e.thumbnail ? `background-image:url(${e.thumbnail})` : ""}></div>
          <div class="meta"><div class="n2 ttl" style="font-size:13px">${e.title}</div><div class="n2 sub" style="font-size:11.5px">${M(e.artists)}</div></div>
          <div class="acts"><button class="ic solid" @click=${() => this._playTrack(e)}>▶</button><button class="ic" @click=${() => this._enqueue(e)}>＋</button></div>
        </div>`)}`;
  }
  static getConfigElement() {
    return document.createElement("ytmusic-library-editor");
  }
  static getStubConfig() {
    return { entity: "" };
  }
};
j.properties = { ...m.properties, _root: { state: !0 }, _open: { state: !0 }, _tracks: { state: !0 }, _loading: { state: !0 } }, j.styles = [W, q`
    /* Port from docs/superpowers/mockups/browse-layout.html (root grid A + drill-in). */
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(94px, 1fr)); gap: 14px; }
    .tile { cursor: pointer; transition: transform .12s ease; }
    .tile:hover { transform: translateY(-3px); }
    .tile .cov { aspect-ratio: 1; border-radius: 13px; background-size: cover; background-color: rgba(255,255,255,.06); box-shadow: 0 8px 22px -8px rgba(0,0,0,.7); }
    .tile:hover .cov { box-shadow: 0 12px 28px -8px rgba(0,0,0,.85); }
    .tile .n { font-size: 12.5px; margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .back { display: inline-flex; gap: 7px; align-items: center; color: var(--ytm-dim); cursor: pointer; margin-bottom: 14px; font-size: 13px; }
    .back:hover { color: #fff; }
    .head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; gap: 10px; }
    .playall { display: inline-flex; gap: 8px; align-items: center; background: var(--ytm-accent); color: #fff; font-weight: 650; font-size: 12.5px; padding: 8px 16px; border-radius: 99px; border: none; cursor: pointer; box-shadow: 0 6px 18px -6px var(--ytm-accent); transition: transform .12s ease; white-space: nowrap; }
    .playall:hover { transform: translateY(-1px); }
    .trow { display: flex; align-items: center; gap: 11px; padding: 8px 6px; border-radius: 10px; transition: background .12s ease; }
    .trow:hover { background: rgba(255,255,255,.06); }
    .num { color: #7e8593; width: 18px; text-align: center; font-size: 12px; flex-shrink: 0; }
    .cov2 { width: 36px; height: 36px; border-radius: 8px; background-size: cover; background-color: rgba(255,255,255,.06); flex-shrink: 0; }
    .meta { flex: 1; min-width: 0; } .n2 { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .acts { display: flex; gap: 7px; flex-shrink: 0; } .acts .ic { width: 30px; height: 30px; font-size: 12px; }
  `];
let tt = j;
customElements.define("ytmusic-library", tt);
class ee extends m {
  constructor() {
    super(...arguments), this._schema = [
      { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
      { name: "accent", selector: { text: {} } }
    ];
  }
  setConfig(t) {
    this._config = t;
  }
  render() {
    return !this.hass || !this._config ? l`` : l`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema} .computeLabel=${(t) => t.name}
      @value-changed=${(t) => this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: t.detail.value }, bubbles: !0, composed: !0 }))}></ha-form>`;
  }
}
customElements.define("ytmusic-library-editor", ee);
window.customCards = window.customCards ?? [];
window.customCards.push({ type: "ytmusic-library", name: "YouTube Music — Library", description: "Browse your library playlists + tracks", preview: !0 });
const re = "0.1.0";
export {
  re as YTMUSIC_CARD_VERSION
};
