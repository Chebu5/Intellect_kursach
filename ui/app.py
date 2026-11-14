import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

import streamlit as st
from core.inference_engine import MedicalExpertSystem
from core.explanation import group_explanation
from core.routing import specialist_distribution
from ui.symptom_groups import SYMPTOM_GROUPS, CHRONIC_CONDITIONS

st.set_page_config(page_title="Медицинская ЭС", page_icon="🩺", layout="wide")
st.title("🩺 Экспертная система маршрутизации пациента")

URGENCY_MAP = {"routine": "Планово", "urgent": "Срочно", "emergency": "Экстренно"}

# ---------- ПРОФИЛЬ ПАЦИЕНТА ----------
with st.sidebar:
    st.header("Профиль пациента")
    age = st.number_input("Возраст", 0, 120, 30)
    sex = st.selectbox("Пол", ["male", "female", "unknown"])
    pregnant = (st.selectbox("Беременность", ["no", "yes"])
                if sex == "female" else "no")
    chronic = st.multiselect(
        "Хронические состояния",
        [cid for cid, _ in CHRONIC_CONDITIONS],
        format_func=dict(CHRONIC_CONDITIONS).get,
        default=[],
    )

# ---------- СИМПТОМЫ ----------
# Без st.form: тогда слайдер выраженности появляется сразу после установки галочки.
selected = []
st.subheader("Отметьте симптомы и укажите выраженность (0–10)")
for group, items in SYMPTOM_GROUPS.items():
    with st.expander(group, expanded=False):
        for sid, label in items:
            c1, c2 = st.columns([3, 1])
            with c1:
                checked = st.checkbox(label, key=f"chk_{sid}")
            if checked:
                with c2:
                    sev = st.slider("Выраженность", 0, 10, 5, key=f"sev_{sid}")
                selected.append({"name": sid, "severity": sev})

# ---------- ЗАПУСК ДИАГНОСТИКИ ----------
if st.button("🔍 Диагностировать", type="primary"):
    es = MedicalExpertSystem()
    es.reset()
    es.assert_patient(age=age, sex=sex, pregnant=pregnant)
    for c in chronic:
        es.assert_chronic(c)
    for s in selected:
        es.assert_symptom(s["name"], severity=s["severity"])
    # Результат хранится в session_state, чтобы не пропадал при движении слайдеров
    st.session_state["result"] = es.run()

# ---------- ВЫВОД ----------
result = st.session_state.get("result")
if result:
    if result["red_flags"]:
        st.error("Экстренные состояния!")
        for rf in result["red_flags"]:
            st.error(f"**{rf['action']}**")

    distribution = specialist_distribution(result["all_recommendations"])
    if distribution:
        top = distribution[0]
        st.success(
            f"Наиболее подходящий специалист: "
            f"{top['specialist'].capitalize()} ({top['percent']:.0f}%)"
        )
        st.metric("Срочность", URGENCY_MAP.get(top["urgency"], top["urgency"]))

        st.markdown("#### К какому специалисту обратиться")
        for d in distribution:
            st.progress(
                min(int(d["percent"]), 100),
                text=(f"{d['specialist'].capitalize()} — {d['percent']:.1f}% "
                      f"(уверенность {round(d['cf'] * 100)}%, "
                      f"{URGENCY_MAP.get(d['urgency'], d['urgency'])})"),
            )
    elif not result["red_flags"]:
        st.info("Недостаточно данных для гипотезы. Рекомендован терапевт.")

    if result["syndromes"]:
        st.markdown("#### Гипотезы по убыванию уверенности")
        for s in result["syndromes"]:
            st.progress(min(int(s["cf"] * 100), 100),
                        text=f"{s['type']} — CF {s['cf']:.2f}")

    with st.expander("Цепочка рассуждений (объяснение)"):
        for stage, rules in group_explanation(result["fired_rules"]).items():
            st.markdown(f"**{stage}**")
            for r in rules:
                st.write(f"- `{r}`")
        st.markdown("---")
        st.markdown("**Полная трассировка CLIPS:**")
        st.code(result["trace"], language="text")