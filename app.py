import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# ==========================================
# 👇 APIキー設定
# ==========================================
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyCvvv_MEZ1zE6gdjmXrfT589tWWRTyhzvE"

if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)

# レイアウト設定
st.set_page_config(page_title="Gal-M@ker", page_icon="🦄", layout="wide")

# --- 🔍 重要なデバッグ機能 ---
# 素材がちゃんとあるかチェックして表示する
def check_assets():
    st.sidebar.title("🔧 開発者メニュー")
    
    # 1. フォント
    if os.path.exists("gal_font.ttf"):
        st.sidebar.success("✅ フォント: OK")
    else:
        st.sidebar.error("❌ フォント無し (gal_font.ttf)")

    # 2. スタンプ
    if os.path.exists("assets/stamps"):
        count = len(os.listdir("assets/stamps"))
        st.sidebar.success(f"✅ スタンプ: {count}個")
    else:
        st.sidebar.error("❌ スタンプフォルダ無し (assets/stamps)")

    # 3. 背景
    if os.path.exists("assets/bgs"):
        count = len(os.listdir("assets/bgs"))
        st.sidebar.success(f"✅ 背景画像: {count}個")
    else:
        st.sidebar.error("❌ 背景フォルダ無し (assets/bgs)")

check_assets()

# --- 🚑 エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 🎨 テーマ色定義 ---
def get_theme_colors(theme):
    c = {
        "bg": "#ffeaf4", "dot": "#ffb6c1", "text": "#ff1493",
        "border": "#ff69b4", "btn": "linear-gradient(180deg, #ffb6c1, #ff69b4)",
        "shadow": "#b0e0e6", "stroke": "white"
    }
    
    if "強め" in theme:
        c = {
            "bg": "#000000", "dot": "#333333", "text": "#FFD700",
            "border": "#FFD700", "btn": "linear-gradient(180deg, #ffd700, #b8860b)",
            "shadow": "#ff0000", "stroke": "black"
        }
    elif "Y2K" in theme:
        c = {
            "bg": "#e0ffff", "dot": "#00ffff", "text": "#0000ff",
            "border": "#0000ff", "btn": "linear-gradient(180deg, #00ffff, #0000ff)",
            "shadow": "#ff00ff", "stroke": "#000080"
        }
    elif "病み" in theme:
        c = {
            "bg": "#1a001a", "dot": "#4b0082", "text": "#e6e6fa",
            "border": "#9370db", "btn": "linear-gradient(180deg, #d8bfd8, #800080)",
            "shadow": "#000000", "stroke": "black"
        }
    return c

# --- CSS注入 (強制適用版) ---
def inject_css(theme):
    c = get_theme_colors(theme)
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Mochiy Pop One', sans-serif !important; }}
        
        /* 背景の強制変更 */
        .stApp {{
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
        
        /* タイトル */
        h1 {{ text-shadow: 3px 3px 0px #fff, 5px 5px 0px {c['shadow']} !important; }}
        
        /* コンテナ枠 */
        .custom-box {{
            border: 4px dotted {c['border']};
            background: rgba(255,255,255,0.7);
            border-radius: 30px;
            padding: 20px;
            margin-bottom: 20px;
        }}
    </style>
    """, unsafe_allow_html=True)
    return c

# --- 画像加工 ---
def process_image(image, caption, theme):
    c = get_theme_colors(theme)
    
    # 1. 美肌フィルター
    img = image.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.1)
    
    width, height = img.size
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    
    # 2. 背景合成 (Assetsがある場合のみ)
    bg_drawn = False
    if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
        try:
            fg = remove(img).convert("RGBA")
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs:
                bg_file = random.choice(bgs)
                bg_img = Image.open(f"assets/bgs/{bg_file}").convert("RGBA")
                canvas.paste(bg_img.resize((width, height)), (0,0))
                canvas.paste(fg, (0,0), fg)
                bg_drawn = True
        except:
            pass
    
    if not bg_drawn:
        canvas.paste(img.convert("RGBA"), (0,0))

    # 3. スタンプ合成
    if os.path.exists("assets/stamps"):
        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')]
        if stamps:
            for _ in range(4):
                try:
                    s_file = random.choice(stamps)
                    s_img = Image.open(f"assets/stamps/{s_file}").convert("RGBA")
                    # 切り抜きなしでそのまま貼る（スマホ対策）
                    size = random.randint(int(width/6), int(width/3))
                    s_img = s_img.resize((size, size))
                    x = random.randint(0, width - size)
                    y = random.randint(0, height - size)
                    canvas.paste(s_img, (x, y), s_img)
                except:
                    pass

    # 4. 文字入れ (フォントがなくても描く！)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("gal_font.ttf", int(width/8))
    except:
        # フォントがない場合はデフォルトを使う
        font = ImageFont.load_default()
        # デフォルトフォントは小さいので、描画位置などを調整しないといけないが
        # とりあえずエラー回避優先
    
    # 文字の縁取りと本体
    text_x = width / 10
    text_y = height / 1.3
    
    # 縁取りを描く（太く！）
    stroke_width = 5
    draw.text((text_x, text_y), caption, font=font, fill=c['stroke'], stroke_width=stroke_width, stroke_fill=c['stroke'])
    # 本体を描く
    draw.text((text_x, text_y), caption, font=font, fill=c['text'])

    return canvas

def get_ai_caption(img, theme, custom):
    if "自由" in theme: return custom if custom else "最強卍"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"平成ギャル語の短いキャッチコピー。テーマ:{theme}。10文字以内。"
        res = model.generate_content([prompt, img])
        return res.text.strip()
    except:
        return "最強KAWAII宣言💖"

# ================= UI =================

# セッション管理
if 'theme' not in st.session_state:
    st.session_state['theme'] = "姫ギャル (Pink)"

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 01. 素材えらび♡")
    
    # ラジオボタン
    new_theme = st.radio(
        "今日のバイブスは？🌈",
        ["姫ギャル (Pink)", "強めギャル (High)", "Y2K (Cyber)", "病みかわ (Emo)", "自由入力"],
        key="theme_selector"
    )
    
    # 変更検知 -> リロード
    if new_theme != st.session_state['theme']:
        st.session_state['theme'] = new_theme
        st.rerun()

    # CSS注入
    c = inject_css(st.session_state['theme'])

    custom_text = ""
    if "自由" in st.session_state['theme']:
        custom_text = st.text_input("文字入力", "ウチら最強")

    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        if st.button("💖 ギャル化スイッチON 💖"):
            with st.spinner("AIが盛ってる最中...🦄"):
                caption = get_ai_caption(image, st.session_state['theme'], custom_text)
                res_img = process_image(image, caption, st.session_state['theme'])
                st.session_state['result'] = res_img
                st.session_state['caption'] = caption

with col2:
    st.markdown(f"""
    <div class="custom-box">
        <h1>Gal-M@ker</h1>
        <p>{st.session_state['theme']} MODE</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'result' in st.session_state:
        st.balloons()
        st.image(st.session_state['result'], use_container_width=True)
        st.success(f"テーマ: {st.session_state['caption']}")
    else:
        st.info("👈 左側で画像を選んでね！")
