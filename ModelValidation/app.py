from flask import Flask, render_template, request
import torch
from PIL import Image

app = Flask(__name__)

# 모델 적용 함수 정의
def load_yolov5_model():
    path_hubconfig = "C:/pythonProject5/labelingpage/yolov5"
    path_weight = "C:/pythonProject5/Age_Grade_best.pt"

    model = torch.hub.load(path_hubconfig, 'custom',
                           path=path_weight, source='local')
    return model

def process_image(image):
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit/', methods=['POST'])
def submit():
    # 사용자가 업로드한 이미지 가져오기
    image_file = request.files['image_files']
    if image_file:
        image = Image.open(image_file)

        # 모델 불러오기
        model = load_yolov5_model()

        # 이미지 처리
        processed_image = process_image(image)

        # 모델에 이미지 적용 (예측)
        with torch.no_grad():
            results = model(processed_image)

        # 결과를 웹 페이지에 전달하고 출력
        return render_template('result.html', results=results)

    return "이미지를 업로드해주세요."

if __name__ == '__main__':
    app.run(debug=True)