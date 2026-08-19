from collections.abc import Mapping
from pathlib import Path
from typing import Any

from joblib import load
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "exoscout_v0_5.joblib"
)

REQUIRED_ARTIFACT_KEYS = {
    "pipeline",
    "features",
    "classification_threshold",
    "class_labels",
    "version",
    "training_observations"
}

POSITIVE_FEATURES = {
    "pl_orbper",
    "pl_trandurh",
    "pl_trandep",
    "st_teff",
    "st_rad"
}

def load_model_artifact(
    artifact_path: Path = DEFAULT_ARTIFACT_PATH
) -> dict[str, Any]:
    if not artifact_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {artifact_path}"
        )

    artifact = load(artifact_path)

    missing_keys = (
        REQUIRED_ARTIFACT_KEYS
        - set(artifact)
    )

    if missing_keys:
        raise ValueError(
            "Model artifact is missing required keys: "
            f"{sorted(missing_keys)}"
        )

    return artifact


def _convert_value(
    value: Any,
    feature_name: str
) -> float:
    if value is None:
        return np.nan

    if isinstance(value, str) and not value.strip():
        return np.nan

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{feature_name} must be numeric or missing."
        ) from error

    if np.isnan(numeric_value):
        return np.nan

    if not np.isfinite(numeric_value):
        raise ValueError(
            f"{feature_name} must be finite."
        )

    if (
        feature_name in POSITIVE_FEATURES
        and numeric_value <= 0
    ):
        raise ValueError(
            f"{feature_name} must be greater than zero."
        )

    return numeric_value


def create_input_frame(
    values: Mapping[str, Any],
    features: list[str]
) -> pd.DataFrame:
    unexpected_features = (
        set(values)
        - set(features)
    )

    if unexpected_features:
        raise ValueError(
            "Unexpected features: "
            f"{sorted(unexpected_features)}"
        )

    observation = {
        feature: _convert_value(
            values.get(feature),
            feature
        )
        for feature in features
    }

    return pd.DataFrame(
        [observation],
        columns=features
    )


def predict_observation(
    values: Mapping[str, Any],
    artifact: dict[str, Any] | None = None
) -> dict[str, Any]:
    if artifact is None:
        artifact = load_model_artifact()

    input_frame = create_input_frame(
        values,
        artifact["features"]
    )

    planet_score = float(
        artifact["pipeline"]
        .predict_proba(input_frame)[0, 1]
    )

    predicted_label = int(
        planet_score
        >= artifact["classification_threshold"]
    )

    return {
        "predicted_label": predicted_label,
        "predicted_class": artifact[
            "class_labels"
        ][predicted_label],
        "planet_score": planet_score,
        "threshold": artifact[
            "classification_threshold"
        ]
    }