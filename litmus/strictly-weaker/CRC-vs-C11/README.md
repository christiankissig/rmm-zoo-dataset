# CRC -> C11  (C11 is strictly weaker)

**Compositional Relaxed Concurrency (CRC)** (Dodds, Batty, Gotsman, *Compositional
Verification of Compiler Optimisations on Relaxed Memory*, ESOP 2018) is a
semantics for a *fragment* of C11: non-atomic accesses with catch-fire semantics,
release/acquire atomics, and sequentially-consistent fences. It deliberately
**omits relaxed atomics** "to avoid well-known problems with thin-air values," and
its SC fences are taken stronger than C11's. Because CRC's fragment cannot even
express the relaxed accesses through which C11 admits message-passing and
thin-air behaviour, every behaviour of a CRC program is also a C11 behaviour while
C11 has extra ones CRC forbids. So CRC is strictly stronger -- C11 is strictly
weaker.

## Direction -- C11 allows, CRC forbids: relaxed message passing

The separating shape is plain message passing (the paper's Fig. 1 / Fig. 3),
stale-data outcome `r0=1 /\ r1=0`:

* `MP+relaxed.litmus` -- writer and reader use **relaxed** atomics. C11 **allows**
  the outcome: relaxed accesses carry no happens-before, so the writer's two
  stores (and the reader's two loads) may be observed out of order. `herd7 -c11`
  => `Sometimes`. CRC has no relaxed accesses, so this program is outside CRC's
  language altogether.
* `MP+relacq.litmus` -- the same shape with the **strongest atomics CRC offers**,
  release/acquire. The release/acquire pair forces happens-before from the data
  write to the data read, making the stale-data outcome a coherence violation:
  CRC **forbids** it, as does flat C11 on this annotation. `herd7 -c11` => `Never`.

The contrast between the two files is exactly the gap: a behaviour C11 exposes
through relaxed atomics that CRC's relaxed-free, thin-air-free fragment excludes.
(CRC additionally strengthens SC fences over C11's, a second source of CRC ⊊ C11;
the paper states this at the model level and ships no dedicated SC-fence litmus,
so it is noted but not exhibited here.)

## Running

Both sides run in herd7 under the bundled C11 model; CRC's relaxed-free fragment
is represented by its release/acquire (strongest) annotation:

```sh
herd7 -c11 strictly-weaker/CRC-vs-C11/MP+relacq.litmus    # Observation MP+relacq Never 0 2      (CRC / C11-relacq forbid)
herd7 -c11 strictly-weaker/CRC-vs-C11/MP+relaxed.litmus   # Observation MP+relaxed Sometimes 1 3 (C11 relaxed allows)
```

Both are wired into `../../run.sh`. CRC has no standalone herd7 model; this is the
same modelling device used for the scoped-GPU `C11 -> {OpenCL,CUDA,HRF}` pairs
(strong side via release/acquire, weak side via the relaxed equivalent), only with
the strength order reversed because here the fragment model is the *stronger* one.

**Reference:** Mike Dodds, Mark Batty, Alexey Gotsman, *Compositional Verification
of Compiler Optimisations on Relaxed Memory*, ESOP 2018,
doi:10.1007/978-3-319-89884-1_36 (arXiv:1802.05918) -- §3.1 Fig. 1 (MP), §3.5
Fig. 3, §3.7 "Differences from C11" (omits relaxed and SC accesses; SC fences
stronger than C11). C11: Mark Batty, Scott Owens, Susmit Sarkar, Peter Sewell,
Tjark Weber, *Mathematizing C++ Concurrency*, POPL 2011, doi:10.1145/1926385.1926394.
