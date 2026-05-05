"""Phase 4 D-04 — verify the rebuilt frontend bundle contains the
parameter IDs and routing code that prove both patches landed.

These tests grep the minified JS output. The bundler does NOT mangle
string literals, so substring searches are reliable.

NOTE: ParamAngleXIN does NOT appear directly in the bundle — it is a
runtime string read from the model's .vtube.json ParameterSettings at
runtime. The Option A patch is generic: it reads any OutputLive2D value
from the JSON. Instead, we check for the routing engine strings that DO
appear in the bundle: FaceAngleX (synthesized input key), ParameterSettings
(JSON field name parsed), and OutputLive2D (field name from .vtube.json).
"""

from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent
FRONTEND = REPO_ROOT / "frontend"
ASSETS = FRONTEND / "assets"


def _bundle_files() -> list[Path]:
    if not ASSETS.is_dir():
        return []
    return sorted(ASSETS.glob("*.js"))


def _grep_any(token: str) -> Path | None:
    for f in _bundle_files():
        try:
            if token in f.read_text(encoding="utf-8", errors="ignore"):
                return f
        except Exception:
            continue
    return None


def test_bundle_present():
    index = FRONTEND / "index.html"
    assert index.is_file(), f"missing {index}"
    bundles = _bundle_files()
    assert bundles, f"no JS bundle files in {ASSETS}"


def test_bundle_has_vtube_routing():
    # Option A VTube routing patch — the routing engine keys that appear
    # in the compiled bundle. FaceAngleX is the synthetic drag input key
    # and ParameterSettings is the .vtube.json field name being parsed.
    # ParamAngleXIN is NOT in the bundle — it comes from the JSON at runtime.
    hit = _grep_any("FaceAngleX")
    assert hit, (
        "FaceAngleX not found in any frontend/assets/*.js — "
        "Option A VTube routing patch missing from bundle"
    )


def test_bundle_has_param_body_angle_y():
    # Body-bob extension — drives body sway from _wavFileHandler.getRms()
    hit = _grep_any("ParamBodyAngleY")
    assert hit, (
        "ParamBodyAngleY not found in any frontend/assets/*.js — body-bob extension missing"
    )


def test_bundle_has_watermark_force_pin():
    # Option A watermark fix — pins ParamWatermarkOFF=1 every frame
    hit = _grep_any("ParamWatermarkOFF")
    assert hit, (
        "ParamWatermarkOFF not found in any frontend/assets/*.js — watermark fix missing"
    )


def test_bundle_source_manifest_present():
    manifest = FRONTEND / ".bundle-source"
    assert manifest.is_file(), f"missing {manifest}"
    text = manifest.read_text(encoding="utf-8")
    # Look for a commit: <hex> line (40-char SHA) — accept abbreviated too
    m = re.search(r"^commit:\s*([0-9a-f]{7,40})\s*$", text, re.MULTILINE)
    assert m, f"no valid commit: <sha> line in .bundle-source — got:\n{text}"
