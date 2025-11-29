import streamlit as st
import subprocess
import sys

# ---------------------------------------------------------
# 🚨 긴급 처방: 라이브러리 강제 업데이트
# ---------------------------------------------------------
try:
    import google.generativeai as genai
    import importlib.metadata
    # 현재 설치된 버전 확인
    version = importlib.metadata.version("google-generativeai")
    # 구버전이면 강제 업데이트 실행
    if version < "0.7.2":
        raise ImportError
except ImportError:
    st.warning("⚠️ 최신 AI 기능을 설치 중입니다... 잠시만 기다려주세요 (약 1분)")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai"])
    st.success("설치 완료! 앱이 자동으로 새로고침 됩니다.")
    st.rerun()

# ---------------------------------------------------------
# 1. 설정 및 API 키 연결
# ---------------------------------------------------------
st.set_page_config(page_title="AI 와인 소믈리에", page_icon="🍷")

# 다시 임포트 (업데이트된 버전 적용)
import google.generativeai as genai
from PIL import Image

try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("API 키가 없습니다. Settings -> Secrets에 키를 넣어주세요.")
        st.stop()
except Exception as e:
    st.error(f"설정 오류: {e}")

# 모델 설정
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------
# 2. 분석 로직
# ---------------------------------------------------------
def analyze_wine(image):
    prompt = """
    이 와인 라벨 사진을 분석하여 정보를 한국어로 정리해 주세요.
    가격은 한국의 세금/유통 구조를 고려하여 미국 현지 가격 대비 현실적인 한국 샵 구매가를 추정해 주세요.

    **1. 🍷 기본 정보**
    *   이름 (한글/영어):
    *   빈티지:
    *   생산지/와이너리:
    *   포도 품종:

    **2. 👅 맛과 향**
    *   바디/산도/타닌/당도 (1~5점):
    *   주요 향:
    *   어울리는 음식:

    **3. ⭐ 평점**
    *   주요 평점 (RP, Vivino 등):
    *   평가 요약:

    **4. 💰 가격 비교 (추정)**
    *   🇺🇸 미국 현지 가격 ($):
    *   🇰🇷 한국 와인샵 가격 (₩): (세금/마진 고려 보정치)

    **5. 💡 총평**
    *   구매 가치 및 시음 적기:
    """
    response = model.generate_content([prompt, image])
    return response.text

# ---------------------------------------------------------
# 3. 화면 표시
# ---------------------------------------------------------
st.title("🍷 AI 와인 소믈리에")
st.caption("최신 Gemini 1.5 Flash 모델이 분석합니다.")

img_file = st.camera_input("와인 라벨을 촬영하세요")

if img_file:
    image = Image.open(img_file)
    with st.spinner('🍷 소믈리에가 분석 중입니다...'):
        try:
            result = analyze_wine(image)
            st.divider()
            st.markdown(result)
        except Exception as e:
            st.error(f"분석 실패: {e}")
            st.info("팁: 사진이 너무 어둡거나 흔들리지 않았는지 확인해주세요.")
