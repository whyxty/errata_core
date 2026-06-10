"""Проверка целесообразности выбора скважины для ГКО.

Самостоятельная задача (объединяет методики В.1 «полная информация» и
В.2 «ограниченная информация»). Результат НЕ сохраняется в session_state.

Критерии (Приложение В):
    В.1  ОП  = Kф / Kпот          < 1      — резерв продуктивности
    В.2  ОД  = Qф / Qож           < 1      — резерв дебита
    В.9  Qож = Σ qуд(m₀)·hэф               — ожидаемый дебит (табл. В.2)
    В.2  m₀  > mгр                         — пласт является коллектором
    В.3  hпга > hпр                        — толщина поглощающих пластов
    В.11 hэф_сум ≥ hпр                     — суммарная толщина разреза
    В.10 q   ≥ qпр                         — приёмистость
    В.12 Cгл ≤ Cг.пр                       — глинистость
    В.13 εот = εобр / εскв        > 0.5     — относит. гидропроводность
    В.14 kэнр = pпл /(ρgH·10⁻⁶)   > 0.7     — энергетический потенциал
    В.4  kms ≥ ksпр (1.1)                   — рост пористости после СКР
    В.5  kmg ≥ kgпр (1.1)                   — рост пористости после ГКР
    В.6  kmsg = kms·kmg                     — суммарный рост пористости
    В.7  Cк ≥ Cк.пр (3 %) → СКО→ГКО; иначе → только ГКО
    В.8  kв.о = hпга / hэф_сум              — охват разреза (рекомендация)
"""
import math

import pandas as pd
import streamlit as st

from modules.ui import calc_gate, clear_result


# ─────────────────────── значения по умолчанию ───────────────────────
_DEF_SCALARS = {
    "Kf": 0.0, "Kpot": 0.0, "Qf": 0.0, "q": 0.0,
    "p_pl": 0.0, "H": 0.0, "C_k": 0.0, "C_gl": 0.0,
    "kms": 1.0, "kmg": 1.0, "h_pga": 0.0,
}

_COLS = ["Кровля, м", "Подошва, м", "hэф, м", "m0, %", "k0, мкм²", "Обрабатываемый"]

_DEF_LAYERS = [
    {"Кровля, м": 0.0, "Подошва, м": 0.0, "hэф, м": 0.0, "m0, %": 0.0, "k0, мкм²": 0.0, "Обрабатываемый": False},
]

# ── Общий пример (заполняет данные под все критерии: ОП и ОД, εот, kэнр и др.) ──
EXAMPLE = {
    "Kf": 16.0, "Kpot": 51.0, "Qf": 50.0, "q": 150.0,
    "p_pl": 25.0, "H": 2800.0, "C_k": 4.0, "C_gl": 5.0,
    "kms": 1.2, "kmg": 1.1, "h_pga": 17.0,
    "layers": [
        {"Кровля, м": 2733.0, "Подошва, м": 2740.0, "hэф, м": 7.0,  "m0, %": 12.0, "k0, мкм²": 0.0210, "Обрабатываемый": True},
        {"Кровля, м": 2756.0, "Подошва, м": 2768.0, "hэф, м": 12.0, "m0, %": 9.8,  "k0, мкм²": 0.0030, "Обрабатываемый": False},
        {"Кровля, м": 2785.0, "Подошва, м": 2795.0, "hэф, м": 10.0, "m0, %": 13.9, "k0, мкм²": 0.0450, "Обрабатываемый": True},
        {"Кровля, м": 2808.0, "Подошва, м": 2820.0, "hэф, м": 12.0, "m0, %": 10.5, "k0, мкм²": 0.0080, "Обрабатываемый": False},
        {"Кровля, м": 2823.0, "Подошва, м": 2851.0, "hэф, м": 18.0, "m0, %": 9.6,  "k0, мкм²": 0.0030, "Обрабатываемый": False},
    ],
}

