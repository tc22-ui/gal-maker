import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# --- 1. 設定 ---
st.set_page_config(page_title="Gal-M@ker", page_icon="🌺", layout="wide")

# --- 2. APIキー ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIza..."

if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 3. エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 4. テーマ定義 (デザイン・言葉) ---
THEME_CONFIG = {
    "姫ギャル (Pink)": {
        "colors": {"bg_base": "#fff0f5", "dot": "#ff69b4", "text": "#ff1493", "border": "#ff69b4", "shadow": "#ffb6c1"},
        "words": ["てんち降臨👼", "優勝した💖", "すきぴ尊い", "あまあま🍬", "ぷりてぃ✨"],
        "loading": ["リボン結び中...", "王子様待ち...", "魔法かけてる...", "キラキラ注入✨"]
    },
    "強めギャル (High)": {
        "colors": {"bg_base": "#000000", "dot": "#333333", "text": "#FFD700", "border": "#FFD700", "shadow": "#FF0000"},
        "words": ["ウチら最強卍", "喧嘩上等🔥", "マブダチ🤝", "治安悪め😎", "レベチ👑"],
        "loading": ["気合い入れ中🔥", "盛れるまで帰らん", "治安悪化中...", "最強バイブス⚡️"]
    },
    "Y2K (Cyber)": {
        "colors": {"bg_base": "#e0ffff", "dot": "#0000ff", "text": "#0000ff", "border": "#0000ff", "shadow": "#00ffff"},
        "words": ["System OK", "Link Start", "Cyber Angel", "Digital Love", "No Data"],
        "loading": ["Downloading...", "Connect Server...", "Hacking...", "System Boot..."]
    },
    "病みかわ (Emo)": {
        "colors": {"bg_base": "#1a001a", "dot": "#800080", "text": "#e6e6fa", "border": "#9370db", "shadow": "#000000"},
        "words": ["永遠...", "愛して†", "救済求ム", "バグり中", "ぴえん🥺"],
        "loading": ["現実逃避中...", "薬飲んだ...", "通信エラー...", "闇の儀式†"]
    },
    "自由入力": {
        "colors": {"bg_base": "#ffffff", "dot": "#cccccc", "text": "#333333", "border": "#333333", "shadow": "#000000"},
        "words": ["最強卍"],
        "loading": ["Now Loading...", "Please Wait...", "Processing...", "Almost Done..."]
    }
}

