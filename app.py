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
            "[4국01-03] 상황에 적절한 준언어·비언어적 표현을 활용하여 듣고 말한다.",
            "[4국01-04] 상황과 상대의 입장을 이해하고 예의를 지키며 대화한다.",
            "[4국05-04] 감각적 표현에 유의하여 작품을 감상하고, 감각적 표현을 활용하여 자신의 생각이나 감정을 표현한다.",
            "[4국05-05] 재미나 감동을 느끼며 작품을 즐겨 감상하는 태도를 지닌다."
        ],
        "분명하고 유창하게": [
            "[4국04-03] 기본적인 문장의 짜임을 이해하고 적절하게 사용한다.",
            "[4국02-01] 글의 의미를 파악하며 유창하게 글을 읽는다.",
            "[4국01-03] 상황에 적절한 준언어·비언어적 표현을 활용하여 듣고 말한다."
        ],
        "짜임새 있는 글, 재미와 감동이 있는 글": [
            "[4국03-01] 중심 문장과 뒷받침 문장을 갖추어 문단을 쓰고, 문장과 문단을 중심으로 고쳐 쓴다.",
            "[4국05-05] 재미나 감동을 느끼며 작품을 즐겨 감상하는 태도를 지닌다."
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
        # GOOGLE_API_KEY와 GEMINI_API_KEY 모두 지원
        api_key = (
            st.secrets.get("GOOGLE_API_KEY") or 
            st.secrets.get("GEMINI_API_KEY") or
            os.getenv("GOOGLE_API_KEY") or
            os.getenv("GEMINI_API_KEY")
        )
        
        if not api_key:
            st.error("API 키가 설정되지 않았습니다. GOOGLE_API_KEY 또는 GEMINI_API_KEY를 환경변수나 Streamlit secrets에 설정해주세요.")
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

def generate_question_prompt(grade, semester, unit, achievement_standard, category):
    """질문 카테고리에 맞는 질문을 생성하는 프롬프트를 만듭니다."""
    
    category_questions = {
        "AI 도구 활용 기초 가이드": [
            "이 단원에서 AI 도구를 처음 사용하는 교사를 위한 기본적인 가이드라인은 무엇인가요?",
            "AI 도구 사용 시 주의해야 할 점과 안전 수칙은 무엇인가요?",
            "학생들의 수준에 맞는 AI 도구 선택 기준은 무엇인가요?"
        ],
        "프롬프트 템플릿 개발 가이드": [
            "이 성취기준에 최적화된 AI 프롬프트 템플릿을 어떻게 작성할 수 있나요?",
            "효과적인 프롬프트 작성 시 고려해야 할 요소들은 무엇인가요?",
            "학생들의 이해도를 높이는 프롬프트 구조는 어떻게 만들어야 하나요?"
        ],
        "AI 활용 사례 추천": [
            "이 단원에서 활용할 수 있는 구체적인 AI 도구 활용 사례를 추천해주세요.",
            "수업 단계별로 AI 도구를 어떻게 활용할 수 있나요?",
            "학생들의 참여도를 높이는 AI 활용 활동은 무엇이 있나요?"
        ],
        "디지털 도구 활용 방법": [
            "이 단원에서 활용할 수 있는 다양한 디지털 도구는 무엇이 있나요?",
            "디지털 도구와 AI를 결합한 수업 설계 방법은 무엇인가요?",
            "학생들의 디지털 역량을 기르는 도구 활용법은 무엇인가요?"
        ]
    }
    
    prompt = f"""
당신은 초등학교 국어 교사를 위한 AI 도구 활용 전문가입니다.

현재 상황:
- 학년: {grade}
- 학기: {semester}
- 단원: {unit}
- 성취기준: {achievement_standard}
- 질문 카테고리: {category}

위의 상황에 맞는 구체적이고 실용적인 질문 3개를 생성해주세요.
각 질문은 교사가 실제로 궁금해할 만한 내용이어야 하며, 
해당 성취기준과 단원의 특성을 고려한 질문이어야 합니다.

다음 형식으로 답변해주세요:

1. [첫 번째 질문]
2. [두 번째 질문]  
3. [세 번째 질문]

각 질문은 구체적이고 실용적이어야 하며, 교사가 바로 적용할 수 있는 내용이어야 합니다.
"""
    
    return prompt

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
2. **프롬프트 템플릿 개발 가이드**: 해당 성취기준에 최적화된 생성형 AI 활용 시 프롬프트 작성 방법 제시
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

def render_common_settings(tab_key=""):
    """공통 설정 부분을 렌더링합니다."""
    # 첫 번째 줄: 학년, 학기, 단원
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 학년 선택 (3학년만)
        grade = st.selectbox(
            "학년 선택",
            ["3학년"],
            key=f"grade_{tab_key}"
        )
    
    with col2:
        # 학기 선택
        semester = st.selectbox(
            "학기 선택",
            ["1학기", "2학기"],
            key=f"semester_{tab_key}"
        )
    
    with col3:
        # 단원 선택 (동적)
        if grade == "3학년" and semester in GRADE_3_DATA:
            units = list(GRADE_3_DATA[semester].keys())
            selected_unit = st.selectbox(
                "단원 선택",
                units,
                key=f"unit_{tab_key}"
            )
        else:
            selected_unit = st.text_input("단원명 입력", placeholder="예: 바른 자세로 듣기", key=f"unit_input_{tab_key}")
    
    # 두 번째 줄: 성취기준 선택 (전체 너비 사용)
    st.markdown("### 성취기준 선택")
    
    # 성취기준 선택 (동적)
    if grade == "3학년" and semester in GRADE_3_DATA and selected_unit in GRADE_3_DATA[semester]:
        achievement_standards = GRADE_3_DATA[semester][selected_unit]
        selected_achievement_standard = st.selectbox(
            "성취기준을 선택하세요",
            achievement_standards,
            key=f"achievement_{tab_key}",
            help="긴 성취기준 문장을 모두 확인할 수 있도록 전체 너비를 사용합니다.",
            disabled=True
        )
        
        # 성취기준 내용 자동 설정
        achievement_standard_content = selected_achievement_standard
        
        # 선택된 성취기준 미리보기
        if selected_achievement_standard:
            st.info(f"**선택된 성취기준:** {selected_achievement_standard}")
    else:
        col4, col5 = st.columns([1, 1])
        with col4:
            selected_achievement_standard = st.text_input("성취기준명 입력", placeholder="예: 바른 자세로 듣는 습관을 기른다.", key=f"achievement_input_{tab_key}")
        with col5:
            achievement_standard_content = st.text_area(
                "성취기준 내용 입력",
                placeholder="해당 성취기준의 내용을 입력해주세요.",
                height=100,
                key=f"achievement_content_{tab_key}"
            )
    
    return {
        "grade": grade,
        "semester": semester,
        "unit": selected_unit,
        "achievement_standard": selected_achievement_standard,
        "achievement_standard_content": achievement_standard_content
    }

def render_question_recommendation_tab():
    """질문 추천받기 탭을 렌더링합니다."""
    st.header("🤖 질문 추천받기")
    st.markdown("AI가 자동으로 적절한 질문을 생성하고 답변해드립니다.")
    
    # 공통 설정
    settings = render_common_settings("recommend")
    
    # 질문 카테고리 선택
    question_category = st.selectbox(
        "질문 카테고리 선택",
        [
            "AI 도구 활용 기초 가이드",
            "프롬프트 템플릿 개발 가이드", 
            "AI 활용 사례 추천",
            "디지털 도구 활용 방법"
        ],
        key="category_recommend"
    )
    
    # 자동 질문하기 버튼
    if st.button("자동 질문하기", type="primary", use_container_width=True, key="auto_question"):
        # LLM 로드 (처음 한 번만)
        if st.session_state.llm is None:
            with st.spinner("AI 모델을 로드하고 있습니다..."):
                st.session_state.llm = create_llm()
                if st.session_state.llm:
                    st.success("AI 모델 로드 완료!")
                else:
                    st.error("AI 모델 로드에 실패했습니다.")
        
        # 자동 질문 및 답변 생성
        if st.session_state.llm:
            try:
                with st.spinner("AI가 질문을 생성하고 답변을 준비하고 있습니다..."):
                    # 교육과정 데이터 로드
                    curriculum_data = load_curriculum_data()
                    
                    # 자동 질문 및 답변 생성 프롬프트
                    auto_prompt = f"""
당신은 초등학교 국어 교사를 위한 AI 도구 활용 전문가입니다.

현재 상황:
- 학년: {settings['grade']}
- 학기: {settings['semester']}
- 단원: {settings['unit']}
- 성취기준: {settings['achievement_standard_content']}
- 질문 카테고리: {question_category}

위의 상황에 맞는 가장 적절하고 실용적인 질문 하나를 생성하고, 그에 대한 구체적이고 실용적인 답변을 제공해주세요.

다음 형식으로 답변해주세요:

## 🤔 생성된 질문
[적절한 질문 하나]

## 💡 AI 답변
[구체적이고 실용적인 답변]

답변은 다음을 포함해야 합니다:
- 간결하고 실용적인 조언
- 구체적인 예시나 단계별 가이드
- 교사가 바로 적용할 수 있는 팁
- 안전하고 윤리적인 AI 활용 방법
"""
                    
                    # 교육과정 데이터가 있으면 추가
                    if curriculum_data:
                        auto_prompt += f"\n\n참고할 교육과정 내용:\n{curriculum_data}"
                    
                    # 질문 및 답변 생성
                    response = st.session_state.llm.invoke(auto_prompt)
                    
                    # 결과 표시
                    st.markdown("### 🎯 AI 자동 질문 및 답변:")
                    st.write(response.content)
                    
            except Exception as e:
                st.error(f"질문 및 답변 생성 중 오류가 발생했습니다: {str(e)}")

def render_question_input_tab():
    """질문 입력하기 탭을 렌더링합니다."""
    st.header("✍️ 질문 입력하기")
    st.markdown("직접 질문을 입력하여 AI 답변을 받아보세요.")
    
    # 공통 설정
    settings = render_common_settings("input")
    
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
            ],
            key="category_input"
        )
    
    with col8:
        # 질문 입력
        user_question = st.text_area(
            "질문 입력",
            placeholder="구체적인 질문을 입력해주세요. 예: 3학년 1학기 듣기 단원에서 AI 도구를 어떻게 활용할 수 있을까요?",
            height=100,
            key="question_input"
        )
    
    # 질문 제출 버튼
    if st.button("질문하기", type="primary", use_container_width=True, key="submit_question"):
        if not user_question:
            st.error("질문을 입력해주세요.")
        else:
            st.session_state.current_question = {
                "grade": settings['grade'],
                "semester": settings['semester'],
                "unit": settings['unit'],
                "achievement_standard": settings['achievement_standard'],
                "achievement_standard_content": settings['achievement_standard_content'],
                "category": question_category,
                "question": user_question
            }

