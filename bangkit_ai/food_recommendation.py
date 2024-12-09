import pandas as pd
import pickle
from pulp import *

def load_models():
    with open('models/recommend_food/scaler_food_recommendation.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    with open('models/recommend_food/hybrid_similarity_matrix_food_recommendation.pkl', 'rb') as f:
        hybrid_similarity = pickle.load(f)
    
    df = pd.read_csv('dataset_baby/data_baby_food.csv')
    return scaler, hybrid_similarity, df

def process_results(prob, filtered_df, food_vars, daily_budget):
    if LpStatus[prob.status] == 'Optimal':
        # Ambil makanan yang terpilih berdasarkan hasil solver
        selected_foods = [(i, value(food_vars[i])) 
                         for i in filtered_df.index if value(food_vars[i]) > 0.01]
        
        results = []
        for idx, qty in selected_foods:
            food_data = filtered_df.loc[idx].copy()
            food_data['Quantity'] = qty
            food_data['Total_Price'] = qty * food_data['Original_Price_per_product(IDR)']
            results.append(food_data)
            
        final_recommendations = pd.DataFrame(results)

        # Rename columns
        column_mapping = {
            'Food(per 100g)': 'Nama_Makanan',
            'Quantity': 'Banyak_produk',
            'Original_Price_per_product(IDR)': 'Harga_per_Porsi(IDR)',
            'Total_Price': 'Total_Harga',
            'Original_Calorie(kcal)_per_package': 'Kalori_per_Porsi(kcal)',
            'Original_Protein(g)_per_package': 'Protein_per_Porsi(gr)',
            'Original_Carbohydrate(g)_per_package': 'Karbohidrat_per_Porsi(gr)',
            'Original_Fat(g)_per_package': 'Lemak_per_Porsi(gr)',
            'weight_product(g)': 'Berat_per_Produk(gr)'
        }

        final_recommendations = final_recommendations.rename(columns=column_mapping)

        # Calculate totals
        total_nutrients = {
            'Kalori': sum(row['Kalori_per_Porsi(kcal)'] * row['Banyak_produk'] 
                         for _, row in final_recommendations.iterrows()),
            'Protein': sum(row['Protein_per_Porsi(gr)'] * row['Banyak_produk'] 
                          for _, row in final_recommendations.iterrows()),
            'Karbohidrat': sum(row['Karbohidrat_per_Porsi(gr)'] * row['Banyak_produk'] 
                              for _, row in final_recommendations.iterrows()),
            'Lemak': sum(row['Lemak_per_Porsi(gr)'] * row['Banyak_produk'] 
                        for _, row in final_recommendations.iterrows())
        }

        total_cost = final_recommendations['Total_Harga'].sum()
        remaining_budget = daily_budget - total_cost

        return final_recommendations[['Nama_Makanan', 'Banyak_produk', 
                                    'Berat_per_Produk(gr)',  # Menambahkan kolom berat ke output
                                    'Harga_per_Porsi(IDR)', 'Total_Harga',
                                    'Kalori_per_Porsi(kcal)', 'Protein_per_Porsi(gr)',
                                    'Karbohidrat_per_Porsi(gr)', 'Lemak_per_Porsi(gr)',
                                    'Notes']], {
            'Total_Nutrients': total_nutrients,
            'Remaining_Budget': remaining_budget
        }
    else:
        return "Tidak ada solusi yang ditemukan. Coba lagi dengan budget yang lebih tinggi.", {}

def get_food_recommendations(age_months, daily_needs, daily_budget, user_preferences=None):
    # Load models
    scaler, hybrid_similarity, df = load_models()
    
    # Preprocessing
    df = df.fillna(0)
    features_to_normalize = ['Calcium(mg)', 'Protein(g)', 'Carbohydrate(g)',
                           'Fat(g)', 'Calorie(kcal)', 'Price_per_product(IDR)']
    df[features_to_normalize] = scaler.transform(df[features_to_normalize])

    # Filter berdasarkan umur
    filtered_df = df[
        (df['Recommended_Age_Start(months)'] <= age_months) &
        (df['Recommended_Age_End(months)'] >= age_months)
    ]
    
    if filtered_df.empty:
        return "No food matches the age criteria", {}

    # Proses user preferences
    if user_preferences:
        pref_indices = [i for i, food in enumerate(df['Food(per 100g)']) 
                       if food in user_preferences]
        if pref_indices:
            similarity_scores = hybrid_similarity[pref_indices].mean(axis=0)
            filtered_df['similarity_score'] = similarity_scores[filtered_df.index]
            filtered_df = filtered_df.sort_values('similarity_score', ascending=False)

    # Inverse transform untuk mendapatkan nilai asli
    original_values = scaler.inverse_transform(filtered_df[features_to_normalize])
    for i, feature in enumerate(features_to_normalize):
        filtered_df[f'Original_{feature}'] = original_values[:, i]

    # Hitung nutrisi per package
    for nutri in ['Calcium(mg)', 'Protein(g)', 'Carbohydrate(g)', 'Fat(g)', 'Calorie(kcal)']:
        filtered_df[f'Original_{nutri}_per_package'] = (
            filtered_df[f'Original_{nutri}'] / 100) * filtered_df['weight_product(g)']

    # Setup Linear Programming
    prob = LpProblem("Hybrid_Food_Recommendation", LpMinimize)
    food_vars = LpVariable.dicts("Food", filtered_df.index, lowBound=0, cat='Integer')

    # Objective: Minimize quantity while maximizing similarity (if available)
    if 'similarity_score' in filtered_df.columns:
        prob += lpSum([food_vars[i] * (1 - filtered_df.loc[i, 'similarity_score']) 
                      for i in filtered_df.index])
    else:
        prob += lpSum([food_vars[i] for i in filtered_df.index])

    # Nutrient constraints for age 0-5 months
    if age_months < 6:
        # Budget constraints
        prob += lpSum([filtered_df.loc[i, 'Original_Price_per_product(IDR)'] * food_vars[i] 
                      for i in filtered_df.index]) <= daily_budget * 1.5

        # Calories
        prob += lpSum([filtered_df.loc[i, 'Original_Calorie(kcal)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) <= daily_needs['calorie'] * 1.5
        prob += lpSum([filtered_df.loc[i, 'Original_Calorie(kcal)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) >= daily_needs['calorie'] * 0.8
        
        # Protein
        prob += lpSum([filtered_df.loc[i, 'Original_Protein(g)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) <= daily_needs['protein'] * 2.0
        prob += lpSum([filtered_df.loc[i, 'Original_Protein(g)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) >= daily_needs['protein'] * 0.5
        
        # Other nutrients
        for nutrient, need in [('Carbohydrate(g)', 'carb'), ('Fat(g)', 'fat')]:
            prob += lpSum([filtered_df.loc[i, f'Original_{nutrient}_per_package'] * food_vars[i] 
                          for i in filtered_df.index]) <= daily_needs[need] * 1.5
            prob += lpSum([filtered_df.loc[i, f'Original_{nutrient}_per_package'] * food_vars[i] 
                          for i in filtered_df.index]) >= daily_needs[need] * 0.5

        # Ensure minimum ASI if in preferences
        if 'ASI (Air Susu Ibu)' in user_preferences:
            asi_index = filtered_df[filtered_df['Food(per 100g)'] == 'ASI (Air Susu Ibu)'].index
            if len(asi_index) > 0:
                prob += food_vars[asi_index[0]] >= 1

        # Pastikan ASI diprioritaskan
        asi_index = filtered_df[filtered_df['Food(per 100g)'] == 'ASI (Air Susu Ibu)'].index
        formula_index = filtered_df[filtered_df['Food(per 100g)'] == 'Susu Formula Bayi 0-6 bulan'].index
        
        if len(asi_index) > 0:
            # Memastikan minimal 1 porsi ASI
            prob += food_vars[asi_index[0]] >= 1
            
            # Jika ada susu formula, batasi penggunaannya
            if len(formula_index) > 0:
                # Pastikan jumlah formula tidak melebihi ASI
                prob += food_vars[formula_index[0]] <= food_vars[asi_index[0]] * 0.5
                
                # Atau bisa juga membatasi formula dengan nilai maksimal
                prob += food_vars[formula_index[0]] <= 1
    # buat constraints untuk usia 6 ke atas
    else:
        # Budget constraints
        prob += lpSum([filtered_df.loc[i, 'Original_Price_per_product(IDR)'] * food_vars[i] 
                      for i in filtered_df.index]) <= daily_budget * 1.5
        prob += lpSum([filtered_df.loc[i, 'Original_Price_per_product(IDR)'] * food_vars[i] 
                      for i in filtered_df.index]) >= daily_budget * 0.5

        # Nutrient constraints
        # Calories (80-120%)
        prob += lpSum([filtered_df.loc[i, 'Original_Calorie(kcal)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) <= daily_needs['calorie'] * 1.2
        prob += lpSum([filtered_df.loc[i, 'Original_Calorie(kcal)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) >= daily_needs['calorie'] * 0.8

        # Protein (80-200%)
        prob += lpSum([filtered_df.loc[i, 'Original_Protein(g)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) <= daily_needs['protein'] * 2.0
        prob += lpSum([filtered_df.loc[i, 'Original_Protein(g)_per_package'] * food_vars[i] 
                      for i in filtered_df.index]) >= daily_needs['protein'] * 0.8

        # Other nutrients (80-120%)
        for nutrient, need in [('Carbohydrate(g)', 'carb'), ('Fat(g)', 'fat')]:
            prob += lpSum([filtered_df.loc[i, f'Original_{nutrient}_per_package'] * food_vars[i] 
                          for i in filtered_df.index]) <= daily_needs[need] * 1.2
            prob += lpSum([filtered_df.loc[i, f'Original_{nutrient}_per_package'] * food_vars[i] 
                          for i in filtered_df.index]) >= daily_needs[need] * 0.8
    # Solve model
    prob.solve(PULP_CBC_CMD(msg=0))

    return process_results(prob, filtered_df, food_vars, daily_budget)

