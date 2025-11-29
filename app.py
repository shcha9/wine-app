import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="모델 점검", page_icon="🔍")
st.title("🔍 내 API 키로 쓸 수 있는 모델 찾기")

# 1. API 키 설정
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        st.success("✅ API 키가 감지되었습니다.")
    else:
        st.error("API 키가 없습니다.")
        st.stop()
except Exception as e:
    st.error(f"설정 오류: {e}")

# 2. 모델 리스트 조회 (여기가 핵심!)
st.markdown("### 📋 사용 가능한 모델 목록")

if st.button("모델 리스트 조회하기"):
    try:
        found_flash = False
        # 구글 서버에 "나 뭐 쓸 수 있어?" 하고 물어보는 명령어
        for m in genai.list_models():
            st.write(f"- `{m.name}`")
            if 'gemini-1.5-flash' in m.name:
                found_flash = True
        
        st.divider()
        if found_flash:
            st.success("🎉 `gemini-1.5-flash`가 목록에 있습니다! 코드가 잘못된 거였습니다.")
        else:
            st.error("🚨 목록에 `gemini-1.5-flash`가 없습니다!")
            st.markdown("""
            **[해결 방법]**
            이 API 키는 구형 프로젝트나, 권한이 제한된 클라우드 프로젝트에서 만들어진 것 같습니다.
            
            1. **[Google AI Studio](https://aistudio.google.com/app/apikey)** 에 접속하세요.
            2. **Create API key**를 누르세요.
            3. 중요: **Create API key in new project (새 프로젝트에서 만들기)** 를 선택하세요.
            4. 그 새 키를 Streamlit Secrets에 다시 등록하세요.
            """)
            
    except Exception as e:
        st.error(f"목록 조회 실패: {e}")
        st.markdown("API 키 자체가 잘못되었거나, Google Cloud 결제/권한 설정 문제일 수 있습니다.")
