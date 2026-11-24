# Is this a new (meta)field? A literature check (24 November 2026)

## The question

The work so far is taxonomy. The search finds theories ("species") and F1 sorts them into families. The hope is that
cataloguing patterns comes next, then conjectures, then perhaps theorems. Could that be a new (meta)field? Before saying
so, we looked for the closest prior work.

## How it was checked

- **Three web searches in parallel, one per strand**, each run by a research agent (Claude Code; not part of the search,
  so rule 6 is untouched):
  - **A.** Automated theory formation and theory exploration.
  - **B.** Catalogues leading to conjectures and proofs, and catalogues of equational theories.
  - **C.** Open-ended search over mathematical objects, ecological estimators, and the "meta" level.
- **Their tables** are in [`metafield_sources/`](metafield_sources/): about 105 rows, with overlaps between strands.
  Each row says whether the agent opened the page or only saw a search snippet.
- **Primary pages I opened myself:**
  - Le Floch's 456 semigroup varieties: the abstract and the future-work section.
  - SemiBase: the abstract.
  - Wolfram's "Axiom systems in the wild" (Metamathematics, section 17).
  - Wolfram's essay "What Is Ruliology?".
  - STADS: the abstract.
  - Lenia: the abstract.
- **Records only, for existence:** the ESARM 2008 table of contents (Charnley and Colton) and the ICCC 2015 record
  (Bou et al.). The descriptions of those two papers come from the agents' reading.
- **Already cited**, so not searched again: McCune and Padmanabhan, McCune–Padmanabhan–Veroff, the ETP, Le Floch's 990
  quasigroup laws (arXiv:2603.29909), Janota–Rawson–Schulz, and MAP-Elites.

## Verdict

**"A new (meta)field" does not hold.** Four traditions already occupy that ground.

1. **Automated theory formation and theory exploration** have been an established field since the 1970s.
   - Lenat's AM (1976).
   - Colton's HR (1999–2014). It runs the same loop we do on finite algebras: Otter proves, MACE refutes, and an
     interestingness score steers the search.
   - Buchberger named "theory exploration" in 2000. The Automatheo workshops followed (2009–2012), and so did the
     QuickSpec, Hipster and IsaCoSy line.
   - Colton, Torres, Cairns and Sorge (MKM 2006) let HR explore the one-axiom star algebras, and then proved a theorem
     about the whole family.
2. **Wolfram's "ruliology" and empirical metamathematics.**
   - A New Kind of Science (2002, ch. 12) enumerates one-operator axiom systems from the simplest upward. That search
     found the shortest single axiom for Boolean algebra.
   - In Metamathematics (2022, section 17) every axiom system is a possible field of mathematics.
   - His essay "What Is Ruliology?" (Jan 2026) calls the systematic exploration of rules a new science. He compares its
     early stage to natural history, which moves from observations to classifications to principles. That is our arc,
     claimed for rules in general.
3. **Computational universal algebra and exhaustive catalogues of varieties.**
   - Ježek and Kepka (1979–89) classified the varieties defined by short identities.
   - Berman and Burris (1996) catalogued the 3-element groupoids.
   - Phillips and Vojtěchovský (2005) found the 26 Bol–Moufang varieties with Otter and Mace4.
   - After the ETP the work sped up:
     - Le Floch's 456 semigroup varieties: all conjunctions of semigroup laws of order ≤ 4, in Lean (arXiv:2609.39872,
       Sep 2026).
     - SemiBase: 505 certified semigroup varieties (arXiv:2610.02500, Oct 2026).
     - Berlioz and Melliès: a "latent space" of laws built from satisfaction statistics on finite magmas, close to our
       law × structure matrix.
   - Le Floch's future-work section reports that ETP members have almost finished the conjunction lattice of
     one-operation laws of order ≤ 3.
4. **From catalogue to pattern to conjecture to theorem**, and the natural history of objects found by search.
   - The catalogue-to-theorem arc:
     - BSD, from EDSAC point counts (1965);
     - Graffiti, and its successor TxGraffiti;
     - AutoGraphiX;
     - Davies et al. (Nature 2021);
     - the murmurations of elliptic curves (2022), proved for modular forms by Zubrilina (Invent. math. 2025).
   - The natural history: Lenia (2019) describes more than 400 "species" in 18 families of a continuous cellular
     automaton, many found by evolutionary search, with a hierarchical taxonomy and binomial names.

