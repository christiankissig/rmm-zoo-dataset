#!/usr/bin/env bash
# Run every herd7-checkable litmus test in this tree and check it against the
# expected outcome (Allowed = "Sometimes", Forbidden = "Never").
#
# Requires herdtools7 on PATH:   opam install herdtools7 && eval $(opam env)
# Usage:  ./run.sh            # run all
#         ./run.sh -v         # also echo each herd7 command
#
# The Java / OCaml / mordor tests are NOT run here (different toolchains); see the
# per-pair READMEs.  Tests that require a model herd7 does not ship (IMM,
# Promising) are listed at the end as SKIP with a pointer to their README.

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
M="$HERE/models"
VERBOSE=${1:-}
pass=0 fail=0

# check <name> <expected Never|Sometimes> <herd7 args...>
check() {
  local name="$1" expect="$2"; shift 2
  [ "$VERBOSE" = "-v" ] && echo "  herd7 $*"
  local got
  got=$(herd7 "$@" 2>/dev/null | awk '/^Observation/{print $3; exit}')
  if [ "$got" = "$expect" ]; then
    printf '  PASS  %-44s %s\n' "$name" "$got"; pass=$((pass+1))
  else
    printf '  FAIL  %-44s got=%s want=%s\n' "$name" "${got:-ERROR}" "$expect"; fail=$((fail+1))
  fi
}

echo "=== strictly weaker: test ALLOWED in the weaker model, FORBIDDEN in the stronger ==="

echo "[SC vs TSO]  SB"
check "SC forbids SB"          Never     -model sc.cat     strictly-weaker/SC-vs-TSO/SB.litmus
check "TSO allows SB"          Sometimes -model x86tso.cat strictly-weaker/SC-vs-TSO/SB.litmus

echo "[SC vs x86-TSO]  SB"
check "SC forbids SB"          Never     -model sc.cat     strictly-weaker/SC-vs-x86-TSO/SB.litmus
check "x86-TSO allows SB"      Sometimes -model x86tso.cat strictly-weaker/SC-vs-x86-TSO/SB.litmus

echo "[SC vs C11]  relaxed SB"
check "SC forbids SB"          Never     -model "$M/abstract-sc.cat" strictly-weaker/SC-vs-C11/SB-relaxed.litmus
check "C11 allows SB"          Sometimes -c11                        strictly-weaker/SC-vs-C11/SB-relaxed.litmus

echo "[TSO vs PSO]  MP (store-store)"
check "TSO forbids MP"         Never     -model "$M/abstract-tso.cat" strictly-weaker/TSO-vs-PSO/MP.litmus
check "PSO allows MP"          Sometimes -model "$M/abstract-pso.cat" strictly-weaker/TSO-vs-PSO/MP.litmus

echo "[TSO vs ARMv8]  LB (load-store)"
check "TSO forbids LB"         Never     -model "$M/abstract-tso.cat" strictly-weaker/TSO-vs-ARMv8/LB.litmus
check "ARMv8 allows LB"        Sometimes -model aarch64.cat           strictly-weaker/TSO-vs-ARMv8/LB.litmus

echo "[SC vs BMM]  SB (store->load): BMM is TSO-style buffered"
check "SC forbids SB"          Never     -model "$M/abstract-sc.cat"  strictly-weaker/SC-vs-BMM/SB.litmus
check "BMM allows SB"          Sometimes -model "$M/abstract-tso.cat" strictly-weaker/SC-vs-BMM/SB.litmus

echo "[TSO vs RMMOA]  MP (store->store): RMMOA coincides with PSO"
check "TSO forbids MP"         Never     -model "$M/abstract-tso.cat" strictly-weaker/TSO-vs-RMMOA/MP.litmus
check "RMMOA allows MP"        Sometimes -model "$M/abstract-pso.cat" strictly-weaker/TSO-vs-RMMOA/MP.litmus

echo "[TSO vs RVWMO]  MP (store-store)"
check "TSO forbids MP"         Never     -model "$M/abstract-tso.cat" strictly-weaker/TSO-vs-RVWMO/MP.litmus
check "RVWMO allows MP"        Sometimes -model riscv.cat             strictly-weaker/TSO-vs-RVWMO/MP.litmus

