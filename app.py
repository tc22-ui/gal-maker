import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import google.generativeai as genai
import time

# ==========================================
# 👇 APIキー設定 (ここにキーを貼る！)
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
def get_theme_styles(theme):
    # デフォルト（おまかせ・姫ギャル）
    colors = {
        "bg_color": "#ffeaf4", # 薄ピンク
        "bg_dot": "#ffb6c1",   # ドットのピンク
        "text_main": "#ff69b4", # 濃いピンク
        "text_sub": "#ff1493",
        "border": "#ff69b4",
        "button_grad": "linear-gradient(180deg, #ffb6c1, #ff69b4)",
        "shadow": "#b0e0e6"    # 水色
    }
    
    if "強めギャル" in theme:
        colors = {
            "bg_color": "#000000", # 黒
            "bg_dot": "#ffd700",   # 金
            "text_main": "#ffd700", # 金
            "text_sub": "#ffffff",
            "border": "#ffd700",
            "button_grad": "linear-gradient(180deg, #ffd700, #b8860b)", # 金グラデ
            "shadow": "#ff0000"    # 赤
        }
    elif "Y2K" in theme:
        colors = {
            "bg_color": "#e0ffff", # 薄い水色
            "bg_dot": "#00ffff",   # サイバー水色
            "text_main": "#0000ff", # 青
            "text_sub": "#000080",
            "border": "#0000ff",
            "button_grad": "linear-gradient(180deg, #00ffff, #0000ff)", # 青グラデ
            "shadow": "#ff00ff"    # ネオン紫
        }
    elif "病みかわ" in theme:
        colors = {
            "bg_color": "#f3e6ff", # 薄紫
            "bg_dot": "#800080",   # 紫
            "text_main": "#800080",
            "text_sub": "#000000",
            "border": "#800080",
            "button_grad": "linear-gradient(180deg, #d8bfd8, #800080)", # 紫グラデ
            "shadow": "#000000"    # 黒
        }
    
    return colors

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

# --- 関数: AIキャッチコピー ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由入力" in theme_mode:
        return custom_text if custom_text else "最強卍"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        base_prompt = "この画像を見て、平成のギャル雑誌の見出し風のキャッチコピーを考えて。10文字以内。"
        if "強めギャル" in theme_mode: style = "オラオラ系、強気、『ウチら』『最強』『卍』を使って。黒ギャル風。"
        elif "姫ギャル" in theme_mode: style = "お姫様系、甘々、ハート多用、『ですわ』『〜み』『天使』を使って。ピンク系。"
        elif "Y2K" in theme_mode: style = "近未来、デジタル、英語混じり、クールに。"
        elif "病みかわ" in theme_mode: style = "少しダーク、意味深、メンヘラ気味。"
        else: style = "とにかくテンションMAXで。"
        response = model.generate_content([f"{base_prompt}\n条件: {style}", image])
        return response.text.strip()
    except:
        return "最強KAWAII宣言💖"

# --- 関数: 画像加工 ---
def apply_gal_effect_safe(base_img, caption_text, theme_mode):
    time.sleep(2) # 待ち時間を少し短縮
    base_img = apply_beauty_filter(base_img)
    width, height = base_img.size
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))

    # 背景切り抜き（失敗したらスキップ）
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

    # フレーム
    frame_dir = "assets/frames"
    if os.path.exists(frame_dir) and len(os.listdir(frame_dir)) > 0:
        frames = [f for f in os.listdir(frame_dir) if not f.startswith('.')]
        if frames:
            fr_img = Image.open(os.path.join(frame_dir, random.choice(frames))).convert("RGBA")
            canvas = Image.alpha_composite(canvas, fr_img.resize((width, height)))

    # ★スタンプ（ここを軽量化！）★
    stamp_dir = "assets/stamps"
    if os.path.exists(stamp_dir) and len(os.listdir(stamp_dir)) > 0:
        stamps = [f for f in os.listdir(stamp_dir) if not f.startswith('.')]
        if stamps:
            for _ in range(random.randint(3, 6)): # スタンプ数
                try:
                    stamp_name = random.choice(stamps)
                    stamp_img = Image.open(os.path.join(stamp_dir, stamp_name)).convert("RGBA")
                    
                    # 【軽量化】rembgは重いので、エラーが出たら「そのまま」使う
                    if CAN_REMOVE_BG:
                        try:
                            # 小さい画像ならいけるかも？だめならスキップ
                            stamp_img = remove(stamp_img)
                        except:
                            pass # 切り抜けなくても、そのまま貼る！

                    size = random.randint(int(width/6), int(width/3))
                    stamp_img = stamp_img.resize((size, size))
                    x = random.randint(0, width - size)
                    y = random.randint(0, height - size)
                    canvas.paste(stamp_img, (x, y), stamp_img)
                except:
                    pass

    # 文字色決定
    text_color = "#ff1493"
    stroke_color = "white"
    if "強めギャル" in theme_mode:
        text_color = "#FFD700"; stroke_color = "black"
    elif "Y2K" in theme_mode:
        text_color = "#00FFFF"; stroke_color = "#000080"
    elif "病みかわ" in theme_mode:
        text_color = "#800080"; stroke_color = "black"

    draw = ImageDraw.Draw(canvas)
    font_path = "gal_font.ttf"
    try:
        font_size = int(width / 7)
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    text_x = width / 10
    text_y = height / 1.4
    draw.text((text_x, text_y), caption_text, font=font, fill=text_color, stroke_width=6, stroke_fill=stroke_color)

    return canvas

