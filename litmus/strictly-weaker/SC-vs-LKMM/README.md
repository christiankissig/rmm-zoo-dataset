# SC → LKMM  (LKMM is strictly weaker)

The Linux Kernel Memory Model is a deliberately *weak* virtual architecture: it
must allow at least everything the underlying CPUs (x86, ARM, POWER, RISC-V)
allow, so that kernel code proven correct under LKMM is correct everywhere.
Consequently it permits reorderings that Sequential Consistency forbids.

## The witness — `SB.litmus`

Classic store-buffering on plain `*_ONCE` accesses with no barrier between the
store and the load in either thread:

```sh
herd7 -model linux-kernel.cat SB.litmus    # Sometimes 0:r0=0 1:r1=0  (allowed)
```

Under SC the outcome `r0=0 /\ r1=0` is **Never** — a total order over all four
accesses cannot leave both reads seeing the initial value. Under LKMM it is
**Sometimes**: the model only orders the store before the load when an explicit
`smp_mb()` (or a release/acquire pair) is inserted. So every SC behaviour is an
LKMM behaviour, but not vice versa — LKMM is strictly weaker.

Inserting `smp_mb()` between the store and load in both threads (`SB+mbonceonces`)
restores `Never`, confirming the relaxation is exactly the missing full barrier.

**Reference:** Alglave, Maranget, McKenney, Parri, Stern, *Frightening Small
Children and Disconcerting Grown-ups: Concurrency in the Linux Kernel*,
ASPLOS 2018.