def render_answer_section():
    """답변 섹션을 렌더링합니다."""
    st.markdown("---")
    
    # 답변 영역
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
                    # 질문 입력 탭에서 온 경우
                    if 'current_question' in st.session_state:
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

def main():
    st.title("📚 초등국어 AI 도구 활용 가이드")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["🤖 질문 추천받기", "✍️ 질문 입력하기"])
    
    with tab1:
        render_question_recommendation_tab()
    
    with tab2:
        render_question_input_tab()
    
    # 답변 섹션 (공통)
    render_answer_section()
    
    # 사용법 안내
    with st.expander("📖 사용법 안내", expanded=False):
        st.markdown("""
        ### 사용 방법:
        
        #### 🤖 질문 추천받기:
        1. **설정**: 학년, 학기, 단원, 성취기준을 선택하세요.
        2. **카테고리 선택**: 원하는 질문 카테고리를 선택하세요.
        3. **자동 질문하기**: AI가 자동으로 적절한 질문을 생성하고 답변해드립니다.
        
        #### ✍️ 질문 입력하기:
        1. **설정**: 학년, 학기, 단원, 성취기준을 선택하세요.
        2. **카테고리 선택**: 질문 카테고리를 선택하세요.
        3. **질문 입력**: 구체적인 질문을 직접 입력하세요.
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