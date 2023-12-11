import os
import requests
import cv2
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/detectTrash", methods=['GET'])
def detectTrash():
    
    image_path = request.args.get('path')
    
    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "File not exists or path not provided"})
    
    # Prediction URL 및 헤더 설정
    url = "https://objectdetect-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/0ca5b4ed-0702-4eee-ad9b-1d06af73ef97/detect/iterations/Iteration3/image"
    headers = {
        'Prediction-Key': 'b9090cf45c45448fa6fc2620c91bafe0',
        'Content-Type': 'application/octet-stream'
    }
    # 이미지 파일을 읽음
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    
    # POST 요청을 보내고 결과를 받음
    response = requests.post(url, headers=headers, data=image_data)
    result = response.json()
    
    image = cv2.imread(image_path)
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
    
    for pred in result['predictions']:
        # 확률이 0.9이상인 예측만 처리하기
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
            
            start_point = (left, top)
            end_point = (left+width, top+height)
            
            color = (255,0,0)
            thickness = 2
            
            # image = cv2.rectangle(image, start_point, end_point, color, thickness)
            # cv2.putText(image, f"{pred['tagName']} ({position})", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # print(f"{pred['tagName']} ({position})")
            
            result = {"position":position}
            
            return jsonify(result)
            
if __name__=="__main__":
    app.run(debug=True)            