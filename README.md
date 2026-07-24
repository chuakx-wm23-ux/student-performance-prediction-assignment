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
