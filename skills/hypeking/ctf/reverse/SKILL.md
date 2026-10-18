---
name: ctf-reverse
description: "CTF reversing checklist — stack/register VM bytecode interpreters, custom SPN/AES-like ciphers, xorshift/PRNG feedback ciphers, anti-debug corruption, CPython .pyc 3.11-3.13 disassembly, Java/JAR, packed/stripped ELF. Trigger: reverse challenge, reversing, vm bytecode, spn, custom cipher, pyc, cpython dis, jar, decompile, anti-debug, strings challenge, elf stripped."
---

# CTF reverse — checklist

Rule of the pack: **never guess a transform you can read out of the binary.**
Every wasted hour in the CTV transcript was a guessed constant, not a missing tool.

## 0. Triage

```bash
file *                    # ELF? pyc? JAR? .NET? PE?
strings -n 6 * | head -50 # flag-ish strings, but assume decoys exist
readelf -h -S * | head    # stripped? PIE? sections missing?
```

`stringson`: four candidate strings, only one had a non-decoy symbol name — **symbol
names are the cheapest oracle.** Prefer named functions over string literals.

## 1. Which target class

| Signal | Path |
|---|---|
| tiny ELF, prints one message | `strings` may just win — check first |
| large switch loop over a byte array | **stack/register VM** (§2) |
| many `S-box`/`T-table` lookups, 4×4 state | **custom SPN / AES-like** (§3) |
| `xorshift`/`rol`/`ror` + a state that feeds back | **PRNG feedback cipher** (§4) |
| `ptrace`/`isatty`/`/proc/self` checks | **anti-debug corruption** (§5) |
| `chall.pyc`, `.pyc` magic | **CPython disassembly** (§6) |
| `.class`/JAR/`cafebabe` | Java / smali path |
| 15 nested encodings, no binary | that is crypto, not reverse |

## 2. VM bytecode

1. Parse the bytecode **linearly** into `(op, arg)` tuples. A "chain splitter" that
   assumes control flow will mis-parse — write the dumb linear parser first.
2. Enumerate opcodes, then build a **forward interpreter**.
3. Validate the forward interpreter against the real binary for one input before
   inverting anything.
4. For a search over candidates, sort by full-run acceptance — 46 unique candidates
   collapsed to 1 once the whole program was executed, not just the header.
5. Then invert (or just emulate forward and compare).

## 3. Custom SPN / AES-like

- Read the state layout from the **stack**, not from the source if absent.
- Verify `MixColumns`-style steps **empirically with gdb** on known input —
  a guessed matrix is the single most common failure.
- Matrix offset off-by-one is real: `add r10, 0x4` *precedes* the compare, so columns
  1..3 come from `+0x8/+0xC/+0x10`, not from the base.
- Build: `sub_bytes → shift → mix → add_key`, validate one round, then invert.

## 4. PRNG feedback cipher

- Identify the generator (xorshift32, LCG, MT) by its shift/xor constants.
- **The feedback path is where the bug hides.** If an op writes only the low byte of
  a 32-bit register that later seeds the generator, emulate that exact partial write.
- Emulate magic-division sequences exactly instead of substituting `%`.
- Forward-verify against the binary, then invert.

## 5. Anti-debug corruption

Common shape: the flag is correct **only** when a debugger is absent, or the check
corrupts the buffer when traced.

- Confirm by running the binary **untraced** and comparing to the traced run.
- Patch the branch in the binary rather than fighting the tracer.
- Document the anti-debug path — it usually *is* the intended trick.

## 6. CPython `.pyc`

```bash
python3 - <<'PY'
import dis, marshal, importlib.util, sys
f=open('chall.pyc','rb'); f.read(16)          # header size varies 3.7+ (16 for 3.7-3.13)
code=marshal.load(f); dis.dis(code)
PY
```

- Match the interpreter version to the pyc magic (`3.13` seen in the field).
- The blob is usually one `print()` of an encoded string → hand off to `crypto/`
  custom-alphabet recovery, and read the **sibling challenge** for the author's scheme.

## 7. Java / JAR

`unzip -o x.jar`, then `jadx`/`procyon`, or `javap -c` for the disassembly. Bytecode
straight-line `String` constant work is usually trivial; the constant pool holds it.

## Unresolved (recorded honestly)

`bootleg` — CTV had no notes on why it failed. If you meet it, write the note.

## Output contract

```
CLASS:     vm | spn | prng | anti-debug | pyc | java | strings
VALIDATED: forward interpreter matches binary on <input>
FLAG:      <flag>
```
