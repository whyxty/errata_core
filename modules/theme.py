"""Тема StimCore — светлая тема (UI Kit) для Streamlit-приложения ГКО.

Палитра и компоненты соответствуют макету «StimCore App UI Kit»:
светлый фон, спокойный индиго-акцент, мягкие тени, Inter + JetBrains Mono.
Применяется через `apply_theme()` сразу после st.set_page_config().
"""
import base64
import io
from functools import lru_cache
from pathlib import Path

import streamlit as st

ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "icon.png"


@lru_cache(maxsize=1)
def icon_data_uri(px: int = 96) -> str:
    """PNG-иконку приложения → data-URI (с уменьшением до px для лёгкости)."""
    try:
        raw = ICON_PATH.read_bytes()
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(raw)).convert("RGBA")
            im.thumbnail((px, px), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            raw = buf.getvalue()
        except Exception:
            pass
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    except Exception:
        return ""


# ──────── Дизайн-токены (StimCore UI Kit, light) ────────
TOKENS = {
    "bg":            "#ffffff",
    "bg_subtle":     "#f7f8fa",   # sidebar, hover fills
    "bg_sunken":     "#f1f3f5",   # table header, pressed
    "bg_tint":       "#fbfbfc",
    "border":        "#e8eaed",
    "border_strong": "#d8dce0",
    "text":          "#16181d",
    "text2":         "#5b6472",
    "text3":         "#8b929e",
    "accent":        "#3b5bdb",
    "accent_hover":  "#2f4ec0",
    "accent_soft":   "#eef1fd",
    "accent_border": "#d6deff",
    "green":         "#16a34a",
    "green_soft":    "#ecfdf3",
    "orange":        "#d97706",
    "orange_soft":   "#fff7ed",
    "red":           "#dc2626",
    "red_soft":      "#fef2f2",
    "sans":          "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "mono":          "'JetBrains Mono', 'SF Mono', Consolas, Menlo, monospace",
}


_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
:root {{
    --bg: {bg};
    --bg-subtle: {bg_subtle};
    --bg-sunken: {bg_sunken};
    --bg-tint: {bg_tint};
    --border: {border};
    --border-strong: {border_strong};
    --text: {text};
    --text-2: {text2};
    --text-3: {text3};
    --accent: {accent};
    --accent-hover: {accent_hover};
    --accent-soft: {accent_soft};
    --accent-border: {accent_border};
    --green: {green};
    --green-soft: {green_soft};
    --orange: {orange};
    --orange-soft: {orange_soft};
    --red: {red};
    --red-soft: {red_soft};
    --sans: {sans};
    --mono: {mono};
    --r-sm: 6px; --r-md: 8px; --r-lg: 10px; --r-xl: 12px;
    --sh-sm: 0 1px 2px rgba(16,24,40,0.05);
    --sh-md: 0 1px 3px rgba(16,24,40,0.07), 0 1px 2px rgba(16,24,40,0.04);
    --sh-lg: 0 6px 16px rgba(16,24,40,0.08), 0 2px 4px rgba(16,24,40,0.04);
    --ring: 0 0 0 3px var(--accent-soft);
}}

/* ─── глобально ─── */
html, body, .stApp {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans);
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}}
/* только шрифт для элементов Streamlit — БЕЗ принудительного фона и цвета,
   иначе обёртка кнопки красится белым/тёмным поверх градиента и текста */
[class*="st-"] {{
    font-family: var(--sans);
}}
.stApp {{ background: var(--bg) !important; }}

/* ширина и отступы основной области */
.block-container {{
    max-width: 920px !important;
    padding-top: 1.4rem !important;
    padding-bottom: 4rem !important;
}}

/* ─── Material Symbols / иконки Streamlit ─── */
.material-icons, .material-icons-outlined,
[class*="material-symbols"],
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
[data-testid*="Icon"] svg {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
    font-weight: normal !important; font-style: normal !important;
    letter-spacing: normal !important; text-transform: none !important;
    white-space: nowrap !important; direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
}}

