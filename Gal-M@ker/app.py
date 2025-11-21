import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# ==========================================
# 👇 APIキー設定 (ここにキーを貼る！)
# ==========================================
# クラウドの金庫から鍵を取り出す
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("鍵が設定されてないよ！")

st.set_page_config(page_title="Gal-M@ker Pure", page_icon="🦄", layout="wide")

# --- 🚑 エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 💄 美肌＆プリクラ風フィルター ---
def apply_beauty_filter(img):
    img = img.convert("RGB")
    smoothed_img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.blend(img, smoothed_img, 0.4)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.15)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.95)
    r, g, b = img.split()
    r = r.point(lambda i: i * 1.05)
    img = Image.merge('RGB', (r, g, b))
    return img

# --- 🦄 デザインCSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
    html, body, [class*="css"] { font-family: 'Mochiy Pop One', sans-serif; }
    .stApp {
        background-color: #ffeaf4;
        background-image: radial-gradient(#ffb6c1 20%, transparent 20%), radial-gradient(#ffb6c1 20%, transparent 20%);
        background-size: 20px 20px; background-position: 0 0, 10px 10px;
    }
    .header-container {
        position: relative; text-align: center; padding: 40px 0; background: rgba(255,255,255,0.4);
        border-radius: 30px; margin-bottom: 30px; border: 4px dotted #ff69b4; overflow: hidden;
    }
    h1 {
        color: #ff69b4; text-shadow: 4px 4px 0px #fff, 6px 6px 0px #b0e0e6; font-size: 5rem !important;
        transform: rotate(-3deg); margin: 0; letter-spacing: 5px; z-index: 2; position: relative;
    }
    .stCaption {
        color: #ff1493 !important; background: #fff; border: 2px dashed #ff69b4; padding: 5px 15px;
        border-radius: 50px; font-size: 1.2rem !important; display: inline-block; transform: rotate(2deg); margin-top: 10px;
    }
    .deco-left { position: absolute; top: 50%; left: 30px; transform: translateY(-50%) rotate(-15deg); font-size: 80px; filter: drop-shadow(4px 4px 0px #fff); animation: bounce 2s infinite; }
    .deco-right { position: absolute; top: 50%; right: 30px; transform: translateY(-50%) rotate(15deg); font-size: 80px; filter: drop-shadow(4px 4px 0px #fff); animation: bounce 2s infinite reverse; }
    @keyframes bounce { 0%, 100% { transform: translateY(-50%) rotate(-15deg) scale(1); } 50% { transform: translateY(-60%) rotate(-10deg) scale(1.1); } }
    .marquee-container { position: absolute; top: 5px; left: 0; width: 100%; overflow: hidden; white-space: nowrap; opacity: 0.7; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 15s linear infinite; color: #ff1493; font-size: 16px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    div[data-testid="stVerticalBlock"] > div > div {
        background-color: rgba(255, 255, 255, 0.6); border: none; border-radius: 30px;
        box-shadow: 0 8px 32px 0 rgba(255, 105, 180, 0.2); backdrop-filter: blur(4px); padding: 20px; margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(180deg, #ffb6c1, #ff69b4); color: white !important; border: 4px solid #fff;
        border-radius: 50px; font-size: 24px; padding: 15px; box-shadow: 0 6px 15px rgba(255, 20, 147, 0.4); transition: 0.2s;
    }
    .stButton>button:hover { transform: scale(1.05) rotate(1deg); }
    h3 { color: #ff1493 !important; background: linear-gradient(transparent 70%, #b0e0e6 70%); display: inline-block; padding: 0 10px; }
    
    .stRadio label { font-size: 18px !important; color: #ff1493 !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# --- 関数: AIにテーマを指示する ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由入力" in theme_mode:
        return custom_text if custom_text else "最強卍"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        base_prompt = "この画像を見て、平成のギャル雑誌の見出し風のキャッチコピーを考えて。10文字以内。"
        
        if "強めギャル" in theme_mode:
            style = "オラオラ系、強気、『ウチら』『最強』『卍』を使って。黒ギャル風。"
        elif "姫ギャル" in theme_mode:
            style = "お姫様系、甘々、ハート多用、『ですわ』『〜み』『天使』を使って。ピンク系。"
        elif "Y2K" in theme_mode:
            style = "近未来、デジタル、英語混じり、クールに。『System』『Connect』『Link』など。"
        elif "病みかわ" in theme_mode:
            style = "少しダーク、意味深、メンヘラ気味。『...』『永遠』『愛』を使って。"
        else:
            style = "とにかくテンションMAXで、楽しそうな感じで。"

        prompt = f"{base_prompt}\n条件: {style}"
        
        response = model.generate_content([prompt, image])
        return response.text.strip()
    except:
        return "最強KAWAII宣言💖"

# --- 関数: 画像加工（色変化対応！） ---
def apply_gal_effect_safe(base_img, caption_text, theme_mode):
    time.sleep(3)
    base_img = apply_beauty_filter(base_img)
    width, height = base_img.size
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))

    if CAN_REMOVE_BG:
        try:
            foreground = remove(base_img).convert("RGBA")
            bg_dir = "assets/bgs"
            if os.path.exists(bg_dir) and len(os.listdir(bg_dir)) > 0:
                bgs = [f for f in os.listdir(bg_dir) if not f.startswith('.')]
                if bgs:
                    bg_img = Image.open(os.path.join(bg_dir, random.choice(bgs))).convert("RGBA")
                    bg_img = bg_img.resize((width, height))
                    canvas.paste(bg_img, (0,0))
            canvas.paste(foreground, (0, 0), foreground)
        except:
            canvas.paste(base_img.convert("RGBA"), (0,0))
    else:
        canvas.paste(base_img.convert("RGBA"), (0,0))

    frame_dir = "assets/frames"
    if os.path.exists(frame_dir) and len(os.listdir(frame_dir)) > 0:
        frames = [f for f in os.listdir(frame_dir) if not f.startswith('.')]
        if frames:
            fr_img = Image.open(os.path.join(frame_dir, random.choice(frames))).convert("RGBA")
            canvas = Image.alpha_composite(canvas, fr_img.resize((width, height)))

    stamp_dir = "assets/stamps"
    if os.path.exists(stamp_dir) and len(os.listdir(stamp_dir)) > 0:
        stamps = [f for f in os.listdir(stamp_dir) if not f.startswith('.')]
        if stamps:
            for _ in range(random.randint(3, 5)):
                try:
                    stamp_name = random.choice(stamps)
                    stamp_img = Image.open(os.path.join(stamp_dir, stamp_name)).convert("RGBA")
                    if CAN_REMOVE_BG:
                        stamp_img = remove(stamp_img)
                    size = random.randint(int(width/6), int(width/3))
                    stamp_img = stamp_img.resize((size, size))
                    x = random.randint(0, width - size)
                    y = random.randint(0, height - size)
                    canvas.paste(stamp_img, (x, y), stamp_img)
                except:
                    pass

    # ★テーマに合わせて文字色を変える！★
    text_color = "#ff1493" # デフォルト（ピンク）
    stroke_color = "white"
    
    if "強めギャル" in theme_mode:
        text_color = "#FFD700" # ゴールド
        stroke_color = "#000000" # 黒
    elif "Y2K" in theme_mode:
        text_color = "#00FFFF" # サイバー水色
        stroke_color = "#000080" # ネイビー
    elif "病みかわ" in theme_mode:
        text_color = "#800080" # 紫
        stroke_color = "#000000" # 黒
    
    draw = ImageDraw.Draw(canvas)
    font_path = "gal_font.ttf"
    try:
        font_size = int(width / 7)
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    text_x = width / 10
    text_y = height / 1.4
    stroke_width = 6
    # 設定した色で描く
    draw.text((text_x, text_y), caption_text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

    return canvas

# --- UIレイアウト ---
st.markdown("""
<div class="header-container">
    <div class="marquee-container">
        <div class="marquee-text">
            Welcome to Gal-M@ker ... Powered by Love Loop Inc ... HEISEI RETRO STYLE ... Let's make KAWAII pictures! ... 🌺🦋💖
        </div>
    </div>
    <div class="deco-left">🌺</div>
    <div class="deco-right">🦋</div>
    <h1>Gal-M@ker</h1>
    <div class="stCaption">✨ Powered by Love Loop Inc. ✨</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 01. 素材えらび♡")
    
    theme_mode = st.radio(
        "今日のバイブスは？🌈",
        ["おまかせ", "強めギャル", "姫ギャル", "Y2K", "病みかわ", "自由入力"]
    )
    
    custom_text = ""
    if theme_mode == "自由入力":
        custom_text = st.text_input("好きな言葉を入れてね！（10文字以内推奨）", "ウチら最強卍")

    st.markdown("---")
    
    uploaded_file = st.file_uploader("ここに写メを投げる！", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.markdown("""<style>div[data-testid="stImage"] > img {border: 10px solid white; box-shadow: 5px 5px 15px rgba(0,0,0,0.2); transform: rotate(-3deg); margin-top: 20px;}</style>""", unsafe_allow_html=True)
        st.image(image, use_container_width=True)
    else:
        st.markdown("""<div style="height: 200px; background: rgba(255,255,255,0.5); border-radius: 20px; border: 3px dotted #ffb6c1; display: flex; align-items: center; justify-content: center; color: #ff69b4;">ここにプレビューが出るよ📸</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if uploaded_file is not None:
        if st.button('💖 ギャル化スイッチON 💖'):
            
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <style>
                @keyframes shake { 0% { transform: translate(1px, 1px) rotate(0deg); } 10% { transform: translate(-1px, -2px) rotate(-1deg); } 50% { transform: translate(-1px, 2px) rotate(-1deg); } 100% { transform: translate(1px, -2px) rotate(-1deg); } }
                .gal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 182, 193, 0.95); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(10px); }
                .gal-loading-container { display: flex; align-items: center; justify-content: center; animation: shake 0.5s infinite; margin-bottom: 20px; width: 100%; flex-wrap: nowrap; }
                .gal-loading-text { font-size: 6vw; font-weight: 900; color: #fff; text-shadow: 4px 4px 0 #ff1493, -2px -2px 0 #ff1493, 4px 4px 20px #ff69b4; margin: 0 20px; white-space: nowrap; }
                .gal-bolt { font-size: 6vw; line-height: 1; flex-shrink: 0; }
                .gal-sub-text { font-size: 24px; color: #ff1493; background: #fff; padding: 10px 30px; border-radius: 50px; border: 4px dotted #ff1493; white-space: nowrap; }
            </style>
            <div class="gal-overlay"><div class="gal-loading-container"><span class="gal-bolt">⚡️</span><div class="gal-loading-text">激かわ加工中</div><span class="gal-bolt">⚡️</span></div><div class="gal-sub-text">AIが魔法をかけてるょ...🦄</div></div>
            """, unsafe_allow_html=True)
            
            gal_text = get_gal_caption(image, theme_mode, custom_text)
            # ここでテーマも渡して色を変える！
            processed_image = apply_gal_effect_safe(image, gal_text, theme_mode)
            
            loading_placeholder.empty()
            st.session_state['processed_image'] = processed_image
            st.session_state['gal_text'] = gal_text

with col2:
    st.markdown("### 02. 完成！！")
    if 'processed_image' in st.session_state:
        st.balloons()
        st.markdown(f"""<div style="text-align: center; font-size: 24px; color: #ff1493; font-weight: bold; margin-bottom: 10px; text-shadow: 2px 2px 0 #fff;">テーマ：{st.session_state['gal_text']}</div>""", unsafe_allow_html=True)
        st.markdown("""<style>div[data-testid="stImage"] {transform: rotate(2deg);}</style>""", unsafe_allow_html=True)
        st.image(st.session_state['processed_image'], use_container_width=True)
    else:
        st.markdown("""<div style="height: 400px; background: rgba(255,255,255,0.5); border-radius: 30px; border: 4px dashed #ff69b4; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #ff1493;"><div style="font-size: 60px;">✨</div><div style="margin-top: 10px; font-weight: bold;">ここに完成画像が出るよ♡</div></div>""", unsafe_allow_html=True)

if not CAN_REMOVE_BG:
    st.warning("⚠️ デコモードのみ稼働中")
