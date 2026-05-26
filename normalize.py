#!/usr/bin/env python
# coding: utf-8

import argparse

import numpy as np
import pandas as pd


def dtr_pred(age: pd.Series, height: pd.Series, sex: pd.Series) -> pd.Series:
    return (
        12.79
        - 0.13 * np.log(age)
        - 5.82 * np.log(height) * sex
        + 3.01 * np.log(age) * np.log(height)
    )


def wt_pred(age: pd.Series, height: pd.Series, sex: pd.Series) -> pd.Series:
    h2 = height**2
    pred = np.log(
        9.11
        - 1.02 * np.log(age)
        - 0.98 * h2 * sex
        + 1.01 * h2 * np.log(age)
    )
    return pred


# Wall Thickness Area
WT_NORM_PAIRS = [
    ("WT_Trachea_norm", "WT_area_Trachea"),
    ("WT_RMB_norm", "WT_area_RMB"),
    ("WT_TriRUL_norm", "WT_area_TriRUL"),
    ("WT_RB1_norm", "WT_area_RB1"),
    ("WT_RB2_norm", "WT_area_RB2"),
    ("WT_RB3_norm", "WT_area_RB3"),
    ("WT_Bronint_norm", "WT_area_Bronint"),
    ("WT_RB4+5_norm", "WT_area_RB4+5"),
    ("WT_RB4_norm", "WT_area_RB4"),
    ("WT_RB5_norm", "WT_area_RB5"),
    ("WT_RLL6_norm", "WT_area_RLL6"),
    ("WT_RB6_norm", "WT_area_RB6"),
    ("WT_RLL7_norm", "WT_area_RLL7"),
    ("WT_RB7_norm", "WT_area_RB7"),
    ("WT_TriRLL_norm", "WT_area_TriRLL"),
    ("WT_RB8_norm", "WT_area_RB8"),
    ("WT_RB9+10_norm", "WT_area_RB9+10"),
    ("WT_RB9_norm", "WT_area_RB9"),
    ("WT_RB10_norm", "WT_area_RB10"),
    ("WT_LMB_norm", "WT_area_LMB"),
    ("WT_TriLUL_norm", "WT_area_TriLUL"),
    ("WT_LB1+2+3_norm", "WT_area_LB1+2+3"),
    ("WT_LB1+2_norm", "WT_area_LB1+2"),
    ("WT_LB1_norm", "WT_area_LB1"),
    ("WT_LB2_norm", "WT_area_LB2"),
    ("WT_LB3_norm", "WT_area_LB3"),
    ("WT_LB4+5_norm", "WT_area_LB4+5"),
    ("WT_LB4_norm", "WT_area_LB4"),
    ("WT_LB5_norm", "WT_area_LB5"),
    ("WT_LLB6_norm", "WT_area_LLB6"),
    ("WT_LB6_norm", "WT_area_LB6"),
    ("WT_TriLLB_norm", "WT_area_TriLLB"),
    ("WT_LB8_norm", "WT_area_LB8"),
    ("WT_LB9+10_norm", "WT_area_LB9+10"),
    ("WT_LB9_norm", "WT_area_LB9"),
    ("WT_LB10_norm", "WT_area_LB10"),
    ("WT_sRUL_norm", "WT_area_sRUL"),
    ("WT_sRML_norm", "WT_area_sRML"),
    ("WT_sRLL_norm", "WT_area_sRLL"),
    ("WT_sLUL_norm", "WT_area_sLUL"),
    ("WT_sLLL_norm", "WT_area_sLLL"),
]

# Diameter Height
D_NORM_PAIRS = [
    ("Dh_Trachea_norm", "Dh_Trachea"),
    ("Dh_RMB_norm", "Dh_RMB"),
    ("Dh_TriRUL_norm", "Dh_TriRUL"),
    ("Dh_RB1_norm", "Dh_RB1"),
    ("Dh_RB2_norm", "Dh_RB2"),
    ("Dh_RB3_norm", "Dh_RB3"),
    ("Dh_Bronint_norm", "Dh_Bronint"),
    ("Dh_RB4+5_norm", "Dh_RB4+5"),
    ("Dh_RB4_norm", "Dh_RB4"),
    ("Dh_RB5_norm", "Dh_RB5"),
    ("Dh_RLL6_norm", "Dh_RLL6"),
    ("Dh_RB6_norm", "Dh_RB6"),
    ("Dh_RLL7_norm", "Dh_RLL7"),
    ("Dh_RB7_norm", "Dh_RB7"),
    ("Dh_TriRLL_norm", "Dh_TriRLL"),
    ("Dh_RB8_norm", "Dh_RB8"),
    ("Dh_RB9+10_norm", "Dh_RB9+10"),
    ("Dh_RB9_norm", "Dh_RB9"),
    ("Dh_RB10_norm", "Dh_RB10"),
    ("Dh_LMB_norm", "Dh_LMB"),
    ("Dh_TriLUL_norm", "Dh_TriLUL"),
    ("Dh_LB1+2+3_norm", "Dh_LB1+2+3"),
    ("Dh_LB1+2_norm", "Dh_LB1+2"),
    ("Dh_LB1_norm", "Dh_LB1"),
    ("Dh_LB2_norm", "Dh_LB2"),
    ("Dh_LB3_norm", "Dh_LB3"),
    ("Dh_LB4+5_norm", "Dh_LB4+5"),
    ("Dh_LB4_norm", "Dh_LB4"),
    ("Dh_LB5_norm", "Dh_LB5"),
    ("Dh_LLB6_norm", "Dh_LLB6"),
    ("Dh_LB6_norm", "Dh_LB6"),
    ("Dh_TriLLB_norm", "Dh_TriLLB"),
    ("Dh_LB8_norm", "Dh_LB8"),
    ("Dh_LB9+10_norm", "Dh_LB9+10"),
    ("Dh_LB9_norm", "Dh_LB9"),
    ("Dh_LB10_norm", "Dh_LB10"),
    ("Dh_sRUL_norm", "Dh_sRUL"),
    ("Dh_sRML_norm", "Dh_sRML"),
    ("Dh_sRLL_norm", "Dh_sRLL"),
    ("Dh_sLUL_norm", "Dh_sLUL"),
    ("Dh_sLLL_norm", "Dh_sLLL"),
]