# ── Пример «только ГКО»: низкая карбонатность Cк < 3 % → СКО не применяют (В.7) ──
EXAMPLE_GKO = {
    "Kf": 16.0, "Kpot": 51.0, "Qf": 50.0, "q": 150.0,
    "p_pl": 25.0, "H": 2800.0, "C_k": 2.0, "C_gl": 6.0,
    "kms": 1.1, "kmg": 1.15, "h_pga": 17.0,
    "layers": [
        {"Кровля, м": 2733.0, "Подошва, м": 2740.0, "hэф, м": 7.0,  "m0, %": 12.0, "k0, мкм²": 0.0210, "Обрабатываемый": True},
        {"Кровля, м": 2756.0, "Подошва, м": 2768.0, "hэф, м": 12.0, "m0, %": 9.8,  "k0, мкм²": 0.0030, "Обрабатываемый": False},
        {"Кровля, м": 2785.0, "Подошва, м": 2795.0, "hэф, м": 10.0, "m0, %": 13.9, "k0, мкм²": 0.0450, "Обрабатываемый": True},
        {"Кровля, м": 2808.0, "Подошва, м": 2820.0, "hэф, м": 12.0, "m0, %": 10.5, "k0, мкм²": 0.0080, "Обрабатываемый": False},
        {"Кровля, м": 2823.0, "Подошва, м": 2851.0, "hэф, м": 18.0, "m0, %": 9.6,  "k0, мкм²": 0.0030, "Обрабатываемый": False},
    ],
}


# ─────────────────────── пороги из конфига ───────────────────────
def _thresholds(cfg: dict) -> dict:
    wc = cfg.get("well_check", {}) if cfg else {}
    return {
        "m_gr":      wc.get("m_gr", 8.0),
        "h_pr":      wc.get("h_pr", 5.0),
        "ks_pr":     wc.get("ks_pr", 1.1),
        "kg_pr":     wc.get("kg_pr", 1.1),
        "C_k_pr":    wc.get("C_k_pr", 3.0),
        "C_gl_pr":   wc.get("C_gl_pr", 10.0),
        "q_pr":      wc.get("q_pr", 24.0),
        "eps_ot_pr": wc.get("eps_ot_pr", 0.5),
        "k_enr_pr":  wc.get("k_enr_pr", 0.7),
        "kvo_low":   wc.get("kvo_low", 0.1),
        "kvo_high":  wc.get("kvo_high", 0.5),
        "rho":       wc.get("rho_water", 1000.0),
        "g":         wc.get("g", 9.81),
        "sdt":       wc.get("specific_debit_table", [
            {"m_min": 7, "m_max": 9, "q": 0.35},
            {"m_min": 9, "m_max": 11, "q": 0.65},
            {"m_min": 11, "m_max": 13, "q": 2.0},
            {"m_min": 13, "m_max": 15, "q": 3.0},
            {"m_min": 15, "m_max": 999, "q": 4.5},
        ]),
    }


def specific_debit(m0: float, table: list) -> float:
    """Удельный ожидаемый дебит по диапазону пористости (табл. В.2)."""
    for row in table:
        if row["m_min"] <= m0 < row["m_max"]:
            return float(row["q"])
    return 0.0


