#!/usr/bin/env python3
"""Private-key recovery when signing nonces follow a recurrence, over GF(order).

Ported and generalised from the Redlimit CTV tooling (ecdsa_solve.py +
kentongan_solve.py). Both solved real challenges: `sandi-garuda`, `cakra`,
`kentongan`.

The idea, in one line: every signature gives

    k_i = (z_i + r_i * d) * s_i^-1        (affine in the unknown key d)

so substituting k_i into the nonce recurrence turns each step into a polynomial
identity in d. Steps that must agree share only the true d, and the key falls out
of a polynomial GCD over GF(order) -- no brute force.

Modes:
  dsa    k_{i+1} = c_deg*k_i^deg + ... + c_1*k_i + c_0   (unknown coeffs, unknown deg)
         -> consistency minors of a homogeneous polynomial system, gcd, root hunt
  ecdsa  square: k_{i+1} = k_i^2 + c
         cakra : k_{i+1} = c*k_i^2 + e                  (both constants unknown)

Usage:
  nonce-recurrence.py --mode dsa   transcript.json  [--deg auto]
  nonce-recurrence.py --mode ecdsa transcript.txt --scheme square
  nonce-recurrence.py --mode ecdsa transcript.txt --scheme cakra
  nonce-recurrence.py --selftest

DSA transcript ('kentongan' shape):
  {"P": {"p": "<hex>", "q": "<hex>", "g": "<hex>"}, "y": "<hex>",
   "entri": [{"no": 1, "teks": "msg", "r": "<hex>", "s": "<hex>"}, ...]}

ECDSA transcript: the repr of a signature list plus flag fields, matched by regex:
  (b'<msg>', <r>, <s>) ...  flag_nonce=<hex> flag_ct=<hex> flag_tag=<hex>
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys

CURVE_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# --------------------------------------------------------------------- polys
# A polynomial is a list of coefficients, index == power of x, over GF(p).


def ptrim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a or [0]


def is_zero(a):
    return a == [0] or not a


def padd(a, b, p):
    n = max(len(a), len(b))
    return [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
            for i in range(n)]


def psub(a, b, p):
    return padd(a, [(-x) % p for x in b], p)


def pmul(a, b, p):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    r[i + j] = (r[i + j] + ai * bj) % p
    return ptrim(r)


def pdivmod(a, b, p):
    a, b = ptrim(a), ptrim(b)
    if is_zero(b):
        raise ZeroDivisionError("poly division by zero")
    inv = pow(b[-1], -1, p)
    q = [0] * max(1, len(a) - len(b) + 1)
    while not is_zero(a) and len(a) >= len(b):
        f = a[-1] * inv % p
        s = len(a) - len(b)
        q[s] = f
        for i, bv in enumerate(b):
            a[s + i] = (a[s + i] - f * bv) % p
        a = ptrim(a)
    return ptrim(q), a


def pgcd(a, b, p):
    a, b = ptrim(a), ptrim(b)
    while not is_zero(b):
        a, b = b, pdivmod(a, b, p)[1]
    if is_zero(a):
        return [0]
    inv = pow(a[-1], -1, p)
    return ptrim([(x * inv) % p for x in a])


def ppowmod(base, exp, f, p):
    r = [1]
    b = ptrim(base[:])
    for _ in range(len(f) - 1):
        b = pdivmod(b, f, p)[1]
    while exp:
        if exp & 1:
            r = pdivmod(pmul(r, b, p), f, p)[1]
        b = pdivmod(pmul(b, b, p), f, p)[1]
        exp >>= 1
    return r


def peval(a, x, p):
    r = 0
    for c in reversed(a):
        r = (r * x + c) % p
    return r


def determinant(M, p):
    """Leibniz expansion: exact over GF(p)[x], at the cost of n! terms."""
    n = len(M)
    total = [0]
    for perm in itertools.permutations(range(n)):
        inv = sum(1 for a in range(n) for b in range(a + 1, n) if perm[a] > perm[b])
        term = [1 if inv % 2 == 0 else -1]
        for i, j in enumerate(perm):
            term = pmul(term, M[i][j], p)
        total = padd(total, term, p)
    return ptrim(total)


def overdet(M, p):
    """Maximal minor of an (n+1 x n) matrix, via an appended identity column."""
    n = len(M[0])
    sq = [[*row, [1] if i == n else [0]] for i, row in enumerate(M)]
    return determinant(sq, p)


def isqrt_mod(a, p):
    """Modular square root of `a` over GF(p), or None. Tonelli-Shanks (works for any odd prime)."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        r = pow(a, (p + 1) // 4, p)
        return r if r * r % p == a else None
    # Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
            if i == m:
                return None
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, b * b % p
        t, r = t * c % p, r * b % p
    return r if r * r % p == a % p else None


