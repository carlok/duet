# How it started

[← README](../README.md)

The project began as a small experiment: a genetic search over *theories* instead of over numbers or programs. A
theory is a handful of equational laws in two binary operations, written `x · y` and `x ∘ y`.

**The first sessions** ran in the cloud on two cores, with z3 as the only prover. They verified 99 theories. Most of
the ones that proved anything turned out to be pieces of lattice theory (64 of 97). The first find that looked new
was not: it was two of the four laws of McKenzie's 1970 basis for lattices.

That set the tone for everything after. The machine is good at walking back into known mathematics, so the real work
is telling what it rediscovered apart from what nobody has written down.

**The move to a Mac** with 11 cores grew the project to fit that job:
- everything runs in Podman, and nothing is installed on the host;
- the search streams, and every promising theory is verified at once;
- five provers built from pinned sources (E, Vampire, Prover9/Mace4, Twee) and Lean 4 for certificates;
- every scaled run is preregistered before it starts.

Along the way, two early lessons:
- **Infinite countermodels.** Four early implications turned out false with only infinite countermodels. Saturating
  provers settled them, with an independent certificate.
- **Survivor claims.** Of 32 claims that resisted the provers, 31 are now refuted and one is open ([S12](open-problems.md)).
  Some refutations came from an LLM working offline, outside the search. They count only after our own machine check.

Next: [why: synergy and the jazz aim](motivation.md).
