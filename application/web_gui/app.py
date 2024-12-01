from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simulated data
data_store = {"counter": 0}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_data", methods=["GET"])
def get_data():
    """Endpoint to fetch the current counter value."""
    return jsonify(data_store)

@app.route("/update_data", methods=["POST"])
def update_data():
    """Endpoint to update the counter value."""
    global data_store
    request_data = request.get_json()
    data_store["counter"] = request_data.get("counter", data_store["counter"])
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)


### - run app -
### - open http://127.0.0.1:5000
