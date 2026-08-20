#!/usr/bin/env bash
# Re-decide every memalloy-provenance claim in models.json.
#
# The counterpart of litmus/kater/run.sh, and it carries a weaker guarantee by
# construction: memalloy searches for a distinguishing execution only up to an
# event bound, so a clean run is "no counterexample up to N events", not a
# proof. Every containment case below therefore records its N, and every edge it
# backs gets that N in its note.
#
# Unlike the kater suite this needs a memalloy CHECKOUT as well as an image: the
# comparator is built from source, and the models live in the checkout.
#
#     docker build -t memalloy-env -f Dockerfile .
#     git clone --recurse-submodules https://github.com/johnwickerson/memalloy
#     docker run --rm -v "$PWD/memalloy:/memalloy" -e LANG=C.UTF-8 memalloy-env \
#         bash -c 'make -C alloystar && make -C src; make -C archs; make -C mappings'
#     MEMALLOY=$PWD/memalloy ./run.sh
#
# Usage:  MEMALLOY=<checkout> ./run.sh          # run all
#         MEMALLOY=<checkout> ./run.sh -v       # also echo each invocation
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
VERBOSE=${1:-}
pass=0 fail=0

IMAGE=${MEMALLOY_IMAGE:-memalloy-env}
DOCKER=${DOCKER:-docker}
MEMALLOY=${MEMALLOY:-}

if ! command -v "$DOCKER" >/dev/null 2>&1; then
  echo "memalloy suite: $DOCKER not found -- install docker, or set DOCKER=podman" >&2
  exit 2
fi
if [ -z "$MEMALLOY" ] || [ ! -x "$MEMALLOY/comparator" ]; then
  echo "memalloy suite: set MEMALLOY to a built memalloy checkout (no ./comparator found)" >&2
  exit 2
fi
if ! "$DOCKER" image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "memalloy suite: image '$IMAGE' not built. Run:  $DOCKER build -t $IMAGE -f $HERE/Dockerfile $HERE" >&2
  exit 2
fi

# The cross-ISA comparisons need operands over a shared vocabulary, which the
# shipped arch-specific models are not. derive-hw-fragment.sh restricts x86tso
# and aarch64 to memalloy's generic Basic_HW arch; zoo_hw_rvwmo.cat is authored
# here, since memalloy ships no RISC-V model at all. Both land in the checkout's
# models/ directory, which is where the comparator looks.
"$HERE/derive-hw-fragment.sh" "$MEMALLOY" >/dev/null || {
  echo "memalloy suite: could not derive the Basic_HW fragment models" >&2; exit 2; }
cp "$HERE/models/zoo_hw_rvwmo.cat" "$MEMALLOY/models/"

# run <expected> <name> <comparator args...>
#   expected 1 = a distinguishing execution must exist (the witness direction)
#   expected 0 = none may exist up to the bound (the containment direction)
run() {
  local want="$1" name="$2"; shift 2
  [ "$VERBOSE" = "-v" ] && echo "  comparator $*"
  local out got
  # Serialise: the comparator names its results directory by the current second
  # and dies on a collision, so back-to-back runs must not share one.
  sleep 1
  out=$("$DOCKER" run --rm -v "$MEMALLOY":/memalloy -e LANG=C.UTF-8 "$IMAGE" \
        bash -c "./comparator $*" 2>&1)
  [ "$VERBOSE" = "-v" ] && echo "$out" | sed 's/^/    /'
  got=$(echo "$out" | sed -n 's/^Alloy found \([0-9]*\) solutions.*/\1/p' | head -1)
  if [ -z "$got" ]; then
    printf '  FAIL  %-52s %s\n' "$name" "no verdict: $(echo "$out" | tail -1 | cut -c1-60)"
    fail=$((fail+1)); return
  fi
  # "expect 1" means at least one, "expect 0" means exactly none.
  if { [ "$want" = 1 ] && [ "$got" -ge 1 ]; } || { [ "$want" = 0 ] && [ "$got" = 0 ]; }; then
    printf '  PASS  %-52s %s\n' "$name" "$got solution(s), as expected"; pass=$((pass+1))
  else
    printf '  FAIL  %-52s %s\n' "$name" "$got solution(s), expected $want"; fail=$((fail+1))
  fi
}

echo "=== cross-ISA, over the common Basic_HW fragment (see derive-hw-fragment.sh) ==="
run 1 "TSO -> ARMv8   witness      (<=4 events)" \
    -desc zoo_tso_arm8_A -arch HW -violates models/zoo_hw_tso.cat \
    -satisfies models/zoo_hw_arm8.cat -events 4 -expect 1
run 0 "TSO -> ARMv8   containment  (<=7 events)" \
    -desc zoo_tso_arm8_B -arch HW -violates models/zoo_hw_arm8.cat \
    -satisfies models/zoo_hw_tso.cat -events 7 -expect 0
run 1 "TSO -> RVWMO   witness      (<=4 events)" \
    -desc zoo_tso_rvwmo_A -arch HW -violates models/zoo_hw_tso.cat \
    -satisfies models/zoo_hw_rvwmo.cat -events 4 -expect 1
run 0 "TSO -> RVWMO   containment  (<=7 events)" \
    -desc zoo_tso_rvwmo_B -arch HW -violates models/zoo_hw_rvwmo.cat \
    -satisfies models/zoo_hw_tso.cat -events 7 -expect 0

echo "=== compilation: the mapping's soundness condition ==="
run 0 "OpenCL -> PTX  sound        (<=4/6 events)" \
    -desc zoo_ocl_ptx -arch OpenCL -arch2 PTX -fencerels \
    -violates models/opencl_scoped.cat -satisfies models/ptx_orig.cat \
    -mapping mappings/fences_as_relations/opencl_ptx.als -events 4 -events2 6 -expect 0

echo "=== controls: the search must be able to find things at these bounds ==="
run 1 "OpenCL -> PTX  buggy mapping IS caught" \
    -desc zoo_ocl_ptx_buggy -arch OpenCL -arch2 PTX -fencerels \
    -violates models/opencl_scoped.cat -satisfies models/ptx_cumul.cat \
    -mapping mappings/fences_as_relations/opencl_ptx_buggy.als -events 5 -events2 5 -expect 1
run 1 "ARMv8 not contained in RVWMO (fragment)" \
    -desc zoo_arm8_rvwmo -arch HW -violates models/zoo_hw_rvwmo.cat \
    -satisfies models/zoo_hw_arm8.cat -events 6 -expect 1

echo
echo "memalloy suite: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
