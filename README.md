## Measure Classify

POST http://127.0.0.1:5000/measure-classify
Request:

```json
{
  "url": "https://storage.googleapis.com/stunby_bucket/baby_testing/baby_3.jpeg",
  "weight": 5.5,
  "age": 6,
  "gender": "male"
}
```

Response:

```json
{
  "baby_length": 45.79,
  "imt": 25.99243856332703,
  "nutritional_status_length": "Sangat Pendek", // "Sangat Pendek", "Pendek", "Normal", "Tinggi", "Tidak Diketahui"
  "nutritional_status_weight": "Gizi Kurang", // "Gizi Buruk", "Gizi Kurang", "Gizi Baik", "Gizi Lebih", "Kategori Tidak DIketahui"
  "status_bb_tb": "Gemuk", // "Sangat Kurus", "Kurus", "Normal", "Gemuk", "Kategori Tidak Diketahui"
  "status_imt": "Obesitas (Obese)", // "Gizi Buruk (Severely Wasted)", "Gizi Kurang (Wasted)", "Gizi Baik (Normal)", "Berisiko Gizi Lebih (Possible Risk of Overweight)", "Gizi Lebih (Overweight)", "Obesitas (Obese)", "Kategori Tidak Diketahui"
  "z_score_bb_tb": 9.666666666666671,
  "z_score_length": -10.285714285714311,
  "z_score_weight": -2.999999999999998
}
```

## Predict Nutrition

POST 127.0.0.1:5000/predict_nutrition
request:

```json
{
    "usia_bulan": 12,           # int: 0-24 bulan
    "gender": "L",              # str: "L" atau "P"
    "berat_kg": 9.5,           # float: berat dalam kg
    "tinggi_cm": 75.0,         # float: tinggi dalam cm
    "aktivitas_level": "Sedang", # str: "Rendah"/"Sedang"/"Aktif"/"Sangat_Aktif"
    "status_asi": "ASI+MPASI"   # str: "ASI_Eksklusif"/"ASI+MPASI"/"MPASI"
}
```

response:

```json
{
  "status": "success",
  "data": {
    "calories_needed": 850.5, // kalori dalam kkal
    "proteins_needed": 20.1, // protein dalam gram
    "fat_needed": 30.2, // lemak dalam gram
    "carbohydrate_needed": 120.5 // karbohidrat dalam gram
  }
}
```

## Add Food Tracking

POST http://127.0.0.1:5000/api/tracking/add-food

request:

```json
{
  "food_name": "ASI (Air Susu Ibu)",
  "portion": 200
}
```

response:

```json
{
  "data": {
    "name": "ASI (Air Susu Ibu)",
    "notes": "ASI Eksklusif direkomendasikan oleh WHO sebagai sumber nutrisi eksklusif.",
    "nutrients": {
      "calcium": 68.0,
      "calories": 140.0,
      "carbohydrate": 14.0,
      "fat": 8.4,
      "proteins": 2.4
    },
    "portion": 200.0
  },
  "status": "success"
}
```

## recommendation food

POST http://127.0.0.1:5000/recommend

REQUEST

```json
{
  "age_months": 12,
  "daily_needs": {
    "protein": 20.1,
    "carb": 120.5,
    "fat": 30.2,
    "calories": 850.5
  },
  "budget": 50000
}
```

RESPONSE

```json
[
  {
    "Calorie(kcal)": 150.0,
    "Carbohydrate(g)": 22.0,
    "Fat(g)": 4.5,
    "Food(per 100g)": "Bubur Pisang Keju",
    "Notes": "Bubur pisang dengan tambahan keju parut. Sumber kalsium dan potasium.",
    "Price_per_product(IDR)": 12000.0,
    "Protein(g)": 3.5000000000000004
  },
  {
    "Calorie(kcal)": 82.0,
    "Carbohydrate(g)": 12.0,
    "Fat(g)": 2.5,
    "Food(per 100g)": "Sup Cream Jagung",
    "Notes": "Jagung dan krim yang dihaluskan menjadi sup. Sumber energi dan protein.",
    "Price_per_product(IDR)": 45000.0,
    "Protein(g)": 2.8
  },
  {
    "Calorie(kcal)": 72.0,
    "Carbohydrate(g)": 8.0,
    "Fat(g)": 3.8,
    "Food(per 100g)": "Susu Formula Lanjutan 6-12 bulan",
    "Notes": "Contoh merek: Bebelac Gold 2 SGM 2 Dancow 2. Diperkaya dengan zat besi dan vitamin esensial.",
    "Price_per_product(IDR)": 15800.000000000002,
    "Protein(g)": 1.8
  },
  {
    "Calorie(kcal)": 107.0,
    "Carbohydrate(g)": 17.0,
    "Fat(g)": 2.5,
    "Food(per 100g)": "Bubur Havermut Susu",
    "Notes": "Havermut yang dimasak dengan susu. Sumber energi dan serat.",
    "Price_per_product(IDR)": 35000.0,
    "Protein(g)": 4.0
  },
  {
    "Calorie(kcal)": 408.0,
    "Carbohydrate(g)": 75.0,
    "Fat(g)": 9.0,
    "Food(per 100g)": "Biskuit Bayi (promina)",
    "Notes": "Biskuit khusus bayi yang mudah larut dalam mulut. Sumber energi cepat.",
    "Price_per_product(IDR)": 19000.0,
    "Protein(g)": 6.3
  }
]
```
