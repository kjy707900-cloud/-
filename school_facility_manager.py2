"""교내 시설 고장 신고 및 처리 관리 시스템

실행:
    python -m pip install -r requirements.txt
    python -m streamlit run school_facility_manager.py

주의: 이 프로그램은 학교 과제용 시제품입니다. 실제 학교에서 운영하려면
학교 승인, 계정 인증, 서버 및 데이터 백업 등 추가 보안 조치가 필요합니다.
"""

# 코드 읽는 순서
# 1. 기본 설정: 건물·고장 종류 목록과 저장 경로를 정함.
# 2. 데이터 함수: CSV 읽기/쓰기, 긴급도 추천, 사진 저장, 신고 등록/검색/수정을 담당함.
# 3. 화면 함수: 학생·교사 화면과 관리자 화면을 구성함.
# 4. main: 전체 화면을 배치하고 프로그램 실행을 시작함.
#
# 기본 문법: def는 함수 정의, if는 조건 판단, for는 반복, return은 결과 반환임.
# with는 폼·탭 등의 화면 영역을 묶고, try/except는 오류 발생 시 안내 처리를 담당함.
# DataFrame은 행과 열로 된 표, dict는 항목 이름과 값을 묶는 자료형임.
# 함수의 -> 표시는 반환 자료형 힌트임. # 뒤의 주석은 실행되지 않음.
# 버튼이나 입력으로 화면이 갱신되면 Streamlit은 코드를 위에서부터 다시 실행함.
# session_state는 같은 사용자 세션 안에서 로그인 상태 등을 유지함.
# 신고와 사진은 서버의 로컬 CSV/폴더에 저장됨. 외부 데이터베이스 저장 방식은 아님.

# 자료형 힌트의 평가를 미룸. 자료형 힌트는 입력값과 반환값의 종류를 설명하며, 값을 자동 변환하지는 않음.
from __future__ import annotations

# 운영체제의 환경 변수에서 관리자 암호를 읽기 위한 모듈을 불러옴.
import os
# 신고 번호에 사용할 무작위 식별자를 만들기 위한 모듈을 불러옴.
import uuid
# 신고 등록 및 수정 시간을 기록하기 위한 기능을 불러옴.
from datetime import datetime
# 파일과 폴더의 경로를 다루는 Path를 불러옴.
from pathlib import Path
# 업로드 객체의 자료형을 제한하지 않는 Any 자료형 힌트를 불러옴.
from typing import Any

# 표 형태의 신고 데이터를 읽고, 합치고, 분석하는 pandas를 pd라는 이름으로 불러옴.
import pandas as pd
# 입력창, 버튼, 표 등 웹 화면을 만드는 Streamlit을 st라는 이름으로 불러옴.
import streamlit as st


# -----------------------------------------------------------------------------
# 기본 설정 및 저장 경로
# -----------------------------------------------------------------------------
# 현재 파이썬 파일이 있는 폴더의 절대 경로를 구함.
APP_DIR = Path(__file__).resolve().parent
# 신고 CSV 파일을 보관할 data 폴더의 경로를 정함.
DATA_DIR = APP_DIR / "data"
# 첨부 사진을 보관할 uploads 폴더의 경로를 정함.
UPLOAD_DIR = APP_DIR / "uploads"
# 신고 데이터를 저장할 CSV 파일의 전체 경로를 정함.
REPORTS_FILE = DATA_DIR / "facility_reports.csv"

# 신고 표에 사용할 열 이름과 저장 순서를 정함. 아래 각 항목은 신고 한 건의 정보임.
COLUMNS = [
    "report_id",  # 신고를 구별하는 번호
    "created_at",  # 처음 신고한 시각
    "reporter_type",  # 학생 또는 교사 구분
    "building",  # 선택한 건물 이름
    "location_detail",  # 층과 교실 등 상세 위치
    "category",  # 고장 종류
    "title",  # 신고 제목
    "description",  # 고장 상황 설명
    "priority",  # 추천 또는 수정된 긴급도
    "status",  # 현재 처리 상태
    "manager_note",  # 관리자의 처리 메모
    "updated_at",  # 마지막으로 수정한 시각
    "image_path",  # 앱 폴더 기준 첨부 사진 경로
]

# 고장 종류 선택창에 표시할 항목을 정함.
CATEGORIES = ["책상·의자", "전기·조명", "냉난방", "컴퓨터·프로젝터", "문·창문", "수도·화장실", "기타"]
# 건물 선택창에 표시할 학교 시설 8곳을 사용자가 지정한 순서대로 정함.
BUILDINGS = ["만대관", "덕린관", "단재관", "급식실", "기숙사", "운동장", "체육관", "귀촌관"]
# 관리자가 선택할 수 있는 처리 상태와 통계 표시 순서를 정함.
STATUSES = ["접수", "확인 중", "조치 예정", "처리 완료", "보류"]
# 긴급도 선택창의 항목과 순서를 정함.
PRIORITIES = ["긴급", "높음", "보통", "낮음"]