# --- 5. CSS注入 (デザインの魂) ---
def inject_css(theme):
    c = THEME_CONFIG[theme]["colors"]
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Mochiy Pop One', sans-serif !important; }}
        
        /* 背景: ドット柄にして動かす */
        [data-testid="stAppViewContainer"] {{
            background-color: {c['bg_base']} !important;
            background-image: radial-gradient({c['dot']} 20%, transparent 20%), radial-gradient({c['dot']} 20%, transparent 20%) !important;
            background-size: 20px 20px !important;
            background-position: 0 0, 10px 10px !important;
        }}
        
        /* 文字色 */
        h1, h2, h3, p, div, label, span {{ color: {c['text']} !important; }}
        
        /* タイトル装飾 */
        h1 {{
            text-shadow: 3px 3px 0px #fff, 5px 5px 0px {c['shadow']} !important;
            transform: rotate(-2deg);
        }}
        
        /* ボタン: ゼリーみたいな質感 */
        .stButton > button {{
            background: linear-gradient(180deg, rgba(255,255,255,0.4), rgba(0,0,0,0.1)) !important;
            background-color: {c['border']} !important;
            color: white !important;
            border: 3px solid #fff !important;
            border-radius: 50px !important;
            box-shadow: 0 5px 15px {c['shadow']} !important;
            font-size: 1.2rem !important;
            transition: transform 0.1s;
        }}
        .stButton > button:active {{ transform: scale(0.95); }}

        /* コンテナ枠 */
        .custom-box {{
            border: 4px dotted {c['border']};
            background: rgba(255,255,255,0.8);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 5px 5px 0px {c['shadow']};
        }}
        
        /* 画面上部のマーキー（流れる文字） */
        .marquee-container {{
            position: fixed; top: 0; left: 0; width: 100%; background: {c['text']}; color: white;
            z-index: 9999; overflow: hidden; white-space: nowrap; padding: 5px 0; font-size: 14px;
        }}
        .marquee-content {{ display: inline-block; animation: marquee 15s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        
        /* 固定デコパーツ */
        .deco-tl {{ position: fixed; top: 50px; left: 10px; font-size: 40px; z-index: 1; animation: float 3s infinite; }}
        .deco-tr {{ position: fixed; top: 50px; right: 10px; font-size: 40px; z-index: 1; animation: float 3s infinite reverse; }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
        
        /* ローディングオーバーレイ (ゲーミング発光) */
        @keyframes rainbow {{
            0% {{ background-color: #ff9a9e; }} 25% {{ background-color: #fad0c4; }}
            50% {{ background-color: #ffd1ff; }} 75% {{ background-color: #a18cd1; }}
            100% {{ background-color: #ff9a9e; }}
        }}
        .gal-loading {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 999999;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            animation: rainbow 2s linear infinite;
        }}
        .gal-loading-text {{
            font-size: 3rem; font-weight: 900; color: white;
            text-shadow: 4px 4px 0 #000;
            animation: shake 0.5s infinite;
        }}
        @keyframes shake {{ 0% {{ transform: rotate(0deg); }} 25% {{ transform: rotate(5deg); }} 75% {{ transform: rotate(-5deg); }} 100% {{ transform: rotate(0deg); }} }}

    </style>
    """, unsafe_allow_html=True)
    
    # マーキーを表示
    st.markdown(f"""
    <div class="marquee-container">
        <div class="marquee-content">
            Welcome to Gal-M@ker ... Powered by Love Loop Inc ... HEISEI RETRO STYLE ... Make it KAWAII ... {theme} MODE ... 🌺🦋💖
        </div>
    </div>
    <div class="deco-tl">🌺</div>
    <div class="deco-tr">🦋</div>
    """, unsafe_allow_html=True)

# --- 6. AI ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由" in theme_mode: return custom_text if custom_text else "最強卍"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        base = "平成ギャル雑誌風のキャッチコピー。10文字以内。"
        cond = "テンションMAX"
        if "強め" in theme_mode: cond = "オラオラ系"
        elif "姫" in theme_mode: cond = "お姫様系"
        elif "Y2K" in theme_mode: cond = "デジタル"
        elif "病み" in theme_mode: cond = "意味深"
        
        response = model.generate_content([f"{base} 条件: {cond}", image])
        return response.text.strip()
    except Exception as e:
        st.sidebar.error(f"AI Error: {e}")
        return random.choice(THEME_CONFIG[theme_mode]["words"])

# --- 7. 画像加工 ---
def process_image(image, caption, theme_mode):
    c = THEME_CONFIG[theme_mode]["colors"]
    img = image.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.15) # 美白
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
    
    # 文字色（テーマ依存）
    tc = c['text']; sc = c['bg_base'] # 縁取りは背景色にすると馴染む
    if "強め" in theme_mode: tc="#FFD700"; sc="black"
    elif "Y2K" in theme_mode: tc="#00FFFF"; sc="#000080"
    
    draw.text((w/10, h/1.4), caption, font=font, fill=tc, stroke_width=6, stroke_fill=sc)
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

    inject_css(st.session_state.theme)
    
    custom_text = ""
    if "自由" in st.session_state.theme: custom_text = st.text_input("文字入力", "ウチら最強")

    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        if st.button("💖 ギャル化スイッチON 💖"):
            # ★ここが新しい！「動くローディング画面」★
            loading_ph = st.empty()
            loading_messages = THEME_CONFIG[st.session_state.theme]["loading"]
            
            # 3回メッセージを変える演出（ワクワク感！）
            for msg in loading_messages[:3]:
                loading_ph.markdown(f"""
                <div class="gal-loading">
                    <div class="gal-loading-text">{msg}</div>
                    <div style="font-size:20px; color:white; margin-top:10px;">Wait a sec...</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.8) # 0.8秒ごとに切り替え
            
            # 処理実行
            caption = get_gal_caption(image, st.session_state.theme, custom_text)
            res = process_image(image, caption, st.session_state.theme)
            
            loading_ph.empty() # 演出終了
            st.session_state.final = res
            st.session_state.cap = caption

with col2:
    c = THEME_CONFIG[st.session_state.theme]["colors"]
    st.markdown(f"""
    <div class="custom-box">
        <h1 style="margin:0;font-size:3rem;">Gal-M@ker</h1>
        <p>{st.session_state.theme} MODE</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'final' in st.session_state:
        st.balloons()
        st.image(st.session_state.final, use_container_width=True)
        st.success(f"テーマ: {st.session_state.cap}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
