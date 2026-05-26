#!/bin/bash
set -e

# 이 스크립트 위치: .../test/auto/ → 프로젝트 루트는 상위 디렉터리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "[작업 디렉터리] ${PROJECT_ROOT}"
echo "[실행 시작] 정규화 변수 CSV 생성 (normalize.py)"
python normalize.py

echo "[실행 완료] 정규화 변수 CSV 생성 완료"

echo "[실행 시작] 템플릿 시트 정규화 반영 (apply_normalization.py)"
python apply_normalization.py --template-id 1u1vV293HHdOIsta7I58qTb5TlKMPnuHZ0JiMUYDmZvQ

echo "[실행 완료] 템플릿 시트 정규화 반영 완료"

echo "[실행 완료] 모든 작업이 완료되었습니다."
