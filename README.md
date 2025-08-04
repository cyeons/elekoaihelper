# 초등국어 AI 도구 활용 가이드

초등학교 국어 교사를 위한 AI 및 에듀테크 도구 활용 가이드 웹 애플리케이션입니다.

## 🎯 주요 기능

- **학년/학기/단원/성취기준 기반 질문**: 교사가 현재 수업 상황에 맞는 구체적인 도움을 받을 수 있습니다.
- **AI 도구 활용 가이드**: AI 도구를 처음 사용하는 교사를 위한 기초 가이드
- **프롬프트 템플릿 개발**: 성취기준에 최적화된 프롬프트 작성 방법 제시
- **AI 활용 사례 추천**: 구체적인 수업 활동과 AI 도구 활용 방법 제안
- **디지털 도구 활용 방법**: 수업에서 활용할 수 있는 다양한 디지털 도구와 활용법 안내

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **Vector Database**: ChromaDB
- **PDF Processing**: PyPDF2
- **Language Model**: LangChain

## 📋 설치 및 실행

### 1. 저장소 클론
```bash
git clone [repository-url]
cd EleAIHelper
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
1. `env_example.txt` 파일을 참고하여 `.env` 파일을 생성합니다.
2. Google Gemini API 키를 발급받아 설정합니다.

```bash
# .env 파일 생성
GOOGLE_API_KEY=your_actual_api_key_here
```

### 5. PDF 파일 준비
- `2022_국어_개정_교육과정.pdf` 파일을 프로젝트 루트 디렉토리에 위치시킵니다.

### 6. 애플리케이션 실행
```bash
streamlit run app.py
```

## 🚀 사용 방법

1. **설정**: 사이드바에서 학년, 학기, 단원, 성취기준을 입력합니다.
2. **질문 카테고리**: 원하는 도움 유형을 선택합니다.
3. **질문 입력**: 구체적인 질문을 입력합니다.
4. **질문하기**: 버튼을 클릭하여 AI 답변을 받습니다.

## 📁 프로젝트 구조

```
EleAIHelper/
├── app.py                 # 메인 애플리케이션
├── requirements.txt       # Python 의존성
├── env_example.txt       # 환경 변수 예시
├── README.md             # 프로젝트 설명
├── 2022_국어_개정_교육과정.pdf  # 교육과정 PDF (사용자가 추가)
└── chroma_db/           # 벡터 데이터베이스 (자동 생성)
```

## 🔧 주요 구성 요소

### 1. PDF 처리 및 벡터화
- PyPDF2를 사용하여 PDF 텍스트 추출
- LangChain의 RecursiveCharacterTextSplitter로 텍스트 분할
- Google Generative AI Embeddings로 벡터화
- ChromaDB에 저장하여 검색 가능하게 함

### 2. 프롬프트 템플릿
성취기준과 질문 카테고리에 맞는 맞춤형 프롬프트를 생성합니다:
- AI 도구 활용 기초 가이드
- 프롬프트 템플릿 개발 가이드
- AI 활용 사례 추천
- 디지털 도구 활용 방법

### 3. 대화 체인
- ConversationalRetrievalChain을 사용하여 컨텍스트 기반 답변
- 벡터 스토어에서 관련 정보 검색
- 메모리를 통한 대화 맥락 유지

## 🚀 배포

### Streamlit Cloud 배포
1. GitHub에 코드를 푸시합니다.
2. [Streamlit Cloud](https://streamlit.io/cloud)에 로그인합니다.
3. 새 앱을 생성하고 GitHub 저장소를 연결합니다.
4. 환경 변수에서 `GOOGLE_API_KEY`를 설정합니다.
5. PDF 파일을 앱에 업로드하거나 별도로 관리합니다.

## 📝 주의사항

- Google Gemini API 키가 필요합니다.
- PDF 파일은 2MB 이하 권장합니다.
- 첫 실행 시 PDF 처리에 시간이 걸릴 수 있습니다.
- API 사용량에 따른 비용이 발생할 수 있습니다.

## 🤝 기여

프로젝트 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다!

## 📄 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다. 