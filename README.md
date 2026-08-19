# ExoScout

ExoScout is a machine learning project that uses NASA TESS Objects of Interest data to distinguish confirmed and known exoplanets from false positives.

## Current Status

v0.4 analyzes how the current models make predictions and where they fail under a group-aware evaluation protocol.

Because multiple TOIs can belong to the same host star and share stellar properties, TIC ID (`tid`) is used to keep observations from the same star within the same data partition.

Model comparison and interpretation are performed using five-fold `StratifiedGroupKFold` cross-validation on the development set. A separate final holdout set remains untouched.

### Out-of-Fold Development Performance

| Model | Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|
| Random Forest | 82.2% | 80.2% | 87.1% | 83.5% |
| HistGradientBoosting | 81.6% | 80.5% | 84.9% | 82.6% |
| Logistic Regression | 72.7% | 71.7% | 78.1% | 74.8% |

Random Forest remains the leading development model.

These are pooled out-of-fold development metrics, not final holdout results.

### v0.4 Findings

- Out-of-fold permutation importance identifies orbital period, transit duration, and transit depth as the strongest contributors to validation accuracy.
- Impurity and permutation importance produce different rankings, showing that frequent internal use of a feature does not necessarily imply an equally strong contribution to generalization.
- Random Forest produces 935 true positives, 773 true negatives, 231 false positives, and 138 false negatives across the out-of-fold predictions.
- 65 Random Forest errors are made with confidence of at least 0.80, representing 17.6% of its errors.
- All three model families misclassify 210 of the same observations. Of these shared errors, 151 are false positives and 59 are false negatives.
- A simple majority-vote ensemble reaches an F1-score of 83.1% and does not improve upon Random Forest.
- The main shared limitation is distinguishing planet-like catalog false positives from genuine planets using the current feature set.

## Dataset

Data source: NASA Exoplanet Archive - TESS Objects of Interest (TOI).

The current model uses:

- Orbital period
- Transit duration
- Transit depth
- TESS magnitude
- Stellar effective temperature
- Stellar surface gravity
- Stellar radius

Labels:

- CP / KP -> planet
- FP -> false positive

Planet Candidates (PC) are excluded from training because their status is unresolved.



## Project Structure

```text
exoscout/
├── data/
├── notebooks/
├── src/
├── requirements.txt
└── README.md
```

## Evaluation Protocol

- Observations are grouped by host star using TIC ID (`tid`).
- Development and final holdout sets contain no shared host stars.
- Model comparison uses five-fold stratified group cross-validation.
- Preprocessing is contained inside each model pipeline.
- Imputation statistics are learned only from the relevant training fold.
- Feature importance and error analysis use development data and out-of-fold predictions.
- The final holdout remains isolated until the modeling procedure has been frozen.

## Current Limitations

- The models have not yet undergone controlled hyperparameter tuning.
- The current feature set contains only seven tabular catalog measurements.
- Feature importance describes predictive associations and does not establish causal astrophysical relationships.
- Correlated features may share or redistribute their measured importance.
- Predicted probabilities have not been calibrated.
- The final holdout has intentionally not yet been evaluated.
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

## Roadmap

### v0.5

- Perform controlled group-aware hyperparameter tuning.
- Select and freeze the final tabular pipeline.
- Evaluate once on the untouched final holdout.

### Future

- Score unresolved Planet Candidates.
- Investigate probability calibration.
- Explore features extracted from TESS light curves.
- Build a lightweight interactive demo.