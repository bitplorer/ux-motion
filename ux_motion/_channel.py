"""MotionChannel — Document contribution for Channel Result compositing.

Channel ``applyOp`` does not understand ``transition.*``.
Motion must not race Channel idiomorph on the same Result.

This plugin injects ``ux-motion-channel.js``, which:

* ``channel:beforeApply`` — peel ``transition.*`` off ``result.ops``
* ``channel:afterApply``  — ``UxMotion.applyOps`` on the stashed list

It does not import ``ux_channel``. Event names are public Channel API.
Use only when Channel is on the page: ``document.use(Motion(), MotionChannel())``.
"""

from __future__ import annotations


class MotionChannel:
    """Contribution. ``name`` carries the owner: motion, channel compositor."""

    plugin_kind = "contribution"
    name = "ux_motion.channel"
    SCRIPT_URL = "/ux-pkg/ux-motion/static/ux-motion-channel.js"

    def __init__(self, *, src: str | None = None, serve: str = "package_mount") -> None:
        self.serve = serve
        self.src = src or (
            self.SCRIPT_URL if serve == "package_mount" else "/static/ux-motion-channel.js"
        )

    def document_head(self):
        try:
            from ux_dom.dom import script
        except ImportError:
            return ()
        return (script(src=self.src, defer=True),)

    def document_body(self):
        return ()

    def served_files(self):
        if self.serve != "package_mount":
            return ()
        try:
            from ux_dom.plugins.safe_static import SafeStaticFile
        except ImportError:
            return ()
        return (
            SafeStaticFile.from_package(
                "ux_motion.scripts",
                "ux-motion-channel.js",
                url=self.SCRIPT_URL,
                plugin=self.name,
                content_type="application/javascript",
            ),
        )

    def artifacts(self):
        return ()
