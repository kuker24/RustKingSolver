# Playbook: Mode 2 — AI Self-Code Audit

Defensive source-code audit of a local repository. No live targets, no
exploitation, no findings.db state machine. Output: `<repo>/security/reports/`.

> If `db/doctor.sh` or this playbook's sibling assets are missing from the
> installed skill dir, degrade per SKILL.md §Graceful Degradation — do NOT abort.

## Phase 0 — Mode & Scope Confirmation

- Target is a filesystem path. Confirm it exists; get repo root.
- Ask (or infer): full scan vs focused categories; whether to include git history;
  where the report goes (default `<repo>/security/reports/FULL_SCAN_<year>.md`).
- Set up a todo list mirroring the phases below — audits are multi-step by definition.

## Phase 1 — Recon (stack + surface inventory)

1. Identify stack from manifests: `package.json`, `requirements.txt`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `composer.json` → framework, ORM, auth libs, payments.
2. Repo map: enumerate `src/`-equivalent trees; flag API routes/handlers,
   middleware, DB layers, upload handlers, cron/webhook endpoints, admin areas.
3. Config sweep: `next.config.*`, `*.env.example`, `docker-compose.yml`,
   `vercel.json`, reverse-proxy configs, CORS/CSP definitions.
4. Dependency audit: `npm audit --omit=dev`, `pip-audit`, `cargo audit`.
5. Git history secret sweep (even if gitleaks is absent):
   ```bash
   git log --all -p | grep -iE "(api[_-]?key|secret|passphrase|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9+/_-]{12,}"
   ```
   Verify `.env*` patterns are gitignored AND untracked (`git ls-files | grep -i env`).
6. Pre-flight tool check (doctor.sh if present, else the manual loop); apply the
   SKILL.md Tool Fallback Matrix and record substitutions.

## Phase 2 — Audit Execution (17 categories)

Work through every category. For each: locate relevant code paths first
(grep for sinks/patterns), read them fully, then decide PASS / FINDING / N/A.

| # | Category | Primary evidence pattern |
|---|----------|--------------------------|
| 1 | Misconfigured DB / no RLS | migration files, RLS policy statements, connection strings |
| 2 | Unprotected API routes | route files lacking auth middleware BEFORE handler logic |
| 3 | Committed secrets | tracked .env files, hardcoded keys, git history |
| 4 | IDOR / access control | resource fetch missing owner_id comparison |
| 5 | Secrets in frontend | NEXT_PUBLIC_/VITE_/REACT_APP_ usage, bundled keys |
| 6 | SSRF | server-side fetch of user URLs; private-range blocking |
| 7 | CSRF | mutating endpoints without origin checks / SameSite tokens |
| 8 | Security headers / CSP | header config; nonce actually wired vs dead; unsafe-inline in prod |
| 9 | Wildcard CORS | Access-Control-Allow-Origin: * (+credentials) |
| 10 | Missing rate limiting | auth/login/reset routes without limiter; limiter bypassable (XFF trust, in-memory) |
| 11 | SQL injection | string-concat queries, raw drivers |
| 12 | XSS | dangerouslySetInnerHTML/innerHTML/v-html, href javascript: sinks |
| 13 | Unverified webhooks | stripe construct_event absence, no idempotency ledger |
| 14 | Insecure uploads | extension-only checks, no magic bytes, original filenames on app origin |
| 15 | Verbose errors | stack traces/SQL/library names in responses; debug pages in prod |
| 16 | Weak password hashing | MD5/SHA-1/plain-SHA256 for stored passwords (timing-safe compare of shared secrets is fine) |
| 17 | Hallucinated packages | deps not on official registries / typosquats; verify each unfamiliar import |

Rules:
- **N/A is an answer** — but must state why in one clause ("no database in stack").
- Every FINDING needs: file path + line numbers, evidence quote/snippet,
  impact sentence, concrete fix, severity per rubric (SKILL.md §Mode 2).
- Read complete functions, not grep matches alone — context kills false positives.

## Phase 3 — Verification & Deduplication

- Re-read every finding's call chain end-to-end: is the sink reachable? Is there
  a sanitizer upstream? Is the route actually routed?
- Merge duplicates across categories (one root cause reported once).
- Confirm exploitability preconditions honestly; downgrade overhyped severity.

## Phase 4 — Report

Render `templates/audit-report.md` into the agreed location. Order:
verdict line → category table → findings (worst first) → positive observations →
remediation priority. Include the fallback-substitution list from Phase 1 so the
coverage claim is auditable.

## Anti-patterns (do not do these)

- Do NOT run offensive tooling against external hosts because they appeared in the code.
- Do NOT report "no RLS" when there is no database at all.
- Do NOT count a category as covered because you grepped once — grep finds candidates, reading finds findings.
- Do NOT leave findings without fixes; an audit without remediation is a list, not a service.
