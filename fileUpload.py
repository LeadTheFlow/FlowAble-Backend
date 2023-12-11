from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

CORS(app, supports_credentials=True, resources={r"/upload": {"origins": "http://localhost:3000"}})

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    # 파일 저장 경로 설정
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    return 'Image uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True, port=5003)
