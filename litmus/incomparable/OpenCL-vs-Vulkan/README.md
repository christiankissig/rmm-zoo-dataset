# OpenCL ↔ Vulkan  (incomparable)

OpenCL 2.0 and the Vulkan memory model are both scoped GPU-API models, but they
factor ordering differently, and neither contains the other.

## Direction 1 — Vulkan allows, OpenCL forbids: happens-before without visibility

Vulkan splits cross-thread ordering into **three** ingredients: happens-before,
**availability** (pushing a write out to a memory domain) and **visibility**
(pulling it into the reader). A bare scoped release/acquire establishes
happens-before but, across a memory domain, *not* availability/visibility — so
Vulkan still permits the message-passing stale read until the program issues
explicit `MakeAvailable` / `MakeVisible` operations. OpenCL has no such split: a
scoped acquire that synchronises with a release also makes the released writes
visible, so OpenCL **forbids** the same outcome. `MP+hb-no-visibility.litmus` is
this shape (the genuine SPIR-V sketch is in its header).

## Direction 2 — OpenCL allows, Vulkan forbids: scope-set / SVM differences

OpenCL exposes `work_item` / `work_group` / `device` / `all_svm_devices` scopes
and fine-grained **SVM** atomics whose host/device coherence has no exact Vulkan
counterpart; Vulkan instead names device/queue-family memory scopes and
storage-class semantics. Behaviours that hinge on OpenCL's SVM/all-devices scope
have no faithful Vulkan expression, giving the reverse separation and making the
two genuinely incomparable rather than one a subset of the other.

## What is and isn't machine-checked

herd7 ships neither model. The Vulkan memory model is specified executably in
**Alloy** (Khronos, led by Jade Alglave and collaborators), and OpenCL/Vulkan-class
models were compared mechanically with the **memalloy** tool
(<https://github.com/johnwickerson/memalloy>). The witness above is documented
with its expected verdicts and cited; the herd7 run only illustrates the shared
release/acquire shape.

**Reference:** *Vulkan Memory Model* (Khronos Vulkan Specification, Memory Model
chapter), 2018, <https://docs.vulkan.org/spec/latest/chapters/memorymodel.html>;
Batty, Donaldson, Wickerson, *Overhauling SC Atomics in C11 and OpenCL*, POPL 2016
(DOI 10.1145/2837614.2837637); Wickerson, Batty, Sorensen, Constantinides,
*Automatically Comparing Memory Consistency Models*, POPL 2017 (DOI
10.1145/3009837.3009838).
