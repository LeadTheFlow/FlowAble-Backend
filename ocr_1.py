'''
실행 명령어
* Running on http://127.0.0.1:5000

flask url = "http://127.0.0.1:5000/api/OCR_result"
response = requests.get(url, params={'path': image_path})

'''

import os
import json
import base64
import requests
import string
from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS

BlueprintOCR = Blueprint('/api/OCR', __name__)
CORS(BlueprintOCR, resources={r"/api/*":{"origins":"*"}})

@BlueprintOCR.route("/api/OCR", methods=['GET'])
def OCR_result():

  #요청에서 이미지 파일 경로 추출
  image_path = request.args.get('path')

  if not image_path or not os.path.exists(image_path):
    return jsonify({"error": "File not exists or path not provided"})

  #민지님 key로 바꿈
  URL = "https://289x53pm3g.apigw.ntruss.com/custom/v1/26842/c927448b0a02c01ba659d0339776a7971c45256d5406bf1a8ec2aaee0ba591fd/general"
    
  # 본인의 Secret Key로 치환
  KEY = "RFl5cE9XVmV6bUhOSkhZaE9JT0VLV3ZKZFp4d0N0QnE="

  headers = {
      "Content-Type": "application/json",
      "X-OCR-SECRET": KEY
  }

  with open(image_path, "rb") as f:
    img = base64.b64encode(f.read()).decode('utf-8')

  payload = {
              "version": "V1",
              "requestId": "sample_id", # 요청을 구분하기 위한 ID, 사용자가 정의
              "timestamp": 0, # 현재 시간값
              "images": [
                  {
                      "name": "sample_image",
                      "format": "jpeg",
                      "data": img
                  }
              ]
          }
          
  response = requests.post(URL, data=json.dumps(payload), headers=headers)
  res = json.loads(response.text)

  texts = []

  if 'images' in res and 'fields' in res['images'][0]:
    for i in range(len(res['images'][0]['fields'])):
        texts.append(res['images'][0]['fields'][i]['inferText'])

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
    
  result = {"brand":brand, "size":size}

  return jsonify(result), 200, {'Content-Type': 'application/json; charset=utf-8'}

app = Flask(__name__)
app.register_blueprint(BlueprintOCR, url_prefix='/api/OCR')

if __name__ == "__main__":
  app.run(debug=True)