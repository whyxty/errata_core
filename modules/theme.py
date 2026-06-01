"""Тема StimCore — светлая тема (UI Kit) для Streamlit-приложения ГКО.

Палитра и компоненты соответствуют макету «StimCore App UI Kit»:
светлый фон, спокойный индиго-акцент, мягкие тени, Inter + JetBrains Mono.
Применяется через `apply_theme()` сразу после st.set_page_config().
"""
import streamlit as st


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
html, body, [class*="st-"], .stApp {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans);
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
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
h2 {{ font-size: 18px !important; }}
h3 {{
    font-size: 13px !important; color: var(--text-3) !important;
    text-transform: uppercase; letter-spacing: 0.04em !important;
    font-weight: 600 !important;
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
    border-right: 1px solid var(--border);
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
/* степперы number_input */
.stNumberInput button {{
    background: var(--bg-subtle) !important;
    border-color: var(--border-strong) !important;
    color: var(--text-2) !important;
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

/* ─── buttons ─── */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{
    height: 38px !important;
    padding: 0 18px !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--sans) !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    border: 1px solid transparent !important;
    transition: background .12s, border-color .12s, box-shadow .12s, transform .06s !important;
    box-shadow: none !important;
}}
.stButton button:active {{ transform: translateY(0.5px) !important; }}
/* primary — индиго filled */
.stButton button[kind="primary"], button[kind="primary"] {{
    background: var(--accent) !important;
    color: #fff !important;
    border: 1px solid var(--accent) !important;
    box-shadow: var(--sh-sm) !important;
    text-shadow: none !important;
}}
.stButton button[kind="primary"]:hover, button[kind="primary"]:hover {{
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    color: #fff !important;
}}
/* secondary — ghost bordered */
.stButton button[kind="secondary"], button[kind="secondary"] {{
    background: var(--bg) !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border-strong) !important;
    text-shadow: none !important;
}}
.stButton button[kind="secondary"]:hover, button[kind="secondary"]:hover {{
    background: var(--bg-subtle) !important;
    color: var(--text) !important;
    border-color: var(--border-strong) !important;
}}
.stButton button:focus-visible {{
    outline: none !important;
    box-shadow: var(--ring) !important;
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
    padding: 4px 2px 16px; margin-bottom: 18px;
    border-bottom: 1px solid var(--border);
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="
            width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0;
            background: var(--accent); display: grid; place-items: center;
            box-shadow: var(--sh-sm);
        "><svg width="17" height="17" viewBox="0 0 24 24" fill="none"
               xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M12 2.5 21.5 12 12 21.5 2.5 12 12 2.5Z"
                  fill="#fff" stroke="#fff" stroke-width="1.5"
                  stroke-linejoin="round"/>
        </svg></div>
        <div>
            <div style="
                font-family: var(--sans); font-size: 16px; font-weight: 600;
                color: var(--text); letter-spacing: -0.01em; line-height: 1.1;
            ">{title}</div>
            <div style="
                font-family: var(--mono); font-size: 10px; font-weight: 500;
                color: var(--text-3); letter-spacing: 0.08em; text-transform: uppercase;
                margin-top: 3px;
            ">{subtitle}</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="
            font-family: var(--mono); font-size: 11px; color: var(--text-3);
            background: var(--bg-subtle); border: 1px solid var(--border);
            border-radius: 20px; padding: 3px 10px;
        ">v0.1 · streamlit</div>
        <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-2);">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: var(--green); display: inline-block;"></span>
            online
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)
