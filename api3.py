from dotenv import load_dotenv
load_dotenv()
import psycopg2
from flask import Flask, jsonify, request, render_template
from datetime import datetime
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def root():
    return render_template("index.html")
    

@app.route('/measurements', methods=['GET'])
def get_measurements():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, station_name, date, ph, turbidity, dissolved_oxygen, temperature, conductivity FROM measurements ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    measurements = {row[0]: {
        "station_name": row[1],
        "date": row[2],
        "ph": row[3],
        "turbidity": row[4],
        "dissolved_oxygen": row[5],
        "temperature": row[6],
        "conductivity": row[7]
    } for row in rows}
    return jsonify(measurements), 201


@app.route('/measurements/<int:measurement_id>', methods=['GET'])
def get_measurement(measurement_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT station_name, date, ph, turbidity, dissolved_oxygen, temperature, conductivity FROM measurements WHERE id = %s;", (measurement_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "Measurement not found"}),404
    measurement = {
        "station_name": row[0],
        "date": row[1],
        "ph": row[2],
        "turbidity": row[3],
        "dissolved_oxygen": row[4],
        "temperature": row[5],
        "conductivity": row[6]
    }
    return jsonify(measurement), 201


@app.route('/measurements/<string:station_name>', methods=['GET'])
def get_measurement_by_station(station_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, station_name, date, ph, turbidity, dissolved_oxygen, temperature, conductivity FROM measurements WHERE station_name = %s order by id;", (station_name,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        return jsonify({"error": f"No measurements found in {station_name}"}), 404
    measurements = [{
        "id": row[0],
        "station_name": row[1],
        "date": row[2],
        "ph": row[3],
        "turbidity": row[4],
        "dissolved_oxygen": row[5],
        "temperature": row[6],
        "conductivity": row[7]
    } for row in rows]
    return jsonify(measurements), 201


@app.route('/measurements', methods=['POST'])
def create_measurement():
    data = request.get_json()
    added=[]
    conn = get_db_connection()
    cur = conn.cursor()
    for items in data:
        time = datetime.now()
        required_fields = ["station_name", "ph", "turbidity", "dissolved_oxygen", "temperature", "conductivity"]
        missing_fields = [field for field in required_fields if field not in items]
        if missing_fields:
            cur.close()
            conn.close()
            return jsonify({"error": f"Missing required field: {', '.join(missing_fields)}"}), 404
        cur.execute(
            """
            INSERT INTO measurements (station_name, date, ph, turbidity, dissolved_oxygen, temperature, conductivity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                items["station_name"],
                time.strftime("%Y-%m-%d %H:%M:%S"),
                items["ph"],
                items["turbidity"],
                items["dissolved_oxygen"],
                items["temperature"],
                items["conductivity"]
            )
        )
        new_id = cur.fetchone()[0]
        added.append(new_id)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Measurement(s) added with id(s): {', '.join(map(str, added))}"}), 200



@app.route('/measurements/<int:measurement_id>', methods=['DELETE'])
def delete_measurement(measurement_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM measurements WHERE id = %s RETURNING id;", (measurement_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        return jsonify({"error": "Measurement not found"}), 404
    return jsonify({"message": "Measurement deleted"}), 200

@app.route('/measurements/<ids>', methods=['DELETE'])
def delete_multiple_by_url(ids):
    try:
        id_list = [int(i) for i in ids.split(',') if i.strip().isdigit()]
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    deleted = []
    not_found = []
    for measurement_id in id_list:
        cur.execute("DELETE FROM measurements WHERE id = %s RETURNING id;", (measurement_id,))
        result = cur.fetchone()
        if result:
            deleted.append(measurement_id)
        else:
            not_found.append(measurement_id)
    conn.commit()
    cur.close()
    conn.close()
    response = {"deleted": deleted}
    if not_found:
        response["not_found"] = not_found
    return jsonify(response), 201

@app.route('/measurements/<int:measurement_id>', methods=['PUT'])
def modify_measurement(measurement_id):
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    data = request.get_json()
    time = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
   
    cur.execute("SELECT station_name, ph, turbidity, dissolved_oxygen, temperature, conductivity FROM measurements WHERE id = %s;", (measurement_id,))
    current = cur.fetchone()

    if not current:
        cur.close()
        conn.close()
        return jsonify({"error": "Measurement not found"}), 404
    
    station_name = data.get("station_name", current[0])
    ph = data.get("ph", current[1])
    turbidity = data.get("turbidity", current[2])
    dissolved_oxygen = data.get("dissolved_oxygen", current[3])
    temperature = data.get("temperature", current[4])
    conductivity = data.get("conductivity", current[5])
    
    cur.execute(
        """
        UPDATE measurements SET station_name = %s, date = %s, ph = %s, turbidity = %s, dissolved_oxygen = %s, temperature = %s, conductivity = %s WHERE id = %s;
        """,
        (
            station_name,
            time.strftime("%Y-%m-%d %H:%M:%S"),
            ph,
            turbidity,
            dissolved_oxygen,
            temperature,
            conductivity,
            measurement_id
        )
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Measurement updated"}), 200


@app.route('/measurements/batch', methods=['PUT'])
def modify_multiple_measurements():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of measurement updates"}), 404
    updated = []
    not_found = []
    duplicate_id=set()
    conn = get_db_connection()
    cur = conn.cursor()
    time = datetime.now()
    for item in data:
        print(item)
        measurement_id = item.get("id")
        if measurement_id in duplicate_id:
            cur.close()
            conn.close()
            return jsonify({"error": "Duplicate ID found"}), 404
        duplicate_id.add(measurement_id)
        if "id" not in item:
            cur.close()
            conn.close()
            return jsonify({"error": "Missing required field: id"}), 404
        # if measurement_id is None:
        #     continue
        cur.execute("SELECT station_name, ph, turbidity, dissolved_oxygen, temperature, conductivity FROM measurements WHERE id = %s;", (measurement_id,))
        current = cur.fetchone()
        if not current:
            not_found.append(measurement_id)
            continue

        station_name = item.get("station_name", current[0])
        ph = item.get("ph", current[1])
        turbidity = item.get("turbidity", current[2])
        dissolved_oxygen = item.get("dissolved_oxygen", current[3])
        temperature = item.get("temperature", current[4])
        conductivity = item.get("conductivity", current[5])

        cur.execute(
            """
            UPDATE measurements SET station_name = %s, date = %s, ph = %s, turbidity = %s, dissolved_oxygen = %s, temperature = %s, conductivity = %s WHERE id = %s;
            """,
            (
                station_name,
                time.strftime("%Y-%m-%d %H:%M:%S"),
                ph,
                turbidity,
                dissolved_oxygen,
                temperature,
                conductivity,
                measurement_id
            )
        )
        updated.append(measurement_id)
    conn.commit()
    cur.close()
    conn.close()
    response = {"updated": updated}
    if not_found:
        response["not_found"] = not_found
    return jsonify(response), 201


if __name__ == '__main__': 
    app.run(debug=True)