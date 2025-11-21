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
    # クラウド(Streamlit Cloud)用
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # ローカル開発用（自分のキーを入れてね）
    GOOGLE_API_KEY = "AIzaSyCvvv_MEZ1zE6gdjmXrfT589tWWRTyhzvE"

# APIキーが正しく設定されているかチェック
if GOOGLE_API_KEY.startswith("AIza"):
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("🚨 APIキーが設定されてないか、間違ってるよ！")
    st.stop() # 処理をここで止める

# レイアウト設定（ワイド表示）
st.set_page_config(page_title="Gal-M@ker", page_icon="🦄", layout="wide")

# --- 🚑 エラー回避 ---
try:
    from rembg import remove
    CAN_REMOVE_BG = True
except:
    CAN_REMOVE_BG = False

# --- 🎨 テーマごとの色定義（バイブス） ---
def get_theme_styles(theme):
    # デフォルト（おまかせ・姫ギャル）
    colors = {
        "bg_color": "#ffeaf4", # 薄ピンク
        "bg_grad": "#ffb6c1",   # グラデ用
        "text_main": "#ff1493", # 濃いピンク
        "text_sub": "#ff69b4",
        "border": "#ff69b4",
        "button": "linear-gradient(180deg, #ffb6c1, #ff69b4)",
        "shadow": "#b0e0e6"    # 水色
    }
    
    if "強めギャル" in theme:
        colors = {
            "bg_color": "#000000", # 真っ黒
            "bg_grad": "#333333",  # ダークグレー
            "text_main": "#FFD700", # ゴールド
            "text_sub": "#ffffff", # 白
            "border": "#FFD700",
            "button": "linear-gradient(180deg, #ffd700, #b8860b)",
            "shadow": "#ff0000"    # 赤
        }
    elif "Y2K" in theme:
        colors = {
            "bg_color": "#e0ffff", # 薄い水色
            "bg_grad": "#00ffff",  # サイバー水色
            "text_main": "#0000ff", # 青
            "text_sub": "#000080",
            "border": "#0000ff",
            "button": "linear-gradient(180deg, #00ffff, #0000ff)",
            "shadow": "#ff00ff"    # ネオン紫
        }
    elif "病みかわ" in theme:
        colors = {
            "bg_color": "#1a001a", # ほぼ黒の紫
            "bg_grad": "#4b0082",  # インディゴ
            "text_main": "#e6e6fa", # ラベンダー
            "text_sub": "#dda0dd",
            "border": "#9370db",
            "button": "linear-gradient(180deg, #d8bfd8, #800080)",
            "shadow": "#000000"
        }
    
    return colors

# --- 💄 美肌＆プリクラ風フィルター ---
def apply_beauty_filter(img):
    img = img.convert("RGB")
    # 1. 肌を滑らかにする（ソフトフォーカス）
    smoothed_img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.blend(img, smoothed_img, 0.4)
    # 2. 美白効果（明るく飛ばす）
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.15)
    # 3. コントラスト調整（少しふんわりさせる）
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.95)
    # 4. 血色感（ピンクフィルター）
    r, g, b = img.split()
    r = r.point(lambda i: i * 1.05)
    img = Image.merge('RGB', (r, g, b))
    return img

# --- 関数: AIキャッチコピー（ここを修正！） ---
def get_gal_caption(image, theme_mode, custom_text):
    # 自由入力ならそれをそのまま返す
    if "自由入力" in theme_mode:
        return custom_text if custom_text else "最強卍"

    try:
        # モデルの準備
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 基本の指示
        base_prompt = "この画像を見て、平成のギャル雑誌の見出し風のキャッチコピーを考えて。10文字以内。"
        
        # テーマごとの追加指示
        style = ""
        if "強めギャル" in theme_mode:
            style = "オラオラ系、強気、『ウチら』『最強』『卍』を使って。黒ギャル風。"
        elif "姫ギャル" in theme_mode:
            style = "お姫様系、甘々、ハート多用、『ですわ』『〜み』『天使』を使って。ピンク系。"
        elif "Y2K" in theme_mode:
            style = "近未来、デジタル、英語混じり、クールに。『System』『Connect』『Link』など。"
        elif "病みかわ" in theme_mode:
            style = "少しダーク、意味深、メンヘラ気味。『...』『永遠』『愛』を使って。"
        else: # おまかせ
            style = "とにかくテンションMAXで、楽しそうな感じで。"

        # 指示を合体させる
        final_prompt = f"{base_prompt}\n条件: {style}"
        
        # AIに生成させる
        response = model.generate_content([final_prompt, image])
        return response.text.strip()
        
    except Exception as e:
        # エラーが起きたら、コンソールに原因を表示して、デフォルトの言葉を返す
        print(f"AI生成エラー: {e}")
        return "最強KAWAII宣言💖" # ← こればっかり出るのは、どこかでエラーになってる証拠

