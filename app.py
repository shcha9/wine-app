import streamlit as st
import google.generativeai as genai
import importlib.metadata

st.set_page_config(page_title="와인 앱 진단모드", page_icon="🔧")

# ---------------------------------------------------------
# 🕵️ 자가 진단 (여기가 핵심!)
# ---------------------------------------------------------
st.title("🔧 앱 상태 진단")

try:
    # 현재 설치된 라이브러리 버전 확인
    version = importlib.metadata.version("google-generativeai")
    st.metric(label="현재 설치된 AI 버전", value=version)
    
    if version < "0.7.2":
        st.error(f"🚨 버전이 너무 낮습니다! (현재: {version})")
        st.markdown("""
        **[해결 방법]**
        GitHub의 `requirements.txt` 파일 이름이나 내용이 틀렸을 확률이 99%입니다.
        
        1. GitHub 파일명이 **requirements.txt** (s가 있는지, 오타 없는지) 확인하세요.
        2. 파일 내용에 **google-generativeai>=0.7.2** 라고 적혀있는지 확인하세요.
        3. 확인 후 앱을 **Reboot** 하세요.
        """)
    else:
        st.success("✅ 버전은 정상입니다! (0.7.2 이상)")

except Exception as e:
    st.error(f"버전 확인 불가: {e}")

# ---------------------------------------------------------
# 🍷 와인 분석 기능 (버전이 맞을 때만 실행)
# ---------------------------------------------------------
# API 키 설정
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.warning("API 키가 아직 설정되지 않았습니다.")

# 모델 연결 시도
if st.button("테스트 실행 (누르면 분석 시작)"):
    try:
        # 모델 불러오기
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("와인 짧게 한줄 설명")
        st.info(f"테스트 결과: {response.text}")
    except Exception as e:
        st.error(f"⚠️ 여전히 오류 발생: {e}")
        st.markdown("버전이 정상인데도 이 오류가 나면, **API Key를 다시 발급**받아야 할 수도 있습니다.")

img_file = st.camera_input("와인 라벨을 촬영하세요")
if img_file:
    model = genai.GenerativeModel('gemini-1.5-flash')
    with st.spinner('분석 중...'):
        try:
            res = model.generate_content(["이 와인 라벨 정보를 한국어로 알려줘", img_file])
            st.markdown(res.text)
        except Exception as e:
            st.error(str(e))
