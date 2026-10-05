"""
Download the PISA 2018 student questionnaire file and extract the
career-aspiration columns into a lightweight CSV for exploratory analysis.

Run locally (needs internet access to oecd.org):
    pip install pyreadstat pandas requests
    python get_pisa_aspirations.py

Output: pisa2018_aspirations.csv
"""

import os
import zipfile
import requests
import pyreadstat

URL = "https://webfs.oecd.org/pisa2018/SPSS_STU_QQQ.zip"
ZIP_PATH = "SPSS_STU_QQQ.zip"
SAV_NAME = "CY07_MSU_STU_QQQ.sav"  # file inside the zip; adjust if it differs
OUT_CSV = "pisa2018_aspirations.csv"

COLS = [
    "CNT",         # country
    "ST004D01T",   # gender
    "OCOD3",       # aspired occupation, ISCO-coded (the "what they want to be")
    "BSMJ",        # expected occupational status (ISEI score)
    "ESCS",        # socioeconomic status index
    "W_FSTUWT",    # final student weight (use for any aggregate estimate)
    "PV1MATH",     # first plausible value, math (achievement, optional)
    "PV1READ",     # first plausible value, reading
    "PV1SCIE",     # first plausible value, science
]


def download():
    if os.path.exists(ZIP_PATH):
        print(f"{ZIP_PATH} already present, skipping download.")
        return
    print(f"Downloading {URL} ...")
    with requests.get(URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(ZIP_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print("Download complete.")


def unzip():
    with zipfile.ZipFile(ZIP_PATH) as z:
        names = z.namelist()
        sav = next((n for n in names if n.lower().endswith(".sav")), None)
        if sav is None:
            raise SystemExit(f"No .sav found in zip. Contents: {names}")
        if not os.path.exists(sav):
            print(f"Extracting {sav} ...")
            z.extract(sav)
        return sav


def extract(sav_path):
    print("Reading selected columns...")
    df, meta = pyreadstat.read_sav(sav_path, usecols=COLS)

    labels = meta.variable_value_labels
    if "ST004D01T" in labels:
        df["gender"] = df["ST004D01T"].map(labels["ST004D01T"])
    if "OCOD3" in labels:
        df["occupation"] = df["OCOD3"].map(labels["OCOD3"])

    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV}: {len(df):,} rows, {df.shape[1]} columns")
    print(df[["CNT", "gender", "occupation", "BSMJ"]].head())


if __name__ == "__main__":
    download()
    sav = unzip()
    extract(sav)
