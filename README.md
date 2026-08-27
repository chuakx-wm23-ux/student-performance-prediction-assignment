# Student Performance Prediction

This project uses supervised machine learning classification with KNN, SVM and ANN.

## Features
- Number of Subjects
- Average Score
- Attendance Rate
- Study Hours Per Day
- Previous CGPA

## Target
- Excellent
- Good
- Average
- At Risk

## Dataset Source
University Student Performance & Habits Dataset

Author:
Robiul Hasan Jisan

Source:
https://www.kaggle.com/datasets/robiulhasanjisan/university-student-performance-and-habits-dataset

The original dataset was further processed using feature engineering by adding:
• Number_of_Subjects
• Average_Score
The target variable (Final_CGPA) was converted into four performance classes:
• Excellent
• Good
• Average
• At Risk

## Feature Engineering Note
The original Kaggle dataset does not contain individual subject marks.
`Number_of_Subjects` and `Average_Score` in the included CSV are reproducible
engineered estimates created for this project. They must not be described as
original Kaggle columns.

## Run locally
```bash
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

## Upload to GitHub
Upload:
- app.py
- train_model.py
- requirements.txt
- README.md
- submission.txt
- dataset folder
- models folder
- results folder

Run `python train_model.py` once before uploading if model/result files are missing.


Final feature selection:
- Average_Score
- Attendance_Pct
- Study_Hours_Per_Day
- Previous_CGPA

Number_of_Subjects is retained as a displayed student profile item but excluded from ML model input after feature evaluation.


## Final Feature & Excel Export Design

Number_of_Subjects is retained in the Prediction page and Excel export as student profile information.
It is excluded from the machine learning input features after feature evaluation.

Final ML input features:
- Average_Score
- Attendance_Pct
- Study_Hours_Per_Day
- Previous_CGPA

Excel reports may still display Number_of_Subjects together with prediction results.


# Final Prototype Design

## Final ML Input Features
The final prediction model uses:
1. Average_Score
2. Attendance_Pct
3. Study_Hours_Per_Day
4. Previous_CGPA

## Additional Student Information
Number_of_Subjects is retained in the user interface and exported reports as academic workload information, but excluded from ML input after feature evaluation.

## System Workflow
Dataset → Data Preprocessing → Feature Selection → KNN/SVM/ANN Models → Performance Prediction → Report Export

## Prototype Features
- Single student prediction
- Batch prediction support
- Input validation
- Model comparison
- Correlation analysis
- Dataset exploration
- Excel report generation


## Final Complete Prototype Features

### Prediction Module
- Single student prediction
- Batch prediction upload
- Input validation
- Performance category prediction

### Machine Learning Module
Models:
- KNN
- SVM
- ANN

Final selected features:
- Average Score
- Attendance Percentage
- Study Hours Per Day
- Previous CGPA

### Feature Selection
Number of Subjects remains available as student profile information but excluded from the final ML input after evaluation.

### Reporting
- Prediction result export
- Batch result export
- Model performance comparison

### System Flow
Dataset → Preprocessing → Feature Selection → ML Training → Prediction → Report Generation


Feature Analysis page added for explaining final feature selection.


## Professional Prototype Enhancements

Prediction Output:
- Predicted performance category
- Best model identification
- Confidence presentation
- Student recommendation

Model Evaluation:
- Accuracy comparison
- Precision, Recall and F1-score comparison
- Confusion matrix analysis

The system is designed as an academic decision support prototype.


# Final Submission Prototype

## Core Features
- Single student prediction
- Batch prediction
- Model comparison (KNN, SVM, ANN)
- Correlation analysis
- Feature analysis
- Dataset exploration
- Excel report generation

## Final Feature Selection
Machine learning input:
- Average_Score
- Attendance_Pct
- Study_Hours_Per_Day
- Previous_CGPA

Number_of_Subjects remains available as student profile information.
