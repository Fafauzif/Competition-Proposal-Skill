# Visual QA and preservation

## Verification must match the risk

This user's priority is a polished editable deck that follows the current design without disturbing approved work. Automated tests and renders answer different questions. Use structural checks for editability, relationships and preservation, and actual visual inspection for composition and readability. Do not claim one proves the other.

For a new/broadly redesigned deck, render every final slide and inspect each authored slide individually at full size. Use contact sheets for whole-deck rhythm, not as the only QA. For a narrow change, inspect changed slides individually and compare all retained slides by the correct old-to-new mapping. Recheck exact final bytes if finalization changed the candidate.

## Visual checks

| Area | Check |
| --- | --- |
| Typography | Correct family, size, weight and emphasis; no hidden shrink-to-fit; inherited fonts resolve correctly |
| Hierarchy | Main point is clear; explanation supports the visual; no repeated empty labels |
| Wrapping | No clipped words, awkward tiny last lines, three-line subheads caused by avoidable verbosity, or URL collisions |
| Geometry | Alignment, intentional margins, baseline consistency, sufficient gaps and no accidental overlap |
| Frameworks | Correct branch count, connector attachments, arrow direction and no false mapping |
| Charts | Labels/units/series readable; values match source/model; no misleading axes or decorative substitutions |
| Screens | Important content visible at presentation scale; suitable frame and proportions; callouts point to exact features |
| Sources | Correct size, concise wording, necessary caveats and working destinations |
| Deck flow | Varied but related layouts; no repetitive box grid; title-only story remains coherent |

Repair the cause of overflow: simplify copy, allocate more space, change arrangement or distribute within the permitted count. Never fix it by silently shrinking the source font hierarchy. A slide can feel crowded without actual overlap; judge explanation volume and visual hierarchy, not just bounding boxes.

## Preserve approved material

Record input hashes and the last approved base. Keep untouched slide XML and notes as bytes where possible. Preserve related layouts, masters, themes, fonts, media, chart parts and embedded workbooks. Re-exporting an entire original deck can subtly alter these even when only a few slides changed; selective assembly is preferable for strict preservation.

Use an explicit old-slide → new-slide mapping. Compare bodies and notes byte-for-byte for strict locks. When a narrow exception is authorized, compare structural equality after excluding only the exact named objects/properties allowed to change; never exclude all text or all relationships just to obtain a pass. Retargeting a hyperlink is distinct from altering visible slide content.

Also compare rendered mapped slides under the same renderer, font environment, resolution and settings. Identical slide XML is not enough if a shared theme or font changed. Pixel differences need investigation; they can be renderer/environment changes or real modifications. Do not relax the threshold until the cause is understood. Do not label an approximate visual match as exact preservation.

Existing off-canvas decorative objects or template overlaps may generate warnings. Evaluate them against the original. Preserve intentional or pre-existing content outside the authorized scope. Do not modify approved slides merely to satisfy a generic validator's style preference.

## Evidence and financial checks

Verify every newly written quantitative claim against the ledger: numerator, denominator, unit, timeframe, source and caveat. Check headline statements against chart/table scope. Verify expected-impact calculations from the specified assumptions. Reconcile executive summary and finance. Keep chart caches and workbook values consistent, and preserve formulas/lineage where supplied.

Do not recompute or redesign an unchanged financial model during a bibliography-only revision. Hash/compare its retained parts instead. Broaden testing only to resolve a concrete risk or required gate.

## Package and navigation checks

Run the host presentation finalizer. Also check, as relevant:

- Final slide count and order match the request.
- All selected native elements are present and editable; no flattening of required text/charts/tables.
- Every relationship target exists; external URLs and internal destinations are distinct.
- Internal links target logical exhibits after physical numbering changes.
- Each appendix code/title links to its exhibit and each return link reaches the right category page.
- Bibliography contains all required references and correct URL targets.
- No old donor text, donor notes, logos or data leaked into the new case.
- Any required anonymity holds across requested content and hidden dependencies.

The bundled `audit_deck.py` checks package structure and declared preservation/navigation contracts. It cannot judge factual truth or text fit. `compare_renders.py` compares mapped PDF pages at a fixed size; it cannot establish native application editability.

## Honest handoff

Render and inspect the exact finalized artifact or prove it is byte-identical to the rendered candidate. Report PowerPoint/Google Slides testing only if actually performed there. If only package and render checks were performed, state that boundary when it materially affects use. Do not promise identical import rendering across applications.

Save through the current environment's required artifact mechanism. Return the deliverable concisely, identify any unresolved material limitation, and stop. Keep working code, QA logs and temporary previews private unless requested. Do not add an unrequested scorecard or claim guaranteed competition results.
