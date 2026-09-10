# ExoScout — Methodology

Full detail on the modeling procedure, evaluation protocol, and known limitations.
For a quick overview see the [README](../README.md).

## Task

Binary classification of NASA TESS Objects of Interest (TOI):

* `CP` (confirmed planet) / `KP` (known planet) → **planet** (label 1)
* `FP` (false positive) → **catalog false positive** (label 0)
* `PC` (planet candidate) is excluded from training because its status is unresolved.

The goal is to reproduce the human `CP/KP` vs `FP` catalog disposition from seven
tabular catalog measurements, so that likely false positives can be triaged
without manual vetting.

## Dataset

Source: [NASA Exoplanet Archive — TESS Objects of Interest](https://exoplanetarchive.ipac.caltech.edu/).

Features used by the model:

| Feature | Description |
| --- | --- |
| `pl_orbper` | Orbital period (days) |
| `pl_trandurh` | Transit duration (hours) |
| `pl_trandep` | Transit depth (ppm) |
| `st_tmag` | TESS-band magnitude of the host star |
| `st_teff` | Stellar effective temperature (K) |
| `st_logg` | Stellar surface gravity, log(g) |
| `st_rad` | Stellar radius (solar radii) |

`src/load_data.py` downloads the current TOI table when no cached local copy is
available. The Streamlit demo instead loads the frozen model artifact and does
not need the dataset at runtime.

Because multiple TOIs can orbit the same host star and share stellar properties,
the TIC ID (`tid`) is used as a grouping key so that observations from one star
never span a train/validation boundary.

## Evaluation protocol

* Observations are grouped by host star using TIC ID (`tid`).
* A single `StratifiedGroupKFold` split (5 folds, `random_state=42`) separates a
  development set from a final holdout. The two sets share **no** host stars.
* Model comparison and hyperparameter tuning use five-fold stratified group
  cross-validation on the development set only.
* Preprocessing lives inside each model `Pipeline`; imputation statistics are
  learned only from the training fold.
* **F1-score** is the declared primary model-selection metric.
* The classification threshold is fixed at **0.5**.
* Feature importance and error analysis use development data and out-of-fold
  predictions.
* The feature set, preprocessing pipeline, hyperparameters, metric, and threshold
  were **frozen before the holdout was opened**.
* The final holdout was evaluated **once** and was not used to revise anything.

Development uses 2,077 observations; the holdout contains 519 observations from
previously unseen host stars.

## Final model

```
SimpleImputer(strategy="median", add_indicator=True)
  → RandomForestClassifier(
        n_estimators=500,
        max_depth=20,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
    )
classification threshold = 0.5
```

### Final performance

| Evaluation set  | Accuracy | Precision | Recall | F1-score |
| --------------- | -------: | --------: | -----: | -------: |
| Development OOF |    83.2% |     81.1% |  88.1% |    84.5% |
| Final holdout   |    85.2% |     83.7% |  88.4% |    86.0% |

Final holdout confusion matrix (519 observations):

* 237 correctly identified planets
* 205 correctly identified catalog false positives
* 46 catalog false positives classified as planets
* 31 missed planets

The final holdout result was consistent with, and slightly higher than, the
group-aware development estimate. No modeling decision was changed after the
holdout was evaluated.

## Model optimization (v0.5)

The original Random Forest achieved an out-of-fold F1-score of 83.5%.

v0.5 evaluated 40 hyperparameter configurations across five group-aware folds
(200 cross-validation fits). The search varied number of trees, maximum tree
depth, minimum observations per leaf, and features considered at each split.

The three leading configurations produced practically equivalent validation
F1-scores. A regularized candidate (`min_samples_leaf=2`, `max_depth=20`) was
selected before opening the holdout, sacrificing less than one tenth of a
percentage point in mean validation F1 relative to the highest-ranked
configuration.

An unconstrained comparison forest produced trees as deep as 28, with 15.3%
exceeding depth 20 — confirming that the selected depth limit actively
constrains part of the forest rather than acting as a cosmetic parameter.

A post-hoc diagnostic using development out-of-fold probabilities found a maximum
F1-score of 84.9% at a threshold of 0.47, compared with 84.5% at the frozen
threshold of 0.5. Because the difference was modest and the diagnostic was
performed after the final evaluation, the preregistered threshold and all
reported holdout results were left unchanged.

## Interpretability and error analysis (v0.4)

* Out-of-fold permutation importance identified orbital period, transit duration,
  and transit depth as the strongest contributors to validation accuracy.
* Impurity and permutation importance produced different rankings, showing that
  frequent internal use of a feature does not necessarily imply an equally
  strong contribution to generalization.
* The untuned Random Forest produced 935 true positives, 773 true negatives,
  231 false positives, and 138 false negatives across its out-of-fold
  predictions.
* 65 Random Forest errors were made with confidence of at least 0.80,
  representing 17.6% of its errors.
* All three model families misclassified 210 of the same observations. Of these
  shared errors, 151 were false positives and 59 were false negatives.
* A simple majority-vote ensemble reached an F1-score of 83.1% and did not
  improve upon Random Forest.
* The main shared limitation was distinguishing planet-like catalog false
  positives from genuine planets using the current feature set.

## Inference flow

* `artifacts/exoscout_v0_5.joblib` contains the frozen pipeline trained
  exclusively on the development set, together with its feature order, threshold,
  class labels, and metadata.
* `src/predict.py` loads the artifact, validates the input, builds the required
  tabular observation, and returns the model output.
* `app.py` provides the Streamlit interface and displays the result.

The exported artifact was checked against three previously evaluated holdout
observations; its scores and predicted labels matched the original notebook
inference.

## Current limitations

* The model uses only seven tabular catalog measurements.
* The final Random Forest retains a substantial train–validation performance gap.
* Repeated modeling decisions on the same development folds may introduce some
  model-selection bias.
* The independent holdout contains 519 observations, so its metrics remain
  subject to sampling variation.
* Feature importance describes predictive associations, not causal astrophysical
  relationships. Correlated features may share or redistribute importance.
* Predicted scores have **not** been calibrated and must not be interpreted as
  reliable probabilities.
* Training uses only resolved `CP`, `KP`, and `FP` labels; unresolved Planet
  Candidates may represent a harder population.
* Raw TESS light curves are not used.
* The TOI catalog changes over time, so rerunning the notebooks against a later
  archive snapshot may not exactly reproduce the historical v0.5 metrics.
* The original holdout has already been evaluated and cannot be treated as an
  untouched test set for future model revisions.

## Version history

### v0.1
* First Logistic Regression baseline; established the binary CP/KP vs FP task.

### v0.2
* Analyzed missing values by class.
* Added median imputation and missingness indicators.
* Introduced cross-validation and experiment tracking.

### v0.3
* Introduced group-aware splitting by host star.
* Created an untouched final holdout.
* Compared Logistic Regression, Random Forest, and HistGradientBoosting.
* Selected Random Forest as the leading development model.

### v0.4
* Compared impurity and out-of-fold permutation importance.
* Performed out-of-fold error and confidence analysis.
* Compared error overlap across model families.
* Tested and rejected a simple majority-vote ensemble.
* Kept the final holdout untouched.

### v0.5
* Performed controlled group-aware hyperparameter optimization.
* Compared the leading configurations fold by fold.
* Selected a regularized final Random Forest pipeline.
* Verified the effective depth of unconstrained trees.
* Evaluated per-class out-of-fold performance.
* Froze the complete modeling procedure.
* Evaluated once on the untouched final holdout (F1 86.0%).

### v0.5.1
* Exported the frozen v0.5 pipeline as a reusable model artifact.
* Added validated inference logic outside the notebooks.
* Added a lightweight Streamlit demonstration.
* Added local execution instructions and an MIT License.

## Future work

* Investigate probability calibration before interpreting model scores as
  reliable probabilities.
* Evaluate distribution shift before applying the model to unresolved Planet
  Candidates.
* Explore additional physically motivated catalog features.
* Extract features from TESS light curves.
* Validate any future model revision on a new independent temporal or external
  evaluation set.
