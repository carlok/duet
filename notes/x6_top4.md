# X6's N1 ranks 1–4: `bc43fd42`, `d0e963d9`, `d14ced44`, `3818b88f` (23 Nov 2026; post hoc)

Status: **candidates, not identified**. "No source found" is weak evidence. Checks: `notes/dig_light.py <key>`
(outputs `notes/dig_<key>.out`) and `notes/x6_top4_checks.py` parts 1–2 (outputs `notes/x6_top4_checks.out`,
`notes/x6_top4_checks_2.out`). E runs 20–60 s per goal; "False" in the outputs means no proof in that budget, not a
refutation.

## A family of three

| key | laws |
| --- | --- |
| `bc43fd42` | x·(y·z) = x·(z∘y), x·(((y∘y)·z)·w) = x |
| `d0e963d9` | x·(y∘y) = x, x·((x·y)·x) = x, x·(y·z) = x·(z∘y) |
| `d14ced44` | x·(y∘y) = x, x·(y·z) = x·(z∘y), x·((x·y)∘y) = x·y |

- **A common core.** Each implies K = {x·(y·y) = x, x·(y∘y) = x, x·(y·z) = x·(z∘y)}. K implies none of them, and E
  proves no implication between any two of them (part 1).
- **Reading of K:** every square, of either operation, is a right identity for ·, and left multiplication cannot tell
  y·z from z∘y. K also gives x·(y∘z) = x·(z·y).
- **Emergent laws:** x·(y·y) = x is emergent in all three (`dig_*.out`).
- **Shadow:** with x·y = x∘y, each becomes the left-zero band x·y = x.
- **ETP:** x = x◇(y◇y) is Equation 11, and x◇(y◇z) = x◇(z◇y) is Equation 4358 (both mappings checked by
  `law_index`). ETP names neither.
- **Literature:** a web-only agent searched on 23 Nov. x(yz) ≈ x(zy) appears as a one-operation identity in Huang and
  Lehtonen, "Associative-commutative spectra for some varieties of groupoids", arXiv:2401.15786. That is a paper on
  AC-spectra, not on these theories. Nothing was found for squares as right units, or for the two-operation law.

## `3818b88f`: a triple system with a selector

T = {x·(x·y) = y, (x·y)·y = x, x∘(x·y) = x∘y, (x·x)∘(x∘x) = x, (x·(x·x))∘x = x}.

- **Plain reading (E, both ways).** T is equivalent to:
  - x·y = y·x and x·(x·y) = y: · is a totally symmetric quasigroup;
  - x∘x = x;
  - (x·x)∘x = x;
  - x∘(x·y) = x∘y.
- **Reading.** A totally symmetric quasigroup is a triple system: the blocks are the sets {x, y, x·y}. The law
  x∘(x·y) = x∘y says that x∘y depends only on x and the block through x and y. So ∘ is a selector on (point, block)
  pairs: idempotent, and returning x on the block {x, x·x}.
- E also proves x∘(y·x) = x∘y. It does not prove x·x = x, commutativity of ∘, or associativity of ∘.
- **Models from triple systems** (`notes/3818b88f_models.py`, labelled tables). Every TS-quasigroup on n ≤ 4 elements
  carries ∘ operations satisfying the reading: 2, 29 and 1,024 on n = 2, 3, 4, almost all non-degenerate in our
  sense (∘ not a projection, a constant or ·). Of these, 2, 28 and 432 are selectors, with x∘y in {x, y, x·y}. On
  n = 4 every choice of one value per (point, block) works. So ∘ is very free: the theory is a triple system plus
  a nearly arbitrary choice function, and that weighs against calling it a deep fusion. Sampled models pass the
  five original laws (law_vector).
- **Shadow:** with x·y = x∘y, only one-element models are left.
- **ETP:** x = y◇(y◇x) is Equation 16, x = (x◇y)◇y is Equation 26, and commutativity is Equation 43 (checked).
- **Literature:** TS-quasigroups, squags and sloops (Quackenbush 1976), and the cubic-curve TS-quasigroups (Etherington;
  Padmanabhan and McCune 2006). Nothing pairs a TS-quasigroup with an idempotent second operation, and nothing was
  found for x∘(x·y) = x∘y. The agent suggests orientations or selectors on Steiner triple systems as the next place to
  look.
- **Drápal, Griggs and Kozlik, "Triple systems and binary operations"** (Discrete Math. 325 (2014) 1–11,
  doi:10.1016/j.disc.2014.02.007), the closest prior art found. Only the abstract was read, by a web-only agent
  from the archived Open University page; the full text was not reachable. It builds one idempotent operation per
  Steiner, Mendelsohn or hybrid triple system (x∗y = the third point of the block), and no second operation. Our ∘
  is constant on each block from x's point of view, which is a different kind of operation. A remark in the full
  text cannot be ruled out.
  look.

## Reading

None of the four is identified. The family pins down only how · treats squares and products from the left, so it
sits close to left-zero bands. 3818b88f is a classical object, a triple system, with a second operation that chooses
within blocks. That is the more structured of the two, and the better one to show a design theorist.
