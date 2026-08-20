#!/usr/bin/env bash
# Re-check every kater-provenance claim in models.json.
#
# Each query in queries/ is one machine-checkable half of one edge: the
# containment direction of a strictly_weaker edge, or the soundness condition of
# a compilation edge. kater decides them by language inclusion, unbounded, so a
# pass here is a proof about the .kat renderings named in the query -- not a
# no-counterexample-up-to-N result. Every query in queries/ is expected to HOLD;
# the ones that do not are parked in open/ with a note, and are not run here.
#
# Requires docker and the kater image (pull is ~700MB):
#     docker pull genmc/kater
#
# Usage:  ./run.sh          # run all
#         ./run.sh -v       # also echo each kater invocation and its output
#
# The queries include kater's own kat/*.kat model definitions from inside the
# image rather than vendoring them: they are GPL-3.0, this dataset is BSD-3, and
# the image is the version of record anyway. That is why the mount lands at
# /root/kater/zoo and the includes read ../../kat/ -- kater resolves an include
# against the directory of the file it was handed.

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
VERBOSE=${1:-}
pass=0 fail=0

# Pinned by digest: kater's verdicts are the evidence for edges in models.json,
# so the tool that produced them is pinned exactly like herd7 is in litmus/run.sh.
# Bump deliberately, re-running this suite first.
IMAGE=${KATER_IMAGE:-genmc/kater@sha256:0542cb49effeb47129fd09a93cb96794ac91382c451479dc963e584a01edbe07}
DOCKER=${DOCKER:-docker}

if ! command -v "$DOCKER" >/dev/null 2>&1; then
  echo "kater suite: $DOCKER not found -- install docker, or set DOCKER=podman" >&2
  exit 2
fi
if ! "$DOCKER" image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "kater suite: image not present locally. Run:  $DOCKER pull ${IMAGE%@*}" >&2
  exit 2
fi

# LKMM is not usable straight from the image: kat/lkmm2.kat is written over
# internal (-imm) relations, which kater rejects in every mode, so it does not
# load at all. derive-lkmm.sh restates it over kater's builtin theory into a
# scratch directory mounted alongside the zoo -- generated per run rather than
# vendored, because it is a derivative of a GPL-3.0 file and this dataset is
# BSD-3. Queries reach it at ../../derived/.
DERIVED=$(mktemp -d)
trap 'rm -rf "$DERIVED"' EXIT
if ! ./derive-lkmm.sh "$DERIVED/lkmm.kat" "$IMAGE"; then
  echo "kater suite: could not derive the LKMM model" >&2
  exit 2
fi

# check <name> <query file, relative to this directory>
check() {
  local name="$1" query="$2"
  [ "$VERBOSE" = "-v" ] && echo "  kater zoo/$query"
  local out rc
  out=$("$DOCKER" run --rm -v "$HERE":/root/kater/zoo:ro \
        -v "$DERIVED":/root/kater/derived:ro --workdir /root/kater \
        --entrypoint /root/kater/Release/kater "$IMAGE" "zoo/$query" 2>&1)
  rc=$?
  [ "$VERBOSE" = "-v" ] && [ -n "$out" ] && echo "$out" | sed 's/^/    /'
  # An assertion kater could not use is worse than one that fails: it prints a
  # warning, drops the premise, and still exits 0 -- so a "proof" could rest on
  # something the tool silently ignored. Treat it as a failure.
  if echo "$out" | grep -q "Ignoring unsupported assumption"; then
    printf '  FAIL  %-46s %s\n' "$name" "assumption silently dropped"; fail=$((fail+1)); return
  fi
  case $rc in
    0) printf '  PASS  %-46s %s\n' "$name" "holds"; pass=$((pass+1)) ;;
    6) printf '  FAIL  %-46s %s\n' "$name" "refuted: $(echo "$out" | sed -n 's/^Counterexample: //p' | head -1)"; fail=$((fail+1)) ;;
    *) printf '  FAIL  %-46s %s\n' "$name" "kater error (exit $rc): $(echo "$out" | head -1)"; fail=$((fail+1)) ;;
  esac
}

# refute <name> <query file> -- the mirror of check(): a control that is only
# doing its job while it FAILS. Used to keep the compilation targets honest: a
# target whose ordering relation has grown to contain po makes every query
# against it hold vacuously, and a suite of nothing but expected passes cannot
# tell that apart from a proof.
refute() {
  local name="$1" query="$2"
  [ "$VERBOSE" = "-v" ] && echo "  kater zoo/$query   (expected to be refuted)"
  local out rc
  out=$("$DOCKER" run --rm -v "$HERE":/root/kater/zoo:ro \
        -v "$DERIVED":/root/kater/derived:ro --workdir /root/kater \
        --entrypoint /root/kater/Release/kater "$IMAGE" "zoo/$query" 2>&1)
  rc=$?
  [ "$VERBOSE" = "-v" ] && [ -n "$out" ] && echo "$out" | sed 's/^/    /'
  case $rc in
    6) printf '  PASS  %-46s %s\n' "$name" "refuted, as it must be"; pass=$((pass+1)) ;;
    0) printf '  FAIL  %-46s %s\n' "$name" "HOLDS -- target is degenerate, queries against it are vacuous"; fail=$((fail+1)) ;;
    *) printf '  FAIL  %-46s %s\n' "$name" "kater error (exit $rc): $(echo "$out" | head -1)"; fail=$((fail+1)) ;;
  esac
}

echo "=== strictly weaker: the CONTAINMENT half (strictness stays with the litmus witness) ==="
check "SC -> TSO      (tso <= sc+)"           queries/strictly-weaker-SC-vs-TSO.kat
check "SC -> C11      (psc, coherence)"       queries/strictly-weaker-SC-vs-C11.kat
check "RC11 -> C11    (psc, coherence)"       queries/strictly-weaker-RC11-vs-C11.kat
check "SC -> LKMM     (hb, prop;ppo*, coherence)" queries/strictly-weaker-SC-vs-LKMM.kat

echo "=== compilation: the mapping's soundness condition ==="
check "IMM -> x86-TSO (psc <= tso*)"          queries/compilation-IMM-vs-x86-TSO.kat
check "IMM -> ARMv8   (psc <= ob*)"           queries/compilation-IMM-vs-ARMv8.kat

echo "=== controls: the compilation targets must not contain po (else the above is vacuous) ==="
refute "x86-TSO not degenerate (po <= tso+)"  controls/non-degenerate-x86-TSO.kat
refute "ARMv8 not degenerate   (po <= ob+)"   controls/non-degenerate-ARMv8.kat

echo
echo "kater suite: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
