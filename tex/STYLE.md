# The paper: page budget, narrative and style

The paper (`paper.tex`) stays at **7 pages or fewer**, bibliography included, so that each new result displaces
something rather than adding a page. **The type stays standard:** 11pt body, 1in margins; tables and the bibliography
keep the `\small` they have always had. Room comes from less prose, not smaller type. Written 27 Nov 2026, after X12.

## Where the space goes (27 Nov 2026, after the restructure)

| part | form | grows with |
|---|---|---|
| abstract | prose, no per-run numbers; points to Table 1 | should not grow |
| question, related work | prose | rarely |
| setting and method | six numbered pipeline steps | a new stage or screen: one step |
| funnel and the nine | Tables 1 and 2, one paragraph | a new level-8 theory: one row, one clause |
| calibration | prose | no |
| claims finite search cannot refute | one paragraph and the open claim | no |
| rediscovery | one paragraph and Table 3 (identifications) | a new identification: one row |
| what each change taught | five lines and Table 4 (runs) | a new run: one row |
| families | one paragraph | no (new families go in Table 4) |
| limitations, status | four bullets, one paragraph | rarely |
| bibliography | 28 cited entries; notes only "Not read" or an identifier | a new source |

Reserve after the restructure: about a quarter of page 7 (roughly 12 lines).

## Narrative

The paper is a method and its standing results, not a diary of runs.
- **Lessons, not runs.** Table 4 says what each change taught; the five lines above it state the lessons. The
  chronology lives in `docs/search.md` and `REPORT.md`.
- **The nine are the subject.** Results open with the funnel and the unidentified theories. Everything else supports
  how much to trust them: calibration, refutations, rediscovery, the arms.
- **Identifications are a table, not a story.** What was found, what it turned out to be, the source. The route is in
  the ledger (`notes/rediscovery.md`).
- **Say what is open.** Limitations and status stay, short.

## Style

- **Lists, steps and tables before prose.** A procedure is numbered steps; a comparison or a sequence of runs is a
  table; prose only for the argument and the lessons.
- **Each number once.** It goes in a table, or in the abstract, or in the prose, not in all three. The prose points to
  the table.
- **No internal names in prose.** Not `x10a`, `fusion6` or `V8`: say "the first block of X10", "an arm that lowers the
  priority of common families", "a time limit on Z3". Run names (X4, X12) are fine where the table uses them.
- **No per-run lists in the abstract.** Say what holds now (241 families, still rising).
- **Terse table cells:** one or two lines each; a cell that wraps to four lines needs fewer words.
- **One example per claim**, the one that carries it.
- **Bibliography notes:** "Not read", or an identifier `abbrv` would not print (an arXiv number). Reading status goes
  in the ledger or the REPORT.
- Crisp register (unslop `crisp`): concrete facts and plain verbs, no previews or recaps. "Synergy" is the defined term,
  not jargon.

## Rules for adding a result

1. A new run adds one row to Table 4, and prose only if it changes a lesson (two lines at most).
2. A new identification adds one row to Table 3.
3. A new level-8 theory adds one row to Table 2 and one clause to its paragraph.
4. When the reserve is gone, every addition names what it displaces, in the commit message.
5. Rebuild with `podman run --rm -v "$PWD/tex:/tex" soup-tex make -B` (plain `make` can skip a rebuild when the source
   changed within the same second) and check the page count, overfull boxes and undefined citations before every
   commit.

## What the restructure moved out (27 Nov 2026)

These are in `REPORT.md`, `docs/search.md` or the ledger, not in the paper any more: the count 3,478 of 3,596 behind
the 97%; X4's lattice skip detail of one proposal in four; the shape of X10's parameter disguise and its 15 of 20 models
over 𝔽₄ or ℤ/6; X11's 5 of 20 classical candidates; the example implication with an infinite countermodel; "found
after the Latin-square literature" (the limitations keep the missed Yang–Baxter source); the status sentence on
which candidates were studied; the reading notes on five references.
