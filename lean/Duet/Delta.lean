import Mathlib.Logic.Function.Basic
import Mathlib.Data.Prod.Basic

/-! # The core of candidate 10c98c4b: Δ-bijective algebras with their dual operation

General statements, for every type and every pair of operations; no finite model and no `decide`.
Written by hand on 22 Nov 2026 (`notes/10c98c4b.md`). The facts are prior art: Dehornoy, Adv. Math. 282 (2015),
arXiv:1403.3019, §1 (the involutivity laws); Bonatto, Kinyon, Stanovský and Vojtěchovský, arXiv:1910.02148, §2.5,
Lemmas 2.10 and 2.11 (idea credited to Rump, Adv. Math. 193, 2005).
What is checked here is our reading of them and the reformulation of the four absorption laws.

* `B_iff_inverse`: B says that `delta g` is a two-sided inverse of `delta f`, where `delta f (x, y) = (f x y, f y x)`.
* `exists_B_iff_bijective`: some `g` satisfies B with `f` iff `delta f` is bijective.
* `absorb₁_iff` … `absorb₄_iff`: under B, each absorption law is a law about one operation (idempotent translations).
* `sq_inj`, `comm_imp_eq`: under B, `f x x = f y y → x = y` and `f x y = f y x → x = y`.
-/

namespace Duet.Delta

variable {α : Type*}

/-- `delta f (x, y) = (x · y, y · x)`. -/
def delta (f : α → α → α) (p : α × α) : α × α := (f p.1 p.2, f p.2 p.1)

/-- The core B: `(x·y)∘(y·x) = x` and `(x∘y)·(y∘x) = x`, with `·` = `f` and `∘` = `g`. -/
def B (f g : α → α → α) : Prop :=
  (∀ x y : α, g (f x y) (f y x) = x) ∧ (∀ x y : α, f (g x y) (g y x) = x)

theorem B_symm {f g : α → α → α} (h : B f g) : B g f := ⟨h.2, h.1⟩

theorem delta_swap (f : α → α → α) (p : α × α) : delta f p.swap = (delta f p).swap := rfl

/-- B says exactly that `delta g` is a two-sided inverse of `delta f`. -/
theorem B_iff_inverse (f g : α → α → α) :
    B f g ↔ Function.LeftInverse (delta g) (delta f) ∧ Function.RightInverse (delta g) (delta f) := by
  constructor
  · rintro ⟨h1, h2⟩
    refine ⟨fun p => ?_, fun p => ?_⟩
    · obtain ⟨x, y⟩ := p
      simp only [delta, h1]
    · obtain ⟨x, y⟩ := p
      simp only [delta, h2]
  · rintro ⟨h1, h2⟩
    refine ⟨fun x y => ?_, fun x y => ?_⟩
    · exact congrArg Prod.fst (h1 (x, y))
    · exact congrArg Prod.fst (h2 (x, y))

/-- Some operation `g` satisfies B with `f` iff `(x, y) ↦ (x·y, y·x)` is a bijection (Δ-bijectivity). -/
theorem exists_B_iff_bijective (f : α → α → α) :
    (∃ g : α → α → α, B f g) ↔ Function.Bijective (delta f) := by
  constructor
  · rintro ⟨g, hB⟩
    obtain ⟨hl, hr⟩ := (B_iff_inverse f g).1 hB
    exact ⟨hl.injective, hr.surjective⟩
  · intro hb
    obtain ⟨inv, hl, hr⟩ := Function.bijective_iff_has_inverse.1 hb
    -- the inverse commutes with the swap, because `delta f` does
    have hswap : ∀ q : α × α, inv q.swap = (inv q).swap := by
      intro q
      calc inv q.swap = inv (delta f (inv q)).swap := by rw [hr q]
        _ = inv (delta f (inv q).swap) := by rw [delta_swap]
        _ = (inv q).swap := hl _
    refine ⟨fun u v => (inv (u, v)).1, fun x y => ?_, fun x y => ?_⟩
    · show (inv (delta f (x, y))).1 = x
      rw [hl (x, y)]
    · show f (inv (x, y)).1 (inv (y, x)).1 = x
      have h1 : (inv (y, x)).1 = (inv (x, y)).2 := by
        have := hswap (x, y)
        rw [Prod.swap_prod_mk] at this
        rw [this, Prod.fst_swap]
      rw [h1]
      exact congrArg Prod.fst (hr (x, y))

/-- Under B, `(x∘y)·x = x` iff every left translation of `·` is idempotent. -/
theorem absorb₁_iff {f g : α → α → α} (hB : B f g) :
    (∀ x y : α, f (g x y) x = x) ↔ (∀ a b : α, f a (f a b) = f a b) := by
  constructor
  · intro h a b
    have := h (f a b) (f b a)
    rwa [hB.1 a b] at this
  · intro h x y
    have := h (g x y) (g y x)
    rwa [hB.2 x y] at this

/-- Under B, `x·(y∘x) = x` iff every right translation of `·` is idempotent. -/
theorem absorb₂_iff {f g : α → α → α} (hB : B f g) :
    (∀ x y : α, f x (g y x) = x) ↔ (∀ a b : α, f (f a b) b = f a b) := by
  constructor
  · intro h a b
    have := h (f a b) (f b a)
    rwa [hB.1 b a] at this
  · intro h x y
    have := h (g x y) (g y x)
    rwa [hB.2 x y] at this

/-- Under B, `(x·y)∘x = x` iff every left translation of `∘` is idempotent. -/
theorem absorb₃_iff {f g : α → α → α} (hB : B f g) :
    (∀ x y : α, g (f x y) x = x) ↔ (∀ a b : α, g a (g a b) = g a b) :=
  absorb₁_iff (B_symm hB)

/-- Under B, `x∘(y·x) = x` iff every right translation of `∘` is idempotent. -/
theorem absorb₄_iff {f g : α → α → α} (hB : B f g) :
    (∀ x y : α, g x (f y x) = x) ↔ (∀ a b : α, g (g a b) b = g a b) :=
  absorb₂_iff (B_symm hB)

/-- Under B, squaring is injective (Bonatto et al., Lemma 2.11, one half). -/
theorem sq_inj {f g : α → α → α} (hB : B f g) {x y : α} (h : f x x = f y y) : x = y := by
  have hx := hB.1 x x
  have hy := hB.1 y y
  rw [h] at hx
  exact hx.symm.trans hy

/-- Under B, two elements that commute are equal. -/
theorem comm_imp_eq {f g : α → α → α} (hB : B f g) {x y : α} (h : f x y = f y x) : x = y := by
  have hx := hB.1 x y
  have hy := hB.1 y x
  rw [h] at hx hy
  exact hx.symm.trans hy

end Duet.Delta
