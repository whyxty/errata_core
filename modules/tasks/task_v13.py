"""Задача В.10 — Объёмы продавочной и вытесняющей жидкости.

Методика (Приложение В):
    В.56  Vвтс = 1,2·Vз.рs                          — по объёму зоны растворения
    В.57  Vвтс = 0,3·Vks                            — оценка с запасом (если Vз.рs неизвестен)
    В.58  Vпрд = 0,785·[ dв²·Hн.о + (Dк² − dвн²)·(Hн.о − Hв.о) ]
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from modules.input_data import get_inputs


# Пример В.10.1 (из методички)
EXAMPLE_V10 = {
    "V_ks": 6.0, "V_zrs": 0.9,
    "H_no": 2823.0, "H_vo": 2733.0,
    "D_k": 0.124, "d_vn": 0.073, "d_v": 0.062,
}


# ─────────────────────── расчёт ───────────────────────
def solve(p: dict) -> dict:
    V_ks, V_zrs = p["V_ks"], p["V_zrs"]
    H_no, H_vo = p["H_no"], p["H_vo"]
    D_k, d_vn, d_v = p["D_k"], p["d_vn"], p["d_v"]

    # Вытесняющая жидкость
    V_vts_56 = 1.2 * V_zrs if V_zrs > 0 else None         # В.56
    V_vts_57 = 0.3 * V_ks if V_ks > 0 else None           # В.57
    if V_vts_56 is not None:
        V_vts, V_vts_src = V_vts_56, "по зоне растворения (В.56)"
    elif V_vts_57 is not None:
        V_vts, V_vts_src = V_vts_57, "оценка с запасом (В.57)"
    else:
        V_vts, V_vts_src = None, "—"

    # Продавочная жидкость (В.58)
    interval = max(H_no - H_vo, 0.0)
    tubing_term = (d_v ** 2) * H_no
    annulus_term = (D_k ** 2 - d_vn ** 2) * interval
    V_prd = 0.785 * (tubing_term + annulus_term) if (H_no > 0 and D_k > 0) else None

    return {
        "V_vts_56": V_vts_56, "V_vts_57": V_vts_57,
        "V_vts": V_vts, "V_vts_src": V_vts_src,
        "V_prd": V_prd, "interval": interval,
        "tubing_term": tubing_term, "annulus_term": annulus_term,
    }


# ─────────────────────── UI ───────────────────────
def _load_example():
    for k, v in EXAMPLE_V10.items():
        st.session_state[f"v13_{k}"] = v


def render(cfg: dict):
    inp = get_inputs()

    title_col, btn_col = st.columns([5, 1.3])
    title_col.subheader("Объёмы продавочной и вытесняющей жидкости")
    if btn_col.button("Пример В.10.1", key="ex_v13", type="secondary", use_container_width=True):
        _load_example(); st.rerun()

    st.caption("Определить объёмы продавочной и вытесняющей жидкости для кислотной обработки. "
               "Продавочная жидкость заменяет СКР в объёмах НКТ и эксплуатационной колонны в "
               "интервале перфорации; вытесняющая — перемещает СКР за пределы зоны растворения "
               "для полного использования химической активности кислоты.")

    with st.expander("📖 Формулы", expanded=False):
        st.latex(r"V_{\text{втс}} = 1{,}2\,V_{\text{з.р}s} \tag{В.56}")
        st.latex(r"V_{\text{втс}} = 0{,}3\,V_{ks} \quad(\text{с запасом, если }V_{\text{з.р}s}\text{ неизвестен}) \tag{В.57}")
        st.latex(r"V_{\text{прд}} = 0{,}785\left[\,d_{\text{в}}^2 H_{\text{н.о}} + "
                 r"(D_{\text{к}}^2 - d_{\text{вн}}^2)(H_{\text{н.о}} - H_{\text{в.о}})\,\right] \tag{В.58}")
        st.markdown("*dв, dвн — внутр./наруж. диаметр НКТ; Dк — внутр. диаметр ЭК; "
                    "Hн.о, Hв.о — глубина нижнего/верхнего отверстия перфорации.*")

    # ── инициализация (по умолчанию — из общих данных скважины) ──
    st.session_state.setdefault("v13_V_ks", 6.0)
    st.session_state.setdefault("v13_V_zrs", 0.9)
    st.session_state.setdefault("v13_H_no", float(inp.get("H_no") or 0.0) or 2823.0)
    st.session_state.setdefault("v13_H_vo", float(inp.get("H_vo") or 0.0) or 2733.0)
    st.session_state.setdefault("v13_D_k", float(inp.get("D_k") or 0.0) or 0.124)
    st.session_state.setdefault("v13_d_vn", float(inp.get("d_vn") or 0.0) or 0.073)
    st.session_state.setdefault("v13_d_v", float(inp.get("d_v") or 0.0) or 0.062)

    with st.expander("📥 Исходные данные", expanded=True):
        c1, c2 = st.columns(2)
        st.session_state["v13_V_ks"] = c1.number_input(
            "Vks, м³ — объём СКР", value=float(st.session_state["v13_V_ks"]), step=0.5, min_value=0.0)
        st.session_state["v13_V_zrs"] = c2.number_input(
            "Vз.рs, м³ — объём зоны растворения (0 = неизвестно)",
            value=float(st.session_state["v13_V_zrs"]), step=0.1, min_value=0.0)

        c1, c2, c3 = st.columns(3)
        st.session_state["v13_H_no"] = c1.number_input(
            "Hн.о, м — нижнее отв. перфорации", value=float(st.session_state["v13_H_no"]), step=10.0)
        st.session_state["v13_H_vo"] = c2.number_input(
            "Hв.о, м — верхнее отв. перфорации", value=float(st.session_state["v13_H_vo"]), step=10.0)
        st.session_state["v13_D_k"] = c3.number_input(
            "Dк, м — внутр. диаметр ЭК", value=float(st.session_state["v13_D_k"]), step=0.001, format="%.3f")

        c1, c2 = st.columns(2)
        st.session_state["v13_d_vn"] = c1.number_input(
            "dвн, м — наружный диаметр НКТ", value=float(st.session_state["v13_d_vn"]), step=0.001, format="%.3f")
        st.session_state["v13_d_v"] = c2.number_input(
            "dв, м — внутренний диаметр НКТ", value=float(st.session_state["v13_d_v"]), step=0.001, format="%.3f")

    p = {k: st.session_state[f"v13_{k}"] for k in
         ("V_ks", "V_zrs", "H_no", "H_vo", "D_k", "d_vn", "d_v")}
    res = solve(p)

    # ── метрики ──
    c1, c2, c3 = st.columns(3)
    c1.metric("Vпрд, м³ (продавочная)", f"{res['V_prd']:.2f}" if res["V_prd"] is not None else "—")
    c2.metric("Vвтс, м³ (вытесняющая)", f"{res['V_vts']:.2f}" if res["V_vts"] is not None else "—",
              delta=res["V_vts_src"], delta_color="off")
    total = (res["V_prd"] or 0) + (res["V_vts"] or 0)
    c3.metric("Σ доп. жидкости, м³", f"{total:.2f}" if total else "—")

    # ── подстановка в формулу В.58 ──
    if res["V_prd"] is not None:
        st.markdown("##### Продавочная жидкость (В.58)")
        st.latex(
            r"V_{\text{прд}} = 0{,}785\left[%.3f^2\cdot%.0f + (%.3f^2-%.3f^2)(%.0f-%.0f)\right] = %.2f\ \text{м}^3"
            % (p["d_v"], p["H_no"], p["D_k"], p["d_vn"], p["H_no"], p["H_vo"], res["V_prd"])
        )
        st.caption(f"Объём НКТ: {0.785*res['tubing_term']:.2f} м³ + кольцевой объём в интервале "
                   f"перфорации ({res['interval']:.0f} м): {0.785*res['annulus_term']:.2f} м³.")

    # ── вытесняющая жидкость: оба варианта ──
    st.markdown("##### Вытесняющая жидкость (В.56 / В.57)")
    vts_df = pd.DataFrame([
        {"Способ": "По зоне растворения (В.56)", "Формула": "1,2·Vз.рs",
         "Значение, м³": f"{res['V_vts_56']:.2f}" if res["V_vts_56"] is not None else "— (нет Vз.рs)"},
        {"Способ": "С запасом (В.57)", "Формула": "0,3·Vks",
         "Значение, м³": f"{res['V_vts_57']:.2f}" if res["V_vts_57"] is not None else "—"},
    ])
    st.dataframe(vts_df, use_container_width=True, hide_index=True)

    # ── диаграмма ──
    if res["V_prd"] is not None and res["V_vts"] is not None:
        fig = go.Figure(go.Bar(
            x=["Продавочная Vпрд", "Вытесняющая Vвтс"],
            y=[res["V_prd"], res["V_vts"]],
            text=[f"{res['V_prd']:.2f}", f"{res['V_vts']:.2f}"],
            textposition="outside",
        ))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10),
                          yaxis_title="V, м³")
        st.plotly_chart(fig, use_container_width=True)

    # ── заключение ──
    if res["V_prd"] is not None and res["V_vts"] is not None:
        st.success(
            f"**Продавочная жидкость:** Vпрд = {res['V_prd']:.2f} м³.  \n"
            f"**Вытесняющая жидкость:** Vвтс = {res['V_vts']:.2f} м³ ({res['V_vts_src']}).")
    else:
        st.info("Заполните исходные данные или нажмите «Пример В.10.1».")
