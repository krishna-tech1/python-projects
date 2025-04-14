import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Predefined categories
CATEGORIES = ["Food", "Transport", "Bills", "Entertainment", "Groceries", "Travel", "Health", "Others"]

def train_model():
    """Train the expense categorization model and save it."""
    training_data = pd.DataFrame({
        "description": [
            "Bought pizza for dinner", "Uber ride to office", "Paid electricity bill", "Netflix subscription",
            "Grocery shopping at Walmart", "Dinner at restaurant", "Flight ticket to NYC", "Gym membership renewal"
        ],
        "category": ["Food", "Transport", "Bills", "Entertainment", "Groceries", "Food", "Travel", "Health"]
    })

    vectorizer = TfidfVectorizer()
    classifier = LogisticRegression()
    
    model_pipeline = Pipeline([
        ("vectorizer", vectorizer),
        ("classifier", classifier)
    ])

    model_pipeline.fit(training_data["description"], training_data["category"])
    
    joblib.dump(model_pipeline, "expense_classifier.pkl")

def predict_category(description):
    """Predict expense category from description."""
    model = joblib.load("expense_classifier.pkl")
    return model.predict([description])[0]

if __name__ == "__main__":
    train_model()
