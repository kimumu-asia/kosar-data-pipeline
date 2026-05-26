"""
clinical_struct.csv → normalize.py 동일 처리 → 입력한 스프레드시트(복사 없음)
Variables 탭에서 SUBJID_batch 행을 찾아 정규화 열만 병합한다.
"""

import argparse

import pandas as pd

from apply_key_variables import get_google_client, get_variables_worksheet
from normalize import build_normalized_dataframe
from sheet_row_merge import merge_df_into_rows_by_subjid

DEFAULT_CLINICAL_CSV = "clinical_struct.csv"


def main():
    parser = argparse.ArgumentParser(
        description="템플릿 스프레드시트 ID로 Variables 탭 행 업데이트 (정규화 값 반영)",
    )
    parser.add_argument(
        "spreadsheet_id",
        help="업데이트할 Google Sheets 스프레드시트 ID (복사본이 아닌 원본/템플릿)",
    )
    parser.add_argument(
        "--input",
        "-i",
        default=DEFAULT_CLINICAL_CSV,
        help=f"clinical struct CSV 경로 (기본: {DEFAULT_CLINICAL_CSV})",
    )
    args = parser.parse_args()

    print(f"1/4 입력 CSV 읽기·정규화: {args.input}")
    final_df = build_normalized_dataframe(pd.read_csv(args.input))

    print("2/4 Google 연결...")
    gc = get_google_client()
    spreadsheet = gc.open_by_key(args.spreadsheet_id)

    print("3/4 Variables 워크시트 열기...")
    worksheet = get_variables_worksheet(spreadsheet)

    print("4/4 SUBJID_batch별 기존 행에 값 병합...")
    merge_df_into_rows_by_subjid(worksheet, final_df, subjid_col="SUBJID_batch")

    print("완료.")


if __name__ == "__main__":
    main()
