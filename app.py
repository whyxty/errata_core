"""Главный Streamlit-файл калькулятора глинокислотной обработки (ГКО)."""
import streamlit as st

from modules.constants import reset_to_default, empty_config
from modules.theme import apply_theme, stimcore_header
from modules.tasks import (
    task_v11, task_v12, task_v13, task_v14, task_v15,
    task_v8, task_v16, task_v17,
)

st.set_page_config(page_title="StimCore — ГКО", page_icon="◆", layout="wide")
apply_theme()

# Состояние констант — при первом запуске пусто
if "constants" not in st.session_state:
    st.session_state["constants"] = empty_config()

stimcore_header("StimCore", "Глинокислотная обработка")

# ───────────────────────── НАВИГАЦИЯ (pipeline) ─────────────────────────
PREP_PAGES = [
    "Месторождение",
]
TASK_PAGES = [
    "В.11 · Рецептура",
    "В.12 · Длит. реакции ГКР",
    "В.13 · Зона растворения",
    "В.14 · Растворённая порода",
    "В.15 · Пористость",
    "В.8 · Проницаемость",
    "В.16 · Эффективность",
    "В.17 · Реагенты, объёмы",
]
ALL_PAGES = PREP_PAGES + TASK_PAGES

if "page" not in st.session_state:
    st.session_state["page"] = PREP_PAGES[0]

# Отложенный переход (кнопки «Далее» внутри страниц)
_pending = st.session_state.pop("_pending_page", None)
if _pending in ALL_PAGES:
    st.session_state["page"] = _pending


def _on_prep():
    if st.session_state["_radio_prep"] is not None:
        st.session_state["page"] = st.session_state["_radio_prep"]


def _on_tasks():
    if st.session_state["_radio_tasks"] is not None:
        st.session_state["page"] = st.session_state["_radio_tasks"]


st.sidebar.markdown("### ◆ STIMCORE · ГКО")
page = st.session_state["page"]

st.sidebar.markdown("##### ПОДГОТОВКА")
st.sidebar.radio(
    "Подготовка", PREP_PAGES,
    index=PREP_PAGES.index(page) if page in PREP_PAGES else None,
    key="_radio_prep", on_change=_on_prep,
    label_visibility="collapsed",
)

st.sidebar.markdown("##### ЗАДАЧИ ГКО")
st.sidebar.radio(
    "Задачи ГКО", TASK_PAGES,
    index=TASK_PAGES.index(page) if page in TASK_PAGES else None,
    key="_radio_tasks", on_change=_on_tasks,
    label_visibility="collapsed",
)

page = st.session_state["page"]


