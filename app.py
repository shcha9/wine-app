import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------------------------------------------------------
# 1. 앱 디자인 및 설정 (커스텀 CSS)
# ---------------------------------------------------------
st.set_page_config(page_title="VINO AI", page_icon="🍷", layout="centered")

# 깔끔한 UI를 위한 CSS 주입
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa; 
    }
    h1 {
        color: #722F37; /* 와인색 */
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #722F37;
        color: white;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #722F37;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. API 및 모델 설정
# ---------------------------------------------------------
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("API 키 설정이 필요합니다.")
        st.stop()
except Exception as e:
    st.error(f"시스템 오류: {e}")

# ⭐ 요청하신 Pro 모델 설정 (가장 똑똑한 모델)
# 만약 2.5 버전이 있다면 'gemini-2.5-pro'로 수정하시면 됩니다.
model_name = "gemini-2.5-pro" 
model = genai.GenerativeModel(model_name)

# ---------------------------------------------------------
# 3. AI 분석 로직 (구조화된 데이터 요청)
# ---------------------------------------------------------
def analyze_wine_pro(image):
    prompt = """
    당신은 20년 경력의 마스터 소믈리에입니다. 
    이 와인 라벨을 분석하여 앱 사용자에게 보여줄 정보를 작성해주세요.
    
    반드시 아래 형식을 지켜주세요.
    
    [정보]
    이름: (와인 이름 한글)
    영문: (와인 이름 영어)
    생산지: (국가 > 지역)
    품종: (포도 품종)
    빈티지: (연도)
    
    [점수]
    평점: (90~100점 사이 점수, Vivino/RP 데이터 기반 추정)
    
    [맛]
    바디: (1~5 숫자만)
    타닌: (1~5 숫자만)
    산도: (1~5 숫자만)
    당도: (1~5 숫자만)
    
    [가격]
    미국: (숫자만, 달러)
    한국: (숫자만, 원화, 미국가 대비 1.8배 내외 세금보정)
    
    [리뷰]
    (이 와인의 특징, 맛의 뉘앙스, 페어링 추천을 3문장으로 요약하여 매력적으로 작성)
    """
    
    response = model.generate_content([prompt, image])
    return response.text

# ---------------------------------------------------------
# 4. 데이터 파싱 (텍스트를 예쁜 UI로 만들기 위한 가공)
# ---------------------------------------------------------
def parse_result(text):
    # AI 응답에서 필요한 정보를 추출하는 간단한 파서
    data = {"맛": {}}
    try:
        lines = text.split('\n')
        for line in lines:
            if "이름:" in line: data['이름'] = line.split(":")[1].strip()
            if "영문:" in line: data['영문'] = line.split(":")[1].strip()
            if "생산지:" in line: data['생산지'] = line.split(":")[1].strip()
            if "품종:" in line: data['품종'] = line.split(":")[1].strip()
            if "빈티지:" in line: data['빈티지'] = line.split(":")[1].strip()
            if "평점:" in line: data['평점'] = line.split(":")[1].strip().replace("점","")
            if "미국:" in line: data['미국'] = line.split(":")[1].strip()
            if "한국:" in line: data['한국'] = line.split(":")[1].strip()
            
            # 맛 그래프용 데이터
            if "바디:" in line: data['맛']['바디'] = int(line.split(":")[1].strip())
            if "타닌:" in line: data['맛']['타닌'] = int(line.split(":")[1].strip())
            if "산도:" in line: data['맛']['산도'] = int(line.split(":")[1].strip())
            if "당도:" in line: data['맛']['당도'] = int(line.split(":")[1].strip())
            
        # 리뷰는 텍스트 덩어리로
        if "[리뷰]" in text:
            data['리뷰'] = text.split("[리뷰]")[1].strip()
        else:
            data['리뷰'] = text # 파싱 실패시 전체 출력
            
    except:
        data['리뷰'] = text # 에러나면 그냥 통으로 보여줌
    return data

# ---------------------------------------------------------
# 5. 메인 UI 화면
# ---------------------------------------------------------
st.title("VINO AI")
st.markdown("### 📸 프리미엄 와인 분석")
st.caption(f"Powered by Google {model_name}")

# 카메라 영역
img_file = st.camera_input("라벨을 스캔하세요", label_visibility="collapsed")

if img_file:
    image = Image.open(img_file)
    
    # 로딩 애니메이션
    with st.spinner('🍷 소믈리에가 테이스팅 중입니다...'):
        try:
            # 1. AI 분석 실행
            raw_text = analyze_wine_pro(image)
            # 2. 결과 가공
            info = parse_result(raw_text)
            
            st.divider()
            
            # --- 결과 화면 시작 ---
            
            # 1. 헤더 (이름 및 국기)
            if '이름' in info:
                st.header(info['이름'])
                st.markdown(f"**{info.get('영문', '')}**")
                st.markdown(f"📍 {info.get('생산지', '')} | 🍇 {info.get('품종', '')} | 📅 {info.get('빈티지', '')}")
            else:
                st.markdown(raw_text) # 파싱 실패 시 원본 출력

            st.divider()

            # 2. 핵심 요약 (탭 구성)
            tab1, tab2, tab3 = st.tabs(["🏆 평점/가격", "👅 맛 그래프", "📝 테이스팅 노트"])

            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("예상 평점", f"{info.get('평점', 'N/A')}점", "Expert")
                with col2:
                    st.metric("한국 추정가", f"{info.get('한국', 'N/A')}")
                with col3:
                    st.metric("미국 현지가", f"${info.get('미국', 'N/A')}")
                
                st.caption("※ 가격은 세금 및 유통 마진이 포함된 추정치입니다.")

            with tab2:
                # 맛 데이터 시각화 (슬라이더로 표현)
                if info['맛']:
                    st.write("🍷 **Taste Profile**")
                    st.slider("바디감 (Body)", 1, 5, info['맛'].get('바디', 3), disabled=True)
                    st.slider("타닌 (Tannin)", 1, 5, info['맛'].get('타닌', 3), disabled=True)
                    st.slider("산도 (Acidity)", 1, 5, info['맛'].get('산도', 3), disabled=True)
                    st.slider("당도 (Sweetness)", 1, 5, info['맛'].get('당도', 1), disabled=True)
                else:
                    st.info("맛 정보를 분석하지 못했습니다.")

            with tab3:
                st.info(info.get('리뷰', raw_text))

        except Exception as e:
            st.error("죄송합니다. 분석 중 오류가 발생했습니다.")
            st.error(f"오류 코드: {e}")

else:
    # 대기 화면 꾸미기
    st.info("카메라 버튼을 눌러 와인 라벨을 찍어주세요.")
