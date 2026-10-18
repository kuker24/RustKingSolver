# Verification loop

## When

Activate this loop when a required verification check fails, proof evidence is missing or lost after teardown, or when there is temptation to weaken a test or harness assertion to turn a check green.

## Corrective action

1. Treat failures as signals: diagnose whether the defect lies in product behavior or harness configuration.
2. Fix the product code or update the test harness so that it accurately exercises the user path.
3. Re-run verification from the beginning (launch, doctor, drive, observe, cleanup).
4. Never weaken tests: do not delete tests, mark failing tests with skip/xfail, loosen threshold assertions, comment out checks, or bypass the user path with internal setters just to force a PASS.

## Evidence

Record mechanical proof in the evidence ledger:
- Every completed check requires a single verifiable line starting with `FACT:` containing the exact command run, exit code, and artifact path (e.g. `FACT: exit 0`, `FACT: artifacts/verify.png`).
- A screenshot or transcript is a `FACT` only if the artifact file physically exists at the path named by the verification skill after cleanup finishes.
- `JUDGMENT:` entries are advisory only and cannot substitute for or override missing or failing `FACT:` rows.
- A missing verification command is recorded as `NOT_CONFIGURED`, never as `PASS`.
