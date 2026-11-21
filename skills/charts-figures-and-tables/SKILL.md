---
name: charts-figures-and-tables
description: Choose, build, and verify decision-relevant visuals for written proposals. Use for exact charts, Gantts, process flows, issue trees, risk exhibits, financial plots, editable tables, and appendix diagrams. Defaults to a wide, shallow layout in the main proposal and a size chosen for readability in the appendix.
---

# Charts, Figures, and Tables

Start with the question the exhibit answers and the sentence it supports. Use the reader's task to choose a chart, diagram, table, or short sentence. Give each exhibit a job, such as comparing options on the same basis, showing what an actor does next, or making a calculation inspectable.

1. **Prepare the inputs.** Record the source, values, category order, time period, unit, denominator, and actual/estimate/target status. Define axes and ranges before styling. Separate an illustrative operating scenario from observed results. Match labels and boundaries across prose, exhibits, and workbook.
2. **Choose the form.** Use horizontal comparisons for long labels, lines for ordered changes, Gantts for work and ownership over time, and branches or lanes for decisions and handoffs. Use native, restrained tables when the reader needs exact values or a reliable lookup. See the [selection guide](references/selection.md) for the 12 bundled families and other appropriate options.
3. **Fit the actual page.** In the main proposal prioritize horizontal length: use the available text width with a shallow chart when it can still be read. Shorten labels accurately, remove redundant chart text, or move dense support into an appendix. For appendices, let the comparison and readability determine dimensions. Portrait, landscape, square, or a readable pair can all fit. Reflow rather than set a hard aspect ratio.
4. **Render.** Use a project-required method when specified. Otherwise, use the bundled TeX-first script. It switches automatically to Matplotlib when a working TeX path is unavailable. If neither is available, use another capable local renderer and preserve the data and as much of the layout as possible. See [rendering and compact layouts](references/rendering.md) for regeneration and fallback checks.
5. **Inspect the exact artifact.** Check chart marks against source data, text and legends at actual insertion size, and caption and links in the final PDF or DOCX. Compare the exported figure with its input, especially after fallback. Fix clipping, crowded labels, mismatched units, missing negatives, and inappropriate chart or axis changes. Use the source notes and caption in the audience file. Keep diagnostics and tool details in the handoff only when they matter.

Use image generation for conceptual scenes when appropriate. Use a deterministic renderer or native editing tool for quantities, precise labels, risk scores, schedules, and diagrams where the connections must be exact.
