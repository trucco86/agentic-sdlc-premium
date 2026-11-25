# Bilingual editorial policy

Portuguese is the canonical edition until a complete English edition is approved.

## Agent contracts
- Translation: translate every source page, including headings, tables, captions and diagram labels. Preserve code, identifiers, URLs and technical meaning. Record source page IDs.
- Technical review: compare each translation with the original; flag omissions, invented claims and terminology drift.
- Editorial QA: require coverage of every source page, review evidence, working links and visual inspection of diagrams and tables.
- Publishing: expose English only when all pages are approved; preserve continuous reading and internal TOC links. Never silently fall back to Portuguese in English mode.

## Release gates
Require matching canonical source SHA-256, complete page mapping, independent technical review, editorial approval and explicit merge authorization. A changed source invalidates affected translations. A missing English edition must not block the existing Portuguese reader.

## Terminology
Keep established terms such as Agentic SDLC, CI/CD, lead time, throughput, guardrails, harness engineering and pull request consistent. Preserve executable code verbatim unless a separately reviewed correction is required.

## Implementation backlog
1. Extract source page inventory and translation units.
2. Translate and review all 323 pages, including non-text visual content.
3. Build an English edition with continuous reading and language selector.
4. Validate completeness, browser navigation, print and public deployment.
5. Automate incremental translation and review on canonical changes.

This policy is a specification, not an active translation agent or a completed English edition.
