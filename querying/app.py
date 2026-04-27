from flask import Flask, request, jsonify
from database import process_entry, process_exit

app = Flask(__name__)

@app.route("/enterRequest", methods=["POST"])
def enterRequest():
    payload = request.get_json()

    if not payload:
        return jsonify({"success": False, "error": "Invalid payload"}), 400

    try:
        result = process_entry(payload)
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/exitRequest", methods=["POST"])
def exitRequest():
    payload = request.get_json()

    if not payload:
        return jsonify({"success": False, "error": "Invalid payload"}), 400

    try:
        result = process_exit(payload)
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
