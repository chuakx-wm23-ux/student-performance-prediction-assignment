from pathlib import Path
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dataset" / "Student_data.csv"
MODELS = ROOT / "models"
RESULTS = ROOT / "results"

st.set_page_config(
    page_title="Student Performance Prediction",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
:root {
    --sidebar-width: 285px;
    --navy: #0f172a;
    --navy-soft: #172554;
    --blue: #2563eb;
    --violet: #7c3aed;
    --surface: #ffffff;
    --surface-soft: #f8fafc;
    --border: #e2e8f0;
    --text: #172033;
    --muted: #64748b;
}

.stApp {
    background:
        radial-gradient(circle at top right, rgba(124, 58, 237, 0.08), transparent 30%),
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 28%),
        #f4f7fb;
    color: var(--text);
}

.block-container {
    max-width: 1250px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    width: var(--sidebar-width) !important;
    min-width: var(--sidebar-width) !important;
    background:
        linear-gradient(180deg, #0f172a 0%, #111c35 58%, #172554 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] > div:first-child {
    width: var(--sidebar-width) !important;
    padding: 1.25rem 1rem 1.5rem 1rem;
}

[data-testid="stSidebar"] * {
    color: white;
}

[data-testid="stSidebar"] h1 {
    font-size: 2.35rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    margin-bottom: 1.35rem !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 1.22rem !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 0.6rem;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 0.72rem 0.85rem;
    transition: all 0.18s ease;
    min-height: 60px;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.10);
    transform: translateX(3px);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(37,99,235,0.95), rgba(124,58,237,0.95));
    border-color: rgba(255,255,255,0.18);
    box-shadow: 0 10px 26px rgba(37,99,235,0.22);
}

[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
}

/* Main hero */
.hero {
    padding: 2.2rem 2.35rem;
    border-radius: 24px;
    color: white;
    background:
        linear-gradient(120deg, rgba(30,58,138,0.98), rgba(37,99,235,0.96), rgba(124,58,237,0.96));
    margin-bottom: 1.5rem;
    box-shadow: 0 22px 55px rgba(37, 99, 235, 0.20);
    position: relative;
    overflow: hidden;
}

.hero:after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    right: -70px;
    top: -95px;
    background: rgba(255,255,255,0.12);
}

.hero h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 850;
    letter-spacing: -0.035em;
    position: relative;
    z-index: 1;
}

.hero p {
    margin-top: .65rem;
    margin-bottom: 0;
    color: #e0e7ff;
    font-size: 1.02rem;
    position: relative;
    z-index: 1;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    border: none;
    border-radius: 14px;
    font-weight: 800;
    color: white;
    min-height: 46px;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
    transition: transform .18s ease, box-shadow .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(37, 99, 235, 0.26);
}

/* High-end black style for Make Another Prediction only */
div[data-testid="stButton"] button[kind="secondary"] {
    background: linear-gradient(135deg, #111827 0%, #020617 100%) !important;
    color: #ffffff !important;
    border: 1px solid #374151 !important;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.28) !important;
}

div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
    border-color: #4b5563 !important;
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(2, 6, 23, 0.38) !important;
}

/* Inputs and cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 10px 28px rgba(15,23,42,0.05);
}

[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-weight: 800 !important;
}

[data-testid="stForm"] {
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.1rem 1.2rem 1.35rem 1.2rem;
    box-shadow: 0 18px 44px rgba(15,23,42,0.06);
}

[data-testid="stDataFrame"],
[data-testid="stImage"],
[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 18px;
}

/* CGPA guide */
.cgpa-guide {
    background: rgba(255,255,255,0.95);
    padding: 22px;
    border-radius: 20px;
    border: 1px solid var(--border);
    margin: 14px 0 20px 0;
    box-shadow: 0 14px 34px rgba(15,23,42,0.05);
}

.cgpa-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.cgpa-card {
    padding: 17px;
    border-radius: 14px;
    text-align: center;
    font-size: 0.95rem;
    border: 1px solid rgba(15,23,42,0.04);
}

.cgpa-title {
    font-weight: 850;
    font-size: 1.06rem;
    margin-bottom: 6px;
}

