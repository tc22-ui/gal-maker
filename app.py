import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps, ImageChops
import os
import random
import google.generativeai as genai
import time
import numpy as np

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

# --- 4. テーマ定義 (フチをなくして発光色を定義！) ---
THEME_CONFIG = {
    "姫ギャル (Pink)": {
        "colors": {
            "bg_base": "#fff0f5", "dot": "#ff69b4",
            "text": "#ff69b4", "glow": "#ff1493", # 文字色と発光色
            "border": "#ff69b4", "shadow": "#ff1493"
        },
        "words": ["姫降臨", "お城に帰宅♡", "全世界一番可愛", "人形同盟", "王子様どこ？", "LOVE♡"],
        "loading": ["全人類、私に跪け！\nプリンセス・レボリューション！", "鏡よ鏡、今この瞬間だけは魔法をかけて♡\nラブリー・オーバーロード！", "可愛さは正義、ダサさは有罪！\n執行対象、発見♡"]
    },
    "強めギャル (High)": {
        "colors": {
            "bg_base": "#000000", "dot": "#333333",
            "text": "#FFD700", "glow": "#FFA500", # ゴールド文字とオレンジ発光
            "border": "#FFD700", "shadow": "#FF0000"
        },
        "words": ["我等友情永久不滅", "喧嘩上等", "治安悪め", "卍最強卍", "鬼盛れ注意", "全国制覇"],
        "loading": ["気合注入、根性全開！\n地元最強の底力、見せたんで！", "売られた喧嘩は高値で買うよ？\nゴールデン・ナックル！", "黒肌はダイヤモンドの輝き！\n闇を切り裂くギャル魂！"]
    },
    "Y2K (Cyber)": {
        "colors": {
            "bg_base": "#e0ffff", "dot": "#0000ff",
            "text": "#00bfff", "glow": "#0000ff", # 水色文字と青発光
            "border": "#0000ff", "shadow": "#00ffff"
        },
        "words": ["ズッ友だよ！！", "激アツ🔥", "運命共同体", "あげぽよ⤴︎", "LOVExxx", "バリ3📡"],
        "loading": ["バリ3、激盛れ、バイブスMAX！\n届いて、私のテレパシー！", "過去も未来もウチらのもん！\nミレニアム・パラパラ・ダンス！", "デコ電チャージ、ストラップ装着！\n繋がれ、運命のチェーン！"]
    },
    "病みかわ (Emo)": {
        "colors": {
            "bg_base": "#1a001a", "dot": "#800080",
            "text": "#d8bfd8", "glow": "#800080", # 薄紫文字と紫発光
            "border": "#9370db", "shadow": "#d8bfd8"
        },
        "words": ["虚無", "生きるの辛", "顔面国宝", "依存先→", "†昇天†", "鬱..."],
        "loading": ["現実なんていらない…\n夢の世界へ、オーバードーズ・マジック", "私の痛み、あなたにもあげる。\nジェラシー・インジェクション！", "愛してくれなきゃ呪っちゃうよ？\n束縛のレッド・リボン！"]
    },
    "自由入力": {
        "colors": {
            "bg_base": "#ffffff", "dot": "#cccccc",
            "text": "#ff00ff", "glow": "#ff00ff", # 蛍光ピンク
            "border": "#333333", "shadow": "#000000"
        },
        "words": ["最強卍"],
        "loading": ["Now Loading...", "Please Wait...", "Processing..."]
    }
}