# --- メイン処理開始 ---

# 1. 先にUIを描画して、テーマを取得する
st.markdown("### 01. バイブス設定🌈")
theme_mode = st.radio(
    "テーマを選んでね！",
    ["おまかせ (AI)", "強めギャル (High)", "姫ギャル (Pink)", "Y2K (Cyber)", "病みかわ (Emo)", "自由入力"],
    horizontal=True
)

# 2. テーマに応じた色を取得
c = get_theme_styles(theme_mode)

# 3. CSSを動的に生成して注入！
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
    html, body, [class*="css"] {{ font-family: 'Mochiy Pop One', sans-serif; }}
    
    /* 背景色とドット色を変える */
    .stApp {{
        background-color: {c['bg_color']};
        background-image: radial-gradient({c['bg_dot']} 20%, transparent 20%), radial-gradient({c['bg_dot']} 20%, transparent 20%);
        background-size: 20px 20px; background-position: 0 0, 10px 10px;
        transition: background-color 0.5s ease;
    }}
    
    /* タイトル周り */
    .header-container {{
        background: rgba(255,255,255,0.6); border: 4px dotted {c['border']}; border-radius: 30px; padding: 20px; text-align: center; margin-bottom: 20px;
    }}
    h1 {{
        color: {c['text_main']}; text-shadow: 4px 4px 0px #fff, 6px 6px 0px {c['shadow']};
        font-size: 4rem !important; transform: rotate(-3deg); margin: 0;
    }}
    
    /* ボタンの色も変える */
    .stButton>button {{
        background: {c['button_grad']}; color: white !important; border: 4px solid #fff;
        border-radius: 50px; font-size: 24px; padding: 10px 30px; box-shadow: 0 6px 15px {c['text_main']}66;
    }}
    
    /* その他 */
    h3 {{ color: {c['text_main']} !important; }}
    .stRadio label {{ color: {c['text_main']} !important; font-weight: bold; }}
    
    /* マーキー */
    .marquee-text {{ color: {c['text_sub']}; }}
</style>
""", unsafe_allow_html=True)

# --- UIレイアウト ---
st.markdown(f"""
<div class="header-container">
    <div class="marquee-container">
        <div class="marquee-text">Welcome to Gal-M@ker ... {theme_mode} MODE ... Powered by Love Loop Inc ... 🌺🦋💖</div>
    </div>
    <h1>Gal-M@ker</h1>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ここに写メを投げる！", type=['jpg', 'png', 'jpeg'])

custom_text = ""
if "自由入力" in theme_mode:
    custom_text = st.text_input("好きな言葉（10文字以内）", "ウチら最強卍")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    if st.button('💖 ギャル化スイッチON 💖'):
        # ローディング演出
        loading_placeholder = st.empty()
        loading_placeholder.markdown(f"""
        <style>
            @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 50% {{ transform: translate(-1px, 2px) rotate(-1deg); }} 100% {{ transform: translate(1px, -2px) rotate(-1deg); }} }}
            .gal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: {c['bg_color']}ee; z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(10px); }}
            .gal-loading-text {{ font-size: 6vw; font-weight: 900; color: #fff; text-shadow: 4px 4px 0 {c['text_main']}, 4px 4px 20px {c['text_main']}; white-space: nowrap; animation: shake 0.5s infinite; }}
        </style>
        <div class="gal-overlay"><div class="gal-loading-text">⚡️ {theme_mode} 加工中 ⚡️</div></div>
        """, unsafe_allow_html=True)
        
        gal_text = get_gal_caption(image, theme_mode, custom_text)
        processed_image = apply_gal_effect_safe(image, gal_text, theme_mode)
        
        loading_placeholder.empty()
        st.balloons()
        st.image(processed_image, use_container_width=True)
        st.success(f"テーマ: {gal_text}")

if not CAN_REMOVE_BG:
    st.warning("※クラウド環境のため、背景切り抜き機能は制限されています")
