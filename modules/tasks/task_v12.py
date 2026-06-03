"""Задача В.12 — Расход жидкости и давление во время нагнетания
кислотного раствора в пласт.

Методика (Приложение В): по кривой приёмистости pу = f(t), снятой при
пробном нагнетании жидкости с расходом q0, определяют квазиустойчивое
давление на устье pк и обосновывают допустимые расход qк и давление КО.

Проверки:
    В.10  qк ≥ qпр                       — нижний предел расхода
    В.15  pк ≤ pопр                      — нагнетание без пакера
    В.19  pгст = ρ·g·H·10⁻⁶              — гидростатическое давление
    В.18  grad pк  = (pгст + pк)/(0,01·H)
    В.17  grad pгрп = pгрп/(0,01·H)
    В.20  grad pгрп ≈ 100·(pгст + 0,008·H)/H   (если ГРП не исследован)
    В.16  grad pк < grad pгрп            — гидроразрыв не ожидается
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from modules.input_data import get_inputs


_PT_COLS = ["t, мин", "pу, МПа", "V, м³"]

# Точки кривой приёмистости из рис. В.1 (пробное нагнетание q0 = 225 м³/сут,
# нефтяная скважина — кривая 2). V = q0·t = 225/1440·t ≈ 0,156·t м³.
EXAMPLE_POINTS = [
    {"t, мин": 0,  "pу, МПа": 0.0,   "V, м³": 0.00},
    {"t, мин": 1,  "pу, МПа": 6.0,   "V, м³": 0.16},
    {"t, мин": 2,  "pу, МПа": 9.0,   "V, м³": 0.31},
    {"t, мин": 3,  "pу, МПа": 10.6,  "V, м³": 0.47},
    {"t, мин": 5,  "pу, МПа": 11.4,  "V, м³": 0.78},
    {"t, мин": 8,  "pу, МПа": 11.8,  "V, м³": 1.25},
    {"t, мин": 12, "pу, МПа": 11.95, "V, м³": 1.88},
    {"t, мин": 16, "pу, МПа": 12.0,  "V, м³": 2.50},
    {"t, мин": 20, "pу, МПа": 12.0,  "V, м³": 3.12},
]

EXAMPLE_SCALARS = {
    "q0": 225.0, "p_k": 12.0,
    "H_top": 1840.0, "H_bot": 1960.0,
    "p_opr": 20.0, "well_type": "нефтяная",
    "grad_grp_mode": "Региональный градиент (табл.)",
    "grad_grp_meas": 1.8,
}


# ─────────────────────── конфиг ───────────────────────
def _cfg_inj(cfg: dict) -> dict:
    inj = (cfg or {}).get("injection", {})
    wc = (cfg or {}).get("well_check", {})
    return {
        "grad_grp_oil":   inj.get("grad_grp_oil", 1.8),
        "grad_grp_water": inj.get("grad_grp_water", 1.9),
        "q_pr":           inj.get("q_pr", wc.get("q_pr", 24.0)),
        "rho":            inj.get("rho_water", 1000.0),
        "g":              inj.get("g", 9.8),
    }


# ─────────────────────── расчёт ───────────────────────
def solve(params: dict, T: dict) -> dict:
    H_top, H_bot = params["H_top"], params["H_bot"]
    H = (H_top + H_bot) / 2.0 if (H_top and H_bot) else (H_top or H_bot or 0.0)
    p_k, p_opr, q0 = params["p_k"], params["p_opr"], params["q0"]
    rho, g = T["rho"], T["g"]

    # В.19 — гидростатическое давление воды в скважине
    p_gst = rho * g * H * 1e-6 if H > 0 else None
    # В.18 — градиент давления при нагнетании
    grad_pk = ((p_gst + p_k) / (0.01 * H)) if (p_gst is not None and H > 0) else None
    # В.20 — оценка градиента ГРП, если не исследован
    grad_grp_b20 = (100.0 * (p_gst + 0.008 * H) / H) if (p_gst is not None and H > 0) else None

    # выбор градиента ГРП
    if params["grad_grp_mode"].startswith("Региональный"):
        grad_grp = T["grad_grp_water"] if params["well_type"] == "водонагнетательная" else T["grad_grp_oil"]
        grad_grp_src = f"региональный для {params['well_type']} скв."
    elif params["grad_grp_mode"].startswith("По формуле"):
        grad_grp = grad_grp_b20
        grad_grp_src = "оценка по (В.20)"
    else:
        grad_grp = params["grad_grp_meas"]
        grad_grp_src = "измеренный (предв. ГРП)"

    # ── критерии ──
    ok_pakerless = (p_k <= p_opr) if p_opr > 0 else None          # В.15
    ok_no_frac = (grad_pk < grad_grp) if (grad_pk is not None and grad_grp) else None  # В.16
    ok_q = (q0 >= T["q_pr"]) if q0 > 0 else None                  # В.10

    return {
        "H": H, "p_gst": p_gst, "grad_pk": grad_pk,
        "grad_grp": grad_grp, "grad_grp_b20": grad_grp_b20, "grad_grp_src": grad_grp_src,
        "p_k": p_k, "p_opr": p_opr, "q0": q0,
        "ok_pakerless": ok_pakerless, "ok_no_frac": ok_no_frac, "ok_q": ok_q,
    }


# ─────────────────────── график ───────────────────────
def build_chart(pts: pd.DataFrame, res: dict):
    t = pts["t, мин"].to_numpy(dtype=float)
    p = pts["pу, МПа"].to_numpy(dtype=float)

    fig = go.Figure()
    # измеренные точки + сглаживающая линия
    fig.add_trace(go.Scatter(
        x=t, y=p, mode="lines+markers", name="pу (замеры)",
        line=dict(shape="spline", width=2.5), marker=dict(size=7),
    ))

    # линия квазиустойчивого pк
    fig.add_hline(y=res["p_k"], line_dash="dash", line_color="#16a34a",
                  annotation_text=f"pк = {res['p_k']:.1f} МПа", annotation_position="bottom right")
    # линия давления опрессовки pопр (предел)
    if res["p_opr"] > 0:
        fig.add_hline(y=res["p_opr"], line_dash="dot", line_color="#dc2626",
                      annotation_text=f"pопр = {res['p_opr']:.1f} МПа", annotation_position="top right")

    fig.update_layout(
        height=420, margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="t, мин", yaxis_title="pу, МПа",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


# ─────────────────────── UI ───────────────────────
def _load_example():
    st.session_state["v12_points"] = [dict(r) for r in EXAMPLE_POINTS]
    for k, v in EXAMPLE_SCALARS.items():
        st.session_state[f"v12_{k}"] = v


def render(cfg: dict):
    T = _cfg_inj(cfg)
    inp = get_inputs()

    title_col, btn_col = st.columns([5, 1.3])
    title_col.subheader("Расход жидкости и давление при нагнетании кислоты в пласт")
    if btn_col.button("Пример В.3.1", key="ex_v12", type="secondary", use_container_width=True):
        _load_example(); st.rerun()

    st.caption("По кривой приёмистости pу = f(t) (рис. В.1) определяем квазиустойчивое "
               "давление на устье pк и обосновываем допустимые расход qк и давление КО.")

    with st.expander("Обозначения и условия", expanded=False):
        st.markdown("""
