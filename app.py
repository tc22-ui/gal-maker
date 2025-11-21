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

st.set_page_config(page_title="Gal-M@ker Pure", page_icon="🦄", layout="wide")

# --- 🚑 エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 🎨 テーマごとの色定義 ---
def get_theme_colors(theme):
    # デフォルト
    c = {
        "bg": "#ffeaf4",
        "dot": "#ffb6c1",
        "text": "#ff1493",
        "border": "#ff69b4",
        "btn": "linear-gradient(180deg, #ffb6c1, #ff69b4)",
        "shadow": "#b0e0e6"
    }
    
    if "強めギャル" in theme:
        c = {
            "bg": "#000000",
            "dot": "#333333",
            "text": "#FFD700",
            "border": "#FFD700",
            "btn": "linear-gradient(180deg, #ffd700, #b8860b)",
            "shadow": "#ff0000"
        }
    elif "Y2K" in theme:
        c = {
            "bg": "#e0ffff",
            "dot": "#00ffff",
            "text": "#0000ff",
            "border": "#0000ff",
            "btn": "linear-gradient(180deg, #00ffff, #0000ff)",
            "shadow": "#ff00ff"
        }
    elif "病みかわ" in theme:
        c = {
            "bg": "#1a001a",
            "dot": "#4b0082",
            "text": "#e6e6fa",
            "border": "#9370db",
            "btn": "linear-gradient(180deg, #d8bfd8, #800080)",
            "shadow": "#000000"
        }
    return c

