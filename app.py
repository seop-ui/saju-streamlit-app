import os
from datetime import date, time
from typing import Dict, Any, Optional

import streamlit as st

LANG = {
    "ko": {
        "app_title": "사주 프로그램",
        "hero_desc": "이름, 생년월일, 태어난 시간을 바탕으로 사주팔자, 오행 분포, 사주풀이를 확인할 수 있습니다.",
        "privacy_1": "MeSO",
        "privacy_2": "사주풀이",
        "privacy_3": "만세력",
        "privacy_4": "오행",
        "important": "유의사항",
        "important_body": "입력값은 저장하지 않습니다. 사주 보기를 누르면 계산과 사주풀이가 함께 진행됩니다.",
        "lang_select": "언어 선택",
        "lang_ko": "한국어",
        "lang_en": "English",
        "input_section": "입력 정보",
        "name": "이름",
        "birth_date": "생년월일",
        "birth_time": "태어난 시간",
        "time_basis": "출생 시간 기준",
        "time_us": "미국 기준",
        "time_kr": "한국 기준",
        "time_help": "30분 단위로 선택할 수 있어요",
        "calendar_type": "달력 구분",
        "solar": "양력",
        "lunar": "음력",
        "gender": "성별",
        "female": "여성",
        "male": "남성",
        "other": "기타",
        "submit": "사주 보기",
        "submit_help": "사주 계산과 사주풀이가 함께 진행됩니다",
        "result_section": "사주 결과",
        "pillars": "사주팔자",
        "year": "연주",
        "month": "월주",
        "day": "일주",
        "hour": "시주",
        "elements": "오행 분포",
        "input_info": "입력 정보",
        "stems_branches": "천간지지",
        "stems": "천간",
        "branches": "지지",
        "reset": "초기화",
        "clear_result": "결과만 지우기",
        "fortune_title": "사주풀이",
        "many_elements": "많은 오행",
        "few_elements": "적은 오행",
        "timezone_note": "미국에서 사용할 경우 입력한 출생 시간을 미국 현지 시간 기준으로 그대로 넣고, 출생 시간 기준에서 미국 기준을 선택하세요.",
        "name_required": "이름을 입력해주세요.",
        "error_prefix": "사주 계산 중 오류가 발생했습니다:",
        "time_us_help": "미국에서 태어났다면 현지 출생 시간을 그대로 입력하세요.",
        "time_kr_help": "한국 기준으로 해석하려면 한국 기준 시간을 입력하세요.",
    },
    "en": {
        "app_title": "Saju Reading",
        "hero_desc": "Enter a name, birth date, and birth time to view the Four Pillars, Five Elements, and a guided saju interpretation.",
        "privacy_1": "MeSO",
        "privacy_2": "Four Pillars Analysis",
        "privacy_3": "Ten Thousand Year Calendar",
        "privacy_4": "Five Elements",
        "important": "Important Notice",
        "important_body": "Your input data is not stored. When you click “View Reading,” both the calculation and analysis will be performed.",
        "lang_select": "Language",
        "lang_ko": "한국어",
        "lang_en": "English",
        "input_section": "Input Information",
        "name": "Name",
        "birth_date": "Birth Date",
        "birth_time": "Birth Time",
        "time_basis": "Birth Time Basis",
        "time_us": "US time",
        "time_kr": "Korea time",
        "time_help": "Choose in 30-minute intervals",
        "calendar_type": "Calendar Type",
        "solar": "Solar",
        "lunar": "Lunar",
        "gender": "Gender",
        "female": "Female",
        "male": "Male",
        "other": "Prefer not to say",
        "submit": "View Reading",
        "submit_help": "Calculation and interpretation will run together",
        "result_section": "Reading Result",
        "pillars": "Four Pillars",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "hour": "Hour",
        "elements": "Five Elements",
        "input_info": "Input Summary",
        "stems_branches": "Heavenly Stems & Earthly Branches",
        "stems": "Heavenly Stems",
        "branches": "Earthly Branches",
        "reset": "Reset",
        "clear_result": "Clear Result",
        "fortune_title": "Saju Interpretation",
        "many_elements": "Dominant elements",
        "few_elements": "Weaker elements",
        "timezone_note": "If the person was born in the US, enter the local birth time as-is and choose US time basis.",
        "name_required": "Please enter a name.",
        "error_prefix": "An error occurred while calculating the saju reading:",
        "time_us_help": "Use the local US birth time exactly as recorded.",
        "time_kr_help": "Choose Korea time only if you want the input interpreted on a Korea-time basis.",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "ko")
    return LANG[lang].get(key, key)


try:
    from sajupy import calculate_saju
except Exception:
    calculate_saju = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


st.set_page_config(page_title="Saju App", page_icon="🔮", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --brand-deep: #3B4F38;
        --brand-ivory: #F8F5F2;
        --brand-soft: #EEF2EC;
        --brand-line: #D8DED5;
        --brand-text: #243022;
        --brand-muted: #6E786C;
    }
    .stApp {
        background: linear-gradient(180deg, #FCFBF9 0%, var(--brand-ivory) 100%);
        color: var(--brand-text);
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }
    .hero-card {
        background: linear-gradient(135deg, #30412D 0%, #3B4F38 55%, #4A6247 100%);
        color: white;
        padding: 32px;
        border-radius: 28px;
        margin-bottom: 18px;
        box-shadow: 0 18px 40px rgba(59,79,56,0.20);
    }
    .soft-card {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--brand-line);
        border-radius: 22px;
        padding: 4px 4px 4px 4px;
        margin-bottom: 10px;
        box-shadow: 0 10px 28px rgba(59,79,56,0.06);
        backdrop-filter: blur(6px);
    }
    .pill-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 14px;
    }
    .pill {
        background: rgba(248,245,242,0.95);
        color: var(--brand-deep);
        padding: 8px 13px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        border: 1px solid rgba(255,255,255,0.35);
    }
    .section-title {
        font-size: 1.12rem;
        font-weight: 800;
        margin-bottom: 10px;
        margin-top: 8px;
        color: var(--brand-deep);
    }
    .stem-grid {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:12px;
    }
    .stem-item {
        background:#FBFAF8;
        border:1px solid var(--brand-line);
        border-radius:16px;
        padding:14px 14px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
    }
    .stem-label {
        font-size:0.80rem;
        color:var(--brand-muted);
        margin-bottom:4px;
    }
    .stem-value {
        font-size:1.18rem;
        font-weight:800;
        color:var(--brand-deep);
    }
    .fortune-box {
        background: #FFFEFC;
        border: 1px solid var(--brand-line);
        border-radius: 20px;
        padding: 20px 22px;
        line-height: 1.82;
    }
    .mini-note {
        color: var(--brand-muted);
        font-size: 0.92rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.78);
        border: 1px solid var(--brand-line);
        border-radius: 18px;
        padding: 14px 10px;
        box-shadow: 0 6px 18px rgba(59,79,56,0.04);
    }
    div[data-testid="stMetricLabel"] {
        color: var(--brand-muted);
    }
    div[data-testid="stMetricValue"] {
        color: var(--brand-deep);
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stDateInput > div > div,
    .stTimeInput > div > div {
        border-radius: 16px !important;
    }
    .stButton > button {
        border-radius: 16px !important;
        border: 1px solid var(--brand-line) !important;
    }
    .element-summary {
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        margin-top:10px;
    }
    .element-chip {
        background:#F3F0EB;
        border:1px solid var(--brand-line);
        border-radius:999px;
        padding:7px 11px;
        color:var(--brand-deep);
        font-size:0.9rem;
        font-weight:700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_sensitive_state() -> None:
    for key in [
        "name", "birth_date", "birth_time", "calendar_type", "gender",
        "saju_result", "ai_interpretation", "show_result", "time_basis",
    ]:
        if key in st.session_state:
            del st.session_state[key]


def element_of_char(char: str) -> str:
    stem_map = {
        "甲": "목", "乙": "목", "丙": "화", "丁": "화", "戊": "토", "己": "토", "庚": "금", "辛": "금", "壬": "수", "癸": "수",
    }
    branch_map = {
        "子": "수", "丑": "토", "寅": "목", "卯": "목", "辰": "토", "巳": "화", "午": "화", "未": "토", "申": "금", "酉": "금", "戌": "토", "亥": "수",
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
    return {"많은 오행": strong, "적은 오행": weak, "오행 분포": counts}


def run_saju_engine(birth_date: date, birth_time: time, calendar_type: str, time_basis: str) -> Dict[str, Any]:
    if calculate_saju is None:
        raise RuntimeError("sajupy 라이브러리를 불러오지 못했습니다.")

    kwargs = {
        "year": birth_date.year,
        "month": birth_date.month,
        "day": birth_date.day,
        "hour": birth_time.hour,
        "minute": birth_time.minute,
    }

    if calendar_type in ["음력", "Lunar"]:
        kwargs["is_lunar"] = True
        kwargs["is_leap_month"] = False

    # sajupy 현재 호출 규격상 country 인자를 직접 받지 않을 수 있어
    # 우선 UI에서 기준만 받고 계산 엔진에는 안전한 공통 인자만 넘긴다.
    return calculate_saju(**kwargs)


def build_ai_prompt(name: str, result: Dict[str, Any]) -> str:
    lang = result.get("기본정보", {}).get("언어", "ko")
    ending = "참고용으로 가볍게 봐주세요." if lang == "ko" else "Please take this as a light reference."
    return f"""
당신은 사주풀이 보조 어시스턴트입니다.
아래 정보는 사용자의 원본 생년월일이 아니라 이미 계산된 사주 결과입니다.
이 결과만 바탕으로 {('한국어' if lang == 'ko' else '영어')}로 자연스럽고 읽기 쉬운 사주풀이를 작성하세요.

작성 규칙:
- 과장하거나 단정적으로 예언하지 말 것
- 미신적으로 몰아가지 말고 성향과 흐름 중심으로 설명할 것
- 이름은 반드시 {name} 님 또는 {name} 로만 표기할 것
- 전체 분량은 900~1400자 내외 또는 이에 준하는 영어 분량
- 투자, 의료, 법률, 건강 진단처럼 고위험 조언 금지
- 같은 내용을 반복하지 말 것
- 오행에서 설명한 내용과 성향에서 설명한 내용이 겹치면 하나로 정리할 것
- 읽기 쉽게 소제목과 짧은 단락으로 구성할 것
- 마지막 문장은 반드시 '{ending}' 로 끝낼 것

출력 구조:
1. 사주 요약(Fortune Summary)
2. 사주팔자 풀이(Four Pillars Interpretation)
3. 오행 풀이(Five Elements Analysis)
4. 나는 어떤 사람인가(What Kind of Person Am I?)
5. 타고난 강점과 조심할 점(Innate Strengths & Points to Watch)
6. 잘 맞는 환경과 일 스타일(Best-Fit Environment & Work Style)
7. 대인관계와 감정 흐름(Relationships & Emotional Tendencies)
8. 중요한 조언(Key Advice)
9. 재물운, 애정운, 가족운, 건강운(Wealth, Love, Family & Health Luck)

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


if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"

header_left, header_right = st.columns([0.8, 0.2])
with header_right:
    selected_lang = st.radio(
        t("lang_select"), ["ko", "en"],
        index=0 if st.session_state.get("lang") == "ko" else 1,
        format_func=lambda x: LANG[x]["lang_ko"] if x == "ko" else LANG[x]["lang_en"],
        horizontal=True,
    )
    st.session_state["lang"] = selected_lang

with header_left:
    st.markdown(
        f"""
        <div class="hero-card">
            <div style="font-size:2rem; font-weight:800; margin-bottom:8px;">🔮 {t('app_title')}</div>
            <div style="font-size:1.02rem; opacity:0.94; line-height:1.65;">{t('hero_desc')}</div>
            <div class="pill-row">
                <span class="pill">{t('privacy_1')}</span>
                <span class="pill">{t('privacy_2')}</span>
                <span class="pill">{t('privacy_3')}</span>
                <span class="pill">{t('privacy_4')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander(t("important"), expanded=False):
    st.write(t("important_body"))
    st.caption(t("timezone_note"))

st.markdown(f'<div class="section-title">{t("input_section")}</div>', unsafe_allow_html=True)
st.markdown('<div class="soft-card">', unsafe_allow_html=True)
with st.form("saju_form", clear_on_submit=False):
    top_col1, top_col2 = st.columns([1.15, 1])
    with top_col1:
        name = st.text_input(t("name"), placeholder="예: 홍길동" if st.session_state.get("lang") == "ko" else "e.g. Olivia Kim")
        birth_date = st.date_input(
            t("birth_date"), value=date(1995, 1, 1), min_value=date(1900, 1, 1), max_value=date.today(),
        )
        gender = st.radio(t("gender"), [t("female"), t("male"), t("other")], horizontal=True)
    with top_col2:
        birth_time = st.time_input(t("birth_time"), value=time(12, 0), step=1800)
        st.caption(t("time_help"))
        time_basis = st.radio(t("time_basis"), [t("time_us"), t("time_kr")], horizontal=True)
        st.caption(t("time_us_help") if time_basis == t("time_us") else t("time_kr_help"))
        calendar_type = st.radio(t("calendar_type"), [t("solar"), t("lunar")], horizontal=True)

    st.caption(t("submit_help"))
    submitted = st.form_submit_button(t("submit"), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if submitted:
    if not name.strip():
        st.error(t("name_required"))
    else:
        try:
            saju = run_saju_engine(birth_date, birth_time, calendar_type, time_basis)
            elements = count_five_elements(saju)
            element_summary = summarize_elements(elements)
            result = {
                "기본정보": {
                    "이름": name.strip(),
                    "생년월일": birth_date.isoformat(),
                    "출생시간": birth_time.strftime("%H:%M"),
                    "달력구분": calendar_type,
                    "성별": gender,
                    "출생시간기준": time_basis,
                    "언어": st.session_state.get("lang", "ko"),
                },
                "사주팔자": {
                    "연주": saju.get("year_pillar", ""),
                    "월주": saju.get("month_pillar", ""),
                    "일주": saju.get("day_pillar", ""),
                    "시주": saju.get("hour_pillar", ""),
                },
                "천간지지": {
                    "연간": saju.get("year_stem", ""),
                    "연지": saju.get("year_branch", ""),
                    "월간": saju.get("month_stem", ""),
                    "월지": saju.get("month_branch", ""),
                    "일간": saju.get("day_stem", ""),
                    "일지": saju.get("day_branch", ""),
                    "시간": saju.get("hour_stem", ""),
                    "시지": saju.get("hour_branch", ""),
                },
                "오행": element_summary,
            }
            st.session_state["saju_result"] = result
            st.session_state["show_result"] = True
            st.session_state["ai_interpretation"] = get_ai_interpretation(name.strip(), result)
        except Exception as e:
            st.error(f"{t('error_prefix')} {e}")

if st.session_state.get("show_result") and st.session_state.get("saju_result"):
    result = st.session_state["saju_result"]
    element_counts = result["오행"]["오행 분포"]

    st.markdown(f"<div class='section-title'>{t('result_section')}</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"### {t('pillars')}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t("year"), result["사주팔자"]["연주"])
        col2.metric(t("month"), result["사주팔자"]["월주"])
        col3.metric(t("day"), result["사주팔자"]["일주"])
        col4.metric(t("hour"), result["사주팔자"]["시주"])

    left, right = st.columns([1.1, 0.9])

    with left:
        with st.container(border=True):
            st.markdown(f"### {t('elements')}")
            bar_cols = st.columns(5)
            labels = list(element_counts.keys())
            values = list(element_counts.values())
            max_value = max(values) if values else 1
            for i, (label, value) in enumerate(zip(labels, values)):
                with bar_cols[i]:
                    st.metric(label, value)
                    percent = int((value / max_value) * 100) if max_value else 0
                    st.progress(percent / 100)
            st.markdown(
                f"<div class='element-summary'>"
                f"<span class='element-chip'>{t('many_elements')}: {', '.join(result['오행']['많은 오행'])}</span>"
                f"<span class='element-chip'>{t('few_elements')}: {', '.join(result['오행']['적은 오행'])}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        ai_text = st.session_state.get("ai_interpretation")
        if ai_text:
            with st.container(border=True):
                st.markdown(f"### {t('fortune_title')}")
                st.markdown(f"<div class='fortune-box'>{ai_text}</div>", unsafe_allow_html=True)

    with right:
        with st.container(border=True):
            st.markdown(f"### {t('input_info')}")
            st.write(f"**{t('name')}**: {result['기본정보']['이름']}")
            st.write(f"**{t('birth_date')}**: {result['기본정보']['생년월일']}")
            st.write(f"**{t('birth_time')}**: {result['기본정보']['출생시간']}")
            st.write(f"**{t('calendar_type')}**: {result['기본정보']['달력구분']}")
            st.write(f"**{t('gender')}**: {result['기본정보']['성별']}")
            st.write(f"**{t('time_basis')}**: {result['기본정보']['출생시간기준']}")

        with st.container(border=True):
            st.markdown(f"### {t('stems_branches')}")
            stem_left, stem_right = st.columns(2)
            with stem_left:
                st.markdown(f"**{t('stems')}**")
                st.markdown(
                    f"""
                    <div class='stem-grid'>
                        <div class='stem-item'><div class='stem-label'>{t('year')}</div><div class='stem-value'>{result['천간지지']['연간']}</div></div>
                        <div class='stem-item'><div class='stem-label'>{t('month')}</div><div class='stem-value'>{result['천간지지']['월간']}</div></div>
                        <div class='stem-item'><div class='stem-label'>{t('day')}</div><div class='stem-value'>{result['천간지지']['일간']}</div></div>
                        <div class='stem-item'><div class='stem-label'>{t('hour')}</div><div class='stem-value'>{result['천간지지']['시간']}</div></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with stem_right:
                st.markdown(f"**{t('branches')}**")
                st.markdown(
                    f"""
                    <div class='stem-grid'>
                        <div class='stem-item'><div class='stem-label'>{t('year')}</div><div class='stem-value'>{result['천간지지']['연지']}</div></div>
                        <div class='stem-item'><div class='stem-label'>{t('month')}</div><div class='stem-value'>{result['천간지지']['월지']}</div></div>
                        <div class='stem-item'><div class='stem-label'>{t('day')}</div><div class='stem-value'>{result['천간지지']['일지']}</div></div>
                        <div class='stem-item'><div class='stem-label'>{t('hour')}</div><div class='stem-value'>{result['천간지지']['시지']}</div></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("reset"), type="primary", use_container_width=True):
            reset_sensitive_state()
            st.rerun()
    with col2:
        if st.button(t("clear_result"), use_container_width=True):
            for key in ["saju_result", "ai_interpretation", "show_result"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
