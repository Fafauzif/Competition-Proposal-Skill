#!/usr/bin/env python3
"""Render Essay Studio JSON figures with TeX or an automatic Matplotlib fallback."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import charts


def profile_spec(original, profile, font, width):
    spec = dict(original)
    if font:
        spec["font"] = font
    if width:
        spec["width_cm"] = width
    if profile == "main":
        spec.setdefault("width_cm", 16)
        kind = spec["type"]
        if kind in {"cash_line", "distribution"}:
            spec.setdefault("height_cm", 4.8)
        if kind == "bar_comparison":
            spec.setdefault("height_cm", max(3.2, 1.2 + .65 * len(spec["categories"])))
        if kind == "drivers":
            spec.setdefault("height_cm", max(3.3, 1 + .62 * len(spec["values"])))
    return spec


def render(path, output, backend="auto", profile="appendix", font=None, width=None, dpi=200,
           font_required=False):
    original_data = path.read_bytes()
    original = json.loads(original_data)
    if not isinstance(original, dict) or original.get("type") not in charts.RENDERERS:
        raise ValueError(f"{path.name}: expected a JSON object with a supported chart type")
    name = original.get("id", path.stem)
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", name):
        raise ValueError("id must be a simple filename stem")
    spec = profile_spec(original | {"id": name}, profile, font, width)
    if font_required and not spec.get("font"):
        raise ValueError("--font-required needs --font or a font in the specification")
    driver = charts.RENDERERS[spec["type"]]
    # Validate before trying either renderer. Fallback never masks bad input.
    intro = charts.header(spec)
    body, meta = driver(spec)
    tex = intro + body + "\n\\end{document}\n"
    output.mkdir(parents=True, exist_ok=True)
    message = None
    result = None
    if backend in {"auto", "tex"}:
        with tempfile.TemporaryDirectory(prefix="essay-chart-") as tmp:
            effective_spec = Path(tmp) / (name + ".json")
            effective_spec.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            for engine in ("xelatex", "lualatex"):
                if not shutil.which(engine):
                    continue
                try:
                    result = charts.render(effective_spec, output, dpi=dpi, engine=engine)
                except (RuntimeError, subprocess.SubprocessError) as exc:
                    message = str(exc).splitlines()[0]
                    continue
                if "png" not in result and backend == "auto":
                    message = "TeX succeeded; no PNG rasterizer was available"
                    result = None
                    break
                result["backend"] = "tex"
                break
        if result is None:
            message = message or "No working XeLaTeX or LuaLaTeX executable"
            if backend == "tex":
                raise RuntimeError(message)
    elif backend == "tex-source":
        result = {"backend": "tex-source", "render_status": "source_only", "tex": str(output / f"{name}.tex")}
    if result is None:
        try:
            from fallback import render as fallback
        except ImportError as exc:
            raise RuntimeError(f"{message or 'Matplotlib selected'}. Matplotlib unavailable; install the optional requirements or render TeX source.") from exc
        result = fallback(spec, name, output, dpi, profile, meta, require_font=font_required)
        if message:
            result["fallback_reason"] = message
    # Keep regenerable TeX even when Matplotlib supplied the production render.
    charts.atomic_bytes(output / f"{name}.tex", tex.encode("utf-8"))
    result["tex"] = str(output / f"{name}.tex")
    # A preceding render with a different backend may have left an export absent
    # from the current result. Name it so consumers use the metadata's outputs.
    result["unrefreshed_outputs"] = [str(output / f"{name}.{ext}") for ext in ("pdf", "png", "svg")
                                     if ext not in result and (output / f"{name}.{ext}").exists()]
    result.update(id=name, type=spec["type"], profile=profile, width_cm=spec.get("width_cm", 16),
                  data_summary=meta, input_sha256=hashlib.sha256(original_data).hexdigest(),
                  example_status=spec.get("example_status"), source_note=spec.get("source_note"))
    charts.atomic_bytes(output / f"{name}.meta.json",
                        json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    content = parser.add_mutually_exclusive_group(required=True)
    content.add_argument("spec", nargs="?", type=Path)
    content.add_argument("--all", type=Path, metavar="DIRECTORY")
    content.add_argument("--list", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("build/charts"))
    parser.add_argument("--backend", choices=("auto", "tex", "matplotlib", "tex-source"), default="auto")
    parser.add_argument("--profile", choices=("main", "appendix"), default="appendix")
    parser.add_argument("--font", help="Override figure font family")
    parser.add_argument("--font-required", action="store_true", help="Reject substitution of a mandated font")
    parser.add_argument("--width-cm", type=float, help="Set the intended physical figure width")
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()
    if args.list:
        print("\n".join(charts.TYPES))
        return 0
    if not 72 <= args.dpi <= 600:
        parser.error("--dpi must be 72–600")
    paths = sorted(args.all.glob("*.json")) if args.all else [args.spec]
    if not paths:
        parser.error("The specified directory has no JSON files")
    try:
        names = [json.loads(path.read_bytes()).get("id", path.stem) for path in paths]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate chart IDs in batch would overwrite an output")
        data = [render(path, args.out_dir, args.backend, args.profile, args.font, args.width_cm,
                       args.dpi, args.font_required) for path in paths]
    except (AttributeError, ValueError, TypeError, KeyError, OSError, RuntimeError,
            subprocess.SubprocessError) as error:
        print(f"Chart error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
