from pathlib import Path
from io import BytesIO
from datetime import datetime
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

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
    --sidebar-width: 235px;
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
    max-width: 980px;
    padding-top: 1rem;
    padding-bottom: 2rem;
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
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    margin-bottom: 1.35rem !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.95rem !important;
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
    min-height: 44px;
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
    font-size: 0.98rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
}

/* Main hero */
.hero {
    padding: 1.2rem 1.4rem;
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
    font-size: 1.75rem;
    font-weight: 850;
    letter-spacing: -0.035em;
    position: relative;
    z-index: 1;
}

.hero p {
    margin-top: .65rem;
    margin-bottom: 0;
    color: #e0e7ff;
    font-size: 0.90rem;
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
    padding: 0.75rem 0.9rem;
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

[data-testid="stMetricValue"] > div {
    font-size: 1.85rem !important;
}

[data-testid="stMetricLabel"] p {
    font-size: 0.88rem !important;
}

h2 {
    font-size: 1.45rem !important;
}

h3 {
    font-size: 1.15rem !important;
}

[data-testid="stForm"] {
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 0.85rem 1rem 1rem 1rem;
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
    padding: 15px;
    border-radius: 16px;
    border: 1px solid var(--border);
    margin: 14px 0 20px 0;
    box-shadow: 0 14px 34px rgba(15,23,42,0.05);
}

.cgpa-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.cgpa-card {
    padding: 14px;
    border-radius: 14px;
    text-align: center;
    font-size: 0.95rem;
    border: 1px solid rgba(15,23,42,0.04);
}

.cgpa-title {
    font-weight: 850;
    font-size: 0.98rem;
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

/* About page */
.about-hero {
    background: linear-gradient(120deg, #eef2ff, #f5f3ff);
    border: 1px solid #ddd6fe;
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 10px 28px rgba(79, 70, 229, 0.08);
}

.about-hero-title {
    font-size: 1.35rem;
    font-weight: 850;
    color: #312e81;
    margin-bottom: 6px;
}

.about-hero-subtitle {
    color: #475569;
    font-size: 0.92rem;
}

.about-card {
    border-radius: 16px;
    padding: 16px;
    min-height: 165px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.about-blue {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
}

.about-green {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.about-purple {
    background: linear-gradient(135deg, #faf5ff, #ede9fe);
}

.about-orange {
    background: linear-gradient(135deg, #fff7ed, #ffedd5);
}

.about-yellow {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
}

.about-red {
    background: linear-gradient(135deg, #fff1f2, #fee2e2);
}

.about-card h4 {
    margin: 0 0 10px 0;
    font-size: 1.02rem;
    color: #172033;
}

.about-list-item {
    background: rgba(255,255,255,0.72);
    border-radius: 10px;
    padding: 8px 10px;
    margin: 7px 0;
    font-size: 0.88rem;
}

.about-model {
    background: rgba(255,255,255,0.70);
    border-radius: 10px;
    padding: 9px 10px;
    margin: 8px 0;
    font-size: 0.88rem;
}

.about-target {
    text-align: center;
    border-radius: 14px;
    padding: 14px 10px;
    min-height: 92px;
    border: 1px solid rgba(148,163,184,0.20);
}

.about-target-title {
    font-size: 1rem;
    font-weight: 850;
    margin-bottom: 5px;
}

.about-target-range {
    font-size: 0.82rem;
    color: #475569;
}

/* Keep overview metric values readable and fully visible */
[data-testid="stMetricValue"] > div {
    font-size: 1.45rem !important;
    line-height: 1.15 !important;
    white-space: normal !important;
}

[data-testid="stMetricLabel"] p {
    font-size: 0.78rem !important;
}

</style>
""", unsafe_allow_html=True)


def make_batch_pdf_bytes(result_df, best_model):
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Student Batch Prediction Report",
        author="Student Performance Prediction System",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    story = [
        Paragraph("Student Batch Prediction Report", title_style),
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | "
            f"Final model: {best_model} | Total students: {len(result_df):,}",
            subtitle_style,
        ),
    ]

    category_order = ["At Risk", "Average", "Good", "Excellent"]
    counts = result_df["Final_Prediction"].value_counts().reindex(
        category_order,
        fill_value=0,
    )

    summary_data = [
        ["Performance Category", "Number of Students"],
        *[[category, int(counts[category])] for category in category_order],
    ]

    summary_table = Table(summary_data, colWidths=[70 * mm, 45 * mm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.HexColor("#ffffff"),
            colors.HexColor("#f8fafc"),
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.extend([
        Paragraph("Prediction Summary", styles["Heading2"]),
        summary_table,
        Spacer(1, 8 * mm),
        Paragraph("Detailed Prediction Results", styles["Heading2"]),
    ])

    preferred_columns = [
        "Student_ID",
        "Student_Name",
        "Number_of_Subjects",
        "Average_Score",
        "Attendance_Pct",
        "Study_Hours_Per_Day",
        "Previous_CGPA",
        "KNN_Prediction",
        "SVM_Prediction",
        "ANN_Prediction",
        "Final_Prediction",
        "Final_Confidence",
    ]
    report_columns = [column for column in preferred_columns if column in result_df.columns]
    pdf_df = result_df[report_columns].copy()

    if "Final_Confidence" in pdf_df.columns:
        pdf_df["Final_Confidence"] = pdf_df["Final_Confidence"].map(
            lambda value: f"{value:.1%}"
        )

    rows_per_page = 24
    for start in range(0, len(pdf_df), rows_per_page):
        page_df = pdf_df.iloc[start:start + rows_per_page]
        table_data = [report_columns] + page_df.astype(str).values.tolist()

        available_width = landscape(A4)[0] - 24 * mm
        column_width = available_width / max(len(report_columns), 1)

        detail_table = Table(
            table_data,
            repeatRows=1,
            colWidths=[column_width] * len(report_columns),
        )
        detail_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#f8fafc"),
            ]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(detail_table)

        if start + rows_per_page < len(pdf_df):
            story.append(PageBreak())

    document.build(story)
    output.seek(0)
    return output.getvalue()


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



def make_excel_bytes(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Prediction Results")
        worksheet = writer.sheets["Prediction Results"]
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 32)
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
    output.seek(0)
    return output.getvalue()


def make_template_bytes():
    template = pd.DataFrame([
        {
            "Student_ID": "ID0001",
            "Student_Name": "Example Student",
            "Number_of_Subjects": 5,
            "Average_Score": 75.0,
            "Attendance_Pct": 85.0,
            "Study_Hours_Per_Day": 3.0,
            "Previous_CGPA": 3.20,
        },
        {
            "Student_ID": "ID0002",
            "Student_Name": "Example Student 2",
            "Number_of_Subjects": 6,
            "Average_Score": 62.5,
            "Attendance_Pct": 72.0,
            "Study_Hours_Per_Day": 2.0,
            "Previous_CGPA": 2.60,
        },
    ])
    return make_excel_bytes(template)


def validate_batch_data(batch_df):
    required = [
        "Number_of_Subjects",
        "Average_Score",
        "Attendance_Pct",
        "Study_Hours_Per_Day",
        "Previous_CGPA",
    ]
    errors = []
    missing = [column for column in required if column not in batch_df.columns]
    if missing:
        return ["Missing required columns: " + ", ".join(missing)]
    if batch_df.empty:
        return ["The uploaded file does not contain any student records."]

    ranges = {
        "Number_of_Subjects": (1, 12),
        "Average_Score": (0, 100),
        "Attendance_Pct": (0, 100),
        "Study_Hours_Per_Day": (0, 24),
        "Previous_CGPA": (0, 4),
    }

    for column, (minimum, maximum) in ranges.items():
        values = pd.to_numeric(batch_df[column], errors="coerce")
        if values.isna().any():
            rows = (values.isna()).to_numpy().nonzero()[0] + 2
            errors.append(f"{column} contains missing or non-numeric values at Excel row(s): " + ", ".join(map(str, rows[:8])))
            continue
        invalid = ~values.between(minimum, maximum, inclusive="both")
        if invalid.any():
            rows = invalid.to_numpy().nonzero()[0] + 2
            errors.append(f"{column} must be between {minimum} and {maximum}. Invalid Excel row(s): " + ", ".join(map(str, rows[:8])))

    subjects = pd.to_numeric(batch_df["Number_of_Subjects"], errors="coerce")
    non_integer = subjects.notna() & (subjects % 1 != 0)
    if non_integer.any():
        rows = non_integer.to_numpy().nonzero()[0] + 2
        errors.append("Number_of_Subjects must contain whole numbers. Invalid Excel row(s): " + ", ".join(map(str, rows[:8])))
    return errors


def predict_batch(batch_df):
    features = [
        "Number_of_Subjects",
        "Average_Score",
        "Attendance_Pct",
        "Study_Hours_Per_Day",
        "Previous_CGPA",
    ]
    result = batch_df.copy()
    best_name = str(evaluation.iloc[0]["Model"])

    for model_name, bundle in models.items():
        model = bundle["model"]
        label_encoder = bundle["label_encoder"]
        encoded = model.predict(batch_df[features]).astype(int)
        labels = label_encoder.inverse_transform(encoded)
        probabilities = model.predict_proba(batch_df[features])
        confidence = probabilities.max(axis=1)
        result[f"{model_name}_Prediction"] = labels
        result[f"{model_name}_Confidence"] = confidence

    result["Final_Prediction"] = result[f"{best_name}_Prediction"]
    result["Final_Confidence"] = result[f"{best_name}_Confidence"]
    result["Best_Model"] = best_name
    return result

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
        "📚 Batch Prediction",
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
        title="Model Performance Comparison",
        height=420
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
        # All inputs are outside st.form so that changes refresh immediately.
        name = st.text_input("Student Name", key="student_name")
        student_id = st.text_input("Student ID", key="student_id")

        number_of_subjects = st.slider(
            "Number of Subjects",
            min_value=1,
            max_value=12,
            value=5,
            key="number_of_subjects"
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
            step=0.5,
            key="attendance"
        )

        study_hours = st.slider(
            "Study Hours Per Day",
            min_value=0.0,
            max_value=12.0,
            value=3.0,
            step=0.1,
            key="study_hours"
        )

        previous_cgpa = st.slider(
            "Previous CGPA",
            min_value=0.0,
            max_value=4.0,
            value=3.0,
            step=0.01,
            key="previous_cgpa"
        )

        submit = st.button(
            "Predict",
            use_container_width=True,
            type="primary"
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

elif page == "Batch Prediction":
    st.subheader("Batch Student Prediction")
    st.markdown(
        "Upload an Excel or CSV file containing multiple students. "
        "The system will validate the data, predict all records using KNN, SVM and ANN, "
        "and let you download a completed Excel file."
    )

    template_col, note_col = st.columns([1, 2])
    with template_col:
        st.download_button(
            "⬇️ Download Excel Template",
            data=make_template_bytes(),
            file_name="student_batch_prediction_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with note_col:
        st.info(
            "Required columns: Number_of_Subjects, Average_Score, Attendance_Pct, "
            "Study_Hours_Per_Day and Previous_CGPA. Student_ID and Student_Name are optional."
        )

    uploaded_file = st.file_uploader(
        "Upload completed Excel or CSV file",
        type=["xlsx", "xls", "csv"],
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                batch_df = pd.read_csv(uploaded_file)
            else:
                batch_df = pd.read_excel(uploaded_file)

            errors = validate_batch_data(batch_df)
            if errors:
                st.error("The uploaded file cannot be processed.")
                for error in errors:
                    st.write(f"• {error}")
            else:
                required = [
                    "Number_of_Subjects",
                    "Average_Score",
                    "Attendance_Pct",
                    "Study_Hours_Per_Day",
                    "Previous_CGPA",
                ]
                for column in required:
                    batch_df[column] = pd.to_numeric(batch_df[column])

                st.success(f"{len(batch_df):,} student records loaded successfully.")
                c1, c2, c3 = st.columns(3)
                c1.metric("Uploaded Students", f"{len(batch_df):,}")
                c2.metric("Required Features", "5")
                c3.metric("Final Model", str(evaluation.iloc[0]["Model"]))

                st.markdown("#### Uploaded Data Preview")
                st.dataframe(batch_df.head(50), hide_index=True, use_container_width=True)

                if st.button("Predict All Students", type="primary", use_container_width=True):
                    with st.spinner("Generating batch predictions..."):
                        st.session_state["batch_prediction_result"] = predict_batch(batch_df)
                    st.rerun()

        except ImportError:
            st.error("Excel support is unavailable. Add openpyxl to requirements.txt and redeploy.")
        except Exception as error:
            st.error(f"Unable to process the uploaded file: {error}")

    if "batch_prediction_result" in st.session_state:
        result_df = st.session_state["batch_prediction_result"]
        st.success(f"Batch prediction completed for {len(result_df):,} students.")

        order = ["At Risk", "Average", "Good", "Excellent"]
        counts = result_df["Final_Prediction"].value_counts().reindex(order, fill_value=0)
        summary_cols = st.columns(4)
        for col, category in zip(summary_cols, order):
            col.metric(category, int(counts[category]))

        summary_df = counts.rename_axis("Performance Category").reset_index(name="Students")
        fig = px.bar(
            summary_df,
            x="Performance Category",
            y="Students",
            text="Students",
            title="Batch Prediction Distribution",
            category_orders={"Performance Category": order},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(title_x=0.5, height=390)
        st.plotly_chart(fig, use_container_width=True)

        display_df = result_df.copy()
        for column in ["KNN_Confidence", "SVM_Confidence", "ANN_Confidence", "Final_Confidence"]:
            display_df[column] = display_df[column].map(lambda value: f"{value:.1%}")

        st.markdown("#### Complete Prediction Results")

        filter_col1, filter_col2 = st.columns([2, 1])

        with filter_col1:
            search_text = st.text_input(
                "Search by Student ID or Student Name",
                placeholder="Type a student ID or name...",
                key="batch_result_search",
            )

        with filter_col2:
            category_filter = st.selectbox(
                "Filter by Performance Category",
                ["All Categories", "At Risk", "Average", "Good", "Excellent"],
                key="batch_category_filter",
            )

        filtered_df = display_df.copy()

        if search_text.strip():
            searchable_columns = [
                column for column in ["Student_ID", "Student_Name"]
                if column in filtered_df.columns
            ]
            if searchable_columns:
                search_mask = pd.Series(False, index=filtered_df.index)
                for column in searchable_columns:
                    search_mask = search_mask | filtered_df[column].astype(str).str.contains(
                        search_text.strip(),
                        case=False,
                        na=False,
                    )
                filtered_df = filtered_df[search_mask]

        if category_filter != "All Categories":
            filtered_df = filtered_df[
                filtered_df["Final_Prediction"] == category_filter
            ]

        st.caption(
            f"Showing {len(filtered_df):,} of {len(display_df):,} predicted records."
        )
        st.dataframe(filtered_df, hide_index=True, use_container_width=True)

        low_confidence_count = int(
            (result_df["Final_Confidence"] < 0.60).sum()
        )
        if low_confidence_count > 0:
            st.warning(
                f"{low_confidence_count:,} prediction(s) have confidence below 60%. "
                "These records may require lecturer review."
            )

        excel_col, pdf_col, clear_col = st.columns(3)

        with excel_col:
            st.download_button(
                "⬇️ Download Predicted Excel",
                data=make_excel_bytes(result_df),
                file_name="student_batch_predictions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with pdf_col:
            st.download_button(
                "📄 Download PDF Report",
                data=make_batch_pdf_bytes(
                    result_df,
                    str(evaluation.iloc[0]["Model"]),
                ),
                file_name="student_batch_prediction_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with clear_col:
            if st.button("↻ Upload Another File", type="secondary", use_container_width=True):
                del st.session_state["batch_prediction_result"]
                st.rerun()


elif page == "Model Results":
    st.subheader("Model Evaluation Dashboard")

    metric_columns = ["Accuracy", "Precision", "Recall", "F1 Score"]
    model_column = "Model"

    best_index = evaluation["Accuracy"].idxmax()
    best_row = evaluation.loc[best_index]
    best_model = str(best_row[model_column])

    st.success(
        f"🏆 Best Model: {best_model} "
        f"with {best_row['Accuracy']:.2%} accuracy"
    )

    st.markdown("### 📊 Model Accuracy Comparison")

    model_colors = {
        "KNN": "#3B82F6",
        "SVM": "#10B981",
        "ANN": "#8B5CF6"
    }

    accuracy_fig = px.bar(
        evaluation,
        x=model_column,
        y="Accuracy",
        color=model_column,
        color_discrete_map=model_colors,
        text=evaluation["Accuracy"].map(lambda value: f"{value:.1%}"),
        title="Accuracy of KNN, SVM and ANN",
        labels={"Accuracy": "Accuracy", model_column: "Model"}
    )
    accuracy_fig.update_traces(textposition="outside")
    accuracy_fig.update_yaxes(
        tickformat=".0%",
        range=[0, min(1.0, float(evaluation["Accuracy"].max()) + 0.12)]
    )
    accuracy_fig.update_layout(
        title_x=0.5,
        height=420,
        margin=dict(l=20, r=20, t=70, b=20)
    )
    st.plotly_chart(accuracy_fig, use_container_width=True)

    st.markdown("### 🤖 Individual Model Performance")

    model_order = ["KNN", "SVM", "ANN"]
    model_tabs = st.tabs(model_order)

    for tab, model_name in zip(model_tabs, model_order):
        with tab:
            model_row = evaluation[
                evaluation[model_column].astype(str).str.upper() == model_name
            ]

            if model_row.empty:
                st.warning(f"No evaluation result was found for {model_name}.")
                continue

            model_row = model_row.iloc[0]

            st.markdown(f"#### {model_name} Performance")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Accuracy", f"{model_row['Accuracy']:.2%}")

            with c2:
                st.metric("Precision", f"{model_row['Precision']:.2%}")

            with c3:
                st.metric("Recall", f"{model_row['Recall']:.2%}")

            with c4:
                st.metric("F1 Score", f"{model_row['F1 Score']:.2%}")

            single_model_data = pd.DataFrame({
                "Metric": metric_columns,
                "Score": [float(model_row[col]) for col in metric_columns]
            })

            model_fig = px.bar(
                single_model_data,
                x="Metric",
                y="Score",
                text=single_model_data["Score"].map(
                    lambda value: f"{value:.1%}"
                ),
                title=f"{model_name} Evaluation Metrics",
                labels={"Score": "Score", "Metric": "Metric"},
                color_discrete_sequence=[model_colors[model_name]]
            )
            model_fig.update_traces(textposition="outside")
            model_fig.update_yaxes(
                tickformat=".0%",
                range=[0, 1.05]
            )
            model_fig.update_layout(
                title_x=0.5,
                height=390,
                margin=dict(l=20, r=20, t=70, b=20)
            )
            st.plotly_chart(model_fig, use_container_width=True)

            if model_name == best_model.upper():
                st.success(
                    f"{model_name} achieved the highest accuracy and was "
                    "selected as the best-performing model."
                )
            else:
                st.info(
                    f"{model_name} was evaluated using Accuracy, Precision, "
                    "Recall and F1 Score."
                )

    st.markdown("### 📋 Complete Model Comparison")

    show = evaluation.copy()
    for col in metric_columns:
        show[col] = show[col].map(lambda value: f"{value:.2%}")

    st.dataframe(
        show,
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "Accuracy shows the overall percentage of correct predictions. "
        "Precision measures how reliable the model's predictions are. "
        "Recall measures how many actual cases were identified, while "
        "F1 Score balances precision and recall."
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
    st.subheader("About This Assignment")

    st.markdown(
        """
<div class="about-hero">
    <div class="about-hero-title">🎓 Student Performance Prediction</div>
    <div class="about-hero-subtitle">
        A supervised machine learning classification assignment for predicting overall student academic performance.
    </div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown("### 📋 Assignment Overview")

    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

    with overview_col1:
        st.metric("Assignment Type", "Supervised")

    with overview_col2:
        st.metric("Task", "Classification")

    with overview_col3:
        st.metric("Students", f"{len(df):,}")

    with overview_col4:
        st.metric("Features", "5")

    st.markdown("### 📊 Input Features and Models")

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown(
            """
<div class="about-card about-blue">
    <h4>📋 Input Features</h4>
    <div class="about-list-item">1. Number of Subjects</div>
    <div class="about-list-item">2. Average Score</div>
    <div class="about-list-item">3. Attendance Rate</div>
    <div class="about-list-item">4. Study Hours Per Day</div>
    <div class="about-list-item">5. Previous CGPA</div>
</div>
""",
            unsafe_allow_html=True
        )

    with right_col:
        st.markdown(
            """
<div class="about-card about-green">
    <h4>🤖 Machine Learning Models</h4>
    <div class="about-model"><b>KNN</b> — K-Nearest Neighbours</div>
    <div class="about-model"><b>SVM</b> — Support Vector Machine</div>
    <div class="about-model"><b>ANN</b> — Artificial Neural Network</div>
</div>
""",
            unsafe_allow_html=True
        )

    st.markdown("### 🎯 Target Classes")

    target_col1, target_col2, target_col3, target_col4 = st.columns(4)

    with target_col1:
        st.markdown(
            """
<div class="about-target about-green">
    <div class="about-target-title">Excellent</div>
    <div class="about-target-range">CGPA 3.50 – 4.00</div>
</div>
""",
            unsafe_allow_html=True
        )

    with target_col2:
        st.markdown(
            """
<div class="about-target about-blue">
    <div class="about-target-title">Good</div>
    <div class="about-target-range">CGPA 3.00 – 3.49</div>
</div>
""",
            unsafe_allow_html=True
        )

    with target_col3:
        st.markdown(
            """
<div class="about-target about-yellow">
    <div class="about-target-title">Average</div>
    <div class="about-target-range">CGPA 2.50 – 2.99</div>
</div>
""",
            unsafe_allow_html=True
        )

    with target_col4:
        st.markdown(
            """
<div class="about-target about-red">
    <div class="about-target-title">At Risk</div>
    <div class="about-target-range">CGPA below 2.50</div>
</div>
""",
            unsafe_allow_html=True
        )

    st.markdown("### 📚 Dataset Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown(
            """
<div class="about-card about-purple">
    <h4>🗂️ Dataset Source</h4>
    <div class="about-list-item">
        University Student Performance & Habits Dataset from Kaggle
    </div>
    <h4 style="margin-top:14px;">🧩 Feature Engineering</h4>
    <div class="about-list-item">Number of Subjects</div>
    <div class="about-list-item">Average Score</div>
</div>
""",
            unsafe_allow_html=True
        )

    with info_col2:
        st.markdown(
            """
<div class="about-card about-orange">
    <h4>⚠️ Important Note</h4>
    <div class="about-list-item">
        Final CGPA is used only during model training to generate the target class.
    </div>
    <div class="about-list-item">
        It is not included as a prediction input because that would cause data leakage.
    </div>
</div>
""",
            unsafe_allow_html=True
        )
