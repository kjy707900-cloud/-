"""교내 시설 고장 신고 및 처리 관리 시스템

실행:
    python -m pip install -r requirements.txt
    python -m streamlit run school_facility_manager.py

주의: 이 프로그램은 학교 과제용 시제품입니다. 실제 학교에서 운영하려면
학교 승인, 계정 인증, 서버 및 데이터 백업 등 추가 보안 조치가 필요합니다.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


# -----------------------------------------------------------------------------
# 기본 설정 및 저장 경로
# -----------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
UPLOAD_DIR = APP_DIR / "uploads"
REPORTS_FILE = DATA_DIR / "facility_reports.csv"

COLUMNS = [
    "report_id",
    "created_at",
    "reporter_type",
    "building",
    "location_detail",
    "category",
    "title",
    "description",
    "priority",
    "status",
    "manager_note",
    "updated_at",
    "image_path",
]

CATEGORIES = ["책상·의자", "전기·조명", "냉난방", "컴퓨터·프로젝터", "문·창문", "수도·화장실", "기타"]
BUILDINGS = ["본관", "별관", "체육관", "급식실", "도서관", "기타"]
STATUSES = ["접수", "확인 중", "조치 예정", "처리 완료", "보류"]
PRIORITIES = ["긴급", "높음", "보통", "낮음"]

# 실제 운영 전에는 환경 변수 FACILITY_ADMIN_PASSWORD에 별도 암호를 설정하세요.
ADMIN_PASSWORD = os.environ.get("FACILITY_ADMIN_PASSWORD", "admin1234")
DEFAULT_ADMIN_PASSWORD = "admin1234"
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def ensure_storage() -> None:
    """신고 데이터와 사진을 저장할 폴더를 준비한다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def empty_reports() -> pd.DataFrame:
    """열 구조가 정해진 빈 신고 데이터 표를 반환한다."""
    return pd.DataFrame(columns=COLUMNS)


def load_reports() -> pd.DataFrame:
    """CSV 파일에서 신고 데이터를 읽는다. 파일이 없으면 빈 표를 반환한다."""
    ensure_storage()
    if not REPORTS_FILE.exists():
        return empty_reports()

    try:
        reports = pd.read_csv(REPORTS_FILE, encoding="utf-8-sig", dtype=str).fillna("")
        # 예전 버전의 데이터 파일에도 새 열이 빠지지 않도록 보정한다.
        for column in COLUMNS:
            if column not in reports.columns:
                reports[column] = ""
        return reports[COLUMNS]
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"신고 파일을 읽지 못했습니다: {error}")
        return empty_reports()


def save_reports(reports: pd.DataFrame) -> bool:
    """신고 데이터를 CSV 파일에 저장하고 성공 여부를 반환한다."""
    ensure_storage()
    try:
        safe_reports = reports.reindex(columns=COLUMNS, fill_value="")
        temporary_file = REPORTS_FILE.with_name("facility_reports.tmp.csv")
        safe_reports.to_csv(temporary_file, index=False, encoding="utf-8-sig")
        temporary_file.replace(REPORTS_FILE)
        return True
    except (OSError, PermissionError, ValueError) as error:
        st.error(f"신고 파일을 저장하지 못했습니다: {error}")
        return False


def recommend_priority(category: str, description: str) -> str:
    """고장 종류와 설명의 단어를 바탕으로 긴급도를 추천한다.

    자동 분류는 참고용이며, 최종 긴급도는 관리자 판단으로 조정한다.
    """
    text = f"{category} {description}".lower()
    urgent_words = ["누전", "감전", "연기", "불꽃", "화재", "가스 냄새", "천장 붕괴"]
    high_words = ["누수", "물이 샘", "유리 파손", "날카로운", "문이 떨어", "넘어질"]

    if any(word in text for word in urgent_words):
        return "긴급"
    if any(word in text for word in high_words):
        return "높음"
    if category in {"전기·조명", "수도·화장실", "문·창문"}:
        return "보통"
    return "낮음"


def save_uploaded_image(uploaded_file: Any, report_id: str) -> str:
    """첨부 사진을 저장하고 저장된 파일 경로를 반환한다."""
    if uploaded_file is None:
        return ""

    ensure_storage()
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("PNG, JPG, JPEG, WEBP 형식의 사진만 첨부할 수 있습니다.")

    image_bytes = uploaded_file.getvalue()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("사진 크기는 5MB 이하여야 합니다.")

    image_name = f"{report_id}{extension}"
    image_path = UPLOAD_DIR / image_name
    image_path.write_bytes(image_bytes)
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
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = f"F-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    return {
        "report_id": report_id,
        "created_at": now,
        "reporter_type": reporter_type,
        "building": building,
        "location_detail": location_detail.strip(),
        "category": category,
        "title": title.strip(),
        "description": description.strip(),
        "priority": recommend_priority(category, description),
        "status": "접수",
        "manager_note": "",
        "updated_at": now,
        "image_path": image_path,
    }


