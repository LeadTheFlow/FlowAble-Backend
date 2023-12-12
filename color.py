from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
import matplotlib.pyplot as plt
from flask_cors import CORS
from kneed import KneeLocator  
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def detect_menstrual_blood(image, red_threshold=100):
    # 이미지를 NumPy 배열로 변환
    image = np.array(image)

    # 이미지를 1차원 배열로 변환
    pixels = image.reshape((-1, 3))

    # Elbow method
    distortions = []
    max_k = 10  # 최대 클러스터 수
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(pixels)
        distortions.append(kmeans.inertia_)

    # Elbow method 그래프
    plt.plot(range(1, max_k + 1), distortions, marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel('Distortion')
    plt.title('Elbow Method for Optimal k')

    # kneed 라이브러리를 사용하여 엘보우 포인트 찾기
    kn = KneeLocator(range(1, max_k + 1), distortions, curve='convex', direction='decreasing')
    optimal_k = kn.knee

    # 최적 k값을 출력
    print(f"자동 생성 k값 (k): {optimal_k}")

    # K-means 클러스터링을 사용하여 색상을 그룹화
    kmeans = KMeans(n_clusters=optimal_k)
    kmeans.fit(pixels)

    # 클러스터 중심
    colors = kmeans.cluster_centers_.astype(int)

    # 대표 색상 팔레트
    palette = colors.tolist()

    # RGB 값을 반환
    rgb_values = [tuple(color) for color in colors]

    # 붉은 계열 색깔 필터링
    red_colors = [color for color in rgb_values if color[0] > red_threshold and color[1] < red_threshold and
                  color[2] < red_threshold]

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
                "message": "월경혈 감지. 월경이 시작한 것 같습니다. 달력에 기록할까요?" if is_menstrual else "월경혈이 감지되지 않습니다. 월경중이 아닌 것 같습니다.",
                "isColor": "true" if is_menstrual else "false"
            }

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
