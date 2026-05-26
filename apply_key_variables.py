import os
import re
import pickle
import pandas as pd
import gspread

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from configs.hospital import HOSPITAL_MAP
from configs.main_columns import HEADER_COLUMNS
from sheet_append import (
    SPREADSHEET_TITLE_BACKUP_PREFIX,
    append_dataframe,
    build_spreadsheet_title,
    _longitudinal_id_from_subjid,
)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CSV_PATH = "key_variables.csv"

TEMPLATE_SPREADSHEET_ID = "11fAsZXk1-M3Ekg_ZVIQvPGfz9dVVwUlMZUVQG-E0E-8"

VARIABLES_SHEET_NAME = "Variables"

AUTH_DIR = "auth"
TOKEN_PATH = os.path.join(AUTH_DIR, "token.pickle")

# NOTE: Google OAuth 인증 후 gspread 클라이언트를 반환
def get_google_client():
    creds = None

    # 이전 실행에서 저장한 토큰이 있으면 재사용
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 만료: refresh_token를 이용해 브라우저 인증 없이 갱신
            creds.refresh(Request())
        else:
            # 최초 인증: credentials.json으로 브라우저 로그인
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_console()

        # 다음 실행을 위해 토큰 저장
        os.makedirs(AUTH_DIR, exist_ok=True)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return gspread.authorize(creds)

# NOTE: 예시
#      HYUMC-14067      → Longitudinal_ID = 0
#      HYUMC-14067-01   → Longitudinal_ID = 1
#      JBUH-28049-00    → Longitudinal_ID = 0 (baseline, -00 접미사)
#
def parse_subject_info(subjid_batch):
    match = re.match(r"^([A-Z0-9]+)-(\d+)(?:-\d+)?$", str(subjid_batch))

    if not match:
        raise ValueError(f"SUBJID_batch 형식 오류: {subjid_batch}")

    hospital_id = match.group(1)
    kosar_id = match.group(2)
    project_id = f"{hospital_id}-{kosar_id}"

    longitudinal_id = _longitudinal_id_from_subjid(subjid_batch)

    hospital = HOSPITAL_MAP.get(hospital_id, "")

    if hospital == "":
        raise ValueError(f"Hospital_ID 매칭 실패: {hospital_id}")

    return {
        "Hospital": hospital,
        "Hospital_ID": hospital_id,
        "KoSAR_ID": kosar_id,
        "Project_ID": project_id,
        "Longitudinal_ID": longitudinal_id,
    }


def _is_missing(value):
    if pd.isna(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def fill_header_columns_na(df, na_value="NA"):
    """HEADER_COLUMNS에 해당하는 열에서만 결측·공란을 na_value로 채운다."""
    result = df.copy()
    for col in HEADER_COLUMNS:
        if col not in result.columns:
            continue
        missing = result[col].map(_is_missing)
        # 만약 해당 열의 dtype이 숫자(float 등이면) 문자열 할당 전에 object로 변환합니다.
        if pd.api.types.is_numeric_dtype(result[col]):
            result[col] = result[col].astype(object)
        result.loc[missing, col] = na_value
 
    return result


# NOTE: CSV 읽기·검증·병합을 Google API 호출 전에 종료 
def build_final_dataframe():
    df = pd.read_csv(CSV_PATH)

    if "SUBJID_batch" not in df.columns:
        raise ValueError("CSV에 SUBJID_batch 컬럼이 없습니다.")

    subject_info_list = df["SUBJID_batch"].apply(parse_subject_info)
    subject_df = pd.DataFrame(subject_info_list.tolist())
    final_df = pd.concat([subject_df, df], axis=1)

    return fill_header_columns_na(final_df)


def get_variables_worksheet(spreadsheet):
    try:
        return spreadsheet.worksheet(VARIABLES_SHEET_NAME)
    except gspread.WorksheetNotFound:
        return spreadsheet.worksheet("Variables")


def main():
    print("1/4 CSV 처리 중...")
    final_df = build_final_dataframe()

    print("2/4 Google 인증 중...")
    gc = get_google_client()

    print("3/4 백업 복사본 생성 중...")
    copied_title = build_spreadsheet_title(SPREADSHEET_TITLE_BACKUP_PREFIX)
    copied_sheet = gc.copy(
        file_id=TEMPLATE_SPREADSHEET_ID,
        title=copied_title,
    )
    print(f"백업 복사 완료: {copied_title}")
    print(
        f"백업 Spreadsheet ID: {copied_sheet.id}, "
        f"https://docs.google.com/spreadsheets/d/{copied_sheet.id}/edit"
    )

    print("4/4 템플릿 Variables 탭에 데이터 추가 중...")
    template_sheet = gc.open_by_key(TEMPLATE_SPREADSHEET_ID)
    worksheet = get_variables_worksheet(template_sheet)
    append_dataframe(
        worksheet,
        final_df,
        missing_value="NA",
        na_headers=HEADER_COLUMNS,
    )
    print(
        f"템플릿 반영 완료: "
        f"https://docs.google.com/spreadsheets/d/{TEMPLATE_SPREADSHEET_ID}/edit"
    )
    print("모든 작업 완료")


if __name__ == "__main__":
    main()