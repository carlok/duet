# Prompt: offline look at the survivor implications

You are a mathematician working on equational logic (universal algebra). Below are 12 small equational
theories over two binary operations, written `·` and `∘`. For each theory, some equations ("open claims") are
neither proved nor refuted by automated tools. Decide, for as many claims as you can, whether the axioms imply
the claim, and give evidence in the machine-checkable form described below. Your output will be checked by
programs; nothing you write is accepted on your word.

## Notation and logic

- Variables x, y, z, w, u, v range over the carrier; every equation is universally quantified.
- `·` and `∘` are two unrelated binary operations. No other laws (no associativity, no commutativity, no
  identity element) unless an axiom states them.
- Implication means equational consequence (Birkhoff): the claim holds in every algebra, finite or infinite,
  that satisfies the axioms.

## What is already known (so you do not repeat it)

- A bounded countermodel search (z3 on the grounded axioms) found no countermodel on 2 to 6 elements. For
  some sizes the search ran out of budget, so small countermodels are unlikely but not excluded.
- The saturation provers E and Vampire, with several minutes each, found neither a proof nor a finite
  saturation. So a proof, if one exists, is not short for a machine; a countermodel, if one exists, is either
  larger than 6 elements or infinite and not given by a small convergent rewrite system.
- Similar theories in the same search had short human proofs that provers found hard: typically one axiom,
  instantiated cleverly, manufactures a local identity or a local zero, and another axiom then uses it.

## What to produce

For each claim you work on, one block of exactly one of these kinds:

1. `PROOF`: a numbered chain of equations E1, E2, ..., En, where En is the claim, each Ei follows from the axioms
   and E1..E(i-1) by a few rewriting/substitution steps. For each step say which axiom or earlier equation is
   used and with what substitution. Keep steps small: each Ei will be given to a prover separately.
2. `FINITE_MODEL`: size n ≥ 7, elements 0..n-1, the two full Cayley tables (n rows of n entries, row = left
   argument), and the claim instance that fails (values of the variables).
3. `INFINITE_MODEL`: an explicit construction: carrier (for example ℤ, ℤ[t], words over an alphabet, normal
   forms of terms) and formulas or an algorithm for both operations; a verification of each axiom; and an
   explicit instance where the claim fails. If the construction is a rewrite system, give the rules in the
   form `lhs -> rhs` with variables X, Y, Z and functions f (for ·) and g (for ∘).
4. `LEMMA_ONLY`: useful consequences of the axioms you derived (as a PROOF chain) without reaching the claim.
5. `NO_PROGRESS`: say so in one line. This is an acceptable answer.

Rules:
- Write equations in the same notation as the axioms (`·`, `∘`, parentheses, variables x y z w u v).
- Do not write "clearly", "it can be shown" or "by symmetry" without the explicit steps. If you use a duality
  (swap the operations, or reverse the arguments), say which, and check that the axioms are closed under it.
- If you recognise a theory as a known variety (or equivalent to one), name it and give a reference you are
  sure of; otherwise say you are not sure. Do not invent references.
- Several theories are related (for example one is another plus one law). Results may transfer; say when.

## Output

Write one Markdown file per theory, `S<i>.md`, plus `summary.md` with one line per claim
(`S<i> | claim | PROOF / FINITE_MODEL / INFINITE_MODEL / LEMMA_ONLY / NO_PROGRESS`). Write only into the output
directory you are given. Do not read or write anything else.

## The theories

### S1 (`00f017a6`)

Axioms:
- x · ((x · y) ∘ y) = x
- x · ((y ∘ x) ∘ z) = x
- x ∘ ((y · x) · z) = x
- x ∘ ((x ∘ y) · y) = x

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S2 (`45b1f0fb`)

Axioms:
- x · x = x
- x ∘ x = x
- x · (x · (x ∘ y)) = x
- x ∘ (x ∘ (x · y)) = x
- ((x ∘ y) · y) · y = y
- ((x · y) ∘ y) ∘ y = y

Open claims:
- x · (x ∘ y) = x

### S3 (`4ec6760a`)

Axioms:
- x · (x ∘ y) = x
- (x · y) ∘ y = y
- x · (y ∘ (x · y)) = x
- ((x ∘ y) · x) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S4 (`513de1ad`)

Axioms:
- x · ((y ∘ z) ∘ (x · z)) = x
- ((x ∘ y) · (x · z)) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S5 (`5e0dc923`)

Axioms:
- x · y = y · x
- x ∘ y = y ∘ x
- x · ((y ∘ x) · x) = x
- x ∘ ((y · x) ∘ x) = x
- (x · (x ∘ y)) · x = x
- (x ∘ (x · y)) ∘ x = x

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S6 (`bbdd0d1c`)

Axioms:
- x · y = y · x
- x ∘ y = y ∘ x
- x · ((y ∘ x) · x) = x
- (x ∘ (x · y)) ∘ x = x

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S7 (`cdf702b5`)

Axioms:
- x · x = x
- (x ∘ y) · (z ∘ (z · x)) = x

Open claims:
- x · (y · x) = x

### S8 (`d25065b6`)

Axioms:
- x · (x · (x ∘ y)) = x
- x ∘ (x ∘ (x · y)) = x
- ((x ∘ y) · y) · y = y
- ((x · y) ∘ y) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S9 (`e6403d7a`)

Axioms:
- x · (y ∘ (x · y)) = x
- x · ((y ∘ x) ∘ z) = x
- (x · (y · z)) ∘ y = y
- ((x ∘ y) · x) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S10 (`f096b282`)

Axioms:
- x · x = x ∘ x
- x · (y ∘ (y ∘ (x ∘ y))) = x
- x ∘ (y · (y · (x · y))) = x
- (((x ∘ y) ∘ x) ∘ x) · y = y
- (((x · y) · x) · x) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · (x · x) = x

### S11 (`f5321de4`)

Axioms:
- x · ((x ∘ x) ∘ y) = x
- x ∘ ((x · x) · y) = x
- (x ∘ x) · (x ∘ x) = x
- (x · x) ∘ (x · x) = x
- (x ∘ (y ∘ y)) · y = y
- (x · (y · y)) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x

### S12 (`f5e53602`)

Axioms:
- x · (y ∘ (y ∘ (x ∘ y))) = x
- x ∘ (y · (y · (x · y))) = x
- (((x ∘ y) ∘ x) ∘ x) · y = y
- (((x · y) · x) · x) ∘ y = y

Open claims:
- x · x = x
- x ∘ x = x
- x · x = x ∘ x
