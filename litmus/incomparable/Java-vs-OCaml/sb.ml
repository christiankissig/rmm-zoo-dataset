(* Store Buffering on the OCaml 5 (multicore) memory model.

   OCaml's model (Dolan, Sivaramakrishnan, Madhavapeddy, PLDI 2018) gives a
   "local data-race-freedom" guarantee: race-free code is SC, and even racy code
   has well-defined, bounded semantics (no out-of-thin-air, no crashes).  Like
   the JMM it is DRF-SC, but the two are *incomparable* on racy programs (see the
   README in this directory):

     - OCaml forbids value forgery: a racy read always returns a value actually
       written to that location -- a memory-safety property stronger than what
       the JMM gives for general object references.
     - The JMM pins down causality / happens-before in ways OCaml's operational
       model does not, and Java `volatile` vs OCaml `Atomic` differ in fencing.

   This program is the OCaml analogue of
   ../../strictly-weaker/SC-vs-Java/SB.java.  Two long-lived domains race on
   plain non-atomic [int array] cells, synchronised each round by a spin barrier
   built from [Atomic].  On x86/ARM you will observe the SC-forbidden (0, 0).
   Replacing the plain cells with [Atomic.t] removes the race and (0,0) vanishes
   -- the DRF-SC guarantee.

   Build & run (OCaml >= 5.0):
     ocaml sb.ml
     # or: ocamlfind ocamlopt sb.ml -o sb && ./sb              *)

let rounds = 2_000_000

(* shared, racy, non-atomic state in a mutable array *)
let m = Array.make 4 0
let x = 0 and y = 1 and r0 = 2 and r1 = 3

(* a tiny two-party sense-reversing barrier *)
let gate = Atomic.make 0          (* round number the workers may enter *)
let done0 = Atomic.make 0
let done1 = Atomic.make 0

let worker which =
  for i = 1 to rounds do
    while Atomic.get gate < i do Domain.cpu_relax () done;
    (if which = 0 then begin m.(x) <- 1; m.(r0) <- m.(y) end
                  else begin m.(y) <- 1; m.(r1) <- m.(x) end);
    Atomic.set (if which = 0 then done0 else done1) i
  done

let () =
  let d0 = Domain.spawn (fun () -> worker 0) in
  let d1 = Domain.spawn (fun () -> worker 1) in
  let both0 = ref 0 in
  for i = 1 to rounds do
    m.(x) <- 0; m.(y) <- 0;                 (* reset before releasing workers *)
    Atomic.set gate i;                       (* release this round *)
    while Atomic.get done0 < i || Atomic.get done1 < i do Domain.cpu_relax () done;
    if m.(r0) = 0 && m.(r1) = 0 then incr both0
  done;
  Domain.join d0; Domain.join d1;
  Printf.printf "rounds=%d  (0,0) seen %d times\n" rounds !both0;
  print_endline
    (if !both0 > 0
     then "=> OCaml's model allows the SC-forbidden (0,0) for racy non-atomic accesses."
     else "=> No (0,0) this run (hardware dependent); re-run or try another machine.")
