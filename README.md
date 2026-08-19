# ExoScout

ExoScout is a machine learning project that uses NASA TESS Objects of Interest data to distinguish confirmed and known exoplanets from catalog false positives.

## Current Status

v0.5 completes the controlled optimization and final evaluation of the tabular Random Forest pipeline.

Because multiple TOIs can belong to the same host star and share stellar properties, TIC ID (`tid`) is used to keep observations from the same star within the same data partition.

Model development uses five-fold `StratifiedGroupKFold` cross-validation on 2,077 development observations. A separate holdout containing 519 observations from previously unseen host stars was evaluated once after the complete modeling procedure had been frozen.

The repository also includes a lightweight Streamlit demonstration that loads the frozen v0.5 pipeline and classifies individual catalog observations without retraining the model.

### Final Model

The final pipeline contains:

* Median imputation
* Missingness indicators
* 500 Random Forest trees
* Maximum tree depth of 20
* Minimum of two observations per leaf
* Square-root feature sampling at each split
* Classification threshold of 0.5

### Final Performance

| Evaluation set  | Accuracy | Precision | Recall | F1-score |
| --------------- | -------: | --------: | -----: | -------: |
| Development OOF |    83.2% |     81.1% |  88.1% |    84.5% |
| Final holdout   |    85.2% |     83.7% |  88.4% |    86.0% |

The final holdout confusion matrix contains:

* 237 correctly identified planets
* 205 correctly identified catalog false positives
* 46 catalog false positives classified as planets
* 31 missed planets

The final holdout result was consistent with, and slightly higher than, the group-aware development estimate. No modeling decision was changed after the holdout was evaluated.

## Interactive Demo

The Streamlit application accepts the seven catalog measurements used by the model and returns:

* A planet-like or catalog false-positive-like classification
* The uncalibrated planet score produced by the Random Forest
* The frozen classification threshold
* A warning when missing measurements are imputed

The application validates the inputs and rejects non-numeric text, infinite values, and non-positive values for physical quantities that must be greater than zero.

The displayed score is not a calibrated probability that an observation is a real exoplanet. The application demonstrates the behavior of the existing catalog classifier; it does not discover or confirm exoplanets, retrain the model, or use final holdout observations.

## Quickstart

Python 3.13 is recommended.

