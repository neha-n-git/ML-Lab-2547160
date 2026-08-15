# NEO Hazard Screening: Predicting PHA-like Characteristics in Near-Earth Objects

**CIA 3 — Machine Learning (MCA 521-4) | ML for Social Good Ensemble Challenge**
**Mission domain:** Crisis (Disaster Response — preparedness and resource-prioritization phase)

---

## 1. Problem Overview

NASA's Minor Planet Center and its network of observatories track over 40,000 known
Near-Earth Objects (NEOs). Of these, only a subset receive the dedicated follow-up
observation needed to fully constrain their orbit and confirm official hazard status.
Telescope time, analyst attention, and computational resources for orbit refinement are
limited, and this bottleneck determines how quickly a genuinely hazardous object gets
identified and prioritized for further study.

This project investigates whether machine learning can identify NEOs exhibiting
characteristics associated with NASA's official Potentially Hazardous Asteroid (PHA)
classification, using orbital and physical features **other than** the two variables
that directly define the official label. NASA's PHA rule is deterministic:

```
PHA = Yes  if  MOID ≤ 0.05 AU   AND   H ≤ 22.0
```

where `MOID` is Minimum Orbit Intersection Distance (closest possible approach to
Earth's orbit) and `H` is absolute magnitude (a brightness/size proxy). Because this
rule is already known and exact, including `MOID` and `H` as model inputs would let a
model trivially reconstruct the existing definition rather than discover anything new.
This project therefore excludes them from its main experiment, and instead asks a
harder, more useful question: **do the remaining orbital and physical characteristics of
an object carry independent predictive signal for PHA-like status?** This has practical
value for newly discovered objects whose MOID has not yet been well constrained by
enough observations.

**Beneficiaries:** NASA's Planetary Defense Coordination Office (PDCO), the Minor Planet
Center, and allied observatories deciding where to direct scarce follow-up observation
resources.

**Framing note:** this is a *preparedness / resource-allocation* tool, not a real-time
incident-response system. It supports the upstream decision — which of thousands of
catalogued objects deserve closer study — that precedes any actual emergency response.
Planetary defense is a recognized part of disaster management; NASA's PDCO and FEMA have
run joint exercises simulating coordinated response to a hypothetical asteroid impact
threat.

---

## 2. Dataset

**Source:** NASA/JPL-Caltech Solar System Dynamics Group, Small-Body Database (SBDB)
Query API.
`https://ssd.jpl.nasa.gov/tools/sbdb_query.html`

**Citation:**
NASA/JPL-Caltech Solar System Dynamics Group. *Small-Body Database (SBDB) Query API.*
Jet Propulsion Laboratory. Retrieved via `https://ssd-api.jpl.nasa.gov/sbdb_query.api`.

**Retrieval method:** the dataset is pulled programmatically at notebook runtime via a
`GET` request to SBDB's Query API, restricted to `sb-group=neo` (Near-Earth Objects
only). This is a live, actively-maintained, government-run catalog updated daily from
Minor Planet Center observations — not a static or third-party mirror. No manual
download step is required, and no Kaggle or other secondary source is used.

**Unit of analysis:** one row = one catalogued Near-Earth Object, described by its
orbital elements, physical properties, and observation-quality metadata at the time of
the API call. Roughly 42,000 objects were retrieved at the time of this project.

**Why restrict to NEOs:** the full SBDB contains ~1.4 million asteroids, but PHA status
is only a meaningful question within the near-Earth population — a main-belt asteroid is
trivially non-PHA by definition. Restricting to NEOs upfront avoids a degenerate
classification task.

### Feature groups retained after cleaning

| Group | Features | Description |
|---|---|---|
| Orbital elements | `e`, `a`, `q`, `i`, `om`, `w`, `ma`, `epoch` | The six classical Keplerian elements plus epoch — describe the size, shape, tilt, and orientation of the orbit, and the object's position along it |
| Derived orbital quantities | `per`, `per_y`, `n`, `ad` | Orbital period, mean motion, and aphelion distance — mathematically derived from `a`/`e`, retained for interpretability |
| Orbit classification | `class` (one-hot: `class_APO`, `class_AMO`, `class_ATE`, `class_IEO`) | NEO orbit subtype (Apollo, Amor, Aten, Atira) — describes whether and how the orbit crosses Earth's |
| Observation quality | `condition_code`, `data_arc`, `n_obs_used`, `data_arc_missing` | How well-tracked and well-characterized the object's orbit is |
| Jupiter Tisserand parameter | `t_jup` | Orbital dynamics parameter distinguishing asteroid-like from comet-like orbits |
| **Excluded (leakage)** | `H`, `moid`, `moid_ld` | Directly define the official PHA label — excluded from the main experiment; retained only for a baseline sanity-check experiment |
| **Target** | `pha` | Binary: 1 = officially classified PHA, 0 = not |

