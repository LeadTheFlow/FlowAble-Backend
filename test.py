import requests

# Flask 서버의 URL
url = "http://127.0.0.1:5000/api/OCR_result"

# 테스트할 이미지 파일의 이름 (현재 디렉토리에 위치해야 함)
image_path = 'elice.jpeg'

# API 엔드포인트에 GET 요청을 보냄
response = requests.get(url, params={'path': image_path})

# JSON 응답을 파싱하고 출력
data = response.json()
print(data)