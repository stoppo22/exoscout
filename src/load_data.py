from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "toi.csv"

URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=select+toi,tid,tfopwg_disp,pl_orbper,pl_trandurh,pl_trandep,"
    "st_tmag,st_teff,st_logg,st_rad+from+toi"
    "&format=csv"
)


def load_data():
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.read_csv(URL)
        DATA_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        df.to_csv(DATA_PATH, index=False)

    return df