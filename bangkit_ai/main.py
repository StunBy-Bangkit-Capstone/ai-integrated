from flask import Flask, request, jsonify
from classification import nutritional_status
from nutrition_prediction_tracking import df_food
from datetime import datetime
from measurement import measure_all

# from chatbot import load_model, stunby_chatbot, StunbyRAG
from nutrition_prediction_tracking import NutritionTracker
from food_recommendation import get_food_recommendations

app = Flask(__name__)
daily_tracking = {}

"""
request body:
{
    "query": "Apa itu stunting?"
}
response:
{
    "query": "Apa itu stunting?",
    "response": "Stunting adalah "
}z
"""
# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.get_json()
#         query = data.get('query')

#         if not query:
#             return jsonify({'error': 'Query tidak boleh kosong'}), 400

#         response = stunby_chatbot(query, rag_model)
#         return jsonify({
#             'query': query,
#             'response': response
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@app.route("/",methods=["GET"])
def gate():
    return jsonify({"message":"api is ready"})


@app.route("/measure-classify", methods=["POST"])
def measure():
    try:
        data = request.get_json()
        url = data["url"]
        baby_weight = data["weight"]
        age = data["age"]
        gender = data["gender"]
        baby_length = measure_all(url)
        print(f"Baby length: {baby_length}")

        # Konversi tensor ke float dan bulatkan ke 2 desimal untuk output
        if baby_length is not None:
            if hasattr(baby_length, "item"):
                baby_length = float(baby_length.item())
            baby_length = round(baby_length, 2)
        if baby_length is not None and baby_weight is not None:
            try:
                (
                    z_score_bb_tb,
                    status_bb_tb,
                    imt,
                    status_imt,
                    z_score_length,
                    nutritional_status_length,
                    z_score_weight,
                    nutritional_status_weight,
                ) = nutritional_status(gender, age, baby_length, baby_weight)
            except:
                return jsonify({"error": "Data tidak ditemukan"}), 400
            return jsonify(
                {
                    "baby_length": float(baby_length),
                    "z_score_bb_tb": float(z_score_bb_tb),
                    "status_bb_tb": status_bb_tb,
                    "imt": float(imt),
                    "status_imt": status_imt,
                    "z_score_length": float(z_score_length),
                    "nutritional_status_length": nutritional_status_length,
                    "z_score_weight": float(z_score_weight),
                    "nutritional_status_weight": nutritional_status_weight,
                }
            )
        else:
            print("There is something wrong")
            return jsonify({"error": "There is something wrong"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


tracker = NutritionTracker()

@app.route("/add-food", methods=["POST"])
def add_food():
    """
    request:
    {
        "food_name": "ASI (Air Susu Ibu)",
        "portion": 200
    }

    response:
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
    """
    try:
        data = request.get_json()
        result = tracker.add_food_tracking(data, df_food)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/predict-nutrition", methods=["POST"])
def predict_nutrition():
    """
    request:
    {
        "usia_bulan": 12,
        "gender": "L",
        "berat_kg": 9.5,
        "tinggi_cm": 75.0,
        "aktivitas_level": "Sedang",
        "status_asi": "ASI+MPASI"
    }

    response:
    {
        "data": {
            "calories_needed": 946.88,
            "carbohydrate_needed": 102.78,
            "fat_needed": 61.81,
            "proteins_needed": 20.74
        },
        "status": "success"
    }
    """
    try:
        params = request.get_json()
        result = tracker.predict_nutrition(params)
        return jsonify({"status": "success", "data": result}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/recommend-food', methods=['POST'])
def recommend_food():
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['age_months', 'daily_budget', 'daily_needs']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        age_months = data['age_months']
        daily_budget = data['daily_budget']
        daily_needs = data['daily_needs']
        user_preferences = data.get('user_preferences', None)

        # Panggil fungsi rekomendasi
        recommendations, summary = get_food_recommendations(
            age_months=age_months,
            daily_needs=daily_needs,
            daily_budget=daily_budget,
            user_preferences=user_preferences
        )

        # Format response
        if isinstance(recommendations, str):
            return jsonify({
                'status': 'error',
                'message': recommendations
            }), 400

        response = {
            'recommendations': recommendations.to_dict('records'),
            'summary': {
                'total_nutrients': summary['Total_Nutrients'],
                'remaining_budget': summary['Remaining_Budget']
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @app.route("/initialize-tracking", methods=["POST"])
# def initialize_tracking():
#     try:
#         data = request.get_json()
#         predicted_needs = tracker.initialize_user_tracking(data)
#         return (
#             jsonify(
#                 {
#                     "status": "success",
#                     "data": {
#                         "predicted_needs": predicted_needs,
#                         "tracking_initialized": True,
#                     },
#                 }
#             ),
#             200,
#         )
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# @app.route('/get-daily/<user_id>/<date>', methods=['GET'])
# def get_daily(user_id, date):
#     """
#     Mendapatkan data tracking dan evaluasi nutrisi harian.

#     Parameters:
#         user_id (str): ID user
#         date (str): Tanggal dalam format YYYY-MM-DD

#     Returns:
#         JSON dengan data tracking dan evaluasi nutrisi
#     """
#     try:
#         # Validasi format tanggal
#         try:
#             datetime.strptime(date, '%Y-%m-%d')
#         except ValueError:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Invalid date format. Use YYYY-MM-DD'
#             }), 400

#         if user_id not in daily_tracking or date not in daily_tracking[user_id]:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'No tracking data found'
#             }), 404

#         tracking_data = daily_tracking[user_id][date]

#         # Add evaluation if predicted needs exist
#         if 'predicted_needs' in tracking_data:
#             evaluation = evaluate_nutrition(
#                 tracking_data['predicted_needs'],
#                 tracking_data['total_nutrients']
#             )

#             return jsonify({
#                 'status': 'success',
#                 'data': {
#                     'tracking': tracking_data,
#                     'evaluation': evaluation
#                 }
#             }), 200

#         return jsonify({
#             'status': 'success',
#             'data': tracking_data
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
