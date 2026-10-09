# Study content rendering and authoring

The app reads ordinary briefing Markdown and renders it with a safe, backward-compatible parser. Dates, Day cycles, specialties, category labels, question choices, recall cards, sources and authors remain authored content. Existing blockquotes, pipe tables, callouts and sequential diagrams are supported.

## Source-based visual aids

For main articles whose verified evidence supports a meaningful visual, include 1–2 compact visuals alongside the explanation. A third is appropriate only when it adds a genuinely distinct view, such as study design, observed events, and the reported adjusted effect with uncertainty. Do not fill every category slot with charts. If the needed values or relationships are missing or unreliable, keep prose/table coverage and explain the limitation briefly.

Read [Visual authoring](docs/VISUAL-AUTHORING.md) and [the exact version-1 schema](docs/visual-schema.md) before writing the blocks. Use a fenced `visual` block containing source-verified JSON; the installed renderer draws a fixed HTML/SVG template. Do not regenerate app code, call image generation, or copy protected journal figures for routine articles.

Supported types:

- `research-design`: verified population, allocation and groups, plus follow-up and endpoint.
- `event-bars`: reported patient-event percentages with events and analysis denominators, on a zero-to-100 axis.
- `comparison-bars`: same-unit numeric comparisons with a true zero baseline, including negative values.
- `effect-ci`: reported difference or ratio with a confidence interval. Difference null is 0; ratio null is 1 on a logarithmic axis.

Every block includes a source URL, label, exact source location and verification date. These fields are attribution, not proof of source review. Preserve the source's reported values, units, denominators, follow-up, uncertainty and comparison order. Never infer a missing observation or confidence interval. Observed group risks and adjusted treatment differences are separate quantities; a non-significant finding does not establish equivalence.

Place visuals under the relevant existing `####` body heading, after an explanatory sentence. Keep `## SPECIALTY_*`, `### paper|guideline|insurance|drug|interaction|safety:`, CASE, SELF_CHECK, RECALL_CARD and AUTHOR structure. Do not change article counts, dates, original authors or specialties to add a visual. Unknown/invalid blocks and a missing renderer retain escaped text rather than crashing the article.

## Tables, callouts and existing sequences

Pipe tables retain links, bold text, alignment and escaped pipes. Wide tables scroll within their own region. Standard callouts (`NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`) remain in their current content block and cannot overwrite the title.

Existing fenced `flow`/`diagram` blocks render an optional `title:` and one explicitly authored step per line as an ordered sequence. They are suitable only for a genuinely linear, source-supported process. Do not flatten branching clinical decisions into an apparent algorithm. Version-1 `research-design` is for population/group study structure, not a branching decision engine.

## Source-preserving SODa-BIC example

The 2026-10-06 SODa-BIC article contains three figures added on 2026-10-09 from the verified primary paper. The adjacent summary was narrowly corrected from language implying equality to “유의한 감소가 확인되지 않았다.” All other original prose, date, source attribution and author are preserved. The added figure date is separate from the original briefing date. The design uses allocated counts 245/255; the event chart uses analysis denominators 244/254; the reported adjusted difference is +1.2%p (95% CI −7.1 to +9.4).

## Safety, caching and historical coverage

Raw HTML is escaped; links are limited to HTTP(S). No arbitrary SVG, image embedding, scripts, callbacks or styling fields are accepted by the visual schema. Labels and descriptions remain text. Question selections are local and are not saved, scored or transmitted.

Service-worker cache names include the app path: `study:<encoded path>:v15`. The shell and renderer assets must load before the new worker activates. Cleanup targets that path's prefix only. The exact older `study-v13` cache is removable only by the production `/study/` worker on `https://bwkim1025.github.io` with matching registration scope. Other applications' caches are untouched.

Failed Markdown returns matching cached Markdown or a plain-text error, never the HTML shell. Previously viewed content is needed for offline reading. Deployment/browser checks are distinct from installed-device PWA migration verification.

The manual evidence-index utility is a partial lookup aid, not automatic history maintenance. A negative lookup cannot establish novelty. Keep the existing 90-day duplicate-check requirement unless a complete, current, source-hash-validated index proves equivalent coverage; otherwise inspect missing/changed/original files and report any coverage gap. Routine authoring permission does not authorize writing an index or changing schedules.
