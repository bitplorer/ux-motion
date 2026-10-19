"use strict";

/* Node DOM shim for the packaged player. No dependencies.
   stdin: {"probe":"duration","plans":{...}} or {"probe":"morph"}
   stdout: one JSON object. */

const fs = require("fs");

const VOID = { input: 1, img: 1, br: 1, hr: 1, meta: 1, link: 1, source: 1 };
const animCalls = [];
const errors = [];

function Element(tag) {
  this.tagName = String(tag || "div").toUpperCase();
  this.attrs = {};
  this.children = [];
  this.parentNode = null;
  this.style = {};
  this.hidden = false;
  this._value = "";
}

Element.prototype.setAttribute = function (name, value) {
  this.attrs[name] = String(value);
  if (name === "value") this._value = String(value);
};

Element.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};

Element.prototype.removeAttribute = function (name) {
  delete this.attrs[name];
};

Object.defineProperty(Element.prototype, "id", {
  get: function () {
    return this.attrs.id || "";
  },
  set: function (value) {
    this.setAttribute("id", value);
  },
});

Object.defineProperty(Element.prototype, "value", {
  get: function () {
    return this._value;
  },
  set: function (value) {
    this._value = String(value);
  },
});

Element.prototype.contains = function (node) {
  var current = node;
  while (current) {
    if (current === this) return true;
    current = current.parentNode;
  }
  return false;
};

Element.prototype.closest = function (sel) {
  var current = this;
  while (current && current.tagName) {
    if (sel.charAt(0) === "#" && current.id === sel.slice(1)) return current;
    if (current.tagName.toLowerCase() === sel.toLowerCase()) return current;
    current = current.parentNode;
  }
  return null;
};

function dropFocusUnder(node) {
  if (document.activeElement && node.contains(document.activeElement)) {
    document.activeElement = document.body;
  }
}

Element.prototype.appendChild = function (child) {
  if (child.parentNode) child.parentNode.removeChild(child);
  this.children.push(child);
  child.parentNode = this;
  return child;
};

Element.prototype.removeChild = function (child) {
  var index = this.children.indexOf(child);
  if (index < 0) throw new Error("removeChild: not a child");
  this.children.splice(index, 1);
  dropFocusUnder(child);
  child.parentNode = null;
  return child;
};

Element.prototype.replaceChild = function (next, old) {
  var index = this.children.indexOf(old);
  if (index < 0) throw new Error("replaceChild: not a child");
  if (next.parentNode) next.parentNode.removeChild(next);
  this.children[index] = next;
  next.parentNode = this;
  dropFocusUnder(old);
  old.parentNode = null;
  return old;
};

Object.defineProperty(Element.prototype, "firstElementChild", {
  get: function () {
    return this.children[0] || null;
  },
});

Object.defineProperty(Element.prototype, "isConnected", {
  get: function () {
    var current = this;
    while (current) {
      if (current === document.documentElement || current === document.body) return true;
      current = current.parentNode;
    }
    return false;
  },
});

Element.prototype.getBoundingClientRect = function () {
  if (this.id === "leave") return { left: 0, top: 0, width: 50, height: 50 };
  if (this.id === "arrive") return { left: 200, top: 0, width: 100, height: 100 };
  return { left: 0, top: 0, width: 10, height: 10 };
};

Element.prototype.focus = function () {
  document.activeElement = this;
};

Element.prototype.animate = function (keyframes, opts) {
  var duration = opts && typeof opts === "object" ? opts.duration : opts;
  animCalls.push({ id: this.id, duration: duration });
  return {
    finished: Promise.resolve(),
    pause: function () {},
    cancel: function () {},
    commitStyles: function () {},
    currentTime: 0,
  };
};

function parseAttrs(raw, el) {
  var re = /([^\s=/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|(\S+)))?/g;
  var match;
  while ((match = re.exec(raw))) {
    var value = match[2];
    if (value == null) value = match[3];
    if (value == null) value = match[4];
    if (value == null) value = "";
    el.setAttribute(match[1], value);
  }
}

function parseHTML(html) {
  var roots = [];
  var stack = [{ children: roots, parentNode: null, tagName: "" }];
  var re = /<!--[\s\S]*?-->|<\/([a-zA-Z0-9]+)\s*>|<([a-zA-Z0-9]+)([^>]*?)(\/?)>|([^<]+)/g;
  var match;
  while ((match = re.exec(String(html)))) {
    if (match[0].indexOf("<!--") === 0) continue;
    if (match[1]) {
      var close = match[1].toLowerCase();
      while (stack.length > 1 && stack[stack.length - 1].tagName.toLowerCase() !== close) stack.pop();
      if (stack.length > 1) stack.pop();
      continue;
    }
    if (match[2]) {
      var el = new Element(match[2]);
      parseAttrs(match[3] || "", el);
      var parent = stack[stack.length - 1];
      parent.children.push(el);
      el.parentNode = parent.tagName ? parent : null;
      var selfClose = !!match[4] || !!VOID[match[2].toLowerCase()];
      if (!selfClose) stack.push(el);
      continue;
    }
  }
  return roots;
}