def find_roots(f, p):
    """Distinct roots of a low-degree polynomial over GF(p)."""
    f = ptrim(f)
    if len(f) == 1:
        return []
    if len(f) == 2:
        return [(-f[0] * pow(f[1], -1, p)) % p]
    if len(f) == 3:
        # ax^2 + bx + c ; x = (-b +- sqrt(b^2-4ac)) / (2a)
        c, b, a = f[0], f[1], f[2]
        inv2a = pow(2 * a % p, -1, p)
        disc = (b * b - 4 * a * c) % p
        if disc == 0:
            return [(-b * inv2a) % p]
        s = isqrt_mod(disc, p)
        if s is None:
            return []
        roots = {((-b + s) * inv2a) % p, ((-b - s) * inv2a) % p}
        return sorted(r for r in roots if peval(f, r, p) == 0)
    roots, stack = [], [f]
    while stack:
        cur = ptrim(stack.pop())
        if len(cur) <= 1:
            continue
        if len(cur) == 2:
            roots.append(-cur[0] * pow(cur[1], -1, p) % p)
            continue
        for attempt in range(40):
            h = psub(ppowmod([2 + attempt, 1], (p - 1) // 2, cur, p), [1], p)
            factor = pgcd(cur, h, p)
            if 1 < len(factor) < len(cur):
                stack.append(pdivmod(cur, factor, p)[0])
                stack.append(factor)
                break
        else:
            roots.append(-cur[0] * pow(cur[1], -1, p) % p)
    return roots


# ----------------------------------------------------------------- DSA mode
def zof(text, q):
    return int.from_bytes(hashlib.sha256(text.encode()).digest(), "big") % q


def solve_nonce_recurrence(entries, p, q, g, y, deg, verbose=True):
    """Recover the private key x from DSA entries whose nonces follow a degree-`deg` Horner recurrence."""
    lin = []
    for e in entries:
        si = pow(int(e["s"], 16), -1, q)
        r = int(e["r"], 16)
        lin.append([zof(e["teks"], q) * si % q, r * si % q])
    rows = []
    for i in range(len(lin) - 1):
        cols, acc = [], [1]
        for _ in range(deg):
            acc = pmul(acc, lin[i], q)
            cols.append(acc)
        cols = cols + [[1], lin[i + 1]]      # constant column + rhs (k_{i+1})
        rows.append(cols)
    size = deg + 1          # unknowns: c_deg .. c_0
    over = deg + 2          # one equation more than unknowns -> consistency condition
    if len(rows) < over:
        if verbose:
            print(f"  deg={deg}: only {len(rows)} rows, need {over}", flush=True)
        return None
    common = None
    for picked in itertools.combinations(range(len(rows)), over):
        det = ptrim(overdet([[rows[r][c] for c in range(size + 1)] for r in picked], q))
        common = det if common is None else pgcd(common, det, q)
        if len(common) <= 1:
            if verbose:
                print(f"  deg={deg}: minors coprime -> no common root", flush=True)
            return None
        if len(common) == 2:
            break
    if verbose:
        print(f"  deg={deg}: gcd degree {len(common) - 1}", flush=True)
    roots = find_roots(common, q)
    if verbose:
        print(f"  candidate roots: {len(roots)}", flush=True)
    for x in roots:
        if pow(g, x, p) == y:
            return x
    return None


def dsa_auto(entries, p, q, g, y, max_deg=6, verbose=True):
    for deg in range(max_deg, 0, -1):
        x = solve_nonce_recurrence(entries, p, q, g, y, deg, verbose)
        if verbose:
            print(f"deg={deg}: x={hex(x) if x else None}", flush=True)
        if x:
            return x
    return None


# --------------------------------------------------------------- ECDSA mode
def parse_sigs(txt):
    return [(m.group(1).encode(), int(m.group(2)), int(m.group(3)))
            for m in re.finditer(r"\(b'([^']*)',\s*(\d+),\s*(\d+)\)", txt)]


def field(txt, name):
    return int(re.search(rf"{name}\s*=\s*(\d+)", txt).group(1))


def hexfield(txt, name):
    return bytes.fromhex(re.search(rf"{name}\s*=\s*(\w+)", txt).group(1))


def H(msg, n=CURVE_N):
    return int.from_bytes(hashlib.sha256(msg).digest(), "big") % n


def affine_nonces(sigs, n):
    """k_i = (z_i + r_i*d) * s_i^-1, as polynomials constant-term first."""
    out = []
    for msg, r, s in sigs:
        si = pow(s, -1, n)
        out.append([H(msg, n) * si % n, r * si % n])
    return out


def recover_d(gpoly, n):
    gpoly = ptrim(gpoly)
    if len(gpoly) != 2:
        raise ValueError(f"gcd did not reduce to a linear factor (degree {len(gpoly) - 1})")
    return -gpoly[0] * pow(gpoly[1], -1, n) % n


def solve_square(txt, n=CURVE_N):
    """k_{i+1} = k_i^2 + c, single unknown constant c.

    q_i = X_{i+1} - X_i^2 equals c at the true key, so consecutive q's are
    differenced to cancel c; that leaves quadratics vanishing only at d.
    """
    X = affine_nonces(parse_sigs(txt), n)
    q = [psub(X[i + 1], pmul(X[i], X[i], n), n) for i in range(len(X) - 1)]
    gpoly = None
    for i in range(len(q) - 1):
        diff = ptrim(psub(q[i], q[i + 1], n))
        gpoly = diff if gpoly is None else pgcd(gpoly, diff, n)
    return recover_d(gpoly, n)


def solve_cakra(txt, n=CURVE_N):
    """k_{i+1} = c*k_i^2 + e, both constants unknown.

    Differencing two consecutive steps cancels e:
        X_{i+1} - X_{i+2} = c*(X_i^2 - X_{i+1}^2)
    so cross-multiplying two of those gives a cubic in d; two cubics share only d.
    """
    X = affine_nonces(parse_sigs(txt), n)
    sq = [pmul(x, x, n) for x in X]
    polys = []
    for i in range(len(X) - 3):
        lhs = pmul(psub(X[i + 1], X[i + 2], n), psub(sq[i + 1], sq[i + 2], n), n)
        rhs = pmul(psub(X[i + 2], X[i + 3], n), psub(sq[i], sq[i + 1], n), n)
        polys.append(ptrim(psub(lhs, rhs, n)))
    gpoly = polys[0]
    for q in polys[1:]:
        gpoly = pgcd(gpoly, q, n)
    return recover_d(gpoly, n)


def unlock(txt, d, label, n=CURVE_N):
    """Decrypt the flag with key = sha256(label || d_32bytes), AES-GCM."""
    from Crypto.Cipher import AES
    key = hashlib.sha256(label + d.to_bytes(32, "big")).digest()
    cipher = AES.new(key, AES.MODE_GCM, nonce=hexfield(txt, "flag_nonce"))
    return cipher.decrypt_and_verify(hexfield(txt, "flag_ct"), hexfield(txt, "flag_tag"))


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    """Validate the polynomial toolkit and both ECDSA schemes on synthetic data."""
    n = CURVE_N
    ok = True

    # over GF(7): (x-1)(x-2) = x^2 - 3x + 2 = [2, 4, 1]
    prod = pmul([6, 1], [5, 1], 7)
    if ptrim(prod) != [2, 4, 1]:
        ok = False
        print(f"FAIL poly mul: {prod}")

    # gcd of (x-3)(x+1) and (x-3)(x+5) over GF(7) should be x-3 = [4, 1]
    a = pmul([4, 1], [1, 1], 7)
    b = pmul([4, 1], [5, 1], 7)
    gpoly = pgcd(a, b, 7)
    if ptrim(gpoly) != ptrim([4, 1]):
        ok = False
        print(f"FAIL gcd: {gpoly}")

    # roots of x^2 + 6x + 5 over GF(7) -> {2, 6}
    r = sorted(find_roots([5, 6, 1], 7))
    if r != [2, 6]:
        ok = False
        print(f"FAIL find_roots GF(7): {r}")

    # p == 1 mod 4 is the case the original shortcut got wrong (CURVE_N is 1 mod 4)
    s = isqrt_mod(9, 13)                      # 13 == 1 mod 4, 3^2 = 9
    if s not in (3, 10) or s * s % 13 != 9:
        ok = False
        print(f"FAIL isqrt_mod on p==1 mod 4: {s}")

    # square scheme round trip
    d = 0x1234567890ABCDEF
    k = 0xdeadbeef
    sigs, c = [], 42
    for i in range(8):
        msg = f"m{i}".encode()
        z = H(msg, n)
        r = (k * 7 + 1) % n
        s = pow(k, -1, n) * (z + r * d) % n
        sigs.append((msg, r, s))
        k = (k * k + c) % n
    txt = repr(sigs)
    if solve_square(txt, n) != d:
        ok = False
        print("FAIL solve_square")

    # cakra scheme round trip
    k = 0xcafebabe
    c2, e2 = 11, 7
    sigs = []
    for i in range(10):
        msg = f"c{i}".encode()
        z = H(msg, n)
        r = (k * 5 + 3) % n
        s = pow(k, -1, n) * (z + r * d) % n
        sigs.append((msg, r, s))
        k = (c2 * k * k + e2) % n
    if solve_cakra(repr(sigs), n) != d:
        ok = False
        print("FAIL solve_cakra")

    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ---------------------------------------------------------------------- main
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mode", choices=["dsa", "ecdsa"])
    p.add_argument("transcript", nargs="?")
    p.add_argument("--scheme", choices=["square", "cakra"], default="square")
    p.add_argument("--deg", default="auto", help="DSA recurrence degree, or 'auto'")
    p.add_argument("--max-deg", type=int, default=6)
    p.add_argument("--order", default=None, help="override GF order (hex or dec) for ECDSA")
    p.add_argument("--label", default=None, help="AES-GCM label for flag unlock")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()
    if not a.mode or not a.transcript:
        p.error("--mode and transcript are required (or use --selftest)")

    if a.mode == "dsa":
        doc = json.load(open(a.transcript))
        P = doc.get("P", doc)
        pp = int(P["p"], 16) if isinstance(P["p"], str) else P["p"]
        qq = int(P["q"], 16) if isinstance(P["q"], str) else P["q"]
        gg = int(P["g"], 16) if isinstance(P["g"], str) else P["g"]
        yy = int(doc["y"], 16) if isinstance(doc["y"], str) else doc["y"]
        entries = sorted(doc.get("entri", doc.get("entries", [])), key=lambda e: e.get("no", 0))
        print(f"q bits={qq.bit_length()}  entries={len(entries)}")
        if a.deg == "auto":
            x = dsa_auto(entries, pp, qq, gg, yy, a.max_deg)
        else:
            x = solve_nonce_recurrence(entries, pp, qq, gg, yy, int(a.deg))
        print("PRIVATE KEY", hex(x) if x else None)
        return 0 if x else 1

    txt = open(a.transcript, errors="replace").read()
    n = int(a.order, 0) if a.order else CURVE_N
    d = solve_square(txt, n) if a.scheme == "square" else solve_cakra(txt, n)
    print(f"scheme={a.scheme} d={hex(d)}")
    if a.label:
        try:
            print("FLAG", unlock(txt, d, a.label.encode()).decode("utf-8", "replace"))
        except Exception as e:                                # noqa: BLE001
            print(f"[unlock failed] {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