# ─────────────────────── расчёт ───────────────────────
def solve(scalars: dict, layers: list, T: dict) -> dict:
    rows = [r for r in layers if (r.get("hэф, м") or 0) > 0 or (r.get("m0, %") or 0) > 0]

    h_ef_sum = sum(float(r.get("hэф, м") or 0) for r in rows)
    collectors = [(r, float(r.get("m0, %") or 0) > T["m_gr"]) for r in rows]
    n_collectors = sum(1 for _, ok in collectors if ok)

    eps_skv = sum(float(r.get("hэф, м") or 0) * float(r.get("k0, мкм²") or 0) for r in rows)
    eps_obr = sum(float(r.get("hэф, м") or 0) * float(r.get("k0, мкм²") or 0)
                  for r in rows if r.get("Обрабатываемый"))
    has_perm = eps_skv > 0
    eps_ot = (eps_obr / eps_skv) if has_perm else None

    Q_ozh = sum(specific_debit(float(r.get("m0, %") or 0), T["sdt"]) * float(r.get("hэф, м") or 0)
                for r in rows)

    Kf, Kpot = scalars["Kf"], scalars["Kpot"]
    Qf, q = scalars["Qf"], scalars["q"]
    p_pl, H = scalars["p_pl"], scalars["H"]
    C_k, C_gl = scalars["C_k"], scalars["C_gl"]
    kms, kmg = scalars["kms"], scalars["kmg"]
    h_pga = scalars["h_pga"]

    OP = (Kf / Kpot) if Kpot > 0 else None
    OD = (Qf / Q_ozh) if (Qf > 0 and Q_ozh > 0) else None
    p_gst = T["rho"] * T["g"] * H * 1e-6 if H > 0 else None
    k_enr = (p_pl / p_gst) if (p_gst and p_gst > 0) else None
    k_vo = (h_pga / h_ef_sum) if h_ef_sum > 0 else None
    kmsg = kms * kmg

    # ── список критериев: (имя, формула, значение, порог, статус) ──
    # статус: True=✓, False=✗, None=нет данных
    crit = []
    crit.append({"Критерий": "Продуктивность (В.1)", "Формула": "ОП = Kф/Kпот < 1",
                 "Значение": f"{OP:.3f}" if OP is not None else "—",
                 "Порог": "< 1",
                 "ok": (OP < 1) if OP is not None else None, "key": True})
    crit.append({"Критерий": "Дебит (В.2)", "Формула": "ОД = Qф/Qож < 1",
                 "Значение": f"{OD:.3f}" if OD is not None else "—",
                 "Порог": "< 1",
                 "ok": (OD < 1) if OD is not None else None, "key": True})
    crit.append({"Критерий": "Пористость (В.2)", "Формула": "m₀ > mгр",
                 "Значение": f"{n_collectors} из {len(rows)}",
                 "Порог": f"> {T['m_gr']:g} %",
                 "ok": (n_collectors >= 1) if rows else None, "key": True})
    crit.append({"Критерий": "Толщина разреза (В.11)", "Формула": "hэф_сум ≥ hпр",
                 "Значение": f"{h_ef_sum:.1f} м",
                 "Порог": f"≥ {T['h_pr']:g} м",
                 "ok": (h_ef_sum >= T["h_pr"]) if h_ef_sum > 0 else None, "key": True})
    crit.append({"Критерий": "Толщина поглощающих (В.3)", "Формула": "hпга > hпр",
                 "Значение": f"{h_pga:.1f} м",
                 "Порог": f"> {T['h_pr']:g} м",
                 "ok": (h_pga > T["h_pr"]) if h_pga > 0 else None, "key": False})
    crit.append({"Критерий": "Приёмистость (В.10)", "Формула": "q ≥ qпр",
                 "Значение": f"{q:.0f} м³/сут" if q > 0 else "—",
                 "Порог": f"≥ {T['q_pr']:g}",
                 "ok": (q >= T["q_pr"]) if q > 0 else None, "key": False})
    crit.append({"Критерий": "Глинистость (В.12)", "Формула": "Cгл ≤ Cг.пр",
                 "Значение": f"{C_gl:.1f} %" if C_gl > 0 else "—",
                 "Порог": f"≤ {T['C_gl_pr']:g} %",
                 "ok": (C_gl <= T["C_gl_pr"]) if C_gl > 0 else None, "key": True})
    crit.append({"Критерий": "Гидропроводность (В.13)", "Формула": "εот = εобр/εскв > 0.5",
                 "Значение": f"{eps_ot:.3f}" if eps_ot is not None else "—",
                 "Порог": f"> {T['eps_ot_pr']:g}",
                 "ok": (eps_ot > T["eps_ot_pr"]) if eps_ot is not None else None, "key": False})
    crit.append({"Критерий": "Энергетика (В.14)", "Формула": "kэнр = pпл/pгст > 0.7",
                 "Значение": f"{k_enr:.3f}" if k_enr is not None else "—",
                 "Порог": f"> {T['k_enr_pr']:g}",
                 "ok": (k_enr > T["k_enr_pr"]) if k_enr is not None else None, "key": False})
    crit.append({"Критерий": "Рост пористости СКР (В.4)", "Формула": "kms ≥ ksпр",
                 "Значение": f"{kms:.3f}",
                 "Порог": f"≥ {T['ks_pr']:g}",
                 "ok": (kms >= T["ks_pr"]), "key": False})
    crit.append({"Критерий": "Рост пористости ГКР (В.5)", "Формула": "kmg ≥ kgпр",
                 "Значение": f"{kmg:.3f}",
                 "Порог": f"≥ {T['kg_pr']:g}",
                 "ok": (kmg >= T["kg_pr"]), "key": False})

    # ── тип обработки (В.7) ──
    if C_k >= T["C_k_pr"] and kms > T["ks_pr"]:
        treatment = "Сначала СКО, затем ГКО"
        treat_note = f"Cк = {C_k:.1f} % ≥ {T['C_k_pr']:g} % и kms = {kms:.2f} > {T['ks_pr']:g}"
    elif C_k < T["C_k_pr"]:
        treatment = "Только ГКО"
        treat_note = f"Cк = {C_k:.1f} % < Cк.пр = {T['C_k_pr']:g} %"
    else:
        treatment = "ГКО (СКР неэффективен)"
        treat_note = f"Cк ≥ Cк.пр, но kms = {kms:.2f} ≤ ksпр = {T['ks_pr']:g} — рост от СКР недостаточен"

    # ── охват (В.8) ──
    if k_vo is None:
        cover = "—"
    elif k_vo < T["kvo_low"]:
        cover = f"kв.о = {k_vo:.2f} < {T['kvo_low']:g} → вторичная перфорация / поинтервальные КО"
    elif k_vo >= T["kvo_high"]:
        cover = f"kв.о = {k_vo:.2f} ≥ {T['kvo_high']:g} → обработка всего разреза"
    else:
        cover = (f"{T['kvo_low']:g} < kв.о = {k_vo:.2f} < {T['kvo_high']:g} → "
                 "первая КО — весь разрез, далее поинтервально")

    # ── итоговый вердикт по ключевым критериям ──
    key_results = [c["ok"] for c in crit if c["key"]]
    key_applicable = [v for v in key_results if v is not None]
    failed_keys = [c["Критерий"] for c in crit if c["key"] and c["ok"] is False]
    suitable = (len(key_applicable) > 0) and all(key_applicable)

    return {
        "rows": rows, "h_ef_sum": h_ef_sum, "n_collectors": n_collectors,
        "eps_skv": eps_skv, "eps_obr": eps_obr, "eps_ot": eps_ot,
        "Q_ozh": Q_ozh, "OP": OP, "OD": OD, "p_gst": p_gst, "k_enr": k_enr,
        "k_vo": k_vo, "kmsg": kmsg, "crit": crit,
        "treatment": treatment, "treat_note": treat_note, "cover": cover,
        "suitable": suitable, "failed_keys": failed_keys,
        "collectors": collectors,
    }


