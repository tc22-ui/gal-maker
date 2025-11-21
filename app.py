import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# ==========================================
# 👇 APIキー設定 & 診断
# ==========================================
api_status = "不明"
try:
    # クラウドの金庫を確認
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        api_status = "✅ クラウドの鍵あり"
    else:
        # ローカルまたは設定忘れ
        GOOGLE_API_KEY = "AIzaSyCvvv_MEZ1zE6gdjmXrfT589tWWRTyhzvE" # ← ローカルで動かす時はここに入れる
        api_status = "⚠️ クラウドの鍵なし（設定が必要です）"
except:
    GOOGLE_API_KEY = "ここにAPIキー"
    api_status = "⚠️ ローカルモード"

if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    api_status = "❌ 鍵が無効です（AIza...で始まっていません）"

# --- レイアウト設定 ---
st.set_page_config(page_title="Gal-M@ker", page_icon="🦄", layout="wide")

# --- 🚑 エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 🎨 テーマ色定義 ---
def get_theme_colors(theme):
    c = {"bg": "#ffeaf4", "dot": "#ffb6c1", "text": "#ff1493", "border": "#ff69b4", "btn": "linear-gradient(180deg, #ffb6c1, #ff69b4)", "shadow": "#b0e0e6", "img_text": "#ff1493", "img_stroke": "white"}
    
    if "強め" in theme:
        c = {"bg": "#000000", "dot": "#333333", "text": "#FFD700", "border": "#FFD700", "btn": "linear-gradient(180deg, #ffd700, #b8860b)", "shadow": "#ff0000", "img_text": "#FFD700", "img_stroke": "black"}
    elif "Y2K" in theme:
        c = {"bg": "#e0ffff", "dot": "#00ffff", "text": "#0000ff", "border": "#0000ff", "btn": "linear-gradient(180deg, #00ffff, #0000ff)", "shadow": "#ff00ff", "img_text": "#00FFFF", "img_stroke": "#000080"}
    elif "病み" in theme:
        c = {"bg": "#1a001a", "dot": "#4b0082", "text": "#e6e6fa", "border": "#9370db", "btn": "linear-gradient(180deg, #d8bfd8, #800080)", "shadow": "#000000", "img_text": "#E6E6FA", "img_stroke": "black"}
    return c

# --- AIキャッチコピー生成 ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由" in theme_mode: return custom_text if custom_text else "最強卍"
    
    # APIキーがおかしい場合は門前払い
    if "❌" in api_status or "⚠️" in api_status:
        return "鍵の設定エラー"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # バイブスごとの指示をさらに極端にする
        style_prompt = ""
        if "強め" in theme_mode: style_prompt = "オラオラ系、強気な口調。『ウチら最強』『卍』『喧嘩上等』みたいな漢字多めのヤンキーギャル語。"
        elif "姫" in theme_mode: style_prompt = "甘々なお姫様口調。『〜ですわ』『てんち』『優勝』みたいなフワフワした言葉。"
        elif "Y2K" in theme_mode: style_prompt = "無機質でクール。『System』『Error』『Connect』など英語とカタカナを混ぜて。"
        elif "病み" in theme_mode: style_prompt = "意味深でダーク。『永遠...』『愛』『救済』などメンヘラチックに。"
        else: style_prompt = "とにかくテンションMAXで楽しそうに。"

        prompt = f"この画像を見て、一言キャッチコピーをつけて。{style_prompt} 10文字以内。絵文字は1つまで。"
        
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        
        # 万が一空っぽなら予備
        return text if text else "無言..."
        
    except Exception as e:
        # エラー内容をコンソールに出す
        print(f"AI Error: {e}")
        # 画面上の文字もエラー理由に変える（これで原因がわかる！）
        return "AIエラー発生中"

# --- 画像加工 ---
def process_image(image, caption, color_settings):
    img = image.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.1)
    w, h = img.size
    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    
    # 背景
    try:
        if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
            fg = remove(img).convert("RGBA")
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs:
                bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h))
                canvas.paste(bg, (0,0))
            canvas.paste(fg, (0,0), fg)
        else:
            canvas.paste(img.convert("RGBA"), (0,0))
    except:
        canvas.paste(img.convert("RGBA"), (0,0))

    # スタンプ
    if os.path.exists("assets/stamps"):
        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')]
        if stamps:
            for _ in range(4):
                try:
                    s = Image.open(f"assets/stamps/{random.choice(stamps)}").convert("RGBA")
                    sz = random.randint(int(w/6), int(w/3))
                    canvas.paste(s.resize((sz, sz)), (random.randint(0, w-sz), random.randint(0, h-sz)), s.resize((sz, sz)))
                except: pass

    # 文字
    draw = ImageDraw.Draw(canvas)
    try: font = ImageFont.truetype("gal_font.ttf", int(w/7))
    except: font = ImageFont.load_default()
    
    draw.text((w/10, h/1.4), caption, font=font, fill=color_settings['img_text'], stroke_width=6, stroke_fill=color_settings['img_stroke'])
    return canvas

# --- UI ---
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');html, body, [class*="css"] { font-family: 'Mochiy Pop One', sans-serif; }</style>""", unsafe_allow_html=True)

if 'theme' not in st.session_state: st.session_state.theme = "姫ギャル (Pink)"

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 01. 素材えらび♡")
    
    # 鍵の状態を表示（デバッグ用）
    if "✅" in api_status:
        st.success(f"システム: {api_status}")
    else:
        st.error(f"システム: {api_status}")
        st.info("Streamlit Cloudの Settings > Secrets にAPIキーを設定してください！")

    new_theme = st.radio("今日のバイブスは？🌈", ["姫ギャル (Pink)", "強めギャル (High)", "Y2K (Cyber)", "病みかわ (Emo)", "自由入力"], key="rad")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    c = get_theme_colors(st.session_state.theme)
    
    # CSS注入
    st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{ background-color: {c['bg']} !important; background-image: radial-gradient({c['dot']} 20%, transparent 20%), radial-gradient({c['dot']} 20%, transparent 20%) !important; background-size: 20px 20px !important; }}
        h1, h2, h3, p, div, label, span {{ color: {c['text']} !important; }}
        .stButton>button {{ background: {c['btn']} !important; color: white !important; border: 3px solid #fff !important; border-radius: 50px !important; box-shadow: 0 5px 10px {c['text']}66 !important; }}
    </style>
    """, unsafe_allow_html=True)

    custom_text = ""
    if "自由" in st.session_state.theme: custom_text = st.text_input("文字入力", "ウチら最強")

    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        if st.button("💖 ギャル化スイッチON 💖"):
            with st.spinner("AIが考え中..."):
                caption = get_gal_caption(image, st.session_state.theme, custom_text)
                res = process_image(image, caption, c)
                st.session_state.final = res
                st.session_state.cap = caption

with col2:
    st.markdown(f"""<div style="border:4px dotted {c['border']};background:rgba(255,255,255,0.7);border-radius:30px;padding:20px;text-align:center;margin-bottom:20px;"><h1 style="margin:0;font-size:3rem;text-shadow:3px 3px 0 #fff,5px 5px 0 {c['shadow']};">Gal-M@ker</h1><p>{st.session_state.theme} MODE</p></div>""", unsafe_allow_html=True)
    if 'final' in st.session_state:
        st.balloons()
        st.image(st.session_state.final, use_container_width=True)
        st.success(f"テーマ: {st.session_state.cap}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
