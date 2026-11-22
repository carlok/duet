import Mathlib.Logic.Function.Basic

/-! # Candidate 55cb2c91 (N1 rank 1): what the theory says

Written by hand on 22 Nov 2026 (`notes/55cb2c91.md`). General statements for every type and every pair of operations.

The theory T, with · = `f` and ∘ = `g`: `x · (x ∘ y) = x` and `x · y = ((y · z) · x) ∘ x`. E proves T equivalent to
C: `x · (y · z) = x · y`, `x · (x ∘ y) = x`, `x · y = (y · x) ∘ x` (both ways; `notes/55cb2c91_checks.py`, part 2).

* `C_implies_T`: one direction, by hand.
* `reduct_iff`: a groupoid `f` is the ·-part of a model of C iff `x · (y · z) = x · y`, `(x · y) · y = x · y`, every
  `x` is a value of `x · -`, and `y · x = y' · x → x · y = x · y'`. Then ∘ is forced on pairs `(y · x, x)`, where it is
  the swap `y · x ↦ x · y`, and free elsewhere (any `w` with `u · w = u`).
-/

namespace Duet.T55cb2c91

variable {α : Type*}

/-- The theory of candidate 55cb2c91. -/
def T (f g : α → α → α) : Prop :=
  (∀ x y, f x (g x y) = x) ∧ (∀ x y z, f x y = g (f (f y z) x) x)

/-- Its reading (equivalent to T by E, both ways). -/
def C (f g : α → α → α) : Prop :=
  (∀ x y z, f x (f y z) = f x y) ∧ (∀ x y, f x (g x y) = x) ∧ (∀ x y, f x y = g (f y x) x)

theorem C_implies_T {f g : α → α → α} (h : C f g) : T f g := by
  obtain ⟨hA, h1, hC⟩ := h
  refine ⟨h1, fun x y z => ?_⟩
  rw [← hA x y z, hC x (f y z)]

/-- The conditions on · alone. -/
def Reduct (f : α → α → α) : Prop :=
  (∀ x y z, f x (f y z) = f x y) ∧ (∀ x y, f (f x y) y = f x y) ∧ (∀ x, ∃ y, f x y = x) ∧
  (∀ x y y', f y x = f y' x → f x y = f x y')

open Classical in
/-- The ∘ built from ·: the swap where it is forced, a fixed choice elsewhere. -/
noncomputable def swapOf (f : α → α → α) (hi : ∀ x, ∃ y, f x y = x) : α → α → α :=
  fun a b => if h : ∃ y, f y b = a then f b (Classical.choose h) else Classical.choose (hi a)

theorem reduct_iff (f : α → α → α) : (∃ g, C f g) ↔ Reduct f := by
  constructor
  · rintro ⟨g, hA, h1, hC⟩
    refine ⟨hA, fun x y => ?_, fun x => ⟨g x x, h1 x x⟩, fun x y y' h => ?_⟩
    · have h2 := h1 (f x y) y
      rw [← hC y x, hA] at h2
      exact h2
    · rw [hC x y, hC x y', h]
  · rintro ⟨hA, hB, hi, hii⟩
    refine ⟨swapOf f hi, hA, fun a b => ?_, fun x y => ?_⟩
    · unfold swapOf
      split
      next h =>
        rw [hA]
        have h2 := hB (Classical.choose h) b
        rw [Classical.choose_spec h] at h2
        exact h2
      next h => exact Classical.choose_spec (hi a)
    · unfold swapOf
      split
      next h => exact hii x y (Classical.choose h) (Classical.choose_spec h).symm
      next h => exact absurd ⟨y, rfl⟩ h

end Duet.T55cb2c91
