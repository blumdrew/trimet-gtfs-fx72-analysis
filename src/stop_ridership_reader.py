# -*- coding: utf-8 -*-

"""
    Author: Andrew Lindstrom
    Date: 2025-01-27
    Purpose: read stop ridership parser output, write csv file
"""

import pandas as pd

import os

def main():
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "stop_level_ridership_spring_2024"
    )
    data = []
    for item in os.listdir(path):
        if not item.endswith("txt"):
            continue
        ldf = pd.read_fwf(os.path.join(path, item), header=None)
        ldf.dropna(axis=0,how="all",inplace=True)
        ldf.replace(",","",inplace=True,regex=True)
        if max(ldf.columns) > 8:
            drop_cols = []
            prior_nan_count = 0
            for col in ldf.columns:
                d = ldf[col]
                nan_count = d.isna().astype(int).sum()
                if nan_count > 0:
                    # determine which way combination has to occur
                    if col == 3:
                        ldf[0] = (
                            ldf[0] 
                            + ldf[1].apply(lambda x: " " + str(x) if not pd.isnull(x) else None).fillna("")
                            + ldf[2].apply(lambda x: " " + str(x) if not pd.isnull(x) else None).fillna("")
                            + ldf[3].apply(lambda x: " " + str(x) if not pd.isnull(x) else None).fillna("")
                        )
                        drop_cols.append(1)
                        drop_cols.append(2)
                        drop_cols.append(3)
                    elif col == 2:
                        # combine 0, 1, 2 as strings
                        ldf[0] = (
                            ldf[0] 
                            + ldf[1].apply(lambda x: " " + str(x) if not pd.isnull(x) else None).fillna("")
                            + ldf[2].apply(lambda x: " " + str(x) if not pd.isnull(x) else None).fillna("")
                        )
                        drop_cols.append(1)
                        drop_cols.append(2)
                    elif col == 1:
                        # combine 0, 1 as strings
                        ldf[0] = ldf[0] + ldf[1].apply(lambda x: " " + str(x) if not pd.isnull(x) else None).fillna("")
                        drop_cols.append(1)
                        pass
                    elif prior_nan_count > 0:
                        # combine n-1, n as a merge of sorts
                        ldf[col] = ldf[[col,col-1]].sum()
                        drop_cols.append(col-1)
                        pass
                prior_nan_count = nan_count
                drop_cols = list(set(drop_cols))
            ldf.drop(drop_cols, axis=1, inplace=True)

        ldf.columns = [
            "stop_name","stop_id","direction","location","ons","offs",
            "total","DELETE_ME","monthly_lifts"
        ]
        data.append(ldf)
    df = pd.concat(data)
    df["total"] = pd.to_numeric(df["total"])
    df["ons"] = pd.to_numeric(df["ons"])
    df["offs"] = pd.to_numeric(df["offs"])
    df.to_csv(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "spring_2024_stop_level_ridership.csv"
        ),
        index=False
    )
    return

main()