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
    from rembg import remove # 念のためここに残しておく
    CAN_REMOVE_BG = False

# --- 4. テーマ定義 ---
THEME_CONFIG = {
    "姫ギャル (Pink)": {
        "colors": {"deco": "#ff69b4", "text": "#ff1493", "border": "#ff69b4", "shadow": "#ffb6c1"},
        "words": ["ジーザス✨", "姫降臨👑", "盛り盛り💖", "アゲ⤴︎", "小悪魔👿", "神室町系", "お水の花道", "Jesus!!"],
        "loading": ["リボン結び中...", "王子様待ち...", "魔法かけてる...", "キラキラ注入✨"]
    },
    "強めギャル (High)": {
        "colors": {"deco": "#FFD700", "text": "#FFD700", "border": "#FFD700", "shadow": "#FF0000"},
        "words": ["鬼盛れ👹", "パない🙌", "マジ神✨", "強め上等🔥", "気合い⚡️", "日サロ通い", "我等友情永久不滅", "全国制覇"],
        "loading": ["日サロで焼き中...", "パラパラ練習中...", "ジャージで集合...", "気合い注入中🔥"]
    },
    "Y2K (Cyber)": {
        "colors": {"deco": "#00ffff", "text": "#0000ff", "border": "#0000ff", "shadow": "#00ffff"},
        "words": ["バリ3📡", "Re:Re:", "No Data", "Cyber", "Techno", "センター問い合わせ", "着信アリ", "パケ死寸前"],
        "loading": ["赤外線通信中...", "センター問い合わせ...", "着うたDL中...", "パケ放題接続..."]
    },
    "病みかわ (Emo)": {
        "colors": {"deco": "#9370db", "text": "#e6e6fa", "border": "#9370db", "shadow": "#000000"},
        "words": ["永遠...", "愛して†", "救済求ム", "バグり中", "ぴえん🥺"],
        "loading": ["現実逃避中...", "薬飲んだ...", "通信エラー...", "闇の儀式†"]
    },
    "自由入力": {
        "colors": {"deco": "#aaaaaa", "text": "#333333", "border": "#333333", "shadow": "#000000"},
        "words": ["最強卍"],
        "loading": ["Now Loading...", "Please Wait...", "Processing...", "Almost Done..."]
    }
}

# --- 5. CSS注入 (フォント変更！) ---
def inject_css(theme):
    c = THEME_CONFIG[theme]["colors"]
    deco_color = c['deco'].replace("#", "%23")
    star_svg = f"""url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50"><path d="M25 0 L30 18 L50 18 L35 30 L40 50 L25 38 L10 50 L15 30 L0 18 L20 18 Z" fill="none" stroke="{deco_color}" stroke-width="2" stroke-linejoin="round" /></svg>')"""
    
    st.markdown(f"""
    <style>
        /* ★フォント変更：Mochiy Pop One -> Potta One (ぷっくり丸文字) ★ */
        @import url('https://fonts.googleapis.com/css2?family=Potta+One&display=swap');
        html, body, [class*="css"] {{ font-family: 'Potta One', sans-serif !important; }}
        
        /* 背景 */
        [data-testid="stAppViewContainer"] {{
            background-color: #f8f9fa !important;
            background-image: linear-gradient(to right, rgba(0,0,0,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.08) 1px, transparent 1px) !important;
            background-size: 25px 25px !important;
        }}
        [data-testid="stAppViewContainer"]::before {{ content: ""; position: fixed; top: 50px; left: 10px; width: 100px; height: 100px; background-image: {star_svg}; background-repeat: no-repeat; opacity: 0.7; pointer-events: none; }}
        [data-testid="stAppViewContainer"]::after {{ content: ""; position: fixed; bottom: 50px; right: 10px; width: 100px; height: 100px; background-image: {star_svg}; background-repeat: no-repeat; transform: rotate(20deg); opacity: 0.7; pointer-events: none; }}
        
        /* 文字色 */
        h1, h2, h3, p, div, label, span {{ color: {c['text']} !important; }}
        
        /* タイトル */
        h1 {{ text-shadow: 3px 3px 0px #fff, 5px 5px 0px {c['shadow']} !important; transform: rotate(-2deg); }}
        
        /* ボタン */
        .stButton > button {{
            background: linear-gradient(180deg, rgba(255,255,255,0.4), rgba(0,0,0,0.1)) !important; background-color: {c['border']} !important; color: white !important; border: 3px solid #fff !important; border-radius: 50px !important; box-shadow: 0 5px 15px {c['shadow']} !important; font-size: 1.2rem !important;
        }}

        /* コンテナ枠 */
        .custom-box {{ border: 3px dashed {c['border']}; background: rgba(255,255,255,0.9); border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 5px 5px 0px rgba(0,0,0,0.1); }}
        
        /* マーキー */
        .marquee-container {{ position: fixed; top: 0; left: 0; width: 100%; background: {c['border']}; color: white; z-index: 9999; overflow: hidden; white-space: nowrap; padding: 5px 0; font-size: 14px; }}
        .marquee-content {{ display: inline-block; animation: marquee 15s linear infinite; color: white; }}

        /* ローディング */
        @keyframes rainbow {{ 0% {{ background-color: #ff9a9e; }} 50% {{ background-color: #a18cd1; }} 100% {{ background-color: #ff9a9e; }} }}
        .gal-loading {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 999999; display: flex; flex-direction: column; justify-content: center; align-items: center; animation: rainbow 2s linear infinite; }}
        .gal-loading-text {{ font-size: 3rem; font-weight: 900; color: white; text-shadow: 4px 4px 0 #000; animation: shake 0.5s infinite; }}
    </style>
    <div class="marquee-container"><div class="marquee-content">Welcome to Gal-M@ker ... Powered by Love Loop Inc ... HEISEI RETRO STYLE ... Make it KAWAII ... {theme} MODE ... 🌺🦋💖</div></div>
    """, unsafe_allow_html=True)
    
    # サイドバーデバッグ（左のメニュー）
    if not GOOGLE_API_KEY.startswith("AIza"):
        st.sidebar.error("🚨 APIキーが設定されていません。AIは動作しません。")
    
    return c

