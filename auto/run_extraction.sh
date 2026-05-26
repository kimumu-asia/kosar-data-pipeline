#!/bin/bash
set -e

# 이 스크립트 위치: .../test/auto/ → 프로젝트 루트는 상위 디렉터리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "[작업 디렉터리] ${PROJECT_ROOT}"
echo "[실행 시작] 주요 지표 생성 (simplify.py)"
python simplify.py &
PID_SIMPLIFY=$!

wait $PID_SIMPLIFY
echo "[실행 완료] 주요 지표 생성 완료"

echo "[실행 시작] 스프레드시트에 데이터 추가 (apply_key_variables.py)"
python apply_key_variables.py &
PID_APPLY_KEY_VARIABLES=$!

wait $PID_APPLY_KEY_VARIABLES
echo "[실행 완료] 스프레드시트에 데이터 추가 완료"

echo "[실행 완료] 모든 작업이 완료되었습니다."