/* ─── скроллбары ─── */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: #d8dce0; border-radius: 6px; border: 3px solid var(--bg); }}
::-webkit-scrollbar-thumb:hover {{ background: #c2c8cf; }}

/* ─── заголовки ─── */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--sans) !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
    font-weight: 700 !important;
}}
h1 {{ font-size: 26px !important; }}
h2 {{ font-size: 20px !important; }}
h3 {{ font-size: 22px !important; color: var(--text) !important;
      letter-spacing: -0.02em !important; font-weight: 700 !important; }}
h4 {{ font-size: 15px !important; color: var(--text) !important;
      font-weight: 600 !important; }}
/* секционные подписи (#####) — мелкий серый капс */
h5, h6 {{
    font-size: 12px !important; color: var(--text-3) !important;
    text-transform: uppercase; letter-spacing: 0.04em !important;
    font-weight: 600 !important; margin: 4px 0 6px !important;
}}

/* подзаголовки st.subheader */
.stApp h2[class*="StyledHeader"], .stApp [data-testid="stHeading"] h2 {{
    color: var(--text) !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}}

/* ─── caption / Markdown ─── */
[data-testid="stMarkdownContainer"] p, .stMarkdown p {{
    color: var(--text-2) !important;
    font-size: 14px;
    line-height: 1.55;
}}
[data-testid="stCaptionContainer"], small {{
    color: var(--text-3) !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
}}

/* код / inline */
code {{
    background: var(--bg-subtle) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border) !important;
    border-radius: 5px;
    padding: 1px 6px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
}}

