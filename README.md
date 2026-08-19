# ExoScout

ExoScout is a machine learning project that uses NASA TESS Objects of Interest data to distinguish confirmed and known exoplanets from false positives.

## Current Status

v0.5 completes the controlled optimization and final evaluation of the tabular Random Forest pipeline.

Because multiple TOIs can belong to the same host star and share stellar properties, TIC ID (`tid`) is used to keep observations from the same star within the same data partition.

Model development uses five-fold `StratifiedGroupKFold` cross-validation on 2,077 development observations. A separate holdout containing 519 observations from previously unseen host stars was evaluated once after the complete modeling procedure had been frozen.

### Final Model

The final pipeline contains:

- Median imputation
- Missingness indicators
- 500 Random Forest trees
- Maximum tree depth of 20
- Minimum of two observations per leaf
- Square-root feature sampling at each split
- Classification threshold of 0.5

### Final Performance

| Evaluation set | Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|
| Development OOF | 83.2% | 81.1% | 88.1% | 84.5% |
| Final holdout | 85.2% | 83.7% | 88.4% | 86.0% |

The final holdout confusion matrix contains:

- 237 correctly identified planets
- 205 correctly identified catalog false positives
- 46 catalog false positives classified as planets
- 31 missed planets

The final holdout result was consistent with, and slightly higher than, the group-aware development estimate. No modeling decision was changed after the holdout was evaluated.

## Model Optimization

The original Random Forest achieved an out-of-fold F1-score of 83.5%.

v0.5 evaluated 40 hyperparameter configurations across five group-aware folds, producing 200 cross-validation fits. The search varied:

- Number of trees
- Maximum tree depth
- Minimum observations per leaf
- Number of features considered at each split

The three leading configurations produced practically equivalent validation F1-scores. A regularized candidate was selected before opening the holdout, favoring `min_samples_leaf=2` and `max_depth=20` while sacrificing less than one tenth of a percentage point in mean validation F1 relative to the highest-ranked configuration.

An unconstrained comparison forest produced trees as deep as 28, with 15.3% exceeding depth 20. This confirmed that the selected depth limit actively constrains part of the forest rather than acting as a cosmetic parameter.

## v0.4 Interpretability and Error Analysis

- Out-of-fold permutation importance identified orbital period, transit duration, and transit depth as the strongest contributors to validation accuracy.
- Impurity and permutation importance produced different rankings, showing that frequent internal use of a feature does not necessarily imply an equally strong contribution to generalization.
- The untuned Random Forest produced 935 true positives, 773 true negatives, 231 false positives, and 138 false negatives across its out-of-fold predictions.
- 65 Random Forest errors were made with confidence of at least 0.80, representing 17.6% of its errors.
- All three model families misclassified 210 of the same observations. Of these shared errors, 151 were false positives and 59 were false negatives.
- A simple majority-vote ensemble reached an F1-score of 83.1% and did not improve upon Random Forest.
- The main shared limitation was distinguishing planet-like catalog false positives from genuine planets using the current feature set.

## Dataset

Data source: NASA Exoplanet Archive — TESS Objects of Interest (TOI).

The current model uses:

- Orbital period
- Transit duration
- Transit depth
- TESS magnitude
- Stellar effective temperature
- Stellar surface gravity
- Stellar radius

Labels:

- CP / KP → planet
- FP → false positive

Planet Candidates (PC) are excluded from training because their status is unresolved.

## Project Structure

```text
exoscout/
├── data/
├── notebooks/
│   ├── 04_feature_and_error_analysis.ipynb
│   └── 05_model_optimization_and_final_evaluation.ipynb
├── src/
├── requirements.txt
└── README.md
```

## Evaluation Protocol

- Observations are grouped by host star using TIC ID (`tid`).
- Development and final holdout sets contain no shared host stars.
- Model comparison and hyperparameter tuning use five-fold stratified group cross-validation.
- Preprocessing is contained inside each model pipeline.
- Imputation statistics are learned only from the relevant training fold during cross-validation.
- F1-score is declared as the primary model-selection metric.
- The classification threshold is fixed at 0.5.
- Feature importance and error analysis use development data and out-of-fold predictions.
- The final feature set, preprocessing pipeline, hyperparameters, metric, and threshold were frozen before the holdout was opened.
- The final holdout was evaluated once and was not used to revise the pipeline.

## Current Limitations

- The current model uses only seven tabular catalog measurements.
- The final Random Forest retains a substantial train–validation performance gap.
- Repeated modeling decisions on the same development folds may introduce some model-selection bias.
- The independent holdout contains 519 observations, so its metrics remain subject to sampling variation.
- Feature importance describes predictive associations and does not establish causal astrophysical relationships.
- Correlated features may share or redistribute their measured importance.
- Predicted probabilities have not been calibrated.
- Training uses only resolved CP, KP, and FP labels; unresolved Planet Candidates may represent a more difficult population.
- Raw TESS light curves are not yet used.

## Version History

### v0.1

- Built the first Logistic Regression baseline.
- Established the binary CP/KP versus FP task.

### v0.2

- Analyzed missing values by class.
- Added median imputation and missingness indicators.
- Introduced cross-validation and experiment tracking.

### v0.3

- Introduced group-aware splitting by host star.
- Created an untouched final holdout.
- Compared Logistic Regression, Random Forest, and HistGradientBoosting.
- Selected Random Forest as the leading development model.

### v0.4

- Compared impurity and out-of-fold permutation importance.
- Performed out-of-fold error and confidence analysis.
- Compared error overlap across model families.
- Tested and rejected a simple majority-vote ensemble.
- Kept the final holdout untouched.

### v0.5

- Performed controlled group-aware hyperparameter optimization.
- Compared the leading configurations fold by fold.
- Selected a regularized final Random Forest pipeline.
- Verified the effective depth of unconstrained trees.
- Evaluated per-class out-of-fold performance.
- Froze the complete modeling procedure.
- Evaluated once on the untouched final holdout.
- Reached a final holdout F1-score of 86.0%.

## Future Work

- Score unresolved Planet Candidates.
- Investigate probability calibration before interpreting scores as reliable probabilities.
- Explore additional physically motivated catalog features.
- Extract features from TESS light curves.
- Validate future model revisions under a new independent evaluation protocol.
- Build a lightweight interactive demo.