def add_report(report: dict[str, str]) -> bool:
    """새 신고를 기존 데이터에 추가하고 CSV에 저장한다."""
    reports = load_reports()
    new_row = pd.DataFrame([report], columns=COLUMNS)
    updated_reports = pd.concat([reports, new_row], ignore_index=True)
    return save_reports(updated_reports)


def find_report(report_id: str) -> dict[str, str] | None:
    """신고 번호가 일치하는 신고 한 건을 찾아 반환한다."""
    reports = load_reports()
    matches = reports[reports["report_id"].str.upper() == report_id.strip().upper()]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def update_report(report_id: str, status: str, priority: str, manager_note: str) -> bool:
    """관리자가 선택한 신고의 상태·긴급도·처리 메모를 수정한다."""
    reports = load_reports()
    matches = reports.index[reports["report_id"] == report_id]
    if len(matches) == 0:
        return False

    row_index = matches[0]
    reports.loc[row_index, "status"] = status
    reports.loc[row_index, "priority"] = priority
    reports.loc[row_index, "manager_note"] = manager_note.strip()
    reports.loc[row_index, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return save_reports(reports)


def display_report(report: dict[str, str]) -> None:
    """신고 한 건의 주요 정보를 화면에 출력한다."""
    st.markdown(f"### 신고 번호: `{report['report_id']}`")
    left, right = st.columns(2)
    left.write(f"**신고 일시:** {report['created_at']}")
    right.write(f"**신고자 구분:** {report['reporter_type']}")
    left.write(f"**위치:** {report['building']} {report['location_detail']}")
    right.write(f"**고장 종류:** {report['category']}")
    left.write(f"**긴급도:** {report['priority']}")
    right.write(f"**처리 상태:** {report['status']}")
    st.write(f"**제목:** {report['title']}")
    st.write(f"**상세 내용:** {report['description']}")
    if report.get("manager_note"):
        st.info(f"관리자 처리 메모: {report['manager_note']}")
    if report.get("image_path"):
        image_path = APP_DIR / report["image_path"]
        if image_path.exists():
            st.image(str(image_path), caption="첨부된 고장 사진", use_container_width=True)


def show_user_page() -> None:
    """학생·교사가 신고를 등록하거나 신고 처리 현황을 조회하는 화면."""
    st.subheader("시설 고장 신고")
    st.caption("이름이나 전화번호는 입력하지 않습니다. 학교에서 승인된 사례만 등록하세요.")

    with st.form("new_report_form", clear_on_submit=True):
        reporter_type = st.radio("신고자 구분", ["학생", "교사"], horizontal=True)
        col1, col2 = st.columns(2)
        building = col1.selectbox("건물", BUILDINGS)
        category = col2.selectbox("고장 종류", CATEGORIES)
        location_detail = st.text_input("상세 위치", placeholder="예: 2층 3학년 2반, 과학실")
        title = st.text_input("신고 제목", placeholder="예: 교실 형광등이 켜지지 않음")
        description = st.text_area("고장 내용", placeholder="언제부터 어떤 문제가 발생했는지 적어 주세요.", height=110)
        uploaded_file = st.file_uploader(
            "고장 사진 첨부 (선택, 최대 5MB)",
            type=["png", "jpg", "jpeg", "webp"],
        )
        submitted = st.form_submit_button("고장 신고 등록", type="primary", use_container_width=True)

    if submitted:
        if not location_detail.strip() or not title.strip() or not description.strip():
            st.warning("상세 위치, 신고 제목, 고장 내용을 모두 입력해 주세요.")
        else:
            try:
                report_id = f"F-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
                image_path = save_uploaded_image(uploaded_file, report_id) if uploaded_file else ""
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
                report["report_id"] = report_id
                if add_report(report):
                    st.success("신고가 등록되었습니다.")
                    st.code(report_id, language=None)
                    st.info(f"자동 추천 긴급도: {report['priority']} / 신고 번호를 저장해 두고 처리 현황을 조회하세요.")
                else:
                    st.error("신고 저장에 실패했습니다. 저장 폴더의 쓰기 권한을 확인해 주세요.")
            except (OSError, ValueError) as error:
                st.error(str(error))

    st.divider()
    st.subheader("신고 처리 현황 조회")
    lookup_id = st.text_input("신고 번호 입력", placeholder="예: F-20261105-ABC123", key="lookup_id")
    if st.button("처리 현황 확인", key="lookup_button"):
        if not lookup_id.strip():
            st.warning("신고 번호를 입력해 주세요.")
        else:
            report = find_report(lookup_id)
            if report is None:
                st.warning("해당 신고 번호를 찾을 수 없습니다.")
            else:
                display_report(report)


def show_admin_page() -> None:
    """관리자 로그인, 신고 관리, 통계 확인 화면."""
    st.subheader("관리자 페이지")
    if not st.session_state.get("admin_authenticated", False):
        password = st.text_input("관리자 암호", type="password", key="admin_password")
        if st.button("관리자 로그인", type="primary"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("암호가 올바르지 않습니다.")
        if ADMIN_PASSWORD == DEFAULT_ADMIN_PASSWORD:
            st.warning("과제 시연용 기본 암호는 admin1234입니다. 실제 운영 전 반드시 변경해야 합니다.")
        return

    if st.button("관리자 로그아웃"):
        st.session_state.admin_authenticated = False
        st.rerun()

    reports = load_reports()
    if reports.empty:
        st.info("아직 등록된 신고가 없습니다. 사용자 화면에서 테스트 신고를 등록해 보세요.")
        return

    total = len(reports)
    open_count = int((reports["status"] != "처리 완료").sum())
    urgent_count = int(reports["priority"].isin(["긴급", "높음"]).sum())
    done_count = int((reports["status"] == "처리 완료").sum())
    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("전체 신고", total)
    metric2.metric("미완료", open_count)
    metric3.metric("긴급·높음", urgent_count)
    metric4.metric("처리 완료", done_count)

    st.divider()
    st.markdown("#### 신고 목록")
    filter_col1, filter_col2 = st.columns(2)
    selected_status = filter_col1.selectbox("처리 상태 필터", ["전체"] + STATUSES)
    selected_category = filter_col2.selectbox("고장 종류 필터", ["전체"] + CATEGORIES)
    filtered = reports.copy()
    if selected_status != "전체":
        filtered = filtered[filtered["status"] == selected_status]
    if selected_category != "전체":
        filtered = filtered[filtered["category"] == selected_category]

    display_columns = ["report_id", "created_at", "building", "location_detail", "category", "priority", "status", "title"]
    st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 신고 처리 내용 수정")
    report_ids = reports["report_id"].tolist()
    selected_id = st.selectbox("수정할 신고 번호", report_ids)
    selected_row = reports[reports["report_id"] == selected_id].iloc[0].to_dict()
    with st.form("update_report_form"):
        st.write(f"**신고 내용:** {selected_row['title']} — {selected_row['building']} {selected_row['location_detail']}")
        status_index = STATUSES.index(selected_row["status"]) if selected_row["status"] in STATUSES else 0
        priority_index = PRIORITIES.index(selected_row["priority"]) if selected_row["priority"] in PRIORITIES else 2
        new_status = st.selectbox("처리 상태", STATUSES, index=status_index)
        new_priority = st.selectbox("긴급도", PRIORITIES, index=priority_index)
        manager_note = st.text_area("처리 메모", value=selected_row["manager_note"], placeholder="예: 시설 담당자에게 전달함")
        update_submitted = st.form_submit_button("처리 내용 저장", type="primary")
    if update_submitted:
        if update_report(selected_id, new_status, new_priority, manager_note):
            st.success("처리 내용이 저장되었습니다.")
            st.rerun()
        else:
            st.error("수정 내용을 저장하지 못했습니다.")

    st.divider()
    st.markdown("#### 신고 통계")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.write("고장 종류별 신고 수")
        category_counts = reports.groupby("category").size().sort_values(ascending=False)
        st.bar_chart(category_counts)
    with chart_col2:
        st.write("처리 상태별 신고 수")
        status_counts = reports.groupby("status").size().reindex(STATUSES, fill_value=0)
        st.bar_chart(status_counts)

    st.write("**반복 신고 위치**")
    location_counts = (
        reports.assign(full_location=reports["building"] + " " + reports["location_detail"])
        .groupby("full_location")
        .size()
        .sort_values(ascending=False)
        .head(5)
    )
    if location_counts.empty:
        st.caption("분석할 데이터가 없습니다.")
    else:
        st.dataframe(location_counts.rename("신고 수").to_frame(), use_container_width=True)

    # 관리자가 엑셀 등에서 활용할 수 있도록 현재 신고 목록을 CSV로 내려받는다.
    csv_data = reports.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "신고 데이터 CSV 다운로드",
        data=csv_data,
        file_name="facility_reports.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    """Streamlit 앱의 시작 화면을 구성한다."""
    st.set_page_config(page_title="교내 시설 관리 시스템", page_icon="🛠️", layout="wide")
    ensure_storage()

    st.title("🛠️ 교내 시설 고장 신고 및 처리 관리 시스템")
    st.write("학생과 교사가 시설 고장을 신고하고, 관리자가 처리 과정을 관리하는 프로그램입니다.")

    with st.sidebar:
        st.header("이용 안내")
        st.write("1. 학생·교사는 고장 신고를 등록합니다.")
        st.write("2. 발급된 신고 번호로 처리 현황을 조회합니다.")
        st.write("3. 관리자는 신고를 확인하고 처리 상태를 변경합니다.")
        st.caption("이름·전화번호 등 개인정보는 신고 내용에 입력하지 마세요.")

    user_tab, admin_tab = st.tabs(["학생·교사 신고 / 조회", "관리자 관리 / 통계"])
    with user_tab:
        show_user_page()
    with admin_tab:
        show_admin_page()


if __name__ == "__main__":
    main()