# --- 関数: 画像加工 ---
def apply_gal_effect_safe(base_img, caption_text, theme_mode):
    time.sleep(2) # 演出用ウェイト

    # 1. まず美肌にする
    base_img = apply_beauty_filter(base_img)
    
    width, height = base_img.size
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))

    # 2. 背景切り抜き＆合成（軽量化のため、失敗したらスキップ）
    bg_drawn = False
    if CAN_REMOVE_BG and os.path.exists("assets/bgs"):
        try:
            fg = remove(base_img).convert("RGBA")
            bgs = [f for f in os.listdir("assets/bgs") if not f.startswith('.')]
            if bgs:
                bg_file = random.choice(bgs)
                bg_img = Image.open(f"assets/bgs/{bg_file}").convert("RGBA")
                canvas.paste(bg_img.resize((width, height)), (0,0))
                canvas.paste(fg, (0,0), fg)
                bg_drawn = True
        except:
            pass
    
    # 背景が描けなかったら、元の写真をそのまま貼る
    if not bg_drawn:
        canvas.paste(base_img.convert("RGBA"), (0,0))

    # 3. フレーム合成
    frame_dir = "assets/frames"
    if os.path.exists(frame_dir) and len(os.listdir(frame_dir)) > 0:
        frames = [f for f in os.listdir(frame_dir) if not f.startswith('.')]
        if frames:
            fr_img = Image.open(os.path.join(frame_dir, random.choice(frames))).convert("RGBA")
            canvas = Image.alpha_composite(canvas, fr_img.resize((width, height)))

    # 4. スタンプ合成（エラー回避版）
    stamp_dir = "assets/stamps"
    if os.path.exists(stamp_dir) and len(os.listdir(stamp_dir)) > 0:
        stamps = [f for f in os.listdir(stamp_dir) if not f.startswith('.')]
        if stamps:
            for _ in range(random.randint(3, 5)):
                try:
                    stamp_name = random.choice(stamps)
                    stamp_img = Image.open(os.path.join(stamp_dir, stamp_name)).convert("RGBA")
                    # スマホ負荷軽減のため、切り抜きはスキップしてそのまま貼る
                    size = random.randint(int(width/6), int(width/3))
                    stamp_img = stamp_img.resize((size, size))
                    x = random.randint(0, width - size)
                    y = random.randint(0, height - size)
                    canvas.paste(stamp_img, (x, y), stamp_img)
                except:
                    pass

    # 5. 文字入れ（色をテーマに合わせる！）
    text_color = "#ff1493" # デフォルト（ピンク）
    stroke_color = "white"
    
    if "強めギャル" in theme_mode:
        text_color = "#FFD700" # ゴールド
        stroke_color = "black"
    elif "Y2K" in theme_mode:
        text_color = "#00FFFF" # サイバー水色
        stroke_color = "#000080" # ネイビー
    elif "病みかわ" in theme_mode:
        text_color = "#E6E6FA" # ラベンダー
        stroke_color = "black"

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
    # 縁取り
    draw.text((text_x, text_y), caption_text, font=font, fill=stroke_color, stroke_width=stroke_width, stroke_fill=stroke_color)
    # 本体
    draw.text((text_x, text_y), caption_text, font=font, fill=text_color)

    return canvas

# ==========================================
# 🚀 メイン処理（UIの構築）
# ==========================================

# 1. まずデフォルトのフォントCSSを読み込む
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&display=swap');
    html, body, [class*="css"] { font-family: 'Mochiy Pop One', sans-serif; }
