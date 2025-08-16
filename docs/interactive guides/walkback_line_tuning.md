# Walkback Line Tuning Module

This document describes the implementation of a **Walkback Line Mode**
for archery tuning in the application. It allows the archer to click
arrow impacts on a vertical reference line at multiple distances and
generates tuning recommendations.

------------------------------------------------------------------------

## User Workflow (UX)

1.  Select bow type & handedness (prefilled from stored setup).
2.  Choose distances (e.g., 5, 10, 15, 20, 30 m).
3.  For each distance, UI displays a vertical line on the target face.
    The archer clicks their arrow impacts near the line.
4.  Press **Analyze** → offsets are computed in cm, slope is fitted, and
    rule engine gives advice.
5.  Show recommendation, e.g.:
    -   "Move rest LEFT 0.2--0.4 mm" (compound)\
    -   "Increase plunger 1/4 turn" (recurve/barebow)

------------------------------------------------------------------------

## Computation

### Inputs

-   `distances_m`: array of shot distances (m).
-   `x_offsets_cm`: horizontal offsets of group centroids from the line
    (cm).\
    Positive = right (RH frame).\
-   Optional: handedness (invert x for LH).

### Derived

-   **Slope** `m = Δx / Δdistance` (cm/m).\
-   **Intercept** `b = x at zero distance` (cm).\
-   **Linearity** `R²`: fit quality.

### Tolerances (base at 30m max)

  Bow type   Slope tol (cm/m)   Intercept tol (cm)
  ---------- ------------------ --------------------
  Compound   ≤ 0.10             ≤ 0.7
  Recurve    ≤ 0.15             ≤ 1.0
  Barebow    ≤ 0.20             ≤ 1.5

------------------------------------------------------------------------

## Rule Logic

-   **Drift slope right (RH):**

    -   Compound: rest LEFT 0.2--0.4 mm\
    -   Recurve/Barebow: reduce plunger tension −1/8 to −1/4 turn, or
        rest IN 0.5 mm

-   **Drift slope left (RH):**

    -   Compound: rest RIGHT 0.2--0.4 mm\
    -   Recurve/Barebow: increase plunger tension +1/8 to +1/4 turn, or
        rest OUT 0.5 mm

-   **Flat slope, residual offset:**\
    → Alignment OK. Finish with sight windage.

-   **Nonlinear (R² \< 0.8):**\
    → Possible clearance, timing (compound), or grip torque.

------------------------------------------------------------------------

## Example Output Messages

-   Compound (RH):\
    "Groups drift 0.14 cm/m right (R² 0.92). Move rest LEFT 0.2--0.4
    mm."

-   Recurve (RH):\
    "Drift 0.18 cm/m left. Increase plunger tension +1/4 turn (or rest
    OUT 0.5 mm)."

-   Barebow:\
    "Drift 0.22 cm/m right. Near tolerance; if calm, reduce plunger 1/8
    turn, else accept."

------------------------------------------------------------------------

## Flask Endpoint Example

``` python
@bp.post("/analyze/walkback/manual")
def analyze_walkback():
    data = request.get_json()
    bow = data.get("bow_type", "compound")
    handed = data.get("handed", "RH")
    dist = data["distances_m"]
    xcm = data["x_offsets_cm"]
    m = data["fit"]["m"]; b = data["fit"]["b"]; r2 = data["fit"]["r2"]
    if handed == "LH": m, b = -m, -b
    # compare vs tolerances and return JSON recommendations
```

------------------------------------------------------------------------

## Nuxt 3 Component

The `WalkbackLine.vue` component allows marking arrows on the target
face, distance switching, and reference line dragging. It computes
slope, intercept, and R² client-side and sends them to Flask for
recommendations.

------------------------------------------------------------------------

## Extras

-   Support **French tune** (5m vs 30m only).\
-   Show residuals per distance.\
-   Lock the line to center by default, but allow dragging.\
-   Include re-check plan in recommendations.

------------------------------------------------------------------------
