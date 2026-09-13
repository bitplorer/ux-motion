/* ux-motion web.v1.3.0 player — vanilla JS, no framework.
   Schedule contract: same as ux_motion.interpret.
   Supports: presence, share (FLIP), bind (scroll/drag), score (multi-hop),
   spring, offset-path, path d morph, reduce_tree swap. */
(function (global) {
  "use strict";

  var running = new Map();
  var playing = new Map();
  var queued = [];
  var scores = new Map(); // scoreId -> { nodes: Element[], resolve: fn }
  var shares = new Map(); // shareId -> first rect
  var tapes = new Map(); // planId -> live bind tape (Soft 1 scroll/progress)

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

  function morphD(recipe, side) {
    var block = recipe && recipe.morph && recipe.morph.d;
    if (!block) return null;
    var raw = block[side];
    if (typeof raw !== "string" || !raw) return null;
    return 'path("' + raw + '")';
  }

  function commitMorphD(el, recipe) {
    var block = recipe && recipe.morph && recipe.morph.d;
    if (!el || !block || typeof block.to !== "string" || !el.setAttribute) return;
    try {
      el.setAttribute("d", block.to);
    } catch (e) {}
  }

  function kf(side, recipe, which) {
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
    var d = morphD(recipe, which);
    if (d) out.d = d;
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
    var tapeIds = [];
    tapes.forEach(function (_tape, planId) {
      tapeIds.push(planId);
    });
    tapeIds.forEach(releaseTape);
  }

  function clamp01(n) {
    n = Number(n);
    if (!(n > 0)) return 0;
    if (n > 1) return 1;
    return n;
  }

  function recipeDuration(recipe, reducedPolicy) {
    recipe = recipe || {};
    var reduced = prefersReduced();
    var skip = reduced && reducedPolicy === "skip";
    var simplify = reduced && reducedPolicy === "simplify";
    if (recipe.spring || recipe.engine === "spring") {
      return skip ? 0 : simplify ? 80 : springDuration(recipe.spring);
    }
    return skip ? 0 : simplify ? Math.min(recipe.duration || 0, 80) : recipe.duration || 240;
  }

  function measureScrollProgress(host, axis) {
    var x = axis === "x";
    if (host && host !== document.documentElement && host !== document.body) {
      if (x && host.scrollWidth > host.clientWidth + 1) {
        var maxX = host.scrollWidth - host.clientWidth;
        return maxX <= 0 ? 0 : clamp01(host.scrollLeft / maxX);
      }
      if (!x && host.scrollHeight > host.clientHeight + 1) {
        var maxY = host.scrollHeight - host.clientHeight;
        return maxY <= 0 ? 0 : clamp01(host.scrollTop / maxY);
      }
    }
    var rect = host && host.getBoundingClientRect ? host.getBoundingClientRect() : { top: 0, left: 0, height: 1, width: 1 };
    if (x) {
      var vw = global.innerWidth || 1;
      var w = rect.width || 1;
      return 1 - clamp01((rect.left + w) / (vw + w));
    }
    var vh = global.innerHeight || 1;
    var h = rect.height || 1;
    return 1 - clamp01((rect.top + h) / (vh + h));
  }

  function partitionWait(kids) {
    // Soft 3: frozen bags exits/stays/enters/nested. Missing role is enter.
    var bags = { exits: [], stays: [], enters: [], nested: [] };
    (kids || []).forEach(function (n) {
      if (!n) return;
      if (n.kind === "track" || n.kind === "stagger") {
        var role = n.role || "enter";
        if (role === "exit") bags.exits.push(n);
        else if (role === "enter") bags.enters.push(n);
        else bags.stays.push(n);
      } else {
        bags.nested.push(n);
      }
    });
    return bags;
  }

  function collectTape(node, t0, items, reduced) {
    if (!node) return t0;
    var kind = node.kind;
    if (kind === "track") {
      var rec = node.recipe || {};
      var start = t0 + (rec.delay || 0);
      var duration = recipeDuration(rec, reduced);
      items.push({
        kind: "track",
        target: node.target,
        role: node.role || "enter",
        after: node.after,
        html: node.html,
        recipe: rec,
        start: start,
        duration: duration,
      });
      return start + duration;
    }
    if (kind === "stagger") {
      var recs = node.recipe || {};
      var durationS = recipeDuration(recs, reduced);
      var gap = node.gap_ms || 40;
      var n = qa(node.selector).length || 3;
      var endS = t0;
      for (var i = 0; i < n; i++) {
        var startS = t0 + (recs.delay || 0) + i * gap;
        items.push({
          kind: "stagger",
          selector: node.selector,
          index: i,
          role: node.role || "enter",
          after: node.after,
          recipe: recs,
          start: startS,
          duration: durationS,
        });
        endS = Math.max(endS, startS + durationS);
      }
      return endS;
    }
    if (kind === "share") {
      var recShare = node.recipe || {};
      return t0 + recipeDuration(recShare, reduced) + (recShare.delay || 0);
    }
    if (kind === "group") {
      return collectPhase(
        { kind: "phase", mode: node.mode || "wait", children: node.tracks || [] },
        t0,
        items,
        reduced
      );
    }
    if (kind === "phase") return collectPhase(node, t0, items, reduced);
    if (kind === "bind" || kind === "score" || kind === "cue") {
      return collectTape(node.child, t0, items, reduced);
    }
    return t0;
  }

  function collectPhase(phase, t0, items, reduced) {
    var kids = phase.children || [];
    var mode = phase.mode || "parallel";
    var staggerMs = phase.stagger_ms || 0;
    if (!kids.length) return t0;
    if (mode === "sequence") {
      var t = t0;
      kids.forEach(function (child, i) {
        var start = t;
        if (i && staggerMs) start = t + staggerMs;
        t = collectTape(child, start, items, reduced);
      });
      return t;
    }
    if (mode === "wait") {
      var bags = partitionWait(kids);
      var exitEnd = t0;
      bags.exits.forEach(function (child) {
        exitEnd = Math.max(exitEnd, collectTape(child, t0, items, reduced));
      });
      var stayEnd = exitEnd;
      bags.stays.forEach(function (child) {
        stayEnd = Math.max(stayEnd, collectTape(child, exitEnd, items, reduced));
      });
      var nestedEnd = t0;
      bags.nested.forEach(function (child) {
        nestedEnd = Math.max(nestedEnd, collectTape(child, t0, items, reduced));
      });
      var enterT = bags.exits.length || bags.stays.length ? stayEnd : t0;
      var enterEnd = enterT;
      bags.enters.forEach(function (child) {
        enterEnd = Math.max(enterEnd, collectTape(child, enterT, items, reduced));
      });
      return Math.max(stayEnd, nestedEnd, enterEnd);
    }
    var endP = t0;
    kids.forEach(function (child, i) {
      endP = Math.max(endP, collectTape(child, t0 + i * staggerMs, items, reduced));
    });
    return endP;
  }

  function armEl(el, recipe, key, reducedPolicy) {
    if (!el) return null;
    var duration = recipeDuration(recipe, reducedPolicy);
    if (recipe && recipe.path && recipe.path.d) {
      try {
        el.style.offsetPath = 'path("' + recipe.path.d + '")';
        el.style.offsetRotate = recipe.path.rotate || "auto";
      } catch (e) {}
    }
    if (!el.animate) {
      return { el: el, anim: null, duration: duration, key: key };
    }
    cancelTarget(key);
    try {
      var anim = el.animate([kf(recipe && recipe.from, recipe, "from"), kf(recipe && recipe.to, recipe, "to")], {
        duration: duration || 1,
        delay: 0,
        easing: recipe && recipe.spring ? "cubic-bezier(0.22, 1, 0.36, 1)" : (recipe && recipe.easing) || "ease-out",
        fill: (recipe && recipe.fill) || "both",
      });
      anim.pause();
      running.set(key, anim);
      return { el: el, anim: anim, duration: duration, key: key };
    } catch (e) {
      return { el: el, anim: null, duration: duration, key: key };
    }
  }

  function armTape(items, reduced) {
    var armed = [];
    items.forEach(function (item) {
      var el;
      var key;
      if (item.kind === "stagger") {
        var els = qa(item.selector);
        el = els[item.index];
        key = item.selector + "#" + item.index;
      } else {
        el = q(item.target);
        key = item.target;
        if (item.role === "enter" && item.html) {
          if (el) cancelTarget(item.target);
          if (el) el = injectHtml(el, item.html);
        }
      }
      if (!el) return;
      if (item.role === "enter") {
        el.hidden = false;
        el.removeAttribute("hidden");
        el.removeAttribute("aria-hidden");
      }
      mark(el, item.role, item.role !== "exit");
      var armedItem = armEl(el, item.recipe, key, reduced);
      if (!armedItem) return;
      armedItem.start = item.start;
      armedItem.role = item.role;
      armedItem.after = item.after || (item.role === "exit" ? "remove" : "keep");
      armed.push(armedItem);
    });
    return armed;
  }

  function applyTape(tape, progress) {
    var p = clamp01(progress);
    var span = tape.span || 0;
    var t = span ? p * span : 0;
    if (tape.host && tape.host.setAttribute) {
      tape.host.setAttribute("data-uxm-progress", p.toFixed(3));
    }
    (tape.items || []).forEach(function (item) {
      if (item.anim) {
        var local = t - (item.start || 0);
        if (local < 0) local = 0;
        var cap = item.duration || 0;
        if (local > cap) local = cap;
        try {
          item.anim.currentTime = local;
        } catch (e) {}
      }
      if (item.role === "exit" && p >= 1 && item.el) {
        applyAfter(item.el, item.after || "keep");
      }
    });
    tape.progress = p;
  }

  function releaseTape(planId) {
    var tape = tapes.get(planId);
    if (!tape) return;
    if (tape.onScroll) {
      try {
        global.removeEventListener("scroll", tape.onScroll);
      } catch (e) {}
      if (tape.host && tape.host.removeEventListener) {
        try {
          tape.host.removeEventListener("scroll", tape.onScroll);
        } catch (e) {}
      }
    }
    (tape.items || []).forEach(function (item) {
      if (item.key) cancelTarget(item.key);
    });
    tapes.delete(planId);
  }

  function attachScrollLoop(tape) {
    var ticking = false;
    var raf = global.requestAnimationFrame || function (fn) {
      return setTimeout(fn, 16);
    };
    function measure() {
      ticking = false;
      if (!tapes.has(tape.planId)) return;
      applyTape(tape, measureScrollProgress(tape.host, tape.axis));
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      raf(measure);
    }
    tape.onScroll = onScroll;
    global.addEventListener("scroll", onScroll, { passive: true });
    if (tape.host && tape.host !== document.documentElement && tape.host.addEventListener) {
      tape.host.addEventListener("scroll", onScroll, { passive: true });
    }
    measure();
  }

  function scrub(planId, progress) {
    var tape = tapes.get(planId);
    if (!tape) return;
    applyTape(tape, progress);
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
      var anim = el.animate([kf(recipe.from, recipe, "from"), kf(recipe.to, recipe, "to")], {
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
          commitMorphD(el, recipe);
        },
        function () {
          running.delete(key);
        }
      );
    } catch (e) {
      commitMorphD(el, recipe);
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

  function playNode(node, reduced, ctx) {
    if (!node) return Promise.resolve();
    if (node.kind === "track" || node.kind === "stagger" || node.kind === "share") {
      return playTrack(node, reduced);
    }
    if (node.kind === "group") {
      return playPhase(
        { kind: "phase", mode: node.mode || "wait", children: node.tracks || [] },
        reduced,
        ctx
      );
    }
    if (node.kind === "phase") return playPhase(node, reduced, ctx);
    if (node.kind === "bind") return playBind(node, reduced, ctx);
    if (node.kind === "score") return playScore(node, reduced, ctx);
    if (node.kind === "cue") return playCue(node, reduced, ctx);
    return Promise.resolve();
  }

  function playPhase(phase, reduced, ctx) {
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
              return playNode(child, reduced, ctx);
            });
          }
          return playNode(child, reduced, ctx);
        });
      }, Promise.resolve());
    }
    if (mode === "wait") {
      var waitBags = partitionWait(kids);
      return Promise.all([
        Promise.all(waitBags.exits.map(function (n) {
          return playTrack(n, reduced);
        }))
          .then(function () {
            return Promise.all(waitBags.stays.map(function (n) {
              return playTrack(n, reduced);
            }));
          })
          .then(function () {
            return Promise.all(waitBags.enters.map(function (n) {
              return playTrack(n, reduced);
            }));
          }),
        Promise.all(waitBags.nested.map(function (n) {
          return playNode(n, reduced, ctx);
        })),
      ]);
    }
    return Promise.all(
      kids.map(function (c, i) {
        if (!staggerMs) return playNode(c, reduced, ctx);
        return new Promise(function (res) {
          setTimeout(res, i * staggerMs);
        }).then(function () {
          return playNode(c, reduced, ctx);
        });
      })
    );
  }

  function playBind(node, reduced, ctx) {
    // Soft 1: scroll/progress arm a live 0..1 tape. drag leftover = one-shot child.
    // Hosts seek with UxMotion.scrub(planId, progress). No gesture listeners.
    var child = node.child;
    if (!child) return Promise.resolve();
    var host = q(node.target) || document.documentElement;
    var planId = (ctx && ctx.planId) || ("bind:" + node.target);
    if (host.setAttribute) {
      host.setAttribute("data-uxm-bind", node.input || "scroll");
    }
    if (node.input === "scroll" || node.input === "progress") {
      releaseTape(planId);
      var items = [];
      var span = collectTape(child, 0, items, reduced);
      var tape = {
        planId: planId,
        host: host,
        input: node.input,
        axis: node.axis || "y",
        span: span,
        items: armTape(items, reduced),
      };
      tapes.set(planId, tape);
      if (node.input === "scroll") attachScrollLoop(tape);
      else applyTape(tape, 0);
      return Promise.resolve();
    }
    return playNode(child, reduced, ctx);
  }

  function playScore(node, reduced, ctx) {
    var child = node.child;
    if (!child) return Promise.resolve();
    if (node.phase === "hold") {
      return playNode(child, reduced, ctx).then(function () {
        // Keep exiting nodes in the map until cue
        scores.set(node.id, { held: true, at: Date.now() });
        document.dispatchEvent(
          new CustomEvent("ux-motion:score-hold", { detail: { id: node.id } })
        );
      });
    }
    return playNode(child, reduced, ctx);
  }

  function playCue(node, reduced, ctx) {
    var held = scores.get(node.score);
    if (held) {
      scores.delete(node.score);
      document.dispatchEvent(
        new CustomEvent("ux-motion:score-resolve", { detail: { id: node.score } })
      );
    }
    if (node.child) return playNode(node.child, reduced, ctx);
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
    var ctx = { planId: plan.id };
    if (reduced === "swap" && plan.reduce_tree && prefersReduced()) {
      return playNode(plan.reduce_tree, "skip", ctx);
    }
    var body = function () {
      return playNode(plan.root, reduced, ctx);
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
      releaseTape(plan.id);
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
    scrub: scrub,
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
