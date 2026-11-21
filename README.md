# Competition Proposal Skill Bank

A private collection for written business case competitions, business plan competitions, and innovation essays in Indonesian or English. Start with **Proposal Workflow**. It chooses the competition track and opens the skills needed for the current task. **Case Deck Design** is available when you explicitly ask for a BCC deck.

## Start in ChatGPT Work

1. Extract the outer ZIP. If **Plugins → Skills → Create → Upload** is available, upload `chatgpt-work/proposal-workflow.zip` as a single skill. Keep it private. Start a Work conversation, attach the current brief and relevant materials, then select **Proposal Workflow** or ask for it by name. The single-skill package embeds all 14 supporting guides and their tools. For full voice calibration against Gotong Sampah or ReGenCity, attach those originals from `references/examples/`.
2. If skill upload is unavailable, attach the outer ZIP or give ChatGPT Work access to the extracted private files. Use [START_HERE.md](START_HERE.md) in the conversation. The starter asks it to open the real workflow and determine which supporting skills apply. Provide the current task files separately.
3. For a private GitHub repo, put the extracted files at the repository root. Keep the curated references private. When a session can read the checkout, point it to [Proposal Workflow](skills/proposal-workflow/SKILL.md). The route table uses repository-relative paths. Keep `skills/` and `references/` together.

[OpenAI's instructions for Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)

| Skill | What it handles |
|---|---|
| [Proposal Workflow](skills/proposal-workflow/SKILL.md) | Task routing from brief to final handoff |
| [Competition Brief and Scope](skills/competition-brief-and-scope/SKILL.md) | Rules, rubric, deliverables, page budget and material assumptions |
| [Proposal Strategy and Argument](skills/proposal-strategy-and-argument/SKILL.md) | Diagnosis, recommendations and the finished solution in use |
| [Writing and Editing](skills/writing-and-editing/SKILL.md) | Voice, prose, headings, content preservation and scoped revisions |
| [Research, Evidence, and Citations](skills/research-evidence-and-citations/SKILL.md) | Claim support, checked sources and reader-facing citations |
| [Implementation, Impact, and Feasibility](skills/implementation-impact-and-feasibility/SKILL.md) | Roadmap, owners, resources, risks, impact and applicable finance |
| [Charts, Figures, and Tables](skills/charts-figures-and-tables/SKILL.md) | Twelve editable figure families, compact layouts and renderer selection |
| [Appendices and Document Production](skills/appendices-and-document-production/SKILL.md) | Visual exhibits, sentence-level links, pagination and final files |
| [Judge Review and Final Checks](skills/judge-review-and-final-checks/SKILL.md) | Rubric scoring, independent critique where available, repair and verification |
| [Find and Use Tools](skills/find-and-use-tools/SKILL.md) | Work capabilities, private catalog and online tool discovery |
| [Competition Brainstorming](skills/competition-brainstorming/SKILL.md) | Develop the user's idea and explore alternatives when warranted |
| [Business Case Competition](skills/business-case-competition/SKILL.md) | The incumbent's decision and an evidenced recommendation |
| [Business Plan Competition](skills/business-plan-competition/SKILL.md) | Buyer, market, operations and commercial viability |
| [Innovation Essay](skills/innovation-essay/SKILL.md) | Literature, the complete innovation, its features and implementation |
| [Case Deck Design](skills/case-deck-design/SKILL.md) | Editable BCC decks by explicit request |

[Reference index](references/README.md) · [Attributions and private-use note](ATTRIBUTIONS.md)

To rebuild the Work upload after editing the repository, run `python tools/build_work_bundle.py` from the extracted root. Its default package includes the calibration notes, shorter full samples, the tool catalog and chart assets. The outer archive holds the complete curated originals. The optional `--include-all-models` switch bundles those originals too.

## Verification

Run `python tools/check_bank.py --bundle chatgpt-work/proposal-workflow.zip` to check the module count, entry point, local links, and archive integrity. The release was also exercised on a new Indonesian innovation-essay brief, a narrow-revision walkthrough, an incumbent-versus-venture routing example, and a chart rendered from a freshly extracted Work package. The chart and deck instructions explain how to verify final outputs in the environment available to the current task.
