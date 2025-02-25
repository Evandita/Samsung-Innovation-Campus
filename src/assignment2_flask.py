from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# --- Konfigurasi MongoDB Atlas ---
MONGO_URI = "mongodb+srv://evanditaw:<password>@database.ced6u.mongodb.net/?appName=Database"
client = MongoClient(MONGO_URI)
db = client.get_database("SIC")
collection = db.get_collection("Assignment_2")

# --- Route untuk Halaman Utama ---
@app.route('/')
def index():
    return "Selamat datang di Sensor Data API!"

# --- Route untuk Menerima Data Sensor ---
@app.route('/send_data', methods=['POST'])
def send_data():
    """
    Route ini menerima data sensor dalam format JSON dengan key:
    - temperature
    - humidity
    - LDR
    Data yang diterima akan disimpan ke MongoDB Atlas.
    """
    # Mendapatkan data JSON dari request
    data = request.get_json(force=True)
    
    # Validasi apakah ketiga key ada
    required_fields = ['temperature', 'humidity', 'LDR']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Data sensor tidak lengkap!'}), 400

    # Mempersiapkan data yang akan disimpan
    sensor_data = {
        "temperature": data['temperature'],
        "humidity": data['humidity'],
        "LDR": data['LDR']
    }

    try:
        # Menyimpan data ke MongoDB
        result = collection.insert_one(sensor_data)
        return jsonify({
            'message': 'Data sensor berhasil disimpan!',
            'id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Jalankan server Flask pada host 0.0.0.0 dan port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