# --- 5. CSS注入 (UIもネオン風に！) ---
def inject_css(theme):
    c = THEME_CONFIG[theme]["colors"]
    deco_color = c['border'].replace("#", "%23")
    star_svg = f"""url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50"><path d="M25 0 L30 18 L50 18 L35 30 L40 50 L25 38 L10 50 L15 30 L0 18 L20 18 Z" fill="none" stroke="{deco_color}" stroke-width="2" stroke-linejoin="round" /></svg>')"""
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Potta+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Potta One', sans-serif !important; }}
        
        [data-testid="stAppViewContainer"] {{
            background-color: #f8f9fa !important;
            background-image: linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px) !important;
            background-size: 25px 25px !important;
        }}
        [data-testid="stAppViewContainer"]::before {{ content: ""; position: fixed; top: 50px; left: 10px; width: 100px; height: 100px; background-image: {star_svg}; background-repeat: no-repeat; opacity: 0.6; pointer-events: none; }}
        [data-testid="stAppViewContainer"]::after {{ content: ""; position: fixed; bottom: 50px; right: 10px; width: 100px; height: 100px; background-image: {star_svg}; background-repeat: no-repeat; transform: rotate(20deg); opacity: 0.6; pointer-events: none; }}
        
        /* ↓ UIの文字もネオン風に変更 ↓ */
        h1, h2, h3, p, div, label, span, [data-testid="stMarkdownContainer"] p {{
            color: {c['text']} !important;
            text-shadow:
                0 0 5px {c['text']},
                0 0 10px {c['glow']},
                0 0 15px {c['glow']},
                4px 4px 2px rgba(0,0,0,0.3) !important;
            letter-spacing: 1px; font-weight: 900 !important;
        }}
        h1 {{ font-size: 3.5rem !important; transform: rotate(-3deg); margin-bottom: 20px !important; }}
        .stRadio label p {{ font-size: 1.2rem !important; }}
        .custom-box {{ border: 3px dashed {c['border']}; background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 20px {c['glow']} inset; }}
        .stButton > button {{
            background: linear-gradient(180deg, #ffffff 0%, {c['text']} 100%) !important; background-color: white !important;
            color: {c['text']} !important; border: 2px solid {c['text']} !important; border-radius: 50px !important;
            box-shadow: 0 0 10px {c['glow']}, 0 4px 0 {c['text']} !important; font-size: 1.4rem !important; transition: all 0.1s; font-weight: bold;
        }}
        .stButton > button:active {{ transform: translateY(4px); box-shadow: 0 0 5px {c['glow']}, 0 2px 0 {c['text']} !important; }}
        .marquee-container {{ position: fixed; top: 0; left: 0; width: 100%; background: {c['border']}; z-index: 9999; overflow: hidden; white-space: nowrap; padding: 8px 0; font-size: 16px; border-bottom: 2px solid white; box-shadow: 0 0 10px {c['glow']}; }}
        .marquee-content {{ display: inline-block; animation: marquee 15s linear infinite; color: white !important; text-shadow: 0 0 5px {c['glow']} !important; font-weight: bold; }}
        @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        @keyframes flash {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
        .gal-loading {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 999999; background-color: rgba(0,0,0,0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; }}
        .gal-loading-text {{ font-family: 'Potta One', sans-serif; font-size: 2rem; line-height: 1.5; font-weight: 900; color: #fff !important; text-shadow: 0 0 10px {c['text']}, 0 0 20px {c['glow']} !important; animation: flash 0.5s infinite; white-space: pre-wrap; }}
    </style>
    <div class="marquee-container"><div class="marquee-content">Welcome to Gal-M@ker ... Powered by Love Loop Inc ... HEISEI RETRO STYLE ... Make it KAWAII ... {theme} MODE ... 🌺🦋💖</div></div>
    """, unsafe_allow_html=True)

# --- 6. AI ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由" in theme_mode: return custom_text if custom_text else "最強卍"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        slang_guide = f"テーマは「{theme_mode}」。リスト: {THEME_CONFIG[theme_mode]['words']}"
        prompt = f"この画像を見て、平成ギャル雑誌のキャッチコピーをつけて。{slang_guide} 10文字以内。令和言葉禁止。"
        response = model.generate_content([prompt, image])
        return response.text.strip()
    except: return random.choice(THEME_CONFIG[theme_mode]["words"])

# --- 7. 画像加工 (★ネオン＆ぷるぷるジェル文字実装★) ---
def draw_neon_gloss_text(canvas, text, font, x, y, text_color_hex, glow_color_hex):
    # 色の準備
    from PIL import ImageColor
    text_color = ImageColor.getrgb(text_color_hex)
    glow_color = ImageColor.getrgb(glow_color_hex)
    
    # 1. 発光（Glow）レイヤーを作成
    # 文字の形のマスクを作る
    mask = Image.new('L', canvas.size, 0)
    d_mask = ImageDraw.Draw(mask)
    d_mask.text((x, y), text, font=font, fill=255)
    
    # マスクを強くぼかして発光体を作る
    glow_mask = mask.filter(ImageFilter.GaussianBlur(radius=15))
    
    # 発光レイヤー（単色）
    glow_layer = Image.new('RGBA', canvas.size, glow_color + (200,)) # 透明度200
    
    # ぼかしたマスクで発光レイヤーを切り抜いて合成
    canvas.paste(glow_layer, (0,0), glow_mask)

    # 2. ドロップシャドウ（影）
    draw = ImageDraw.Draw(canvas)
    shadow_offset = 6
    # 少し透明な黒で柔らかい影を描く
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 180))

    # 3. 文字本体（Main Body）
    draw.text((x, y), text, font=font, fill=text_color)
    
    # 4. 光沢（Gloss）ハイライト - これが命！
    # 白いハイライトレイヤー
    highlight = Image.new('RGBA', canvas.size, (255, 255, 255, 0))
    d_highlight = ImageDraw.Draw(highlight)
    
    # テキストのバウンディングボックス取得
    bbox = draw.textbbox((x, y), text, font=font)
    
    # 上半分に強くシャープな白を入れる
    highlight_h = int((bbox[3] - bbox[1]) * 0.45)
    # 楕円形っぽく描画
    d_highlight.ellipse([bbox[0], bbox[1], bbox[2], bbox[1] + highlight_h*2], fill=(255, 255, 255, 220))
    
    # マスクを使って文字の部分だけハイライトを残す（下半分を切り取る）
    highlight_masked = ImageChops.multiply(highlight, mask.convert('RGBA'))
    # さらに上半分だけ残すための矩形マスク
    top_mask = Image.new('L', canvas.size, 0)
    d_top_mask = ImageDraw.Draw(top_mask)
    d_top_mask.rectangle([bbox[0], bbox[1], bbox[2], bbox[1] + highlight_h], fill=255)
    
    canvas.paste(highlight_masked, (0,0), top_mask)

def process_image(image, caption, theme_mode):
    c = THEME_CONFIG[theme_mode]["colors"]
    img = image.convert("RGB"); img = ImageEnhance.Brightness(img).enhance(1.15)
    w, h = img.size; canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    
    try:
        if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
            from rembg import remove; fg = remove(img).convert("RGBA"); bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs: bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h)); canvas.paste(bg, (0,0))
            canvas.paste(fg, (0,0), fg)
        else: canvas.paste(img.convert("RGBA"), (0,0))
    except: canvas.paste(img.convert("RGBA"), (0,0))
    
    if os.path.exists("assets/stamps"):
        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')]
        if stamps:
            for _ in range(6):
                try:
                    s = Image.open(f"assets/stamps/{random.choice(stamps)}").convert("RGBA")
                    sz = random.randint(int(w/7), int(w/4)); s_res = s.resize((sz, sz))
                    sx, sy = random.randint(0, w-sz), random.randint(0, h-sz)
                    canvas.paste(s_res, (sx, sy), s_res)
                except: pass

    draw = ImageDraw.Draw(canvas)
    font_size = int(min(w, h) / 6)
    
    font_path = "gal_font.ttf"
    for file in os.listdir("."):
        if file.endswith(".ttf") or file.endswith(".otf"):
            font_path = file
            break
            
    try: font = ImageFont.truetype(font_path, font_size)
    except: font = ImageFont.load_default()

    margin = int(min(w, h) * 0.05); max_text_width = w - 2 * margin
    while font_size > 10:
        bbox = draw.textbbox((0, 0), caption, font=font)
        if bbox[2] - bbox[0] <= max_text_width: break
        font_size -= 5
        try: font = ImageFont.truetype(font_path, font_size)
        except: break

    bbox = draw.textbbox((0, 0), caption, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    positions = [(margin, margin), (w-text_w-margin, margin), (margin, h-text_h-margin), (w-text_w-margin, h-text_h-margin), ((w-text_w)/2, h-text_h-margin)]
    bx, by = random.choice(positions)
    fx, fy = max(margin, min(bx, w - text_w - margin)), max(margin, min(by, h - text_h - margin))

    # ★ネオン＆ぷるぷるジェル文字描画★
    draw_neon_gloss_text(canvas, caption, font, fx, fy, c['text'], c['glow'])
    
    return canvas

# --- UI ---
if 'theme' not in st.session_state: st.session_state.theme = "姫ギャル (Pink)"
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 01. 素材えらび♡"); new_theme = st.radio("今日のバイブスは？🌈", list(THEME_CONFIG.keys()), key="rad")
    if new_theme != st.session_state.theme: st.session_state.theme = new_theme; st.rerun()
    inject_css(st.session_state.theme)
    custom_text = "";
    if "自由" in st.session_state.theme: custom_text = st.text_input("文字入力", "ウチら最強")
    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file); st.image(image, use_container_width=True)
        if st.button("💖 ギャル化スイッチON 💖"):
            loading_ph = st.empty(); msg = random.choice(THEME_CONFIG[st.session_state.theme]["loading"])
            loading_ph.markdown(f"""<div class="gal-loading"><div class="gal-loading-text">{msg}</div></div>""", unsafe_allow_html=True)
            time.sleep(3); caption = get_gal_caption(image, st.session_state.theme, custom_text)
            with st.spinner('AIが加工中...'): res = process_image(image, caption, st.session_state.theme)
            loading_ph.empty(); st.session_state.final = res; st.session_state.cap = caption
with col2:
    c = THEME_CONFIG[st.session_state.theme]["colors"]
    st.markdown(f"""<div class="custom-box"><h1 style="margin:0;font-size:3rem;">Gal-M@ker</h1><p style="font-weight: bold; color: {c['text']}">{st.session_state.theme} MODE</p></div>""", unsafe_allow_html=True)
    if 'final' in st.session_state: st.balloons(); st.image(st.session_state.final, use_container_width=True); st.success(f"テーマ: {st.session_state.cap}")
    else: st.info("👈 左側で画像を選んでスイッチON！")
