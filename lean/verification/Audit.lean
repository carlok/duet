import Duet
import Lean.Util.CollectAxioms

/-! Dependency audit, as in curve-symmetry-lean: every declaration in the namespace `Duet` may use only the
axioms propext, Classical.choice and Quot.sound (no native_decide, no sorry). -/

open Lean in
run_cmd do
  let allowed : Array Name := #[`propext, `Classical.choice, `Quot.sound]
  let env ← getEnv
  let mut checked : Nat := 0
  for (name, _) in env.constants.toList do
    if (`Duet).isPrefixOf (privateToUserName name) then
      let axioms ← collectAxioms name
      for axiomName in axioms do
        unless allowed.contains axiomName do
          throwError "Forbidden axiom {axiomName} in {name}"
      checked := checked + 1
  if checked == 0 then
    throwError "Empty audit: the certificates were not loaded"
  logInfo m!"Axiom audit passed: {checked} declarations; allowlist propext, Classical.choice, Quot.sound"