# 실제 운영 전에는 환경 변수 FACILITY_ADMIN_PASSWORD에 별도 암호를 설정하세요.
# 환경 변수의 관리자 암호를 읽고, 설정이 없으면 시연용 기본 암호를 사용함.
ADMIN_PASSWORD = os.environ.get("FACILITY_ADMIN_PASSWORD", "admin1234")
# 현재 암호가 시연용 기본값인지 비교하기 위한 값을 정함.
DEFAULT_ADMIN_PASSWORD = "admin1234"
# 사진 최대 용량을 바이트 단위로 정함. 5 × 1024 × 1024바이트임.
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
# 첨부를 허용할 사진 파일의 확장자 목록을 집합으로 정함.
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def ensure_storage() -> None:
    """신고 데이터와 사진을 저장할 폴더를 준비한다."""
    # data 폴더를 만듦. 상위 폴더도 함께 만들고, 이미 있으면 그대로 둠.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # uploads 폴더를 만듦. 이미 있는 폴더는 지우거나 초기화하지 않음.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def empty_reports() -> pd.DataFrame:
    """열 구조가 정해진 빈 신고 데이터 표를 반환한다."""
    # 정해진 열 이름만 있고 신고 행은 없는 빈 표를 돌려줌.
    return pd.DataFrame(columns=COLUMNS)


def load_reports() -> pd.DataFrame:
    """CSV 파일에서 신고 데이터를 읽는다. 파일이 없으면 빈 표를 반환한다."""
    # 데이터를 읽거나 쓰기 전에 저장 폴더가 있는지 준비함.
    ensure_storage()
    # 아직 신고 CSV 파일이 없는지 확인함.
    if not REPORTS_FILE.exists():
        # 신고 데이터 대신 열 구조를 갖춘 빈 표를 반환함.
        return empty_reports()

    # 파일 처리 등 오류가 발생할 수 있는 코드를 실행하고, 오류가 나면 아래 except에서 처리함.
    try:
        # CSV를 문자열 자료형으로 읽고, 비어 있는 값은 빈 문자열로 채움. utf-8-sig는 한글 인코딩을 지정함.
        reports = pd.read_csv(REPORTS_FILE, encoding="utf-8-sig", dtype=str).fillna("")
        # 예전 버전의 데이터 파일에도 새 열이 빠지지 않도록 보정한다.
        # 필요한 열 이름을 하나씩 꺼내 반복해서 확인함.
        for column in COLUMNS:
            # 기존 파일에 현재 프로그램이 요구하는 열이 빠져 있는지 확인함.
            if column not in reports.columns:
                # 빠진 열을 추가하고 모든 행의 해당 값을 빈 문자열로 채움.
                reports[column] = ""
        # 필요한 열만 정해진 순서로 정리해 반환함.
        return reports[COLUMNS]
    # 지정한 종류의 오류를 잡아 error 변수로 받고, 프로그램 화면에 오류 내용을 안내함.
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        # 실패 원인이나 오류를 화면에 표시함.
        st.error(f"신고 파일을 읽지 못했습니다: {error}")
        # 신고 데이터 대신 열 구조를 갖춘 빈 표를 반환함.
        return empty_reports()


def save_reports(reports: pd.DataFrame) -> bool:
    """신고 데이터를 CSV 파일에 저장하고 성공 여부를 반환한다."""
    # 데이터를 읽거나 쓰기 전에 저장 폴더가 있는지 준비함.
    ensure_storage()
    # 파일 처리 등 오류가 발생할 수 있는 코드를 실행하고, 오류가 나면 아래 except에서 처리함.
    try:
        # 저장할 표의 열 순서를 맞추고, 누락된 열은 빈 값으로 추가함.
        safe_reports = reports.reindex(columns=COLUMNS, fill_value="")
        # 원본 파일에 바로 쓰지 않고 먼저 저장할 임시 CSV 경로를 정함.
        temporary_file = REPORTS_FILE.with_name("facility_reports.tmp.csv")
        # 표의 행 번호를 제외하고 임시 CSV에 저장함. 한글을 읽기 쉽도록 UTF-8 BOM을 포함함.
        safe_reports.to_csv(temporary_file, index=False, encoding="utf-8-sig")
        # 임시 파일 저장이 끝나면 기존 신고 파일을 교체함. 여러 사용자의 동시 저장 충돌까지 막는 기능은 아님.
        temporary_file.replace(REPORTS_FILE)
        # 호출한 곳에 작업이 성공했다는 참 값을 반환함.
        return True
    # 지정한 종류의 오류를 잡아 error 변수로 받고, 프로그램 화면에 오류 내용을 안내함.
    except (OSError, PermissionError, ValueError) as error:
        # 실패 원인이나 오류를 화면에 표시함.
        st.error(f"신고 파일을 저장하지 못했습니다: {error}")
        # 호출한 곳에 작업이 실패했다는 거짓 값을 반환함.
        return False


