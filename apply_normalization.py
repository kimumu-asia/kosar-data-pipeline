"""
clinical_struct.csv → 정규화 → 템플릿 Variables 탭 기존 subject 행에 정규화 열만 병합.

신규 행 추가(append) 없음. 시트에서 (Project_ID, Longitudinal_ID)로 행을 찾아 해당 행만 갱신.
"""

import argparse

import pandas as pd

from apply_key_variables import (
    TEMPLATE_SPREADSHEET_ID,
    get_google_client,
    get_variables_worksheet,
    parse_subject_info,
)
from normalize import build_normalized_dataframe
from sheet_row_merge import merge_df_into_rows_by_subjid

DEFAULT_CLINICAL_CSV = "clinical_struct.csv"


def main():
    parser = argparse.ArgumentParser(
        description="템플릿 Variables 탭에 정규화 값 반영",
    )
    parser.add_argument(
        "--input",
        "-i",
        default=DEFAULT_CLINICAL_CSV,
        help=f"clinical struct CSV 경로 (기본: {DEFAULT_CLINICAL_CSV})",
    )
    parser.add_argument(
        "--template-id",
        default=TEMPLATE_SPREADSHEET_ID,
        help=f"템플릿 스프레드시트 ID (기본: {TEMPLATE_SPREADSHEET_ID})",
    )
    args = parser.parse_args()

    print(f"1/4 입력 CSV 읽기·정규화: {args.input}")
    normalized = build_normalized_dataframe(pd.read_csv(args.input))
    subject_keys = pd.DataFrame(
        normalized["SUBJID_batch"].apply(parse_subject_info).tolist()
    )[["Project_ID", "Longitudinal_ID"]]
    final_df = pd.concat([subject_keys, normalized], axis=1)

    print("2/4 Google 연결...")
    gc = get_google_client()
    spreadsheet = gc.open_by_key(args.template_id)

    print("3/4 Variables 워크시트 열기...")
    worksheet = get_variables_worksheet(spreadsheet)

    print("4/4 (Project_ID, Longitudinal_ID) 기준 기존 행에 정규화 값 병합...")
    merge_df_into_rows_by_subjid(worksheet, final_df)

    print(
        f"완료: https://docs.google.com/spreadsheets/d/{args.template_id}/edit"
    )


if __name__ == "__main__":
    main()
