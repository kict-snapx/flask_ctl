# pip install python-dotenv 


from flask import Flask, request, render_template  
import google.generativeai as genai  
from PIL import Image  
import io  
import base64  
import os  # 환경 변수를 사용하기 위한 모듈  
from dotenv import load_dotenv  # 추가된 부분 

app = Flask(__name__)  

# .env 파일 로드  
load_dotenv()                   # 추가된 부분  

# Gemini API 키 설정  
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  

if not GOOGLE_API_KEY:  
    raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되어 있지 않습니다.")  

genai.configure(api_key=GOOGLE_API_KEY)  

# Gemini 1.5 Flash 모델 설정  
model = genai.GenerativeModel('gemini-1.5-pro')  

def get_gemini_response(prompt, image):  
    buffered = io.BytesIO()  
    image.save(buffered, format='PNG')  
    image_base64 = base64.b64encode(buffered.getvalue()).decode()  
    image_blob = {'mime_type': 'image/png', 'data': image_base64}  
    
    response = model.generate_content([prompt, image_blob])  
    return response.text  

@app.route('/', methods=['GET', 'POST'])  
def index():  
    if request.method == 'POST':  
        file = request.files['file']  
        if file:  
            image = Image.open(file.stream)  
            input_prompt = "Based on this image of a liquor bottle, suggest 3 cocktails that can be made with this spirit. Provide the names and recipes for each cocktail."  
            response = get_gemini_response(input_prompt, image)  
            cocktails = response.split('\n\n')  # 각 칵테일과 레시피가 두 개의 개행으로 구분된다고 가정  
            return render_template('result.html', cocktails=cocktails)  
    return render_template('index.html')  

if __name__ == '__main__':  
    app.run(debug=True)