| Символ | Значение | Условие |
|---|---|---|
| `pу = f(t)` | кривая приёмистости при пробном нагнетании с расходом q0 | замеры |
| `pк` | квазиустойчивое давление на устье (плато кривой) | — |
| `qк ≥ qпр` | нижний предел расхода (В.10) | qпр = 24 м³/сут |
| `pк ≤ pопр` | нагнетание без пакера (В.15) | pопр = 15–40 МПа |
| `pгст = ρ·g·H·10⁻⁶` | гидростатическое давление воды (В.19) | ρ = 1000 кг/м³ |
| `grad pк = (pгст+pк)/(0,01·H)` | градиент при нагнетании (В.18) | МПа/100 м |
| `grad pгрп = pгрп/(0,01·H)` | градиент ГРП (В.17); либо оценка (В.20) | МПа/100 м |
| `grad pк < grad pгрп` | гидроразрыв не ожидается (В.16) | — |

*В песчано-алевролитовых пластах верхний предел расхода не регламентируется
(скорость фильтрации слабо влияет на длительность реакции) — расход ограничивается
только давлением.*
""")

    # ── инициализация ──
    st.session_state.setdefault("v12_points", [dict(r) for r in EXAMPLE_POINTS])
    st.session_state.setdefault("v12_q0", 225.0)
    st.session_state.setdefault("v12_p_k", 12.0)
    st.session_state.setdefault("v12_H_top", float(inp.get("H") or 0.0) or 1840.0)
    st.session_state.setdefault("v12_H_bot", 1960.0)
    st.session_state.setdefault("v12_p_opr", float(inp.get("p_opr") or 0.0) or 20.0)
    st.session_state.setdefault("v12_well_type", inp.get("well_type") or "нефтяная")
    st.session_state.setdefault("v12_grad_grp_mode", "Региональный градиент (табл.)")
    st.session_state.setdefault("v12_grad_grp_meas", 1.8)

    # ── точки кривой ──
    st.markdown("##### Точки кривой приёмистости pу = f(t) (с рис. В.1)")
    df = pd.DataFrame(st.session_state["v12_points"])
    for c in _PT_COLS:
        if c not in df.columns:
            df[c] = 0.0
    df = df[_PT_COLS]
    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, key="v12_editor",
        column_config={
            "t, мин":  st.column_config.NumberColumn("t, мин", format="%.1f"),
            "pу, МПа": st.column_config.NumberColumn("pу, МПа", format="%.2f"),
            "V, м³":   st.column_config.NumberColumn("V, м³", help="Закачанный объём (опц.)", format="%.2f"),
        },
    )
    st.session_state["v12_points"] = edited.to_dict("records")
    pts = edited.copy()
    pts = pts[pd.to_numeric(pts["t, мин"], errors="coerce").notna()]
    pts = pts.sort_values("t, мин").reset_index(drop=True)

    # ── параметры ──
    with st.expander("Параметры нагнетания и скважины", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v12_q0"] = c1.number_input(
            "q0, м³/сут — расход пробного нагнетания", value=float(st.session_state["v12_q0"]), step=5.0)
        st.session_state["v12_p_k"] = c2.number_input(
            "pк, МПа — квазиустойчивое давление на устье", value=float(st.session_state["v12_p_k"]), step=0.5)
        st.session_state["v12_p_opr"] = c3.number_input(
            "pопр, МПа — давление опрессовки колонны", value=float(st.session_state["v12_p_opr"]), step=0.5)

        c1, c2 = st.columns(2)
        st.session_state["v12_H_top"] = c1.number_input(
            "Кровля обрабатываемого интервала, м", value=float(st.session_state["v12_H_top"]), step=10.0)
        st.session_state["v12_H_bot"] = c2.number_input(
            "Подошва обрабатываемого интервала, м", value=float(st.session_state["v12_H_bot"]), step=10.0)
        st.session_state["v12_well_type"] = "нефтяная"

        st.session_state["v12_grad_grp_mode"] = st.radio(
            "Источник градиента ГРП (grad pгрп)",
            ["Региональный градиент (табл.)", "По формуле (В.20)", "Измеренный (предв. ГРП)"],
            index=["Региональный градиент (табл.)", "По формуле (В.20)", "Измеренный (предв. ГРП)"]
            .index(st.session_state["v12_grad_grp_mode"]),
            horizontal=True)
        if st.session_state["v12_grad_grp_mode"].startswith("Измеренный"):
            st.session_state["v12_grad_grp_meas"] = st.number_input(
                "grad pгрп (измеренный), МПа/100 м",
                value=float(st.session_state["v12_grad_grp_meas"]), step=0.01)

    params = {
        "q0": st.session_state["v12_q0"], "p_k": st.session_state["v12_p_k"],
        "p_opr": st.session_state["v12_p_opr"],
        "H_top": st.session_state["v12_H_top"], "H_bot": st.session_state["v12_H_bot"],
        "well_type": st.session_state["v12_well_type"],
        "grad_grp_mode": st.session_state["v12_grad_grp_mode"],
        "grad_grp_meas": st.session_state["v12_grad_grp_meas"],
    }
    res = solve(params, T)

    # ── график ──
    st.markdown("##### Кривая приёмистости")
    if len(pts) >= 2:
        st.plotly_chart(build_chart(pts, res), use_container_width=True)
    else:
        st.info("Введите минимум 2 точки кривой pу = f(t).")

    # ── метрики ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("H (средн.), м", f"{res['H']:.0f}")
    c2.metric("pгст, МПа", f"{res['p_gst']:.2f}" if res["p_gst"] is not None else "—")
    c3.metric("grad pк, МПа/100 м", f"{res['grad_pk']:.2f}" if res["grad_pk"] is not None else "—")
    c4.metric("grad pгрп, МПа/100 м", f"{res['grad_grp']:.2f}" if res["grad_grp"] else "—")

    # ── таблица проверок ──
    st.markdown("##### Проверка условий")
    sym = {True: "✓", False: "✗", None: "—"}
    rows = [
        {"Условие": "Расход (В.10)", "Формула": "qк ≥ qпр",
         "Значение": f"q0 = {res['q0']:.0f} м³/сут", "Порог": f"≥ {T['q_pr']:g}",
         "ok": res["ok_q"]},
        {"Условие": "Давление (В.15)", "Формула": "pк ≤ pопр",
         "Значение": f"pк = {res['p_k']:.1f} МПа", "Порог": f"≤ {res['p_opr']:.1f} МПа",
         "ok": res["ok_pakerless"]},
        {"Условие": "Гидроразрыв (В.16)", "Формула": "grad pк < grad pгрп",
         "Значение": f"{res['grad_pk']:.2f}" if res["grad_pk"] is not None else "—",
         "Порог": f"< {res['grad_grp']:.2f} ({res['grad_grp_src']})" if res["grad_grp"] else "—",
         "ok": res["ok_no_frac"]},
    ]
    crit_df = pd.DataFrame([{**{k: r[k] for k in ("Условие", "Формула", "Значение", "Порог")},
                             "Статус": sym[r["ok"]]} for r in rows])

    def _style(row):
        ok = rows[row.name]["ok"]
        bg = "#ecfdf3" if ok is True else "#fef2f2" if ok is False else "#f7f8fa"
        return [f"background-color: {bg}"] * len(row)

    st.dataframe(crit_df.style.apply(_style, axis=1), use_container_width=True, hide_index=True)

    # ── заключение ──
    st.markdown("##### Заключение")
    paker = "без пакера" if res["ok_pakerless"] else "с пакером (pк > pопр)"
    frac = "гидроразрыв пласта не ожидается" if res["ok_no_frac"] else "возможен гидроразрыв — снизьте pк/расход"
    if res["ok_q"] and res["ok_pakerless"] and res["ok_no_frac"]:
        st.success(
            f"**Рекомендуемый расход КО:** qк = {res['q0']:.0f} м³/сут при pк = {res['p_k']:.1f} МПа.  \n"
            f"Нагнетание проводят **{paker}**; {frac} "
            f"(grad pк = {res['grad_pk']:.2f} < grad pгрп = {res['grad_grp']:.2f} МПа/100 м).")
    else:
        warn = []
        if res["ok_q"] is False:
            warn.append(f"расход q0 = {res['q0']:.0f} < qпр = {T['q_pr']:g} м³/сут")
        if res["ok_pakerless"] is False:
            warn.append(f"pк = {res['p_k']:.1f} > pопр = {res['p_opr']:.1f} МПа — требуется пакер")
        if res["ok_no_frac"] is False:
            warn.append(f"grad pк = {res['grad_pk']:.2f} ≥ grad pгрп = {res['grad_grp']:.2f} МПа/100 м — риск ГРП")
        st.warning("Не выполнены условия: " + "; ".join(warn) + "." if warn
                   else "Недостаточно данных — заполните параметры или нажмите «Пример В.3.1».")
