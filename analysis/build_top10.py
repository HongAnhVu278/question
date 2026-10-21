from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd  
# take in a csv path and return a dict

OUT = {"9995", "9996", "9997", "9998", "9999"} # skip, missing, invalid, no response
DIDNT_FIT = {"9704", "9705"}
GENDERS = {1.0 : "girls", 2.0: "boys"}

def build(csv_path):
    # build df, force type of OCOD3 and CNTSCHID to be string
    df = pd.read_csv(csv_path, dtype={"OCOD3": str, "CNTSCHID": str})

    # drop students who are: no code, missing-data code, no gender
    df = df[df["OCOD3"].notna() & ~df["OCOD3"].isin(OUT) & df["ST004D01T"].isin(GENDERS)]

    entries = []
    # one entry per country, with n for each gender

    for (code, name), country in df.groupby(["CNT","country"]):
        entry = {"code": code, "name": name}

        # calculate for each panel
        for g, key in GENDERS.items():
            
            # group by code in genders
            group = country[country["ST004D01T"]==g]

            total_weight = group["W_FSTUWT"].sum()

            # calculate didnt_feed
            vague = group["OCOD3"].isin(DIDNT_FIT)

            didnt_fit = group.loc[vague,"W_FSTUWT"].sum() / total_weight

            # calculate bars
            jobs = group[~vague]
            per_code = jobs.groupby("OCOD3").agg(
                labels=("occupation", "first"),
                weight=("W_FSTUWT", "sum"),
                students=("W_FSTUWT", "size"),
            )

            per_code = per_code.reset_index()
            per_code = per_code.sort_values(["weight", "OCOD3"],ascending=[False, True])
            per_code = per_code.head(10)

            bars = []

            for row in per_code.itertuples():
                bars.append({
                    "isco": row.OCOD3,
                    "label": row.labels,
                    "share": float(row.weight/total_weight),
                    "count": int(row.students)
                })


            entry[key] = {"n": len(group), "didnt_fit": didnt_fit, "bars": bars}

        entries.append(entry)


    return {
        "year": 2025,
        "min_students": 30,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }

if __name__ == "__main__":
    csv_path = Path(__file__).parent / "data" / "raw" / "pisa2025_aspirations.csv"
    res = build(csv_path)

    print(len(res["entries"]), "countries")
    usa = next(e for e in res["entries"] if e["code"] == "USA")
    print(json.dumps(usa,indent=2))

    # save result in json file
    OUT_FILE = Path(__file__).parent.parent / "client" / "data" / "top10_2025.json"
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        json.dump(res, f, indent=2)
    print("wrote",OUT_FILE)

    

    