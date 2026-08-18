# ExoScout

ExoScout is a machine learning project that uses NASA TESS Objects of Interest data to distinguish confirmed/known exoplanets from false positives.

## Current Status

v0.1 implements a Logistic Regression baseline using tabular features from the NASA Exoplanet Archive.

Baseline performance:
- Accuracy: ~71.7%
- Planet precision: ~73%
- Planet recall: ~80%
- Planet F1-score: ~76%

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

## Current Limitations

Missing rows are currently removed.
Evaluation is based on a single train/test split.
Only Logistic Regression has been tested.
The project currently uses catalog features rather than raw TESS light curves.


## Roadmap

Analyze missing-data patterns
Add missing-value imputation
Add cross-validation
Compare multiple models
Perform feature importance and error analysis
Explore unresolved Planet Candidates
Investigate TESS light curves