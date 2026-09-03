import numpy as np
from app.model_loader import model_holder

def predict_price(area, bedrooms, bathrooms, age, garage, location):
    holder = model_holder

    loc_encoded = holder.label_encoder.transform([location])[0]

    numeric_features = np.array([[area, bedrooms, bathrooms, age, garage]])
    numeric_scaled = holder.scaler.transform(numeric_features)

    features = np.append(numeric_scaled[0], loc_encoded).reshape(1, -1)

    prediction = holder.model.predict(features)[0]
    return float(prediction)
