from flask import Flask, jsonify, request
import os
import json
import base64
import string
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*":{"origins":"*"}})

UPLOAD_FOLDER = 'uploads'  # 업로드된 파일을 저장할 폴더
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 허용되는 파일 확장자 집합

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/product/OCR", methods=['POST'])
def OCR_result():
    # 요청에서 이미지 파일 가져오기
    uploaded_file = request.files.get('file')

    if not uploaded_file or not allowed_file(uploaded_file.filename):
        return jsonify({"error": "Invalid file or file type not allowed"})

    # 업로드된 파일을 안전한 이름으로 저장
    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(file_path)

    # OCR을 위한 코드 (이 부분은 OCR API에 따라 수정 필요)
    URL = "https://289x53pm3g.apigw.ntruss.com/custom/v1/26842/c927448b0a02c01ba659d0339776a7971c45256d5406bf1a8ec2aaee0ba591fd/general"
    KEY = "RFl5cE9XVmV6bUhOSkhZaE9JT0VLV3ZKZFp4d0N0QnE="

    headers = {
        "Content-Type": "application/json",
        "X-OCR-SECRET": KEY
    }

    with open(file_path, "rb") as f:
        img = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "version": "V1",
        "requestId": "sample_id",
        "timestamp": 0,
        "images": [
            {
                "name": "sample_image",
                "format": "png",
                "data": img
            }
        ]
    }

    response = request.post(URL, data=json.dumps(payload), headers=headers)
    res = json.loads(response.text)

    texts = []

    if 'images' in res and 'fields' in res['images'][0]:
        for i in range(len(res['images'][0]['fields'])):
            texts.append(res['images'][0]['fields'][i]['inferText'])

    # OCR 결과를 분석하는 나머지 코드
    brands_list = ['시크릿데이', '화이트', '라엘', '좋은느낌', '유기농본', '오씨본', '한나패드', '바디피트', '순수한면', '쏘피', '오드리선', '허브데이', '콜만', '청담소녀', '뷰코셋', '리버티', '라네이처', '라라문', '내츄럴코튼', '잇츠미', '나트라케어', '예지미인', '앨리스', '엘리스', '슈베스', '슈배스', '29데이즈', '이십구데이즈', '마로메라', '네띠', '잇츠마인'
                  ,'sofy', 'la nature', 'rael', 'corman', 'vuokkoset', 'lalamoon', 'natracare', 'subes', 'maromera', 'naty', 'audrey sun', 'ocbon', 'audreysun', 'maro']
    size_list = ['대형', '중형', '소형', '중대형', '팬티라이너', '오버나이트', '슈퍼롱', '면생리대', '롱라이너'
                'super', 'long', 'normal', 'large', 'medium', 'pantyliner', 'overnight', 'small', 'night']

    brand = ""
    size = ""

    for x in texts:
        x_lower = x.lower()
        translator = str.maketrans('', '', string.punctuation)
        x_lower = x_lower.translate(translator)

        if x in brands_list or x_lower in brands_list:
            brand = x if x in brands_list else x_lower
            if brand == 'maro':
                brand = 'maro mera'

        else:
            for size_option in size_list:
                if size_option in x:
                    size = size_option
                    break
            if not size:
                for size_option in size_list:
                    if size_option in x_lower:
                        size = size_option
                        break

    result = {"brand": brand, "size": size}

    return jsonify(result), 200, {'Content-Type': 'application/json; charset=utf-8'}

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5002)