**Columns dropped during cleaning:** 13 physical-property fields (`diameter`, `density`,
`albedo`, `GM`, `rot_per`, `spec_T`, `spec_B`, `BV`, `UB`, `IR`, `G`, `extent`, `name`)
were dropped due to >90% missingness — these are only measured for objects with radar,
spacecraft, or satellite-derived data, so their absence is an expected property of the
population, not a data-quality error.

---

## 3. Methodology Summary

1. **Data acquisition** — live API pull, restricted to NEOs (Section 1 of notebook).
2. **Cleaning and EDA** — dtype correction, missingness audit (including an explicit
   MCAR/MAR investigation for `data_arc`, resolved via a missingness flag + conditional
   imputation rather than row deletion), outlier checks, one-hot encoding, and a
   leakage-safe stratified train/test split (Sections 2–13).
3. **Class imbalance handling** — PHA is a ~6% minority class. Handled via class
   weighting (`class_weight="balanced"` / `scale_pos_weight`) during training only; the
   test set is never rebalanced, so evaluation reflects the true class distribution
   (Section 15).
4. **Modeling** — baseline (majority-class dummy), Logistic Regression, Random Forest
   (bagging), XGBoost (boosting), and a heterogeneous Stacking ensemble, each evaluated
   with and without the leakage-prone `H`/`moid` features (Sections 14–22).
5. **Explainability** — SHAP (TreeExplainer) global feature importance and individual
   local explanations (true positive, false negative, and a synthetic record), tied back
   to domain interpretation (Section 23).
6. **Ethics and responsible use** — bias/coverage limitations, false-negative vs.
   false-positive cost framing, human oversight requirements, and deployment limits
   (Section 24).
7. **Live demo** — a synthetic NEO record run through the final model with a full SHAP
   explanation (Section 25).

---

## 4. Reproducibility Instructions

1. Open the notebook in Google Colab (recommended) or a local Jupyter environment with
   internet access.
2. Install dependencies if not already present:
   ```
   pip install pandas scikit-learn xgboost shap matplotlib seaborn requests
   ```
3. Run all cells top to bottom. Section 1 pulls the dataset live from NASA's SBDB API —
   no manual download is needed.
4. All train/test splits use `random_state=42`; results should be reproducible up to
   minor drift from NASA's live catalog being updated between runs (the SBDB is refreshed
   daily as new objects are discovered or observations are added).
5. To freeze results exactly as reported, save the output of Section 1
   (`neo_data_raw.csv`) and load from that file on subsequent runs instead of re-querying
   the live API.

---

## 5. Results Summary

| Model (main feature set, H/MOID excluded) | Accuracy | Precision (PHA) | Recall (PHA) | F1 (PHA) |
|---|---|---|---|---|
| Dummy (majority class) | 0.939 | 0.000 | 0.000 | 0.000 |
| Logistic Regression | 0.856 | 0.279 | 0.871 | 0.423 |
| Random Forest | 0.947 | 0.678 | 0.243 | 0.358 |
| XGBoost | 0.927 | 0.446 | 0.867 | 0.589 |
| Stacking (LogReg + RF + XGBoost) | 0.913 | 0.405 | 0.916 | — |

Recall was prioritized over precision throughout model selection, since a missed
hazardous object (false negative) is more costly than a false alarm requiring extra
review. Stacking achieves the highest recall of all models tested on the main feature
set.

Full confusion matrices, ROC curves, and the baseline (H/MOID-included) sanity-check
experiment are provided in the notebook.

---

## 6. Ethics and Limitations (Summary)

- **Coverage bias:** the training data underrepresents newly discovered, poorly-tracked
  objects (see Section 10's missingness analysis); predictions for such objects warrant
  lower confidence.
- **False-negative cost:** prioritized over precision throughout, since missing a
  hazardous object is more costly than an unnecessary review.
- **Human oversight:** this model is a screening tool, not a hazard determination
  system. Output should direct attention for expert MOID-based review, not replace it.
- **No personal data:** the dataset describes physical objects only; no privacy concerns
  apply.

Full discussion in Section 24 of the notebook.

---

## 7. Acknowledgements

Dataset: NASA/JPL-Caltech Solar System Dynamics Group, Small-Body Database (SBDB).
All code in this project was written for this assignment; standard open-source
libraries (`pandas`, `scikit-learn`, `xgboost`, `shap`, `matplotlib`, `seaborn`) are
used under their respective licenses.