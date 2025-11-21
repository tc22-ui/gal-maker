import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# --- 1. 設定 ---
st.set_page_config(page_title="Gal-M@ker", page_icon="🦄", layout="wide")

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyCvvv_MEZ1zE6gdjmXrfT589tWWRTyhzvE"

if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. 色定義（ここを確実に渡す！） ---
THEMES = {
    "姫ギャル (Pink)": {
        "bg": "#ffeaf4", "dot": "#ffb6c1", "text": "#ff1493",
        "border": "#ff69b4", "btn": "linear-gradient(180deg, #ffb6c1, #ff69b4)",
        "shadow": "#b0e0e6", "stroke": "white", # 画像用：文字色ピンク、フチ白
        "img_text": "#ff1493", "img_stroke": "white"
    },
    "強めギャル (High)": {
        "bg": "#000000", "dot": "#333333", "text": "#FFD700",
        "border": "#FFD700", "btn": "linear-gradient(180deg, #ffd700, #b8860b)",
        "shadow": "#ff0000",
        "img_text": "#FFD700", "img_stroke": "black" # 画像用：文字色ゴールド、フチ黒
    },
    "Y2K (Cyber)": {
        "bg": "#e0ffff", "dot": "#00ffff", "text": "#0000ff",
        "border": "#0000ff", "btn": "linear-gradient(180deg, #00ffff, #0000ff)",
        "shadow": "#ff00ff",
        "img_text": "#00FFFF", "img_stroke": "#000080" # 画像用：文字色シアン、フチ紺
    },
    "病みかわ (Emo)": {
        "bg": "#1a001a", "dot": "#4b0082", "text": "#e6e6fa",
        "border": "#9370db", "btn": "linear-gradient(180deg, #d8bfd8, #800080)",
        "shadow": "#000000",
        "img_text": "#E6E6FA", "img_stroke": "black" # 画像用：文字色薄紫、フチ黒
    },
    "自由入力": {
        "bg": "#ffffff", "dot": "#cccccc", "text": "#333333",
        "border": "#333333", "btn": "linear-gradient(180deg, #999999, #333333)",
        "shadow": "#000000",
        "img_text": "#FF00FF", "img_stroke": "white"
    }
}

# --- 3. 画像加工職人（色を引数で受け取る！） ---
def process_image(image, caption, color_settings):
    # 1. 美肌
    img = image.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.1)
    
    w, h = img.size
    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    
    # 2. 背景合成（簡易）
    try:
        from rembg import remove
        fg = remove(img).convert("RGBA")
        # 背景画像があれば使う
        if os.path.exists("assets/bgs"):
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs:
                bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h))
                canvas.paste(bg, (0,0))
        canvas.paste(fg, (0,0), fg)
    except:
        canvas.paste(img.convert("RGBA"), (0,0))

    # 3. スタンプ
    if os.path.exists("assets/stamps"):
        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')]
        if stamps:
            for _ in range(4):
                try:
                    s = Image.open(f"assets/stamps/{random.choice(stamps)}").convert("RGBA")
                    sz = random.randint(int(w/6), int(w/3))
                    canvas.paste(s.resize((sz, sz)), (random.randint(0, w-sz), random.randint(0, h-sz)), s.resize((sz, sz)))
                except: pass

    # 4. 文字入れ（★ここで渡された色を使う！）
    draw = ImageDraw.Draw(canvas)
    try: font = ImageFont.truetype("gal_font.ttf", int(w/8))
    except: font = ImageFont.load_default()
    
    # 受け取った設定から色を取り出す
    fill_color = color_settings['img_text']
    stroke_color = color_settings['img_stroke']
    
    draw.text((w/10, h/1.4), caption, font=font, fill=fill_color, stroke_width=6, stroke_fill=stroke_color)
    return canvas

# --- 4. AI職人（予備の言葉を増やす） ---
def get_ai_text(img, theme, custom):
    if "自由" in theme: return custom if custom else "最強卍"
    
    # エラー時の予備ワードリスト（ランダムで返す）
    fallback_words = ["最強KAWAII💖", "マジ神✨", "盛れたwww", "尊い...†", "優勝🏆", "レベチ🔥"]
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"平成ギャル雑誌風のキャッチコピー。テーマ:{theme}。10文字以内。絵文字1つまで。"
        res = model.generate_content([prompt, img])
        return res.text.strip()
    except:
        return random.choice(fallback_words)

# --- 5. UIメイン ---
if 'theme' not in st.session_state:
    st.session_state.theme = "姫ギャル (Pink)"

# サイドバーでデバッグ情報
st.sidebar.write(f"現在のテーマ: {st.session_state.theme}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 01. 素材えらび♡")
    
    # ラジオボタン変更時にリロード
    def on_theme_change():
        # 変更後の値をsession_stateに確実に入れる
        pass

    new_theme = st.radio(
        "今日のバイブスは？🌈",
        list(THEMES.keys()),
        key="theme_radio",
    )
    
    # 強制リロードロジック
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    # 色を取得
    c = THEMES[st.session_state.theme]

    # CSS注入
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Mochiy Pop One', sans-serif !important; }}
        [data-testid="stAppViewContainer"] {{
            background-color: {c['bg']} !important;
            background-image: radial-gradient({c['dot']} 20%, transparent 20%), radial-gradient({c['dot']} 20%, transparent 20%) !important;
            background-size: 20px 20px !important;
        }}
        h1, h2, h3, p, div, label, span {{ color: {c['text']} !important; }}
        .stButton>button {{
            background: {c['btn']} !important; color: white !important; border: 3px solid #fff !important;
            border-radius: 50px !important; box-shadow: 0 5px 10px {c['text']}66 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    custom_text = ""
    if "自由" in st.session_state.theme:
        custom_text = st.text_input("文字入力", "ウチら最強")

    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        if st.button("💖 ギャル化スイッチON 💖"):
            with st.spinner(f"⚡️ {st.session_state.theme} 加工中..."):
                # AIテキスト生成
                caption = get_ai_text(image, st.session_state.theme, custom_text)
                
                # ★ここで「現在選択中のテーマの色設定(c)」を直接渡す！
                res_img = process_image(image, caption, c)
                
                st.session_state.final_img = res_img
                st.session_state.final_cap = caption

with col2:
    st.markdown(f"""
    <div style="border: 4px dotted {c['border']}; background: rgba(255,255,255,0.7); border-radius: 30px; padding: 20px; text-align: center; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 3rem; text-shadow: 3px 3px 0 #fff, 5px 5px 0 {c['shadow']};">Gal-M@ker</h1>
        <p>{st.session_state.theme} MODE</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'final_img' in st.session_state:
        st.balloons()
        st.image(st.session_state.final_img, use_container_width=True)
        st.success(f"テーマ: {st.session_state.final_cap}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
