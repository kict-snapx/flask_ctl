from flask import Flask, request, render_template  
import google.generativeai as genai  
from PIL import Image  
import io  
import base64  

app = Flask(__name__)  

# Gemini API 키 설정  
GOOGLE_API_KEY = "AIzaSyBrPXiZuak5z6EPISW1xOCLPCQHrKwEqZE"  
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
            cocktails = response.split('\n\n')  # Assuming each cocktail and its recipe are separated by double newlines  
            return render_template('result.html', cocktails=cocktails)  
    return render_template('index.html')  

if __name__ == '__main__':  
    app.run(debug=True)