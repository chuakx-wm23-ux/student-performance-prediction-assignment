from pathlib import Path
from io import BytesIO
from datetime import datetime
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import DataPoint
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.image import Image as XLImage
import matplotlib.pyplot as plt

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
        radial-gradient(
            circle at 50% 78%,
            rgba(246, 190, 210, 0.30) 0%,
            rgba(246, 190, 210, 0.14) 22%,
            transparent 42%
        ),
        radial-gradient(
            circle at 18% 14%,
            rgba(132, 171, 235, 0.24) 0%,
            rgba(132, 171, 235, 0.10) 28%,
            transparent 48%
        ),
        linear-gradient(
            180deg,
            #c9d9f3 0%,
            #d7e2f4 26%,
            #dce4f3 50%,
            #d9d8ea 74%,
            #cfc4df 100%
        );
    background-size: cover;
    background-attachment: fixed;
    color: var(--text);
}

@keyframes ambientShift {
    0% {
        background-position: 0% 0%;
    }
    100% {
        background-position: 100% 100%;
    }
}

.block-container {
    max-width: 980px;
    padding-top: .55rem;
    padding-bottom: 2rem;
    background: rgba(255,255,255,0.06);
    border-radius: 28px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    width: var(--sidebar-width) !important;
    min-width: var(--sidebar-width) !important;
    background:
        radial-gradient(circle at 15% 8%, rgba(99, 102, 241, 0.24), transparent 26%),
        linear-gradient(180deg, #0b1220 0%, #111827 48%, #172554 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
    box-shadow: 10px 0 40px rgba(2, 6, 23, 0.18);
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

/* Sidebar footer */
.sidebar-footer {
    position: fixed;
    left: 18px;
    bottom: 4px;
    width: calc(var(--sidebar-width) - 36px);
    padding: 0.80rem 0.8rem 0.35rem;
    border-top: 1px solid rgba(255,255,255,0.10);
    text-align: center;
    line-height: 1.55;
    z-index: 1000;
}

.sidebar-footer .footer-brand {
    color: #ffffff;
    font-size: 0.98rem;
    font-weight: 800;
    letter-spacing: -0.01em;
}

.sidebar-footer .footer-subtitle {
    color: #b8c7e8;
    font-size: 0.68rem;
    font-weight: 600;
    margin-top: 0.12rem;
}

.sidebar-footer .footer-powered {
    color: #8fa2c7;
    font-size: 0.66rem;
    margin-top: 0.28rem;
}

.sidebar-footer .footer-version {
    color: #7e93ba;
    font-size: 0.64rem;
    margin-top: 0.65rem;
}

.sidebar-footer .footer-group {
    color: #afc6ff;
    font-size: 0.69rem;
    font-weight: 700;
    margin-top: 0.15rem;
}

.sidebar-footer .footer-copyright {
    color: #6e82a8;
    font-size: 0.61rem;
    margin-top: 0.5rem;
}

/* Leave enough space so navigation never overlaps the footer */
[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 12.5rem !important;
}

/* Main hero */
.hero {
    padding: 1.1rem 1.35rem;
    border-radius: 28px;
    color: white;
    background:
        radial-gradient(
            circle at 92% 12%,
            rgba(99, 102, 241, 0.22),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #0b1220 0%,
            #111827 48%,
            #172554 100%
        );
    margin-bottom: 1.15rem;
    box-shadow:
        0 22px 48px rgba(2, 6, 23, 0.30),
        inset 0 1px 0 rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}

.hero:after {
    content: "";
    position: absolute;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    right: -85px;
    top: -105px;
    background: rgba(99,102,241,0.18);
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
    color: #cbd5e1;
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

/* Premium Prediction Hub */
.prediction-hub-shell {
    background:
        radial-gradient(circle at top right, rgba(124,58,237,.10), transparent 28%),
        radial-gradient(circle at bottom left, rgba(37,99,235,.08), transparent 26%),
        linear-gradient(180deg, #f8fbff 0%, #f4f7ff 100%);
    border: 1px solid #e2e8f0;
    border-radius: 28px;
    padding: 1.25rem;
    margin-bottom: 1.1rem;
}

.prediction-welcome {
    background:
        linear-gradient(135deg, rgba(15,23,42,.99), rgba(30,58,138,.97), rgba(91,33,182,.94));
    border-radius: 24px;
    padding: 1.05rem 1.35rem;
    margin-bottom: 1.1rem;
    color: white;
    box-shadow: 0 24px 60px rgba(37,99,235,.20);
    position: relative;
    overflow: hidden;
}

.prediction-welcome:after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    right: -80px;
    top: -100px;
    background: rgba(255,255,255,.09);
}

.prediction-eyebrow {
    font-size: .76rem;
    font-weight: 850;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #c7d2fe;
    margin-bottom: .7rem;
    position: relative;
    z-index: 1;
}

.prediction-welcome h2 {
    color: white !important;
    margin: 0;
    font-size: 1.48rem !important;
    line-height: 1.18;
    position: relative;
    z-index: 1;
}

.prediction-welcome p {
    color: #e2e8f0;
    margin: .5rem 0 0;
    line-height: 1.5;
    font-size: .88rem;
    max-width: 880px;
    position: relative;
    z-index: 1;
}

.prediction-mode-card {
    background: rgba(255,255,255,.98);
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: .82rem .92rem .68rem;
    min-height: 176px;
    box-shadow: 0 16px 38px rgba(15,23,42,.07);
    margin-bottom: .8rem;
    transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.prediction-mode-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 24px 55px rgba(37,99,235,.16);
    border-color: #c7d2fe;
}

.prediction-mode-icon {
    width: 52px;
    height: 52px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.62rem;
    margin-bottom: .95rem;
    background: linear-gradient(135deg, #dbeafe, #ede9fe);
    box-shadow: 0 8px 18px rgba(99,102,241,.12);
    transition: transform .22s ease;
}

.prediction-mode-card:hover .prediction-mode-icon {
    transform: translateY(-3px) rotate(-2deg);
}

.prediction-mode-title {
    font-size: 1.18rem;
    font-weight: 850;
    color: #172033;
    margin-bottom: .48rem;
}

.prediction-mode-desc {
    color: #64748b;
    font-size: .85rem;
    line-height: 1.42;
    min-height: 38px;
}

.prediction-mode-feature {
    background: #f8fafc;
    border: 1px solid #eef2f7;
    border-radius: 10px;
    padding: .5rem .65rem;
    margin-top: .48rem;
    color: #334155;
    font-size: .84rem;
    font-weight: 650;
}

.why-system {
    background: rgba(255,255,255,.95);
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 1.1rem 1.2rem;
    margin-top: 1.15rem;
    box-shadow: 0 12px 30px rgba(15,23,42,.05);
}

.why-system-title {
    font-size: 1.02rem;
    font-weight: 850;
    color: #172033;
    margin-bottom: .8rem;
}

.why-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: .65rem;
}

.why-item {
    background: linear-gradient(135deg, #eff6ff, #f5f3ff);
    border: 1px solid #dbeafe;
    border-radius: 14px;
    padding: .8rem .7rem;
    text-align: center;
    font-size: .82rem;
    font-weight: 750;
    color: #334155;
}

.system-footer {
    text-align: center;
    color: #64748b;
    font-size: .78rem;
    padding: 1.2rem 0 .2rem;
    line-height: 1.7;
}


.mode-page-hero {
    background:
        radial-gradient(circle at top right, rgba(124,58,237,.10), transparent 30%),
        linear-gradient(120deg, #dcecff 0%, #e7edff 52%, #efe7ff 100%);
    border: 1px solid #dbeafe;
    border-radius: 20px;
    padding: .95rem 1.15rem;
    margin-bottom: .8rem;
    box-shadow: 0 12px 30px rgba(37,99,235,.08);
}

.mode-page-eyebrow {
    font-size: .70rem;
    font-weight: 850;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #4338ca;
    margin-bottom: .35rem;
}

.mode-page-hero h2 {
    margin: 0;
    color: #172033 !important;
    font-size: 1.28rem !important;
}

.mode-page-hero p {
    margin: .4rem 0 0;
    color: #475569;
    font-size: .86rem;
    line-height: 1.5;
}


.prediction-feature-row {
    display: flex;
    gap: .38rem;
    flex-wrap: wrap;
    margin-top: .5rem;
}
.prediction-feature-chip {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 999px;
    padding: .28rem .5rem;
    color: #334155;
    font-size: .72rem;
    font-weight: 700;
}
.batch-help-box {
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border: 1px solid #dbeafe;
    border-radius: 16px;
    padding: .72rem .85rem;
    color: #334155;
    font-size: .82rem;
    line-height: 1.45;
}

@media (max-width: 900px) {
    .why-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Premium Glass Surfaces */
[data-testid="stMetric"],
[data-testid="stForm"],
[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"],
.cgpa-guide,
.about-card,
.about-hero,
.batch-card,
.why-system,
.prediction-mode-card {
    background:
        linear-gradient(145deg, rgba(255,255,255,0.88), rgba(244,248,255,0.78)) !important;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(148,163,184,0.24) !important;
    box-shadow:
        0 20px 46px rgba(59,130,246,0.12),
        inset 0 1px 0 rgba(255,255,255,0.90);
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stFileUploader"] section,
[data-baseweb="select"] > div {
    border-radius: 14px !important;
    border: 1px solid #dbe4f0 !important;
    background: rgba(255,255,255,0.90) !important;
    transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-baseweb="select"] > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.14) !important;
}

/* Primary buttons */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    border-radius: 15px !important;
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 52%, #7c3aed 100%) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    box-shadow: 0 14px 28px rgba(79,70,229,0.24) !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 18px 34px rgba(79,70,229,0.30) !important;
}

/* Download buttons */
.stDownloadButton > button {
    border-radius: 15px !important;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    box-shadow: 0 14px 28px rgba(16,185,129,0.22) !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 18px 34px rgba(5,150,105,0.28) !important;
}

/* Sidebar navigation */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.10);
    border-color: rgba(255,255,255,0.12);
    transform: translateX(4px);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    box-shadow: 0 12px 28px rgba(79,70,229,0.30);
}

/* Premium KPI cards */
[data-testid="stMetric"] {
    border-radius: 20px !important;
    transition: transform .18s ease, box-shadow .18s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 22px 48px rgba(37,99,235,0.14) !important;
}

/* Smooth page entrance */
.block-container {
    animation: pageFade .45s ease-out;
}

@keyframes pageFade {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Soft scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(226,232,240,0.55);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #94a3b8, #64748b);
    border-radius: 999px;
    border: 2px solid rgba(248,250,252,0.90);
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    .stApp,
    .block-container {
        animation: none !important;
    }

    * {
        transition: none !important;
    }
}

[data-testid="stPlotlyChart"] {
    background:
        linear-gradient(145deg, rgba(247,250,255,0.92), rgba(235,243,255,0.82)) !important;
    border: 1px solid rgba(96,165,250,0.18) !important;
    box-shadow: 0 22px 48px rgba(59,130,246,0.12) !important;
}

[data-testid="stMetric"]:nth-of-type(4n+1) {
    background: linear-gradient(145deg, rgba(239,246,255,0.96), rgba(219,234,254,0.86)) !important;
}
[data-testid="stMetric"]:nth-of-type(4n+2) {
    background: linear-gradient(145deg, rgba(245,243,255,0.96), rgba(237,233,254,0.86)) !important;
}
[data-testid="stMetric"]:nth-of-type(4n+3) {
    background: linear-gradient(145deg, rgba(236,254,255,0.96), rgba(207,250,254,0.82)) !important;
}
[data-testid="stMetric"]:nth-of-type(4n+4) {
    background: linear-gradient(145deg, rgba(240,253,250,0.96), rgba(204,251,241,0.82)) !important;
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



def make_excel_bytes(dataframe):
    """Create a clean, colour-coded Excel file for batch prediction results."""
    export_df = dataframe.copy()

    # Remove technical confidence/model metadata columns from the downloaded file.
    columns_to_remove = [
        column for column in export_df.columns
        if "Confidence" in column or column == "Best_Model"
    ]
    export_df = export_df.drop(columns=columns_to_remove, errors="ignore")

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
    ]
    ordered_columns = [
        column for column in preferred_columns
        if column in export_df.columns
    ]
    remaining_columns = [
        column for column in export_df.columns
        if column not in ordered_columns
    ]
    export_df = export_df[ordered_columns + remaining_columns]

    friendly_headers = {
        "Student_ID": "Student ID",
        "Student_Name": "Student Name",
        "Number_of_Subjects": "Number of Subjects",
        "Average_Score": "Average Score",
        "Attendance_Pct": "Attendance Rate (%)",
        "Study_Hours_Per_Day": "Study Hours Per Day",
        "Previous_CGPA": "Previous CGPA",
        "KNN_Prediction": "KNN Prediction",
        "SVM_Prediction": "SVM Prediction",
        "ANN_Prediction": "ANN Prediction",
        "Final_Prediction": "FINAL PREDICTION",
    }
    export_df = export_df.rename(columns=friendly_headers)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(
            writer,
            index=False,
            sheet_name="Prediction Results",
        )

        workbook = writer.book
        worksheet = writer.sheets["Prediction Results"]

        # Reusable styles.
        navy_fill = PatternFill("solid", fgColor="1E3A8A")
        final_header_fill = PatternFill("solid", fgColor="5B21B6")
        white_font = Font(color="FFFFFF", bold=True)
        body_font = Font(color="172033")
        thin_grey = Side(style="thin", color="D7DEE8")
        cell_border = Border(
            left=thin_grey,
            right=thin_grey,
            top=thin_grey,
            bottom=thin_grey,
        )

        category_fills = {
            "Excellent": PatternFill("solid", fgColor="DCFCE7"),
            "Good": PatternFill("solid", fgColor="DBEAFE"),
            "Average": PatternFill("solid", fgColor="FEF3C7"),
            "At Risk": PatternFill("solid", fgColor="FEE2E2"),
        }
        category_fonts = {
            "Excellent": Font(color="166534", bold=True),
            "Good": Font(color="1D4ED8", bold=True),
            "Average": Font(color="92400E", bold=True),
            "At Risk": Font(color="B91C1C", bold=True),
        }

        # Header styling.
        for cell in worksheet[1]:
            cell.fill = (
                final_header_fill
                if cell.value == "FINAL PREDICTION"
                else navy_fill
            )
            cell.font = white_font
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )
            cell.border = cell_border

        worksheet.row_dimensions[1].height = 30
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
        worksheet.sheet_view.showGridLines = False

        # Identify key prediction columns.
        header_lookup = {
            cell.value: cell.column
            for cell in worksheet[1]
        }
        final_prediction_col = header_lookup.get("FINAL PREDICTION")
        prediction_headers = {
            "KNN Prediction",
            "SVM Prediction",
            "ANN Prediction",
            "FINAL PREDICTION",
        }

        # Body styling with alternating rows.
        for row_index in range(2, worksheet.max_row + 1):
            alternate_fill = (
                PatternFill("solid", fgColor="F8FAFC")
                if row_index % 2 == 0
                else PatternFill("solid", fgColor="FFFFFF")
            )

            for cell in worksheet[row_index]:
                cell.fill = alternate_fill
                cell.font = body_font
                cell.border = cell_border
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                )

                column_header = worksheet.cell(
                    row=1,
                    column=cell.column,
                ).value

                if column_header == "Student Name":
                    cell.alignment = Alignment(
                        horizontal="left",
                        vertical="center",
                    )

                if column_header in prediction_headers:
                    category = str(cell.value)
                    if category in category_fills:
                        cell.fill = category_fills[category]
                        cell.font = category_fonts[category]

            # Make Final Prediction the visual focus.
            if final_prediction_col is not None:
                final_cell = worksheet.cell(
                    row=row_index,
                    column=final_prediction_col,
                )
                final_cell.border = Border(
                    left=Side(style="medium", color="7C3AED"),
                    right=Side(style="medium", color="7C3AED"),
                    top=thin_grey,
                    bottom=thin_grey,
                )

        # Friendly numeric formats.
        for header, number_format in {
            "Average Score": "0.00",
            "Attendance Rate (%)": "0.0",
            "Study Hours Per Day": "0.0",
            "Previous CGPA": "0.00",
        }.items():
            column_index = header_lookup.get(header)
            if column_index:
                for row_index in range(2, worksheet.max_row + 1):
                    worksheet.cell(
                        row=row_index,
                        column=column_index,
                    ).number_format = number_format

        # Sensible widths.
        width_map = {
            "Student ID": 14,
            "Student Name": 22,
            "Number of Subjects": 18,
            "Average Score": 15,
            "Attendance Rate (%)": 19,
            "Study Hours Per Day": 21,
            "Previous CGPA": 15,
            "KNN Prediction": 17,
            "SVM Prediction": 17,
            "ANN Prediction": 17,
            "FINAL PREDICTION": 21,
        }

        for column_index in range(1, worksheet.max_column + 1):
            header = worksheet.cell(row=1, column=column_index).value
            worksheet.column_dimensions[
                get_column_letter(column_index)
            ].width = width_map.get(header, 16)

        # Add a compact summary sheet only for completed prediction output.
        if "FINAL PREDICTION" in export_df.columns:
            summary_sheet = workbook.create_sheet("Summary")
            summary_sheet.sheet_view.showGridLines = False

            summary_sheet.merge_cells("A1:D1")
            summary_sheet["A1"] = "Batch Prediction Summary"
            summary_sheet["A1"].fill = navy_fill
            summary_sheet["A1"].font = Font(
                color="FFFFFF",
                bold=True,
                size=16,
            )
            summary_sheet["A1"].alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            summary_sheet.row_dimensions[1].height = 32

            summary_sheet["A3"] = "Performance Category"
            summary_sheet["B3"] = "Number of Students"
            summary_sheet["C3"] = "Percentage"
            summary_sheet["D3"] = "Recommended Action"

            for cell in summary_sheet[3]:
                cell.fill = final_header_fill
                cell.font = white_font
                cell.alignment = Alignment(horizontal="center")
                cell.border = cell_border

            category_order = [
                "Excellent",
                "Good",
                "Average",
                "At Risk",
            ]
            counts = (
                export_df["FINAL PREDICTION"]
                .value_counts()
                .reindex(category_order, fill_value=0)
            )
            total_students = len(export_df)

            recommendations = {
                "Excellent": "Maintain strong performance",
                "Good": "Continue current progress",
                "Average": "Provide academic guidance",
                "At Risk": "Early intervention required",
            }

            for offset, category in enumerate(category_order, start=4):
                count = int(counts[category])
                percentage = (
                    count / total_students
                    if total_students
                    else 0
                )

                summary_sheet.cell(offset, 1, category)
                summary_sheet.cell(offset, 2, count)
                summary_sheet.cell(offset, 3, percentage)
                summary_sheet.cell(
                    offset,
                    4,
                    recommendations[category],
                )

                for column_index in range(1, 5):
                    cell = summary_sheet.cell(
                        offset,
                        column_index,
                    )
                    cell.border = cell_border
                    cell.alignment = Alignment(
                        horizontal=(
                            "left"
                            if column_index == 4
                            else "center"
                        ),
                        vertical="center",
                    )

                summary_sheet.cell(offset, 1).fill = category_fills[category]
                summary_sheet.cell(offset, 1).font = category_fonts[category]
                summary_sheet.cell(offset, 3).number_format = "0.0%"

            summary_sheet["A9"] = "Total Students"
            summary_sheet["B9"] = total_students
            summary_sheet["A9"].font = Font(bold=True)
            summary_sheet["B9"].font = Font(bold=True)

            summary_sheet.column_dimensions["A"].width = 24
            summary_sheet.column_dimensions["B"].width = 20
            summary_sheet.column_dimensions["C"].width = 16
            summary_sheet.column_dimensions["D"].width = 32
            summary_sheet.freeze_panes = "A3"

    output.seek(0)
    return output.getvalue()


def make_batch_excel_bytes(dataframe):
    """
    Create a polished batch Excel export.

    Sheet 1: Prediction Results
        - Student information and model input values
        - Final Prediction only, clearly highlighted

    Sheet 2: Model Comparison
        - KNN, SVM and ANN predictions for detailed checking

    Sheet 3: Executive Dashboard
        - KPI cards, native Excel pie chart and bar chart

    Sheet 4: Summary
        - Category totals, percentages and recommended actions
    """
    export_df = dataframe.copy()

    # Remove technical columns that are not useful to normal users.
    columns_to_remove = [
        column for column in export_df.columns
        if "Confidence" in column or column == "Best_Model"
    ]
    export_df = export_df.drop(columns=columns_to_remove, errors="ignore")

    main_columns = [
        column for column in [
            "Student_ID",
            "Student_Name",
            "Number_of_Subjects",
            "Average_Score",
            "Attendance_Pct",
            "Study_Hours_Per_Day",
            "Previous_CGPA",
            "Final_Prediction",
        ]
        if column in export_df.columns
    ]

    comparison_columns = [
        column for column in [
            "Student_ID",
            "Student_Name",
            "KNN_Prediction",
            "SVM_Prediction",
            "ANN_Prediction",
        ]
        if column in export_df.columns
    ]

    friendly_headers = {
        "Student_ID": "Student ID",
        "Student_Name": "Student Name",
        "Number_of_Subjects": "Number of Subjects",
        "Average_Score": "Average Score",
        "Attendance_Pct": "Attendance Rate (%)",
        "Study_Hours_Per_Day": "Study Hours Per Day",
        "Previous_CGPA": "Previous CGPA",
        "KNN_Prediction": "KNN Prediction",
        "SVM_Prediction": "SVM Prediction",
        "ANN_Prediction": "ANN Prediction",
        "Final_Prediction": "FINAL PREDICTION",
    }

    main_df = export_df[main_columns].rename(columns=friendly_headers)
    comparison_df = export_df[comparison_columns].rename(columns=friendly_headers)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        main_df.to_excel(
            writer,
            index=False,
            sheet_name="Prediction Results",
        )
        comparison_df.to_excel(
            writer,
            index=False,
            sheet_name="Model Comparison",
        )

        workbook = writer.book

        # Shared styles.
        navy_fill = PatternFill("solid", fgColor="1E3A8A")
        purple_fill = PatternFill("solid", fgColor="5B21B6")
        light_purple_fill = PatternFill("solid", fgColor="F5F3FF")
        white_fill = PatternFill("solid", fgColor="FFFFFF")
        alternate_fill = PatternFill("solid", fgColor="F8FAFC")
        white_font = Font(color="FFFFFF", bold=True)
        body_font = Font(color="172033")
        subtitle_font = Font(color="64748B", italic=True)
        thin_grey = Side(style="thin", color="D7DEE8")
        purple_side = Side(style="medium", color="7C3AED")

        category_fills = {
            "Excellent": PatternFill("solid", fgColor="DCFCE7"),
            "Good": PatternFill("solid", fgColor="DBEAFE"),
            "Average": PatternFill("solid", fgColor="FEF3C7"),
            "At Risk": PatternFill("solid", fgColor="FEE2E2"),
        }
        category_fonts = {
            "Excellent": Font(color="166534", bold=True),
            "Good": Font(color="1D4ED8", bold=True),
            "Average": Font(color="92400E", bold=True),
            "At Risk": Font(color="B91C1C", bold=True),
        }

        def apply_common_sheet_style(
            worksheet,
            widths,
            highlighted_header=None,
            prediction_headers=None,
        ):
            worksheet.sheet_view.showGridLines = False
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            worksheet.row_dimensions[1].height = 32

            header_lookup = {
                cell.value: cell.column
                for cell in worksheet[1]
            }

            for cell in worksheet[1]:
                cell.fill = (
                    purple_fill
                    if cell.value == highlighted_header
                    else navy_fill
                )
                cell.font = white_font
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True,
                )
                cell.border = Border(
                    left=thin_grey,
                    right=thin_grey,
                    top=thin_grey,
                    bottom=thin_grey,
                )

            for row_index in range(2, worksheet.max_row + 1):
                row_fill = (
                    alternate_fill
                    if row_index % 2 == 0
                    else white_fill
                )

                for cell in worksheet[row_index]:
                    cell.fill = row_fill
                    cell.font = body_font
                    cell.alignment = Alignment(
                        horizontal="center",
                        vertical="center",
                    )
                    cell.border = Border(
                        left=thin_grey,
                        right=thin_grey,
                        top=thin_grey,
                        bottom=thin_grey,
                    )

                    column_header = worksheet.cell(
                        row=1,
                        column=cell.column,
                    ).value

                    if column_header == "Student Name":
                        cell.alignment = Alignment(
                            horizontal="left",
                            vertical="center",
                        )

                    if (
                        prediction_headers
                        and column_header in prediction_headers
                    ):
                        category = str(cell.value)
                        if category in category_fills:
                            cell.fill = category_fills[category]
                            cell.font = category_fonts[category]

                if highlighted_header in header_lookup:
                    highlighted_cell = worksheet.cell(
                        row=row_index,
                        column=header_lookup[highlighted_header],
                    )
                    highlighted_cell.border = Border(
                        left=purple_side,
                        right=purple_side,
                        top=thin_grey,
                        bottom=thin_grey,
                    )

            number_formats = {
                "Average Score": "0.00",
                "Attendance Rate (%)": "0.0",
                "Study Hours Per Day": "0.0",
                "Previous CGPA": "0.00",
            }

            for header, number_format in number_formats.items():
                column_index = header_lookup.get(header)
                if column_index:
                    for row_index in range(2, worksheet.max_row + 1):
                        worksheet.cell(
                            row=row_index,
                            column=column_index,
                        ).number_format = number_format

            for column_index in range(1, worksheet.max_column + 1):
                header = worksheet.cell(
                    row=1,
                    column=column_index,
                ).value
                worksheet.column_dimensions[
                    get_column_letter(column_index)
                ].width = widths.get(header, 16)

        # Sheet 1: clean final result.
        results_sheet = writer.sheets["Prediction Results"]
        apply_common_sheet_style(
            results_sheet,
            widths={
                "Student ID": 14,
                "Student Name": 22,
                "Number of Subjects": 18,
                "Average Score": 15,
                "Attendance Rate (%)": 19,
                "Study Hours Per Day": 21,
                "Previous CGPA": 15,
                "FINAL PREDICTION": 22,
            },
            highlighted_header="FINAL PREDICTION",
            prediction_headers={"FINAL PREDICTION"},
        )

        # Sheet 2: detailed algorithm comparison.
        comparison_sheet = writer.sheets["Model Comparison"]
        apply_common_sheet_style(
            comparison_sheet,
            widths={
                "Student ID": 14,
                "Student Name": 22,
                "KNN Prediction": 18,
                "SVM Prediction": 18,
                "ANN Prediction": 18,
            },
            prediction_headers={
                "KNN Prediction",
                "SVM Prediction",
                "ANN Prediction",
            },
        )

        # Add a professional title above the comparison table.
        comparison_sheet.insert_rows(1, amount=3)
        comparison_sheet.merge_cells("A1:E1")
        comparison_sheet["A1"] = "Machine Learning Model Comparison"
        comparison_sheet["A1"].fill = navy_fill
        comparison_sheet["A1"].font = Font(
            color="FFFFFF",
            bold=True,
            size=16,
        )
        comparison_sheet["A1"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        comparison_sheet.row_dimensions[1].height = 30

        comparison_sheet.merge_cells("A2:E2")
        comparison_sheet["A2"] = (
            "Detailed KNN, SVM and ANN predictions for academic review"
        )
        comparison_sheet["A2"].fill = light_purple_fill
        comparison_sheet["A2"].font = subtitle_font
        comparison_sheet["A2"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        # Reapply freeze/filter after inserted title rows.
        comparison_sheet.freeze_panes = "A5"
        comparison_sheet.auto_filter.ref = (
            f"A4:E{comparison_sheet.max_row}"
        )

        # Sheet 3: executive dashboard with native Excel charts.
        dashboard_sheet = workbook.create_sheet(
            "Executive Dashboard",
            1,
        )
        dashboard_sheet.sheet_view.showGridLines = False
        dashboard_sheet.sheet_view.zoomScale = 80

        # Colour palette.
        dashboard_blue = "1E3A8A"
        dashboard_purple = "6D28D9"
        dashboard_light_blue = "EFF6FF"
        dashboard_border = "CBD5E1"

        card_styles = {
            "Total Students": {
                "fill": "E8EEFF",
                "font": "1E3A8A",
            },
            "Excellent": {
                "fill": "DCFCE7",
                "font": "166534",
            },
            "Good": {
                "fill": "DBEAFE",
                "font": "1D4ED8",
            },
            "Average": {
                "fill": "FEF3C7",
                "font": "B45309",
            },
            "At Risk": {
                "fill": "FEE2E2",
                "font": "B91C1C",
            },
        }

        # Fixed column widths provide a predictable layout in Excel and WPS.
        dashboard_widths = {
            "A": 13,
            "B": 13,
            "C": 13,
            "D": 13,
            "E": 13,
            "F": 13,
            "G": 13,
            "H": 13,
            "I": 13,
            "J": 13,
            "K": 13,
            "L": 13,
            "M": 13,
            "N": 13,
            "O": 13,
        }
        for column_letter, width in dashboard_widths.items():
            dashboard_sheet.column_dimensions[column_letter].width = width

        # Report title.
        dashboard_sheet.merge_cells("A1:O2")
        dashboard_sheet["A1"] = "Student Performance Prediction Report"
        dashboard_sheet["A1"].fill = PatternFill(
            "solid",
            fgColor=dashboard_blue,
        )
        dashboard_sheet["A1"].font = Font(
            color="FFFFFF",
            bold=True,
            size=20,
        )
        dashboard_sheet["A1"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        dashboard_sheet["A1"].border = Border(
            bottom=Side(style="medium", color=dashboard_purple),
        )

        dashboard_sheet.merge_cells("A3:L3")
        dashboard_sheet["A3"] = (
            "Batch prediction dashboard generated by the Student AI system"
        )
        dashboard_sheet["A3"].fill = PatternFill(
            "solid",
            fgColor="F3F0FF",
        )
        dashboard_sheet["A3"].font = Font(
            color="5B21B6",
            bold=True,
            italic=True,
            size=10,
        )
        dashboard_sheet["A3"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        dashboard_sheet.merge_cells("M3:O3")
        dashboard_sheet["M3"] = (
            "Generated: " + datetime.now().strftime("%d %b %Y")
        )
        dashboard_sheet["M3"].fill = PatternFill(
            "solid",
            fgColor="E8EEFF",
        )
        dashboard_sheet["M3"].font = Font(
            color=dashboard_blue,
            bold=True,
            size=9,
        )
        dashboard_sheet["M3"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        # Prediction counts.
        total_students = len(export_df)
        category_order = [
            "Excellent",
            "Good",
            "Average",
            "At Risk",
        ]
        counts = (
            export_df["Final_Prediction"]
            .value_counts()
            .reindex(category_order, fill_value=0)
        )

        # Five aligned KPI cards.
        # Rendered as one image to guarantee identical display in Excel and WPS.
        kpi_buffer = BytesIO()

        kpi_labels = [
            "TOTAL STUDENTS",
            "EXCELLENT",
            "GOOD",
            "AVERAGE",
            "AT RISK",
        ]
        kpi_values = [
            total_students,
            int(counts["Excellent"]),
            int(counts["Good"]),
            int(counts["Average"]),
            int(counts["At Risk"]),
        ]
        kpi_subtitles = [
            "Students analysed",
            "High performance",
            "Positive progress",
            "Academic guidance",
            "Early intervention",
        ]
        kpi_backgrounds = [
            "#E8EEFF",
            "#DCFCE7",
            "#DBEAFE",
            "#FEF3C7",
            "#FEE2E2",
        ]
        kpi_text_colours = [
            "#1E3A8A",
            "#166534",
            "#1D4ED8",
            "#B45309",
            "#B91C1C",
        ]

        fig, axes = plt.subplots(
            1,
            5,
            figsize=(15.4, 2.05),
        )
        fig.patch.set_facecolor("white")

        for axis, label, value, subtitle, background, text_colour in zip(
            axes,
            kpi_labels,
            kpi_values,
            kpi_subtitles,
            kpi_backgrounds,
            kpi_text_colours,
        ):
            axis.set_facecolor(background)
            axis.set_xticks([])
            axis.set_yticks([])

            for spine in axis.spines.values():
                spine.set_visible(True)
                spine.set_color("#CBD5E1")
                spine.set_linewidth(1.1)

            axis.text(
                0.5,
                0.76,
                label,
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color=text_colour,
                transform=axis.transAxes,
            )
            axis.text(
                0.5,
                0.48,
                f"{value:,}",
                ha="center",
                va="center",
                fontsize=20,
                fontweight="bold",
                color=text_colour,
                transform=axis.transAxes,
            )
            axis.text(
                0.5,
                0.20,
                subtitle,
                ha="center",
                va="center",
                fontsize=8.5,
                fontweight="bold",
                color=text_colour,
                transform=axis.transAxes,
            )

        plt.subplots_adjust(
            left=0.01,
            right=0.99,
            top=0.95,
            bottom=0.05,
            wspace=0.045,
        )
        fig.savefig(
            kpi_buffer,
            format="png",
            dpi=170,
            bbox_inches="tight",
            facecolor="white",
        )
        plt.close(fig)
        kpi_buffer.seek(0)

        kpi_image = XLImage(kpi_buffer)
        kpi_image.width = 1370
        kpi_image.height = 165
        dashboard_sheet.add_image(
            kpi_image,
            "A5",
        )

        # Reserve vertical space for the KPI image.
        for row_number, height in {
            5: 30,
            6: 30,
            7: 30,
            8: 30,
        }.items():
            dashboard_sheet.row_dimensions[row_number].hidden = False
            dashboard_sheet.row_dimensions[row_number].height = height

        # Performance summary table.
        dashboard_sheet.row_dimensions[9].height = 12
        dashboard_sheet.merge_cells("A10:E10")
        dashboard_sheet["A10"] = "Performance Summary"
        dashboard_sheet["A10"].fill = PatternFill(
            "solid",
            fgColor=dashboard_blue,
        )
        dashboard_sheet["A10"].font = Font(
            color="FFFFFF",
            bold=True,
            size=13,
        )
        dashboard_sheet["A10"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        summary_headers = [
            "Performance Category",
            "Students",
            "Percentage",
        ]
        summary_columns = [1, 4, 5]

        dashboard_sheet.merge_cells("A11:C11")
        dashboard_sheet["A11"] = summary_headers[0]
        dashboard_sheet["D11"] = summary_headers[1]
        dashboard_sheet["E11"] = summary_headers[2]

        for cell_reference in ["A11", "D11", "E11"]:
            cell = dashboard_sheet[cell_reference]
            cell.fill = PatternFill(
                "solid",
                fgColor=dashboard_purple,
            )
            cell.font = Font(
                color="FFFFFF",
                bold=True,
                size=10,
            )
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            cell.border = Border(
                left=Side(style="thin", color=dashboard_border),
                right=Side(style="thin", color=dashboard_border),
                top=Side(style="thin", color=dashboard_border),
                bottom=Side(style="thin", color=dashboard_border),
            )

        for row_index, category in enumerate(category_order, start=12):
            count = int(counts[category])
            percentage = (
                count / total_students
                if total_students
                else 0
            )

            dashboard_sheet.merge_cells(
                start_row=row_index,
                start_column=1,
                end_row=row_index,
                end_column=3,
            )
            dashboard_sheet.cell(
                row=row_index,
                column=1,
                value=category,
            )
            dashboard_sheet.cell(
                row=row_index,
                column=4,
                value=count,
            )
            dashboard_sheet.cell(
                row=row_index,
                column=5,
                value=percentage,
            )

            category_fill = PatternFill(
                "solid",
                fgColor=card_styles[category]["fill"],
            )
            category_font = card_styles[category]["font"]

            for column_index in range(1, 6):
                cell = dashboard_sheet.cell(
                    row=row_index,
                    column=column_index,
                )
                cell.fill = category_fill
                cell.border = Border(
                    left=Side(style="thin", color=dashboard_border),
                    right=Side(style="thin", color=dashboard_border),
                    top=Side(style="thin", color=dashboard_border),
                    bottom=Side(style="thin", color=dashboard_border),
                )
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                )
                cell.font = Font(
                    color=category_font,
                    bold=(column_index == 1),
                    size=10,
                )

            dashboard_sheet.cell(
                row=row_index,
                column=5,
            ).number_format = "0.0%"

        # Total row.
        dashboard_sheet.merge_cells("A16:C16")
        dashboard_sheet["A16"] = "TOTAL"
        dashboard_sheet["D16"] = total_students
        dashboard_sheet["E16"] = 1

        for cell_reference in ["A16", "D16", "E16"]:
            cell = dashboard_sheet[cell_reference]
            cell.fill = PatternFill(
                "solid",
                fgColor="E0E7FF",
            )
            cell.font = Font(
                color=dashboard_blue,
                bold=True,
                size=10,
            )
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            cell.border = Border(
                left=Side(style="thin", color=dashboard_border),
                right=Side(style="thin", color=dashboard_border),
                top=Side(style="thin", color=dashboard_border),
                bottom=Side(style="thin", color=dashboard_border),
            )
        dashboard_sheet["E16"].number_format = "0%"

        # Charts use the visible Performance Summary table.
        # This is more compatible with WPS than referencing hidden columns.

        # Pie chart in the centre.
        # A rendered image is embedded instead of a native Excel chart because
        # WPS may add unwanted "Series1" labels to native chart data labels.
        pie_buffer = BytesIO()
        pie_colours = ["#22C55E", "#3B82F6", "#F59E0B", "#EF4444"]

        fig, ax = plt.subplots(
            figsize=(6.2, 4.3),
            facecolor="white",
        )
        fig.patch.set_facecolor("white")
        fig.patch.set_edgecolor("#C9D3E6")
        fig.patch.set_linewidth(2.2)
        wedges, texts, autotexts = ax.pie(
            [int(counts[category]) for category in category_order],
            labels=None,
            autopct="%1.0f%%",
            startangle=90,
            colors=pie_colours,
            pctdistance=0.70,
            wedgeprops={
                "linewidth": 1.2,
                "edgecolor": "white",
            },
        )
        ax.set_title(
            "Prediction Distribution",
            fontsize=14,
            fontweight="bold",
            pad=14,
        )
        ax.legend(
            wedges,
            [
                f"{category} ({int(counts[category])})"
                for category in category_order
            ],
            loc="center left",
            bbox_to_anchor=(1.00, 0.5),
            frameon=False,
            fontsize=9,
        )
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight("bold")
            autotext.set_color("white")
        ax.axis("equal")
        ax.set_facecolor("white")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#D6DDEB")
            spine.set_linewidth(1.1)
        plt.tight_layout(pad=0.8)
        fig.savefig(
            pie_buffer,
            format="png",
            dpi=190,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="#C9D3E6",
        )
        plt.close(fig)
        pie_buffer.seek(0)

        pie_image = XLImage(pie_buffer)
        pie_image.width = 420
        pie_image.height = 260
        dashboard_sheet.add_image(
            pie_image,
            "G10",
        )

        # Recommended-action panel on the right.
        dashboard_sheet.merge_cells("J10:N17")
        at_risk_count = int(counts["At Risk"])

        if at_risk_count > 0:
            recommendation_text = (
                "RECOMMENDED ACTION\n\n"
                f"{at_risk_count:,} student(s) were classified as At Risk.\n\n"
                "Early academic intervention and continuous monitoring "
                "are recommended."
            )
            recommendation_fill = "FEE2E2"
            recommendation_colour = "B91C1C"
        else:
            recommendation_text = (
                "RECOMMENDED ACTION\n\n"
                "No students were classified as At Risk.\n\n"
                "Continue monitoring academic progress."
            )
            recommendation_fill = "DCFCE7"
            recommendation_colour = "166534"

        dashboard_sheet["J10"] = recommendation_text
        dashboard_sheet["J10"].fill = PatternFill(
            "solid",
            fgColor=recommendation_fill,
        )
        dashboard_sheet["J10"].font = Font(
            color=recommendation_colour,
            bold=True,
            size=12,
        )
        dashboard_sheet["J10"].alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
        dashboard_sheet["J10"].border = Border(
            left=Side(style="medium", color=recommendation_colour),
            right=Side(style="medium", color=recommendation_colour),
            top=Side(style="medium", color=recommendation_colour),
            bottom=Side(style="medium", color=recommendation_colour),
        )

        # Full-width bar chart below all summary content.
        # The image-based chart is consistent across Microsoft Excel and WPS.
        bar_buffer = BytesIO()
        bar_values = [int(counts[category]) for category in category_order]
        bar_colours = ["#22C55E", "#3B82F6", "#F59E0B", "#EF4444"]

        fig, ax = plt.subplots(
            figsize=(11.8, 4.4),
            facecolor="white",
        )
        fig.patch.set_facecolor("white")
        fig.patch.set_edgecolor("#C9D3E6")
        fig.patch.set_linewidth(2.2)
        bars = ax.bar(
            category_order,
            bar_values,
            color=bar_colours,
            width=0.56,
        )
        ax.set_title(
            "Students by Performance Category",
            fontsize=14,
            fontweight="bold",
            pad=14,
        )
        ax.set_ylabel("Number of Students", fontsize=10)
        ax.set_xlabel("Performance Category", fontsize=10)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#D6DDEB")
            spine.set_linewidth(1.1)
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(False)

        maximum_value = max(bar_values) if bar_values else 1
        ax.set_ylim(0, maximum_value * 1.22)

        for bar, value in zip(bars, bar_values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + maximum_value * 0.035,
                str(value),
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        plt.tight_layout(pad=0.8)
        fig.savefig(
            bar_buffer,
            format="png",
            dpi=190,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="#C9D3E6",
        )
        plt.close(fig)
        bar_buffer.seek(0)

        bar_image = XLImage(bar_buffer)
        bar_image.width = 1360
        bar_image.height = 340
        dashboard_sheet.add_image(
            bar_image,
            "A19",
        )

        # Stable row heights.
        row_heights = {
            1: 30,
            2: 18,
            3: 24,
            5: 26,
            6: 26,
            7: 26,
            8: 26,
            9: 10,
            10: 26,
            11: 24,
            12: 24,
            13: 24,
            14: 24,
            15: 24,
            16: 24,
            17: 24,
            18: 10,
            19: 10,
        }
        for row_number, height in row_heights.items():
            dashboard_sheet.row_dimensions[row_number].height = height

        for row_number in range(19, 37):
            dashboard_sheet.row_dimensions[row_number].height = 23

        dashboard_sheet.freeze_panes = "A5"
        dashboard_sheet.page_setup.orientation = "landscape"
        dashboard_sheet.page_setup.fitToWidth = 1
        dashboard_sheet.page_setup.fitToHeight = 1
        dashboard_sheet.sheet_properties.pageSetUpPr.fitToPage = True
        dashboard_sheet.print_area = "A1:O36"
        dashboard_sheet.sheet_view.zoomScale = 85

        # Sheet 4: executive summary.
        summary_sheet = workbook.create_sheet("Summary")
        summary_sheet.sheet_view.showGridLines = False

        summary_sheet.merge_cells("A1:D1")
        summary_sheet["A1"] = "Batch Prediction Summary"
        summary_sheet["A1"].fill = navy_fill
        summary_sheet["A1"].font = Font(
            color="FFFFFF",
            bold=True,
            size=17,
        )
        summary_sheet["A1"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        summary_sheet.row_dimensions[1].height = 34

        summary_sheet.merge_cells("A2:D2")
        summary_sheet["A2"] = (
            f"Total student records processed: {len(export_df):,}"
        )
        summary_sheet["A2"].fill = light_purple_fill
        summary_sheet["A2"].font = Font(
            color="4C1D95",
            bold=True,
        )
        summary_sheet["A2"].alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        summary_headers = [
            "Performance Category",
            "Number of Students",
            "Percentage",
            "Recommended Action",
        ]
        for column_index, value in enumerate(
            summary_headers,
            start=1,
        ):
            cell = summary_sheet.cell(
                row=4,
                column=column_index,
                value=value,
            )
            cell.fill = purple_fill
            cell.font = white_font
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            cell.border = Border(
                left=thin_grey,
                right=thin_grey,
                top=thin_grey,
                bottom=thin_grey,
            )

        category_order = [
            "Excellent",
            "Good",
            "Average",
            "At Risk",
        ]
        counts = (
            export_df["Final_Prediction"]
            .value_counts()
            .reindex(category_order, fill_value=0)
        )
        recommendations = {
            "Excellent": "Maintain strong performance",
            "Good": "Continue current progress",
            "Average": "Provide academic guidance",
            "At Risk": "Early intervention required",
        }

        total_students = len(export_df)

        for row_index, category in enumerate(
            category_order,
            start=5,
        ):
            count = int(counts[category])
            percentage = (
                count / total_students
                if total_students
                else 0
            )

            values = [
                category,
                count,
                percentage,
                recommendations[category],
            ]

            for column_index, value in enumerate(
                values,
                start=1,
            ):
                cell = summary_sheet.cell(
                    row=row_index,
                    column=column_index,
                    value=value,
                )
                cell.border = Border(
                    left=thin_grey,
                    right=thin_grey,
                    top=thin_grey,
                    bottom=thin_grey,
                )
                cell.alignment = Alignment(
                    horizontal=(
                        "left"
                        if column_index == 4
                        else "center"
                    ),
                    vertical="center",
                )

            summary_sheet.cell(
                row=row_index,
                column=1,
            ).fill = category_fills[category]
            summary_sheet.cell(
                row=row_index,
                column=1,
            ).font = category_fonts[category]
            summary_sheet.cell(
                row=row_index,
                column=3,
            ).number_format = "0.0%"

        summary_sheet["A10"] = "Priority Focus"
        summary_sheet["A10"].fill = navy_fill
        summary_sheet["A10"].font = white_font
        summary_sheet["B10"] = (
            f"{int(counts['At Risk']):,} At-Risk student(s)"
        )
        summary_sheet["B10"].fill = category_fills["At Risk"]
        summary_sheet["B10"].font = category_fonts["At Risk"]

        summary_sheet.column_dimensions["A"].width = 24
        summary_sheet.column_dimensions["B"].width = 21
        summary_sheet.column_dimensions["C"].width = 16
        summary_sheet.column_dimensions["D"].width = 34
        summary_sheet.freeze_panes = "A4"

        # Open the executive dashboard first.
        workbook.active = workbook.sheetnames.index(
            "Executive Dashboard"
        )

    output.seek(0)
    return output.getvalue()


def make_template_bytes():
    template_file = (
        ROOT
        / "template"
        / "student_batch_prediction_template.xlsx"
    )

    if not template_file.exists():
        raise FileNotFoundError(
            "Batch prediction template was not found in the template folder."
        )

    return template_file.read_bytes()


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
        "🎯 Prediction",
        "📊 Model Results",
        "📈 Dataset",
        "ℹ️ About"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown(
    """
<div class="sidebar-footer">
    <div class="footer-brand">🎓 Student AI</div>
    <div class="footer-subtitle">Student Performance Prediction</div>
    <div class="footer-powered">Powered by KNN • SVM • ANN</div>
    <div class="footer-version">Version 1.0</div>
    <div class="footer-group">Developed by RIS Group 5</div>
    <div class="footer-copyright">© 2026 All Rights Reserved</div>
</div>
""",
    unsafe_allow_html=True,
)

page = page.split(" ", 1)[1]

if page != "Prediction":
    st.session_state.pop("prediction_mode", None)

if page != "Prediction":
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
    fig.update_layout(
        title=dict(
            x=0.5,
            xanchor="center",
            y=0.96,
            yanchor="top",
        ),
        margin=dict(l=20, r=20, t=75, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


elif page == "Prediction" and not st.session_state.get("prediction_mode"):
    best_row = evaluation.iloc[0]

    st.markdown('<div class="prediction-hub-shell">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="prediction-welcome">
    <div class="prediction-eyebrow">AI-Powered Academic Decision Support</div>
    <h2>Student Performance Prediction System</h2>
    <p>
        Predict student academic performance using KNN, SVM and ANN.
        Choose individual analysis or batch processing to identify at-risk
        students and support faster academic decisions.
    </p>
    <p><b>Select a prediction mode below to begin.</b></p>
</div>
""",
        unsafe_allow_html=True,
    )

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4, gap="small")
    stat_col1.metric("🏆 Best Model", str(best_row["Model"]))
    stat_col2.metric("🎯 Best Accuracy", f"{best_row['Accuracy']:.1%}")
    stat_col3.metric("📚 Input Features", "5")
    stat_col4.metric("🤖 ML Models", "3")

    card_col1, card_col2 = st.columns(2, gap="small")

    with card_col1:
        st.markdown(
            """
<div class="prediction-mode-card">
    <div class="prediction-mode-icon">👤</div>
    <div class="prediction-mode-title">Individual Prediction</div>
    <div class="prediction-mode-desc">
        Predict the academic performance of one student using manually entered
        information and review the outputs generated by all three models.
    </div>
    <div class="prediction-feature-row">
        <div class="prediction-feature-chip">✓ Real-time</div>
        <div class="prediction-feature-chip">✓ 3-model comparison</div>
        <div class="prediction-feature-chip">✓ Excel report</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button(
            "🚀 Start Individual Prediction",
            key="start_individual_prediction",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["prediction_mode"] = "individual"
            st.rerun()

    with card_col2:
        st.markdown(
            """
<div class="prediction-mode-card">
    <div class="prediction-mode-icon">📂</div>
    <div class="prediction-mode-title">Batch Prediction</div>
    <div class="prediction-mode-desc">
        Upload an Excel or CSV file to predict multiple students simultaneously,
        identify at-risk students and export a professional analytical workbook.
    </div>
    <div class="prediction-feature-row">
        <div class="prediction-feature-chip">✓ Excel / CSV</div>
        <div class="prediction-feature-chip">✓ Dashboard</div>
        <div class="prediction-feature-chip">✓ At-risk detection</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button(
            "📂 Start Batch Prediction",
            key="start_batch_prediction",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["prediction_mode"] = "batch"
            st.rerun()

    st.markdown(
        """
<div class="why-system">
    <div class="why-system-title">Why Use This System?</div>
    <div class="why-grid">
        <div class="why-item">AI-Powered Prediction</div>
        <div class="why-item">Real-Time Analysis</div>
        <div class="why-item">Batch Processing</div>
        <div class="why-item">Professional Excel Reports</div>
        <div class="why-item">Early At-Risk Identification</div>
    </div>
</div>

<div class="system-footer">
    Student Performance Prediction System • Version 1.0<br>
    Developed using Python, Streamlit and Scikit-learn • BMCS2003 Artificial Intelligence
</div>
</div>
""",
        unsafe_allow_html=True,
    )


elif page == "Prediction" and st.session_state.get("prediction_mode") == "individual":
    st.markdown(
        """
<div class="mode-page-hero">
    <div class="mode-page-eyebrow">Single-Student Analysis</div>
    <h2>👤 Individual Prediction</h2>
    <p>
        Enter one student's academic information to generate real-time
        predictions using KNN, SVM and ANN, then download a formatted Excel result.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button(
        "← Back to Prediction Modes",
        key="back_from_individual",
        type="secondary",
    ):
        st.session_state.pop("prediction_mode", None)
        st.session_state.pop("prediction_result", None)
        st.rerun()

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
                "⬇️ Download Result Excel",
                data=saved["report_excel"],
                file_name="individual_prediction_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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

            prediction_lookup = {
                row["Model"]: row["Prediction"]
                for _, row in result_df.iterrows()
            }

            report = pd.DataFrame([{
                "Student_ID": student_id,
                "Student_Name": name,
                "Number_of_Subjects": number_of_subjects,
                "Average_Score": average_score,
                "Attendance_Pct": attendance,
                "Study_Hours_Per_Day": study_hours,
                "Previous_CGPA": previous_cgpa,
                "KNN_Prediction": prediction_lookup.get("KNN", ""),
                "SVM_Prediction": prediction_lookup.get("SVM", ""),
                "ANN_Prediction": prediction_lookup.get("ANN", ""),
                "Final_Prediction": best_row["Prediction"],
                "Best_Model": best_name,
                "Final_Confidence": best_row["Confidence"],
            }])

            st.session_state["prediction_result"] = {
                "prediction": best_row["Prediction"],
                "confidence": float(best_row["Confidence"]),
                "best_model": best_name,
                "result_df": result_df,
                "report_excel": make_excel_bytes(report),
            }

            st.rerun()

elif page == "Prediction" and st.session_state.get("prediction_mode") == "batch":
    st.markdown(
        """
<div class="mode-page-hero">
    <div class="mode-page-eyebrow">Multi-Student Analysis</div>
    <h2>📂 Batch Prediction</h2>
    <p>
        Upload an Excel or CSV file to predict multiple students simultaneously,
        identify at-risk students and export a professional Excel dashboard.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button(
        "← Back to Prediction Modes",
        key="back_from_batch",
        type="secondary",
    ):
        st.session_state.pop("prediction_mode", None)
        st.session_state.pop("batch_prediction_result", None)
        st.rerun()

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
        st.markdown(
            """
<div class="batch-help-box">
    <b>Required columns:</b> Number_of_Subjects, Average_Score,
    Attendance_Pct, Study_Hours_Per_Day and Previous_CGPA.<br>
    <span style="color:#64748b;">Student_ID and Student_Name are optional.</span>
</div>
""",
            unsafe_allow_html=True,
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
        fig.update_layout(
            title=dict(
                x=0.5,
                xanchor="center",
                y=0.96,
                yanchor="top",
            ),
            height=390,
            margin=dict(l=20, r=20, t=75, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        display_df = result_df.copy()
        for column in ["KNN_Confidence", "SVM_Confidence", "ANN_Confidence", "Final_Confidence"]:
            display_df[column] = display_df[column].map(lambda value: f"{value:.1%}")

        st.markdown("#### Batch Prediction Insights")

        insight_col1, insight_col2 = st.columns(2)

        with insight_col1:
            bar_fig = px.bar(
                summary_df,
                x="Performance Category",
                y="Students",
                text="Students",
                title="Students by Predicted Category",
                category_orders={"Performance Category": order},
            )
            bar_fig.update_traces(textposition="outside")
            bar_fig.update_layout(
                title=dict(
                    x=0.5,
                    xanchor="center",
                    y=0.96,
                    yanchor="top",
                ),
                height=390,
                margin=dict(l=20, r=20, t=75, b=20),
            )
            st.plotly_chart(bar_fig, use_container_width=True)

        with insight_col2:
            pie_fig = px.pie(
                summary_df,
                names="Performance Category",
                values="Students",
                title="Prediction Distribution",
                hole=0.42,
            )
            pie_fig.update_layout(
                title=dict(
                    x=0.5,
                    xanchor="center",
                    y=0.96,
                    yanchor="top",
                ),
                height=390,
                margin=dict(l=20, r=20, t=75, b=20),
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        at_risk_df = result_df[
            result_df["Final_Prediction"] == "At Risk"
        ].copy()

        st.markdown("#### ⚠️ At-Risk Student Dashboard")

        risk_col1, risk_col2, risk_col3 = st.columns(3)
        risk_col1.metric("Students Requiring Intervention", len(at_risk_df))
        risk_col2.metric(
            "At-Risk Percentage",
            f"{(len(at_risk_df) / len(result_df)):.1%}" if len(result_df) else "0.0%",
        )
        risk_col3.metric("Recommended Action", "Early Support")

        if at_risk_df.empty:
            st.success("No students were classified as At Risk in this batch.")
        else:
            st.warning(
                f"{len(at_risk_df):,} student(s) were classified as At Risk. "
                "Early academic intervention is recommended."
            )

            risk_columns = [
                column for column in [
                    "Student_ID",
                    "Student_Name",
                    "Average_Score",
                    "Attendance_Pct",
                    "Study_Hours_Per_Day",
                    "Previous_CGPA",
                    "Final_Prediction",
                    "Final_Confidence",
                ]
                if column in at_risk_df.columns
            ]

            at_risk_display = at_risk_df[risk_columns].copy()

            if "Final_Confidence" in at_risk_display.columns:
                at_risk_display["Final_Confidence"] = (
                    at_risk_display["Final_Confidence"]
                    .map(lambda value: f"{value:.1%}")
                )

            st.dataframe(
                at_risk_display,
                hide_index=True,
                use_container_width=True,
            )

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
                ["All Categories"] + order,
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
                    search_mask = search_mask | filtered_df[
                        column
                    ].astype(str).str.contains(
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

        st.dataframe(
            filtered_df,
            hide_index=True,
            use_container_width=True,
        )

        low_confidence_count = int(
            (result_df["Final_Confidence"] < 0.60).sum()
        )

        if low_confidence_count > 0:
            st.info(
                f"{low_confidence_count:,} prediction(s) have confidence below 60%. "
                "These records may require lecturer review."
            )

        download_col, clear_col = st.columns(2)

        with download_col:
            st.download_button(
                "⬇️ Download Predicted Excel",
                data=make_batch_excel_bytes(result_df),
                file_name="student_batch_predictions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with clear_col:
            if st.button(
                "↻ Upload Another File",
                type="secondary",
                use_container_width=True,
            ):
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
        title=dict(
            x=0.5,
            xanchor="center",
            y=0.96,
            yanchor="top",
        ),
        height=420,
        margin=dict(l=20, r=20, t=75, b=20)
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
                title=dict(
                    x=0.5,
                    xanchor="center",
                    y=0.96,
                    yanchor="top",
                ),
                height=390,
                margin=dict(l=20, r=20, t=75, b=20)
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
        fig.update_layout(
            title=dict(
                x=0.5,
                xanchor="center",
                y=0.96,
                yanchor="top",
            ),
            margin=dict(l=20, r=20, t=75, b=20),
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
        fig.update_layout(
            title=dict(
                x=0.5,
                xanchor="center",
                y=0.96,
                yanchor="top",
            ),
            margin=dict(l=20, r=20, t=75, b=20),
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
