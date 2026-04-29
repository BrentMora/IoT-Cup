from flask import Flask, request, jsonify
from database import process_entry, process_exit

app = Flask(__name__)

@app.route("/enterRequest", methods=["POST"])
def enterRequest():
    payload = request.get_json()

    if not payload:
        return jsonify({"success": False, "status": "no data received"}), 400

    try:
        result = process_entry(payload)
        return jsonify({"success": result[0], "status": result[1]})
    except Exception as e:
        return jsonify({"success": False, "status": "unhandled error"}), 500

@app.route("/exitRequest", methods=["POST"])
def exitRequest():
    payload = request.get_json()

    if not payload:
        return jsonify({"success": False, "status": "no data received"}), 400

    try:
        result = process_exit(payload)
        return jsonify({"success": result[0], "status": result[1]})
    except Exception as e:
        return jsonify({"success": False, "status": "unhandled error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)