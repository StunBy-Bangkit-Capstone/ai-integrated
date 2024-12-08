from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os

# Muat model dan data yang disimpan
current_dir = os.path.dirname(__file__)  # Mendapatkan direktori file Python ini
model_path = os.path.join(
    current_dir, "models", "recommend_food", "food_recommendation_model.pkl"
)

with open(model_path, "rb") as f:
    model_data = pickle.load(f)
df = model_data["df"]
similarity_matrix = model_data["similarity_matrix"]
scaler = model_data["scaler"]


# Fungsi untuk mendapatkan rekomendasi
def get_recommendations(age_months, daily_needs, budget, top_n=5):
    features_to_normalize = [
        "Calcium(mg)",
        "Protein(g)",
        "Carbohydrate(g)",
        "Fat(g)",
        "Calorie(kcal)",
        "Price_per_product(IDR)",
    ]

    # Filter berdasarkan usia
    filtered_df = df[
        (df["Recommended_Age_Start(months)"] <= age_months)
        & (df["Recommended_Age_End(months)"] >= age_months)
    ]

    # Filter berdasarkan budget
    price_index = features_to_normalize.index("Price_per_product(IDR)")
    original_prices = scaler.inverse_transform(filtered_df[features_to_normalize])[
        :, price_index
    ]
    filtered_df = filtered_df[original_prices <= budget]

    if filtered_df.empty:
        return "Tidak ada makanan yang sesuai dengan kriteria"

    # Normalisasi kebutuhan nutrisi harian
    daily_needs_normalized = {
        "Calcium(mg)": 0,  # nilai default untuk Calcium
        "Protein(g)": daily_needs["protein"],
        "Carbohydrate(g)": daily_needs["carb"],
        "Fat(g)": daily_needs["fat"],
        "Calorie(kcal)": daily_needs["calorie"],
        "Price_per_product(IDR)": 0,  # nilai default untuk Price
    }

    daily_needs_df = pd.DataFrame([daily_needs_normalized])[features_to_normalize]
    daily_needs_scaled = scaler.transform(daily_needs_df)

    # Hitung similarity dengan kebutuhan nutrisi
    nutrition_features = ["Calorie(kcal)", "Protein(g)", "Carbohydrate(g)", "Fat(g)"]

    # Dapatkan indeks yang sesuai untuk nutrition features
    nutrition_indices = [
        features_to_normalize.index(feat) for feat in nutrition_features
    ]

    similarities = cosine_similarity(
        filtered_df[nutrition_features], daily_needs_scaled[:, nutrition_indices]
    )

    # Dapatkan indeks makanan dengan similarity tertinggi
    similar_indices = similarities.flatten().argsort()[::-1][:top_n]

    # Buat DataFrame hasil rekomendasi
    recommendations = filtered_df.iloc[similar_indices].copy()

    # Denormalisasi nilai untuk ditampilkan
    recommendations[features_to_normalize] = scaler.inverse_transform(
        recommendations[features_to_normalize]
    )

    return recommendations[
        [
            "Food(per 100g)",
            "Calorie(kcal)",
            "Protein(g)",
            "Carbohydrate(g)",
            "Fat(g)",
            "Price_per_product(IDR)",
            "Notes",
        ]
    ].to_dict(orient="records")
