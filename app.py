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

# --- 4. テーマ定義 (魂のワードリスト) ---
THEME_CONFIG = {
    "姫ギャル (Pink)": {
        "colors": {
            "bg_base": "#fff0f5", "dot": "#ff69b4",
            "text": "#ff69b4", "outline": "#ffffff",
            "border": "#ff69b4", "shadow": "#ff1493",
            "img_text": "#ff1493", "img_stroke": "white"
        },
        "words": ["姫降臨", "お城に帰宅♡", "全世界一番可愛", "人形同盟", "王子様どこ？", "LOVE♡"],
        "loading": [
            "全人類、私に跪け！\nプリンセス・レボリューション！",
            "鏡よ鏡、今この瞬間だけは魔法をかけて♡\nラブリー・オーバーロード！",
            "可愛さは正義、ダサさは有罪！\n執行対象、発見♡",
            "お城の外も私の庭！\nロイヤル・ローズ・シャワー！"
        ]
    },
    "強めギャル (High)": {
        "colors": {
            "bg_base": "#000000", "dot": "#333333",
            "text": "#FFD700", "outline": "#000000",
            "border": "#FFD700", "shadow": "#FF0000",
            "img_text": "#FFD700", "img_stroke": "black"
        },
        "words": ["我等友情永久不滅", "喧嘩上等", "治安悪め", "卍最強卍", "鬼盛れ注意", "全国制覇"],
        "loading": [
            "気合注入、根性全開！\n地元最強の底力、見せたんで！",
            "売られた喧嘩は高値で買うよ？\nゴールデン・ナックル！",
            "黒肌はダイヤモンドの輝き！\n闇を切り裂くギャル魂！",
            "天上天下、唯我独尊！\n一番イケてるのはアタシらだ！"
        ]
    },
    "Y2K (Cyber)": {
        "colors": {
            "bg_base": "#e0ffff", "dot": "#0000ff",
            "text": "#0000ff", "outline": "#ffffff",
            "border": "#0000ff", "shadow": "#00ffff",
            "img_text": "#00FFFF", "img_stroke": "#000080"
        },
        "words": ["ズッ友だよ！！", "激アツ🔥", "運命共同体", "あげぽよ⤴︎", "LOVExxx", "バリ3📡"],
        "loading": [
            "バリ3、激盛れ、バイブスMAX！\n届いて、私のテレパシー！",
            "過去も未来もウチらのもん！\nミレニアム・パラパラ・ダンス！",
            "デコ電チャージ、ストラップ装着！\n繋がれ、運命のチェーン！",
            "アゲアゲな世界にしちゃうよ？\nハイビスカス・タイフーン！"
        ]
    },
    "病みかわ (Emo)": {
        "colors": {
            "bg_base": "#1a001a", "dot": "#800080",
            "text": "#E6E6FA", "outline": "#4b0082",
            "border": "#9370db", "shadow": "#d8bfd8",
            "img_text": "#E6E6FA", "img_stroke": "black"
        },
        "words": ["虚無", "生きるの辛", "顔面国宝", "依存先→", "†昇天†", "鬱..."],
        "loading": [
            "現実なんていらない…\n夢の世界へ、オーバードーズ・マジック",
            "私の痛み、あなたにもあげる。\nジェラシー・インジェクション！",
            "愛してくれなきゃ呪っちゃうよ？\n束縛のレッド・リボン！",
            "生きるの辛いけど戦うの。\nメンタル・ブレイク・ヒーリング！"
        ]
    },
    "自由入力": {
        "colors": {
            "bg_base": "#ffffff", "dot": "#cccccc",
            "text": "#333333", "outline": "#ffffff",
            "border": "#333333", "shadow": "#000000",
            "img_text": "#FF00FF", "img_stroke": "white"
        },
        "words": ["最強卍"],
        "loading": ["Now Loading...", "Please Wait...", "Processing...", "Almost Done..."]
    }
}