# ─────────────────────── UI ───────────────────────
def _load_example(ex: dict):
    for k in _DEF_SCALARS:
        st.session_state[f"v11_{k}"] = ex[k]
    st.session_state["v11_layers"] = [dict(r) for r in ex["layers"]]
    # сменить ключ редактора → форсировать пере-инициализацию данными примера
    st.session_state["v11_editor_ver"] = st.session_state.get("v11_editor_ver", 0) + 1
    # только подставить данные; результат — по кнопке РАССЧИТАТЬ
    clear_result("v11")


def render(cfg: dict):
    T = _thresholds(cfg)

    title_col, b1_col, b2_col = st.columns([4, 1.2, 1.2])
    title_col.subheader("Проверка целесообразности выбора скважины для ГКО")
    if b1_col.button("Пример СКО→ГКО", key="ex_v11", type="secondary", use_container_width=True):
        _load_example(EXAMPLE); st.rerun()
    if b2_col.button("Пример ГКО", key="ex_v11_gko", type="secondary", use_container_width=True):
        _load_example(EXAMPLE_GKO); st.rerun()

    st.caption("Объединяет методики В.1 (критерий продуктивности ОП) и "
               "В.2 (критерий дебита ОД). Расчёт — в реальном времени.")

    with st.expander("О задаче", expanded=False):
        st.markdown("""
**Суть:** прежде чем закачивать кислоту — доказать, что обработка даст эффект.
Задача отвечает на три вопроса: *стоит ли* обрабатывать скважину, *какой кислотой*
и *по какой схеме*.

**Как решается:** скважина проверяется по одиннадцати критериям Приложения В (В.1–В.14):

- **Есть ли резерв?** ОП = Кф/Кпот и ОД = Qф/Qож — насколько скважина недорабатывает
  относительно потенциала пласта. Если работает на полную (ОП ≈ 1) — кислота ничего не добавит.
- **Дойдёт ли кислота куда нужно?** Приёмистость (В.10), поглощающие пласты (В.3),
  относительная гидропроводность (В.13) — раствор должен поглотиться именно
  загрязнёнными интервалами.
- **Сработает ли химия?** Глинистость (В.12) — чтобы реакция HF не дала нерастворимый
  осадок; лабораторные kms, kmg (В.4, В.5) — что кислота реально улучшает коллектор;
  карбонатность Cк (В.7) определяет тип: ≥ 3 % — СКО→ГКО, < 3 % — только ГКО.
- **Очистится ли скважина после?** Энергетика kэнр = pпл/pгст (В.14) — хватит ли
  пластового давления вынести продукты реакции.
- **По какой схеме?** Коэффициент охвата kв.о = hпга/hэф (В.8) — весь разрез или поинтервально.

**Дополнительно** оценивается скин-фактор S через уравнение Дюпюи: S > 0 — ПЗП загрязнена
(кислота уберёт загрязнение), S < 0 — зона чистая (цель ГКО — выравнивание профиля приёмистости).

**Результат:** вердикт «пригодна/непригодна», тип обработки, схема охвата, состояние ПЗП.
""")

    with st.expander("Обозначения и критерии", expanded=False):
        st.markdown("""
| Символ | Значение | Условие |
|---|---|---|
| `ОП = Kф/Kпот` | соотношение продуктивности (В.1) | < 1 |
| `ОД = Qф/Qож` | соотношение дебитов (В.2); Qож = Σ qуд·hэф (В.9) | < 1 |
| `m₀ > mгр` | пласт является коллектором (В.2) | для пластов |
| `hпга > hпр` | толщина поглощающих пластов (В.3) | hпр = 5 м |
| `hэф_сум ≥ hпр` | суммарная толщина разреза (В.11) | hпр = 5 м |
| `q ≥ qпр` | приёмистость (В.10) | qпр = 24 м³/сут |
| `Cгл ≤ Cг.пр` | глинистость (В.12) | Cг.пр = 10 % |
| `εот = εобр/εскв` | относит. гидропроводность (В.13); εобр — Σ hэф·k₀ по обрабатываемым | > 0.5 |
| `kэнр = pпл/(ρgH·10⁻⁶)` | энергетический потенциал (В.14) | > 0.7 |
| `kms ≥ ksпр`, `kmg ≥ kgпр` | рост пористости после СКР/ГКР (В.4, В.5) | ≥ 1.1 |
| `Cк ≥ Cк.пр` | выбор СКО→ГКО или только ГКО (В.7) | Cк.пр = 3 % |
| `kв.о = hпга/hэф_сум` | охват разреза (В.8) | рекомендация |
""")

    # ── инициализация состояния ──
    for k, v in _DEF_SCALARS.items():
        st.session_state.setdefault(f"v11_{k}", v)
    st.session_state.setdefault("v11_layers", [dict(r) for r in _DEF_LAYERS])
    st.session_state.setdefault("v11_editor_ver", 0)

    # ── таблица пластов ──
    st.markdown("##### Разрез скважины (пласты)")
    df = pd.DataFrame(st.session_state["v11_layers"])
    for c in _COLS:
        if c not in df.columns:
            df[c] = False if c == "Обрабатываемый" else 0.0
    df = df[_COLS]
    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True,
        key=f"v11_editor_{st.session_state['v11_editor_ver']}",
        column_config={
            "Кровля, м":     st.column_config.NumberColumn("Кровля, м", help="Глубина кровли (верх) пласта", format="%.1f"),
            "Подошва, м":    st.column_config.NumberColumn("Подошва, м", help="Глубина подошвы (низ) пласта", format="%.1f"),
            "hэф, м":        st.column_config.NumberColumn("hэф, м", help="Перфорированная толщина пласта", format="%.1f"),
            "m0, %":         st.column_config.NumberColumn("m₀, %", help="Пористость пласта", format="%.1f"),
            "k0, мкм²":      st.column_config.NumberColumn("k₀, мкм²", help="Проницаемость (опц., для εот)", format="%.4f"),
            "Обрабатываемый":st.column_config.CheckboxColumn("Обрабатываемый", help="Поглощающий/обрабатываемый пласт — для εобр"),
        },
    )
    st.session_state["v11_layers"] = edited.to_dict("records")
    layers = st.session_state["v11_layers"]

    # ── скалярные данные ──
    with st.expander("Параметры скважины", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v11_Kf"]   = c1.number_input("Kф, т/(сут·МПа) — факт. продуктивность",
            value=float(st.session_state["v11_Kf"]), step=1.0)
        st.session_state["v11_Kpot"] = c2.number_input("Kпот, т/(сут·МПа) — потенц. продуктивность",
            value=float(st.session_state["v11_Kpot"]), step=1.0)
        st.session_state["v11_Qf"]   = c3.number_input("Qф, м³/сут — фактический дебит",
            value=float(st.session_state["v11_Qf"]), step=1.0)

        c1, c2, c3 = st.columns(3)
        st.session_state["v11_q"]    = c1.number_input("q, м³/сут — приёмистость",
            value=float(st.session_state["v11_q"]), step=1.0)
        st.session_state["v11_p_pl"] = c2.number_input("pпл, МПа — пластовое давление",
            value=float(st.session_state["v11_p_pl"]), step=0.5)
        st.session_state["v11_H"]    = c3.number_input("H, м — глубина пласта",
            value=float(st.session_state["v11_H"]), step=10.0)

        c1, c2, c3 = st.columns(3)
        st.session_state["v11_C_k"]  = c1.number_input("Cк, % — карбонатность",
            value=float(st.session_state["v11_C_k"]), step=0.1)
        st.session_state["v11_C_gl"] = c2.number_input("Cгл, % — глинистость",
            value=float(st.session_state["v11_C_gl"]), step=0.1)
        st.session_state["v11_h_pga"]= c3.number_input("hпга, м — толщина поглощающих (термометрия)",
            value=float(st.session_state["v11_h_pga"]), step=1.0)

        c1, c2 = st.columns(2)
        st.session_state["v11_kms"]  = c1.number_input("kms — рост пористости после СКР (лаб.)",
            value=float(st.session_state["v11_kms"]), step=0.01, min_value=1.0)
        st.session_state["v11_kmg"]  = c2.number_input("kmg — рост пористости после ГКР (лаб.)",
            value=float(st.session_state["v11_kmg"]), step=0.01, min_value=1.0)

    scalars = {k: st.session_state[f"v11_{k}"] for k in _DEF_SCALARS}

    # ── кнопка расчёта (общий паттерн для всех задач) ──
    res = calc_gate("v11", lambda: solve(scalars, layers, T),
                    prompt="Заполните разрез и параметры скважины, затем нажмите «РАССЧИТАТЬ».")
    if res is None:
        return

    # ── метрики ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ОП = Kф/Kпот", f"{res['OP']:.3f}" if res["OP"] is not None else "—")
    c2.metric("ОД = Qф/Qож", f"{res['OD']:.3f}" if res["OD"] is not None else "—",
              delta=f"Qож={res['Q_ozh']:.1f}" if res["Q_ozh"] > 0 else None, delta_color="off")
    c3.metric("εот = εобр/εскв", f"{res['eps_ot']:.3f}" if res["eps_ot"] is not None else "—")
    c4.metric("kэнр = pпл/pгст", f"{res['k_enr']:.3f}" if res["k_enr"] is not None else "—")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("hэф_сум, м", f"{res['h_ef_sum']:.1f}")
    c2.metric("Коллекторы (m₀>mгр)", f"{res['n_collectors']} из {len(res['rows'])}")
    c3.metric("kв.о = hпга/hэф", f"{res['k_vo']:.3f}" if res["k_vo"] is not None else "—")
    c4.metric("kmsg = kms·kmg", f"{res['kmsg']:.3f}")

    # ── таблица критериев ──
    st.markdown("##### Критерии целесообразности")
    sym = {True: "✓", False: "✗", None: "—"}
    crit_df = pd.DataFrame([{
        "Критерий": c["Критерий"], "Формула": c["Формула"],
        "Значение": c["Значение"], "Порог": c["Порог"],
        "Статус": sym[c["ok"]],
    } for c in res["crit"]])

    def _row_style(row):
        c = res["crit"][row.name]
        if c["ok"] is True:
            return ["background-color: #ecfdf3"] * len(row)
        if c["ok"] is False:
            return ["background-color: #fef2f2"] * len(row)
        return ["background-color: #f7f8fa"] * len(row)

    st.dataframe(crit_df.style.apply(_row_style, axis=1),
                 use_container_width=True, hide_index=True)

    # ── итоговый вердикт ──
    st.markdown("##### Заключение")
    if res["suitable"]:
        st.success(f"**Скважина пригодна для кислотной обработки.** "
                   f"Тип обработки: **{res['treatment']}**. ({res['treat_note']})")
    elif res["failed_keys"]:
        st.error("**Целесообразность под вопросом** — не выполнены ключевые критерии: "
                 + ", ".join(res["failed_keys"]) + ".")
    else:
        st.warning("Недостаточно данных для заключения — заполните параметры скважины "
                   "и разрез (или нажмите «Пример В.1» / «Пример В.2»).")

    st.info(f"**Тип обработки (В.7):** {res['treatment']}.  \n"
            f"**Охват разреза (В.8):** {res['cover']}")

    # ─────────────────────── Скин-фактор S ───────────────────────
    st.markdown("---")
    st.markdown("##### Скин-фактор S (качество призабойной зоны)")
    st.caption("S — скин-фактор. S > 0 — загрязнение/ухудшение ПЗП; S < 0 — улучшение "
               "(эффект кислотной обработки); S = 0 — идеальная (теоретическая) скважина. "
               "Qф берётся из параметров скважины выше. Поскольку поглощение происходит "
               "только в обрабатываемых пластах (по расходометрии/термометрии), Qт "
               "рассчитывается по их параметрам: h = Σhэф и k̄ = εобр/h — из таблицы разреза.")
    st.latex(r"Q_т = \frac{2\pi \cdot k \cdot h \cdot \Delta P}{\mu \cdot \ln\dfrac{R_к}{r_c}}"
             r"\qquad S = \ln\frac{R_к}{r_c}\left(\frac{Q_ф}{Q_т}-1\right)")
    st.caption("Расчёт ведётся строго по формуле в СИ: k [м²], ΔP [Па], μ [Па·с] → Qт [м³/с], "
               "затем перевод в м³/сут (×86 400).")

    st.session_state.setdefault("v11s_Rk", 200.0)
    st.session_state.setdefault("v11s_rc", 0.1)
    st.session_state.setdefault("v11s_dP", 5.0)
    st.session_state.setdefault("v11s_mu", 1.0)

    Qf_skin = float(st.session_state["v11_Qf"])  # фактический дебит из параметров задачи

    # обрабатываемые (поглощающие) пласты — из таблицы разреза:
    #   h_obr = Σhэф; k̄ = εобр / h_obr (тогда k̄·h_obr = εобр — согласовано с В.13)
    h_obr = sum(float(r.get("hэф, м") or 0) for r in res["rows"] if r.get("Обрабатываемый"))
    k_obr = (res["eps_obr"] / h_obr) if h_obr > 0 else 0.0

    c1, c2 = st.columns(2)
    st.session_state["v11s_Rk"] = c1.number_input("Rк, м — радиус контура питания",
        value=float(st.session_state["v11s_Rk"]), step=10.0)
    st.session_state["v11s_rc"] = c2.number_input("r_c, м — радиус скважины",
        value=float(st.session_state["v11s_rc"]), step=0.01, format="%.3f")

    d1, d2 = st.columns(2)
    st.session_state["v11s_dP"] = d1.number_input("ΔP, МПа — депрессия",
        value=float(st.session_state["v11s_dP"]), step=0.5)
    st.session_state["v11s_mu"] = d2.number_input("μ, мПа·с — вязкость",
        value=float(st.session_state["v11s_mu"]), step=0.1)

    st.caption(f"По обрабатываемым пластам: h = {h_obr:.1f} м; "
               f"k̄ = εобр/h = {res['eps_obr']:.4f}/{h_obr:.1f} = {k_obr:.4f} мкм²."
               if h_obr > 0 else
               "В таблице разреза не отмечены обрабатываемые пласты (или у них не задано k₀).")

    Rk, rc = st.session_state["v11s_Rk"], st.session_state["v11s_rc"]
    ln_ratio = math.log(Rk / rc) if (Rk > 0 and rc > 0 and Rk > rc) else None

    # Qт по Дюпюи (S=0) строго по формуле в СИ:
    #   k: мкм² → м² (×1e-12); ΔP: МПа → Па (×1e6); μ: мПа·с → Па·с (×1e-3)
    #   Qт = 2π·k·h·ΔP / (μ·ln(Rк/rc)) [м³/с] → ×86400 [м³/сут]
    k_si = k_obr * 1e-12                          # м²
    dP_si = st.session_state["v11s_dP"] * 1e6     # Па
    mu_si = st.session_state["v11s_mu"] * 1e-3    # Па·с
    if ln_ratio and mu_si > 0 and h_obr > 0 and k_obr > 0:
        Qt_si = (2 * math.pi * k_si * h_obr * dP_si) / (mu_si * ln_ratio)  # м³/с
        Qt = Qt_si * 86400.0                                               # м³/сут
    else:
        Qt_si, Qt = 0.0, 0.0

    # ── результат ──
    if ln_ratio is None:
        st.warning("Проверьте радиусы: нужно r_c < Rк, оба > 0.")
    elif h_obr <= 0 or k_obr <= 0:
        st.warning("Отметьте обрабатываемые пласты в таблице разреза и задайте им hэф и k₀ — "
                   "по ним считаются h и k̄ для Qт.")
    elif Qt <= 0:
        st.warning("Qт должен быть больше 0.")
    else:
        S = ln_ratio * (Qf_skin / Qt - 1.0)
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Qт (Дюпюи), м³/сут", f"{Qt:.1f}")
        cc2.metric("ln(Rк/r_c)", f"{ln_ratio:.3f}")
        cc3.metric("Qф/Qт", f"{Qf_skin / Qt:.3f}")
        cc4.metric("S — скин-фактор", f"{S:+.2f}")

        def _sci(x: float) -> str:
            """Число в LaTeX-научной записи: 5e-14 → 5{,}0\\cdot10^{-14}."""
            mant, exp = f"{x:.4e}".split("e")
            mant = f"{float(mant):g}"
            e = int(exp)
            return mant if e == 0 else r"%s \cdot 10^{%d}" % (mant, e)

        with st.expander("Подстановка по шагам (СИ)", expanded=True):
            st.markdown("**Шаг 1. Параметры обрабатываемых пластов и перевод в СИ:**")
            st.latex(r"h = \sum h_{эф} = %.1f\ \text{м} \qquad "
                     r"\bar{k} = \frac{\varepsilon_{обр}}{h} = \frac{%.4f}{%.1f} = %.4f\ \text{мкм}^2"
                     % (h_obr, res["eps_obr"], h_obr, k_obr))
            st.latex(r"\bar{k} = %.4f\ \text{мкм}^2 = %s\ \text{м}^2 \qquad "
                     r"\Delta P = %g\ \text{МПа} = %s\ \text{Па} \qquad "
                     r"\mu = %g\ \text{мПа·с} = %s\ \text{Па·с}"
                     % (k_obr, _sci(k_si),
                        st.session_state["v11s_dP"], _sci(dP_si),
                        st.session_state["v11s_mu"], _sci(mu_si)))
            st.markdown("**Шаг 2. Логарифм отношения радиусов:**")
            st.latex(r"\ln\frac{R_к}{r_c} = \ln\frac{%g\ \text{м}}{%g\ \text{м}} = %.3f"
                     % (Rk, rc, ln_ratio))
            st.markdown("**Шаг 3. Теоретический дебит по Дюпюи:**")
            st.latex(
                r"Q_т = \frac{2\pi \cdot %s\ \text{м}^2 \cdot %.1f\ \text{м} \cdot %s\ \text{Па}}"
                r"{%s\ \text{Па·с} \cdot %.3f} = %s\ \text{м}^3/\text{с}"
                % (_sci(k_si), h_obr, _sci(dP_si), _sci(mu_si), ln_ratio, _sci(Qt_si)))
            st.latex(
                r"Q_т = %s\ \text{м}^3/\text{с} \cdot 86\,400\ \text{с/сут} = %.1f\ \text{м}^3/\text{сут}"
                % (_sci(Qt_si), Qt))
            st.markdown("**Шаг 4. Скин-фактор:**")
            st.latex(
                r"S = \ln\frac{%g}{%g}\left(\frac{%.1f\ \text{м}^3/\text{сут}}{%.1f\ \text{м}^3/\text{сут}}-1\right)"
                r" = %.3f \cdot (%.5f) = %.2f"
                % (Rk, rc, Qf_skin, Qt, ln_ratio, Qf_skin / Qt - 1.0, S))
        if S > 0.5:
            st.error(f"S = {S:+.2f} > 0 — призабойная зона загрязнена/ухудшена, "
                     "обработка целесообразна.")
        elif S < -0.5:
            st.success(f"S = {S:+.2f} < 0 — ПЗП улучшена (эффект КО).")
        else:
            st.info(f"S = {S:+.2f} ≈ 0 — близко к идеальной скважине.")
