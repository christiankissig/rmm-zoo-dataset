# Toolchain for building and running memalloy (Wickerson et al., POPL 2017).
# memalloy targets an old stack (JDK 8, OCaml ~4.07, ant); this image supplies it
# so the comparator runs without touching the host. Verified working: Alloy* builds
# (dist/alloy4.2.jar), the OCaml `comparator` binary builds, and a smoke comparison
# returns a solution.
#
#   docker build -t memalloy-env -f Dockerfile .
#   git clone --recurse-submodules https://github.com/johnwickerson/memalloy
#   docker run --rm -v "$PWD/memalloy:/memalloy" -e LANG=C.UTF-8 memalloy-env bash -c '\
#       make -C alloystar && make -C src ; \
#       ./comparator -desc smoke -arch C -violates models/sc.cat \
#         -satisfies models/c11_nodrf.cat -satisfies models/c11_normws.cat \
#         -satisfies models/c11_onlysc.cat -events 4 -expect 1 '
#
# Notes learned the hard way:
#  * LANG=C.UTF-8 is required, else javac fails on a non-ASCII char in an Alloy*
#    source comment ("unmappable character for encoding ASCII").
#  * `make -C src` builds every binary, then fails on its `doc` target (needs
#    `python`); the `comparator` binary is already produced before that, so ignore
#    the doc error (or add python). Do NOT run the top-level `make comparator`
#    target — it overwrites the working OCaml binary with a stale Python 2 wrapper.
#  * The OCaml comparator invokes alloystar/dist/alloy4.2.jar directly, so no
#    Python is needed for the core search; the default sat4j solver is pure Java.
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive TZ=UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-8-jdk ant graphviz make ca-certificates \
      ocaml-nox ocaml-findlib ocamlbuild libxml-light-ocaml-dev \
      python3 python-is-python3 \
 && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
ENV OS=amd64-linux JAVA_HEAP_SIZE=3g LANG=C.UTF-8 LC_ALL=C.UTF-8
WORKDIR /memalloy