**What we found no prior work on.** This is weak evidence: three web searches, partly from snippets.

- **An open-ended quality-diversity search whose individuals are sets of laws in two operations**, with synergy (laws
  the whole implies and no single law does) as the objective. The nearest cases:
  - Charnley and Colton (ESARM 2008) generated 100 specialisations of one algebra and ranked them by average proof
    length.
  - TheoryMine mass-generated inductive theories and filtered them against a library.
  - Wolfram and Le Floch enumerate, in one operation.
- **A taxonomy of theories by reduct signature, counted with richness estimators.** The nearest cases:
  - Colton et al. (IJCAR 2004) classify the *models* of one theory, not theories.
  - STADS applies the estimators to fuzzing.
  - Lenia's families come without estimators.
- **Conjectures stated across families of varieties.** HR, AGInT and MATHsAiD conjecture inside one theory.
- **Two independent operations at scale.** Every exhaustive catalogue found is one-operation, or quasigroup-derived, or
  model-driven, like the semiring catalogues.

**The defensible framing** is a new combination inside automated theory formation and computational universal algebra:
open-ended search over two-operation theories, aimed at fusion, with a taxonomy of what it finds. The activity already
has a name (ruliology). We cite Wolfram and the theory-formation literature, and we do not coin a field.

## What this changes in the project

1. **The Chao1 numbers need a caveat** (fixed in `soup.taxonomy`, the README and `docs/families.md`). Chao1 assumes
   unbiased sampling from a fixed population. Our sampling is adaptive and deliberately biased:
   - the fusion arms skip known theories and everything seen before;
   - the arms changed from run to run.

   STADS raises the same problem for fuzzers, and Hajič and Moss (2025) show that the bounds stay loose while new items
   keep arriving at a steady rate. X7 alone added 26 families. So "Chao1 138" is not an estimate of how many families
   exist. It is only a descriptive index, and the plain count (124, still rising) is the honest number.
2. **The one-operation catalogues next door are useful, not just competition.**
   - When the ETP's order-≤3 conjunction lattice appears, the ·-reducts and ∘-reducts of our structured families can be
     placed in it.
   - Le Floch's semigroup lattice already covers every associative reduct.
   - Jipsen's CAL-db (a database of classes of algebras) is a further known library to check candidates against.
3. **For the conjecture phase, existing work to build on:**
   - HR's interestingness literature (Colton, Bundy and Walsh 2000);
   - "short statement, hard proof" ranking (Charnley and Colton 2008);
   - Colton et al. 2006 as the model of a theorem about a whole family;
   - Davis's critique of Davies et al. (2021), as a warning against overclaiming.
4. **The paper's related work** now names the four traditions.

## Sources checked first-hand

| Source | What was checked |
| --- | --- |
| Le Floch, *Lattice of 456 semigroup varieties from equations of order up to 4*, arXiv:2609.39872 (Sep 2026) | abstract; future work: order-≤3 magma conjunctions nearly done, order 4 at least several million classes |
| Araújo, Hůla, Janota, Lee, Naskręcki, *Proving at Scale for Universal Algebra* (SemiBase), arXiv:2610.02500 (Oct 2026) | abstract: 505 varieties from the order-6 bases; LLM-guided proof search, Lean audit |
| Wolfram, *Metamathematics* (2022), section 17, https://www.wolframscience.com/metamathematics/axiom-systems-in-the-wild/ | each axiom system a possible field; one-operator enumeration with an ATP |
| Wolfram, *What Is Ruliology?*, Wolfram Institute, 12 Jan 2026, https://wolframinstitute.org/output/what-is-ruliology | "a new science"; natural history first, then classifications and principles |
| Böhme, *STADS: Software Testing as Species Discovery*, TOSEM 2018, arXiv:1803.02130 | ecological estimators on a discovery process with adaptive sampling bias |
| Chan, *Lenia: Biology of Artificial Life*, Complex Systems 2019, arXiv:1812.05433 | over 400 species in 18 families, many found by evolutionary search, hierarchical taxonomy |
| Charnley, Colton, ESARM 2008, CEUR-WS Vol-378 paper 1 | existence and authors only (the PDF was not readable here) |
| Bou et al., *The role of blending in mathematical invention*, ICCC 2015 | existence and authors only (Semantic Scholar record) |
