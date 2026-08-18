# ExoScout

ExoScout is a machine learning project that uses NASA TESS Objects of Interest data to distinguish confirmed/known exoplanets from false positives.

## Current Status

v0.2 improves the original Logistic Regression baseline with more rigorous missing-data handling and evaluation.

Missingness analysis showed that some features are missing much more frequently among false positives than among confirmed/known planets. Instead of dropping incomplete rows, v0.2 uses median imputation while preserving missingness through binary indicators.

The model is evaluated using 5-fold stratified cross-validation.

Current performance:
- Accuracy: 73.5% ± 1.7%
- Planet precision: 72.4% ± 1.8%
- Planet recall: 78.9% ± 3.4%
- Planet F1-score: 75.5% ± 1.7%

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

- Only Logistic Regression has been evaluated so far.
- Missing values are imputed using a simple median strategy.
- Current evaluation uses only tabular catalog features.
- No feature importance or detailed error analysis has been performed yet.
- Raw TESS light curves are not yet used.


## Roadmap

### v0.3
- Compare Logistic Regression with tree-based models
- Analyze feature importance
- Perform detailed error analysis

### Future
- Score unresolved Planet Candidates
- Investigate probability calibration
- Explore features extracted from TESS light curves
- Build a lightweight interactive demo