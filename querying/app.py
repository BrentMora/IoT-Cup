from flask import Flask, request, jsonify
from database import query_and_update

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    payload = request.get_json()

    if not payload:
        return jsonify({"success": False, "error": "Invalid payload"}), 400

    try:
        result = query_and_update(payload)
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
