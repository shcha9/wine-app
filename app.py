import streamlit as st
import google.generativeai as genai
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="AI 와인 소믈리에", page_icon="🍷")

# 제목
st.title("🍷 AI 와인 소믈리에")
st.markdown("와인 라벨을 찍으면 **맛, 평점, 한-미 가격**을 분석해 드립니다.")

# API 키 설정 (Streamlit Secrets에서 가져옴)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("API 키가 설정되지 않았습니다. 설정 메뉴에서 키를 입력해주세요.")
        st.stop()
except Exception as e:
    st.error(f"설정 오류: {e}")

model = genai.GenerativeModel('gemini-1.5-flash')

# 분석 함수
def analyze_wine(image):
    prompt = """
    이 와인 라벨 사진을 분석하여 다음 정보를 한국어로 정리해 주세요.
    가격은 한국의 세금/유통 구조를 고려하여 미국 현지 가격 대비 현실적인 한국 샵 구매가를 추정해 주세요.

    **1. 🍷 기본 정보**
    *   이름 (한글/영어):
    *   빈티지:
    *   생산지 및 와이너리:
    *   포도 품종:

    **2. 👅 맛과 향 (테이스팅 노트)**
    *   바디 / 산도 / 타닌 / 당도 (1~5점):
    *   주요 향 (아로마):
    *   어울리는 음식:

    **3. ⭐ 평점 및 평가**
    *   주요 평점 (Robert Parker, Vivino 등):
    *   전문가 평가 요약:

    **4. 💰 가격 비교 (추정)**
    *   🇺🇸 미국 현지 가격 ($):
    *   🇰🇷 한국 와인샵 가격 (₩): (세금 고려 1.5~2배 보정치)

    **5. 💡 한줄 총평**
    *   구매 가치 및 시음 적기:
    """
    response = model.generate_content([prompt, image])
    return response.text

# 카메라 입력
img_file = st.camera_input("와인 라벨을 촬영하세요")

if img_file:
    image = Image.open(img_file)
    with st.spinner('🍷 소믈리에가 분석 중입니다...'):
        try:
            result = analyze_wine(image)
            st.divider()
            st.markdown(result)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
