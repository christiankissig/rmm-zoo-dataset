// Store Buffering on the Java Memory Model.
//
// SC forbids the outcome r0 == 0 && r1 == 0: in any sequentially consistent
// interleaving at least one thread must run its load after the other's store.
// The JMM only guarantees SC for data-race-free programs.  Here x and y are
// *plain* (non-volatile) fields written and read concurrently -- a data race --
// so the JMM lets each thread's store be reordered past its load.  On any
// TSO-or-weaker machine (incl. x86) you will observe the SC-forbidden (0, 0).
//
// Build & run:
//   javac SB.java
//   java SB
//
// Uses a jcstress-style harness: two long-lived worker threads synchronised by
// a CyclicBarrier each round, so the racy accesses actually overlap.  Declaring
// x and y `volatile` removes the race and makes (0,0) vanish -- the DRF-SC
// guarantee.

import java.util.concurrent.CyclicBarrier;

public class SB {
    static int x, y;     // plain (racy) shared state
    static int r0, r1;   // observed reads

    public static void main(String[] args) throws Exception {
        final int ROUNDS = 2_000_000;
        final CyclicBarrier start = new CyclicBarrier(3);
        final CyclicBarrier end   = new CyclicBarrier(3);
        long both0 = 0, count00 = 0;

        Thread t0 = new Thread(() -> {
            for (int i = 0; i < ROUNDS; i++) {
                await(start);
                x = 1;
                r0 = y;
                await(end);
            }
        });
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < ROUNDS; i++) {
                await(start);
                y = 1;
                r1 = x;
                await(end);
            }
        });
        t0.setDaemon(true); t1.setDaemon(true);
        t0.start(); t1.start();

        for (int i = 0; i < ROUNDS; i++) {
            x = 0; y = 0;            // reset before the round
            await(start);            // release both workers
            await(end);             // wait for both to finish
            if (r0 == 0 && r1 == 0) {
                count00++;
                if (both0++ == 0)
                    System.out.printf(
                        "First SC-forbidden (r0=0, r1=0) at round %d%n", i);
            }
        }

        System.out.printf("rounds=%d  (0,0) seen %d times%n", ROUNDS, count00);
        System.out.println(count00 > 0
            ? "=> JMM allows a behaviour SC forbids (store/load reordered across the race)."
            : "=> No (0,0) this run; it is hardware-dependent -- re-run or try another machine.");
    }

    static void await(CyclicBarrier b) {
        try { b.await(); } catch (Exception e) { throw new RuntimeException(e); }
    }
}
