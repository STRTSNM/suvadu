# Suvadu (சுவடு) ⚡

> *"Static analysis is a guess. Tracing is the truth."*

**Suvadu** (Tamil for *Footprint*) isn't just another transpiler. It’s a middle finger to the "Translation Gap"—that annoying loss of performance and soul that happens when you try to move logic from a high-level language to a low-level one.

Currently, Suvadu is proving its point by turning **Python into high-performance, hand-crafted C**. But that’s just the sandbox. The ultimate goal? Taking the battle-hardened logic of the **Linux Kernel** and transpiling it into clean, memory-safe **Rust** without losing the "Systems" feel.

---

## The "Trace" Philosophy

Most transpilers look at code as a dead pile of text. **Suvadu watches it live.** By hooking into the runtime, Suvadu "witnesses" your variables in motion. It doesn't guess if a number is a `float` or an `int`; it knows because it watched it happen. This "Tracer-Informed Logic" allows us to generate code that looks like a senior C dev wrote it at 3 AM:

* **Zero-Cost Primitives:** No generic "Object" bloat. If it behaves like an `int`, it becomes a raw C `int`.
* **Memory Forensics:** We don't do lazy `realloc`. We observe the max memory footprint during the trace and `malloc` the exact buffer size ahead of time.
* **Pointer Obsession:** Suvadu generates pointer arithmetic (`*(ptr + i)`) and aliasing logic instead of basic array indexing. It’s built for the cache, not just the compiler.

---

## Progress Log

| Status | Objective | Description |
| --- | --- | --- |
| Done | **Tracer-Informed Mapping** | Real-time type specialization for primitives. |
| Done | **Universal List Logic** | Native array management using `memcpy` and pre-allocation. |
| Done | **Human-Idiom Generation** | Emitting pointer-offset logic that mimics C systems code. |
| Done | **Zero-Bloat Headers** | Dynamically resolving only the headers you actually use. |
| (╥﹏╥) | **Functional Scoping** | Moving from a single `main()` to modular C headers and sources. |
| (╥﹏╥) | **Const-Correctness** | Auto-auditing variables to lock down memory safety. |
| 🌌 | **The Kernel Bridge** | Transpiling C-based Linux kernel subsystems to idiomatic Rust. |

---

## 🚀 Usage (PoC)

Write your logic in `code.py`, then let Suvadu footprint the execution:

1. **Trace & Transpile:**
```bash
python tracer.py > output.c
```


2. **Burn it to Binary:**
```bash
make output
```



---

## The Vision

I chose Python to C because they are the languages I live in right now, but Suvadu is an idea that transcends the language pair. It’s about building a bridge that preserves **intent**.

The future of Suvadu is taking the "footprints" of legacy C systems and automating their migration to Rust, ensuring the next generation of the Linux Kernel is as fast as the old one, but impossible to break.

