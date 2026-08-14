# SC → Java  (the JMM is strictly weaker)

**Distinguishing behaviour:** store→load reordering across a data race.

herd7 has no Java model, so this edge is demonstrated with a real JVM program,
`SB.java`. The Java Memory Model guarantees SC only for *data-race-free*
programs. `SB.java` deliberately races on two plain (non-`volatile`) fields in
the store-buffering shape, so the JMM permits each thread's store to be reordered
past its load — producing the `(0,0)` that SC forbids.

```sh
javac SB.java
java SB
```

Expected output (the round number varies; on a TSO/weaker machine `(0,0)` shows
up within a couple of million rounds):

```
First SC-forbidden (r0=0, r1=0) at round 1892815
rounds=2000000  (0,0) seen 1 times
=> JMM allows a behaviour SC forbids (store/load reordered across the race).
```

It uses a jcstress-style barrier harness so the racy accesses actually overlap.
Declaring `x` and `y` `volatile` removes the race and the `(0,0)` outcome
vanishes — the JMM's DRF-SC guarantee. For rigorous, statistically-controlled
runs use [jcstress](https://github.com/openjdk/jcstress); this standalone program
is enough to *exhibit* the behaviour.

**Reference:** Manson, Pugh, Adve, *The Java Memory Model*, POPL 2005; JSR-133.
