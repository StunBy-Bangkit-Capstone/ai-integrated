from flask import Blueprint, request, jsonify
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import os

# Load model dan scaler
MODEL_DIR = "models/baby_nutrition"
df_food = pd.read_csv('dataset_baby/data_baby_food.csv')

# Load saved models
model = load_model(os.path.join(MODEL_DIR, "baby_nutrition_model.h5"))
scaler_X = joblib.load(os.path.join(MODEL_DIR, "scaler_X.save"))
scaler_y = joblib.load(os.path.join(MODEL_DIR, "scaler_y.save"))


def encode_input(usia_bulan, gender, berat_kg, tinggi_cm, aktivitas_level, status_asi):
    """
    Mengubah input kategorikal menjadi nilai numerik.

    Parameters:
        usia_bulan (int): Usia bayi dalam bulan
        gender (str): Jenis kelamin ('L' atau 'P')
        berat_kg (float): Berat badan dalam kg
        tinggi_cm (float): Tinggi badan dalam cm
        aktivitas_level (str): Level aktivitas ('Rendah', 'Sedang', 'Aktif', 'Sangat_Aktif')
        status_asi (str): Status ASI ('ASI_Eksklusif', 'ASI+MPASI', 'MPASI')

    Returns:
        dict: Data yang sudah diencode

    Raises:
        ValueError: Jika input tidak valid
    """
    # Mapping kategori ke nilai encoding
    gender_mapping = {"L": 0, "P": 1}
    aktivitas_mapping = {"Rendah": 1, "Sedang": 3, "Aktif": 0, "Sangat_Aktif": 2}
    status_asi_mapping = {"ASI_Eksklusif": 1, "ASI+MPASI": 0, "MPASI": 2}

    # Encode data input
    try:
        encoded_data = {
            "Usia_Bulan": usia_bulan,
            "Gender": gender_mapping[gender],
            "Berat_Kg": berat_kg,
            "Tinggi_Cm": tinggi_cm,
            "Aktivitas_Level": aktivitas_mapping[aktivitas_level],
            "Status_ASI": status_asi_mapping[status_asi],
        }
        return encoded_data
    except KeyError as e:
        raise ValueError(f"Invalid input for encoding: {e}")


def predict_nutrition(params):
    """
    Memprediksi kebutuhan nutrisi berdasarkan parameter input.

    Parameters:
        params (dict): Dictionary berisi parameter prediksi
            {
                "age": int,
                "weight": float,
                "gender": str,
                "height": float,
                "activity": str,
                "asi_status": str
            }

    Returns:
        dict: Hasil prediksi kebutuhan nutrisi
            {
                "calories": float,
                "proteins": float,
                "fat": float,
                "carbohydrate": float
            }

    Raises:
        ValueError: Jika parameter tidak valid
    """
    try:
        # Encode input
        encoded_input = encode_input(
            usia_bulan=params["age"],
            gender=params["gender"],
            berat_kg=params["weight"],
            tinggi_cm=params["height"],
            aktivitas_level=params["activity"],
            status_asi=params["asi_status"],
        )

        # Konversi ke DataFrame
        input_df = pd.DataFrame([encoded_input])

        # Normalisasi input
        input_scaled = scaler_X.transform(input_df)

        # Prediksi
        pred_scaled = model.predict(input_scaled)

        # Balikkan normalisasi pada prediksi
        prediction = scaler_y.inverse_transform(pred_scaled)

        return {
            "calories_needed": float(max(0, prediction[0][0])),
            "proteins_needed": float(max(0, prediction[0][1])),
            "fat_needed": float(max(0, prediction[0][2])),
            "carbohydrate_needed": float(max(0, prediction[0][3])),
        }
    except Exception as e:
        raise ValueError(f"Prediction error: {str(e)}")

def evaluate_nutrition(predicted, consumed):
    """
    Helper function untuk mengevaluasi nutrisi.
    
    Parameters:
        predicted (dict): Predicted nutritional needs
        consumed (dict): Consumed nutrients
    
    Returns:
        dict: Evaluation results
    """
    evaluation = {}
    for nutrient in ['calories', 'proteins', 'fat', 'carbohydrate']:
        if nutrient not in predicted:
            continue
            
        consumed_amount = consumed[nutrient]
        predicted_amount = predicted[nutrient]
        percentage = (consumed_amount / predicted_amount * 100) if predicted_amount > 0 else 0
        
        evaluation[nutrient] = {
            'consumed': round(consumed_amount, 2),
            'predicted_needed': round(predicted_amount, 2),
            'percentage': round(percentage, 1),
            'status': 'adequate' if 90 <= percentage <= 110 else 'low' if percentage < 90 else 'high'
        }
    
    return evaluation