def recommend_priority(category: str, description: str) -> str:
    """고장 종류와 설명의 단어를 바탕으로 긴급도를 추천한다.

    자동 분류는 참고용이며, 최종 긴급도는 관리자 판단으로 조정한다.
    """
    # 고장 종류와 설명을 한 문자열로 합쳐 검색 대상으로 만들고 영문은 소문자로 바꿈.
    text = f"{category} {description}".lower()
    # 긴급으로 추천할 위험 관련 검색어를 정함.
    urgent_words = ["누전", "감전", "연기", "불꽃", "화재", "가스 냄새", "천장 붕괴"]
    # 높음으로 추천할 위험 관련 검색어를 정함.
    high_words = ["누수", "물이 샘", "유리 파손", "날카로운", "문이 떨어", "넘어질"]

    # 긴급 검색어 중 하나라도 입력 내용에 포함되어 있는지 검사함.
    if any(word in text for word in urgent_words):
        # 긴급 검색어가 발견되어 긴급 등급을 반환하고 함수를 끝냄.
        return "긴급"
    # 긴급 조건에 해당하지 않은 경우, 높음 검색어가 하나라도 포함되는지 검사함.
    if any(word in text for word in high_words):
        # 높음 검색어가 발견되어 높음 등급을 반환하고 함수를 끝냄.
        return "높음"
    # 위험 검색어가 없더라도 지정된 고장 종류이면 보통으로 분류함.
    if category in {"전기·조명", "수도·화장실", "문·창문"}:
        # 지정된 고장 종류이므로 보통 등급을 반환함.
        return "보통"
    # 앞의 조건에 모두 해당하지 않으면 낮음 등급을 반환함. 키워드 기반 규칙이며 AI 학습 모델은 아님.
    return "낮음"


def save_uploaded_image(uploaded_file: Any, report_id: str) -> str:
    """첨부 사진을 저장하고 저장된 파일 경로를 반환한다."""
    # 첨부한 사진이 없는 경우인지 확인함.
    if uploaded_file is None:
        # 사진이 없으므로 저장 경로를 빈 문자열로 반환함.
        return ""

    # 데이터를 읽거나 쓰기 전에 저장 폴더가 있는지 준비함.
    ensure_storage()
    # 업로드한 파일 이름에서 확장자를 추출하고 소문자로 바꿈.
    extension = Path(uploaded_file.name).suffix.lower()
    # 허용하지 않은 확장자인지 검사함. 실제 이미지 내용까지 검증하는 코드는 아님.
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        # 잘못된 입력에 대한 오류를 발생시켜 호출한 곳에서 안내 메시지를 표시하도록 함.
        raise ValueError("PNG, JPG, JPEG, WEBP 형식의 사진만 첨부할 수 있습니다.")

    # 업로드한 사진의 실제 파일 데이터를 바이트 형태로 읽음.
    image_bytes = uploaded_file.getvalue()
    # 읽은 사진 데이터의 크기가 최대 용량을 초과하는지 검사함.
    if len(image_bytes) > MAX_IMAGE_SIZE:
        # 잘못된 입력에 대한 오류를 발생시켜 호출한 곳에서 안내 메시지를 표시하도록 함.
        raise ValueError("사진 크기는 5MB 이하여야 합니다.")

    # 신고 번호와 확장자를 합쳐 저장할 사진 이름을 만듦.
    image_name = f"{report_id}{extension}"
    # 사진 저장 폴더와 파일 이름을 합쳐 저장 위치를 만듦.
    image_path = UPLOAD_DIR / image_name
    # 사진의 바이트 데이터를 실제 파일로 저장함.
    image_path.write_bytes(image_bytes)
    # 앱 폴더를 기준으로 한 상대 경로를 문자열로 반환함.
    return str(image_path.relative_to(APP_DIR))


def create_report(
    reporter_type: str,
    building: str,
    location_detail: str,
    category: str,
    title: str,
    description: str,
    image_path: str = "",
) -> dict[str, str]:
    """입력값을 신고 데이터 한 건으로 구성하여 반환한다."""
    # 현재 서버 시간을 연-월-일 시:분:초 형식의 문자열로 만듦.
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # F-날짜-무작위 6자리 형식의 신고 번호를 만듦. 짧은 무작위 번호이므로 중복 가능성이 완전히 없는 것은 아님.
    report_id = f"F-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    # 신고의 여러 항목을 이름과 값의 쌍으로 묶은 딕셔너리로 반환함.
    return {
        "report_id": report_id,  # 신고를 구별하는 번호
        "created_at": now,  # 처음 신고한 시각
        "reporter_type": reporter_type,  # 학생 또는 교사 구분
        "building": building,  # 선택한 건물 이름
        "location_detail": location_detail.strip(),  # 층과 교실 등 상세 위치
        "category": category,  # 고장 종류
        "title": title.strip(),  # 신고 제목
        "description": description.strip(),  # 고장 상황 설명
        "priority": recommend_priority(category, description),  # 추천 또는 수정된 긴급도
        "status": "접수",  # 현재 처리 상태
        "manager_note": "",  # 관리자의 처리 메모
        "updated_at": now,  # 마지막으로 수정한 시각
        "image_path": image_path,  # 앱 폴더 기준 첨부 사진 경로
    }


