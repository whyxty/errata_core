"""Задача В.16 — Технологическая и экономическая эффективность ГКО.

Приток через две зоны растворения (СКР r_з.рs и ГКР r_з.рg) в радиальном пласте.

Формулы (Приложение В):
    В.86  Ag = ln(rk/rc) / [ (k0/kg)·ln(rз.рg/rc) + (k0/ks)·ln(rз.рs/rз.рg) + ln(rk/rз.рs) ]
    В.87  Qg = Ag·Qф
    В.88  DQн = (Qg − Qф)·Tн·ρн·(100 − W0)/100
    В.89  Qg = Ag·εот·Qф + (1 − εот)·Qф           (учёт охвата)
    В.90  DQн = (Ag − 1)·εот·Qф·Tн·ρн·(100 − W0)/100
    В.91  Эн = (Цн − Cн)·DQн − Zко
"""
import math

import pandas as pd
import streamlit as st

from modules.input_data import get_inputs
from modules.ui import calc_gate, clear_result


_V_COLS = ["Vскр, м³", "Vгкр, м³", "rз.рs, м", "rз.рg, м", "ks, мкм²", "kg, мкм²", "Zко, руб"]


def _vol_label(row: dict) -> str:
    vs = float(row.get("Vскр, м³") or 0)
    vg = float(row.get("Vгкр, м³") or 0)
    return f"{vs:g}+{vg:g}" if (vs or vg) else "—"

# Пример В.16.1 (табл. В.25). ks, kg для вариантов 6+6 и 9+9 приняты как для 3+3
# (точные значения берут из табл. В.9/В.23/В.13 — поле редактируемое).
EXAMPLE_V16 = {
    "k_0": 0.044, "r_c": 0.1, "r_k": 200.0,
    "Q_f": 86.6, "T_n": 100.0, "rho_n": 0.84, "W_0": 81.9,
    "Ts_n": 150.0, "C_n": 80.0, "eps_ot": 1.0,
    "variants": [
        {"Vскр, м³": 3, "Vгкр, м³": 3, "rз.рs, м": 0.54, "rз.рg, м": 0.43, "ks, мкм²": 0.074, "kg, мкм²": 0.169, "Zко, руб": 3000},
        {"Vскр, м³": 6, "Vгкр, м³": 6, "rз.рs, м": 0.76, "rз.рg, м": 0.61, "ks, мкм²": 0.074, "kg, мкм²": 0.169, "Zко, руб": 4000},
        {"Vскр, м³": 9, "Vгкр, м³": 9, "rз.рs, м": 0.92, "rз.рg, м": 0.74, "ks, мкм²": 0.074, "kg, мкм²": 0.169, "Zко, руб": 5000},
    ],
}


# ─────────────────────── расчёт ───────────────────────
def solve_variant(base: dict, row: dict):
    """Возвращает dict с Ag, Qg, DQ, E или None при некорректных данных."""
    try:
        k0 = base["k_0"]; rc = base["r_c"]; rk = base["r_k"]
        rzrs = float(row.get("rз.рs, м") or 0); rzrg = float(row.get("rз.рg, м") or 0)
        ks = float(row.get("ks, мкм²") or 0); kg = float(row.get("kg, мкм²") or 0)
        Z = float(row.get("Zко, руб") or 0)
        if not (0 < rc < rzrg < rzrs < rk) or ks <= 0 or kg <= 0 or k0 <= 0:
            return None
        num = math.log(rk / rc)
        den = (k0 / kg) * math.log(rzrg / rc) + (k0 / ks) * math.log(rzrs / rzrg) + math.log(rk / rzrs)
        Ag = num / den

        Qf, Tn, rho, W0 = base["Q_f"], base["T_n"], base["rho_n"], base["W_0"]
        eps = base["eps_ot"]
        Qg = Ag * eps * Qf + (1 - eps) * Qf                          # В.89
        DQ = (Ag - 1) * eps * Qf * Tn * rho * (100 - W0) / 100       # В.90
        E = (base["Ts_n"] - base["C_n"]) * DQ - Z                    # В.91
        return {"Ag": Ag, "Qg": Qg, "DQ": DQ, "E": E, "Z": Z,
                "rzrs": rzrs, "rzrg": rzrg, "ks": ks, "kg": kg}
    except Exception:
        return None


# ─────────────────────── UI ───────────────────────
def _load_example():
    for k, v in EXAMPLE_V16.items():
        if k == "variants":
            st.session_state["v15_variants"] = [dict(r) for r in v]
        else:
            st.session_state[f"v15_{k}"] = v
    clear_result("v15")


