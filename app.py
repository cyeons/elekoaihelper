import streamlit as st
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# 환경 변수 로드 (로컬에서는 .env, Streamlit Cloud에서는 secrets.toml)
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="초등국어 AI 도구 활용 가이드",
    page_icon="📚",
    layout="wide"
)

# 세션 상태 초기화
if 'llm' not in st.session_state:
    st.session_state.llm = None

# 3학년 1~2학기 데이터 (사용자가 내용을 채워넣을 예정)
GRADE_3_DATA = {
    "1학기": {
        "생생하게 표현해요": [
            "감각적 표현에 유의하여 작품을 감상하고, 감각적 표현을 활용하여 자신의 생각이나 감정을 표현한다.",
            "성취기준2",
            "성취기준3"
        ],
        "단원2": [
            "성취기준1",
            "성취기준2",
            "성취기준3"
        ]
    },
    "2학기": {
        "단원1": [
            "성취기준1",
            "성취기준2",
            "성취기준3"
        ],
        "단원2": [
            "성취기준1",
            "성취기준2",
            "성취기준3"
        ]
    }
}

def load_curriculum_data():
    """교육과정 데이터를 로드합니다."""
    try:
        # MD 파일 경로
        md_path = "2022_korean_curriculum.md"
        
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            st.warning("교육과정 MD 파일을 찾을 수 없습니다. 기본 프롬프트로 진행합니다.")
            return ""
    
    except Exception as e:
        st.error(f"교육과정 데이터 로드 중 오류가 발생했습니다: {str(e)}")
        return ""