```bash
git clone https://github.com/stoppo22/exoscout.git
cd exoscout

python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

The application will open in the browser. Empty fields are treated as missing catalog measurements and processed by the frozen preprocessing pipeline.

## Model Optimization

The original Random Forest achieved an out-of-fold F1-score of 83.5%.

v0.5 evaluated 40 hyperparameter configurations across five group-aware folds, producing 200 cross-validation fits. The search varied:

* Number of trees
* Maximum tree depth
* Minimum observations per leaf
* Number of features considered at each split

The three leading configurations produced practically equivalent validation F1-scores. A regularized candidate was selected before opening the holdout, favoring `min_samples_leaf=2` and `max_depth=20` while sacrificing less than one tenth of a percentage point in mean validation F1 relative to the highest-ranked configuration.

An unconstrained comparison forest produced trees as deep as 28, with 15.3% exceeding depth 20. This confirmed that the selected depth limit actively constrains part of the forest rather than acting as a cosmetic parameter.

A post-hoc diagnostic using development out-of-fold probabilities found a maximum F1-score of 84.9% at a threshold of 0.47, compared with 84.5% at the frozen threshold of 0.5. Because the difference was modest and the diagnostic was performed after the final evaluation, the preregistered threshold and all reported holdout results remained unchanged.

## v0.4 Interpretability and Error Analysis

* Out-of-fold permutation importance identified orbital period, transit duration, and transit depth as the strongest contributors to validation accuracy.
* Impurity and permutation importance produced different rankings, showing that frequent internal use of a feature does not necessarily imply an equally strong contribution to generalization.
* The untuned Random Forest produced 935 true positives, 773 true negatives, 231 false positives, and 138 false negatives across its out-of-fold predictions.
* 65 Random Forest errors were made with confidence of at least 0.80, representing 17.6% of its errors.
* All three model families misclassified 210 of the same observations. Of these shared errors, 151 were false positives and 59 were false negatives.
* A simple majority-vote ensemble reached an F1-score of 83.1% and did not improve upon Random Forest.
* The main shared limitation was distinguishing planet-like catalog false positives from genuine planets using the current feature set.

## Dataset

Data source: NASA Exoplanet Archive — TESS Objects of Interest (TOI).

The current model uses:

* Orbital period
* Transit duration
* Transit depth
* TESS magnitude
* Stellar effective temperature
* Stellar surface gravity
* Stellar radius

Labels:

* CP / KP → planet
* FP → false positive

Planet Candidates (PC) are excluded from training because their status is unresolved.

`src/load_data.py` downloads the current TOI table when no cached local copy is available. The demonstration instead loads the fixed exported model artifact and does not require the dataset at runtime.

## Project Structure

```text
exoscout/
├── artifacts/
│   └── exoscout_v0_5.joblib
├── data/
├── notebooks/
│   ├── 01_baseline.ipynb
│   ├── 02_missingness_and_cv.ipynb
│   ├── 03_model_comparison.ipynb
│   ├── 04_feature_and_error_analysis.ipynb
│   └── 05_model_optimization_and_final_evaluation.ipynb
├── src/
│   ├── load_data.py
│   └── predict.py
├── app.py
├── LICENSE
├── requirements.txt
└── README.md
```

## Inference Flow

The demonstration uses three components:

* `artifacts/exoscout_v0_5.joblib` contains the frozen pipeline trained exclusively on the development set, together with its feature order, threshold, labels, and metadata.
* `src/predict.py` loads the artifact, validates the input, constructs the required tabular observation, and obtains the model output.
* `app.py` provides the Streamlit interface and displays the result.

The exported artifact was checked against three previously evaluated holdout observations. Its scores and predicted labels matched the original notebook inference.

## Evaluation Protocol

* Observations are grouped by host star using TIC ID (`tid`).
* Development and final holdout sets contain no shared host stars.
* Model comparison and hyperparameter tuning use five-fold stratified group cross-validation.
* Preprocessing is contained inside each model pipeline.
* Imputation statistics are learned only from the relevant training fold during cross-validation.
* F1-score is declared as the primary model-selection metric.
* The classification threshold is fixed at 0.5.
* Feature importance and error analysis use development data and out-of-fold predictions.
* The final feature set, preprocessing pipeline, hyperparameters, metric, and threshold were frozen before the holdout was opened.
* The final holdout was evaluated once and was not used to revise the pipeline.

## Current Limitations

* The current model uses only seven tabular catalog measurements.
* The final Random Forest retains a substantial train–validation performance gap.
* Repeated modeling decisions on the same development folds may introduce some model-selection bias.
* The independent holdout contains 519 observations, so its metrics remain subject to sampling variation.
* Feature importance describes predictive associations and does not establish causal astrophysical relationships.
* Correlated features may share or redistribute their measured importance.
* Predicted scores have not been calibrated and must not be interpreted as reliable probabilities.
* Training uses only resolved CP, KP, and FP labels; unresolved Planet Candidates may represent a more difficult population.
* Raw TESS light curves are not used.
* The TOI catalog changes over time, so rerunning the notebooks against a later archive snapshot may not exactly reproduce the historical v0.5 metrics.
* The original holdout has already been evaluated and cannot be treated as an untouched test set for future model revisions.

## Version History

### v0.1

* Built the first Logistic Regression baseline.
* Established the binary CP/KP versus FP task.

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
* Evaluated once on the untouched final holdout.
* Reached a final holdout F1-score of 86.0%.

## Future Work

* Investigate probability calibration before interpreting model scores as reliable probabilities.
* Evaluate distribution shift before applying the model to unresolved Planet Candidates.
* Explore additional physically motivated catalog features.
* Extract features from TESS light curves.
* Validate any future model revision using a new independent temporal or external evaluation set.

## License

This project is available under the MIT License.
