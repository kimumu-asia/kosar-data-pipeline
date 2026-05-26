#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

from configs.main_columns import FILTERING_COLUMNS, HEADER_COLUMNS

# Option: 필요한 열만 추출한다. KoSAR 관리문서에 반영할 때 사용하는 용도
target_csv_path = 'struct.csv'

df = pd.read_csv(target_csv_path)

if len(FILTERING_COLUMNS) != len(HEADER_COLUMNS):
    raise ValueError(
        f"FILTERING_COLUMNS({len(FILTERING_COLUMNS)})와 "
        f"HEADER_COLUMNS({len(HEADER_COLUMNS)}) 길이가 다릅니다."
    )

# NOTE. key_variables.csv의 컬럼명을 리네임
# KoSAR 관리문서의 헤더와 동일하도록 WT area => WT로 변경
#  - zip(FILTERING_COLUMNS, HEADER_COLUMNS)로 같은 위치끼리 (원본, 헤더) 쌍 생성
#    예: ("WT_area_Trachea", "WT_Trachea")
#  - dict(...)로 리네임용 매핑 생성
COLUMN_RENAME = dict(zip(FILTERING_COLUMNS, HEADER_COLUMNS))

df[FILTERING_COLUMNS].rename(columns=COLUMN_RENAME).to_csv(
    "key_variables.csv", index=False
)
