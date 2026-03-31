import os
from datetime import date, time
from typing import Dict, Any, Optional

import streamlit as st

try:
    from sajupy import calculate_saju
except Exception:
    calculate_saju = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


st.set_page_config(page_title="사주 프로그램", page_icon="🔮", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    .hero-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: white;
        padding: 28px;
        border-radius: 22px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    .soft-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    }
    .pill-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 8px;
    }
    .pill {
        background: #eef2ff;
        color: #3730a3;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        border: 1px solid #c7d2fe;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .subtle {
        color: #6b7280;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_sensitive_state() -> None:
    for key in [
        "name",
        "birth_date",
        "birth_time",
        "calendar_type",
        "gender",
        "use_ai",
        "saju_result",
        "ai_interpretation",
        "show_result",
    ]:
        if key in st.session_state:
            del st.session_state[key]


def element_of_char(char: str) -> str:
    stem_map = {
        "甲": "목", "乙": "목",
        "丙": "화", "丁": "화",
        "戊": "토", "己": "토",
        "庚": "금", "辛": "금",
        "壬": "수", "癸": "수",
    }
    branch_map = {
        "子": "수", "丑": "토", "寅": "목", "卯": "목",
        "辰": "토", "巳": "화", "午": "화", "未": "토",
        "申": "금", "酉": "금", "戌": "토", "亥": "수",
    }
    return stem_map.get(char) or branch_map.get(char) or "기타"


def count_five_elements(saju: Dict[str, Any]) -> Dict[str, int]:
    counts = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    chars = [
        saju.get("year_stem", ""), saju.get("year_branch", ""),
        saju.get("month_stem", ""), saju.get("month_branch", ""),
        saju.get("day_stem", ""), saju.get("day_branch", ""),
        saju.get("hour_stem", ""), saju.get("hour_branch", ""),
    ]
    for ch in chars:
        e = element_of_char(ch)
        if e in counts:
            counts[e] += 1
    return counts


def summarize_elements(counts: Dict[str, int]) -> Dict[str, Any]:
    max_value = max(counts.values())
    min_value = min(counts.values())
    strong = [k for k, v in counts.items() if v == max_value]
    weak = [k for k, v in counts.items() if v == min_value]
    return {
        "많은 오행": strong,
        "적은 오행": weak,
        "오행 분포": counts,
    }


def run_saju_engine(
    birth_date: date,
    birth_time: time,
    calendar_type: str,
) -> Dict[str, Any]:
    if calculate_saju is None:
        raise RuntimeError("sajupy 라이브러리를 불러오지 못했습니다.")

    # sajupy 문서 기준 기본 호출 형태
    # 음력 입력은 is_lunar=True, 윤달은 MVP에서는 미지원
    kwargs = {
        "year": birth_date.year,
        "month": birth_date.month,
        "day": birth_date.day,
        "hour": birth_time.hour,
        "minute": birth_time.minute,
    }

    if calendar_type == "음력":
        kwargs["is_lunar"] = True
        kwargs["is_leap_month"] = False

    saju = calculate_saju(**kwargs)
    return saju


def build_ai_prompt(name: str, result: Dict[str, Any]) -> str:
    return f"""
당신은 사주 해석 보조 어시스턴트입니다.
아래 정보는 사용자의 원본 생년월일이 아니라 이미 계산된 사주 결과입니다.
이 결과만 바탕으로 참고용 해석을 한국어로 작성하세요.

작성 규칙:
- 과장하거나 단정적으로 예언하지 말 것
- 미신적으로 몰아가지 말고 성향 분석 중심으로 설명할 것
- 아래 6개 섹션을 이 순서로 작성할 것
1. 한줄 요약
2. 성향
3. 강점
4. 주의할 점
5. 인간관계/일 스타일
6. 참고 포인트
- 각 섹션은 2~4문장 이내
- 이름은 반드시 {name} 님으로만 표기
- 투자, 의료, 법률, 건강 진단처럼 고위험 조언 금지
- 마지막에 '참고용 해석입니다.' 문장으로 마무리

계산 결과:
{result}
""".strip()


def get_api_key() -> Optional[str]:
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def get_ai_interpretation(name: str, result: Dict[str, Any]) -> Optional[str]:
    api_key = get_api_key()
    if not api_key:
        return "OPENAI_API_KEY가 설정되지 않아 AI 해석을 생성할 수 없습니다."
    if OpenAI is None:
        return "OpenAI SDK가 설치되지 않아 AI 해석을 생성하지 못했습니다."

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-5.4-mini",
            input=build_ai_prompt(name, result),
        )
        return response.output_text
    except Exception as e:
        return f"AI 해석 생성 중 오류가 발생했습니다: {e}"