def add_report(report: dict[str, str]) -> bool:
    """새 신고를 기존 데이터에 추가하고 CSV에 저장한다."""
    # 저장된 신고 CSV를 읽어 표 형태로 가져옴.
    reports = load_reports()
    # 새 신고 딕셔너리를 한 행짜리 표로 바꿈.
    new_row = pd.DataFrame([report], columns=COLUMNS)
    # 기존 신고 표 아래에 새 신고 한 행을 붙이고 행 번호를 다시 매김.
    updated_reports = pd.concat([reports, new_row], ignore_index=True)
    # 새 신고가 추가된 전체 표를 저장하고 성공 여부를 반환함.
    return save_reports(updated_reports)


def find_report(report_id: str) -> dict[str, str] | None:
    """신고 번호가 일치하는 신고 한 건을 찾아 반환한다."""
    # 저장된 신고 CSV를 읽어 표 형태로 가져옴.
    reports = load_reports()
    # 입력 번호의 앞뒤 공백을 제거하고 대문자로 맞춘 뒤, 같은 신고 번호를 가진 행만 찾음.
    matches = reports[reports["report_id"].str.upper() == report_id.strip().upper()]
    # 검색 결과가 한 건도 없는지 확인함.
    if matches.empty:
        # 일치하는 신고가 없다는 의미로 None을 반환함.
        return None
    # 검색된 첫 번째 행을 딕셔너리로 바꿔 반환함.
    return matches.iloc[0].to_dict()


