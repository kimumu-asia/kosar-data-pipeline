"""Spreadsheet 기존 행 업데이트: (Project_ID, Longitudinal_ID)로 행을 찾아 값 병합."""

import pandas as pd
from gspread.utils import rowcol_to_a1

from sheet_append import (
    _cell_key,
    _header_key,
    _row_by_project_id,
    _subject_key,
    format_sheet_rows,
    update_spreadsheet_title,
)


def _cell_val(value):
    if pd.isna(value):
        return ""
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, AttributeError):
            pass
    return value


def _subject_key_from_df_row(series):
    """df 행의 Project_ID, Longitudinal_ID로 시트 행 매칭 키를 만든다."""
    pid = _cell_key(series["Project_ID"])
    if not pid:
        raise ValueError("df 행의 Project_ID가 비어 있습니다.")
    return _subject_key(pid, series["Longitudinal_ID"])


def merge_df_into_rows_by_subjid(worksheet, df):
    """
    시트 Variables 탭에서 (Project_ID, Longitudinal_ID)가 일치하는 기존 행을 찾아
    df에 있는 열만 덮어쓴다. 해당 subject 행이 없으면 오류. append_rows는 사용하지 않는다.

    Args:
        worksheet: gspread Variables 탭 워크시트.
        df: Project_ID, Longitudinal_ID 열이 포함된 DataFrame.

    동작:
        1) 시트에서 (Project_ID, Longitudinal_ID) → 행 번호(1-based) 맵을 만든다.
        2) df 각 행의 키로 기존 행을 찾아 복사 후, df·헤더가 맞는 셀만 갱신한다.
        3) batch_update로 한 번에 반영한다.
        4) 갱신된 행에 Arial·가운데 정렬(format_sheet_rows)을 적용한다.
        5) 스프레드시트 문서 제목을 최종 반영일 기준으로 갱신한다.
    """
    for col in ("Project_ID", "Longitudinal_ID"):
        if col not in df.columns:
            raise ValueError(f"df에 '{col}' 열이 필요합니다.")
    # 시트를 2차원 문자열 리스트로 가져온다. existing[0] = 헤더 행, 이후 = 데이터 행.
    existing = worksheet.get_all_values()

    if not existing:
        raise ValueError("Variables 워크시트가 비어 있어 헤더를 알 수 없습니다.")

    headers = existing[0]
    ncols = len(headers)

    # 헤더 문자열(strip) → 열 인덱스(0-based). 시트의 헤더와 df의 열 이름 매칭에 사용
    #    key_to_col = {"SUBJID_batch": 0, "Age": 1, "Sex": 2}
    key_to_col = {_header_key(h): i for i, h in enumerate(headers)}
    row_by_subject = _row_by_project_id(existing)

    # 행마다 "범위 + 갱신 후 전체 행 값"을 쌓아두고, 마지막에 한 번에 batch_update.
    updates = []
    # 변경할 subject의 행 번호 목록
    updated_row_nums = []

    for _, series in df.iterrows():
        lookup_key = _subject_key_from_df_row(series)
        row_num = row_by_subject.get(lookup_key)
        if row_num is None:
            pid, lid = lookup_key
            raise ValueError(
                "시트에 해당 subject 행이 없습니다 "
                f"(Project_ID={pid!r}, Longitudinal_ID={lid!r})."
            )

        # 갱신 전 그 행 스냅샷을 복사하고, 헤더 열 개수까지 길이를 맞춘다 (짧은 행 패딩).
        base = list(existing[row_num - 1])
        while len(base) < ncols:
            base.append("")

        # df에 있는 열 중, 시트 헤더와 이름이 같은 열만 덮어쓴다. 나머지 시트 열은 그대로 유지.
        # 시트에만 있고 df에 없는 열은 손대지 않음.
        for col_name in df.columns:
            hk = _header_key(str(col_name))
            if hk not in key_to_col:
                continue
            ci = key_to_col[hk]
            while len(base) <= ci:
                base.append("")
            base[ci] = _cell_val(series[col_name])

        end_a1 = rowcol_to_a1(row_num, ncols)
        updates.append({"range": f"A{row_num}:{end_a1}", "values": [base[:ncols]]})
        updated_row_nums.append(row_num)

    worksheet.batch_update(updates, value_input_option="USER_ENTERED")
    update_spreadsheet_title(worksheet)

    for row_num in sorted(set(updated_row_nums)):
        format_sheet_rows(worksheet, row_num, row_num, ncols)