st.markdown(
    """
    <div class="hero-card">
        <div style="font-size:2rem; font-weight:800; margin-bottom:8px;">🔮 사주 프로그램</div>
        <div style="font-size:1.02rem; opacity:0.92; line-height:1.6;">
            이름, 생년월일, 태어난 시간을 바탕으로 사주팔자와 오행 분포를 확인할 수 있는 버전입니다.<br>
            입력값은 저장하지 않고 세션 내에서만 처리되도록 구성했습니다.
        </div>
        <div class="pill-row">
            <span class="pill">DB 저장 없음</span>
            <span class="pill">파일 저장 없음</span>
            <span class="pill">세션 기반 처리</span>
            <span class="pill">AI 해석 선택 가능</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("중요 안내", expanded=False):
    st.markdown(
        """
- 현재 버전은 `sajupy` 라이브러리를 이용한 실사용 MVP입니다.
- 사주 계산 라이브러리의 결과를 그대로 표시합니다.
- AI 해석은 선택 기능이며, 원본 개인정보 대신 계산 결과만 전송하도록 구성했습니다.
- 앱을 새로고침하거나 초기화하면 입력값과 결과가 세션에서 제거됩니다.
        """
    )

st.markdown('<div class="section-title">입력 정보</div>', unsafe_allow_html=True)
st.markdown('<div class="soft-card">', unsafe_allow_html=True)
with st.form("saju_form", clear_on_submit=False):
    top_col1, top_col2 = st.columns([1.2, 1])
    with top_col1:
        name = st.text_input("이름", placeholder="예: 홍길동")
        birth_date = st.date_input(
            "생년월일",
            value=date(1995, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )
    with top_col2:
        birth_time = st.time_input("태어난 시간", value=time(12, 0), step=1800)
        st.caption("30분 단위로 선택할 수 있어요")
        calendar_type = st.radio("달력 구분", ["양력", "음력"], horizontal=True)

    bottom_col1, bottom_col2 = st.columns([1, 1])
    with bottom_col1:
        gender = st.radio("성별", ["여성", "남성", "기타/미선택"], horizontal=True)
    with bottom_col2:
        use_ai = st.checkbox("AI 해석 추가하기", value=False)
        st.caption("원본 입력값이 아니라 계산된 결과 기준으로 해석")

    submitted = st.form_submit_button("사주 보기", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if submitted:
    if not name.strip():
        st.error("이름을 입력해주세요.")
    else:
        try:
            saju = run_saju_engine(birth_date, birth_time, calendar_type)
            elements = count_five_elements(saju)
            element_summary = summarize_elements(elements)

            result = {
                "기본정보": {
                    "이름": name.strip(),
                    "생년월일": birth_date.isoformat(),
                    "출생시간": birth_time.strftime("%H:%M"),
                    "달력구분": calendar_type,
                    "성별": gender,
                },
                "사주팔자": {
                    "연주": saju.get("year_pillar", ""),
                    "월주": saju.get("month_pillar", ""),
                    "일주": saju.get("day_pillar", ""),
                    "시주": saju.get("hour_pillar", ""),
                },
                "천간지지": {
                    "year_stem": saju.get("year_stem", ""),
                    "year_branch": saju.get("year_branch", ""),
                    "month_stem": saju.get("month_stem", ""),
                    "month_branch": saju.get("month_branch", ""),
                    "day_stem": saju.get("day_stem", ""),
                    "day_branch": saju.get("day_branch", ""),
                    "hour_stem": saju.get("hour_stem", ""),
                    "hour_branch": saju.get("hour_branch", ""),
                },
                "오행": element_summary,
                "부가정보": {
                    "birth_date": saju.get("birth_date", ""),
                    "birth_time": saju.get("birth_time", ""),
                    "zi_time_type": saju.get("zi_time_type", None),
                    "solar_correction": saju.get("solar_correction", None),
                },
            }

            st.session_state["saju_result"] = result
            st.session_state["show_result"] = True

            if use_ai:
                st.session_state["ai_interpretation"] = get_ai_interpretation(name.strip(), result)
            else:
                st.session_state["ai_interpretation"] = None

        except Exception as e:
            st.error(f"사주 계산 중 오류가 발생했습니다: {e}")

if st.session_state.get("show_result") and st.session_state.get("saju_result"):
    result = st.session_state["saju_result"]
    element_counts = result["오행"]["오행 분포"]

    st.markdown("<div class='section-title'>사주 결과</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 사주팔자")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("연주", result["사주팔자"]["연주"])
        col2.metric("월주", result["사주팔자"]["월주"])
        col3.metric("일주", result["사주팔자"]["일주"])
        col4.metric("시주", result["사주팔자"]["시주"])

    left, right = st.columns([1.1, 0.9])

    with left:
        with st.container(border=True):
            st.markdown("### 오행 분포")
            chart_data = {
                "오행": list(element_counts.keys()),
                "개수": list(element_counts.values()),
            }
            st.bar_chart(chart_data, x="오행", y="개수")
            st.caption(
                f"많은 오행: {', '.join(result['오행']['많은 오행'])}  ·  적은 오행: {', '.join(result['오행']['적은 오행'])}"
            )

        ai_text = st.session_state.get("ai_interpretation")
        if ai_text:
            with st.container(border=True):
                st.markdown("### AI 해석")
                st.write(ai_text)

    with right:
        with st.container(border=True):
            st.markdown("### 입력 정보")
            st.write(f"**이름**: {result['기본정보']['이름']}")
            st.write(f"**생년월일**: {result['기본정보']['생년월일']}")
            st.write(f"**태어난 시간**: {result['기본정보']['출생시간']}")
            st.write(f"**달력 구분**: {result['기본정보']['달력구분']}")
            st.write(f"**성별**: {result['기본정보']['성별']}")

        with st.container(border=True):
            st.markdown("### 천간지지")
            st.json(result["천간지지"])

    with st.expander("상세 데이터 보기"):
        st.json(result)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("초기화", type="primary", use_container_width=True):
            reset_sensitive_state()
            st.rerun()
    with col2:
        if st.button("결과만 지우기", use_container_width=True):
            for key in ["saju_result", "ai_interpretation", "show_result"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

st.divider()
st.markdown(
    """
### requirements.txt에 추가할 내용
```txt
streamlit
sajupy
openai
```

### 다음 개선 포인트
- 윤달 입력 추가
- 태양시 보정 on/off 옵션 추가
- 오행 막대차트 UI 추가
- 십성/대운까지 확장
- 결과 PDF 저장 기능 추가
    """
)
