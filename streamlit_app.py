import streamlit as st
from google import genai

# ── 페이지 기본 설정 ──────────────────────────────────────────────────────────
st.set_page_config(page_title="딸깍 스터디 AI 챗봇", page_icon="🤖")
st.title("딸깍 스터디 AI 챗봇 🤖")

# ── API 키 로드 ────────────────────────────────────────────────────────────────
# st.secrets 는 .streamlit/secrets.toml 파일에서 키를 안전하게 읽어옵니다.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "⚠️ **GEMINI_API_KEY 를 찾을 수 없어요!**\n\n"
        "`.streamlit/secrets.toml` 파일에 아래처럼 키를 입력해 주세요:\n\n"
        "```toml\n"
        'GEMINI_API_KEY = "여기에_실제_키_입력"\n'
        "```\n\n"
        "API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey) 에서 무료로 발급받을 수 있습니다."
    )
    st.stop()  # 키가 없으면 여기서 앱 실행을 멈춥니다.

# ── Gemini 클라이언트 초기화 ──────────────────────────────────────────────────
client = genai.Client(api_key=api_key)
MODEL = "gemini-2.5-flash"

# ── 대화 기록 초기화 ──────────────────────────────────────────────────────────
# st.session_state 는 브라우저 탭이 열려 있는 동안 대화 기록을 유지합니다.
if "messages" not in st.session_state:
    st.session_state.messages = []  # {"role": "user"|"assistant", "content": "..."}

# ── 저장된 대화 기록을 화면에 출력 ───────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 사용자 입력 처리 ──────────────────────────────────────────────────────────
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    # 사용자 말풍선 표시 및 기록 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Gemini API 에 보낼 대화 기록 구성
    # google-genai 는 "contents" 리스트에 role/parts 형태로 전달합니다.
    # Gemini API 는 AI 역할을 "assistant" 가 아닌 "model" 로 표기합니다.
    history = [
        {"role": "model" if msg["role"] == "assistant" else "user", "parts": [{"text": msg["content"]}]}
        for msg in st.session_state.messages
    ]

    # AI 답변 생성 및 스트리밍 출력
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        with st.spinner("생각하는 중..."):
            response = client.models.generate_content(
                model=MODEL,
                contents=history,
            )
            full_response = response.text

        response_placeholder.markdown(full_response)

    # AI 답변을 대화 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})
