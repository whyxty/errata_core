"""Главный Streamlit-файл калькулятора глинокислотной обработки (ГКО)."""
import streamlit as st

from modules.constants import reset_to_default
from modules.theme import apply_theme, stimcore_header
from modules.tasks import (
    task_v11, task_v12, task_v13, task_v14, task_v15,
    task_v8, task_v16, task_v17,
)

st.set_page_config(page_title="StimCore — ГКО", page_icon="◆", layout="wide")
apply_theme()

# Константы месторождения грузятся из gko_config.json (без экрана редактирования)
if "constants" not in st.session_state:
    st.session_state["constants"] = reset_to_default()

stimcore_header("StimCore", "Глинокислотная обработка")

# ───────────────────────── НАВИГАЦИЯ ─────────────────────────
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

if "page" not in st.session_state:
    st.session_state["page"] = TASK_PAGES[0]

# Отложенный переход (кнопки «Далее» внутри задач)
_pending = st.session_state.pop("_pending_page", None)
if _pending in TASK_PAGES:
    st.session_state["page"] = _pending


def _on_tasks():
    if st.session_state["_radio_tasks"] is not None:
        st.session_state["page"] = st.session_state["_radio_tasks"]


st.sidebar.markdown("### ◆ STIMCORE · ГКО")
page = st.session_state["page"]

st.sidebar.markdown("##### ЗАДАЧИ ГКО")
st.sidebar.radio(
    "Задачи ГКО", TASK_PAGES,
    index=TASK_PAGES.index(page) if page in TASK_PAGES else 0,
    key="_radio_tasks", on_change=_on_tasks,
    label_visibility="collapsed",
)

page = st.session_state["page"]


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
if page in TASK_RENDERERS:
    TASK_RENDERERS[page](cfg)

st.sidebar.markdown("---")
st.sidebar.caption("Литература: Приложение В — методика проектирования КО (ветка ГКО: СКР → ГКР).")
