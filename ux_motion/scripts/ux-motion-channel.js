/* ux-motion-channel — play transition.* after Channel authority morph.

   Channel applyOp does not understand transition.*.
   Motion must not race Channel idiomorph on the same Result.
   This is a Channel client hook, not Glue, not a Bridge, not an Adapter.
*/
(function (global) {
  function isMotion(op) {
    return op && String(op.op || "").indexOf("transition.") === 0;
  }

  document.addEventListener("channel:beforeApply", function (e) {
    var box = e.detail;
    var result = box && box.result;
    if (!result || !Array.isArray(result.ops)) return;
    var motion = [];
    var rest = [];
    result.ops.forEach(function (op) {
      if (isMotion(op)) motion.push(op);
      else rest.push(op);
    });
    result.ops = rest;
    result._uxMotion = motion;
  });

  document.addEventListener("channel:afterApply", function (e) {
    var result = e.detail;
    var motion = result && result._uxMotion;
    if (
      motion &&
      motion.length &&
      global.UxMotion &&
      typeof global.UxMotion.applyOps === "function"
    ) {
      global.UxMotion.applyOps(motion);
    }
  });
})(typeof window !== "undefined" ? window : this);
