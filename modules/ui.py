"""Общие UI-хелперы для задач ГКО.

Единый паттерн для всех задач:
- кнопка «РАССЧИТАТЬ» считает результат только по нажатию и замораживает его
  в снимок (session_state), чтобы он не пересчитывался сам при правке полей;
- «Пример» только подставляет данные (через clear_result результат прячется,
  пока пользователь снова не нажмёт РАССЧИТАТЬ).
"""
import streamlit as st


def calc_gate(task_id: str, compute_fn, *, prompt: str | None = None):
    """Кнопка РАССЧИТАТЬ + заморозка результата в снимок.

    task_id     — префикс ключей задачи (напр. "v11");
    compute_fn  — функция без аргументов, вызывается ТОЛЬКО по нажатию кнопки,
                  её возврат сохраняется как результат;
    prompt      — подсказка, показываемая пока расчёта ещё не было.

    Возвращает текущий снимок результата или None (если ещё не считали).
    """
    res_key = f"{task_id}_res"
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    if mid.button("РАССЧИТАТЬ", key=f"{task_id}_calc_btn", type="primary",
                  use_container_width=True):
        st.session_state[res_key] = compute_fn()

    res = st.session_state.get(res_key)
    if res is None and prompt:
        st.info(prompt)
    return res


def clear_result(task_id: str):
    """Сбросить снимок результата задачи (вызывать при подстановке «Примера»)."""
    st.session_state.pop(f"{task_id}_res", None)


def render_stub(task_id: str, title: str):
    """Единый каркас для ещё не наполненной задачи: заголовок + кнопка РАССЧИТАТЬ.

    Кнопка присутствует во всех задачах для единообразия; пока формулы не заданы,
    по нажатию показывается пометка «в разработке»."""
    st.subheader(title)
    st.caption("Модуль в разработке — расчёт появится после добавления формул "
               "по методике (Приложение В).")
    res = calc_gate(task_id, lambda: {"stub": True},
                    prompt="Нажмите «РАССЧИТАТЬ» (формулы для этой задачи ещё не заданы).")
    if res is not None:
        st.warning("Формулы для этой задачи ещё не заданы. "
                   "Пришлите их — и расчёт появится здесь.")
