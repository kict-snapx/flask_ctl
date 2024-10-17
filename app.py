from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# OpenAI API 키 설정
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image):
    base64_image = encode_image(image)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지에 있는 술병들을 분석해주세요. 각 술의 이름과 종류를 알려주세요."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def recommend_cocktails(spirit):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 전문 바텐더입니다. 주어진 술을 사용하여 만들 수 있는 칵테일을 추천해주세요."},
            {"role": "user", "content": f"다음 술을 사용하여 만들 수 있는 칵테일 3가지를 추천해주세요: {spirit}. 각 칵테일에 대해 이름과 간단한 설명 그리고 레시피를 제공해주세요. 각 칵테일 추천을 '###'로 구분해주세요."}
        ],
        max_tokens=700
    )
    
    cocktails = response.choices[0].message.content.split('###')
    formatted_cocktails = "\n\n".join(cocktail.strip() for cocktail in cocktails if cocktail.strip())
    
    return formatted_cocktails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400
    
    if file:
        file_data = file.read()
        base64_image = base64.b64encode(file_data).decode('utf-8')
        file.seek(0)  # 파일 포인터를 처음으로 되돌림
        spirits = analyze_image(file)
        return jsonify({
            'spirits': spirits,
            'image': base64_image
        })

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    spirit = data.get('spirit')
    
    if not spirit:
        return jsonify({'error': '선택된 술이 없습니다.'}), 400
    
    cocktails = recommend_cocktails(spirit)
    return jsonify({'cocktails': cocktails})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)