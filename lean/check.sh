#!/bin/sh
# Check every certificate with Lean, reusing the compiled packages of an existing Lake project mounted read-only
# at /reuse (Lean v4.35.0, Mathlib v4.35.0). No Lake, no downloads (pattern of curve-symmetry-lean/lean/check.sh).
set -eu
src=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
reuse=${REUSE:-/reuse}
[ -f "$reuse/.lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean" ] || { echo "no compiled Mathlib at $reuse" >&2; exit 2; }
paths=
for p in "$reuse"/.lake/packages/*; do
  [ -d "$p/.lake/build/lib/lean" ] && paths="${paths:+$paths:}$p/.lake/build/lib/lean"
done
build=$(mktemp -d)
mkdir -p "$build/Duet"
export LEAN_PATH="$build:$paths"
cd "$src"
for m in $(awk '/^import Duet\./ {print $2}' Duet.lean); do
  f=$(echo "$m" | tr . /).lean
  lean -DwarningAsError=true -o "$build/$(echo "$m" | tr . /).olean" "$f"
  echo "checked $m"
done
lean -DwarningAsError=true -o "$build/Duet.olean" Duet.lean
lean -DwarningAsError=true verification/Audit.lean
