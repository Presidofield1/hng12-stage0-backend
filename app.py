#Import needed libraries

from flask import Flask, jsonify, request
import os
import requests
from flask_cors import CORS
from datetime import datetime, timezone

# Initialise app
app = Flask(__name__)
CORS(app)

@app.get('/api/classify')
def classify_name():
    name = request.args.get('name')

    #Check if name is Missing or Empty (400)
    if not name:
        return jsonify({"status": "error", "message": "Missing or empty name"}), 400
    
    if not isinstance(name, str) or name.isdigit():
        return jsonify({"status": "error", "message": "name is not string"}), 422
    try:
        # Call the API provided
        external_url = f"https://api.genderize.io/?name={name}"
        response = requests.get(external_url, timeout=5) # 5s timeout to keep it fast

        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Upstream failure"}), 502
        
        data = response.json()

        # Cases Presented
        gender = data.get("gender")
        sample_size = data.get("count", 0)
        probability = data.get ("probability", 0.0)

        if gender is None or sample_size == 0:
            return jsonify ({"status": "error", "message": "No prediction available"})
        
        # Processing the given conditions
        is_confident = (probability >= 0.7) and (sample_size >= 100)

        #ISO 8610 UTC Timestamp
        process_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


        return jsonify({
            "status": "success",
            "data": {
                "name": name,
                "gender": gender,
                "probability": probability,
                "sample_size": sample_size,
                "condition": is_confident,
                "processed_time": process_time
            }
        }), 200
    
    except Exception:
        return jsonify({"status": "error", "message": "Server failure"}), 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)


