
1. Predict Nutrition

POST 127.0.0.1:5000/api/prediction/predict_nutrition
request:
```
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
```
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

2. Inisialisasi tracking
POST http://127.0.0.1:5000/api/tracking/initialize-tracking
REQUEST:
```
{
    "user_id": "user123",
    "usia_bulan": 12,
    "gender": "L",
    "berat_kg": 9.5,
    "tinggi_cm": 75,
    "aktivitas_level": "Sedang",
    "status_asi": "ASI+MPASI"
}
```

RESPONSE:
```
{
    "data": {
        "predicted_needs": {
            "calories_needed": 918.9876098632812,
            "carbohydrate_needed": 98.3218765258789,
            "fat_needed": 63.94084167480469,
            "proteins_needed": 20.159221649169922
        },
        "tracking_initialized": true
    },
    "status": "success"
}
```

3. Add Food Tracking

POST http://127.0.0.1:5000/api/tracking/add-food
Request:
```
{
    "user_id": "user123",
    "food_name": "ASI (Air Susu Ibu)",
    "date": "2024-10-20",
    "portion": 100
}
```

Response:
```
{
    "data": {
        "foods": [
            {
                "name": "ASI (Air Susu Ibu)",
                "notes": "ASI Eksklusif direkomendasikan oleh WHO sebagai sumber nutrisi eksklusif.",
                "nutrients": {
                    "calcium": 34.0,
                    "calories": 70.0,
                    "carbohydrate": 7.0,
                    "fat": 4.2,
                    "proteins": 1.2
                },
                "portion": 100.0
            }
        ],
        "total_nutrients": {
            "calcium": 34.0,
            "calories": 70.0,
            "carbohydrate": 7.0,
            "fat": 4.2,
            "proteins": 1.2
        }
    },
    "status": "success"
}
```

4. Get Daily Tracking
```
GET http://127.0.0.1:5000/api/tracking/get-daily/user123/2024-01-20
```
