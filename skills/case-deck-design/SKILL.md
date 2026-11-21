---
name: case-deck-design
description: Build or revise editable business-case competition and consulting pitch decks from the user's Markdown context pack, current deck and supplied PPTX slide bank. Inspect and adapt native donor elements into new layouts, preserve the current design and approved slides, and verify evidence, citations, navigation and rendered output. Activate only for an explicit user request for a BCC deck, PPTX design, slide-bank reuse, or scoped revision of such a deck.
---

# Case Deck Design

Activate only when the user explicitly asks for a BCC deck or a deck revision. Use the actual organizer requirements and current project as the source of slide limits, content, and design rules. A context pack labeled draft or superseded cannot override accepted decisions or later evidence.

Translate the user's arguments into an editable, carefully composed case presentation. Treat the master AI context pack as the content authority and the current working deck as the design authority. Treat the supplied slide bank as a collection of reusable native elements and useful compositions. Do not bundle, assume access to, or default to a slide bank from another project.

## The working agreement

- Preserve the user's thesis, recommendations and mechanisms. Improve sequencing, explanations, headlines and visual communication. Flag unsupported arguments and propose alternatives separately; do not silently replace the strategy.
- Reuse actual elements: framework branches, folded panels, process lanes, timeline bars, risk tables, chart arrangements, number treatments and callout containers. Recombine selected elements into layouts that fit the content. Whole-slide duplication is useful when the composition fits, but is not the default unit of reuse.
- Follow the **current** deck's typography, font sizes, palette, spacing, logo treatment, section markers and source conventions. Recolor and restyle copied elements to that system. A donor's branding is not the target design. Explicit current instructions take priority over inferred patterns.
- Keep text, structural diagrams, data charts and tables editable. Use screenshots or generated imagery for experience illustrations, photos and other appropriate raster assets, not as a substitute for editable slide content.
- For a **new deck or broad redesign**, inspect the materials and form a concrete storyline. If the user asks to see a plan first, present it with donor-element options and thumbnails where useful. When production is authorized, ask once about consequential unresolved scope or design choices and build the agreed deck. Continue useful read-only work while awaiting a material decision.
- For a **clearly scoped revision**, make the requested change directly and preserve everything outside scope. Do not restart a full discovery or approval cycle. A request to change two backmatter sections is not permission to improve solutions, finance, wording or other slides.
- Preserve the original file and create a separate output. Treat approved or locked slides, notes and dependencies as immutable except for specifically authorized changes. Include navigation retargeting needed to preserve the authorized result. Ask before a correction would change other content or interactions outside the agreed scope.

## Start with the right inputs

Read [Intake and planning](references/intake-and-planning.md). Identify the current MD context pack, current working PPTX, slide bank(s), competition brief, raw supporting files, visual assets, scope and approval state. Identify their roles explicitly; a combined deck may contain several brands and finished slides.

If the pack leaves a material claim unresolved, first inspect supplied raw files. Ask for the specific missing dataset, workbook, interview excerpt or source when needed. Mark nonblocking gaps clearly. Do not manufacture evidence or ask for files already available. Apply the environment's access and connector rules.

Keep a small private record for the actual task: input hashes and roles, locked/allowed-edit slides, design contract, slide plan, evidence/source ledger and donor-element map. Use logical slide IDs so insertions and appendix changes do not break references. Avoid imposing a fixed slide count, industry, strategy acronym, color palette or bibliography length.

## Inspect the slide bank and capture the design

Read [Element reuse and design](references/element-reuse-and-design.md).

1. Use `scripts/inspect_pptx.py` to inventory every slide and native object. Extract IDs, text, type, bounds, explicit fonts/colors, links, dependency types and editability clues. The report is not a visual assessment or complete inheritance resolver.
2. Render the bank. Inspect all slides through labelled contact sheets, then inspect shortlisted donor slides individually at readable size. Search by rhetorical purpose and visual arrangement, not only titles or keywords.
3. Inspect representative completed target slides at full size and their native properties. Separate stable design rules from one-off choices. Resolve inherited theme/layout styling when explicit attributes are absent. Record actual dimensions and units.
4. Select elements based on their purpose. Log donor file/hash, slide, shape IDs, target slide/element, adaptation and dependencies. Show actual donor crops in the pre-build plan; explain what will be recombined and why.