# --- 6. AI & ロジック ---
def get_gal_caption(image, theme_mode, custom_text):
    if "自由入力" in theme_mode: return custom_text if custom_text else "最強卍"
    
    try:
        # まず最新版のflashを試す
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        slang_guide = ""
        if "姫" in theme_mode: slang_guide = "2005年頃のageha風。甘々でゴージャス。単語: ジーザス, 盛り, 姫"
        elif "強め" in theme_mode: slang_guide = "2000年頃のegg風。ガングロ系。単語: 鬼, パない, 強い"
        elif "Y2K" in theme_mode: slang_guide = "平成初期のガラケー・サイバー文化。単語: バリ3, 着信, デジ"
        elif "病み" in theme_mode: slang_guide = "前略プロフのポエム風。単語: 永遠, 孤独, 運命"
        
        prompt = f"この画像を見て、平成ギャル雑誌のキャッチコピーをつけて。{slang_guide} 10文字以内。令和言葉禁止。絵文字1つまで。"
        response = model.generate_content([prompt, image])
        return response.text.strip()
    except Exception as e:
        # AIが失敗したら、テーマに合った予備ワードを出す
        fallback_list = THEME_CONFIG[theme_mode]["words"]
        st.sidebar.warning(f"AI通信エラー発生。予備ワード使用。")
        return random.choice(fallback_list)

# --- 7. 画像加工 ---
def process_image(image, caption, theme_mode):
    c = THEME_CONFIG[theme_mode]["colors"]
    img = image.convert("RGB"); img = ImageEnhance.Brightness(img).enhance(1.15)
    w, h = img.size; canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    
    # 背景・スタンプ（ロジック変更なし）...
    try:
        from rembg import remove
        if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
            fg = remove(img).convert("RGBA");
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')];
            if bgs:
                bg = Image.open(f"assets/bgs/{random.choice(bgs)}").convert("RGBA").resize((w, h));
                canvas.paste(bg, (0,0));
            canvas.paste(fg, (0,0), fg);
        else: canvas.paste(img.convert("RGBA"), (0,0));
    except: canvas.paste(img.convert("RGBA"), (0,0))
    
    if os.path.exists("assets/stamps"):
        stamps = [f for f in os.listdir("assets/stamps") if not f.startswith('.')];
        if stamps:
            for _ in range(4):
                try:
                    s = Image.open(f"assets/stamps/{random.choice(stamps)}").convert("RGBA")
                    sz = random.randint(int(w/6), int(w/3));
                    canvas.paste(s.resize((sz, sz)), (random.randint(0, w-sz), random.randint(0, h-sz)), s.resize((sz, sz)))
                except: pass

    draw = ImageDraw.Draw(canvas);
    try: font = ImageFont.truetype("gal_font.ttf", int(w/7))
    except: font = ImageFont.load_default();
    
    # 文字色（テーマ依存）
    tc = c['text']; sc = "white"
    if "強め" in theme_mode: tc=c['text']; sc="black"
    elif "Y2K" in theme_mode: tc="#00FFFF"; sc="#000080"
    elif "病み" in theme_mode: tc="#E6E6FA"; sc="#000000"
    
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
    if "自由入力" in st.session_state.theme: custom_text = st.text_input("文字入力", "ウチら最強")

    uploaded_file = st.file_uploader("画像を選択", type=['jpg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        if st.button("💖 ギャル化スイッチON 💖"):
            loading_ph = st.empty()
            loading_messages = THEME_CONFIG[st.session_state.theme]["loading"]
            
            for msg in loading_messages[:3]:
                loading_ph.markdown(f"""<div class="gal-loading"><div class="gal-loading-text">{msg}</div><div style="font-size:20px; color:white; margin-top:10px;">Wait a sec...</div></div>""", unsafe_allow_html=True)
                time.sleep(0.8)
            
            caption = get_gal_caption(image, st.session_state.theme, custom_text)
            res = process_image(image, caption, st.session_state.theme)
            
            loading_ph.empty()
            st.session_state.final = res
            st.session_state.cap = caption

with col2:
    st.markdown(f"""<div class="custom-box"><h1 style="margin:0;font-size:3rem;color:{THEME_CONFIG[st.session_state.theme]['colors']['text']};">Gal-M@ker</h1><p style="color:{THEME_CONFIG[st.session_state.theme]['colors']['text']};">{st.session_state.theme} MODE</p></div>""", unsafe_allow_html=True)
    if 'final' in st.session_state:
        st.balloons()
        st.image(st.session_state.final, use_container_width=True)
        st.success(f"テーマ: {st.session_state.cap}")
    else:
        st.info("👈 左側で画像を選んでスイッチON！")
