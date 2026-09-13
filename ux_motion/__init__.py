"""ux_motion — server-authored, composable presence + transition plans.

    from ux_motion import scene, fade, send, share, tokens, patterns

    # Classic presence
    result = scene("nav").exit("#old", fade.exit()).enter("#new", fade.enter()).play()

    # Shared element (FLIP)
    scene("pdp").share("hero", leave="#grid-img", arrive="#pdp-img").play()

    # Scroll-scrubbed tape
    scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter()).play()

    # SVG path d morph (similar paths; not offset-path / along)
    scene("icon").enter("#blob", morph_d("M0,0 L20,0 Z", "M0,20 L20,0 Z")).play()

    # Multi-hop across HTTP Results
    scene("leave").as_score("checkout", phase="hold").exit("#cart", fade.exit()).play()

    # Drop-in HOF — tree stays a tree until the wire
    appear(section(h1("Shop"), id="view"), stagger=".tile").play()
    rise(product_view())

IR major is ``v: "1"``. Additive fields only. Never reuse keys.
"""

from ux_motion._adapter import send
from ux_motion._markup import as_html
from ux_motion._render import render_markup
from ux_motion._freeze import freeze_plan
from ux_motion._hof import (
    HOFS,
    appear,
    css_target,
    hop,
    hop_arrive,
    hop_leave,
    leave,
    motion,
    notice,
    sheet,
    staggered,
    swap,
)
from ux_motion._channel import MotionChannel
from ux_motion._api import (
    Motion,
    Scene,
    bind,
    cue,
    group,
    parallel,
    scene,
    score,
    sequence,
    share,
    stagger,
    track,
    wait,
)
from ux_motion._compile import compile_plan
from ux_motion._contract import CONTRACT
from ux_motion._ir import PlanError, validate_plan
from ux_motion._version import API_VERSION, IR_VERSION, PLAYER_VERSION, __version__
from ux_motion._ops import OP_CANCEL, OP_PLAY, OP_REWIND, as_update, cancel, play, rewind, rewind_plan, to_result
from ux_motion._patterns import PATTERNS, list_stagger, modal, multi_hop_arrive, multi_hop_leave, page, shared_page, toast
from ux_motion._player import (
    Event,
    ScrubFrame,
    WAIT_BAGS,
    WAIT_CLOCKS,
    WaitBags,
    WaitClock,
    explain,
    frames,
    interpret,
    partition_wait,
    scrub,
    span_ms,
    wait_clocks,
)
from ux_motion._presence import Presence, region, stamp
from ux_motion._recipes import Recipe, along, blur, fade, morph_d, none, rise, scale, slide, snap, springy
from ux_motion._schema import schema
from ux_motion._tokens import Tokens, tokens
from ux_motion._wire import dumps, loads



__all__ = [
    "API_VERSION",
    "PLAYER_VERSION",
    "__version__",
    "CONTRACT",
    "IR_VERSION",
    "OP_CANCEL",
    "OP_PLAY",
    "OP_REWIND",
    "Event",
    "HOFS",
    "Motion",
    "MotionChannel",
    "PATTERNS",
    "PlanError",
    "Presence",
    "Recipe",
    "ScrubFrame",
    "Scene",
    "Tokens",
    "WAIT_BAGS",
    "WAIT_CLOCKS",
    "WaitBags",
    "WaitClock",
    "along",
    "appear",
    "as_html",
    "as_update",
    "bind",
    "blur",
    "cancel",
    "compile_plan",
    "css_target",
    "cue",
    "dumps",
    "explain",
    "fade",
    "freeze_plan",
    "frames",
    "group",
    "hop",
    "hop_arrive",
    "hop_leave",
    "interpret",
    "leave",
    "list_stagger",
    "loads",
    "modal",
    "morph_d",
    "motion",
    "multi_hop_arrive",
    "multi_hop_leave",
    "none",
    "notice",
    "page",
    "parallel",
    "partition_wait",
    "play",
    "region",
    "render_markup",
    "rewind",
    "rewind_plan",
    "rise",
    "scale",
    "scene",
    "schema",
    "score",
    "scrub",
    "send",
    "sequence",
    "share",
    "shared_page",
    "sheet",
    "slide",
    "snap",
    "span_ms",
    "springy",
    "stagger",
    "staggered",
    "stamp",
    "swap",
    "to_result",
    "toast",
    "tokens",
    "track",
    "validate_plan",
    "wait",
    "wait_clocks",
]

Motion.appear = staticmethod(appear)
Motion.leave = staticmethod(leave)
Motion.swap = staticmethod(swap)
Motion.sheet = staticmethod(sheet)
Motion.notice = staticmethod(notice)
Motion.staggered = staticmethod(staggered)
Motion.hop = hop
Motion.motion = staticmethod(motion)
