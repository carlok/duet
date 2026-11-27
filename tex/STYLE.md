# The paper: page budget, narrative and style

The paper (`paper.tex`) stays at **7 pages or fewer**, bibliography included, so that each new result displaces
something rather than adding a page. Written 27 Nov 2026, after X12, when the paper had just been cut back from 8
pages to 7.

## Where the space goes now (7 pages)

| part | words | grows with |
|---|---:|---|
| abstract | 230 | every run (funnel numbers, families per run) |
| question, related work | 360 | rarely |
| setting and method | 380 | a new verifier stage or screen |
| funnel and the nine (two tables, one paragraph) | 550 | a new level-8 theory (one table row) |
| calibration | 120 | no |
| claims finite search cannot refute | 250 | no (history) |
| rediscovery and disguises | 320 | every identification |
| diagonal attractor and the fusion arms | 390 | every run |
| families | 200 | every run |
| limitations, status | 360 | rarely |
| bibliography (37 entries, some with reading notes) | ~1.7 pages | every new source |

The growth is in four places: the abstract's per-run numbers, the run-by-run story of the arms, the prose list of
identifications and the bibliography. The rest is stable.

## Narrative

The paper is a method and its standing results, not a diary of runs.
- **Lessons, not runs.** The arms section tells what each change taught: rediscovery, disguises, the diagonal attractor,
  steering away from the known, diversity pressure. A run's name appears only where its number is the evidence. The
  chronology lives in `docs/search.md` and `REPORT.md`.
- **The nine are the subject.** Results open with the funnel and the unidentified theories. Everything else supports
  how much to trust them: calibration, refutations, rediscovery, the arms.
- **Identifications are a list, not a story.** Each needs only its key, what it turned out to be and the source; the
  route is in the ledger (`notes/rediscovery.md`).
- **Say what is open.** Limitations and status stay, short.

## Style

- **Each number once.** It goes in a table, or in the abstract, or in the prose, not in all three. The prose points to
  the table.
- **No internal names in prose.** Not `x10a`, `fusion6` or `V8`: say "the first block of X10", "an arm that lowers the
  priority of common families", "a time limit on Z3".
- **No per-run lists in the abstract.** Say what holds now (241 families, still rising), not the last five increments.
- **One example per claim**, the one that carries it.
- **Reading status of a source** goes in the ledger or the REPORT, not in the bibliography note, except for "not read".
- Crisp register (unslop `crisp`): concrete facts and plain verbs, no previews or recaps. "Synergy" is the defined term,
  not jargon.

## Rules for adding a result

1. A new run adds one row to a runs table, and prose only if it changes a lesson (two lines at most).
2. A new identification adds one row to an identifications table.
3. A new level-8 theory adds one row to the table of the nine (and its paragraph gets one clause).
4. At 7.0 pages, every addition names what it displaces, in the commit message.
5. Rebuild and check the page count before every commit (`podman run --rm -v "$PWD/tex:/tex" soup-tex`).

## Moves that buy room (not yet applied)

| move | saves now | effect on growth |
|---|---:|---|
| the X4–X12 prose becomes a runs table (run, arm in words, verified, new families, lesson) plus 5 lines of lessons | ~5 lines | one row per run instead of 2–4 lines |
| abstract without the funnel enumeration and per-run family counts; it points to Table 1 | ~3 lines | stops growing |
| identifications as a 4-row table (Δ-bijective, Steiner disguise, Heyting fragment, g-dimonoid) | ~3 lines | one row each |
| "claims finite search cannot refute" cut to the method and the one open claim | ~6 lines | none |
| bibliography notes shortened to "not read" / nothing | ~5 lines | fewer per source |
| status cut to provenance and the repository link | ~3 lines | none |

Together, about 25 lines, half a page of reserve. Last resort, not to be used yet: 10pt type (about 0.7 pages).
