# Chart verification

The original [Essay Studio verification record](../assets/charts/verification.json) covers its archived TeX renders. The current bank preserves the 13 source fixtures, corresponding previews, and original TeX renderer. The archived PDF, PNG, and input hashes match the gallery catalog.

The current wrapper and fallback were checked in a relocated folder with spaces and no TeX executables on the discovery path. Automatic fallback rendered all 13 fixtures across 12 families into decodable PNGs, one-page vector PDFs, editable SVGs, and regenerable TeX. The fixture contact sheet was inspected for labels, flow, and plot geometry. The wide Gantt renders at about 16 × 3.3 cm and retains its four periods and task labels. The paired sectional graphic opens as both vector PDF and PNG.

Additional checks exercised an invalid Gantt, a missing mandatory font, source-only status, and conservation of histogram counts. The original renderer's 14 input and export self-checks also passed. TeX executables in the current environment failed to compile due to missing local TeX format/package files, so this revision used Matplotlib for fresh compiled media. The repository contains the original verified TeX examples and backend for an environment with a working TeX installation.

These checks cover the bundled fixtures. Every new chart still needs inspection at its intended size in the delivered document.
