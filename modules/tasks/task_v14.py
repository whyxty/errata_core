"""Задача В.15 — Изменение пористости песчаного коллектора после ГКР.

Методику применяют при отсутствии прямых лабораторных определений kmg
(задача В.13), при наличии данных задачи В.14.

Формулы (Приложение В):
    В.82  DVg  = ρп·DGg / ρск           — прирост пористости (объёмная доля), %
    В.83  mg   = ms + DVg               — пористость после ГКР, %
    В.84  kmg  = mg / ms                — рост пористости после ГКР
    В.85  kmsg = kms·kmg                — рост пористости по сравнению с начальной
"""
import streamlit as st
import plotly.graph_objects as go

from modules.input_data import get_inputs
from modules.ui import calc_gate, clear_result


# Пример В.15.1 (из методички)
EXAMPLE_V15 = {
    "DG_g": 4.92, "rho_sk": 2700.0, "rho_p": 2300.0,
    "m_s": 16.8, "k_ms": 1.2, "m_0": 14.0,
}


# ─────────────────────── расчёт ───────────────────────
def solve(p: dict) -> dict:
    DG_g, rho_sk, rho_p = p["DG_g"], p["rho_sk"], p["rho_p"]
    m_s, k_ms = p["m_s"], p["k_ms"]

    DV_g = (rho_p * DG_g / rho_sk) if rho_sk > 0 else None     # В.82
    m_g = (m_s + DV_g) if DV_g is not None else None           # В.83
    k_mg = (m_g / m_s) if (m_g is not None and m_s > 0) else None  # В.84
    k_msg = (k_ms * k_mg) if k_mg is not None else None        # В.85

    return {"DV_g": DV_g, "m_g": m_g, "k_mg": k_mg, "k_msg": k_msg}


# ─────────────────────── UI ───────────────────────
def _load_example():
    for k, v in EXAMPLE_V15.items():
        st.session_state[f"v14_{k}"] = v
    clear_result("v14")


def render(cfg: dict):
    inp = get_inputs()

    title_col, btn_col = st.columns([5, 1.3])
    title_col.subheader("Изменение пористости песчаного коллектора")
    if btn_col.button("Пример", key="ex_v14", type="secondary", use_container_width=True):
        _load_example(); st.rerun()

    st.caption("Ожидаемое изменение пористости песчаного коллектора после обработки "
               "глинокислотным раствором. Применяют при отсутствии прямых лабораторных "
               "определений kmg (по данным о количестве карбонатов и глин — задача В.14).")

    with st.expander("Формулы", expanded=False):
        st.latex(r"DV_g = \rho_{\text{п}}\,DG_g / \rho_{\text{ск}} \quad\text{(В.82)}")
        st.latex(r"m_g = m_s + DV_g \quad\text{(В.83)}")
        st.latex(r"k_{mg} = m_g / m_s \quad\text{(В.84)}")
        st.latex(r"k_{msg} = k_{ms}\,k_{mg} \quad\text{(В.85)}")
        st.markdown("*DGg — масс. доля растворённой породы (задача В.14); ρп, ρск — плотность "
                    "породы и скелета; ms, kms — пористость и рост пористости после СКР.*")

    # ── инициализация (пусто — данные вводит пользователь или кнопка «Пример») ──
    st.session_state.setdefault("v14_DG_g", 0.0)
    st.session_state.setdefault("v14_rho_sk", 0.0)
    st.session_state.setdefault("v14_rho_p", 0.0)
    st.session_state.setdefault("v14_m_s", 0.0)
    st.session_state.setdefault("v14_k_ms", 0.0)
    st.session_state.setdefault("v14_m_0", 0.0)

    with st.expander("Исходные данные", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v14_DG_g"] = c1.number_input(
            "DGg, % — растворённая порода (В.14)", value=float(st.session_state["v14_DG_g"]), step=0.1, min_value=0.0)
        st.session_state["v14_rho_p"] = c2.number_input(
            "ρп, кг/м³ — плотность породы", value=float(st.session_state["v14_rho_p"]), step=10.0)
        st.session_state["v14_rho_sk"] = c3.number_input(
            "ρск, кг/м³ — плотность скелета", value=float(st.session_state["v14_rho_sk"]), step=10.0)

        c1, c2, c3 = st.columns(3)
        st.session_state["v14_m_s"] = c1.number_input(
            "ms, % — пористость после СКР", value=float(st.session_state["v14_m_s"]), step=0.1, min_value=0.0)
        st.session_state["v14_k_ms"] = c2.number_input(
            "kms — рост пористости после СКР", value=float(st.session_state["v14_k_ms"]), step=0.01, min_value=0.0)
        st.session_state["v14_m_0"] = c3.number_input(
            "m₀, % — начальная пористость (справ.)", value=float(st.session_state["v14_m_0"]), step=0.1, min_value=0.0)

    p = {k: st.session_state[f"v14_{k}"] for k in ("DG_g", "rho_sk", "rho_p", "m_s", "k_ms", "m_0")}

    # ── кнопка расчёта: результат показывается только после нажатия ──
    res = calc_gate("v14", lambda: solve(p),
                    prompt="Заполните исходные данные, затем нажмите «РАССЧИТАТЬ».")
    if res is None:
        return

    # ── метрики ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DVg, %", f"{res['DV_g']:.2f}" if res["DV_g"] is not None else "—")
    c2.metric("mg, % (после ГКР)", f"{res['m_g']:.1f}" if res["m_g"] is not None else "—")
    c3.metric("kmg = mg/ms", f"{res['k_mg']:.3f}" if res["k_mg"] is not None else "—")
    c4.metric("kmsg = kms·kmg", f"{res['k_msg']:.3f}" if res["k_msg"] is not None else "—")

    # ── подстановка ──
    if res["DV_g"] is not None:
        st.markdown("##### Расчёт")
        st.latex(r"DV_g = %.0f\cdot%.2f / %.0f = %.2f\ \%%" % (p["rho_p"], p["DG_g"], p["rho_sk"], res["DV_g"]))
        st.latex(r"m_g = %.1f + %.2f = %.1f\ \%%" % (p["m_s"], res["DV_g"], res["m_g"]))
        st.latex(r"k_{mg} = %.1f / %.1f = %.2f" % (res["m_g"], p["m_s"], res["k_mg"]))
        st.latex(r"k_{msg} = %.2f \cdot %.2f = %.2f" % (p["k_ms"], res["k_mg"], res["k_msg"]))

    # ── диаграмма роста пористости ──
    if res["m_g"] is not None:
        fig = go.Figure(go.Bar(
            x=["m₀ (нач.)", "ms (после СКР)", "mg (после ГКР)"],
            y=[p["m_0"], p["m_s"], res["m_g"]],
            text=[f"{p['m_0']:.1f}", f"{p['m_s']:.1f}", f"{res['m_g']:.1f}"],
            textposition="outside",
        ))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Пористость, %")
        st.plotly_chart(fig, use_container_width=True)

    # ── заключение ──
    if res["k_msg"] is not None:
        st.success(
            f"**Пористость после ГКР:** mg = {res['m_g']:.1f} %.  \n"
            f"**Рост после ГКР:** kmg = {res['k_mg']:.2f}; "
            f"**суммарный рост (к начальной):** kmsg = {res['k_msg']:.2f}.")
    else:
        st.info("Заполните исходные данные или нажмите «Пример».")
