import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# --- 1. ページ設定（絶対に一番最初！） ---
st.set_page_config(page_title="Gal-M@ker", page_icon="🦄", layout="wide")

# --- 2. セッション状態の初期化（記憶領域を作る） ---
if 'theme' not in st.session_state:
    st.session_state.theme = "姫ギャル (Pink)"
if 'generated' not in st.session_state:
    st.session_state.generated = False

# --- 3. APIキー設定 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyCvvv_MEZ1zE6gdjmXrfT589tWWRTyhzvE" # ここに自分のキー（ローカル用）

if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 4. 色定義（辞書） ---
THEMES = {
    "姫ギャル (Pink)": {
        "bg": "#ffeaf4", "dot": "#ffb6c1", "text": "#ff1493",
        "border": "#ff69b4", "btn": "linear-gradient(180deg, #ffb6c1, #ff69b4)", "shadow": "#b0e0e6", "stroke": "white"
    },
    "強めギャル (High)": {
        "bg": "#000000", "dot": "#333333", "text": "#FFD700",
        "border": "#FFD700", "btn": "linear-gradient(180deg, #ffd700, #b8860b)", "shadow": "#ff0000", "stroke": "black"
    },
    "Y2K (Cyber)": {
        "bg": "#e0ffff", "dot": "#00ffff", "text": "#0000ff",
        "border": "#0000ff", "btn": "linear-gradient(180deg, #00ffff, #0000ff)", "shadow": "#ff00ff", "stroke": "#000080"
    },
    "病みかわ (Emo)": {
        "bg": "#1a001a", "dot": "#4b0082", "text": "#e6e6fa",
        "border": "#9370db", "btn": "linear-gradient(180deg, #d8bfd8, #800080)", "shadow": "#000000", "stroke": "black"
    },
    "自由入力": {
        "bg": "#ffffff", "dot": "#cccccc", "text": "#333333",
        "border": "#333333", "btn": "linear-gradient(180deg, #999999, #333333)", "shadow": "#000000", "stroke": "white"
    }
}

# --- 5. UI構築開始 ---

# ★ ここが重要！ラジオボタンの値を即座に反映させるコールバック関数
def update_theme():
    # ラジオボタンが変更されたら、session_stateのthemeも更新される
    pass

# レイアウト分割
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 01. 素材えらび♡")
    
    # ★ ラジオボタン（変更があったらページを即リロードする設定）
    selected_theme = st.radio(
        "今日のバイブスは？🌈",
        list(THEMES.keys()),
        key="theme", # ここでsession_state.themeと紐づける
        on_change=update_theme # 変更時に実行
    )
    
    # 現在のテーマの色を取得
    c = THEMES[st.session_state.theme]

    # ★ ここでCSSを注入（テーマが決まった直後！）
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Mochiy Pop One', sans-serif !important; }}
        
        /* 背景色の強制変更 */
        [data-testid="stAppViewContainer"] {{
            background-color: {c['bg']} !important;
            background-image: radial-gradient({c['dot']} 20%, transparent 20%), radial-gradient({c['dot']} 20%, transparent 20%) !important;
            background-size: 20px 20px !important;
        }}
        
        /* 文字色 */
        h1, h2, h3, p, span, div, label {{ color: {c['text']} !important; }}
        
        /* ボタン */
        .stButton > button {{
            background: {c['btn']} !important;
            color: white !important;
            border: 3px solid #fff !important;
            border-radius: 50px !important;
            box-shadow: 0 5px 10px {c['text']}66 !important;
        }}
        
        /* カスタムボックス */
        .custom-box {{
            border: 4px dotted {c['border']};
            background: rgba(255,255,255,0.7);
            border-radius: 30px; padding: 20px; text-align: center; margin-bottom: 20px;
        }}
        
        h1 {{ text-shadow: 3px 3px 0px #fff, 5px 5px 0px {c['shadow']} !important; }}
    </style>
    """, unsafe_allow_html=True)

    # 自由入力
    custom_text = ""
    if "自由" in st.session_state.theme:
        custom_text = st.text_input("文字入力", "ウチら最強")

    st.markdown("---")
    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        # 実行ボタン
        if st.button("💖 ギャル化スイッチON 💖"):
            st.session_state.generated = True # 処理開始フラグ
            
            # ローディング表示
            with st.spinner(f"⚡️ {st.session_state.theme} 加工中..."):
                # AI処理（エラーハンドリング強化）
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    base_p = "平成ギャル雑誌風のキャッチコピー。10文字以内。"
                    cond = "テンションMAX"
                    if "強め" in st.session_state.theme: cond = "オラオラ系、強気、漢字多め"
                    elif "姫" in st.session_state.theme: cond = "お姫様系、甘々"
                    elif "Y2K" in st.session_state.theme: cond = "デジタル、近未来、英語"
                    elif "病み" in st.session_state.theme: cond = "意味深、ダーク"
                    
                    if "自由" in st.session_state.theme:
                        caption = custom_text if custom_text else "最強"
                    else:
                        res = model.generate_content([f"{base_p} 条件: {cond}", image])
                        caption = res.text.strip()
                except Exception as e:
                    caption = f"Error: {e}" # エラーならそのまま表示

                # 画像処理
                try:
                    # 1. 美肌
                    img = image.convert("RGB")
                    img = ImageEnhance.Brightness(img).enhance(1.1)
                    
                    w, h = img.size
                    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
                    
                    # 2. 背景・スタンプ（簡易版）
                    # rembgなどの重い処理は一旦tryの中でやるが、失敗しても止まらないようにする
                    try:
                        from rembg import remove
                        fg = remove(img).convert("RGBA")
                        # 背景
                        if os.path.exists("assets/bgs"):
                            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
                            if bgs:
                                bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h))
                                canvas.paste(bg, (0,0))
                        canvas.paste(fg, (0,0), fg)
                    except:
                        # 失敗したら元画像を貼る
                        canvas.paste(img.convert("RGBA"), (0,0))

                    # スタンプ
                    if os.path.exists("assets/stamps"):
                        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')]
                        if stamps:
                            for _ in range(4):
                                s = Image.open(f"assets/stamps/{random.choice(stamps)}").convert("RGBA")
                                sz = random.randint(int(w/6), int(w/3))
                                s = s.resize((sz, sz))
                                canvas.paste(s, (random.randint(0, w-sz), random.randint(0, h-sz)), s)

                    # 文字入れ
                    draw = ImageDraw.Draw(canvas)
                    try: font = ImageFont.truetype("gal_font.ttf", int(w/8))
                    except: font = ImageFont.load_default()
                    
                    draw.text((w/10, h/1.4), caption, font=font, fill=c['text'], stroke_width=6, stroke_fill=c['stroke'])
                    
                    st.session_state.final_image = canvas
                    st.session_state.final_caption = caption
                    
                except Exception as e:
                    st.error(f"画像処理エラー: {e}")

# --- 右カラム（結果表示） ---
with col2:
    st.markdown(f"""
    <div class="custom-box">
        <h1>Gal-M@ker</h1>
        <p>{st.session_state.theme} MODE</p>
        <small>API Status: {"✅ OK" if GOOGLE_API_KEY.startswith("AIza") else "❌ NG"}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # 生成済みなら結果を表示
    if st.session_state.generated and 'final_image' in st.session_state:
        st.balloons()
        st.image(st.session_state.final_image, use_container_width=True)
        st.success(f"テーマ: {st.session_state.final_caption}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
