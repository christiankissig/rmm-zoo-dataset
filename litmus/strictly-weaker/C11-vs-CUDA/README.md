# C11 → CUDA  (CUDA is strictly weaker)

**Distinguishing behaviour:** a release/acquire pair that synchronises under flat
C11 but, narrowed to `cuda::thread_scope_block` across two thread blocks, provides
no happens-before — so message passing leaks a stale value.

CUDA's `cuda::atomic` / `cuda::atomic_ref` mirror the C++11 atomics interface but
carry a **thread scope** template parameter (`thread_scope_block`,
`thread_scope_device`, `thread_scope_system`). At `thread_scope_system` it matches
C11; at a narrower scope a release/acquire orders only threads that share that
scope. `MP+relacq.litmus` is the message-passing shape with `release`/`acquire`,
which C11 forbids. `MP+block-relaxed.litmus` is the same program at
`thread_scope_block` with producer and consumer in *different* blocks, where the
synchronisation is vacuous and the outcome is allowed.

```sh
# CUDA at thread_scope_system (= flat C11): release/acquire synchronise
herd7 -c11 MP+relacq.litmus          # Never 0 2      (forbidden)
# CUDA at thread_scope_block across blocks: no cross-scope order (modelled relaxed)
herd7 -c11 MP+block-relaxed.litmus   # Sometimes 1 3  (allowed)
```

## What is and isn't machine-checked

herd7's C model has no scopes, so the CUDA side is modelled by its semantic
equivalent: a `thread_scope_block` release/acquire observed across two blocks
establishes no happens-before, i.e. `memory_order_relaxed` for that
synchronisation. The genuine `cuda::atomic_ref` source is in the header of
`MP+block-relaxed.litmus`. CUDA's scoped atomics are defined on, and lowered to,
the PTX memory model, which Lustig et al. formalise and machine-check.

**Reference:** Lustig, Sahasrabuddhe, Giroux, *A Formal Analysis of the NVIDIA PTX
Memory Consistency Model*, ASPLOS 2019 (DOI 10.1145/3297858.3304043); NVIDIA CUDA
C++ Programming Guide / `libcu++` (`cuda::atomic` thread scopes).
