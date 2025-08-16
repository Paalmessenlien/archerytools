# Bareshaft Tuning Module

This document describes the implementation of a **Bareshaft Test Mode**
for archery tuning in the application. It allows the archer to record
the position of bareshafts relative to fletched arrows and generates
tuning recommendations for compound, recurve, and barebow.

------------------------------------------------------------------------

## User Workflow (UX)

1.  Select bow type & handedness (prefilled from stored setup).\
2.  Shoot a group of **fletched** and **bareshaft** arrows at 15--20 m.\
3.  Record where the bareshafts land relative to the fletched group
    (left, right, high, low).\
4.  Input the observed pattern in the app.\
5.  Press **Analyze** → rule engine evaluates and gives the smallest
    correction step.\
6.  Show recommendation, e.g.:
    -   "Move rest IN 0.3--0.6 mm" (compound, bareshafts left).\
    -   "Reduce plunger tension 1/4 turn" (recurve, bareshafts left).

------------------------------------------------------------------------

## Inputs

-   `bareshaft_offset`: relative direction of bareshaft group
    (left/right/high/low).\
-   `bow_type`: `"compound"`, `"recurve"`, `"barebow"`.\
-   `handedness`: `"RH"` or `"LH"` (flip left/right logic for LH).

------------------------------------------------------------------------

## Rule Logic

### Compound

-   **Bareshaft left (RH):** arrow too stiff → move rest IN 0.3--0.6 mm,
    or reduce point weight.\
-   **Bareshaft right (RH):** arrow too weak → move rest OUT 0.3--0.6
    mm, or increase point weight.\
-   **High/low differences:** check nocking point height.

### Olympic Recurve / Barebow

-   **Bareshaft left (RH):** arrow too stiff → reduce plunger tension
    (−1/4 turn) or rest IN.\
-   **Bareshaft right (RH):** arrow too weak → increase plunger tension
    (+1/4 turn) or rest OUT.\
-   **High bareshaft:** nocking point too low → raise slightly (0.5--1.0
    mm).\
-   **Low bareshaft:** nocking point too high → lower slightly (0.5--1.0
    mm).

------------------------------------------------------------------------

## Tolerances

-   Goal: bareshafts within **5--7 cm** of fletched group at 20 m.\
-   Small vertical offsets (≤2 cm) are acceptable.\
-   Always re-test after a single adjustment.

------------------------------------------------------------------------

## Example Output Messages

-   Compound (RH):\
    "Bareshafts land **6 cm left** of fletched. Arrow stiff. Move rest
    IN 0.3--0.6 mm or reduce point weight."

-   Recurve (RH):\
    "Bareshafts land **8 cm right** of fletched. Arrow weak. Increase
    plunger tension +1/4 turn or rest OUT 0.5 mm."

-   Barebow (RH):\
    "Bareshafts group **high** vs fletched. Lower nocking point 0.5--1.0
    mm."

------------------------------------------------------------------------

## Flask Rule Integration

``` python
if meas.bareshaft_offset:
    offset = meas.bareshaft_offset.lower()
    if setup.bow_type == "compound":
        if "left" in offset:
            recs.append({"component":"rest","action":"move_in","magnitude":"0.3–0.6 mm","why":"Bareshafts left → stiff"})
        if "right" in offset:
            recs.append({"component":"rest","action":"move_out","magnitude":"0.3–0.6 mm","why":"Bareshafts right → weak"})
    else:
        if "left" in offset:
            recs.append({"component":"plunger","action":"reduce_tension","magnitude":"-1/4 turn","why":"Bareshafts left → stiff"})
        if "right" in offset:
            recs.append({"component":"plunger","action":"increase_tension","magnitude":"+1/4 turn","why":"Bareshafts right → weak"})
    if "high" in offset:
        recs.append({"component":"nocking_point","action":"lower","magnitude":"0.5–1.0 mm","why":"Bareshafts high"})
    if "low" in offset:
        recs.append({"component":"nocking_point","action":"raise","magnitude":"0.5–1.0 mm","why":"Bareshafts low"})
```

------------------------------------------------------------------------

## Extras

-   Display **visual overlay** in UI showing expected bareshaft/fletched
    group positions.\
-   Store historical tests for comparison (progress tracking).\
-   Combine with paper/walkback results for multi-test validation.

------------------------------------------------------------------------
