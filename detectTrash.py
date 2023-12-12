from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from PIL import Image
import io
import numpy as np
import cv2

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={r"/api/detectTrash": {"origins": "http://localhost:3000"}})

@app.route("/api/detectTrash", methods=['POST'])
def detectTrash():
    image_file = request.files.get('file')
    if not image_file:
        return jsonify({"error": "File not provided"})

    # 이미지를 PIL Image 객체로 변환 후 바이트 스트림으로 저장
    image = Image.open(image_file)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    # Object Detection API 요청
    url = "https://objectdetect-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/0ca5b4ed-0702-4eee-ad9b-1d06af73ef97/detect/iterations/Iteration3/image"
    headers = {
        'Prediction-Key': 'b9090cf45c45448fa6fc2620c91bafe0',
        'Content-Type': 'application/octet-stream'
    }
    response = requests.post(url, headers=headers, data=img_byte_arr)
    result = response.json()

    # OpenCV를 사용하여 이미지 처리
    nparr = np.frombuffer(img_byte_arr, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return jsonify({"error": "Invalid image data"})
    
    h, w = image.shape[:2]
    # 이미지 가로, 세로 3등분하기
    # 가로 2개, 세로 2개 선을 기준으로 나눈다.
    # one_w : 가로 첫번째 선, two_w : 가로 두번째 선
    # one_h : 세로 첫번째 선, two_h : 세로 두번째 선
    one_w = w / 3
    two_w = 2 * (w / 3)
    one_h = h / 3
    two_h = 2 * (h / 3)
    
    # 물체 감지 여부 확인 후 없다면 return
    detected_objects = result.get('predictions', [])
    if not detected_objects:
        return jsonify({"message": "물체 없음"})
    
    for pred in result.get('predictions', []):
        if pred['probability'] >= 0.9:
            box = pred['boundingBox']
            left = int(box['left'] * w)
            top = int(box['top'] * h)
            width = int(box['width'] * w)
            height = int(box['height'] * h)
            
            #바운딩 박스 중심 계산
            center_x = left + (width / 2)
            center_y = top + (height / 2)
            
            # 위치에 따른 구역 결정 (9분할)
            if center_x < one_w and center_y < one_h:
                position = "왼쪽 상단"
            elif center_x > one_w and center_x < two_w and center_y < one_h:
                position = "상단"
            elif center_x > two_w and center_y < one_h:
                position = "오른쪽 상단"
            elif center_x < one_w and center_y > one_h and center_y < two_h:
                position = "왼쪽"
            elif center_x > one_w and center_x < two_h and center_y > one_h and center_y < two_h:
                position = "중앙"
            elif center_x > two_w and center_y > one_h and center_y < two_h:
                position = "오른쪽"
            elif center_x < one_w and center_y > two_h:
                position = "왼쪽 하단"
            elif center_x > one_w and center_x < two_h and center_y > two_h:
                position = "하단"
            elif center_x > two_h and center_y > two_h:
                position = "오른쪽 하단"
            else:
                position = "위치 알 수 없음"
            
            data = {"position":position}

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5004)
            