Object.defineProperty(Element.prototype, "innerHTML", {
  get: function () {
    return this.children
      .map(function (child) {
        return "<" + child.tagName.toLowerCase() + ">";
      })
      .join("");
  },
  set: function (html) {
    this.children.forEach(function (child) {
      child.parentNode = null;
    });
    dropFocusUnder(this);
    this.children = [];
    var parsed = parseHTML(html);
    for (var i = 0; i < parsed.length; i++) this.appendChild(parsed[i]);
  },
});

function walk(node, visit) {
  if (!node || !node.children) return;
  for (var i = 0; i < node.children.length; i++) {
    visit(node.children[i]);
    walk(node.children[i], visit);
  }
}

function queryAll(root, sel) {
  var found = [];
  var id = sel.charAt(0) === "#" ? sel.slice(1) : null;
  walk(root, function (node) {
    if (id) {
      if (node.id === id) found.push(node);
      return;
    }
    if (node.tagName.toLowerCase() === sel.toLowerCase()) found.push(node);
  });
  return found;
}

const document = {
  readyState: "complete",
  documentElement: null,
  body: null,
  activeElement: null,
  addEventListener: function () {},
  removeEventListener: function () {},
  dispatchEvent: function () {},
  createElement: function (tag) {
    return new Element(tag);
  },
  getElementById: function (id) {
    return queryAll(document.documentElement, "#" + id)[0] || null;
  },
  querySelector: function (sel) {
    return queryAll(document.documentElement, sel)[0] || null;
  },
  querySelectorAll: function (sel) {
    return queryAll(document.documentElement, sel);
  },
};

const html = new Element("html");
const body = new Element("body");
html.appendChild(body);
document.documentElement = html;
document.body = body;
document.activeElement = body;

function mount(tag, id) {
  var node = new Element(tag);
  node.id = id;
  body.appendChild(node);
  return node;
}

mount("div", "a");
mount("div", "leave");
mount("div", "arrive");
var card = mount("div", "card");
var input = new Element("input");
input.id = "q";
input.value = "typed";
card.appendChild(input);
mount("div", "x");

const realError = console.error;
console.error = function () {
  var parts = [];
  for (var i = 0; i < arguments.length; i++) parts.push(String(arguments[i]));
  errors.push(parts.join(" "));
  realError.apply(console, arguments);
};

global.window = global;
global.document = document;
global.CustomEvent = function CustomEvent(type, init) {
  this.type = type;
  this.detail = init && init.detail;
};

const playerPath = process.argv[2];
eval(fs.readFileSync(playerPath, "utf8"));

function durationsFor(sel) {
  var id = sel.charAt(0) === "#" ? sel.slice(1) : sel;
  return animCalls.filter(function (call) {
    return call.id === id;
  }).map(function (call) {
    return call.duration;
  });
}

async function playLabeled(plans) {
  var out = {};
  var labels = Object.keys(plans);
  for (var i = 0; i < labels.length; i++) {
    var label = labels[i];
    animCalls.length = 0;
    try {
      UxMotion.cancel();
    } catch (err) {}
    await UxMotion.play(plans[label].plan);
    out[label] = durationsFor(plans[label].sel);
  }
  return out;
}

function morphOnce(focused) {
  errors.length = 0;
  global.Idiomorph = {
    morph: function () {
      throw new Error("idiomorph failed");
    },
  };
  var before = document.getElementById("card");
  var field = document.getElementById("q");
  field.value = "typed";
  if (focused) field.focus();
  else document.activeElement = document.body;
  var thrown = null;
  try {
    UxMotion.applyOp({
      op: "morph",
      target: "#card",
      html: '<div id="card"><input id="q" value="server"></div>',
    });
  } catch (err) {
    thrown = String(err && err.message ? err.message : err);
  }
  var after = document.getElementById("card");
  var active = document.activeElement;
  return {
    same_node: before === after,
    focus_kept: !!(
      active &&
      active.id === "q" &&
      active.closest("#card") === before
    ),
    input_value: document.getElementById("q").value,
    errors_surfaced: errors.slice(),
    thrown: thrown,
  };
}

async function main() {
  var raw = fs.readFileSync(0, "utf8");
  var req = JSON.parse(raw);
  var result;
  if (req.probe === "duration") {
    result = await playLabeled(req.plans);
  } else if (req.probe === "morph") {
    result = { focused: morphOnce(true), unfocused: morphOnce(false) };
  } else {
    throw new Error("unknown probe " + req.probe);
  }
  process.stdout.write(JSON.stringify(result));
}

main().catch(function (err) {
  process.stderr.write(String(err && err.stack ? err.stack : err) + "\n");
  process.exit(2);
});
