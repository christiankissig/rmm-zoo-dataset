#!/usr/bin/env bash
# Derive abstract Basic_HW models from memalloy's arch-specific ones.
#
# Why: the zoo's TSO -> ARMv8 and TSO -> RVWMO edges are cross-ISA, and
# memalloy's comparator takes ONE -arch for both operands. models/x86tso.cat is
# tagged "X86" and models/aarch64.cat is tagged "ARM8", so they cannot be handed
# to the same run: the two models do not share a vocabulary of events, which is
# the same obstacle kater hits on the identical pair.
#
# memalloy does have a common vocabulary -- Basic_HW, tag "HW", archs/exec_H.als
# -- carrying reads, writes, po, rf, co, fr, the three dependency relations and
# the atomicity relation, but NO fences and no acquire/release annotations. That
# is the common fragment, and restricting to it is what makes the comparison
# well-posed rather than a category error.
#
# The restriction is mechanical, and deliberately so: every arch-specific term
# is dropped, and every one of them is EMPTY on the fragment anyway (no fence
# events => mfence, dmb, dmbld, dmbst, isb are empty; no annotations => SCACQ,
# SCREL are empty). So the derived models are exact restrictions of the shipped
# ones, not weakened approximations -- and the script, not prose, is the record
# of what was dropped.
#
# Generated rather than committed: models/x86tso.cat is LGPL (from herd) and
# this dataset is BSD-3, the same reason litmus/kater/derive-lkmm.sh generates
# its operand instead of vendoring it.
#
# Usage:  ./derive-hw-fragment.sh MEMALLOY_CHECKOUT
set -eu
MEM=${1:?usage: derive-hw-fragment.sh MEMALLOY_CHECKOUT}
[ -f "$MEM/models/x86tso.cat" ] || { echo "not a memalloy checkout: $MEM" >&2; exit 2; }

# ---- TSO ------------------------------------------------------------------
# From models/x86tso.cat: retag X86 -> HW, and drop `mfence` from hb. The LOCKED
# / implied terms stay: `atom` is a Basic_HW relation, so locked RMWs are in the
# fragment.
sed -e 's/^"X86"$/"HW"/' \
    -e 's/^let hb = mfence | implied/let hb = implied/' \
    "$MEM/models/x86tso.cat" > "$MEM/models/zoo_hw_tso.cat"

# ---- ARMv8 ----------------------------------------------------------------
# From models/aarch64.cat: retag ARM8 -> HW, drop the two dob terms that mention
# isb, drop bob entirely (every one of its terms is a fence or an SCACQ/SCREL
# annotation), and drop the aob term ranged on SCACQ.
sed -e 's/^"ARM8"$/"HW"/' \
    -e '/((ctrl & isb) | addr; isb); \[R\]/d' \
    -e 's/^    | \[range(atom)\]; rfi; \[SCACQ\].*$//' \
    -e '/^let bob = dmb$/,/^    | po; \[SCREL\]; coi$/d' \
    -e '/^    | bob$/d' \
    "$MEM/models/aarch64.cat" > "$MEM/models/zoo_hw_arm8.cat"

for f in zoo_hw_tso zoo_hw_arm8; do
  # Nothing arch-specific may survive: a leftover fence or annotation name would
  # not resolve against exec_H.als and the run would fail confusingly later.
  if awk '/\(\*/{c=1} !c; /\*\)/{c=0}' "$MEM/models/$f.cat" \
     | grep -qE '\b(mfence|dmb|dmbld|dmbst|isb|SCACQ|SCREL)\b'; then
    echo "derive-hw-fragment.sh: arch-specific vocabulary survived in $f.cat" >&2
    exit 1
  fi
done
echo "derived: models/zoo_hw_tso.cat models/zoo_hw_arm8.cat"