EXTRACT_COLUMNS = [
    "SUBJID_batch",
    "Dh_Trachea_norm",
    "Dh_RMB_norm",
    "Dh_TriRUL_norm",
    "Dh_Bronint_norm",
    "Dh_RB4+5_norm",
    "Dh_RLL6_norm",
    "Dh_RLL7_norm",
    "Dh_TriRLL_norm",
    "Dh_RB9+10_norm",
    "Dh_LMB_norm",
    "Dh_TriLUL_norm",
    "Dh_LB1+2+3_norm",
    "Dh_LB1+2_norm",
    "Dh_LB4+5_norm",
    "Dh_LLB6_norm",
    "Dh_TriLLB_norm",
    "Dh_LB9+10_norm",
    "Dh_sRUL_norm",
    "Dh_sRML_norm",
    "Dh_sRLL_norm",
    "Dh_sLUL_norm",
    "Dh_sLLL_norm",
    "WT_Trachea_norm",
    "WT_RMB_norm",
    "WT_TriRUL_norm",
    "WT_Bronint_norm",
    "WT_RB4+5_norm",
    "WT_RLL6_norm",
    "WT_RLL7_norm",
    "WT_TriRLL_norm",
    "WT_RB9+10_norm",
    "WT_LMB_norm",
    "WT_TriLUL_norm",
    "WT_LB1+2+3_norm",
    "WT_LB1+2_norm",
    "WT_LB4+5_norm",
    "WT_LLB6_norm",
    "WT_TriLLB_norm",
    "WT_LB9+10_norm",
    "WT_sRUL_norm",
    "WT_sRML_norm",
    "WT_sRLL_norm",
    "WT_sLUL_norm",
    "WT_sLLL_norm",
]


def build_normalized_dataframe(source: pd.DataFrame) -> pd.DataFrame:
    """
    clinical_struct 등 struct + 임상(Sex, Age, Height) 컬럼이 있는 DataFrame을 받아
    정규화 열만 담은 final_df를 반환한다.
    """
    f = source.copy()
    for col in ("Age", "Height", "Sex"):
        if col not in f.columns:
            raise ValueError(f"정규화에 필요한 컬럼이 없습니다: {col}")

    f["Height"] = f["Height"] / 100

    f["Dtr_pred"] = dtr_pred(f["Age"], f["Height"], f["Sex"])
    f["WT_pred"] = wt_pred(f["Age"], f["Height"], f["Sex"])

    wt = f["WT_pred"]
    dtr = f["Dtr_pred"]

    for norm_col, area_col in WT_NORM_PAIRS:
        if area_col not in f.columns:
            raise KeyError(f"WT 정규화 소스 컬럼 없음: {area_col}")
        f[norm_col] = (f[area_col] / wt).round(6)

    for norm_col, dh_col in D_NORM_PAIRS:
        if dh_col not in f.columns:
            raise KeyError(f"Dh 정규화 소스 컬럼 없음: {dh_col}")
        f[norm_col] = (f[dh_col] / dtr).round(6)

    missing_out = [c for c in EXTRACT_COLUMNS if c not in f.columns]
    if missing_out:
        raise ValueError(f"EXTRACT_COLUMNS 중 생성되지 않은 열: {missing_out}")

    return f[EXTRACT_COLUMNS].copy()


def main_cli():
    parser = argparse.ArgumentParser(description="성별/나이/키를 기준으로 struct 변수 정규화")
    parser.add_argument(
        "--input",
        default="clinical_struct.csv",
        help="입력 CSV (기본: clinical_struct.csv)",
    )
    parser.add_argument(
        "--output",
        default="normalization_variables.csv",
        help="저장 CSV (기본: normalization_variables.csv)",
    )
    args = parser.parse_args()
    inp = pd.read_csv(args.input)
    out_df = build_normalized_dataframe(inp)
    out_df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main_cli()
