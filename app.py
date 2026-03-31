import streamlit as st
from datetime import date, time

st.set_page_config(page_title="사주 프로그램", page_icon="🔮", layout="centered")

def reset_sensitive_state():
    for key in [
        "name",
        "birth_date",
        "birth_time",
        "calendar_type",
        "gender",
        "result"
    ]:
        if key in st.session_state:
            del st.session_state[key]

st.title("🔮 사주 프로그램")
st.caption("입력값은 저장하지 않고, 세션 내에서만 처리되도록 구성한 기본 버전입니다.")

st.info("이름, 생년월일, 태어난 시간은 결과 계산용으로만 사용되며, 별도로 저장하지 않습니다.")

with st.form("saju_form"):
    name = st.text_input("이름", placeholder="예: 홍길동")
    birth_date = st.date_input(
        "생년월일",
        value=date(1995, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )
    birth_time = st.time_input(
        "태어난 시간",
        value=time(12, 0),
        step=60
    )
    calendar_type = st.radio("달력 구분", ["양력", "음력"], horizontal=True)
    gender = st.radio("성별", ["여성", "남성", "기타/미선택"], horizontal=True)

    submitted = st.form_submit_button("사주 보기")

if submitted:
    if not name.strip():
        st.error("이름을 입력해주세요.")
    else:
        # 현재는 개인정보 저장 없는 구조 확인용 임시 결과
        result = {
            "이름": name.strip(),
            "생년월일": birth_date.isoformat(),
            "태어난 시간": birth_time.strftime("%H:%M"),
            "달력 구분": calendar_type,
            "성별": gender,
            "안내": "현재는 입력/초기화 구조를 먼저 만든 단계이며, 만세력 계산 로직은 다음 단계에서 추가합니다."
        }
        st.session_state["result"] = result

if "result" in st.session_state:
    st.subheader("입력 결과")
    st.json(st.session_state["result"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("초기화", type="primary", use_container_width=True):
            reset_sensitive_state()
            st.rerun()

    with col2:
        if st.button("결과만 지우기", use_container_width=True):
            if "result" in st.session_state:
                del st.session_state["result"]
            st.rerun()
