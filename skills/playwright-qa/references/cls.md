# Visual Layout Shift (CLS) Recipe

Exploratory layout shift observation recipe for `playwright-qa`.

## Boundary
- Visual screenshots provide qualitative visual proof of shifts between actions, NOT quantitative Core Web Vitals scores.
- Measured numerical CLS (< 0.1) thresholds belong to `/full-performance-audit`.
- If an observed layout shift requires deep performance profiling, attach `/chrome-devtools-axi` via `opencode-chromium-cdp` (`127.0.0.1:9223`).

## Recipe: Before-and-After Shift Observation

When testing interactive surfaces susceptible to layout instability (lazy images, dynamic fonts, asynchronous banners, expanding drawers):

1. **Baseline Snapshot & Screenshot:**
   ```bash
   playwright-cli -s=task-ui snapshot
   playwright-cli -s=task-ui screenshot --filename=artifacts/cls-before.png
   ```

2. **Trigger Asynchronous Interaction / Mutation:**
   ```bash
   playwright-cli -s=task-ui click e4
   ```

3. **Settled Screenshot:**
   ```bash
   playwright-cli -s=task-ui screenshot --filename=artifacts/cls-after.png
   ```

4. **Verify Evidence:**
   - Confirm visual elements did not unexpectedly reflow or displace existing content.
   - Record `FACT: artifacts/cls-before.png` and `FACT: artifacts/cls-after.png`.
   - Never claim quantitative CLS compliance from screenshots alone.