def render(cfg: dict):
    inp = get_inputs()

    title_col, btn_col = st.columns([5, 1.3])
    title_col.subheader("Технологическая и экономическая эффективность ГКО")
    if btn_col.button("Пример", key="ex_v15", type="secondary", use_container_width=True):
        _load_example(); st.rerun()

    st.caption("Степень увеличения дебита при притоке через две зоны растворения (СКР и ГКР) "
               "и экономическая эффективность обработки. Сравните варианты объёмов СКР+ГКР и "
               "выберите рациональный.")

    with st.expander("Формулы", expanded=False):
        st.latex(r"A_g = \frac{\ln(r_k/r_c)}{(k_0/k_g)\ln(r_{\text{з.рg}}/r_c) + "
                 r"(k_0/k_s)\ln(r_{\text{з.рs}}/r_{\text{з.рg}}) + \ln(r_k/r_{\text{з.рs}})} \quad\text{(В.86)}")
        st.latex(r"Q_g = A_g\,Q_\phi \quad\text{(В.87)}")
        st.latex(r"DQ_{\text{н}} = (Q_g - Q_\phi)\,T_{\text{н}}\,\rho_{\text{н}}\,(100 - W_0)/100 \quad\text{(В.88)}")
        st.latex(r"Q_g = A_g\,\varepsilon_{\text{от}}\,Q_\phi + (1-\varepsilon_{\text{от}})\,Q_\phi \quad\text{(В.89)}")
        st.latex(r"DQ_{\text{н}} = (A_g-1)\,\varepsilon_{\text{от}}\,Q_\phi\,T_{\text{н}}\,\rho_{\text{н}}\,(100-W_0)/100 \quad\text{(В.90)}")
        st.latex(r"\mathit{Э}_{\text{н}} = (\mathit{Ц}_{\text{н}} - C_{\text{н}})\,DQ_{\text{н}} - Z_{\text{ко}} \quad\text{(В.91)}")

    # ── инициализация (часть — из общих данных скважины) ──
    st.session_state.setdefault("v15_k_0", 0.0)
    st.session_state.setdefault("v15_r_c", 0.0)
    st.session_state.setdefault("v15_r_k", 0.0)
    st.session_state.setdefault("v15_Q_f", 0.0)
    st.session_state.setdefault("v15_T_n", 0.0)
    st.session_state.setdefault("v15_rho_n", 0.0)
    st.session_state.setdefault("v15_W_0", 0.0)
    st.session_state.setdefault("v15_Ts_n", 0.0)
    st.session_state.setdefault("v15_C_n", 0.0)
    st.session_state.setdefault("v15_eps_ot", 1.0)
    st.session_state.setdefault("v15_variants", [])

    with st.expander("Общие параметры скважины и экономика", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v15_k_0"] = c1.number_input("k₀, мкм² — проницаемость до КО",
            value=float(st.session_state["v15_k_0"]), step=0.001, format="%.3f")
        st.session_state["v15_r_c"] = c2.number_input("r_c, м — радиус скважины",
            value=float(st.session_state["v15_r_c"]), step=0.01, format="%.2f")
        st.session_state["v15_r_k"] = c3.number_input("r_k, м — радиус контура питания",
            value=float(st.session_state["v15_r_k"]), step=10.0)

        c1, c2, c3, c4 = st.columns(4)
        st.session_state["v15_Q_f"] = c1.number_input("Qф, м³/сут — дебит до КО",
            value=float(st.session_state["v15_Q_f"]), step=1.0)
        st.session_state["v15_T_n"] = c2.number_input("Tн, сут — длит. повыш. дебита",
            value=float(st.session_state["v15_T_n"]), step=1.0)
        st.session_state["v15_rho_n"] = c3.number_input("ρн, т/м³",
            value=float(st.session_state["v15_rho_n"]), step=0.01, format="%.2f")
        st.session_state["v15_W_0"] = c4.number_input("W₀, % — обводнённость",
            value=float(st.session_state["v15_W_0"]), step=0.1)

        c1, c2, c3 = st.columns(3)
        st.session_state["v15_Ts_n"] = c1.number_input("Цн, руб/т — цена нефти",
            value=float(st.session_state["v15_Ts_n"]), step=10.0)
        st.session_state["v15_C_n"] = c2.number_input("Cн, руб/т — себестоимость",
            value=float(st.session_state["v15_C_n"]), step=10.0)

        st.session_state["v15_eps_ot"] = st.number_input(
            "εот — относит. гидропроводность обрабатываемых прослоёв (В.13), 1 = весь разрез",
            value=float(st.session_state["v15_eps_ot"]), step=0.05, min_value=0.0, max_value=1.0)

    base = {k: st.session_state[f"v15_{k}"] for k in
            ("k_0", "r_c", "r_k", "Q_f", "T_n", "rho_n", "W_0", "Ts_n", "C_n", "eps_ot")}

    # ── таблица вариантов ──
    st.markdown("##### Варианты объёмов СКР+ГКР (rз.рs, rз.рg — из табл. В.9/В.23; ks, kg — В.13)")
    df = pd.DataFrame(st.session_state["v15_variants"])
    for c in _V_COLS:
        if c not in df.columns:
            df[c] = 0.0
    df = df[_V_COLS]
    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, key="v15_editor",
        column_config={
            "Vскр, м³": st.column_config.NumberColumn("Vскр, м³", format="%g"),
            "Vгкр, м³": st.column_config.NumberColumn("Vгкр, м³", format="%g"),
            "rз.рs, м": st.column_config.NumberColumn("rз.рs, м", format="%.2f"),
            "rз.рg, м": st.column_config.NumberColumn("rз.рg, м", format="%.2f"),
            "ks, мкм²": st.column_config.NumberColumn("ks, мкм²", format="%.3f"),
            "kg, мкм²": st.column_config.NumberColumn("kg, мкм²", format="%.3f"),
            "Zко, руб": st.column_config.NumberColumn("Zко, руб", format="%.0f"),
        },
    )
    st.session_state["v15_variants"] = edited.to_dict("records")
    variants = st.session_state["v15_variants"]

    # ── кнопка расчёта: результат показывается только после нажатия ──
    def _compute():
        out = []
        for row in variants:
            r = solve_variant(base, row)
            if r is not None:
                out.append((row, r))
        return out

    results = calc_gate("v15", _compute,
                        prompt="Заполните параметры и варианты, затем нажмите «РАССЧИТАТЬ».")
    if results is None:
        return
    if not results:
        st.info("Заполните корректные варианты (r_c < rз.рg < rз.рs < r_k; ks, kg > 0) "
                "или нажмите «Пример».")
        return

    # ── таблица результатов ──
    st.markdown("##### Результаты (табл. В.25)")
    res_df = pd.DataFrame([{
        "Vскр+Vгкр, м³": _vol_label(row),
        "Радиус зоны раств., м": f"{r['rzrs']:.2f}+{r['rzrg']:.2f}",
        "Кратность Ag": f"{r['Ag']:.3f}",
        "Qg, м³/сут": f"{r['Qg']:.1f}",
        "ΔQн, т": f"{r['DQ']:.1f}",
        "Zко, руб": f"{r['Z']:.0f}",
        "Эн, руб": f"{r['E']:.0f}",
    } for row, r in results])

    best_idx = max(range(len(results)), key=lambda i: results[i][1]["E"])

    def _hi(row):
        return ["background-color: #ecfdf3" if row.name == best_idx else ""] * len(row)

    st.dataframe(res_df.style.apply(_hi, axis=1), use_container_width=True, hide_index=True)

    # ── подстановка В.86 по каждому варианту ──
    st.markdown("##### Расчёт Ag (В.86)")
    for row, r in results:
        st.caption(f"Вариант {_vol_label(row)} м³:")
        st.latex(
            r"A_g = \frac{\ln(%.0f/%.1f)}{(%.3f/%.3f)\ln(%.2f/%.1f) + (%.3f/%.3f)\ln(%.2f/%.2f) + \ln(%.0f/%.2f)} = %.3f"
            % (base["r_k"], base["r_c"], base["k_0"], r["kg"], r["rzrg"], base["r_c"],
               base["k_0"], r["ks"], r["rzrs"], r["rzrg"], base["r_k"], r["rzrs"], r["Ag"])
        )

    # ── вывод ──
    best_row, best = results[best_idx]
    st.success(
        f"**Рациональный объём:** {_vol_label(best_row)} м³ — "
        f"наибольшая эффективность Эн = {best['E']:.0f} руб. "
        f"(Ag = {best['Ag']:.3f}, Qg = {best['Qg']:.1f} м³/сут, ΔQн = {best['DQ']:.1f} т).")
