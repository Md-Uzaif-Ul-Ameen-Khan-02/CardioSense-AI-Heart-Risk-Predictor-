import datetime as dt
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="CardioSense AI | Heart Risk Predictor",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(1200px 600px at 10% -10%, rgba(255, 75, 110, 0.18), transparent 60%),
        radial-gradient(900px 500px at 100% 0%, rgba(80, 120, 255, 0.18), transparent 55%),
        #0b0f1a;
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1300px; }

/* Hero */
.hero {
    position: relative; overflow: hidden;
    padding: 34px 38px; border-radius: 24px;
    background: linear-gradient(135deg, rgba(255,75,110,0.20), rgba(80,120,255,0.18));
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
    margin-bottom: 22px;
}
.hero h1 { margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.5px; color: #fff; }
.hero h1 span {
    background: linear-gradient(90deg, #ff4b6e, #ff9f6e);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { margin: 8px 0 0; color: #b9c2d9; font-size: 1.02rem; max-width: 760px; }
.pulse {
    position: absolute; right: 38px; top: 26px; font-size: 3.6rem;
    animation: beat 1.4s infinite; filter: drop-shadow(0 0 18px rgba(255,75,110,.7));
}
@keyframes beat { 0%,100% {transform: scale(1);} 15% {transform: scale(1.18);} 30% {transform: scale(1);} 45% {transform: scale(1.12);} }

.badge {
    display: inline-block; padding: 4px 12px; margin: 14px 8px 0 0; border-radius: 999px;
    font-size: .74rem; font-weight: 600; letter-spacing: .4px; color: #dfe6ff;
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12);
}

/* Cards */
.card {
    padding: 22px 24px; border-radius: 20px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.09);
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.30);
    height: 100%;
}
.card h3 { margin: 0 0 4px; font-size: 1.02rem; color: #fff; font-weight: 700; }
.card .sub { color: #8f9ab8; font-size: .82rem; margin-bottom: 10px; }

.kpi { text-align: left; }
.kpi .label { color: #8f9ab8; font-size: .78rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.kpi .value { color: #fff; font-size: 1.9rem; font-weight: 800; margin-top: 4px; }
.kpi .note { color: #8f9ab8; font-size: .8rem; margin-top: 2px; }

.verdict { padding: 22px 26px; border-radius: 20px; margin-bottom: 18px; }
.verdict.high { background: linear-gradient(135deg, rgba(255,59,92,.28), rgba(255,59,92,.08)); border: 1px solid rgba(255,59,92,.55); }
.verdict.low  { background: linear-gradient(135deg, rgba(34,214,143,.25), rgba(34,214,143,.07)); border: 1px solid rgba(34,214,143,.5); }
.verdict h2 { margin: 0; font-size: 1.5rem; font-weight: 800; color: #fff; }
.verdict p { margin: 6px 0 0; color: #d3daee; font-size: .95rem; }

.chip { display: inline-block; padding: 5px 12px; margin: 4px 6px 4px 0; border-radius: 999px; font-size: .8rem; font-weight: 600; }
.chip.warn { background: rgba(255,159,67,.15); color: #ffb870; border: 1px solid rgba(255,159,67,.4); }
.chip.ok   { background: rgba(34,214,143,.13); color: #5be3ae; border: 1px solid rgba(34,214,143,.35); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1424 0%, #0b0f1a 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}
section[data-testid="stSidebar"] .stMarkdown h2 { font-size: 1.15rem; font-weight: 700; }

/* Buttons */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    width: 100%; border: 0; border-radius: 14px; padding: .8rem 1rem;
    font-weight: 700; font-size: 1rem; color: #fff;
    background: linear-gradient(90deg, #ff4b6e, #ff7a59);
    box-shadow: 0 10px 25px rgba(255,75,110,.35);
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 14px 32px rgba(255,75,110,.5); color: #fff;
}

/* Tabs */
button[data-baseweb="tab"] { font-weight: 600; }

.disclaimer { color: #7c87a6; font-size: .78rem; text-align: center; margin-top: 28px; line-height: 1.5; }

/* ---------- Responsive layout ---------- */
.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); margin-bottom: 10px; }
.grid .card { height: auto; }
.mobile-hint {
    display: none; align-items: center; gap: 10px; margin-bottom: 16px;
    padding: 12px 16px; border-radius: 14px; font-size: .88rem; color: #dfe6ff;
    background: rgba(80,120,255,.14); border: 1px solid rgba(80,120,255,.4);
}

/* Let Streamlit columns wrap and stack instead of squeezing */
div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 1rem; }
div[data-testid="stColumn"], div[data-testid="column"] { min-width: min(100%, 320px); }

/* Charts and tables never overflow their container */
.js-plotly-plot, .plotly, div[data-testid="stPlotlyChart"] { max-width: 100%; }
div[data-testid="stDataFrame"] { max-width: 100%; overflow-x: auto; }

/* Tabs scroll sideways on small screens */
div[data-baseweb="tab-list"] { overflow-x: auto; scrollbar-width: none; }
div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }

/* Fluid type */
.hero h1 { font-size: clamp(1.7rem, 4.2vw, 2.5rem); }
.kpi .value { font-size: clamp(1.4rem, 3vw, 1.9rem); }

@media (max-width: 992px) {
    .block-container { padding-left: 1.2rem; padding-right: 1.2rem; }
    .hero { padding: 28px 28px; }
}

@media (max-width: 768px) {
    .block-container { padding: 1rem .8rem 2.5rem; }
    .hero { padding: 22px 20px; border-radius: 18px; }
    .hero p { font-size: .92rem; }
    .pulse { position: static; display: block; font-size: 2.4rem; margin-bottom: 6px; }
    .badge { margin-top: 10px; font-size: .68rem; }
    .card { padding: 16px; border-radius: 16px; }
    .verdict { padding: 16px 18px; border-radius: 16px; }
    .verdict h2 { font-size: 1.2rem; }
    .grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .mobile-hint { display: flex; }
    button[data-baseweb="tab"] { padding-left: 10px; padding-right: 10px; font-size: .85rem; }
}

@media (max-width: 480px) {
    .grid { grid-template-columns: 1fr; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Load model artifacts (cached)
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading model...")
def load_artifacts():
    here = Path(__file__).resolve().parent
    search_dirs = [here, here.parent, Path.cwd()]

    def find(name: str) -> Path:
        # Case-insensitive lookup in the app folder, its parent, and the working folder
        for d in search_dirs:
            if d.is_dir():
                for p in d.iterdir():
                    if p.is_file() and p.name.lower() == name.lower():
                        return p
        raise FileNotFoundError(name)

    model = joblib.load(find("knn_heart.pkl"))
    scaler = joblib.load(find("scaler.pkl"))
    columns = joblib.load(find("columns.pkl"))
    return model, scaler, columns


try:
    model, scaler, expected_columns = load_artifacts()
except FileNotFoundError as e:
    here = Path(__file__).resolve().parent
    st.error(f"Model file missing: {e}")
    for d in [here, here.parent]:
        st.write(f"Files in `{d}`:", sorted(p.name for p in d.iterdir()))
    st.info("Make sure KNN_heart.pkl, scaler.pkl and columns.pkl are in one of the folders listed above.")
    st.stop()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def predict(inputs: dict):
    raw_input = {
        "Age": inputs["age"],
        "RestingBP": inputs["resting_bp"],
        "Cholesterol": inputs["cholesterol"],
        "FastingBS": inputs["fasting_bs"],
        "MaxHR": inputs["max_hr"],
        "Oldpeak": inputs["oldpeak"],
        "Sex_" + inputs["sex"]: 1,
        "ChestPainType_" + inputs["chest_pain"]: 1,
        "RestingECG_" + inputs["resting_ecg"]: 1,
        "ExerciseAngina_" + inputs["exercise_angina"]: 1,
        "ST_Slope_" + inputs["st_slope"]: 1,
    }
    df = pd.DataFrame([raw_input])
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[expected_columns]
    scaled = scaler.transform(df)
    pred = int(model.predict(scaled)[0])

    prob = None
    if hasattr(model, "predict_proba"):
        classes = list(model.classes_)
        prob = float(model.predict_proba(scaled)[0][classes.index(1)]) if 1 in classes else None
    return pred, prob


def gauge(prob: float) -> go.Figure:
    pct = prob * 100
    color = "#22d68f" if pct < 35 else "#ffb020" if pct < 65 else "#ff3b5c"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 46, "color": "#fff"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#6b7694"},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35], "color": "rgba(34,214,143,0.15)"},
                    {"range": [35, 65], "color": "rgba(255,176,32,0.15)"},
                    {"range": [65, 100], "color": "rgba(255,59,92,0.18)"},
                ],
            },
        )
    )
    fig.update_layout(height=290, margin=dict(l=20, r=20, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter"})
    return fig


def radar(inputs: dict) -> go.Figure:
    # Each metric scaled 0-100 where 100 = most concerning end of the range
    def scale(v, lo, hi):
        return max(0, min(100, (v - lo) / (hi - lo) * 100))

    cats = ["Age", "Blood pressure", "Cholesterol", "ST depression", "Low max HR"]
    patient = [
        scale(inputs["age"], 18, 100),
        scale(inputs["resting_bp"], 80, 200),
        scale(inputs["cholesterol"], 100, 600),
        scale(inputs["oldpeak"], 0, 6),
        100 - scale(inputs["max_hr"], 60, 220),
    ]
    healthy = [scale(40, 18, 100), scale(120, 80, 200), scale(190, 100, 600), 0, 100 - scale(165, 60, 220)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=healthy + healthy[:1], theta=cats + cats[:1], fill="toself", name="Typical healthy",
                                  line=dict(color="#22d68f"), fillcolor="rgba(34,214,143,0.15)"))
    fig.add_trace(go.Scatterpolar(r=patient + patient[:1], theta=cats + cats[:1], fill="toself", name="You",
                                  line=dict(color="#ff4b6e"), fillcolor="rgba(255,75,110,0.25)"))
    fig.update_layout(
        height=330, margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter", "color": "#c9d1e8"},
        polar=dict(bgcolor="rgba(255,255,255,0.03)",
                   radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)", showticklabels=False),
                   angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")),
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


def indicators(i: dict):
    flags = []
    if i["resting_bp"] >= 140: flags.append(("High resting blood pressure", True))
    elif i["resting_bp"] >= 130: flags.append(("Elevated resting blood pressure", True))
    else: flags.append(("Resting blood pressure in range", False))

    if i["cholesterol"] >= 240: flags.append(("High cholesterol", True))
    elif i["cholesterol"] >= 200: flags.append(("Borderline cholesterol", True))
    else: flags.append(("Cholesterol in range", False))

    flags.append(("Fasting blood sugar above 120 mg/dL", True) if i["fasting_bs"] == 1 else ("Fasting blood sugar normal", False))
    flags.append(("Exercise-induced angina present", True) if i["exercise_angina"] == "Y" else ("No exercise-induced angina", False))
    flags.append(("Significant ST depression", True) if i["oldpeak"] >= 2 else ("ST depression low", False))
    flags.append(("Asymptomatic chest pain pattern", True) if i["chest_pain"] == "ASY" else ("Chest pain type not asymptomatic", False))
    flags.append(("Flat/Down ST slope", True) if i["st_slope"] in ("Flat", "Down") else ("Upward ST slope", False))
    flags.append(("Age 55+", True) if i["age"] >= 55 else ("Age under 55", False))
    return flags


# ----------------------------------------------------------------------------
# Sidebar: inputs
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🩺 Patient Profile")
    st.caption("Fill in the clinical details, then run the analysis.")

    with st.form("patient_form"):
        st.markdown("**Demographics**")
        age = st.slider("Age", 18, 100, 40)
        sex_label = st.radio("Sex", ["Male", "Female"], horizontal=True)

        st.markdown("**Vitals & Labs**")
        resting_bp = st.number_input("Resting Blood Pressure (mm Hg)", 80, 200, 120)
        cholesterol = st.number_input("Cholesterol (mg/dL)", 100, 600, 200)
        fasting_label = st.radio("Fasting Blood Sugar > 120 mg/dL", ["No", "Yes"], horizontal=True)

        st.markdown("**Cardiac Tests**")
        chest_pain = st.selectbox(
            "Chest Pain Type",
            ["ATA", "NAP", "TA", "ASY"],
            format_func=lambda x: {"ATA": "ATA - Atypical Angina", "NAP": "NAP - Non-Anginal Pain",
                                   "TA": "TA - Typical Angina", "ASY": "ASY - Asymptomatic"}[x],
        )
        resting_ecg = st.selectbox(
            "Resting ECG", ["Normal", "ST", "LVH"],
            format_func=lambda x: {"Normal": "Normal", "ST": "ST-T wave abnormality", "LVH": "Left ventricular hypertrophy"}[x],
        )
        max_hr = st.slider("Max Heart Rate", 60, 220, 150)
        angina_label = st.radio("Exercise-Induced Angina", ["No", "Yes"], horizontal=True)
        oldpeak = st.slider("Oldpeak (ST Depression)", 0.0, 6.0, 1.0, 0.1)
        st_slope = st.selectbox("ST Slope", ["Up", "Flat", "Down"])

        submitted = st.form_submit_button("🔍 Analyze Risk")

inputs = {
    "age": age,
    "sex": "M" if sex_label == "Male" else "F",
    "chest_pain": chest_pain,
    "resting_bp": resting_bp,
    "cholesterol": cholesterol,
    "fasting_bs": 1 if fasting_label == "Yes" else 0,
    "resting_ecg": resting_ecg,
    "max_hr": max_hr,
    "exercise_angina": "Y" if angina_label == "Yes" else "N",
    "oldpeak": oldpeak,
    "st_slope": st_slope,
}

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="pulse">🫀</div>
        <h1>Cardio<span>Sense</span> AI</h1>
        <p>An intelligent heart-risk screening dashboard powered by a K-Nearest Neighbours model.
        Enter clinical details in the sidebar and get an instant, visual risk assessment.</p>
        <span class="badge">KNN MODEL</span>
        <span class="badge">11 CLINICAL FEATURES</span>
        <span class="badge">INSTANT RESULTS</span>
    </div>
    <div class="mobile-hint">👈 <span>On a phone? Tap the <b>&raquo;</b> arrow at the top-left to open the patient form.</span></div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Run prediction
# ----------------------------------------------------------------------------
if submitted:
    with st.spinner("Analyzing patient data..."):
        pred, prob = predict(inputs)
    st.session_state["result"] = {"pred": pred, "prob": prob, "inputs": dict(inputs), "time": dt.datetime.now()}

result = st.session_state.get("result")

if not result:
    steps = [
        ("📝", "1. Enter details", "Use the sidebar to provide the patient's vitals, labs and ECG findings."),
        ("⚡", "2. Run analysis", "Click Analyze Risk. The model scales your inputs and finds the nearest matching cases."),
        ("📊", "3. Review insights", "See the risk gauge, profile radar, clinical indicators and a downloadable report."),
    ]
    cards = "".join(f'<div class="card"><h3>{i} {t}</h3><div class="sub">{d}</div></div>' for i, t, d in steps)
    st.markdown(f'<div class="grid">{cards}</div>', unsafe_allow_html=True)
    st.info("👈 Start by filling the form in the sidebar.")
else:
    pred, prob, res_in = result["pred"], result["prob"], result["inputs"]
    high = pred == 1

    if high:
        st.markdown(
            '<div class="verdict high"><h2>⚠️ Elevated Risk Detected</h2>'
            "<p>The model predicts this profile is at risk of heart disease / stroke. Please consult a qualified cardiologist.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="verdict low"><h2>✅ Low Risk Profile</h2>'
            "<p>The model predicts this profile is not at risk. Keep up regular check-ups and a healthy lifestyle.</p></div>",
            unsafe_allow_html=True,
        )

    kpis = [
        ("Prediction", "At Risk" if high else "Not at Risk", "Model classification"),
        ("Risk Score", f"{prob*100:.0f}%" if prob is not None else "N/A", "Neighbour-based probability"),
        ("Blood Pressure", f"{res_in['resting_bp']}", "mm Hg (resting)"),
        ("Max Heart Rate", f"{res_in['max_hr']}", "beats per minute"),
    ]
    kpi_html = "".join(
        f'<div class="card kpi"><div class="label">{l}</div><div class="value">{v}</div><div class="note">{n}</div></div>'
        for l, v, n in kpis
    )
    st.markdown(f'<div class="grid">{kpi_html}</div>', unsafe_allow_html=True)

    st.write("")
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Risk Analysis", "🧬 Clinical Indicators", "💡 Recommendations", "📄 Report"])

    with tab1:
        a, b = st.columns(2)
        with a:
            st.markdown('<div class="card"><h3>Risk Gauge</h3><div class="sub">Share of nearest neighbours with heart disease</div></div>', unsafe_allow_html=True)
            if prob is not None:
                st.plotly_chart(gauge(prob), use_container_width=True, config={"displayModeBar": False})
            else:
                st.warning("This model does not expose probabilities.")
        with b:
            st.markdown('<div class="card"><h3>Profile vs Typical Healthy</h3><div class="sub">Further from centre = more concerning</div></div>', unsafe_allow_html=True)
            st.plotly_chart(radar(res_in), use_container_width=True, config={"displayModeBar": False})

    with tab2:
        flags = indicators(res_in)
        st.markdown('<div class="card"><h3>Rule-based clinical checks</h3><div class="sub">General reference thresholds, separate from the model output</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip {"warn" if w else "ok"}">{"⚠️" if w else "✔"} {t}</span>' for t, w in flags)
        st.markdown(chips + "</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("**Submitted values**")
        st.dataframe(
            pd.DataFrame({"Feature": list(res_in.keys()), "Value": [str(v) for v in res_in.values()]}),
            use_container_width=True, hide_index=True,
        )

    with tab3:
        tips = [
            ("🥗", "Eat heart-healthy", "Favour vegetables, whole grains, fish and nuts; limit salt, sugar and processed fats."),
            ("🏃", "Stay active", "Aim for about 150 minutes of moderate exercise per week, as your doctor permits."),
            ("🚭", "Avoid tobacco & limit alcohol", "Smoking is one of the strongest modifiable cardiac risk factors."),
            ("🩸", "Monitor regularly", "Track blood pressure, cholesterol and blood sugar with periodic check-ups."),
            ("😴", "Sleep & stress", "Seven to eight hours of sleep and stress management support heart health."),
        ]
        tip_html = "".join(f'<div class="card"><h3>{ic} {t}</h3><div class="sub">{d}</div></div>' for ic, t, d in tips)
        st.markdown(f'<div class="grid">{tip_html}</div>', unsafe_allow_html=True)
        if high:
            st.warning("Because the model flagged elevated risk, please book an appointment with a cardiologist for a proper evaluation.")

    with tab4:
        report_df = pd.DataFrame([{**res_in, "prediction": "At Risk" if high else "Not at Risk",
                                   "risk_score_pct": round(prob * 100, 1) if prob is not None else None,
                                   "generated_at": result["time"].strftime("%Y-%m-%d %H:%M")}])
        st.markdown('<div class="card"><h3>Assessment report</h3><div class="sub">Download this assessment as a CSV file.</div></div>', unsafe_allow_html=True)
        st.dataframe(report_df.T.rename(columns={0: "Value"}), use_container_width=True)
        st.download_button("⬇️ Download report (CSV)", report_df.to_csv(index=False).encode("utf-8"),
                           file_name="cardiosense_report.csv", mime="text/csv")

st.markdown(
    '<div class="disclaimer">⚕️ CardioSense AI is an educational machine-learning demo and is not a medical device. '
    "It does not replace professional medical diagnosis, advice or treatment.</div>",
    unsafe_allow_html=True,
)