/* ─── sidebar ─── */
[data-testid="stSidebar"] {{
    background: var(--bg-subtle) !important;
    border-right: 1px solid var(--border-strong);
}}
/* ручка изменения ширины сайдбара — всегда видимая линия + грип по центру */
[data-testid="stSidebar"] div[style*="col-resize"] > div {{
    background: #b8bec6 !important;
    width: 3px !important;
    height: 100% !important;
    margin: 0 auto !important;
    opacity: 1 !important;
    transition: background .12s, width .12s;
}}
[data-testid="stSidebar"] div[style*="col-resize"]:hover > div {{
    background: var(--accent) !important;
    width: 4px !important;
}}
[data-testid="stSidebar"] div[style*="col-resize"]::after {{
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 6px; height: 46px;
    border-radius: 3px;
    background: var(--text-3);
    box-shadow: var(--sh-sm);
    z-index: 2;
    transition: background .12s, height .12s;
}}
[data-testid="stSidebar"] div[style*="col-resize"]:hover::after {{
    background: var(--accent);
    height: 64px;
}}
[data-testid="stSidebar"] .stMarkdown h3 {{
    font-size: 14px !important; font-weight: 600 !important;
    color: var(--text) !important; letter-spacing: -0.01em !important;
    text-transform: none !important; margin: 2px 0 6px !important;
}}
[data-testid="stSidebar"] .stMarkdown h5 {{
    font-size: 11px !important; font-weight: 600 !important;
    color: var(--text-3) !important; letter-spacing: 0.04em !important;
    text-transform: uppercase; margin: 14px 0 2px !important;
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] {{ gap: 1px !important; }}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label {{
    font-family: var(--sans) !important;
    font-size: 13px !important;
    color: var(--text-2) !important;
    position: relative;
    padding: 7px 8px 7px 22px !important;
    border-radius: var(--r-sm);
    transition: background .12s, color .12s;
}}
/* tick-кружок слева */
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label::before {{
    content: ""; position: absolute; left: 8px; top: 50%;
    transform: translateY(-50%); width: 5px; height: 5px;
    border-radius: 50%; background: var(--border-strong);
    transition: background .12s;
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:hover {{
    background: #eceef1; color: var(--text) !important;
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:hover::before {{
    background: var(--text-3);
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:has(input:checked) {{
    background: var(--accent-soft); color: var(--accent) !important; font-weight: 600;
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:has(input:checked)::before {{
    background: var(--accent);
}}
/* спрятать дефолтный radio-кружок */
[data-testid="stSidebar"] [class*="stRadio"] [data-baseweb="radio"] > div:first-child {{
    display: none !important;
}}

/* ─── number/text input ─── */
.stNumberInput input, .stTextInput input, .stTextArea textarea {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--mono) !important;
    font-weight: 500;
    font-size: 13px !important;
    transition: border-color 0.12s, box-shadow 0.12s;
}}
.stNumberInput input:focus, .stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: var(--ring) !important;
    outline: none !important;
}}
.stNumberInput label, .stTextInput label, .stTextArea label,
.stSelectbox label, .stCheckbox label, .stRadio label, .stSlider label {{
    font-family: var(--sans) !important;
    font-size: 12.5px !important;
    color: var(--text-2) !important;
    font-weight: 500 !important;
    text-transform: none !important;
}}
/* степперы number_input — тематический индиго-ховер */
.stNumberInput button,
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{
    background: var(--bg-subtle) !important;
    border-color: var(--border-strong) !important;
    color: var(--text-2) !important;
    transition: background .12s, color .12s !important;
}}
.stNumberInput button:hover,
[data-testid="stNumberInputStepUp"]:hover, [data-testid="stNumberInputStepDown"]:hover {{
    background: var(--accent) !important;
    color: #fff !important;
}}
.stNumberInput button:active,
[data-testid="stNumberInputStepUp"]:active, [data-testid="stNumberInputStepDown"]:active {{
    background: var(--accent-hover) !important;
}}

/* кнопки тулбара таблицы (data_editor): Add row и т.п. */
[data-testid="stBaseButton-elementToolbar"] {{
    border-radius: var(--r-sm) !important;
    color: var(--text-2) !important;
    transition: background .12s, color .12s !important;
}}
[data-testid="stBaseButton-elementToolbar"]:hover {{
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
}}

/* ─── selectbox ─── */
.stSelectbox > div > div {{
    background-color: var(--bg) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--r-sm) !important;
}}
.stSelectbox div[role="combobox"] {{
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-weight: 500 !important;
}}

/* ─── slider ─── */
.stSlider [data-baseweb="slider"] > div > div > div {{ background: var(--accent) !important; }}
.stSlider [data-baseweb="slider"] > div > div {{ background: var(--border-strong) !important; }}
.stSlider [role="slider"] {{
    background: #fff !important;
    border: 2px solid var(--accent) !important;
    box-shadow: var(--sh-sm) !important;
}}
.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"],
.stSlider [data-testid="stThumbValue"] {{
    font-family: var(--mono) !important; color: var(--text-3) !important;
}}

/* ─── checkbox ─── */
.stCheckbox [role="checkbox"][aria-checked="true"] {{
    background: var(--accent) !important; border-color: var(--accent) !important;
}}

/* ─── buttons (премиальный дизайн: градиент + блик + мягкая тень) ─── */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{
    position: relative !important;
    height: 38px !important;
    padding: 0 22px !important;
    border-radius: 9px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #fff;
    letter-spacing: 0.01em !important;
    text-transform: none !important;
    border: 1px solid transparent !important;
    overflow: hidden !important;
    isolation: isolate;
    transition: transform .22s cubic-bezier(.34,1.56,.64,1),
                box-shadow .22s ease, border-color .2s, color .2s, filter .2s !important;
    animation: moveInBottom .45s ease-out backwards;
}}
/* подпись кнопки наследует её цвет (иначе markdown-<p> делает текст серым) */
.stButton button *, .stDownloadButton button *, .stFormSubmitButton button * {{
    color: inherit !important;
    background: transparent !important;
}}
/* блик-«шайн», пробегающий при наведении */
.stButton button::before, .stDownloadButton button::before, .stFormSubmitButton button::before {{
    content: "";
    position: absolute;
    top: 0; left: -85%;
    width: 55%; height: 100%;
    background: linear-gradient(120deg, transparent 0%,
                rgba(255,255,255,0.45) 50%, transparent 100%);
    transform: skewX(-20deg);
    transition: left .6s ease;
    z-index: 1;
    pointer-events: none;
}}
.stButton button:hover::before, .stDownloadButton button:hover::before,
.stFormSubmitButton button:hover::before {{ left: 135%; }}

.stButton button:active, .stDownloadButton button:active, .stFormSubmitButton button:active {{
    transform: translateY(0) scale(0.98) !important;
}}

/* primary — индиго-градиент */
.stButton button[kind="primary"], button[kind="primary"] {{
    background: linear-gradient(135deg, #5570f2 0%, var(--accent) 55%, #2f4ec0 100%) !important;
    color: #fff !important;
    box-shadow: 0 2px 6px rgba(59,91,219,0.30),
                0 1px 2px rgba(16,24,40,0.12),
                inset 0 1px 0 rgba(255,255,255,0.18) !important;
}}
.stButton button[kind="primary"]:hover, button[kind="primary"]:hover {{
    color: #fff !important;
    transform: translateY(-2px) !important;
    filter: saturate(1.08) brightness(1.04) !important;
    box-shadow: 0 10px 24px rgba(59,91,219,0.42),
                0 3px 8px rgba(16,24,40,0.14),
                inset 0 1px 0 rgba(255,255,255,0.25) !important;
}}

/* secondary — белая с индиго-акцентом */
.stButton button[kind="secondary"], button[kind="secondary"] {{
    background: #fff !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent-border) !important;
    box-shadow: 0 1px 2px rgba(16,24,40,0.06) !important;
}}
.stButton button[kind="secondary"]:hover, button[kind="secondary"]:hover {{
    color: var(--accent-hover) !important;
    border-color: var(--accent) !important;
    background: var(--accent-soft) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 18px rgba(59,91,219,0.16),
                0 2px 5px rgba(16,24,40,0.08) !important;
}}
/* у белой кнопки блик мягче (на светлом фоне) */
.stButton button[kind="secondary"]::before {{
    background: linear-gradient(120deg, transparent 0%,
                rgba(59,91,219,0.12) 50%, transparent 100%) !important;
}}

.stButton button:focus-visible {{
    outline: none !important;
    box-shadow: var(--ring) !important;
}}
.stButton button:disabled, .stButton button[disabled] {{
    filter: grayscale(0.4) brightness(0.97) !important;
    opacity: 0.6 !important; transform: none !important;
    box-shadow: none !important; cursor: not-allowed !important;
}}

@keyframes moveInBottom {{
    0%   {{ opacity: 0; transform: translateY(18px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

/* ─── metric ─── */
[data-testid="stMetric"] {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 16px 18px;
    transition: box-shadow .15s, border-color .15s;
}}
[data-testid="stMetric"]:hover {{
    border-color: var(--border-strong);
    box-shadow: var(--sh-md);
}}
[data-testid="stMetricLabel"] {{
    color: var(--text-3) !important;
    font-family: var(--sans) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
}}
[data-testid="stMetricValue"] {{
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 26px !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: var(--sans) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}}

/* ─── expander → card ─── */
[data-testid="stExpander"] {{
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    margin-bottom: 12px;
    box-shadow: none !important;
    overflow: hidden;
}}
[data-testid="stExpander"] summary {{
    font-family: var(--sans) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    padding: 14px 18px !important;
    transition: background .12s;
}}
[data-testid="stExpander"] summary:hover {{
    background: var(--bg-tint); color: var(--text) !important;
}}
[data-testid="stExpander"][open] summary {{
    border-bottom: 1px solid var(--border);
    color: var(--text) !important;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{ padding: 18px !important; }}

/* ─── alerts ─── */
[data-testid="stAlert"] {{
    border-radius: var(--r-md) !important;
    border: 1px solid transparent !important;
    border-left-width: 1px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    padding: 11px 14px !important;
}}
div[data-testid="stAlert"][kind="info"] {{
    background: var(--accent-soft) !important; border-color: var(--accent-border) !important; color: #2a3a78 !important;
}}
div[data-testid="stAlert"][kind="success"] {{
    background: var(--green-soft) !important; border-color: #c7ecd5 !important; color: #14663b !important;
}}
div[data-testid="stAlert"][kind="warning"] {{
    background: var(--orange-soft) !important; border-color: #fcdcb3 !important; color: #8a4d09 !important;
}}
div[data-testid="stAlert"][kind="error"] {{
    background: var(--red-soft) !important; border-color: #f7cccc !important; color: #99231f !important;
}}
[data-testid="stAlert"] p {{ color: inherit !important; }}

/* ─── dataframe / table ─── */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    overflow: hidden;
}}
.dataframe, [data-testid="stDataFrame"] table {{
    font-family: var(--mono) !important;
    font-size: 12.5px !important;
    color: var(--text) !important;
}}
[data-testid="stDataFrame"] thead tr th {{
    background: var(--bg-subtle) !important;
    color: var(--text-3) !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 11px !important;
    font-weight: 600 !important;
    border-bottom: 1px solid var(--border) !important;
}}

/* ─── tabs ─── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--bg-subtle);
    border-radius: var(--r-md);
    padding: 4px; gap: 2px;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: var(--sans) !important;
    font-size: 13px !important;
    text-transform: none;
    color: var(--text-2) !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: var(--bg) !important;
    color: var(--accent) !important;
    box-shadow: var(--sh-sm);
}}

/* ─── plotly чарт → card ─── */
.stPlotlyChart, .js-plotly-plot {{
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg);
    padding: 6px;
}}

/* ─── LaTeX блоки → formula card ─── */
.katex {{ color: var(--text) !important; font-size: 14px !important; }}
.katex-display {{
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 14px 18px !important;
    margin: 14px 0 !important;
}}

/* ─── divider ─── */
hr {{ border-color: var(--border) !important; margin: 24px 0 !important; }}

/* ─── link ─── */
a {{ color: var(--accent) !important; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* ─── скрытие default Streamlit-меню ─── */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stStatusWidget"] {{ display: none; }}
</style>
""".format(**TOKENS)


def apply_theme():
    """Применяет визуальную тему StimCore (light) — вызывать сразу после st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)
    _apply_plotly_template()


def _apply_plotly_template():
    """Регистрирует и активирует светлый шаблон Plotly в стиле StimCore UI Kit."""
    try:
        import plotly.io as pio
        import plotly.graph_objects as go

        tpl = go.layout.Template()
        tpl.layout = dict(
            paper_bgcolor=TOKENS["bg"],
            plot_bgcolor=TOKENS["bg"],
            font=dict(family=TOKENS["sans"], size=12, color=TOKENS["text2"]),
            colorway=[
                TOKENS["accent"], TOKENS["green"], TOKENS["orange"],
                TOKENS["red"], "#7c3aed", "#0891b2", "#db2777",
            ],
            xaxis=dict(
                gridcolor=TOKENS["border"],
                linecolor=TOKENS["border_strong"],
                zerolinecolor=TOKENS["border_strong"],
                tickfont=dict(color=TOKENS["text3"], size=11, family=TOKENS["mono"]),
                title_font=dict(color=TOKENS["text2"], size=12),
            ),
            yaxis=dict(
                gridcolor=TOKENS["border"],
                linecolor=TOKENS["border_strong"],
                zerolinecolor=TOKENS["border_strong"],
                tickfont=dict(color=TOKENS["text3"], size=11, family=TOKENS["mono"]),
                title_font=dict(color=TOKENS["text2"], size=12),
            ),
            legend=dict(
                bgcolor=TOKENS["bg"],
                bordercolor=TOKENS["border"],
                borderwidth=1,
                font=dict(color=TOKENS["text2"], size=11),
            ),
            title=dict(font=dict(color=TOKENS["text"], size=14)),
            hoverlabel=dict(
                bgcolor=TOKENS["bg"],
                bordercolor=TOKENS["border_strong"],
                font=dict(color=TOKENS["text"], family=TOKENS["mono"]),
            ),
        )
        pio.templates["stimcore"] = tpl
        pio.templates.default = "stimcore"
    except Exception:
        pass


def stimcore_header(title: str = "StimCore", subtitle: str = "ГКО"):
    """Шапка приложения в стиле StimCore UI Kit (логотип + бренд + статус-чип)."""
    st.markdown(f"""
<div style="
    display: flex; align-items: center; justify-content: space-between;
    padding: 20px 2px 16px; margin-bottom: 20px;
    border-bottom: 1px solid var(--border); overflow: visible;
">
    <div style="display: flex; align-items: center; gap: 13px;">
        <img src="{icon_data_uri()}" alt="ErrataCore" style="
            width: 40px; height: 40px; border-radius: 9px; flex-shrink: 0;
            object-fit: cover; box-shadow: var(--sh-sm);
        "/>
        <div>
            <div style="
                font-family: var(--sans); font-size: 19px; font-weight: 700;
                color: var(--text); letter-spacing: -0.02em; line-height: 1.35;
                padding-top: 2px;
            ">{title}</div>
            <div style="
                font-family: var(--mono); font-size: 10px; font-weight: 500;
                color: var(--text-3); letter-spacing: 0.08em; text-transform: uppercase;
                margin-top: 3px;
            ">{subtitle}</div>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)
