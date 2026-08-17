import pandas as pd
import os
data_path = "data/toi.csv"

url = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=select+toi,tfopwg_disp,pl_orbper,pl_trandurh,pl_trandep,"
    "st_tmag,st_teff,st_logg,st_rad+from+toi"
    "&format=csv"
)
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    df = pd.read_csv(url)
    df.to_csv(data_path,index=False)



filtered_df = df[df["tfopwg_disp"].isin(["CP", "KP", "FP"])]

mapping ={
'CP': 1,
'KP' : 1,
'FP' :0

}

filtered_df["target"]= filtered_df["tfopwg_disp"].map(mapping)
print(filtered_df[["tfopwg_disp", "target"]].head())
