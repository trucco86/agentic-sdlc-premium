# English edition execution plan

Priority: complete English edition of canonical V0.6 (323 pages). No paid API, new secrets or external translation services. Use Codex within available subscription limits; do not assume parallel capacity.

1. Run translation_inventory.py and reconcile all versioned English units. Verify canonical source and per-page hashes. Audit existing pilot translations against PDF pages; do not assume they are complete or correct.
2. Partition pages 1–323 into 13 non-overlapping ranges of up to 25 pages. Resume missing or invalid units; split ranges further if context limits require it. Preserve code, URLs, terminology, tables and diagram labels. Compare truncated extraction with source PDF. Never invent missing text.
3. Store each range in a distinct JSON file under editorial/translations/en; reconcile existing pilot files to avoid duplicates. Keep author and review metadata truthful. Do not self-approve. Commit each completed range and run tests. Report counts of drafted, reviewed and blocked pages.
4. Build a private English HTML preview and PT-BR/EN selector preserving page position. Clearly label incomplete content; never silently substitute Portuguese. Translate navigation and diagram labels, preserving source semantics. Test mobile, keyboard navigation, links and language persistence.
5. Run all CI gates; request independent technical, editorial and visual reviews. No merge, deploy or public selector before explicit owner authorization and required gates. Report actual evidence and blockers.

Start with content translation, not additional orchestration infrastructure. Use isolated worktrees only if available; otherwise process sequentially. No external API billing.
