from flask import Blueprint, request, jsonify
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import os
from datetime import datetime

# Load model dan scaler
MODEL_DIR = "models/baby_nutrition"
df_food = pd.read_csv("dataset_baby/data_baby_food.csv")

model = load_model(os.path.join(MODEL_DIR, "baby_nutrition_model.h5"))
scaler_X = joblib.load(os.path.join(MODEL_DIR, "scaler_X.save"))
scaler_y = joblib.load(os.path.join(MODEL_DIR, "scaler_y.save"))


# def __init__(self, db_connection):
#     self.db = db_connection
# def __init__(self):
#     self.daily_tracking = {}


class NutritionTracker:
    def add_food_tracking(self, data, df_food):
        food_name = data["food_name"]
        portion = float(data["portion"])

        if portion <= 0:
            raise ValueError("Portion must be greater than 0")

        food_data = df_food[
            df_food["Food (per 100g)"].str.strip().str.lower()
            == food_name.strip().lower()
        ]
        if food_data.empty:
            raise ValueError(f"Food '{food_name}' not found in database")

        food_row = food_data.iloc[0]
        food_nutrients = self._calculate_nutrients(food_row, portion)

        # Mengembalikan hanya informasi nutrisi makanan yang dicari
        return {
            "name": food_name,
            "portion": portion,
            "nutrients": {
                "calories": round(food_nutrients["calories"], 2),
                "calcium": round(food_nutrients["calcium"], 2),
                "proteins": round(food_nutrients["proteins"], 2),
                "fat": round(food_nutrients["fat"], 2),
                "carbohydrate": round(food_nutrients["carbohydrate"], 2),
            },
            "notes": food_row["Notes"],
        }

    def _calculate_nutrients(self, food_row, portion):
        return {
            "calories": food_row["Calorie(kcal)"] * portion / 100,
            "calcium": food_row["Calcium(mg)"] * portion / 100,
            "proteins": food_row["Protein(g)"] * portion / 100,
            "fat": food_row["Fat(g)"] * portion / 100,
            "carbohydrate": food_row["Carbohydrate(g)"] * portion / 100,
        }

    def predict_nutrition(self, params):
        required_fields = [
            "usia_bulan",
            "gender",
            "berat_kg",
            "tinggi_cm",
            "aktivitas_level",
            "status_asi",
        ]

        if not all(field in params for field in required_fields):
            raise ValueError("Missing required fields")

        try:
            encoded_input = self.encode_input(params)
            input_df = pd.DataFrame([encoded_input])
            input_scaled = scaler_X.transform(input_df)
            pred_scaled = model.predict(input_scaled)
            prediction = scaler_y.inverse_transform(pred_scaled)

            return {
                "calories_needed": round(float(max(0, prediction[0][0])), 2),
                "proteins_needed": round(float(max(0, prediction[0][1])), 2),
                "fat_needed": round(float(max(0, prediction[0][2])), 2),
                "carbohydrate_needed": round(float(max(0, prediction[0][3])), 2),
            }

        except Exception as e:
            raise ValueError(f"Prediction error: {str(e)}")

    def encode_input(self, params):
        # Mapping kategori ke nilai encoding
        gender_mapping = {"L": 0, "P": 1}
        aktivitas_mapping = {"Rendah": 1, "Sedang": 3, "Aktif": 0, "Sangat_Aktif": 2}
        status_asi_mapping = {"ASI_Eksklusif": 1, "ASI+MPASI": 0, "MPASI": 2}

        # Encode data input
        try:
            encoded_data = {
                "Usia_Bulan": params["usia_bulan"],
                "Gender": gender_mapping[params["gender"]],
                "Berat_Kg": params["berat_kg"],
                "Tinggi_Cm": params["tinggi_cm"],
                "Aktivitas_Level": aktivitas_mapping[params["aktivitas_level"]],
                "Status_ASI": status_asi_mapping[params["status_asi"]],
            }
            return encoded_data
        except KeyError as e:
            raise ValueError(f"Invalid input for encoding: {e}")


# def initialize_user_tracking(self, user_data):
#         required_fields = [
#             "user_id",
#             "usia_bulan",
#             "gender",
#             "berat_kg",
#             "tinggi_cm",
#             "aktivitas_level",
#             "status_asi",
#         ]

#         if not all(field in user_data for field in required_fields):
#             raise ValueError("Missing required fields")

#         prediction_params = {
#             "age": user_data["usia_bulan"],
#             "weight": user_data["berat_kg"],
#             "gender": user_data["gender"],
#             "height": user_data["tinggi_cm"],
#             "activity": user_data["aktivitas_level"],
#             "asi_status": user_data["status_asi"],
#         }

#         predicted_needs = self.predict_nutrition(prediction_params)

#         if user_data["user_id"] not in self.daily_tracking:
#             self.daily_tracking[user_data["user_id"]] = {}

#         current_date = datetime.now().strftime("%Y-%m-%d")
#         self.daily_tracking[user_data["user_id"]][current_date] = {
#             "predicted_needs": predicted_needs,
#             "total_nutrients": {
#                 "calories": 0,
#                 "proteins": 0,
#                 "fat": 0,
#                 "carbohydrate": 0,
#                 "calcium": 0,
#             },
#             "foods": [],
#         }

#         return predicted_needs


# def _update_tracking(self, user_id, date, food_name, portion, food_nutrients, notes):
#     for nutrient in food_nutrients:
#         self.daily_tracking[user_id][date]['total_nutrients'][nutrient] += food_nutrients[nutrient]

#     self.daily_tracking[user_id][date]['foods'].append({
#         'name': food_name,
#         'portion': portion,
#         'nutrients': food_nutrients,
#         'notes': notes
#     })


# def predict_nutrition(params):
#     try:
#         # Encode input
#         encoded_input = encode_input(
#             usia_bulan=params["age"],
#             gender=params["gender"],
#             berat_kg=params["weight"],
#             tinggi_cm=params["height"],
#             aktivitas_level=params["activity"],
#             status_asi=params["asi_status"],
#         )

#         # Konversi ke DataFrame
#         input_df = pd.DataFrame([encoded_input])

#         # Normalisasi input
#         input_scaled = scaler_X.transform(input_df)

#         # Prediksi
#         pred_scaled = model.predict(input_scaled)

#         # Balikkan normalisasi pada prediksi
#         prediction = scaler_y.inverse_transform(pred_scaled)

#         return {
#             "calories_needed": float(max(0, prediction[0][0])),
#             "proteins_needed": float(max(0, prediction[0][1])),
#             "fat_needed": float(max(0, prediction[0][2])),
#             "carbohydrate_needed": float(max(0, prediction[0][3])),
#         }
#     except Exception as e:
#         raise ValueError(f"Prediction error: {str(e)}")

# def evaluate_nutrition(predicted, consumed):
#     evaluation = {}
#     for nutrient in ['calories', 'proteins', 'fat', 'carbohydrate']:
#         if nutrient not in predicted:
#             continue

#         consumed_amount = consumed[nutrient]
#         predicted_amount = predicted[nutrient]
#         percentage = (consumed_amount / predicted_amount * 100) if predicted_amount > 0 else 0

#         evaluation[nutrient] = {
#             'consumed': round(consumed_amount, 2),
#             'predicted_needed': round(predicted_amount, 2),
#             'percentage': round(percentage, 1),
#             'status': 'adequate' if 90 <= percentage <= 110 else 'low' if percentage < 90 else 'high'
#         }

#     return evaluation
