# Rendering and compact layouts

The [gallery catalog](../assets/charts/catalog.json) lists the original editable JSON inputs, generated TeX, and archival previews. Its paths are relative to this skill directory. The original renderer and gallery come from [Essay Studio](https://github.com/Fafauzif/Essay-Studio/tree/8fddfff968f492a1f13dc0bb7f97ca78bd09980a). The supplied examples are synthetic. Replace them with the current proposal's facts and clearly identified assumptions.

From this skill directory:

```sh
python scripts/render.py --list
python scripts/render.py assets/charts/compact/compact-gantt.json --profile main --out-dir build/charts
python scripts/render.py assets/charts/examples/gantt_year1.json --profile appendix --out-dir build/charts
python scripts/render.py --all assets/charts/examples --font "Liberation Serif" --out-dir build/gallery
python scripts/charts.py --self-test
```

The original examples request Times New Roman, which may be absent. Supply an installed alternative when the guidebook permits. Add `--font-required` with the required font if substitution would violate the brief. A font present in a built asset may still print at a different size after inserting it into a narrower column. Inspect the placed figure.

| Backend | What it needs | What it produces |
|---|---|---|
| `auto` (default) | Working XeLaTeX or LuaLaTeX, with fontspec, standalone, TikZ/PGFPlots, an installed font, and a rasterizer. Otherwise uses Matplotlib when available. | Checked PNG and PDF, regenerable TeX, JSON metadata, and SVG when Matplotlib rendered. |
| `tex` | Working TeX toolchain. PyMuPDF or `pdftoppm` for PNG. | PDF and TeX, plus PNG if a rasterizer is present. |
| `matplotlib` | Matplotlib in the active Python environment. See [requirements](../requirements.txt). | Editable SVG text/objects, PDF, PNG, and TeX for later regeneration. |
| `tex-source` | Python. | TeX and metadata. No figure is rendered in this mode. |

The wrapper validates the JSON with the original chart contract before it chooses an engine. If the automatic path uses a fallback, inspect the recorded backend and any fallback reason. Use the paths in the current metadata. An output marked unrefreshed may be from an earlier engine run. Reports with substituted mandatory fonts need a corrected export. If a rendered alternative is not available, keep the source and report the exact missing export.

The `main` profile preserves data and starts with a shallower default for supported quantitative charts. Measure the actual live width of the page or column and pass `--width-cm` when it differs from the specification. `height_cm` can refine the default when the plot supports it. For dense figures, select fewer decision-critical series or categories based on the argument and link to complete detail. Preserve the original data and include a scope note when showing a subset. `appendix` follows the dimensions in the specification and leaves the full gallery defaults available.

### Compact worked layouts

- [Wide four-phase Gantt input](../assets/charts/compact/compact-gantt.json) and [preview](../assets/charts/compact/compact-gantt.png). Use brief row labels and an explicit time unit. Put extra notes, assigned roles, and exact acceptance checks in the text or a linked exhibit. The start and end indices are inclusive and 1-based.
- [Paired sections editable SVG](../assets/charts/compact/paired-sections.svg) and [preview](../assets/charts/compact/paired-sections.png). Use aligned panel titles and a common plotting scale where positions encode quantities. The sample is a schematic with common geometry. Edit or redraw in a vector editor and verify both panels have enough space. Place nearby short exhibits in the same reading flow; a tall independent figure can use the full appendix width or height when it makes the evidence clearer.

### Review after export

1. Inspect figures on the final page at normal reading size. Check label sizes, text wrapping, legends, values, color contrast, axis baselines and panel comparisons.
2. Compare data payloads, category ordering, time-unit definitions, uncertainty intervals, and sources to the approved inputs. In grouped comparisons, check all marks and labels. Test empty/constant/negative ranges when relevant.
3. Reopen the actual final PDF, with bibliography and exhibit links if present. Preserve machine-readable values and editable source alongside the production graphic as appropriate to the requested output.