def update_report(report_id: str, status: str, priority: str, manager_note: str) -> bool:
    """관리자가 선택한 신고의 상태·긴급도·처리 메모를 수정한다."""
    # 저장된 신고 CSV를 읽어 표 형태로 가져옴.
    reports = load_reports()
    # 신고 번호가 일치하는 행의 인덱스, 즉 표에서의 위치를 찾음.
    matches = reports.index[reports["report_id"] == report_id]
    # 수정할 신고가 존재하지 않는 경우인지 확인함.
    if len(matches) == 0:
        # 호출한 곳에 작업이 실패했다는 거짓 값을 반환함.
        return False

    # 수정할 첫 번째 신고 행의 위치를 저장함.
    row_index = matches[0]
    # 선택한 신고 행의 처리 상태를 새 값으로 변경함.
    reports.loc[row_index, "status"] = status
    # 선택한 신고 행의 긴급도를 새 값으로 변경함.
    reports.loc[row_index, "priority"] = priority
    # 메모의 앞뒤 공백을 제거한 뒤 선택한 신고 행에 저장함.
    reports.loc[row_index, "manager_note"] = manager_note.strip()
    # 수정 시각을 현재 서버 시간으로 갱신함.
    reports.loc[row_index, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 변경된 신고 표를 CSV에 저장하고 성공 여부를 반환함.
    return save_reports(reports)


def display_report(report: dict[str, str]) -> None:
    """신고 한 건의 주요 정보를 화면에 출력한다."""
    # 마크다운 서식을 적용하여 제목이나 신고 번호를 표시함.
    st.markdown(f"### 신고 번호: `{report['report_id']}`")
    # 가로로 나란히 표시할 화면 열을 만들고 각 열을 변수에 저장함.
    left, right = st.columns(2)
    # 신고 세부 항목을 왼쪽 또는 오른쪽 열에 표시함.
    left.write(f"**신고 일시:** {report['created_at']}")
    # 신고 세부 항목을 왼쪽 또는 오른쪽 열에 표시함.
    right.write(f"**신고자 구분:** {report['reporter_type']}")
    # 신고 세부 항목을 왼쪽 또는 오른쪽 열에 표시함.
    left.write(f"**위치:** {report['building']} {report['location_detail']}")
    # 신고 세부 항목을 왼쪽 또는 오른쪽 열에 표시함.
    right.write(f"**고장 종류:** {report['category']}")
    # 신고 세부 항목을 왼쪽 또는 오른쪽 열에 표시함.
    left.write(f"**긴급도:** {report['priority']}")
    # 신고 세부 항목을 왼쪽 또는 오른쪽 열에 표시함.
    right.write(f"**처리 상태:** {report['status']}")
    # 문자열 또는 신고 내용을 화면에 표시함.
    st.write(f"**제목:** {report['title']}")
    # 문자열 또는 신고 내용을 화면에 표시함.
    st.write(f"**상세 내용:** {report['description']}")
    # 관리자 메모가 비어 있지 않을 때만 메모를 표시함.
    if report.get("manager_note"):
        # 처리 메모, 안내 또는 추천 결과를 정보 메시지로 표시함.
        st.info(f"관리자 처리 메모: {report['manager_note']}")
    # 신고에 사진 경로가 기록되어 있는지 확인함.
    if report.get("image_path"):
        # 저장된 상대 경로에 앱 폴더를 붙여 사진의 전체 경로를 만듦.
        image_path = APP_DIR / report["image_path"]
        # 사진 파일이 실제로 남아 있는 경우에만 표시함.
        if image_path.exists():
            # 저장된 사진을 설명과 함께 화면 폭에 맞춰 표시함.
            st.image(str(image_path), caption="첨부된 고장 사진", use_container_width=True)


def show_user_page() -> None:
    """학생·교사가 신고를 등록하거나 신고 처리 현황을 조회하는 화면."""
    # 화면의 구역 제목을 표시함.
    st.subheader("시설 고장 신고")
    # 작은 글씨로 도움말 또는 안내를 표시함.
    st.caption("이름이나 전화번호는 입력하지 않습니다. 학교에서 승인된 사례만 등록하세요.")

    # 입력 요소를 하나의 신고 양식으로 묶음. 제출 시 입력값을 함께 전달하고 양식을 비움.
    with st.form("new_report_form", clear_on_submit=True):
        # 학생 또는 교사를 선택하는 버튼을 가로로 배치하고 선택값을 저장함.
        reporter_type = st.radio("신고자 구분", ["학생", "교사"], horizontal=True)
        # 가로로 나란히 표시할 화면 열을 만들고 각 열을 변수에 저장함.
        col1, col2 = st.columns(2)
        # 지정된 8개 건물 중 선택한 이름을 building 변수에 저장함.
        building = col1.selectbox("건물", BUILDINGS)
        # 고장 종류 목록에서 선택한 값을 category 변수에 저장함.
        category = col2.selectbox("고장 종류", CATEGORIES)
        # 층, 교실 등 상세 위치를 입력받음. placeholder는 입력 전 보이는 예시 문구임.
        location_detail = st.text_input("상세 위치", placeholder="예: 2층 3학년 2반, 과학실")
        # 고장 신고의 짧은 제목을 입력받음.
        title = st.text_input("신고 제목", placeholder="예: 교실 형광등이 켜지지 않음")
        # 여러 줄로 고장 설명을 입력받음. height는 입력창 높이를 지정함.
        description = st.text_area("고장 내용", placeholder="언제부터 어떤 문제가 발생했는지 적어 주세요.", height=110)
        # 선택적으로 사진을 첨부할 수 있는 입력창을 만듦. 용량 검사는 사진 저장 함수에서 수행함.
        uploaded_file = st.file_uploader(
            "고장 사진 첨부 (선택, 최대 5MB)",
            type=["png", "jpg", "jpeg", "webp"],
        )
        # 신고 제출 버튼을 만들고 이번 실행에서 제출되었는지 참 또는 거짓으로 받음.
        submitted = st.form_submit_button("고장 신고 등록", type="primary", use_container_width=True)

    # 사용자가 신고 등록 버튼을 눌렀을 때만 등록 절차를 진행함.
    if submitted:
        # 상세 위치, 제목, 설명 중 공백을 제외한 내용이 없는 항목이 있는지 검사함.
        if not location_detail.strip() or not title.strip() or not description.strip():
            # 입력 누락이나 주의할 내용을 경고 메시지로 표시함.
            st.warning("상세 위치, 신고 제목, 고장 내용을 모두 입력해 주세요.")
        # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
        else:
            # 파일 처리 등 오류가 발생할 수 있는 코드를 실행하고, 오류가 나면 아래 except에서 처리함.
            try:
                # F-날짜-무작위 6자리 형식의 신고 번호를 만듦. 짧은 무작위 번호이므로 중복 가능성이 완전히 없는 것은 아님.
                report_id = f"F-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
                # 사진이 있으면 저장하고 경로를 받음. 사진이 없으면 빈 문자열을 사용함.
                image_path = save_uploaded_image(uploaded_file, report_id) if uploaded_file else ""
                # 양식에서 입력받은 정보를 전달하여 신고 한 건의 딕셔너리를 만듦.
                report = create_report(
                    reporter_type,
                    building,
                    location_detail,
                    category,
                    title,
                    description,
                    image_path,
                )
                # 사진 저장 전 생성한 번호와 신고 번호가 다르지 않도록 맞춘다.
                # 사진 파일에 사용한 번호를 최종 신고 번호로 지정함.
                report["report_id"] = report_id
                # 신고를 기존 표에 추가하여 저장하고, 성공했는지 확인함.
                if add_report(report):
                    # 등록 또는 수정의 성공 메시지를 표시함.
                    st.success("신고가 등록되었습니다.")
                    # 발급된 신고 번호를 복사하기 쉬운 코드 상자로 표시함.
                    st.code(report_id, language=None)
                    # 처리 메모, 안내 또는 추천 결과를 정보 메시지로 표시함.
                    st.info(f"자동 추천 긴급도: {report['priority']} / 신고 번호를 저장해 두고 처리 현황을 조회하세요.")
                # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
                else:
                    # 실패 원인이나 오류를 화면에 표시함.
                    st.error("신고 저장에 실패했습니다. 저장 폴더의 쓰기 권한을 확인해 주세요.")
            # 지정한 종류의 오류를 잡아 error 변수로 받고, 프로그램 화면에 오류 내용을 안내함.
            except (OSError, ValueError) as error:
                # 실패 원인이나 오류를 화면에 표시함.
                st.error(str(error))

    # 구역을 구분하는 가로선을 표시함.
    st.divider()
    # 화면의 구역 제목을 표시함.
    st.subheader("신고 처리 현황 조회")
    # 조회할 신고 번호를 입력받음. key는 이 입력창을 구분하는 고유 이름임.
    lookup_id = st.text_input("신고 번호 입력", placeholder="예: F-20261105-ABC123", key="lookup_id")
    # 처리 현황 확인 버튼을 눌렀을 때 조회 절차를 진행함.
    if st.button("처리 현황 확인", key="lookup_button"):
        # 조회할 신고 번호를 비워 두었는지 검사함.
        if not lookup_id.strip():
            # 입력 누락이나 주의할 내용을 경고 메시지로 표시함.
            st.warning("신고 번호를 입력해 주세요.")
        # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
        else:
            # 입력한 신고 번호로 저장 데이터에서 신고를 검색함.
            report = find_report(lookup_id)
            # 해당 번호의 신고를 찾지 못했는지 확인함.
            if report is None:
                # 입력 누락이나 주의할 내용을 경고 메시지로 표시함.
                st.warning("해당 신고 번호를 찾을 수 없습니다.")
            # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
            else:
                # 찾은 신고의 위치, 내용, 처리 상태와 사진 등을 표시함.
                display_report(report)


def show_admin_page() -> None:
    """관리자 로그인, 신고 관리, 통계 확인 화면."""
    # 화면의 구역 제목을 표시함.
    st.subheader("관리자 페이지")
    # 현재 브라우저 세션에 관리자 로그인 상태가 없거나 거짓이면 로그인 화면을 표시함.
    if not st.session_state.get("admin_authenticated", False):
        # 화면에서 입력 문자를 가리는 비밀번호 입력창을 만듦.
        password = st.text_input("관리자 암호", type="password", key="admin_password")
        # 관리자 로그인 버튼을 눌렀을 때 암호를 비교함.
        if st.button("관리자 로그인", type="primary"):
            # 입력한 암호가 설정된 관리자 암호와 같은지 확인함.
            if password == ADMIN_PASSWORD:
                # 현재 세션에 관리자 인증 완료 상태를 기록함.
                st.session_state.admin_authenticated = True
                # 스크립트를 처음부터 다시 실행하여 바뀐 로그인 상태나 데이터를 화면에 반영함.
                st.rerun()
            # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
            else:
                # 실패 원인이나 오류를 화면에 표시함.
                st.error("암호가 올바르지 않습니다.")
        # 설정된 암호가 시연용 기본 암호인지 확인함.
        if ADMIN_PASSWORD == DEFAULT_ADMIN_PASSWORD:
            # 입력 누락이나 주의할 내용을 경고 메시지로 표시함.
            st.warning("과제 시연용 기본 암호는 admin1234입니다. 실제 운영 전 반드시 변경해야 합니다.")
        # 현재 함수를 종료하여 이후 코드를 실행하지 않음.
        return

    # 로그아웃 버튼을 누르면 인증 상태를 해제함.
    if st.button("관리자 로그아웃"):
        # 현재 세션의 관리자 인증 상태를 해제함.
        st.session_state.admin_authenticated = False
        # 스크립트를 처음부터 다시 실행하여 바뀐 로그인 상태나 데이터를 화면에 반영함.
        st.rerun()

    # 저장된 신고 CSV를 읽어 표 형태로 가져옴.
    reports = load_reports()
    # 등록된 신고가 없는지 확인함.
    if reports.empty:
        # 처리 메모, 안내 또는 추천 결과를 정보 메시지로 표시함.
        st.info("아직 등록된 신고가 없습니다. 사용자 화면에서 테스트 신고를 등록해 보세요.")
        # 현재 함수를 종료하여 이후 코드를 실행하지 않음.
        return

    # 전체 신고 행 수를 계산함.
    total = len(reports)
    # 처리 완료가 아닌 행의 수를 계산함. 참 값을 합치면 해당 행 수가 됨.
    open_count = int((reports["status"] != "처리 완료").sum())
    # 긴급도가 긴급 또는 높음인 신고 수를 계산함. 완료된 신고도 포함함.
    urgent_count = int(reports["priority"].isin(["긴급", "높음"]).sum())
    # 처리 상태가 처리 완료인 신고 수를 계산함.
    done_count = int((reports["status"] == "처리 완료").sum())
    # 가로로 나란히 표시할 화면 열을 만들고 각 열을 변수에 저장함.
    metric1, metric2, metric3, metric4 = st.columns(4)
    # 계산한 신고 건수를 해당 제목과 함께 요약 지표로 표시함.
    metric1.metric("전체 신고", total)
    # 계산한 신고 건수를 해당 제목과 함께 요약 지표로 표시함.
    metric2.metric("미완료", open_count)
    # 계산한 신고 건수를 해당 제목과 함께 요약 지표로 표시함.
    metric3.metric("긴급·높음", urgent_count)
    # 계산한 신고 건수를 해당 제목과 함께 요약 지표로 표시함.
    metric4.metric("처리 완료", done_count)

    # 구역을 구분하는 가로선을 표시함.
    st.divider()
    # 마크다운 서식을 적용하여 제목이나 신고 번호를 표시함.
    st.markdown("#### 신고 목록")
    # 가로로 나란히 표시할 화면 열을 만들고 각 열을 변수에 저장함.
    filter_col1, filter_col2 = st.columns(2)
    # 처리 상태 필터를 선택받음. 전체를 선택하면 상태로 제한하지 않음.
    selected_status = filter_col1.selectbox("처리 상태 필터", ["전체"] + STATUSES)
    # 고장 종류 필터를 선택받음. 전체를 선택하면 종류로 제한하지 않음.
    selected_category = filter_col2.selectbox("고장 종류 필터", ["전체"] + CATEGORIES)
    # 원본 신고 표를 유지하면서 필터링할 복사본을 만듦.
    filtered = reports.copy()
    # 전체가 아닌 특정 처리 상태를 선택했는지 확인함.
    if selected_status != "전체":
        # 선택한 처리 상태와 일치하는 행만 남김.
        filtered = filtered[filtered["status"] == selected_status]
    # 전체가 아닌 특정 고장 종류를 선택했는지 확인함.
    if selected_category != "전체":
        # 남은 행 중 선택한 고장 종류와 일치하는 행만 남김. 두 필터는 함께 적용됨.
        filtered = filtered[filtered["category"] == selected_category]

    # 신고 목록 표에서 보여줄 열과 순서를 지정함.
    display_columns = ["report_id", "created_at", "building", "location_detail", "category", "priority", "status", "title"]
    # 신고 목록 또는 집계 결과를 표로 표시함.
    st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

    # 구역을 구분하는 가로선을 표시함.
    st.divider()
    # 마크다운 서식을 적용하여 제목이나 신고 번호를 표시함.
    st.markdown("#### 신고 처리 내용 수정")
    # 전체 신고 표에서 신고 번호 열을 꺼내 파이썬 리스트로 바꿈.
    report_ids = reports["report_id"].tolist()
    # 관리자가 수정할 신고 번호를 선택하도록 함. 위 필터와 별개로 전체 신고 번호를 사용함.
    selected_id = st.selectbox("수정할 신고 번호", report_ids)
    # 선택한 신고 번호의 첫 번째 행을 찾아 딕셔너리로 바꿈.
    selected_row = reports[reports["report_id"] == selected_id].iloc[0].to_dict()
    # 상태, 긴급도, 메모를 한 번에 제출하는 수정 양식을 만듦.
    with st.form("update_report_form"):
        # 문자열 또는 신고 내용을 화면에 표시함.
        st.write(f"**신고 내용:** {selected_row['title']} — {selected_row['building']} {selected_row['location_detail']}")
        # 기존 처리 상태의 목록 위치를 구해 기본 선택값으로 사용함. 목록에 없으면 첫 항목을 선택함.
        status_index = STATUSES.index(selected_row["status"]) if selected_row["status"] in STATUSES else 0
        # 기존 긴급도의 목록 위치를 구함. 목록에 없으면 세 번째 항목인 보통을 선택함.
        priority_index = PRIORITIES.index(selected_row["priority"]) if selected_row["priority"] in PRIORITIES else 2
        # 기존 상태를 기본값으로 보여주고 변경할 처리 상태를 선택받음.
        new_status = st.selectbox("처리 상태", STATUSES, index=status_index)
        # 기존 긴급도를 기본값으로 보여주고 변경할 긴급도를 선택받음.
        new_priority = st.selectbox("긴급도", PRIORITIES, index=priority_index)
        # 기존 관리자 메모를 표시하고 수정할 내용을 입력받음.
        manager_note = st.text_area("처리 메모", value=selected_row["manager_note"], placeholder="예: 시설 담당자에게 전달함")
        # 처리 내용 저장 버튼을 만들고 제출 여부를 받음.
        update_submitted = st.form_submit_button("처리 내용 저장", type="primary")
    # 수정 양식을 제출했을 때만 변경 내용을 저장함.
    if update_submitted:
        # 선택한 신고의 상태, 긴급도, 메모를 수정하고 저장 성공 여부를 확인함.
        if update_report(selected_id, new_status, new_priority, manager_note):
            # 등록 또는 수정의 성공 메시지를 표시함.
            st.success("처리 내용이 저장되었습니다.")
            # 스크립트를 처음부터 다시 실행하여 바뀐 로그인 상태나 데이터를 화면에 반영함.
            st.rerun()
        # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
        else:
            # 실패 원인이나 오류를 화면에 표시함.
            st.error("수정 내용을 저장하지 못했습니다.")

    # 구역을 구분하는 가로선을 표시함.
    st.divider()
    # 마크다운 서식을 적용하여 제목이나 신고 번호를 표시함.
    st.markdown("#### 신고 통계")
    # 가로로 나란히 표시할 화면 열을 만들고 각 열을 변수에 저장함.
    chart_col1, chart_col2 = st.columns(2)
    # 아래 통계 제목과 그래프를 해당 열 안에 표시함.
    with chart_col1:
        # 문자열 또는 신고 내용을 화면에 표시함.
        st.write("고장 종류별 신고 수")
        # 전체 신고를 고장 종류별로 묶어 건수를 세고 많은 순서로 정렬함.
        category_counts = reports.groupby("category").size().sort_values(ascending=False)
        # 집계된 신고 수를 막대그래프로 표시함.
        st.bar_chart(category_counts)
    # 아래 통계 제목과 그래프를 해당 열 안에 표시함.
    with chart_col2:
        # 문자열 또는 신고 내용을 화면에 표시함.
        st.write("처리 상태별 신고 수")
        # 전체 신고를 처리 상태별로 묶어 건수를 셈. 정해진 상태 순서로 맞추고 없는 상태는 0으로 채움.
        status_counts = reports.groupby("status").size().reindex(STATUSES, fill_value=0)
        # 집계된 신고 수를 막대그래프로 표시함.
        st.bar_chart(status_counts)

    # 문자열 또는 신고 내용을 화면에 표시함.
    st.write("**반복 신고 위치**")
    # 같은 건물과 상세 위치의 신고를 묶어 신고가 많은 상위 5개 위치를 계산함.
    location_counts = (
        # 건물 이름과 상세 위치를 공백으로 연결한 full_location 열을 임시로 추가함.
        reports.assign(full_location=reports["building"] + " " + reports["location_detail"])
        # 완성된 위치 문자열이 같은 신고끼리 묶음.
        .groupby("full_location")
        # 각 위치 그룹에 포함된 신고 수를 셈.
        .size()
        # 신고 수가 많은 위치부터 내림차순으로 정렬함.
        .sort_values(ascending=False)
        # 정렬된 결과의 앞쪽 5개 위치만 선택함.
        .head(5)
    )
    # 집계된 위치 정보가 없는지 확인함.
    if location_counts.empty:
        # 작은 글씨로 도움말 또는 안내를 표시함.
        st.caption("분석할 데이터가 없습니다.")
    # 바로 앞 if 조건에 해당하지 않는 경우 아래 처리를 실행함.
    else:
        # 신고 목록 또는 집계 결과를 표로 표시함.
        st.dataframe(location_counts.rename("신고 수").to_frame(), use_container_width=True)

    # 관리자가 엑셀 등에서 활용할 수 있도록 현재 신고 목록을 CSV로 내려받는다.
    # 전체 신고 표를 CSV 문자열로 바꾼 뒤 한글 인코딩을 지정한 바이트 데이터로 변환함.
    csv_data = reports.to_csv(index=False).encode("utf-8-sig")
    # 현재 전체 신고 데이터를 CSV 파일로 내려받는 버튼을 만듦.
    st.download_button(
        "신고 데이터 CSV 다운로드",
        data=csv_data,
        file_name="facility_reports.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Streamlit 앱의 시작 화면을 구성한다."""
    # 브라우저 제목, 아이콘과 넓은 화면 배치를 설정함.
    st.set_page_config(page_title="교내 시설 관리 시스템", page_icon="🛠️", layout="wide")
    # 데이터를 읽거나 쓰기 전에 저장 폴더가 있는지 준비함.
    ensure_storage()

    # 프로그램의 큰 제목을 표시함.
    st.title("🛠️ 교내 시설 고장 신고 및 처리 관리 시스템")
    # 문자열 또는 신고 내용을 화면에 표시함.
    st.write("학생과 교사가 시설 고장을 신고하고, 관리자가 처리 과정을 관리하는 프로그램입니다.")

    # 아래 안내 요소를 화면 옆 사이드바에 배치함.
    with st.sidebar:
        # 안내 영역의 제목을 표시함.
        st.header("이용 안내")
        # 문자열 또는 신고 내용을 화면에 표시함.
        st.write("1. 학생·교사는 고장 신고를 등록합니다.")
        # 문자열 또는 신고 내용을 화면에 표시함.
        st.write("2. 발급된 신고 번호로 처리 현황을 조회합니다.")
        # 문자열 또는 신고 내용을 화면에 표시함.
        st.write("3. 관리자는 신고를 확인하고 처리 상태를 변경합니다.")
        # 작은 글씨로 도움말 또는 안내를 표시함.
        st.caption("이름·전화번호 등 개인정보는 신고 내용에 입력하지 마세요.")

    # 사용자 화면과 관리자 화면을 나누는 두 탭을 만듦. Streamlit은 두 탭의 코드 모두 실행함.
    user_tab, admin_tab = st.tabs(["학생·교사 신고 / 조회", "관리자 관리 / 통계"])
    # 사용자 탭 영역에 신고 및 조회 화면을 배치함.
    with user_tab:
        # 신고 등록과 신고 번호 조회 화면을 구성하는 함수를 호출함.
        show_user_page()
    # 관리자 탭 영역에 로그인, 관리 및 통계 화면을 배치함.
    with admin_tab:
        # 관리자 화면 함수를 호출함. 함수 안에서 로그인 상태를 검사함.
        show_admin_page()


# 이 파일이 실행 진입점일 때만 main 함수를 호출함. 다른 파일에서 import하면 호출하지 않음.
if __name__ == "__main__":
    # 앱의 시작 함수 main을 실행함.
    main()
