import os
import json
import re
import base64
import io
from flask import Flask, render_template, request
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

app = Flask(__name__)

# Config
GEN_AI_KEY = os.getenv("GEMINI_API_KEY")
if GEN_AI_KEY:
    genai.configure(api_key=GEN_AI_KEY)

def get_gemini_response(image):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = """
        Analyze this food image and return a JSON with:
        {
            "food_name": "Food Name",
            "nutrition": {
                "calories": "kcal",
                "protein": "g",
                "carbs": "g",
                "fat": "g",
                "fiber": "g",
                "vitamins": "summary",
                "minerals": "summary"
            },
            "healthiness": "healthy" or "unhealthy", 
            "reasoning": "Quick explanation",
            "recommendations": [
                {
                    "name": "Alternative Name",
                    "calories": "kcal",
                    "description": "Why it is better"
                }
            ]
        }
        """
        
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def calculate_daily_needs(profile):
    try:
        weight = float(profile.get('weight', 70))
        height = float(profile.get('height', 170))
        age = int(profile.get('age', 25))
        gender = profile.get('gender', 'male').lower()
        activity = profile.get('activity', 'moderate').lower()

        # Mifflin-St Jeor
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        return int(bmr * multipliers.get(activity, 1.55))
    except:
        return 2000

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return render_template('index.html', error="No file uploaded")
    
    file = request.files['file']
    if not file or file.filename == '':
        return render_template('index.html', error="No file selected")
        
    try:
        image_data = file.read()
        image_parts = Image.open(io.BytesIO(image_data))
        
        # Optional: daily needs
        tdee = None
        percentage = None
        
        if request.form.get('calculate_needs') == 'true':
            tdee = calculate_daily_needs(request.form)
        
        result = get_gemini_response(image_parts)
        
        if not result:
            return render_template('index.html', error="Analysis failed. check API key.")
            
        if tdee and result.get('nutrition'):
            try:
                cal_str = str(result['nutrition'].get('calories', '0'))
                cal_match = re.search(r'\d+', cal_str)
                if cal_match:
                    cals = int(cal_match.group())
                    percentage = round((cals / tdee) * 100, 1)
            except:
                pass

        img_b64 = base64.b64encode(image_data).decode('utf-8')
        
        return render_template('result.html', 
                               result=result, 
                               image_data=img_b64,
                               tdee=tdee,
                               percentage_of_needs=percentage)
                               
    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=False)