echo "[PSO vs RMO]  LB (load-store)"
check "PSO forbids LB"         Never     -model "$M/abstract-pso.cat" strictly-weaker/PSO-vs-RMO/LB.litmus
check "RMO allows LB"          Sometimes -model "$M/abstract-rmo.cat" strictly-weaker/PSO-vs-RMO/LB.litmus

echo "[RMO vs Coherence]  MP+addr"
check "RMO forbids MP+addr"    Never     -model "$M/abstract-rmo.cat"       strictly-weaker/RMO-vs-Coherence/MP+addr.litmus
check "Coherence allows MP+addr" Sometimes -model "$M/abstract-coherence.cat" strictly-weaker/RMO-vs-Coherence/MP+addr.litmus

echo "[RMO vs Alpha]  MP+dmb+addr (address dependency): RMO preserves it, Alpha does not"
check "RMO forbids MP+addr"    Never     -model "$M/abstract-rmo.cat"   strictly-weaker/RMO-vs-Alpha/MP+dmb+addr.litmus
check "Alpha allows MP+addr"   Sometimes -model "$M/abstract-alpha.cat" strictly-weaker/RMO-vs-Alpha/MP+dmb+addr.litmus

echo "[ARM vs Coherence]  MP+dmb+addr"
check "ARM forbids MP+addr"    Never     -model arm.cat                    strictly-weaker/ARM-vs-Coherence/MP+dmb+addr.litmus
check "Coherence allows MP+addr" Sometimes -model "$M/abstract-coherence.cat" strictly-weaker/ARM-vs-Coherence/MP+dmb+addr.litmus

echo "[POWER vs Coherence]  MP+sync+addr"
check "POWER forbids MP+addr"  Never     -model ppc.cat                    strictly-weaker/POWER-vs-Coherence/MP+sync+addr.litmus
check "Coherence allows MP+addr" Sometimes -model "$M/abstract-coherence.cat" strictly-weaker/POWER-vs-Coherence/MP+sync+addr.litmus

echo "[ARMv8 vs ARM]  WRC+addrs (non-multi-copy-atomic)"
check "ARMv7 allows WRC+addrs" Sometimes -model arm.cat     strictly-weaker/ARMv8-vs-ARM/WRC+addrs.arm.litmus
check "ARMv8 forbids WRC+addrs" Never    -model aarch64.cat strictly-weaker/ARMv8-vs-ARM/WRC+addrs.aarch64.litmus

echo "[RC11 vs C11]  IRIW+sc-fences"
check "RC11 forbids IRIW+scf"  Never     -model rc11.cat      strictly-weaker/RC11-vs-C11/IRIW+scfences.litmus
check "C11 (orig) allows IRIW+scf" Sometimes -model c11_orig.cat strictly-weaker/RC11-vs-C11/IRIW+scfences.litmus

echo "[RC11 vs C++20]  LB (thin-air): RC11 forbids, C++20 allows"
check "RC11 forbids LB"        Never     -model rc11.cat     strictly-weaker/RC11-vs-C++20/LB-relaxed.litmus
check "C++20 allows LB"        Sometimes -model c11_orig.cat strictly-weaker/RC11-vs-C++20/LB-relaxed.litmus

echo "[PSO vs POWER]  MP+sync+po (load-load): POWER allows, PSO forbids"
check "PSO forbids MP+sync+po" Never     -model "$M/abstract-pso.cat" strictly-weaker/PSO-vs-POWER/MP+sync+po.litmus
check "POWER allows MP+sync+po" Sometimes -model ppc.cat              strictly-weaker/PSO-vs-POWER/MP+sync+po.litmus

echo "[RC11 vs sMRD]  LB (load->store): RC11's acyclic(po|rf) is too strong; sMRD/C11 allow"
check "RC11 forbids LB"        Never     -model rc11.cat      strictly-weaker/RC11-vs-sMRD/LB.litmus
check "C11 allows LB (sMRD matches)" Sometimes -model c11_orig.cat strictly-weaker/RC11-vs-sMRD/LB.litmus

echo "[CRC vs C11]  MP (relaxed): C11 allows, CRC's relaxed-free fragment forbids"
check "CRC forbids MP (relacq)" Never     -c11 strictly-weaker/CRC-vs-C11/MP+relacq.litmus
check "C11 allows MP (relaxed)" Sometimes -c11 strictly-weaker/CRC-vs-C11/MP+relaxed.litmus

