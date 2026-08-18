"""Single source of truth for package versions.

Bump rules (see docs/13-VERSIONING.md):
- API_VERSION / __version__: semver for the Python facade + JS player.
- IR_VERSION: wire plan major only. Additive fields stay on the same major.
"""

from __future__ import annotations

# Public library release (Python package + docs + player alignment).
__version__ = "1.3.0"

# Same as __version__. Kept as API_VERSION for facade clarity.
API_VERSION = __version__

# Plan IR major. Only change when the wire shape breaks receivers.
IR_VERSION = "1"

# Browser player string; must equal API_VERSION for a release.
PLAYER_VERSION = __version__
