import re
from datetime import datetime

from gspread.utils import rowcol_to_a1

SPREADSHEET_TITLE_PREFIX = "KoSAR_CT 현황 v2.0"
SPREADSHEET_TITLE_BACKUP_PREFIX = "KoSAR_CT 현황 backup v2.0"


def _header_key(name):
    return str(name).strip()


def _cell_key(raw):
    if raw is None or (isinstance(raw, float) and raw != raw):
        return ""
    return _header_key(str(raw))


def _normalize_longitudinal_id(raw):
    key = _cell_key(raw)
    if not key:
        return "0"
    try:
        return str(int(float(key)))
    except ValueError:
        return key


def _project_id_from_subjid(subjid_batch):
    match = re.match(r"^([A-Z0-9]+)-(\d+)(?:-\d+)?$", str(subjid_batch))
    if not match:
        return _cell_key(subjid_batch)
    return f"{match.group(1)}-{match.group(2)}"


def _longitudinal_id_from_subjid(subjid_batch):
    """SUBJID_batch 접미사에서 Longitudinal_ID를 유도한다.

    HYUMC-14067 → 0, HYUMC-14067-01 → 1, JBUH-28049-00 → 0 (baseline).
    """
    match = re.match(r"^[A-Z0-9]+-\d+-(\d+)$", str(subjid_batch))
    if not match:
        return 0
    return int(match.group(1))


def _subject_key(project_id, longitudinal_id):
    return (_cell_key(project_id), _normalize_longitudinal_id(longitudinal_id))


def _subject_key_from_row(row, key_to_col, subjid_col="SUBJID_batch"):
    """시트 행(list)에서 (Project_ID, Longitudinal_ID) 키를 만든다."""
    pid = ""
    if "Project_ID" in key_to_col:
        col_idx = key_to_col["Project_ID"]
        if col_idx < len(row):
            pid = _cell_key(row[col_idx])

    lid = "0"
    if "Longitudinal_ID" in key_to_col:
        col_idx = key_to_col["Longitudinal_ID"]
        if col_idx < len(row):
            lid = _normalize_longitudinal_id(row[col_idx])

    if not pid and subjid_col in key_to_col:
        col_idx = key_to_col[subjid_col]
        if col_idx < len(row):
            subjid = row[col_idx]
            pid = _project_id_from_subjid(subjid)
            if "Longitudinal_ID" not in key_to_col:
                lid = _longitudinal_id_from_subjid(subjid)

    return _subject_key(pid, lid)


def _subject_key_from_series(series, subjid_col="SUBJID_batch"):
    """DataFrame 행(Series)에서 (Project_ID, Longitudinal_ID) 키를 만든다."""
    pid = ""
    if "Project_ID" in series.index:
        pid = _cell_key(series["Project_ID"])

    lid = "0"
    if "Longitudinal_ID" in series.index:
        lid = _normalize_longitudinal_id(series["Longitudinal_ID"])

    if not pid and subjid_col in series.index:
        subjid = series[subjid_col]
        pid = _project_id_from_subjid(subjid)
        if "Longitudinal_ID" not in series.index:
            lid = _longitudinal_id_from_subjid(subjid)

    return _subject_key(pid, lid)


def _existing_subject_keys(existing, subjid_col="SUBJID_batch"):
    """시트에 이미 있는 (Project_ID, Longitudinal_ID) 집합."""
    if not existing:
        return set()

    headers = existing[0]
    key_to_col = {_header_key(h): i for i, h in enumerate(headers)}

    if "Project_ID" not in key_to_col:
        preview = ", ".join(_header_key(h) for h in headers[:20] if _header_key(h))
        raise ValueError(
            "시트에 'Project_ID' 열이 필요합니다.\n"
            f"헤더(일부): {preview}"
        )

    found = set()
    for row in existing[1:]:
        key = _subject_key_from_row(row, key_to_col, subjid_col=subjid_col)
        if key[0]:
            found.add(key)
    return found


def _row_by_project_id(existing, subjid_col="SUBJID_batch"):
    """(Project_ID, Longitudinal_ID) → 시트 행 번호(1-based). sheet_row_merge용."""
    if not existing:
        return {}

    headers = existing[0]
    key_to_col = {_header_key(h): i for i, h in enumerate(headers)}

    if "Project_ID" not in key_to_col:
        preview = ", ".join(_header_key(h) for h in headers[:20] if _header_key(h))
        raise ValueError(
            "시트에 'Project_ID' 열이 필요합니다.\n"
            f"헤더(일부): {preview}"
        )

    # NOTE: row_by는 시트의 subject 키 → 행 번호(1-based) 맵을 만든다. key가 튜플임
    # {('KDH-21033', '0'): 2, ('KDH-21035', '0'): 3, ...}
    row_by = {}
    duplicates = []
    for r, row in enumerate(existing[1:], start=2):
        key = _subject_key_from_row(row, key_to_col, subjid_col=subjid_col)
        if not key[0]:
            continue
        if key in row_by:
            duplicates.append(key)
        else:
            row_by[key] = r

    if duplicates:
        dup_preview = [
            f"Project_ID={pid}, Longitudinal_ID={lid}"
            for pid, lid in sorted(set(duplicates))[:20]
        ]
        raise ValueError(
            "시트에 동일 (Project_ID, Longitudinal_ID)가 중복됩니다: "
            + "; ".join(dup_preview)
        )
    return row_by

