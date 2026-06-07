# StimCore — калькулятор глинокислотной обработки (ГКО)

Инженерное Streamlit-приложение по методике «Проектирование кислотной обработки»
(Приложение В). ГКО — последовательная обработка: сначала СКР (HCl), затем ГКР
(HCl + HF). Результаты задач сохраняются в `st.session_state` и подхватываются
следующими шагами.

## Запуск локально

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Деплой на Streamlit Community Cloud

1. Запушьте репозиторий на GitHub.
2. На https://share.streamlit.io → **Create app** → выберите репозиторий.
3. **Main file path:** `app.py`. Deploy.

`requirements.txt` и `runtime.txt` (Python 3.11) подхватываются автоматически.

## Структура

```
app.py                     навигация-pipeline + раздел «Месторождение»
gko_config.json            константы месторождения (редактируются в UI)
modules/
  theme.py                 светлая тема StimCore (apply_theme, stimcore_header)
  constants.py             загрузка/сохранение конфигурации
  input_data.py            общие данные скважины
  reference_tables.py      справочники В.4/В.5/В.20/В.26/В.27/В.29
  ui.py                    общие UI-хелперы (calc_gate, clear_result)
  tasks/
    task_v11.py            Целесообразность ГКО (render(cfg))
    task_v12.py            Расход и давление нагнетания
    task_v13.py            Продавочная и вытесняющая жидкость
    task_v14.py            Изменение пористости
    task_v15.py            Эффективность ГКО
```

## Навигация (Задачи ГКО)

1. Целесообразность ГКО
2. Расход и давление нагнетания
3. Продавочная и вытесняющая жидкость
4. Изменение пористости
5. Эффективность ГКО
