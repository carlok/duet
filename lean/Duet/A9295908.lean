import Mathlib.Order.Lattice
import Mathlib.Order.BoundedOrder.Basic
import Mathlib.Order.Heyting.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fin.VecNotation

/-! # Candidate a9295908 (N1 rank 3): what the theory says

Written by hand on 22 Nov 2026 (`notes/a9295908.md`). General statements for every type and every pair of operations,
plus one finite counterexample by `decide`.

The theory T, with · = `f` and ∘ = `g`: `x · (x ∘ x) = x`, `(x ∘ y) · y = y`, `x · y = x ∘ (y · x)`.

* `T_iff_C`: T is equivalent to C: · is commutative and idempotent, `x ∘ (x · y) = x · y` and `(x ∘ y) · y = y`.
* `inf_iff`: when · is the meet of a semilattice, T says exactly that each map `y ↦ x ∘ y` is the identity on the
  elements below `x` and never moves an element down: `y ≤ x → x ∘ y = y` and `y ≤ x ∘ y`.
* `threshold_model`: so on every meet-semilattice with a top, `x ∘ y = (if y ≤ x then y else ⊤)` gives a model. On a
  chain this is Gödel implication with `x ∘ x = x` instead of `⊤`.
* `heyting_model`: every (generalized) Heyting algebra is a model with `x ∘ y = (y ⇨ x) ⇨ y`. That is the
  strict-order connective of Gödel logic on chains, so T is valid in Heyting algebras under that interpretation.
* `not_assoc`: T does not force · to be associative (a 3-element model, `decide`).
-/

namespace Duet.A9295908

variable {α : Type*}

/-- The theory of candidate a9295908. -/
def T (f g : α → α → α) : Prop :=
  (∀ x, f x (g x x) = x) ∧ (∀ x y, f (g x y) y = y) ∧ (∀ x y, f x y = g x (f y x))

/-- Its reading: a commutative idempotent `f` and two laws for `g`. -/
def C (f g : α → α → α) : Prop :=
  (∀ x, f x x = x) ∧ (∀ x y, f x y = f y x) ∧ (∀ x y, g x (f x y) = f x y) ∧ (∀ x y, f (g x y) y = y)

/-- Under T, `x ∘ x = x`. -/
theorem T_diag {f g : α → α → α} (h : T f g) (x : α) : g x x = x := by
  have h3 := h.2.2 x (g x x)
  rw [h.1 x, h.2.1 x x] at h3
  exact h3.symm

/-- Under T, · is commutative. -/
theorem T_comm {f g : α → α → α} (h : T f g) (x y : α) : f x y = f y x := by
  have hab : f (f x y) (f y x) = f y x := by
    have := h.2.1 x (f y x)
    rwa [← h.2.2 x y] at this
  have hba : f (f y x) (f x y) = f x y := by
    have := h.2.1 y (f x y)
    rwa [← h.2.2 y x] at this
  have := h.2.2 (f x y) (f y x)
  rw [hab, hba, T_diag h] at this
  exact this.symm

theorem T_iff_C (f g : α → α → α) : T f g ↔ C f g := by
  constructor
  · intro h
    refine ⟨fun x => ?_, T_comm h, fun x y => ?_, h.2.1⟩
    · have := h.1 x
      rwa [T_diag h] at this
    · have := h.2.2 x y
      rw [T_comm h y x] at this
      exact this.symm
  · rintro ⟨hi, hc, hg, h2⟩
    have hd : ∀ x, g x x = x := fun x => by
      have := hg x x
      rwa [hi] at this
    refine ⟨fun x => ?_, h2, fun x y => ?_⟩
    · rw [hd, hi]
    · rw [hc y x, hg]

/-- With · the meet of a semilattice: `x ∘ -` fixes the elements below `x` and never moves an element down. -/
theorem inf_iff [SemilatticeInf α] (g : α → α → α) :
    T (fun a b => a ⊓ b) g ↔ (∀ x y : α, y ≤ x → g x y = y) ∧ (∀ x y : α, y ≤ g x y) := by
  rw [T_iff_C]
  constructor
  · rintro ⟨-, -, hg, h2⟩
    refine ⟨fun x y hyx => ?_, fun x y => ?_⟩
    · have := hg x y
      simp only at this
      rwa [inf_eq_right.mpr hyx] at this
    · have := h2 x y
      simp only at this
      exact inf_eq_right.mp this
  · rintro ⟨hfix, hext⟩
    refine ⟨fun x => ?_, fun x y => ?_, fun x y => ?_, fun x y => ?_⟩
    · simp
    · exact inf_comm x y
    · exact hfix x _ inf_le_left
    · exact inf_eq_right.mpr (hext x y)

/-- On every meet-semilattice with a top: `x ∘ y = y` if `y ≤ x`, else `⊤`. -/
theorem threshold_model [SemilatticeInf α] [OrderTop α] [DecidableRel ((· ≤ ·) : α → α → Prop)] :
    T (fun a b => a ⊓ b) (fun x y : α => if y ≤ x then y else ⊤) := by
  rw [inf_iff]
  refine ⟨fun x y hyx => by simp [hyx], fun x y => ?_⟩
  split_ifs
  · exact le_refl y
  · exact le_top

/-- Every (generalized) Heyting algebra is a model, with · the meet and `x ∘ y = (y ⇨ x) ⇨ y`. On a chain this is the
strict-order connective of Gödel logic (Baaz, Ciabattoni and Zach 2000); see `notes/a9295908.md`. -/
theorem heyting_model [GeneralizedHeytingAlgebra α] :
    T (fun a b => a ⊓ b) (fun x y : α => (y ⇨ x) ⇨ y) := by
  rw [inf_iff]
  refine ⟨fun x y hyx => ?_, fun x y => le_himp⟩
  simp only [himp_eq_top_iff.mpr hyx, top_himp]

/-- A 3-element model in which · is not associative (∘ is the right projection). -/
def f3 : Fin 3 → Fin 3 → Fin 3 := fun x y => ![![0, 2, 0], ![2, 1, 0], ![0, 0, 2]] x y
def g3 : Fin 3 → Fin 3 → Fin 3 := fun _ y => y

theorem not_assoc : T f3 g3 ∧ ¬ ∀ x y z : Fin 3, f3 (f3 x y) z = f3 x (f3 y z) := by
  unfold T f3 g3
  decide

end Duet.A9295908
