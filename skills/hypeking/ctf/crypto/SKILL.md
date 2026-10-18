---
name: ctf-crypto
description: "CTF crypto checklist — ECDSA/DSA nonce-reuse and nonce-recurrence key recovery, custom base-N alphabet recovery by known-plaintext, RSA, AES-GCM, XOR/Vigenere, xorshift PRNG. Trigger: crypto challenge, ecdsa, dsa, nonce, nonce reuse, polynomial recurrence, custom base32, base64 custom alphabet, rsa, aes-gcm, lcg, xorshift."
---

# CTF crypto — checklist

Order of attack, cheapest first. Every step has a "how do I know this is the bug"
test; run the test before writing the solver.

## 0. Triage (2 minutes)

```bash
file *  ;  head -c 200 *  ;  strings -n 6 * | head -40
```

| Signal | Bug class |
|---|---|
| several `(msg, r, s)` triples, any repeated `r` | nonce reuse → instant `d` |
| device says "advances its RNG" / "never repeats a random number" | nonce **recurrence** |
| one long string, small distinct-char count | custom base-N alphabet |
| `n`, `e`, `c` with small `e` | RSA low exponent / Håstad |
| two moduli sharing a factor | RSA common-factor gcd |
| `flag_nonce`/`flag_ct`/`flag_tag` | AES-GCM with a derived key |

## 1. Nonce reuse (do this first, it is 3 lines)

Same `r` twice ⇒ `k = (z1 - z2)/(s1 - s2)`, then `d = (s1*k - z1)/r` over `q`.

## 2. Nonce recurrence — the CTV case

`sandi-garuda`, `cakra`, `kentongan`. The device advances the nonce with a hidden
polynomial: `k_{i+1} = f(k_i) mod q`.

Each signature gives `k_i = (z_i + r_i·d)·s_i⁻¹`, i.e. **`k_i` is affine in the
unknown private key `d`**. Substituting turns every recurrence step into a
polynomial identity in `d`. Two steps that must agree share only the true `d`, so
the key falls out of a **polynomial gcd over GF(q)**, not a brute force.

```bash
python3 ~/.omp/agent/skills/hypeking/ctf/scripts/nonce-recurrence.py \
    --mode dsa  transcript.json --deg auto      # kentongan (Horner, unknown degree)
python3 ~/.omp/agent/skills/hypeking/ctf/scripts/nonce-recurrence.py \
    --mode ecdsa transcript.txt --scheme square # k_{i+1} = k_i² + c
python3 ~/.omp/agent/skills/hypeking/ctf/scripts/nonce-recurrence.py \
    --mode ecdsa transcript.txt --scheme cakra  # k_{i+1} = c·k_i² + e
```

**Bugs that cost the most time (all real, all from the transcript):**

- Coefficient order inverted. `[A, B]` means `A + B·x`, i.e. constant-term **first**.
- Differencing must cancel the *unknown constant* explicitly; eliminating it by
  "dividing by the leading coefficient" is mathematically invalid.
- The consistency system is homogeneous → you need **deg+2 equations for deg+1
  unknowns**, and the minor must include the **rhs column**. A deg×deg minor is
  identically zero and tells you nothing.
- Verify the polynomial machinery on synthetic data *before* trusting a negative
  result. A wrong solver returns "no root" for a solvable challenge.
- Always confirm: `pow(g, x, p) == y`. Never submit an unverified key.

## 3. Custom base-N alphabet

Symptom: a string whose **distinct char count** matches a base exactly
(25 distinct in 48 chars ⇒ base32, 30 bytes). `cyp` spent many iterations here.

Order:
1. Count distinct symbols. That is the radix candidate, not a guess.
2. Assume the **known flag prefix** (`REDLIMIT{`, `CTF{`, …) and solve the alphabet
   by known-plaintext: each output byte pins log2(radix) symbols.
3. If the prefix maps **inconsistently** (same ciphertext symbol must decode to two
   different plaintext values), it is **not** positional/monoalphabetic — stop
   assuming and switch model:
   - custom base32 with shuffled alphabet → recover alphabet by prefix, then verify
     the whole string has no conflicts;
   - pure substitution (no bit grouping) → larger radix, test `nb = 8`;
   - truncated alphabet → the classic bug: `alpha[:r]` only holds `r` symbols, so
     chars past position `r-1` fail. Check alphabet length ≥ radix.
4. Write the search with the **plaintext-printable constraint**, not brute force
   over all permutations.

## 4. RSA

- Shared factor: `gcd(n1, n2)` across two moduli.
- Small `e`: integer `e`-th root, or Håstad broadcast with CRT when `e` messages.
- Sibling challenge gives you the author's style — `cyp2` stored raw bytes while
  `cyp` encoded a string. Read the sibling before inventing a scheme.

## 5. AES-GCM / stream

- Verify before you decrypt: a **GCM tag that validates is proof** the key is right.
  `AES.new(key, AES.MODE_GCM, nonce=n).decrypt_and_verify(ct, tag)`.
- Derived key convention seen in the field: `sha256(label || d.to_bytes(32,'big'))`.

## 6. Misc

- `onenc`, `base-jumper`: nested base conversions — decode **iteratively**, printing
  after each layer, never in one blind pass.
- xorshift/LCG: recover state from consecutive outputs, then invert. If a bit-op
  feeds back (e.g. `rol r8b` mutating the low byte of `r8d` that seeds `esi`),
  emulate the **exact** instruction, do not approximate with `%` arithmetic.
- Magic division ≠ modulo. Emulate the compiler's sequence exactly; `i % 7` is a
  guess that will silently produce a 90 % correct flag.

## Output contract

```
BUG:      <class>
EVIDENCE: <what proved it>
VERIFIED: pow(g,x,p)==y | gcm tag ok | printable flag
FLAG:     <flag>
```
