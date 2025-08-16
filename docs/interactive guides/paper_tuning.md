# Paper Tuning Module

This document describes the implementation of a **Paper Test Mode** for
archery tuning in the application. It allows the archer to record paper
tear results and generates tuning recommendations based on bow type and
tear direction.

------------------------------------------------------------------------

## User Workflow (UX)

1.  Select bow type & handedness (prefilled from stored setup).
2.  Shoot an arrow through paper at 2--3 m distance.
3.  Record the tear direction observed: left, right, high, low (or
    combinations like nock-left, nock-high).
4.  Input the tear result into the app (UI selector or quick buttons).
5.  Press **Analyze** → rule engine evaluates the tear and suggests the
    smallest correction step.
6.  Show recommendations such as:
    -   "Move rest IN 0.3--0.6 mm" (compound, RH, left tear)\
    -   "Reduce plunger tension 1/4 turn" (recurve/barebow, left tear)

------------------------------------------------------------------------

## Inputs

-   `paper_tune_tear`: string label (e.g., `"left"`, `"right"`,
    `"high"`, `"low"`, `"nock-left"`).\
-   `bow_type`: `"compound"`, `"recurve"`, `"barebow"`.\
-   `handedness`: `"RH"` or `"LH"` (flip left/right logic for LH).

------------------------------------------------------------------------

## Rule Logic

### Compound

-   **Left tear (RH):** move rest IN 0.3--0.6 mm.\
-   **Right tear (RH):** move rest OUT 0.3--0.6 mm.\
-   **High tear:** lower nocking point 0.5--1.0 mm or stiffen launcher
    blade.\
-   **Low tear:** raise nocking point 0.5--1.0 mm or soften launcher
    blade.\
-   **Diagonal tears:** fix vertical first, then horizontal.

### Olympic Recurve / Barebow

-   **Left tear (RH):** reduce plunger tension (−1/4 turn).\
-   **Right tear (RH):** increase plunger tension (+1/4 turn).\
-   **High tear:** lower nocking point slightly (0.5--1.0 mm).\
-   **Low tear:** raise nocking point slightly (0.5--1.0 mm).

------------------------------------------------------------------------

## Tolerances

-   One micro-adjustment at a time.\
-   Retest after each adjustment.\
-   Vertical issues (high/low) usually prioritized first.\
-   If erratic tears persist → check clearance (powder test).

------------------------------------------------------------------------

## Example Output Messages

-   Compound (RH):\
    "Paper shows **left tear**. Move rest IN 0.3--0.6 mm. Re-test."

-   Compound (RH):\
    "Paper shows **low tear**. Raise nocking point 0.5--1.0 mm or soften
    blade."

-   Recurve (RH):\
    "Paper shows **right tear**. Increase plunger tension +1/4 turn."

-   Barebow (RH):\
    "Paper shows **high tear**. Lower nocking point 0.5--1.0 mm."

------------------------------------------------------------------------

## Flask Rule Integration

``` python
if meas.paper_tune_tear:
    t = meas.paper_tune_tear.lower()
    if setup.bow_type == "compound":
        if "left" in t:
            recs.append({"component":"rest","action":"move_in","magnitude":"0.3–0.6 mm","why":"Paper tear left"})
        if "right" in t:
            recs.append({"component":"rest","action":"move_out","magnitude":"0.3–0.6 mm","why":"Paper tear right"})
        if "high" in t:
            recs.append({"component":"nocking_point","action":"lower","magnitude":"0.5–1.0 mm","why":"Paper tear high"})
        if "low" in t:
            recs.append({"component":"nocking_point","action":"raise","magnitude":"0.5–1.0 mm","why":"Paper tear low"})
    else:
        if "left" in t:
            recs.append({"component":"plunger","action":"reduce_tension","magnitude":"-1/4 turn","why":"Paper tear left"})
        if "right" in t:
            recs.append({"component":"plunger","action":"increase_tension","magnitude":"+1/4 turn","why":"Paper tear right"})
        if "high" in t:
            recs.append({"component":"nocking_point","action":"lower","magnitude":"0.5–1.0 mm","why":"Paper tear high"})
        if "low" in t:
            recs.append({"component":"nocking_point","action":"raise","magnitude":"0.5–1.0 mm","why":"Paper tear low"})
```

------------------------------------------------------------------------

## Extras

-   Combine paper test results with bareshaft/walkback to confirm
    consistency.\
-   Add a **"show me" overlay** image in UI to help archers identify
    tears visually.\
-   Store test history for comparison (before/after adjustments).

------------------------------------------------------------------------
