import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
st.set_page_config(page_title="AI 와인 소믈리에", page_icon="🍷")
st.title("🍷 AI 와인 소믈리에")

# API 키 연결
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("API 키가 없습니다. Settings에서 키를 설정해주세요.")
        st.stop()
except Exception as e:
    st.error(f"설정 오류: {e}")

# ---------------------------------------------------------
# 2. 모델 자동 검색 및 선택 (핵심 기능!)
# ---------------------------------------------------------
@st.cache_resource
def get_available_models():
    """사용 가능한 모델 목록을 가져옵니다."""
    models = []
    try:
        for m in genai.list_models():
            # 이미지를 볼 수 있는(generateContent) 모델만 골라냅니다
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
    except Exception as e:
        st.error(f"모델 목록을 가져오는데 실패했습니다: {e}")
    return models

# 모델 목록 가져오기
available_models = get_available_models()

# 만약 목록이 비어있으면 기본값 사용
if not available_models:
    available_models = ["models/gemini-1.5-flash", "models/gemini-pro-vision"]

# ⭐ 사용자에게 모델을 선택하게 함 (사이드바)
st.sidebar.header("⚙️ 설정")
selected_model_name = st.sidebar.selectbox(
    "사용할 AI 모델 선택:",
    available_models,
    index=0  # 첫 번째 모델을 기본으로 선택
)

st.sidebar.info(f"선택된 모델: `{selected_model_name}`")

# ---------------------------------------------------------
# 3. 분석 로직
# ---------------------------------------------------------
def analyze_wine(image, model_name):
    model = genai.GenerativeModel(model_name)
    
    prompt = """
    이 와인 라벨 사진을 분석하여 다음 정보를 한국어로 정리해 주세요.
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
# 4. 메인 화면
# ---------------------------------------------------------
img_file = st.camera_input("와인 라벨을 촬영하세요")

if img_file:
    image = Image.open(img_file)
    with st.spinner(f'🍷 {selected_model_name} 모델이 분석 중입니다...'):
        try:
            result = analyze_wine(image, selected_model_name)
            st.divider()
            st.markdown(result)
        except Exception as e:
            st.error("분석 실패!")
            st.error(f"오류 내용: {e}")
            st.warning("👈 왼쪽 사이드바에서 다른 모델을 선택해서 다시 시도해보세요.")