</style>
""", unsafe_allow_html=True)

# 2. UI配置（ここが重要！先にラジオボタンを置く）
st.markdown("### 01. 素材えらび♡")

# ★ ここでラジオボタンを表示し、ユーザーの選択を受け取る
theme_mode = st.radio(
    "今日のバイブスは？🌈",
    ["姫ギャル (Pink)", "強めギャル (High)", "Y2K (Cyber)", "病みかわ (Emo)", "自由入力"],
    horizontal=True,
    key="theme_selector" # ユニークなキーを割り当てる
)

custom_text = ""
if "自由入力" in theme_mode:
    custom_text = st.text_input("好きな言葉（10文字以内）", "ウチら最強卍")

# 3. 選択されたテーマに基づいて、動的にCSSを生成する！
c = get_theme_styles(theme_mode)

# ★ 生成したCSSを、ページ全体に「強制的に」注入する
st.markdown(f"""
<style>
    /* アプリ全体の背景を強制的に変える */
    .stApp {{
        background-color: {c['bg_color']} !important;
        background-image:
            radial-gradient({c['bg_grad']} 20%, transparent 20%),
            radial-gradient({c['bg_grad']} 20%, transparent 20%) !important;
        background-size: 20px 20px !important;
        background-position: 0 0, 10px 10px !important;
        transition: background-color 0.3s, background-image 0.3s; /* ふわっと切り替える */
    }}
    
    /* テキストの色もテーマに合わせる */
    h1, h2, h3, p, label, span, div, .stMarkdown {{
        color: {c['text_main']} !important;
    }}
    
    /* タイトルの装飾 */
    h1.main-title {{
        text-shadow: 4px 4px 0px #fff, 6px 6px 0px {c['shadow']} !important;
        font-size: 4rem !important;
        transform: rotate(-3deg);
        padding-bottom: 20px;
        text-align: center;
        width: 100%;
    }}

    /* ヘッダーや結果表示の枠 */
    .custom-container {{
        background: rgba(255,255,255,0.6);
        border: 4px dotted {c['border']} !important;
        border-radius: 30px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }}

    /* ラジオボタンの文字 */
    .stRadio label p {{
        font-size: 18px !important;
        color: {c['text_main']} !important;
        font-weight: bold !important;
    }}

    /* ボタンの色 */
    .stButton > button {{
        background: {c['button']} !important;
        color: white !important;
        border: 4px solid #fff !important;
        border-radius: 50px !important;
        font-size: 24px !important;
        padding: 10px 30px !important;
        box-shadow: 0 6px 15px {c['text_main']}66 !important;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton > button:hover {{
        transform: scale(1.05);
    }}
</style>
""", unsafe_allow_html=True)

# --- ヘッダー表示（CSS適用後なので色が合う！）---
st.markdown(f"""
<div class="custom-container">
    <div style="font-size: 12px; opacity: 0.7; margin-bottom: 10px;">
        Welcome to Gal-M@ker ... {theme_mode} MODE ...
    </div>
    <h1 class="main-title">Gal-M@ker</h1>
    <div style="background: #fff; border: 2px dashed {c['border']}; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-top: 10px;">
        ✨ Powered by Love Loop Inc. ✨
    </div>
</div>
""", unsafe_allow_html=True)

# --- アップロードエリア ---
st.markdown("---")
uploaded_file = st.file_uploader("ここに写メを投げる！", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    st.markdown("### 02. 完成！！")
    
    if st.button('💖 ギャル化スイッチON 💖'):
        # ローディング演出（ここも色を合わせる）
        loading_placeholder = st.empty()
        loading_placeholder.markdown(f"""
        <style>
            @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 50% {{ transform: translate(-1px, 2px) rotate(-1deg); }} 100% {{ transform: translate(1px, -2px) rotate(-1deg); }} }}
            .gal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: {c['bg_color']}ee; z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(10px); }}
            .gal-loading-text {{ font-size: 40px; font-weight: 900; color: #fff; text-shadow: 2px 2px 0 {c['text_main']}, 2px 2px 10px {c['text_main']}; white-space: nowrap; animation: shake 0.5s infinite; }}
        </style>
        <div class="gal-overlay"><div class="gal-loading-text">⚡️ {theme_mode} 加工中 ⚡️</div></div>
        """, unsafe_allow_html=True)
        
        # AIに言葉を考えさせる
        gal_text = get_gal_caption(image, theme_mode, custom_text)
        # 画像を加工する（色情報も渡す）
        processed_image = apply_gal_effect_safe(image, gal_text, theme_mode)
        
        loading_placeholder.empty()
        st.balloons()
        st.image(processed_image, use_container_width=True)
        # 結果の文字色も合わせる
        st.markdown(f"""<div style="text-align: center; font-size: 24px; color: {c['text_main']}; font-weight: bold; margin-bottom: 10px;">テーマ：{gal_text}</div>""", unsafe_allow_html=True)

if not CAN_REMOVE_BG:
    st.info("💡 ヒント: サーバー負荷軽減のため、今は「デコモード」で動いてるよ！")
