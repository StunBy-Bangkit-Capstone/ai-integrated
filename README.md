## Measure Classify

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
  "nutritional_status_length": "Sangat Pendek",
  "nutritional_status_weight": "Gizi Kurang",
  "status_bb_tb": "Gemuk",
  "status_imt": "Obesitas (Obese)",
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
        "calories_needed": 850.5,      # kalori dalam kkal
        "proteins_needed": 20.1,       # protein dalam gram
        "fat_needed": 30.2,           # lemak dalam gram
        "carbohydrate_needed": 120.5   # karbohidrat dalam gram
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

```
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
