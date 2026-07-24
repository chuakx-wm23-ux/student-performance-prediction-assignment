from pathlib import Path
import json
import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dataset" / "Student_data.csv"
MODELS = ROOT / "models"
RESULTS = ROOT / "results"
MODELS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

def category(x):
    if x >= 3.5:
        return "Excellent"
    if x >= 3.0:
        return "Good"
    if x >= 2.5:
        return "Average"
    return "At Risk"

def main():
    df = pd.read_csv(DATA)
    df["Performance_Category"] = df["Final_CGPA"].apply(category)

    features = [
        "Number_of_Subjects",
        "Average_Score",
        "Attendance_Pct",
        "Study_Hours_Per_Day",
        "Previous_CGPA",
    ]

    X = df[features]
    encoder = LabelEncoder()
    y = encoder.fit_transform(df["Performance_Category"])

    algorithms = {
        "KNN": KNeighborsClassifier(n_neighbors=9, weights="distance"),
        "SVM": SVC(C=2.0, probability=True, random_state=42),
        "ANN": MLPClassifier(
            hidden_layer_sizes=(32, 16),
            max_iter=500,
            early_stopping=False,
            random_state=42
        ),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rows = []

    for name, algorithm in algorithms.items():
        print(f"Training {name}...")

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", algorithm),
        ])

        model.fit(X_train, y_train)
        prediction = model.predict(X_test)

        rows.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, prediction),
            "Precision": precision_score(y_test, prediction, average="weighted", zero_division=0),
            "Recall": recall_score(y_test, prediction, average="weighted", zero_division=0),
            "F1 Score": f1_score(y_test, prediction, average="weighted", zero_division=0),
        })

        joblib.dump(
            {"model": model, "label_encoder": encoder},
            MODELS / f"{name.lower()}_model.joblib"
        )

        cm = confusion_matrix(y_test, prediction)
        fig, ax = plt.subplots(figsize=(6, 5))
        image = ax.imshow(cm)
        ax.set_title(f"{name} Confusion Matrix")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_xticks(range(len(encoder.classes_)), encoder.classes_, rotation=25, ha="right")
        ax.set_yticks(range(len(encoder.classes_)), encoder.classes_)

        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center")

        fig.colorbar(image, ax=ax)
        fig.tight_layout()
        fig.savefig(RESULTS / f"{name.lower()}_confusion_matrix.png", dpi=160)
        plt.close(fig)

    evaluation = pd.DataFrame(rows).sort_values("Accuracy", ascending=False)
    evaluation.to_csv(RESULTS / "evaluation.csv", index=False)

    metadata = {
        "features": features,
        "best_model": evaluation.iloc[0]["Model"],
        "best_accuracy": float(evaluation.iloc[0]["Accuracy"]),
    }
    (MODELS / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(evaluation)

if __name__ == "__main__":
    main()