## Explain the case clearly

Read [Writing, evidence and impact](references/writing-evidence-and-impact.md). Use the user's natural professional voice. Lead analysis slides with supported insights; allow descriptive solution headlines explaining what the system enables. Give the practical problem before the method. Include enough connected explanation to understand why the feature addresses the problem.

Across each solution, cover what it is, who uses it, the diagnosed barrier, the mechanism and actors, relevant benchmark evidence where available, and expected impact with a transparent quantitative basis. Cover these consistently without forcing identical layouts or a fixed two-slide format.

Keep observations, reports, interpretations, benchmarks, proposals and model outputs separate. Derive impacts from supplied assumptions or label scenarios/targets explicitly. Never turn benchmark results into a promised result for this case. Keep revenue, contribution and cash distinct and avoid counting the same booking twice.

## Build using the available presentation workflow

Load the environment's Presentations skill and its relevant implementation, template-following, native-evidence and finalization guidance. It owns tool/API choices and output validation. Do not replace it with a hardcoded authoring stack. In the environment for which this skill was developed, authored slides use `@oai/artifact-tool`; package-level helpers below preserve native parts rather than re-exporting untouched slides.

Read [Native reuse and assembly](references/native-reuse-and-assembly.md) when moving elements or combining authored and preserved slides. Author current-case copy and data with host tools. Reuse donor geometry and apply the target design. Keep charts and workbook relationships intact. Avoid shared-master changes affecting locked slides.

| Helper | Job |
| --- | --- |
| `inspect_pptx.py` | Inventory slides, object IDs, explicit styles and dependency clues |
| `contact_sheet.py` | Make labelled review sheets from a rendered PDF |
| `transplant_elements.py` | Reuse shape shells and grouped frameworks in authored placeholders |
| `assemble_deck.py` | Combine selected base/authored slides while retaining base slide bytes |
| `audit_deck.py` | Verify package links, preservation mappings and declared navigation targets |
| `compare_renders.py` | Compare mapped slides from two rendered PDFs for pixel changes |

Run `--help` and read the relevant reference before using a helper. Dependency-bearing donor charts and pictures require a supported native copy workflow; the bounded transplant helper rejects them instead of dropping relationships. Use the host's chart/image APIs or a task-specific dependency importer when needed. Never claim a recreated element is a literal transplant.

For assets, speaker notes, citations and backmatter, read [Assets and navigation](references/assets-and-navigation.md). Every placeholder needs a format, required content, purpose and status. Source lines should locate evidence for the audience. Keep production commentary and QA logs private. Use the current design's source size and check actual legibility in the intended presentation. Reflow content where needed to keep sources readable.

## Inspect and deliver

Read [Visual QA and preservation](references/visual-qa-and-preservation.md). Render the exact final candidate; inspect every new or changed slide individually and compare with the target design. Check wrapping, clipping, spacing, connectors, editability, chart data and navigation. Verify retained slide/notes bytes and mapped rendered slides for scoped changes. Existing defects outside scope are separate findings, not automatic repair instructions.

Complete host finalization and save through its required delivery mechanism. Report only what was tested: renders and structural checks do not prove native PowerPoint or Google Slides compatibility. State necessary limitations. Link the deliverable, identify the requested outcome briefly, and stop optional redesign/testing once remaining risks are resolved.

## Read only the relevant detail

- [Intake and planning](references/intake-and-planning.md): source roles, questions, approval state and concrete plan.
- [Element reuse and design](references/element-reuse-and-design.md): bank inspection, object selection, design contract and recomposition.
- [Writing, evidence and impact](references/writing-evidence-and-impact.md): copy, issue trees, solutions, benchmarks and financial claims.
- [Native reuse and assembly](references/native-reuse-and-assembly.md): helper interfaces, transfer limits, assembly and manifests.
- [Assets and navigation](references/assets-and-navigation.md): prototypes, generated assets, APA references, categorized appendices and links.
- [Visual QA and preservation](references/visual-qa-and-preservation.md): rendering, invariants, scoped revisions and final checks.
