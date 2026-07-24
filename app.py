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
.stApp { background: #f5f7fb; }
.block-container { max-width: 1200px; padding-top: 1.5rem; }

.hero {
    padding: 2rem;
    border-radius: 22px;
    color: white;
    background: linear-gradient(120deg, #1e3a8a, #2563eb, #7c3aed);
    margin-bottom: 1.2rem;
}

.hero h1 {
    margin: 0;
    font-size: 2.3rem;
}

.hero p {
    margin-top: .5rem;
    color: #e0e7ff;
}

[data-testid="stSidebar"] {
    background: #0f172a;
}

[data-testid="stSidebar"] * {
    color: white;
}

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    color: white;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
}

.cgpa-guide {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin: 14px 0 20px 0;
}

.cgpa-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.cgpa-card {
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    font-size: 0.95rem;
}

.cgpa-title {
    font-weight: 800;
    font-size: 1.05rem;
    margin-bottom: 5px;
}

.excellent { background: #dcfce7; }
.good { background: #dbeafe; }
.average { background: #fef3c7; }
.risk { background: #fee2e2; }

@media (max-width: 800px) {
    .cgpa-grid {
        grid-template-columns: repeat(2, 1fr);
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
page = st.sidebar.radio(
    "Menu",
    ["Home", "Prediction", "Model Results", "Dataset", "About"]
)

st.markdown(
    '<div class="hero">'
    '<h1>Student Performance Prediction</h1>'
    '<p>Supervised classification using KNN, SVM and ANN.</p>'
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

        submit = st.form_submit_button("Predict")

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

        st.success(f"Predicted Performance: {best_row['Prediction']}")
        st.metric("Confidence", f"{best_row['Confidence']:.1%}")

        st.dataframe(
            result_df.assign(
                Confidence=result_df["Confidence"].map(lambda x: f"{x:.1%}")
            ),
            hide_index=True,
            use_container_width=True
        )

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

        st.download_button(
            "Download Result",
            report.to_csv(index=False).encode("utf-8"),
            "prediction_result.csv",
            "text/csv"
        )


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
