# ExoScout

ExoScout is a machine learning project that uses NASA TESS Objects of Interest data to distinguish confirmed/known exoplanets from false positives.

## Current Status

v0.3 compares linear and nonlinear model families under a group-aware evaluation protocol.

Because multiple TOIs can belong to the same host star and share stellar properties, TIC ID (`tid`) is used to keep observations from the same star within the same data partition.

A separate final holdout set remains untouched, while model comparison is performed using 5-fold stratified group cross-validation on the development set.

Current results:

- Logistic Regression: 72.7% ± 0.7% accuracy
- Random Forest: 82.2% ± 1.1% accuracy
- HistGradientBoosting: 81.6% ± 1.0% accuracy

Random Forest is currently the leading model.
The development and final holdout sets preserve nearly identical class proportions despite grouping by host star.


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
├── src/
├── requirements.txt
└── README.md
```


## Current Limitations

- Model comparison has been performed without substantial hyperparameter tuning.
- Current models use only tabular catalog features.
- Feature importance and detailed error analysis have not yet been performed.
- The final holdout set has intentionally not yet been evaluated.
- Raw TESS light curves are not yet used.

## Roadmap

### v0.4
- Analyze feature importance
- Compute permutation importance
- Perform detailed error analysis
- Compare errors across model families

### v0.5
- Perform controlled hyperparameter tuning
- Select the final tabular pipeline
- Evaluate once on the untouched final holdout

### Future
- Score unresolved Planet Candidates
- Investigate probability calibration
- Explore features extracted from TESS light curves
- Build a lightweight interactive demo