echo "[CSRA vs C11]  LB-oota (control-dep thin-air): C11 allows, CSRA forbids"
check "C11 allows LB-oota"     Sometimes -c11 strictly-weaker/CSRA-vs-C11/LB-oota.litmus

# SRA vs RA. Both cat models are authored here (models/{ra,sra}.cat), differing
# only in write-coherence vs strong-write-coherence, so the pair is bracketed by
# controls: a model that forbade or allowed everything would produce the same
# split. MP+relacq must be forbidden by both; IRIW must be allowed by both
# (Lahav & Boker Ex. 3.5 marks it allowed under RA and SRA alike).
echo "[SRA vs RA]  2+2W: RA's local mo/hb agreement vs SRA's global one"
check "SRA forbids 2+2W"       Never     -model "$M/sra.cat" strictly-weaker/SRA-vs-RA/2+2W.litmus
check "RA allows 2+2W"         Sometimes -model "$M/ra.cat"  strictly-weaker/SRA-vs-RA/2+2W.litmus
check "  control: RA forbids MP+relacq"  Never     -model "$M/ra.cat"  strictly-weaker/SRA-vs-RA/MP+relacq.litmus
check "  control: SRA forbids MP+relacq" Never     -model "$M/sra.cat" strictly-weaker/SRA-vs-RA/MP+relacq.litmus
check "  control: RA allows IRIW"        Sometimes -model "$M/ra.cat"  strictly-weaker/SRA-vs-RA/IRIW.litmus
check "  control: SRA allows IRIW"       Sometimes -model "$M/sra.cat" strictly-weaker/SRA-vs-RA/IRIW.litmus

# RA vs WRA. All three witnesses are single-location programs: WRA decides which of
# two writes to a location is the later by hb|loc rather than mo, and hb|loc is only
# partial, so WRA loses SC-per-location. sra.cat agrees with ra.cat throughout (the
# SRA/RA split is 2+2W, above) and is checked here to show the two axes are separate.
echo "[RA vs WRA]  Ex. 3.7: WRA has no SC-per-location"
check "RA forbids WW"           Never     -model "$M/ra.cat"  strictly-weaker/RA-vs-WRA/WW.litmus
check "WRA allows WW"           Sometimes -model "$M/wra.cat" strictly-weaker/RA-vs-WRA/WW.litmus
check "RA forbids Oscillating"  Never     -model "$M/ra.cat"  strictly-weaker/RA-vs-WRA/Oscillating.litmus
check "WRA allows Oscillating"  Sometimes -model "$M/wra.cat" strictly-weaker/RA-vs-WRA/Oscillating.litmus
check "RA forbids SF"           Never     -model "$M/ra.cat"  strictly-weaker/RA-vs-WRA/SF.litmus
check "WRA allows SF"           Sometimes -model "$M/wra.cat" strictly-weaker/RA-vs-WRA/SF.litmus
check "  SRA agrees with RA: WW"          Never -model "$M/sra.cat" strictly-weaker/RA-vs-WRA/WW.litmus
check "  SRA agrees with RA: Oscillating" Never -model "$M/sra.cat" strictly-weaker/RA-vs-WRA/Oscillating.litmus
check "  SRA agrees with RA: SF"          Never -model "$M/sra.cat" strictly-weaker/RA-vs-WRA/SF.litmus
# wra.cat's init ordering is load-bearing: without it weak-read-coherence can never
# fire against an initial value and WRA wrongly allows message passing, i.e. is not
# causally consistent. This is the control that catches that.
check "  control: WRA forbids MP+relacq" Never -model "$M/wra.cat" strictly-weaker/SRA-vs-RA/MP+relacq.litmus

echo "[SC vs SRA]  IRIW: SRA is the strongest of the family, still weaker than SC"
check "SC forbids IRIW"         Never     -model "$M/abstract-sc.cat" strictly-weaker/SC-vs-SRA/IRIW.litmus
check "SRA allows IRIW"         Sometimes -model "$M/sra.cat"         strictly-weaker/SC-vs-SRA/IRIW.litmus
check "  control: SC allows MP+relacq-ok"  Sometimes -model "$M/abstract-sc.cat" strictly-weaker/SC-vs-SRA/MP+relacq-ok.litmus
check "  control: SRA allows MP+relacq-ok" Sometimes -model "$M/sra.cat"         strictly-weaker/SC-vs-SRA/MP+relacq-ok.litmus