# ───────────────────────── РАЗДЕЛ «МЕСТОРОЖДЕНИЕ» ─────────────────────────
def render_constants_ui():
    import pandas as pd
    st.header("🛠 Месторождение (константы)")
    cfg = st.session_state["constants"]

    cfg["field_name"] = st.text_input("Название профиля месторождения",
                                      value=cfg.get("field_name", ""))

    with st.expander("Кинетика реакции (α)", expanded=True):
        rk = cfg["reaction_kinetics"]
        rk["alpha_kgo"] = st.number_input(
            "α в k_г.о = exp(−α·r)", value=float(rk["alpha_kgo"]), step=0.01,
            help="Для Предкарпатья = 0.1")
        st.caption(rk.get("comment_alpha", ""))

    with st.expander("Свойства породы (диапазоны)"):
        rp = cfg["rock_properties"]
        c1, c2, c3 = st.columns(3)
        rp["rho_sk_default"] = c1.number_input("ρ_ск default, кг/м³", value=float(rp["rho_sk_default"]), step=10.0)
        rp["rho_p_default"]  = c2.number_input("ρ_п default, кг/м³",  value=float(rp["rho_p_default"]),  step=10.0)
        rp["k_mg_default"]   = c3.number_input("k_mg default", value=float(rp["k_mg_default"]), step=0.05)
        rp["R_mg_min"]       = c1.number_input("R_mg min, кг/(м³·экв)", value=float(rp["R_mg_min"]), step=1e-6, format="%.7f")
        rp["R_mg_max"]       = c2.number_input("R_mg max, кг/(м³·экв)", value=float(rp["R_mg_max"]), step=1e-6, format="%.7f")
        rp["R_mg_default"]   = c3.number_input("R_mg default, кг/(м³·экв)", value=float(rp["R_mg_default"]), step=1e-6, format="%.7f")

    with st.expander("Коэффициенты растворимости породы"):
        d = cfg["dissolution_coefficients"]
        c1, c2 = st.columns(2)
        d["a_gl_clay"]     = c1.number_input("a_гл — доля глин в ГКР (DG_g = a·C_гл + b·C_к)", value=float(d["a_gl_clay"]), step=0.05)
        d["b_k_carbonate"] = c2.number_input("b_к — доля карбонатов в ГКР", value=float(d["b_k_carbonate"]), step=0.05)
        c1, c2 = st.columns(2)
        d["a_clay_skr"]      = c1.number_input("a (СКР, для оценки СКР-стадии)", value=float(d["a_clay_skr"]), step=0.05)
        d["b_carbonate_skr"] = c2.number_input("b (СКР)", value=float(d["b_carbonate_skr"]), step=0.05)
        st.caption(d.get("comment", ""))

    with st.expander("Регрессии k₀(m₀) — табл. В.11"):
        for KL in range(1, 6):
            key = f"KL_{KL}"
            r = cfg["permeability_regressions"][key]
            c1, c2 = st.columns(2)
            r["A"] = c1.number_input(f"{key} A", value=float(r["A"]), format="%.3e", key=f"reg_A_{KL}")
            r["B"] = c2.number_input(f"{key} B", value=float(r["B"]), step=0.01, key=f"reg_B_{KL}")

    with st.expander("k_s* = A·exp(B·C_к) (В.44)"):
        ps = cfg["permeability_change_after_sko"]
        c1, c2 = st.columns(2)
        ps["A"] = c1.number_input("A (k_s*)", value=float(ps["A"]), step=0.05)
        ps["B"] = c2.number_input("B (k_s*)", value=float(ps["B"]), step=0.01)

    with st.expander("Таблица В.20 — диффузия HF D_г(C_HF)"):
        df = pd.DataFrame(cfg["hf_diffusion_table"]["rows"])
        edited = st.data_editor(df, num_rows="dynamic", key="cfg_b20_editor",
                                use_container_width=True)
        cfg["hf_diffusion_table"]["rows"] = edited.to_dict("records")

    with st.expander("Таблица В.15 — число обработок N_ко → y (% HF)"):
        st.caption(cfg["n_ko_table"].get("comment", ""))
        df = pd.DataFrame(cfg["n_ko_table"]["rows"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    left, _, right = st.columns([2, 6, 2])
    if left.button("ПРИМЕР", use_container_width=True, key="btn_example", type="secondary"):
        st.session_state["constants"] = reset_to_default()
        st.rerun()
    if right.button("ДАЛЕЕ  →", use_container_width=True, key="btn_next", type="primary"):
        st.session_state["_pending_page"] = "В.11 · Рецептура"
        st.rerun()


# ───────────────────────── РОУТИНГ ЗАДАЧ ─────────────────────────
TASK_RENDERERS = {
    "В.11 · Рецептура":          task_v11.render,
    "В.12 · Длит. реакции ГКР":  task_v12.render,
    "В.13 · Зона растворения":   task_v13.render,
    "В.14 · Растворённая порода":task_v14.render,
    "В.15 · Пористость":         task_v15.render,
    "В.8 · Проницаемость":       task_v8.render,
    "В.16 · Эффективность":      task_v16.render,
    "В.17 · Реагенты, объёмы":   task_v17.render,
}

cfg = st.session_state["constants"]
if page == "Месторождение":
    render_constants_ui()
elif page in TASK_RENDERERS:
    TASK_RENDERERS[page](cfg)

st.sidebar.markdown("---")
st.sidebar.caption("Литература: Приложение В — методика проектирования КО (ветка ГКО: СКР → ГКР).")
