import joblib
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

data = fetch_california_housing(as_frame=True)

X = data.data
y = data.target

print("Features shape:", X.shape)
print("Target shape:", y.shape)
print("Feature columns:", list(X.columns))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

model = Pipeline([
    (
        "regressor",
        RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
    )
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.4f} (units of $100,000)")
print(f"R2 Score: {r2:.4f}")
print(f"MAE in USD: ${mae * 100000:,.2f}")

joblib.dump(model, "model.pkl")
joblib.dump(list(X.columns), "house_features.pkl")

print("Model and feature metadata saved successfully!")