# Scoped GPU models. herd7 has no scoped architecture, so the weaker (scoped) side
# is modelled by its semantic equivalent: a release/acquire narrowed to a scope the
# two threads do NOT share carries no happens-before, i.e. it behaves as relaxed.
# The C11 (strong) side is checked directly under -c11. See each pair's README.
echo "[C11 vs OpenCL]  MP (work_group scope across work-groups)"
check "C11 forbids MP+relacq"      Never     -c11 strictly-weaker/C11-vs-OpenCL/MP+relacq.litmus
check "OpenCL allows MP (wg scope)" Sometimes -c11 strictly-weaker/C11-vs-OpenCL/MP+wg-relaxed.litmus

echo "[C11 vs CUDA]  MP (block scope across blocks)"
check "C11 forbids MP+relacq"       Never     -c11 strictly-weaker/C11-vs-CUDA/MP+relacq.litmus
check "CUDA allows MP (block scope)" Sometimes -c11 strictly-weaker/C11-vs-CUDA/MP+block-relaxed.litmus

echo "[C11 vs HRF]  MP (non-shared scopes = scoped race)"
check "C11 forbids MP+relacq"       Never     -c11 strictly-weaker/C11-vs-HRF/MP+relacq.litmus
check "HRF allows MP (scoped race)" Sometimes -c11 strictly-weaker/C11-vs-HRF/MP+scoped-relaxed.litmus

echo
echo "=== incomparable: a test allowed in one model, forbidden in the other ==="

echo "[ARM vs POWER]  SB+lwsync (POWER-only barrier): POWER allows"
check "POWER allows SB+lwsync" Sometimes -model ppc.cat               incomparable/ARM-vs-POWER/SB+lwsync.litmus

echo "[ARMv8 vs RVWMO]  SB+fence.tso (RISC-V-only barrier): RVWMO allows"
check "RVWMO allows SB+fence.tso" Sometimes -model riscv.cat          incomparable/ARMv8-vs-RVWMO/SB+fence.tso.litmus

echo "[C11 vs WJES]  TC7 (load->load reorder): C11 allows, WJES forbids"
check "C11 allows TC7"         Sometimes -c11 incomparable/C11-vs-WJES/TC7.litmus

echo "[C11 vs RMC]  MP (relaxed): C11 allows; RMC's VEDGE/XEDGE forbid"
check "C11 allows MP (relaxed)" Sometimes -c11 incomparable/C11-vs-RMC/MP+relaxed.litmus

# C++20 vs C11: two-sided. P0668 strengthens seq_cst (C++20 forbids IRIW+scf that
# C11 allows); P0982 weakens release sequences (C++11 forbids an RS outcome C++20
# allows, and C++20 forbids one C++11/17 allow). The repaired-SC direction is
# modelled with rc11.cat vs c11_orig.cat -- the cpp* models below all inherit
# RC11's repaired SC, so they cannot show the P0668 direction.
echo "[C++20 vs C11]  IRIW+sc-fences (P0668): C++20 forbids, C11 allows"
check "C++20 forbids IRIW+scf" Never     -model rc11.cat     incomparable/C++20-vs-C11/IRIW+scfences.litmus
check "C11 allows IRIW+scf"    Sometimes -model c11_orig.cat incomparable/C++20-vs-C11/IRIW+scfences.litmus

