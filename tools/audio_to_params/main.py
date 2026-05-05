"""Phase 4 D-07 sidecar CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loguru import logger

try:
    from .adapter import infer
except ImportError:
    # Support direct invocation: python tools/audio_to_params/main.py
    _pkg_dir = Path(__file__).parent.parent.parent
    if str(_pkg_dir) not in sys.path:
        sys.path.insert(0, str(_pkg_dir))
    from tools.audio_to_params.adapter import infer  # type: ignore[no-redef]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audio_to_params",
        description="Phase 4 sidecar: WAV + transcript -> Live2D parameter trajectory JSON",
    )
    p.add_argument("--audio", required=True, help="Path to input WAV file")
    p.add_argument("--transcript", required=True, help="Audio transcript (string)")
    p.add_argument(
        "--out",
        default=None,
        help="Output JSON path (default: <audio_basename>_traj.json)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audio_p = Path(args.audio)
    if not audio_p.is_file():
        logger.error(f"audio file not found: {audio_p}")
        return 2
    out_path = (
        Path(args.out) if args.out else audio_p.with_name(audio_p.stem + "_traj.json")
    )
    result = infer(str(audio_p), args.transcript)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info(
        f"Wrote {out_path} — {len(result['frames'])} frames, "
        f"engine={result['engine']}, duration={result['duration_seconds']}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
