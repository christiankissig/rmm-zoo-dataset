# C11 <-> JSMM  (incomparable)

The **JavaScript Memory Model (JSMM)** (mechanised and repaired by Watt et al.,
PLDI 2020) is built on the C11 model and, like C11, *suffers the thin-air
problem* -- so out-of-thin-air does **not** separate them. They are incomparable
for two other reasons: JavaScript has **no undefined behaviour** (racy
non-atomic accesses get a defined semantics, where C11 makes them catch-fire UB),
and JavaScript's shared memory is a `SharedArrayBuffer` -- a linear byte buffer --
so JSMM supports **mixed-size accesses** that C11 cannot express.

## Direction 1 -- C11 allows (catch-fire), JSMM forbids: the racy non-atomic access

`MP+race.litmus` is the paper's Fig. 6 shape: a non-atomic ("Unordered") access
races SeqCst atomics on the same location. C11 declares the data race **undefined
behaviour** -- catch-fire -- so it vacuously "allows" the outcome (and every
other). JSMM gives the racy access a defined, byte-level (`reads-byte-from`)
semantics, and its SC-atomics validity rule pins the access in the total order,
**forbidding** the witness. So an outcome C11 admits only by giving up (UB) is one
JSMM positively rules out.

(The exact Fig. 6 outcome is what the paper's later *ARMv8 repair* re-weakens to
allow; the FORBID verdict here is the original/spec-level JSMM as of PLDI 2020.)

## Direction 2 -- JSMM allows, C11 cannot express: mixed-size tearing

The paper's Fig. 14: a 16-bit view over a `SharedArrayBuffer` is read racily while
another agent writes `0x0101`. JSMM's byte-wise `reads-byte-from` lets the 16-bit
read assemble byte 0 from the write (`0x01`) and byte 1 from the zero-initialised
buffer (`0x00`), yielding `0x0001` -- a value no agent ever wrote as a unit. C11
has no mixed-size accesses (its locations are discrete and typed), so it cannot
even express the program; the nearest mixed-size C11 extension (Flur et al.) makes
such a race UB rather than a defined torn value. This is the cleanest
JSMM-allows / C11-cannot-express direction.

## Running

Neither direction is machine-run. herd7's `-c11` does not implement catch-fire
(it models the racy access as a plain write, so it cannot reproduce the
C11-UB-vs-JSMM-defined distinction), and herd7 has no mixed-size / byte-level
model for Direction 2. Both verdicts are **cited** from the mechanised JSMM. The
`MP+race.litmus` file documents the Direction-1 program shape only.

**Reference:** Conrad Watt, Christopher Pulte, Anton Podkopaev, Guillaume
Barbier, Stephen Dolan, Shaked Flur, Jean Pichon-Pharabod, Shu-yu Guo, *Repairing
and Mechanising the JavaScript Relaxed Memory Model*, PLDI 2020,
doi:10.1145/3385412.3385973 (§1.3, Fig. 6, Fig. 14). C11: Mark Batty et al.,
*Mathematizing C++ Concurrency*, POPL 2011, doi:10.1145/1926385.1926394.
