import streamlit as st

from src.predict import (
    load_model_artifact,
    predict_observation
)


st.set_page_config(
    page_title="ExoScout",
    page_icon="🪐",
    layout="centered"
)


FEATURE_CONFIG = {
    "pl_orbper": {
        "label": "Orbital period (days)",
        "default": "10.07",
        "help": "Time required to complete one orbit."
    },
    "pl_trandurh": {
        "label": "Transit duration (hours)",
        "default": "2.40",
        "help": "Duration of the observed transit."
    },
    "pl_trandep": {
        "label": "Transit depth (ppm)",
        "default": "839.90",
        "help": "Decrease in stellar brightness during transit."
    },
    "st_tmag": {
        "label": "TESS magnitude",
        "default": "9.07",
        "help": "Brightness of the host star in the TESS band."
    },
    "st_teff": {
        "label": "Stellar effective temperature (K)",
        "default": "5552",
        "help": "Effective temperature of the host star."
    },
    "st_logg": {
        "label": "Stellar log(g)",
        "default": "4.62",
        "help": "Logarithmic surface gravity of the host star."
    },
    "st_rad": {
        "label": "Stellar radius (solar radii)",
        "default": "0.79",
        "help": "Radius of the host star relative to the Sun."
    }
}


@st.cache_resource
def get_model_artifact():
    return load_model_artifact()


st.title("🪐 ExoScout")

st.write(
    "A lightweight demonstration of the frozen ExoScout v0.5 "
    "Random Forest pipeline trained on NASA TESS Objects of Interest."
)

st.info(
    "This application demonstrates a catalog classification model. "
    "It does not discover or confirm exoplanets."
)

try:
    artifact = get_model_artifact()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()


with st.form("exoscout_input_form"):
    st.subheader("Observation features")

    st.caption(
        "Delete a value to represent a missing catalog measurement."
    )

    columns = st.columns(2)
    values = {}

    for index, feature in enumerate(artifact["features"]):
        configuration = FEATURE_CONFIG[feature]

        with columns[index % 2]:
            values[feature] = st.text_input(
                configuration["label"],
                value=configuration["default"],
                help=configuration["help"]
            )

    submitted = st.form_submit_button(
        "Classify observation",
        type="primary",
        use_container_width=True
    )


if submitted:
    missing_count = sum(
        not str(value).strip()
        for value in values.values()
    )

    if missing_count == len(values):
        st.error(
            "Enter at least one measurement before classification."
        )
    else:
        try:
            result = predict_observation(
                values,
                artifact
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.subheader("Model output")

            if result["predicted_label"] == 1:
                st.success(
                    "Classification: planet-like observation"
                )
            else:
                st.warning(
                    "Classification: catalog false-positive-like observation"
                )

            st.metric(
                "Uncalibrated planet score",
                f"{result['planet_score']:.1%}"
            )

            st.progress(result["planet_score"])

            st.caption(
                "Frozen classification threshold: "
                f"{result['threshold']:.2f}"
            )

            if missing_count:
                st.warning(
                    f"{missing_count} missing measurement(s) were handled "
                    "by the pipeline's median imputation and missingness "
                    "indicators."
                )

            with st.expander("How to interpret this result"):
                st.write(
                    "The score is produced by the frozen v0.5 Random Forest. "
                    "It is not a calibrated probability that the object is "
                    "a real exoplanet. The model was trained on resolved "
                    "catalog labels and may not generalize to unresolved "
                    "Planet Candidates."
                )


st.divider()

st.caption(
    "Model version: v0.5 · "
    "7 tabular features · "
    "500-tree Random Forest · "
    "threshold 0.5"
)