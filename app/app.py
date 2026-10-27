
import io
import joblib
import pandas as pd

from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from app.schemas import HouseFeatures

app = FastAPI(title="House Price Prediction API")

# Resolve model path relative to the project root
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model.pkl"

# Load model once when the application starts
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None


REQUIRED_COLUMNS = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]


@app.get("/")
def home():
    return {
        "message": "Welcome to House Price Prediction API!",
        "status": "running",
        "model_loaded": model is not None,
    }


@app.get("/health")
def health():
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifact is unavailable.",
        )

    return {"status": "healthy", "model_loaded": True}


@app.post("/predict")
def predict_price(house: HouseFeatures):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifact not found. Prediction is unavailable.",
        )

    try:
        input_data = {
            "MedInc": house.MedInc,
            "HouseAge": house.HouseAge,
            "AveRooms": house.AveRooms,
            "AveBedrms": house.AveBedrms,
            "Population": house.Population,
            "AveOccup": house.AveOccup,
            "Latitude": house.Latitude,
            "Longitude": house.Longitude,
        }

        df = pd.DataFrame([input_data], columns=REQUIRED_COLUMNS)
        prediction = float(model.predict(df)[0])
        price_usd = prediction * 100000

        return {
            "predicted_price": f"${price_usd:,.0f}",
            "prediction_price_short": f"${price_usd:.2f}",
            "confidence_range": (
                f"${price_usd - 30000:.2f} "
                f"to ${price_usd + 30000:.2f}"
            ),
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check the input and application logs.",
        )


@app.post("/predict/csv")
def predict_bulk_price(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifact not found. Prediction is unavailable.",
        )

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    try:
        contents = file.file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded CSV file is empty.",
            )

        df = pd.read_csv(io.BytesIO(contents))

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_columns}",
            )

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="CSV contains no data rows.",
            )

        df_features = df[REQUIRED_COLUMNS]

        if not all(
            pd.api.types.is_numeric_dtype(df_features[column])
            for column in REQUIRED_COLUMNS
        ):
            raise HTTPException(
                status_code=400,
                detail="All required feature columns must be numeric.",
            )

        if df_features.isnull().any().any():
            raise HTTPException(
                status_code=400,
                detail="Feature columns cannot contain missing values.",
            )

        predictions = model.predict(df_features)
        df["predicted_price"] = predictions * 100000

        return {
            "total_predictions": len(df),
            "results": df.to_dict(orient="records"),
        }

    except HTTPException:
        raise

    except (pd.errors.ParserError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Unable to parse the uploaded CSV file.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Bulk prediction failed. Check the application logs.",
        )

    finally:
        file.file.close()