def build_spreadsheet_title(prefix=SPREADSHEET_TITLE_PREFIX, when=None):
    """스프레드시트 문서 제목 문자열을 만든다. 예: KoSAR_CT 현황 v2.0 (2025.05.22)"""
    stamp = (when or datetime.now()).strftime("%Y.%m.%d")
    return f"{prefix} ({stamp})"


def update_spreadsheet_title(worksheet, prefix=SPREADSHEET_TITLE_PREFIX, when=None):
    """데이터 반영 후 스프레드시트 문서 제목을 갱신한다."""
    worksheet.spreadsheet.update_title(build_spreadsheet_title(prefix, when=when))


def format_sheet_rows(worksheet, start_row, end_row, num_cols):
    """지정 행 범위에 Arial·가운데 정렬을 적용한다 (1-based 행/열)."""
    if start_row > end_row or num_cols < 1:
        return

    cell_range = f"{rowcol_to_a1(start_row, 1)}:{rowcol_to_a1(end_row, num_cols)}"
    worksheet.format(
        cell_range,
        {
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {"fontFamily": "Arial"},
        },
    )


# NOTE: spreadsheet에 표기하기 위한 decorate 처리
#       특정 헤더에 대한 결측치 표기 처리 ("NA") , 이 외 빈 문자열 처리
def decorate_dataframe(headers, df, missing_value="", na_headers=None):
    """시트 제목행 순서에 맞춰 DataFrame 행을 2차원 리스트로 변환한다."""
    col_map = {_header_key(col): col for col in df.columns}
    na_header_keys = {_header_key(h) for h in (na_headers or [])}
    rows = []

    for _, series in df.iterrows():
        row = []
        for header in headers:
            key = _header_key(header)
            use_na = key in na_header_keys
            if key and key in col_map:
                row.append(series[col_map[key]])
            else:
                row.append(missing_value if use_na else "")
        rows.append(row)

    return rows


def append_dataframe(
    worksheet, df, missing_value="", na_headers=None, subjid_col="SUBJID_batch"
):
    """기존 데이터는 유지하고, 시트 제목행에 맞춰 마지막 행 아래에 추가한다.

    중복 판별: (Project_ID, Longitudinal_ID) 쌍이 시트·df 모두에 있으면 skip.
    df는 Project_ID·Longitudinal_ID 열이 있으면 사용하고, 없으면 SUBJID_batch에서 유도한다.
    """
    if subjid_col not in df.columns:
        raise ValueError(f"DataFrame에 '{subjid_col}' 컬럼이 없습니다.")

    existing = worksheet.get_all_values()

    if not existing:
        headers = df.columns.tolist()
        data_rows = df.values.tolist()
        worksheet.update([headers] + data_rows)
        if data_rows:
            format_sheet_rows(worksheet, 2, 1 + len(data_rows), len(headers))
            update_spreadsheet_title(worksheet)
        return

    existing_keys = _existing_subject_keys(existing, subjid_col=subjid_col)
    df_keys = df.apply(
        lambda row: _subject_key_from_series(row, subjid_col=subjid_col),
        axis=1,
    )
    is_existing = df_keys.isin(existing_keys) & df_keys.map(lambda k: bool(k[0]))

    for pid, lid in df_keys[is_existing].unique():
        print(
            f"  skip: Project_ID={pid}, Longitudinal_ID={lid}, 이미 시트에 데이터가 존재함"
        )

    df_append = df.loc[~is_existing]
    if df_append.empty:
        print("추가할 신규 행이 없습니다.")
        return

    headers = existing[0]
    rows = decorate_dataframe(
        headers, df_append, missing_value=missing_value, na_headers=na_headers
    )

    if not rows:
        return

    start_row = len(existing) + 1
    worksheet.append_rows(rows)
    format_sheet_rows(worksheet, start_row, start_row + len(rows) - 1, len(headers))
    update_spreadsheet_title(worksheet)
    print(f"  추가 완료: {len(rows)}행")
