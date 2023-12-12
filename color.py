from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*":{"origins":"*"}})
def detect_menstrual_blood(image, k=3, red_threshold=100):
    # 이미지를 NumPy 배열로 변환합니다.
    image = np.array(image)

    # 이미지를 1차원 배열로 변환합니다.
    pixels = image.reshape((-1, 3))
    
    # K-means 클러스터링을 사용하여 색상을 그룹화합니다.
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)

    # 클러스터 중심을 얻어옵니다.
    colors = kmeans.cluster_centers_.astype(int)

    # 대표 색상 팔레트를 반환합니다.
    palette = colors.tolist()

    # RGB 값을 반환합니다.
    rgb_values = [tuple(color) for color in colors]

    # 붉은 계열 색깔 필터링
    red_colors = [color for color in rgb_values if color[0] > red_threshold and color[1] < red_threshold and color[2] < red_threshold]

    if red_colors:
        return True
    else:
        return False

@app.route("/api/color", methods=["GET", "POST"])
def index():
    data = None

    if request.method == "POST":
        # POST 요청에서 이미지 파일 받기
        uploaded_file = request.files["file"]

        if uploaded_file.filename != "":
            # 이미지 분석 및 결과 확인
            image = Image.open(uploaded_file)
            is_menstrual = detect_menstrual_blood(image)

            # 결과에 따라 메시지 설정
            data = {
                "message": "월경혈 감지. 월경이 시작한 것 같습니다. 달력에 기록할까요?" if is_menstrual else "월경혈이 감지되지 않습니다. 월경중이 아닌 것 같습니다."
            }

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)