.excellent { background: #dcfce7; }
.good { background: #dbeafe; }
.average { background: #fef3c7; }
.risk { background: #fee2e2; }

/* Headings */
h1, h2, h3 {
    color: var(--text);
    letter-spacing: -0.02em;
}

@media (max-width: 800px) {
    .cgpa-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .hero h1 {
        font-size: 2rem;
    }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA)

    df["Performance_Category"] = pd.cut(
        df["Final_CGPA"],
        bins=[-float("inf"), 2.5, 3.0, 3.5, float("inf")],
        labels=["At Risk", "Average", "Good", "Excellent"],
        right=False
    )

    return df


@st.cache_resource
def load_models():
    return {
        "KNN": joblib.load(MODELS / "knn_model.joblib"),
        "SVM": joblib.load(MODELS / "svm_model.joblib"),
        "ANN": joblib.load(MODELS / "ann_model.joblib"),
    }


def show_cgpa_guide():
    st.markdown(
        """
<div class="cgpa-guide">
<h3 style="margin-top:0;">CGPA Classification Guide</h3>

<div class="cgpa-grid">

<div class="cgpa-card excellent">
<div class="cgpa-title">Excellent</div>
CGPA 3.50 – 4.00
</div>

<div class="cgpa-card good">
<div class="cgpa-title">Good</div>
CGPA 3.00 – 3.49
</div>

<div class="cgpa-card average">
<div class="cgpa-title">Average</div>
CGPA 2.50 – 2.99
</div>

<div class="cgpa-card risk">
<div class="cgpa-title">At Risk</div>
CGPA below 2.50
</div>

</div>
</div>
""",
        unsafe_allow_html=True
    )


df = load_data()
models = load_models()
evaluation = pd.read_csv(RESULTS / "evaluation.csv")

st.sidebar.title("🎓 Student AI")
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Home",
        "📝 Prediction",
        "📊 Model Results",
        "📈 Dataset",
        "ℹ️ About"
    ],
    label_visibility="collapsed"
)

page = page.split(" ", 1)[1]

st.markdown(
    '<div class="hero">'
    '<h1>Student Performance Prediction</h1>'
    '<p>AI-powered academic performance analysis using KNN, SVM and ANN.</p>'
    '</div>',
    unsafe_allow_html=True
)

if page == "Home":
    best = evaluation.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", f"{len(df):,}")
    c2.metric("Features", "5")
    c3.metric("Best Model", best["Model"])
    c4.metric("Best Accuracy", f"{best['Accuracy']:.1%}")

    chart = evaluation.melt(
        id_vars="Model",
        value_vars=["Accuracy", "Precision", "Recall", "F1 Score"],
        var_name="Metric",
        value_name="Score"
    )

    fig = px.bar(
        chart,
        x="Model",
        y="Score",
        color="Metric",
        barmode="group",
        range_y=[0, 1],
        title="Model Performance Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)


elif page == "Prediction":
    st.subheader("Student Prediction")
    show_cgpa_guide()

    # Show the latest result at the top of the page.
    # This avoids making the user scroll down after pressing Predict.
    if "prediction_result" in st.session_state:
        saved = st.session_state["prediction_result"]

        st.success(f"Predicted Performance: {saved['prediction']}")
        result_col1, result_col2 = st.columns(2)
        result_col1.metric("Confidence", f"{saved['confidence']:.1%}")
        result_col2.metric("Best Model", saved["best_model"])

        st.dataframe(
            saved["result_df"].assign(
                Confidence=saved["result_df"]["Confidence"].map(
                    lambda x: f"{x:.1%}"
                )
            ),
            hide_index=True,
            use_container_width=True
        )

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            st.download_button(
                "⬇️ Download Result",
                saved["report_csv"],
                "prediction_result.csv",
                "text/csv",
                use_container_width=True
            )

        with button_col2:
            if st.button(
                "↻ Make Another Prediction",
                key="make_another_prediction",
                type="secondary",
                use_container_width=True
            ):
                del st.session_state["prediction_result"]
                st.rerun()

    else:
        with st.form("prediction_form"):
            name = st.text_input("Student Name")
            student_id = st.text_input("Student ID")

            number_of_subjects = st.slider(
                "Number of Subjects",
                min_value=1,
                max_value=12,
                value=5
            )

            scores = []
            columns = st.columns(2)

            for i in range(number_of_subjects):
                with columns[i % 2]:
                    score = st.number_input(
                        f"Subject {i + 1} Score",
                        min_value=0.0,
                        max_value=100.0,
                        value=75.0,
                        step=1.0,
                        key=f"subject_{i}"
                    )
                    scores.append(score)

            average_score = sum(scores) / len(scores)
            st.info(f"Calculated Average Score: {average_score:.2f}")

            attendance = st.slider(
                "Attendance Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=85.0,
                step=0.5
            )

            study_hours = st.slider(
                "Study Hours Per Day",
                min_value=0.0,
                max_value=12.0,
                value=3.0,
                step=0.1
            )

            previous_cgpa = st.slider(
                "Previous CGPA",
                min_value=0.0,
                max_value=4.0,
                value=3.0,
                step=0.01
            )

            submit = st.form_submit_button(
                "Predict",
                use_container_width=True
            )

        if submit:
            input_df = pd.DataFrame([{
                "Number_of_Subjects": number_of_subjects,
                "Average_Score": average_score,
                "Attendance_Pct": attendance,
                "Study_Hours_Per_Day": study_hours,
                "Previous_CGPA": previous_cgpa,
            }])

            predictions = []
            best_name = evaluation.iloc[0]["Model"]

            for model_name, bundle in models.items():
                model = bundle["model"]
                label_encoder = bundle["label_encoder"]

                pred_code = int(model.predict(input_df)[0])
                pred_label = label_encoder.inverse_transform([pred_code])[0]

                probabilities = model.predict_proba(input_df)[0]
                confidence = float(probabilities[pred_code])

                predictions.append({
                    "Model": model_name,
                    "Prediction": pred_label,
                    "Confidence": confidence,
                })

            result_df = pd.DataFrame(predictions)
            best_row = result_df[result_df["Model"] == best_name].iloc[0]

            report = pd.DataFrame([{
                "Student Name": name,
                "Student ID": student_id,
                "Number of Subjects": number_of_subjects,
                "Average Score": average_score,
                "Attendance Rate": attendance,
                "Study Hours Per Day": study_hours,
                "Previous CGPA": previous_cgpa,
                "Prediction": best_row["Prediction"],
                "Best Model": best_name,
                "Confidence": best_row["Confidence"],
            }])

            st.session_state["prediction_result"] = {
                "prediction": best_row["Prediction"],
                "confidence": float(best_row["Confidence"]),
                "best_model": best_name,
                "result_df": result_df,
                "report_csv": report.to_csv(index=False).encode("utf-8"),
            }

            st.rerun()

elif page == "Model Results":
    st.subheader("Model Evaluation")

    show = evaluation.copy()

    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        show[col] = show[col].map(lambda x: f"{x:.2%}")

    st.dataframe(show, hide_index=True, use_container_width=True)

    selected = st.selectbox(
        "Select Model",
        ["ANN", "SVM", "KNN"]
    )

    st.image(
        RESULTS / f"{selected.lower()}_confusion_matrix.png",
        caption=f"{selected} Confusion Matrix",
        use_container_width=True
    )


elif page == "Dataset":
    st.subheader("Dataset Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(
            df,
            x="Average_Score",
            nbins=25,
            title="Average Score Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            df,
            x="Attendance_Pct",
            y="Average_Score",
            color="Performance_Category",
            title="Attendance vs Average Score"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        df.head(100),
        hide_index=True,
        use_container_width=True
    )


else:
    st.subheader("About This Project")

    st.markdown("""
### Student Performance Prediction

This project applies **supervised machine learning classification** to predict a student's overall academic performance.

### Models Used

- K-Nearest Neighbours (KNN)
- Support Vector Machine (SVM)
- Artificial Neural Network (ANN)

### Input Features

- Number of Subjects
- Average Score
- Attendance Rate
- Study Hours Per Day
- Previous CGPA

### Target Classes

- Excellent
- Good
- Average
- At Risk

### Important Note

`Final_CGPA` is used only during model training to generate the target class.  
It is not included as an input on the Prediction page because that would cause **data leakage**.

### Dataset Source

University Student Performance & Habits Dataset from Kaggle, with additional feature engineering for:

- `Number_of_Subjects`
- `Average_Score`
""")
