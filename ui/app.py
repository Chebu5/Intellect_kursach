import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

import streamlit as st
from core.inference_engine import MedicalExpertSystem
from core.explanation import group_explanation

st.set_page_config(page_title="Медицинская ЭС", page_icon="🩺", layout="wide")
st.title("🩺 Экспертная система маршрутизации пациента")

# ---------- ПРОФИЛЬ ПАЦИЕНТА ----------
with st.sidebar:
    st.header("Профиль пациента")
    age = st.number_input("Возраст", 0, 120, 30)
    sex = st.selectbox("Пол", ["male", "female", "unknown"])
    pregnant = (st.selectbox("Беременность", ["no", "yes"])
                if sex == "female" else "no")
    chronic = st.multiselect(
        "Хронические состояния",
        ["diabetes", "hypertension", "asthma", "copd", "smoker", "anticoagulants"],
        default=[],
    )

# ---------- СИМПТОМЫ ----------
SYMPTOM_GROUPS = {
    "Грудь / сердце / дыхание": [
        ("chest-pain", "Боль или дискомфорт в груди"),
        ("chest-radiation", "Боль отдаёт в руку, шею, челюсть"),
        ("dyspnea", "Одышка"),
        ("palpitations", "Сердцебиение"),
        ("cough", "Кашель"),
        ("fever", "Температура"),
        ("wheezing", "Свистящее дыхание"),
        ("worse-on-inspiration", "Боль усиливается при вдохе"),
        ("sweating", "Холодный пот"),
        ("throat-swelling", "Отёк горла / языка"),
    ],
    "ЖКТ": [
        ("heartburn", "Изжога"),
        ("sour-taste", "Кислый привкус"),
        ("worse-after-meals", "Ухудшение после еды"),
        ("abdomen-pain", "Боль в животе"),
        ("abdomen-rigid", "Твёрдый / напряжённый живот"),
        ("nausea", "Тошнота"),
        ("lower-abdomen-pain", "Боль внизу живота"),
        ("vaginal-discharge", "Выделения из влагалища"),
        ("vaginal-bleeding", "Кровянистые выделения"),
    ],
    "Спина / неврология": [
        ("back-pain", "Боль в спине"),
        ("leg-radiation", "Боль отдаёт в ногу"),
        ("numbness", "Онемение / покалывание"),
        ("muscle-weakness", "Мышечная слабость"),
        ("headache", "Головная боль"),
        ("sudden-onset", "Боль возникла внезапно"),
        ("photophobia", "Светобоязнь"),
        ("visual-aura", "Зрительная аура / вспышки"),
        ("eye-pain", "Боль в области глаза"),
        ("nasal-congestion", "Заложенность носа"),
        ("stress", "Хронический стресс"),
        ("facial-droop", "Опущение лица"),
        ("arm-weakness", "Слабость в руке"),
        ("speech-difficulty", "Нарушение речи"),
    ],
    "Кожа / аллергия": [
        ("skin-rash", "Сыпь"),
        ("itching", "Зуд"),
        ("after-contact", "После контакта с аллергеном"),
        ("mole-change", "Изменилась родинка"),
    ],
    "Эндокринология / общее": [
        ("polyuria", "Частое мочеиспускание"),
        ("polydipsia", "Жажда"),
        ("weight-loss", "Похудание без причины"),
        ("weight-gain", "Набор веса"),
        ("cold-intolerance", "Зябкость"),
        ("fatigue", "Утомляемость"),
        ("confusion", "Спутанность сознания"),
        ("dysuria", "Резь при мочеиспускании"),
        ("flank-pain", "Боль в боку"),
        ("hematuria", "Кровь в моче"),
    ],
    "Психика": [
        ("panic-attack", "Панические атаки"),
        ("low-mood", "Подавленность"),
        ("anhedonia", "Потеря интереса"),
        ("insomnia", "Бессонница"),
        ("suicidal-thoughts", "Суицидальные мысли"),
    ],
}

selected = []
with st.form("symptoms_form"):
    st.subheader("Отметьте симптомы и укажите выраженность (0–10)")
    for group, items in SYMPTOM_GROUPS.items():
        with st.expander(group, expanded=False):
            for sid, label in items:
                c1, c2 = st.columns([3, 1])
                with c1:
                    checked = st.checkbox(label, key=f"chk_{sid}")
                with c2:
                    sev = st.slider("Выраженность", 0, 10, 5, key=f"sev_{sid}") if checked else None
                if checked:
                    selected.append({"name": sid, "severity": sev if sev is not None else 5})
    submitted = st.form_submit_button("🔍 Диагностировать")

# ---------- ВЫВОД ----------
if submitted:
    es = MedicalExpertSystem()
    es.reset()
    es.assert_patient(age=age, sex=sex, pregnant=pregnant)
    for c in chronic:
        es.assert_chronic(c)
    for s in selected:
        es.assert_symptom(s["name"], severity=s["severity"])

    result = es.run()

    if result["red_flags"]:
        st.error("Экстренные состояния!")
        for rf in result["red_flags"]:
            st.error(f"**{rf['action']}**")

    if result["best_recommendation"]:
        rec = result["best_recommendation"]
        st.success(f"Рекомендуемый специалист: {rec['specialist']}")
        col1, col2 = st.columns(2)
        col1.metric("Уверенность", f"{round(rec['cf'] * 100)}%")
        urgency_map = {"routine": "Планово", "urgent": "Срочно", "emergency": "Экстренно"}
        col2.metric("Срочность", urgency_map.get(rec["urgency"], rec["urgency"]))

    if result["syndromes"]:
        st.markdown("Гипотезы по убыванию уверенности")
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