# --- 5. CSS注入 ---
def inject_css(theme):
    c = THEME_CONFIG[theme]["colors"]
    deco_color = c['deco'].replace("#", "%23") if 'deco' in c else c['border'].replace("#", "%23")
    star_svg = f"""url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50"><path d="M25 0 L30 18 L50 18 L35 30 L40 50 L25 38 L10 50 L15 30 L0 18 L20 18 Z" fill="none" stroke="{deco_color}" stroke-width="2" stroke-linejoin="round" /></svg>')"""
    outline = c['outline']
    
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
        
        h1, h2, h3, p, div, label, span, [data-testid="stMarkdownContainer"] p {{
            color: {c['text']} !important;
            text-shadow: 1.5px 1.5px 0 {outline}, -1.5px -1.5px 0 {outline}, -1.5px 1.5px 0 {outline}, 1.5px -1.5px 0 {outline}, 4px 4px 0px {c['shadow']} !important;
            letter-spacing: 1px; font-weight: 900 !important;
        }}
        h1 {{ font-size: 3.5rem !important; transform: rotate(-3deg); margin-bottom: 20px !important; -webkit-text-stroke: 2px {outline}; }}
        .stRadio label p {{ font-size: 1.2rem !important; }}
        .custom-box {{ border: 3px dashed {c['border']}; background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 8px 8px 0px rgba(0,0,0,0.1); }}
        .stButton > button {{
            background: linear-gradient(180deg, #ffffff 0%, {c['shadow']} 100%) !important; background-color: white !important;
            color: {c['text']} !important; border: 3px solid {c['text']} !important; border-radius: 50px !important;
            box-shadow: 0 6px 0 {c['text']} !important; font-size: 1.4rem !important; transition: all 0.1s; font-weight: bold;
        }}
        .stButton > button:active {{ transform: translateY(4px); box-shadow: 0 2px 0 {c['text']} !important; }}
        .marquee-container {{ position: fixed; top: 0; left: 0; width: 100%; background: {c['border']}; z-index: 9999; overflow: hidden; white-space: nowrap; padding: 8px 0; font-size: 16px; border-bottom: 3px solid white; }}
        .marquee-content {{ display: inline-block; animation: marquee 15s linear infinite; color: white !important; text-shadow: 2px 2px 0 #000 !important; font-weight: bold; }}
        @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}

        /* 変身バンク風ローディング */
        @keyframes flash {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
        .gal-loading {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 999999;
            background-color: rgba(0,0,0,0.9); /* 背景を暗くして文字を目立たせる */
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            padding: 20px; text-align: center;
        }}
        .gal-loading-text {{
            font-family: 'Potta One', sans-serif;
            font-size: 2rem; /* スマホでも入るサイズ */
            line-height: 1.5;
            font-weight: 900;
            color: #fff !important;
            text-shadow: 0 0 10px {c['text']}, 0 0 20px {c['text']} !important; /* 発光表現 */
            animation: flash 0.5s infinite;
            white-space: pre-wrap; /* 改行を反映 */
        }}
    </style>
    <div class="marquee-container"><div class="marquee-content">Welcome to Gal-M@ker ... Powered by Love Loop Inc ... HEISEI RETRO STYLE ... Make it KAWAII ... {theme} MODE ... 🌺🦋💖</div></div>
    """, unsafe_allow_html=True)

# --- 6. AI ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由" in theme_mode: return custom_text if custom_text else "最強卍"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        slang_guide = f"テーマは「{theme_mode}」。必ず以下のリストにあるような雰囲気の言葉を選んで。リスト: {THEME_CONFIG[theme_mode]['words']}"
        prompt = f"この画像を見て、平成ギャル雑誌のキャッチコピーをつけて。{slang_guide} 10文字以内。令和言葉禁止。"
        response = model.generate_content([prompt, image])
        return response.text.strip()
    except Exception as e:
        # AIエラー時はリストからランダム選出
        return random.choice(THEME_CONFIG[theme_mode]["words"])

# --- 7. 画像加工 ---
def process_image(image, caption, theme_mode):
    c = THEME_CONFIG[theme_mode]["colors"]
    img = image.convert("RGB"); img = ImageEnhance.Brightness(img).enhance(1.15)
    w, h = img.size; canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    
    try:
        if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
            from rembg import remove
            fg = remove(img).convert("RGBA");
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs:
                bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h));
                canvas.paste(bg, (0,0));
            canvas.paste(fg, (0,0), fg);
        else: canvas.paste(img.convert("RGBA"), (0,0));
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
    
    tc = c['img_text']; sc = c['img_stroke']
    
    # 文字（二重フチ風に描画）
    # 1. 太い外枠
    draw.text((w/10, h/1.4), caption, font=font, fill=sc, stroke_width=10, stroke_fill=sc)
    # 2. 本体
    draw.text((w/10, h/1.4), caption, font=font, fill=tc)
    
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
            loading_ph = st.empty()
            loading_messages = THEME_CONFIG[st.session_state.theme]["loading"]
            
            # ★変身バンク演出★
            # ランダムに1つ選んで表示（長めの文章も読めるように時間を取る）
            msg = random.choice(loading_messages)
            
            # 背景を暗くして、文字を発光させる演出
            loading_ph.markdown(f"""
            <div class="gal-loading">
                <div class="gal-loading-text">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(3) # 3秒間、変身セリフを見せつける！
            
            caption = get_gal_caption(image, st.session_state.theme, custom_text)
            res = process_image(image, caption, st.session_state.theme)
            
            loading_ph.empty()
            st.session_state.final = res
            st.session_state.cap = caption

with col2:
    c = THEME_CONFIG[st.session_state.theme]["colors"]
    st.markdown(f"""
    <div class="custom-box">
        <h1 style="margin:0;font-size:3rem;">Gal-M@ker</h1>
        <p style="font-weight: bold; color: {c['text']}">{st.session_state.theme} MODE</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'final' in st.session_state:
        st.balloons()
        st.image(st.session_state.final, use_container_width=True)
        st.success(f"テーマ: {st.session_state.cap}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
