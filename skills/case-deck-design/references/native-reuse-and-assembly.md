# Native reuse and assembly

## Scope and prerequisites

Use the environment's current presentation tooling for authoring text, tables, charts, assets and new layouts. These Python helpers operate on existing PPTX packages; they do not replace the host authoring API, renderer, finalizer or required save workflow. Use the runtime Python with `lxml`, and `PyMuPDF` plus `Pillow` for PDF review helpers. They do not require `python-pptx`.

Resolve this skill's actual directory at use time; do not assume it retains the human-readable folder name after installation. Run scripts by absolute path. Run work in the task's private build directory, never in the installed skill. Inspect tool help before use. Keep all original attachments unchanged.

## Inventory and visual selection

```
python /path/to/skill/scripts/inspect_pptx.py bank.pptx --output bank-inventory.json
python /path/to/skill/scripts/contact_sheet.py bank.pdf --outdir bank-contact-sheets
```

The inventory reports actual slide order, object IDs, local bounds, explicit styles, group membership and relationships. It does not resolve all inherited formatting or judge appearance. Render through the host's presentation workflow and inspect candidate slides/crops. The contact-sheet script assembles existing rendered pages solely for QA; it does not draw slide illustrations.

For visual donor proposals, identify source file/hash, slide number and object IDs. Confirm the selected object is native rather than a flattened image. For grouped selections, keep a coherent coordinate system and preserve visual z-order.

## Transplant native shape shells and frameworks

Author placeholders with unique stable shape names using the host tool. Use a text-bearing placeholder for `shell` mode or a blank placeholder for `group` mode. Do not rely on generated shape IDs remaining stable across exports. Use inspected names plus exact donor IDs and hash.

```
python /path/to/skill/scripts/transplant_elements.py \
  --authored authored.pptx --donor bank.pptx \
  --map donor-map.json --output authored-with-elements.pptx
```

Example map schema; replace illustrative values with inspected IDs and hashes:

```json
{
  "donor_sha256": "exact SHA256 from the inspected source",
  "records": [
    {
      "target_slide": 1,
      "target_name": "reuse.solution.description",
      "donor_slide": 42,
      "donor_ids": [3018],
      "mode": "shell",
      "use_target_fill": true,
      "use_target_line": true,
      "palette": {"lt2": "EEEEEE", "BFBFBF": "B8C8D5"}
    },
    {
      "target_slide": 2,
      "target_name": "reuse.issue.branch.left",
      "donor_slide": 77,
      "donor_ids": [3201, 3202, 3203],
      "mode": "group",
      "palette": {"accent1": "123456"}
    }
  ]
}
```

Palette values above demonstrate syntax, not this skill's design defaults. Derive the real palette from the current target deck. `shell` retains donor native geometry/effects while taking authored text, identity, frame and, by default, fill and line. `group` clears donor text and wraps selected native geometry into the blank target frame. Author the replacement text separately at the target font sizes. Optional `source_box_px` has x/y/w/h in 96-DPI CSS pixels and controls the grouping viewport; use it only after confirming bounds.

The helper retains donor z-order, remaps copied object IDs and internal connector attachments, strips old hyperlinks and clears donor text. It rejects missing IDs, duplicate targets, mixed coordinate parents for groups, selecting a group plus its child, dependency-bearing objects, and overwriting either input. It creates a reuse report with hashes and actual donor IDs.

**Bounded capability:** only relationship-free native shapes/connectors/groups are supported by this helper. Charts, pictures, tables and embedded objects require a supported native transfer or current-data reconstruction. An error here is not evidence that all element reuse is impossible. Use a different donor unit, transfer supported parts, and handle data-bearing objects with host tools. Do not remove required relationships or rasterize editable evidence to bypass the limitation.

For a native chart, preserve the chart part, style/color dependencies and original embedded workbook where supplied, then update current-case series/labels/data through supported APIs. Preserve formulas and lineage; a literal snapshot is not an equivalent replacement. If rebuilding the visual with a new native chart is appropriate, disclose it as reconstruction and use current source data.

For a table, preserve editable cells, widths, row heights, styles and borders while replacing content. Do not copy an old table's data accidentally. For a picture, preserve native aspect ratio and apply a meaningful crop without discarding required pixels. For dependencies inheriting from donor themes, resolve/restyle deliberately; copying XML alone can change appearance under a different theme.

## Assemble retained and authored slides

Use selective assembly for strong preservation. Keep the approved base package. Export only authored slides, with transferred donor elements applied, then choose the final order. The assembler preserves base slide bodies and notes rather than importing/re-exporting them through the authoring engine.

```
python /path/to/skill/scripts/assemble_deck.py \
  --base approved.pptx --authored authored-with-elements.pptx \
  --manifest assembly.json --output candidate.pptx
```

Example manifest:

```json
{
  "order": [
    {"id": "summary", "source": "authored", "slide": 1},
    {"id": "analysis", "source": "base", "slide": 2},
    {"id": "index", "source": "authored", "slide": 2},
    {"id": "survey", "source": "base", "slide": 31}
  ],
  "redirects": {"base:1": "summary", "base:28": "index"},
  "owner_redirects": {"base:31": {"base:28": "index"}},
  "links": [
    {"owner": "index", "shape_name": "index.code.B1", "target": "survey", "mode": "both"}
  ]
}
```

`order` gives unique logical IDs and unique source selections. `redirects` changes relationships pointing to a source slide. `owner_redirects` overrides specific targets for one source slide, useful when exhibit return links now belong to different index-category pages. `links` adds links to uniquely named **authored** shapes; modes are shape, text or both. Native text hyperlinks often survive PDF export where shape-level clicks do not. Keep visual styling intentional and inspect the result.

Optional `base_sha256` and `authored_sha256` enforce inspected inputs. An assembler-generated report supplies final logical positions and a `preserved` list of before/after slide mappings. Retained slide bodies and notes must remain byte-identical. Explicitly authorized body edits must be made separately before assembly, with their own scope comparison.

The assembler imports authored dependencies under unique names, registers masters/fonts, repairs content types and relationships, prunes unreachable parts, and canonicalizes active slide filenames to visible order. It retargets references after that mapping. It refuses unresolved links to omitted slides; supply an explicit redirect rather than silently dropping navigation.

Limits: both decks must use identical declared canvas dimensions; selections cannot repeat a source slide; base custom shows and sections require a task-specific metadata-preserving workflow. The helper does not infer source codes from text, update workbook data, fix legacy package defects, anonymize sources, or claim native application compatibility. It does not copy the entire donor bank into the deliverable.

## Audits and rendered comparison

```
python /path/to/skill/scripts/audit_deck.py candidate.pptx \
  --base approved.pptx --mapping candidate.assembly.json \
  --expected-links expected-links.json --output package-audit.json
python /path/to/skill/scripts/compare_renders.py \
  --before approved.pdf --after candidate.pdf \
  --mapping candidate.assembly.json --output render-comparison.json
```

An expected-links file is a list of `{slide, shape_name, target_slide}` for internal links or `{slide, shape_name, url}` for external links. Map files accept a list of `{before, after}`, or an object containing `preserved` or `mapping`. Use final physical slide numbers after assembly. The audit checks body/notes identity, relationship destinations, object-ID uniqueness and named link contracts. It reports native chart/table counts but does not establish semantic editability or correctness.

Render both versions using the same office renderer and font environment. The render comparator rasterizes the existing PDFs at the same width and reports exact pixel differences. Review every changed slide visually as well. Do not weaken checks merely because a mismatched template or missing font produces differences. Complete the host finalization gates and render the exact final artifact before delivery.