def create_llm():
    """LLM을 생성합니다."""
    try:
        # Streamlit Cloud에서는 secrets를 사용, 로컬에서는 환경변수 사용
        api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
        
        if not api_key:
            st.error("GOOGLE_API_KEY가 설정되지 않았습니다. 환경변수나 Streamlit secrets를 확인해주세요.")
            return None
            
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.7
        )
        return llm
    
    except Exception as e:
        st.error(f"LLM 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def generate_prompt_template(grade, semester, unit, achievement_standard, question, curriculum_data=""):
    """성취기준에 맞는 프롬프트 템플릿을 생성합니다."""
    
    base_prompt = f"""
당신은 초등학교 국어 교사를 위한 AI 도구 활용 전문가입니다.

현재 상황:
- 학년: {grade}학년
- 학기: {semester}학기  
- 단원: {unit}
- 성취기준: {achievement_standard}

교사의 질문: {question}

다음 중 하나의 역할로 답변해주세요:

1. **AI 도구 활용 기초 가이드**: 교사가 AI 도구를 처음 사용할 때 필요한 기본 지식과 팁을 제공
2. **프롬프트 템플릿 개발 가이드**: 해당 성취기준에 최적화된 프롬프트 작성 방법 제시
3. **AI 활용 사례 추천**: 구체적인 수업 활동과 AI 도구 활용 방법 제안
4. **디지털 도구 활용 방법**: 수업에서 활용할 수 있는 다양한 디지털 도구와 활용법 안내

답변은 다음 형식으로 제공해주세요:
- 간결하고 실용적인 조언
- 구체적인 예시나 단계별 가이드
- 교사가 바로 적용할 수 있는 팁
- 안전하고 윤리적인 AI 활용 방법

2022 국어 개정 교육과정의 내용을 참고하여 답변해주세요.
"""
    
    # 교육과정 데이터가 있으면 추가
    if curriculum_data:
        base_prompt += f"\n\n참고할 교육과정 내용:\n{curriculum_data}"
    
    return base_prompt

def main():
    st.title("📚 초등국어 AI 도구 활용 가이드")
    st.markdown("---")
    
    # 첫 번째 줄: 학년, 학기, 단원
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 학년 선택 (3학년만)
        grade = st.selectbox(
            "학년 선택",
            ["3학년"]
        )
    
    with col2:
        # 학기 선택
        semester = st.selectbox(
            "학기 선택",
            ["1학기", "2학기"]
        )
    
    with col3:
        # 단원 선택 (동적)
        if grade == "3학년" and semester in GRADE_3_DATA:
            units = list(GRADE_3_DATA[semester].keys())
            selected_unit = st.selectbox(
                "단원 선택",
                units
            )
        else:
            selected_unit = st.text_input("단원명 입력", placeholder="예: 바른 자세로 듣기")
    
    # 두 번째 줄: 성취기준 선택
    col4, col5, col6 = st.columns([1, 1, 1])
    
    with col4:
        # 성취기준 선택 (동적)
        if grade == "3학년" and semester in GRADE_3_DATA and selected_unit in GRADE_3_DATA[semester]:
            achievement_standards = GRADE_3_DATA[semester][selected_unit]
            selected_achievement_standard = st.selectbox(
                "성취기준 선택",
                achievement_standards
            )
            
            # 성취기준 내용 자동 설정
            achievement_standard_content = selected_achievement_standard
        else:
            selected_achievement_standard = st.text_input("성취기준명 입력", placeholder="예: 바른 자세로 듣는 습관을 기른다.")
            achievement_standard_content = st.text_area(
                "성취기준 내용 입력",
                placeholder="해당 성취기준의 내용을 입력해주세요.",
                height=100
            )
    
    # 질문 카테고리와 질문 입력
    col7, col8 = st.columns([1, 2])
    
    with col7:
        # 질문 카테고리 선택
        question_category = st.selectbox(
            "질문 카테고리",
            [
                "AI 도구 활용 기초 가이드",
                "프롬프트 템플릿 개발 가이드", 
                "AI 활용 사례 추천",
                "디지털 도구 활용 방법"
            ]
        )
    
    with col8:
        # 질문 입력
        user_question = st.text_area(
            "질문 입력",
            placeholder="구체적인 질문을 입력해주세요. 예: 3학년 1학기 듣기 단원에서 AI 도구를 어떻게 활용할 수 있을까요?",
            height=100
        )
    
    # 질문 제출 버튼
    if st.button("질문하기", type="primary", use_container_width=True):
        if not user_question:
            st.error("질문을 입력해주세요.")
        else:
            st.session_state.current_question = {
                "grade": grade,
                "semester": semester,
                "unit": selected_unit,
                "achievement_standard": selected_achievement_standard,
                "achievement_standard_content": achievement_standard_content,
                "category": question_category,
                "question": user_question
            }
    
    st.markdown("---")
    
    # 하단 답변 영역
    if 'current_question' in st.session_state:
        st.header("💡 AI 답변")
        
        # 교육과정 데이터 로드
        curriculum_data = load_curriculum_data()
        
        # LLM 로드 (처음 한 번만)
        if st.session_state.llm is None:
            with st.spinner("AI 모델을 로드하고 있습니다..."):
                st.session_state.llm = create_llm()
                if st.session_state.llm:
                    st.success("AI 모델 로드 완료!")
                else:
                    st.error("AI 모델 로드에 실패했습니다.")
        
        # 질문 처리
        if st.session_state.llm:
            try:
                with st.spinner("AI가 답변을 생성하고 있습니다..."):
                    # 프롬프트 템플릿 생성
                    prompt = generate_prompt_template(
                        st.session_state.current_question['grade'],
                        st.session_state.current_question['semester'],
                        st.session_state.current_question['unit'],
                        st.session_state.current_question['achievement_standard_content'],
                        st.session_state.current_question['question'],
                        curriculum_data
                    )
                    
                    # 답변 생성
                    response = st.session_state.llm.invoke(prompt)
                    
                    # 답변 표시
                    st.markdown("### 답변:")
                    st.write(response.content)
                    
            except Exception as e:
                st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 사용법 안내
    with st.expander("📖 사용법 안내", expanded=False):
        st.markdown("""
        ### 사용 방법:
        1. **설정**: 상단에서 학년, 학기, 단원, 성취기준을 선택하세요.
        2. **질문 카테고리**: 원하는 도움 유형을 선택하세요.
        3. **질문 입력**: 구체적인 질문을 입력하세요.
        4. **질문하기**: 버튼을 클릭하여 AI 답변을 받으세요.
        
        ### 지원하는 질문 유형:
        - AI 도구 활용 기초 가이드
        - 프롬프트 템플릿 개발 가이드
        - AI 활용 사례 추천
        - 디지털 도구 활용 방법
        
        ### 현재 지원 학년:
        - 3학년 1학기, 2학기
        """)

if __name__ == "__main__":
    main() 