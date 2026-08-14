# SC -> BMM  (BMM is strictly weaker)

The **Buffered Memory Model (BMM)** is a pragmatic, TSO-style buffered model
proposed as a candidate semantics for Java (Demange et al., *Plan B: A Buffered
Memory Model for Java*, POPL 2013). Each thread owns a FIFO store buffer, so the
only relaxation over Sequential Consistency is **store->load reordering**: a load
may be satisfied from memory before a program-order-earlier store of the same
thread has drained out of the buffer. The authors prove the external DRF
theorem and the soundness of several transformations, and modify an
open-source JVM to preserve BMM at ~1% overhead on x86. Because the single
relaxation is precisely the x86/TSO store buffer, BMM coincides with TSO on this
behaviour -- the `TSO -> BMM` edge in `models.json` is `equivalent` -- while SC
forbids all reordering. So SC is strictly stronger: SC forbids the store-buffering
outcome that BMM permits.

## Direction -- BMM allows, SC forbids: store->load reordering (SB)

`SB.litmus` is the canonical store-buffering shape. P0 writes `x` then reads `y`;
P1 writes `y` then reads `x`. The outcome `0:r0=0 /\ 1:r0=0` (each thread's load
misses the other thread's store) requires both loads to be reordered before the
program-order-earlier stores. SC forbids it: a single global total order
consistent with program order cannot put both reads ahead of both writes. BMM
allows it: each store sits in its thread's buffer while the load reads the
still-zero memory.

## Running

BMM has no dedicated herd7 model, but its single relaxation is exactly TSO's, so
it is checked through the portable `models/abstract-tso.cat`; SC through
`models/abstract-sc.cat`:

```sh
herd7 -model models/abstract-sc.cat  strictly-weaker/SC-vs-BMM/SB.litmus   # Observation SB Never 0 3      (SC forbids)
herd7 -model models/abstract-tso.cat strictly-weaker/SC-vs-BMM/SB.litmus   # Observation SB Sometimes 1 3  (BMM allows)
```

Both are wired into `../../run.sh`.

**Reference:** Delphine Demange, Vincent Laporte, Lei Zhao, Suresh Jagannathan,
David Pichardie, Jan Vitek, *Plan B: A Buffered Memory Model for Java*, POPL 2013,
doi:10.1145/2429069.2429110. Lamport, *How to Make a Multiprocessor Computer That
Correctly Executes Multiprocess Programs*, IEEE TC 1979, doi:10.1109/TC.1979.1675439.
