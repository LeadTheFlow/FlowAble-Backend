from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*":{"origins":"*"}})

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        "message" : "Hello this is api end point"
    }

    return jsonify(data)

if __name__ == '__main__': 
    app.run(debug=True, port=5000)