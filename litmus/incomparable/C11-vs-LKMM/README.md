# C11 ↔ LKMM  (incomparable — different primitive sets)

C11 and the Linux Kernel Memory Model both sit at the language level above the
hardware, but neither one contains the other. The incomparability is **not** a
reordering difference on a shared instruction set (as with ARM ↔ POWER); it is
that each model has synchronisation primitives the other cannot express.

## LKMM has, C11 lacks — RCU (`RCU.litmus`)

LKMM models RCU directly: `rcu_read_lock()`/`rcu_read_unlock()` read-side
critical sections and `synchronize_rcu()` grace periods, with the fundamental
guarantee that a grace period orders pre-existing read-side sections against
later updates.

```sh
herd7 -model linux-kernel.cat RCU.litmus    # Never 1:r0=1 1:r1=0  (forbidden)
```

C11 has no RCU primitive at all — the test cannot be written in the C11 model,
let alone reproduce this guarantee. (Userspace RCU emulates it with fences, but
that is a library, not the C11 model.)

## C11 has, LKMM lacks — per-object SC atomics

Conversely, C11 provides `memory_order_seq_cst` atomics that participate in a
single global total order per the SC axioms (as repaired in RC11). LKMM has no
equivalent per-object sequentially-consistent access; its strongest ordering is
assembled from `smp_mb()` full barriers, which give a different (and not
strictly comparable) guarantee.

Because each model can state an ordering the other cannot, neither is a subset
of the other → **incomparable**.

**Reference:** Alglave, Maranget, McKenney, Parri, Stern, *Frightening Small
Children and Disconcerting Grown-ups: Concurrency in the Linux Kernel*,
ASPLOS 2018; Batty, Owens, Sarkar, Sewell, Weber, *Mathematizing C++
Concurrency*, POPL 2011.
