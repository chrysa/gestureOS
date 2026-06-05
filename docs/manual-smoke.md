# Manual smoke & verification checklist

Human-run checks that CI cannot perform (need a real camera, display, or input device).
Referenced by later construction-plan steps.

## Reference machine (for latency numbers)

Record the machine the budget numbers were measured on, so p95 figures are comparable.

| Field | Value |
|-------|-------|
| CPU | _fill in_ |
| RAM | _fill in_ |
| GPU (if used) | _fill in_ |
| OS / kernel | _fill in_ |
| Python | 3.14 |
| Camera | _fill in (model, resolution, FPS)_ |

> The < 50 ms perception→action p95 requirement is defined **on this reference machine**.

## Latency budget (Step 1b)

- [ ] `make bench` runs and prints the per-stage + end-to-end table.
- [ ] No-op backend: glue p95 < 5 ms (asserted automatically).
- [ ] (After Step 6a) Real frames in `benchmarks/fixtures/`: end-to-end p95 < 50 ms.

## OS Control Layer (Step 3)

- [ ] Linux: `ydotool` has `uinput` access (add user to `input` group / udev rule).
- [ ] Cursor move / click / scroll / drag observed on a real desktop.

## Gesture MVP (Step 6a–6c)

- [ ] Camera capture starts; hand landmarks tracked under normal lighting.
- [ ] Cursor follows the index finger with no perceptible lag.
- [ ] Pinch → click, two-finger → scroll, drag works.

## MultiScreen (Step 7)

- [ ] Cursor crosses between 2–4 screens with correct spatial mapping.
