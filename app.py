import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# --- 1. 設定 ---
st.set_page_config(page_title="Gal-M@ker", page_icon="🦄", layout="wide")

# --- 2. APIキー ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIza..." # ローカル用

if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 3. エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 4. テーマごとの設定（色＆予備の言葉） ---
THEME_CONFIG = {
    "姫ギャル (Pink)": {
        "colors": {"bg": "#ffeaf4", "dot": "#ffb6c1", "text": "#ff1493", "border": "#ff69b4", "btn": "linear-gradient(180deg, #ffb6c1, #ff69b4)", "shadow": "#b0e0e6", "img_text": "#ff1493", "img_stroke": "white"},
        "words": ["てんち降臨👼", "優勝した💖", "すきぴ尊い", "あまあま🍬", "ぷりてぃ✨"]
    },
    "強めギャル (High)": {
        "colors": {"bg": "#000000", "dot": "#333333", "text": "#FFD700", "border": "#FFD700", "btn": "linear-gradient(180deg, #ffd700, #b8860b)", "shadow": "#ff0000", "img_text": "#FFD700", "img_stroke": "black"},
        "words": ["ウチら最強卍", "喧嘩上等🔥", "マブダチ🤝", "治安悪め😎", "レベチ👑"]
    },
    "Y2K (Cyber)": {
        "colors": {"bg": "#e0ffff", "dot": "#00ffff", "text": "#0000ff", "border": "#0000ff", "btn": "linear-gradient(180deg, #00ffff, #0000ff)", "shadow": "#ff00ff", "img_text": "#00FFFF", "img_stroke": "#000080"},
        "words": ["System OK", "Link Start", "Cyber Angel", "Digital Love", "No Data"]
    },
    "病みかわ (Emo)": {
        "colors": {"bg": "#1a001a", "dot": "#4b0082", "text": "#e6e6fa", "border": "#9370db", "btn": "linear-gradient(180deg, #d8bfd8, #800080)", "shadow": "#000000", "img_text": "#E6E6FA", "img_stroke": "black"},
        "words": ["永遠...", "愛して†", "救済求ム", "バグり中", "ぴえん🥺"]
    },
    "自由入力": {
        "colors": {"bg": "#ffffff", "dot": "#cccccc", "text": "#333333", "border": "#333333", "btn": "linear-gradient(180deg, #999999, #333333)", "shadow": "#000000", "img_text": "#FF00FF", "img_stroke": "white"},
        "words": ["最強卍"]
    }
}

# --- 5. CSS注入 ---
def inject_css(theme):
    c = THEME_CONFIG[theme]["colors"]
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Mochiy Pop One', sans-serif !important; }}
        [data-testid="stAppViewContainer"] {{ background-color: {c['bg']} !important; background-image: radial-gradient({c['dot']} 20%, transparent 20%), radial-gradient({c['dot']} 20%, transparent 20%) !important; background-size: 20px 20px !important; }}
        h1, h2, h3, p, span, div, label {{ color: {c['text']} !important; }}
        .stButton > button {{ background: {c['btn']} !important; color: white !important; border: 3px solid #fff !important; border-radius: 50px !important; box-shadow: 0 5px 10px {c['text']}66 !important; }}
        h1 {{ text-shadow: 3px 3px 0px #fff, 5px 5px 0px {c['shadow']} !important; }}
        .custom-box {{ border: 4px dotted {c['border']}; background: rgba(255,255,255,0.7); border-radius: 30px; padding: 20px; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)
    return c

# --- 6. AI (賢い予備機能付き) ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由" in theme_mode: return custom_text if custom_text else "最強卍"

    try:
        # 安定版のgemini-proを優先で試す
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"平成ギャル雑誌風のキャッチコピー。テーマ:{theme_mode}。10文字以内。絵文字は1つまで。"
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        if text: return text
    except Exception as e:
        # エラーが起きたら、サイドバーにこっそり表示（デバッグ用）
        st.sidebar.error(f"AI Error Log: {e}")
    
    # ★ここが新機能！AIがダメでも、テーマに合った言葉を選ぶ！
    fallback_list = THEME_CONFIG[theme_mode]["words"]
    return random.choice(fallback_list)

# --- 7. 画像加工 ---
def process_image(image, caption, theme_mode):
    c = THEME_CONFIG[theme_mode]["colors"]
    img = image.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.1)
    w, h = img.size
    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    
    try:
        if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
            fg = remove(img).convert("RGBA")
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs:
                bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h))
                canvas.paste(bg, (0,0))
            canvas.paste(fg, (0,0), fg)
        else: canvas.paste(img.convert("RGBA"), (0,0))
    except: canvas.paste(img.convert("RGBA"), (0,0))

    if os.path.exists("assets/stamps"):
        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')]
        if stamps:
            for _ in range(4):
                try:
                    s = Image.open(f"assets/stamps/{random.choice(stamps)}").convert("RGBA")
                    sz = random.randint(int(w/6), int(w/3))
                    canvas.paste(s.resize((sz, sz)), (random.randint(0, w-sz), random.randint(0, h-sz)), s.resize((sz, sz)))
                except: pass

    draw = ImageDraw.Draw(canvas)
    try: font = ImageFont.truetype("gal_font.ttf", int(w/7))
    except: font = ImageFont.load_default()
    
    draw.text((w/10, h/1.4), caption, font=font, fill=c['img_text'], stroke_width=6, stroke_fill=c['img_stroke'])
    return canvas

# --- UI ---
if 'theme' not in st.session_state: st.session_state.theme = "姫ギャル (Pink)"

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 01. 素材えらび♡")
    new_theme = st.radio("今日のバイブスは？🌈", list(THEME_CONFIG.keys()), key="rad")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    c = inject_css(st.session_state.theme)
    
    custom_text = ""
    if "自由" in st.session_state.theme: custom_text = st.text_input("文字入力", "ウチら最強")

    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        if st.button("💖 ギャル化スイッチON 💖"):
            with st.spinner("AIが考え中..."):
                caption = get_gal_caption(image, st.session_state.theme, custom_text)
                res = process_image(image, caption, st.session_state.theme)
                st.session_state.final = res
                st.session_state.cap = caption

with col2:
    c = THEME_CONFIG[st.session_state.theme]["colors"]
    st.markdown(f"""<div class="custom-box"><h1 style="margin:0;font-size:3rem;text-shadow:3px 3px 0 #fff,5px 5px 0 {c['shadow']};">Gal-M@ker</h1><p>{st.session_state.theme} MODE</p></div>""", unsafe_allow_html=True)
    if 'final' in st.session_state:
        st.balloons()
        st.image(st.session_state.final, use_container_width=True)
        st.success(f"テーマ: {st.session_state.cap}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
