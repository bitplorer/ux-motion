/* ux-motion web.v1.3.0 player — vanilla JS, no framework.
   Schedule contract: same as ux_motion.interpret.
   Supports: presence, share (FLIP), bind (scroll/drag), score (multi-hop),
   spring, offset-path, reduce_tree swap. */
(function (global) {
  "use strict";

  var running = new Map();
  var playing = new Map();
  var queued = [];
  var scores = new Map(); // scoreId -> { nodes: Element[], resolve: fn }
  var shares = new Map(); // shareId -> first rect

  function prefersReduced() {
    return !!(global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function q(sel, root) {
    try {
      return (root || document).querySelector(sel);
    } catch (e) {
      return null;
    }
  }

  function qa(sel, root) {
    try {
      return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    } catch (e) {
      return [];
    }
  }

  function kf(side) {
    side = side || {};
    var x = side.x || 0;
    var y = side.y || 0;
    var s = side.scale == null ? 1 : side.scale;
    var r = side.rotate || 0;
    var blur = side.blur;
    var t = "translate(" + x + "px," + y + "px) rotate(" + r + "deg) scale(" + s + ")";
    var out = {
      opacity: side.opacity == null ? 1 : String(side.opacity),
      transform: t,
    };
    if (blur != null) out.filter = "blur(" + blur + "px)";
    if (side.offset != null) out.offsetDistance = Math.round(side.offset * 100) + "%";
    return out;
  }

  function cancelTarget(sel) {
    var a = running.get(sel);
    if (a && a.cancel) {
      try {
        a.cancel();
      } catch (e) {}
    }
    running.delete(sel);
  }

  function cancelAll() {
    queued = [];
    running.forEach(function (_a, key) {
      cancelTarget(key);
    });
    playing.clear();
  }

  function springDuration(spring) {
    if (!spring) return 480;
    var mass = spring.mass || 1;
    var stiffness = spring.stiffness || 280;
    var damping = spring.damping || 24;
    var omega = Math.sqrt(stiffness / mass);
    var zeta = damping / (2 * Math.sqrt(stiffness * mass));
    var t = zeta < 1 ? 4 / (zeta * omega) : 4 / omega;
    return Math.min(Math.max(t * 1000, 120), 2000);
  }

  function animateEl(el, recipe, key, reducedPolicy) {
    if (!el || !el.animate) return Promise.resolve();
    var reduced = prefersReduced();
    var skip = reduced && reducedPolicy === "skip";
    var simplify = reduced && reducedPolicy === "simplify";
    var duration;
    if (recipe.spring || recipe.engine === "spring") {
      duration = skip ? 0 : simplify ? 80 : springDuration(recipe.spring);
    } else {
      duration = skip ? 0 : simplify ? Math.min(recipe.duration || 0, 80) : recipe.duration || 240;
    }
    var delay = skip ? 0 : recipe.delay || 0;
    cancelTarget(key);

    if (recipe.path && recipe.path.d) {
      try {
        el.style.offsetPath = 'path("' + recipe.path.d + '")';
        el.style.offsetRotate = recipe.path.rotate || "auto";
      } catch (e) {}
    }

    try {
      var anim = el.animate([kf(recipe.from), kf(recipe.to)], {
        duration: duration,
        delay: delay,
        easing: recipe.spring ? "cubic-bezier(0.22, 1, 0.36, 1)" : recipe.easing || "ease-out",
        fill: recipe.fill || "both",
      });
      running.set(key, anim);
      return anim.finished.then(
        function () {
          running.delete(key);
          try {
            anim.commitStyles();
            anim.cancel();
          } catch (e) {}
        },
        function () {
          running.delete(key);
        }
      );
    } catch (e) {
      return Promise.resolve();
    }
  }

  function mark(el, role, present) {
    if (!el) return;
    el.setAttribute("data-uxm-role", role === "layout" ? "stay" : role);
    el.setAttribute("data-uxm-present", present ? "1" : "0");
  }

  function applyAfter(el, after) {
    if (!el) return;
    if (after === "remove") {
      if (el.parentNode) el.parentNode.removeChild(el);
      return;
    }
    if (after === "hide") {
      el.hidden = true;
      el.setAttribute("aria-hidden", "true");
    }
  }

  function injectHtml(host, html) {
    if (!host) return null;
    var wrap = document.createElement("div");
    wrap.innerHTML = String(html);
    var incoming = wrap.firstElementChild;
    if (!incoming) {
      host.innerHTML = String(html);
      return host;
    }
    incoming.setAttribute("data-uxm-incoming", "1");
    // Prefer Idiomorph so matching ids (img-{sku}) keep decoded bitmaps.
    // Scope: only when the incoming root is the same node as the live host.
    // Idiomorph's id map is the old host + its pantry — it does not steal
    // nodes from the rest of the document.
    if (
      global.Idiomorph &&
      typeof global.Idiomorph.morph === "function" &&
      incoming.id &&
      host.id &&
      incoming.id === host.id
    ) {
      try {
        global.Idiomorph.morph(host, incoming, {
          morphStyle: "outerHTML",
          restoreFocus: false,
        });
      } catch (err) {
        if (host.parentNode) {
          host.parentNode.replaceChild(incoming, host);
          return incoming;
        }
        host.innerHTML = "";
        host.appendChild(incoming);
        return incoming;
      }
      // Tag-name change replaces the node. Never animate a detached host.
      if (host.isConnected) return host;
      var live = host.id ? document.getElementById(host.id) : null;
      return live || incoming;
    }
    if (incoming.id && host.id && incoming.id === host.id && host.parentNode) {
      host.parentNode.replaceChild(incoming, host);
      return incoming;
    }
    host.innerHTML = "";
    host.appendChild(incoming);
    return incoming;
  }

  function rectOf(el) {
    var r = el.getBoundingClientRect();
    return { left: r.left, top: r.top, width: r.width, height: r.height };
  }

  function playShare(node, reduced) {
    var leave = q(node.leave);
    var arrive = q(node.arrive);
    if (!leave || !arrive) return Promise.resolve();
    var first = rectOf(leave);
    var last = rectOf(arrive);
    var dx = first.left - last.left;
    var dy = first.top - last.top;
    var sx = first.width / (last.width || 1);
    var sy = first.height / (last.height || 1);
    var recipe = node.recipe || { duration: 320, easing: "cubic-bezier(0.16, 1, 0.3, 1)", fill: "both" };
    mark(leave, "share-leave", false);
    mark(arrive, "share-arrive", true);
    arrive.hidden = false;
    arrive.removeAttribute("hidden");
    var inv = {
      from: { x: dx, y: dy, scale: (sx + sy) / 2, opacity: 1 },
      to: { x: 0, y: 0, scale: 1, opacity: 1 },
      duration: recipe.duration || 320,
      delay: recipe.delay || 0,
      easing: recipe.easing || "cubic-bezier(0.16, 1, 0.3, 1)",
      fill: "both",
    };
    return animateEl(arrive, inv, "share:" + node.id, reduced).then(function () {
      applyAfter(leave, "hide");
    });
  }

  function playTrack(node, reduced) {
    if (node.kind === "stagger") {
      var els = qa(node.selector);
      return Promise.all(
        els.map(function (el, i) {
          var rec = Object.assign({}, node.recipe, {
            delay: (node.recipe.delay || 0) + i * (node.gap_ms || 40),
          });
          mark(el, node.role, node.role !== "exit");
          return animateEl(el, rec, node.selector + "#" + i, reduced).then(function () {
            if (node.role === "exit") applyAfter(el, node.after || "keep");
          });
        })
      );
    }
    if (node.kind === "share") return playShare(node, reduced);

    var el = q(node.target);
    if (node.role === "enter" && node.html) {
      // Drop any fill:both leftover on the live host *before* morph.
      // replaceChild used to do this by throwing the node away.
      if (el) cancelTarget(node.target);
      if (el) el = injectHtml(el, node.html);
    }
    if (!el) return Promise.resolve();
    if (node.role === "enter") {
      el.hidden = false;
      el.removeAttribute("hidden");
      el.removeAttribute("aria-hidden");
    }
    mark(el, node.role, node.role !== "exit");
    return animateEl(el, node.recipe, node.target, reduced).then(function () {
      if (node.role === "exit") applyAfter(el, node.after || "remove");
      else {
        el.removeAttribute("data-uxm-incoming");
        mark(el, node.role, true);
      }
    });
  }

  function playNode(node, reduced) {
    if (!node) return Promise.resolve();
    if (node.kind === "track" || node.kind === "stagger" || node.kind === "share") {
      return playTrack(node, reduced);
    }
    if (node.kind === "group") {
      return playPhase(
        { kind: "phase", mode: node.mode || "wait", children: node.tracks || [] },
        reduced
      );
    }
    if (node.kind === "phase") return playPhase(node, reduced);
    if (node.kind === "bind") return playBind(node, reduced);
    if (node.kind === "score") return playScore(node, reduced);
    if (node.kind === "cue") return playCue(node, reduced);
    return Promise.resolve();
  }

  function playPhase(phase, reduced) {
    var kids = phase.children || [];
    var mode = phase.mode || "parallel";
    var staggerMs = phase.stagger_ms || 0;
    if (mode === "sequence") {
      return kids.reduce(function (p, child, i) {
        return p.then(function () {
          if (i && staggerMs) {
            return new Promise(function (res) {
              setTimeout(res, staggerMs);
            }).then(function () {
              return playNode(child, reduced);
            });
          }
          return playNode(child, reduced);
        });
      }, Promise.resolve());
    }
    if (mode === "wait") {
      var exits = [];
      var stays = [];
      var enters = [];
      var nested = [];
      kids.forEach(function (n) {
        if (n.kind === "track" || n.kind === "stagger") {
          if (n.role === "exit") exits.push(n);
          else if (n.role === "enter") enters.push(n);
          else stays.push(n);
        } else {
          nested.push(n);
        }
      });
      return Promise.all([
        Promise.all(exits.map(function (n) {
          return playTrack(n, reduced);
        }))
          .then(function () {
            return Promise.all(stays.map(function (n) {
              return playTrack(n, reduced);
            }));
          })
          .then(function () {
            return Promise.all(enters.map(function (n) {
              return playTrack(n, reduced);
            }));
          }),
        Promise.all(nested.map(function (n) {
          return playNode(n, reduced);
        })),
      ]);
    }
    return Promise.all(
      kids.map(function (c, i) {
        if (!staggerMs) return playNode(c, reduced);
        return new Promise(function (res) {
          setTimeout(res, i * staggerMs);
        }).then(function () {
          return playNode(c, reduced);
        });
      })
    );
  }

  function playBind(node, reduced) {
    // Bind installs a scrub listener; for one-shot play we run the child fully.
    // Hosts that want continuous scrub call UxMotion.scrub(planId, progress).
    var child = node.child;
    if (!child) return Promise.resolve();
    var host = q(node.target) || document;
    var planKey = "bind:" + node.target;
    host.setAttribute("data-uxm-bind", node.input || "scroll");
    if (node.input === "scroll") {
      var onScroll = function () {
        var rect = host.getBoundingClientRect ? host.getBoundingClientRect() : { top: 0, height: 1 };
        var vh = global.innerHeight || 1;
        var progress = 1 - Math.min(Math.max((rect.top + rect.height) / (vh + rect.height), 0), 1);
        host.setAttribute("data-uxm-progress", String(progress.toFixed(3)));
      };
      host._uxmScroll = onScroll;
      global.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
    return playNode(child, reduced);
  }

  function playScore(node, reduced) {
    var child = node.child;
    if (!child) return Promise.resolve();
    if (node.phase === "hold") {
      return playNode(child, reduced).then(function () {
        // Keep exiting nodes in the map until cue
        scores.set(node.id, { held: true, at: Date.now() });
        document.dispatchEvent(
          new CustomEvent("ux-motion:score-hold", { detail: { id: node.id } })
        );
      });
    }
    return playNode(child, reduced);
  }

  function playCue(node, reduced) {
    var held = scores.get(node.score);
    if (held) {
      scores.delete(node.score);
      document.dispatchEvent(
        new CustomEvent("ux-motion:score-resolve", { detail: { id: node.score } })
      );
    }
    if (node.child) return playNode(node.child, reduced);
    return Promise.resolve();
  }

  function collectTargets(node, acc) {
    if (!node) return;
    if (node.target) acc.push(node.target);
    if (node.selector) acc.push(node.selector);
    if (node.leave) acc.push(node.leave);
    if (node.arrive) acc.push(node.arrive);
    (node.tracks || []).forEach(function (c) {
      collectTargets(c, acc);
    });
    (node.children || []).forEach(function (c) {
      collectTargets(c, acc);
    });
    if (node.child) collectTargets(node.child, acc);
  }

  function drain() {
    if (playing.size) return;
    var next = queued.shift();
    if (next) next();
  }

  function runPlan(plan) {
    var reduced = plan.reduced || "simplify";
    if (reduced === "swap" && plan.reduce_tree && prefersReduced()) {
      return playNode(plan.reduce_tree, "skip");
    }
    var body = function () {
      return playNode(plan.root, reduced);
    };
    if (plan.engine === "view" && document.startViewTransition && !prefersReduced()) {
      try {
        var vt = document.startViewTransition(function () {
          return body();
        });
        return vt.finished.catch(function () {});
      } catch (e) {
        return body();
      }
    }
    return body();
  }

  function playPlan(plan) {
    if (!plan || plan.kind !== "plan") return Promise.resolve();
    if (plan.interrupt === "ignore" && playing.has(plan.id)) {
      return playing.get(plan.id);
    }
    if (plan.interrupt === "queue" && playing.size) {
      return new Promise(function (resolve) {
        queued.push(function () {
          resolve(playPlan(Object.assign({}, plan, { interrupt: "replace" })));
        });
      });
    }
    if (plan.interrupt === "replace") {
      var acc = [];
      collectTargets(plan.root, acc);
      acc.forEach(cancelTarget);
    }
    document.dispatchEvent(
      new CustomEvent("ux-motion:start", { detail: { id: plan.id, complete: plan.complete || null } })
    );
    var p = runPlan(plan).then(function () {
      playing.delete(plan.id);
      document.dispatchEvent(
        new CustomEvent("ux-motion:complete", {
          detail: { id: plan.id, action: plan.complete || null },
        })
      );
      drain();
    });
    playing.set(plan.id, p);
    return p;
  }

  function applyAll(sel, fn) {
    qa(sel).forEach(fn);
  }

  function applyOp(op) {
    if (!op || !op.op) return Promise.resolve();
    if (op.op === "transition.play" && op.plan) return playPlan(op.plan);
    if (op.op === "transition.rewind" && op.plan) return playPlan(op.plan);
    if (op.op === "transition.cancel") {
      cancelAll();
      document.dispatchEvent(new CustomEvent("ux-motion:interrupt", { detail: { id: op.id || null } }));
      return Promise.resolve();
    }
    if (op.op === "seq" && op.ops) {
      return op.ops.reduce(function (p, child) {
        return p.then(function () {
          return applyOp(child);
        });
      }, Promise.resolve());
    }
    if (op.op === "morph" && op.target && op.html != null) {
      var el = q(op.target);
      if (el) injectHtml(el, op.html);
      return Promise.resolve();
    }
    if (op.op === "remove" && op.target) {
      applyAll(op.target, function (rm) {
        if (rm.parentNode) rm.parentNode.removeChild(rm);
      });
      return Promise.resolve();
    }
    if (op.op === "set_attr" && op.target && op.attrs) {
      applyAll(op.target, function (sa) {
        Object.keys(op.attrs).forEach(function (k) {
          sa.setAttribute(k, String(op.attrs[k]));
        });
      });
    }
    if (op.op === "set_text" && op.target) {
      applyAll(op.target, function (st) {
        st.textContent = op.text || "";
      });
    }
    return Promise.resolve();
  }

  function applyOps(ops) {
    return (ops || []).reduce(function (p, op) {
      return p.then(function () {
        return applyOp(op);
      });
    }, Promise.resolve());
  }

  function bootEmbedded() {
    if (!document || !document.querySelectorAll) return;
    var nodes = document.querySelectorAll('script[type="application/ux-motion+json"]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.getAttribute("data-play") === "false") continue;
      try {
        var plan = JSON.parse(el.textContent || "{}");
        if (plan && plan.kind === "plan") playPlan(plan);
      } catch (err) {}
    }
  }

  global.UxMotion = {
    play: playPlan,
    applyOps: applyOps,
    applyOp: applyOp,
    cancel: cancelAll,
    boot: bootEmbedded,
    version: "1.3.0",
  };

  if (typeof document !== "undefined" && document.addEventListener) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bootEmbedded);
    } else {
      bootEmbedded();
    }
  }
})(typeof window !== "undefined" ? window : this);