# --- ここが修正ポイント！CSS注入関数 ---
def inject_custom_css(theme):
    c = get_theme_colors(theme)
    
    st.markdown(f"""
    <style>
        /* フォント読み込み */
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
        
        /* 全体にフォント適用 */
        html, body, [class*="css"] {{
            font-family: 'Mochiy Pop One', sans-serif !important;
        }}

        /* ★最強の背景指定★ */
        /* .stApp はアプリのルート要素。ここを狙い撃つ */
        .stApp {{
            background-color: {c['bg']} !important;
            background-image:
                radial-gradient({c['dot']} 20%, transparent 20%),
                radial-gradient({c['dot']} 20%, transparent 20%) !important;
            background-size: 20px 20px !important;
            background-position: 0 0, 10px 10px !important;
            background-attachment: fixed !important; /* スクロールしても背景固定 */
        }}
        
        /* ヘッダーバー（上の白い部分）も色を変える */
        header {{
            background-color: transparent !important;
        }}

        /* 文字色の一括変更 */
        h1, h2, h3, p, span, div, label, .stMarkdown {{
            color: {c['text']} !important;
        }}
        
        /* タイトル装飾 */
        h1 {{
            text-shadow: 4px 4px 0px #fff, 6px 6px 0px {c['shadow']} !important;
            font-size: 4rem !important;
            transform: rotate(-3deg);
            text-align: center;
            padding-bottom: 20px;
        }}

        /* コンテナ（白い枠）のデザイン */
        .custom-box {{
            background: rgba(255,255,255,0.6);
            border: 4px dotted {c['border']};
            border-radius: 30px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}

        /* ボタンデザイン */
        .stButton > button {{
            background: {c['btn']} !important;
            color: white !important;
            border: 4px solid #fff !important;
            border-radius: 50px !important;
            font-size: 24px !important;
            padding: 10px 30px !important;
            box-shadow: 0 6px 15px {c['text']}66 !important;
            width: 100%;
            transition: 0.3s;
        }}
        .stButton > button:hover {{
            transform: scale(1.05);
        }}

        /* アップローダーの枠線 */
        [data-testid="stFileUploader"] {{
            border: 3px dashed {c['border']} !important;
            border-radius: 20px !important;
            background-color: rgba(255,255,255,0.5) !important;
        }}
        
        /* ラジオボタンの選択肢 */
        .stRadio label {{
            font-size: 18px !important;
            font-weight: bold !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    return c

# --- 画像加工ロジック ---
def apply_gal_effect_safe(base_img, caption_text, theme_mode):
    time.sleep(2)
    # 美肌
    base_img = base_img.convert("RGB")
    base_img = Image.blend(base_img, base_img.filter(ImageFilter.GaussianBlur(1.5)), 0.4)
    base_img = ImageEnhance.Brightness(base_img).enhance(1.15)
    base_img = ImageEnhance.Contrast(base_img).enhance(0.95)
    r, g, b = base_img.split()
    base_img = Image.merge('RGB', (r.point(lambda i: i * 1.05), g, b))

    width, height = base_img.size
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))

    # 切り抜き
    if CAN_REMOVE_BG:
        try:
            fg = remove(base_img).convert("RGBA")
            bg_dir = "assets/bgs"
            if os.path.exists(bg_dir) and len(os.listdir(bg_dir)) > 0:
                bg_img = Image.open(os.path.join(bg_dir, random.choice(bgs))).convert("RGBA")
                canvas.paste(bg_img.resize((width, height)), (0,0))
            canvas.paste(fg, (0,0), fg)
        except:
            canvas.paste(base_img.convert("RGBA"), (0,0))
    else:
        canvas.paste(base_img.convert("RGBA"), (0,0))

    # フレーム
    frame_dir = "assets/frames"
    if os.path.exists(frame_dir):
        fs = [f for f in os.listdir(frame_dir) if not f.startswith('.')]
        if fs:
            fr = Image.open(os.path.join(frame_dir, random.choice(fs))).convert("RGBA")
            canvas = Image.alpha_composite(canvas, fr.resize((width, height)))

    # 文字色
    tc = "#ff1493"; sc = "white"
    if "強めギャル" in theme_mode: tc = "#FFD700"; sc = "black"
    elif "Y2K" in theme_mode: tc = "#00FFFF"; sc = "#000080"
    elif "病みかわ" in theme_mode: tc = "#E6E6FA"; sc = "black"

    draw = ImageDraw.Draw(canvas)
    font_path = "gal_font.ttf"
    try: font = ImageFont.truetype(font_path, int(width/7))
    except: font = ImageFont.load_default()
    
    draw.text((width/10, height/1.4), caption_text, font=font, fill=tc, stroke_width=6, stroke_fill=sc)
    return canvas

def get_gal_caption(image, theme_mode, custom_text):
    if "自由入力" in theme_mode: return custom_text if custom_text else "最強卍"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        base = "平成ギャル雑誌風のキャッチコピー。10文字以内。"
        cond = "テンションMAX"
        if "強め" in theme_mode: cond = "オラオラ系、強気"
        elif "姫" in theme_mode: cond = "お姫様系、甘々"
        elif "Y2K" in theme_mode: cond = "デジタル、近未来"
        elif "病み" in theme_mode: cond = "意味深、ダーク"
        response = model.generate_content([f"{base} 条件: {cond}", image])
        return response.text.strip()
    except:
        return "最強KAWAII宣言💖"


# ==========================================
# 🚀 メイン処理（ここがUIの心臓部）
# ==========================================

# 1. 状態管理（選択されたテーマを覚える）
if 'theme' not in st.session_state:
    st.session_state['theme'] = "姫ギャル (Pink)"

# 2. レイアウト開始
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 01. 素材えらび♡")
    
    # ★ここでラジオボタンを表示し、変更があったらsession_stateを更新する
    selected_theme = st.radio(
        "今日のバイブスは？🌈",
        ["姫ギャル (Pink)", "強めギャル (High)", "Y2K (Cyber)", "病みかわ (Emo)", "自由入力"],
        key="theme_radio" # キーを指定
    )
    
    # ラジオボタンの値が変わったら即座に反映
    if selected_theme != st.session_state['theme']:
        st.session_state['theme'] = selected_theme
        # 画面をリロードしてCSSを適用し直す（これが必殺技）
        st.rerun()

    # 3. ここでCSSを注入！（一番強力なタイミング）
    # カラムの中だろうが関係なく、ページ全体に効くように書いた関数を呼ぶ
    c = inject_custom_css(st.session_state['theme'])

    custom_text = ""
    if "自由入力" in st.session_state['theme']:
        custom_text = st.text_input("好きな言葉（10文字以内）", "ウチら最強卍")

    st.markdown("---")
    uploaded_file = st.file_uploader("ここに写メを投げる！", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.markdown("""<style>div[data-testid="stImage"] > img {border: 10px solid white; box-shadow: 5px 5px 15px rgba(0,0,0,0.2); transform: rotate(-3deg); margin-top: 20px;}</style>""", unsafe_allow_html=True)
        st.image(image, use_container_width=True)
    else:
        st.markdown(f"""<div style="height: 200px; background: rgba(255,255,255,0.5); border-radius: 20px; border: 3px dotted {c['border']}; display: flex; align-items: center; justify-content: center; color: {c['text']};">ここにプレビューが出るよ📸</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if uploaded_file is not None:
        if st.button('💖 ギャル化スイッチON 💖'):
            loading_ph = st.empty()
            loading_ph.markdown(f"""
            <style>.gal-loading-text {{ font-size: 40px; font-weight: 900; color: #fff; text-shadow: 2px 2px 0 {c['text']}, 2px 2px 10px {c['text']}; animation: shake 0.5s infinite; }}
            .gal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: {c['bg']}ee; z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(10px); }}
            @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 50% {{ transform: translate(-1px, 2px) rotate(-1deg); }} 100% {{ transform: translate(1px, -2px) rotate(-1deg); }} }}
            </style><div class="gal-overlay"><div class="gal-loading-text">⚡️ {st.session_state['theme']} 加工中 ⚡️</div></div>""", unsafe_allow_html=True)
            
            txt = get_gal_caption(image, st.session_state['theme'], custom_text)
            res = apply_gal_effect_safe(image, txt, st.session_state['theme'])
            
            loading_ph.empty()
            st.session_state['res'] = res
            st.session_state['txt'] = txt

with col2:
    # ヘッダーをここに配置（CSS適用後なので色が合う）
    st.markdown(f"""
    <div class="custom-box">
        <div style="font-size: 12px; opacity: 0.7; margin-bottom: 10px;">
            Welcome to Gal-M@ker ... {st.session_state['theme']} ...
        </div>
        <h1>Gal-M@ker</h1>
        <div style="background: #fff; border: 2px dashed {c['border']}; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-top: 10px; color: {c['text']};">
            ✨ Powered by Love Loop Inc. ✨
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 02. 完成！！")
    if 'res' in st.session_state:
        st.balloons()
        st.markdown(f"""<div style="text-align: center; font-size: 24px; color: {c['text']}; font-weight: bold; margin-bottom: 10px;">テーマ：{st.session_state['txt']}</div>""", unsafe_allow_html=True)
        st.image(st.session_state['res'], use_container_width=True)
    else:
        st.markdown(f"""<div style="height: 400px; background: rgba(255,255,255,0.5); border-radius: 30px; border: 4px dashed {c['border']}; display: flex; align-items: center; justify-content: center; flex-direction: column; color: {c['text']};"><div style="font-size: 60px;">✨</div><div style="margin-top: 10px; font-weight: bold;">ここに完成画像が出るよ♡</div></div>""", unsafe_allow_html=True)

if not CAN_REMOVE_BG:
    st.info("💡 サーバー負荷軽減モードで稼働中")
