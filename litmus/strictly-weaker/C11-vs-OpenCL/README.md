# C11 → OpenCL  (OpenCL is strictly weaker)

**Distinguishing behaviour:** a release/acquire pair that synchronises under flat
C11 but, narrowed to `memory_scope_work_group` across two work-groups, provides no
happens-before — so message passing leaks a stale value.

OpenCL 2.0 adds memory *scopes* (`work_item`, `work_group`, `device`,
`all_svm_devices`) on top of C11's orderings. At `all_svm_devices` scope it
coincides with C11; at any narrower scope a release/acquire only orders threads
that *share* that scope instance. `MP+relacq.litmus` is the standard
message-passing shape with a `release` store and an `acquire` load: C11 forbids
the flag-set / data-stale outcome. `MP+wg-relaxed.litmus` is the same program with
the synchronisation at `work_group` scope and the two threads in *different*
work-groups — where the release/acquire carry no order and the outcome is allowed.

```sh
# C11 (= OpenCL at all-svm-devices scope): release/acquire synchronise
herd7 -c11 MP+relacq.litmus      # Never 0 2      (forbidden)
# OpenCL at work_group scope across work-groups: no cross-scope order (modelled relaxed)
herd7 -c11 MP+wg-relaxed.litmus  # Sometimes 1 3  (allowed)
```

## What is and isn't machine-checked

herd7's bundled C model has no notion of scopes, so the OpenCL side is modelled by
its *semantic equivalent*: a `work_group`-scoped release/acquire observed across
two work-groups establishes no happens-before, which is precisely
`memory_order_relaxed` for that synchronisation (Batty, Donaldson & Wickerson,
POPL 2016, §2). The genuine scoped source is in the header of
`MP+wg-relaxed.litmus`. The C11 *forbids* direction is verified directly under
`-c11`; the OpenCL *allows* direction is verified on the relaxed model of the
cross-scope behaviour and cited to the OpenCL formalisation.

**Reference:** Batty, Donaldson, Wickerson, *Overhauling SC Atomics in C11 and
OpenCL*, POPL 2016 (DOI 10.1145/2837614.2837637); Alglave, Batty, Donaldson,
Gopalakrishnan, Ketema, Poetzl, Sorensen, Wickerson, *GPU Concurrency: Weak
Behaviours and Programming Assumptions*, ASPLOS 2015.