# Release-sequence axis, now mechanised with the cpp_memory_model cat suite
# (models/cpp/, vendored from gonzalobg/cpp_memory_model). From C++17 a release
# sequence is continued only by RMWs, no longer by later same-thread relaxed
# stores; cpp11/cpp17/cpp2w model C++11/17/20 and the rs/ family witnesses both
# directions. This supersedes the old RS+cpp20.litmus workaround, which simulated
# C++20 semantics inside the program because no C++20 model was on hand; cpp2w.cat
# is a genuine C++20 model.
echo "[C++20 vs C11]  release seq, dir A (C++11/17 allow, C++20 forbids): mp-rs-add-est-atomic"
check "C++11 allows (rs)"      Sometimes -model models/cpp/cpp11.cat cpp_memory_model/rs/mp-rs-add-est-atomic.litmus
check "C++17 allows (rs)"      Sometimes -model models/cpp/cpp17.cat cpp_memory_model/rs/mp-rs-add-est-atomic.litmus
check "C++20 forbids (rs)"     Never     -model models/cpp/cpp2w.cat cpp_memory_model/rs/mp-rs-add-est-atomic.litmus
echo "[C++20 vs C11]  release seq, dir B (C++11 forbids, C++20 allows -- now a race): RS.litmus"
check "C++11 forbids RS"       Never     -model models/cpp/cpp11.cat incomparable/C++20-vs-C11/RS.litmus
check "C++20 allows RS"        Sometimes -model models/cpp/cpp2w.cat incomparable/C++20-vs-C11/RS.litmus
echo "[C++ versions]  only C++17 allows the partial-RS outcome: mp-rs-st-eadd-atomics"
check "C++11 forbids"          Never     -model models/cpp/cpp11.cat cpp_memory_model/rs/mp-rs-st-eadd-atomics.cpp11.litmus
check "C++17 allows"           Sometimes -model models/cpp/cpp17.cat cpp_memory_model/rs/mp-rs-st-eadd-atomics.cpp11.litmus
check "C++20 forbids"          Never     -model models/cpp/cpp2w.cat cpp_memory_model/rs/mp-rs-st-eadd-atomics.cpp11.litmus

# New nodes C++17 and RC17 (the cpp_memory_model variants), each placed by a clean,
# by-construction witnessed strictly-weaker edge. C++17 sits below both C11 and RC17.
echo "[C11 vs C++17]  release-seq narrowing: C11 forbids, C++17 allows"
check "C11 forbids"            Never     -model models/cpp/cpp11.cat strictly-weaker/C11-vs-C++17/mp-rs-st-eadd-atomics.cpp11.litmus
check "C++17 allows"           Sometimes -model models/cpp/cpp17.cat strictly-weaker/C11-vs-C++17/mp-rs-st-eadd-atomics.cpp11.litmus
echo "[RC11 vs RC17]  release-seq narrowing: RC11 forbids, RC17 allows"
check "RC11 forbids"           Never     -model models/cpp/rc11.cat  strictly-weaker/RC11-vs-RC17/mp-rs-add-est-atomic.litmus
check "RC17 allows"            Sometimes -model models/cpp/rc17.cat  strictly-weaker/RC11-vs-RC17/mp-rs-add-est-atomic.litmus
echo "[RC17 vs C++17]  no-thin-air axiom: RC17 forbids LB, C++17 allows"
check "RC17 forbids LB"        Never     -model models/cpp/rc17.cat  strictly-weaker/RC17-vs-C++17/LB-relaxed.litmus
check "C++17 allows LB"        Sometimes -model models/cpp/cpp17.cat strictly-weaker/RC17-vs-C++17/LB-relaxed.litmus

echo
echo "Summary: $pass passed, $fail failed."
echo
echo "Not run here (see per-pair READMEs):"
echo "  strictly-weaker/SC-vs-Java   -> javac SB.java && java SB"
echo "  strictly-weaker/MRD-vs-C11   -> mordor (forbids OOTA); C11 permits it"
echo "  incomparable/Java-vs-OCaml   -> java SB / ocaml sb.ml + literature"
echo "  incomparable/RC11-vs-IMM     -> needs the IMM Coq artifact (not in herd7)"
echo "  incomparable/C11-vs-Promising-> needs the Promising tool (not in herd7)"
echo "  strictly-weaker/HRF-vs-ScopedC11 -> scope-matching rule; memalloy + literature"
echo "  incomparable/PTX-vs-AMDGPU   -> no scoped arch in herd7; memalloy + literature"
echo "  incomparable/OpenCL-vs-Vulkan-> no scoped arch in herd7; memalloy + literature"
echo "  strictly-weaker/MRD-vs-sMRD  -> mordor-family; false-dependency optimisation (cited)"
echo "  strictly-weaker/RC11-vs-JAM  -> JAM Coq artifact; thin-air at plain mode (cited)"
echo "  strictly-weaker/Weakestmo-vs-C11 -> event-structure model (cited; reclassified from incomparable)"
echo "  incomparable/Java-vs-OHMM    -> JMM/OHMM operational models (cited)"
echo "  incomparable/C11-vs-{GOS,JSMM,RAO,TSC} -> survey research models (cited / model-level)"
echo "  incomparable/Promising-vs-{Weakestmo,CSRA} -> Promising + event-structure artifacts (cited)"
[ "$fail" -eq 0 ]
