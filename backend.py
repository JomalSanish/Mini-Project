from flask import Flask, request, jsonify # backend to frontend connectivity
from flask_cors import CORS
from pymongo import MongoClient #mongodb
from google import genai  # Gemini AI
import PyPDF2  # for parsing pdf
from docx import Document  # for parsing document format
from datetime import datetime # current time

app = Flask(__name__)
CORS(app)

# Connect to MongoDB Cluster
mongo_client = MongoClient("mongodb+srv://22cs029:mits123@primarycluster.eu4op.mongodb.net/?retryWrites=true&w=majority&appName=PrimaryCluster")
db = mongo_client.get_database("HealthMonitor")
users_collection = db.get_collection("users")
reports_collection = db.get_collection("reports")

# Initialize the Gemini AI client
client = genai.Client(api_key="AIzaSyCygULILuxUr_lPWYxXY2mFqcOQnpWeuyU")

def extract_text_from_file(file):
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = '\n'.join([page.extract_text() for page in pdf_reader.pages])
        return text
    elif file.filename.endswith(('.doc', '.docx')):
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file.filename.endswith('.txt'):
        return file.read().decode('utf-8')
    return None

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"success": False, "error": "User already exists"}), 400

    users_collection.insert_one({"email": email, "password": password})
    return jsonify({"success": True}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    user = users_collection.find_one({"email": email})
    if user and user.get("password") == password:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        text_input = request.form.get('text')
        file = request.files.get('file')
        email = request.form.get('email') 

        input_text = text_input or ''
        if file:
            extracted_text = extract_text_from_file(file)
            input_text += '\n' + (extracted_text if extracted_text else '')

        prompt = f"""Analyze these medical inputs and provide:
Don't use numbers or asterisks; keep the response short.
1. Possible diseases (list top 3 with likelihood percentage)
2. Urgency level (low/medium/high)
3. Whether to consult a doctor (yes/no)
4. Recommended specialist type
5. Brief explanation
6. Keep the result as if it's coming from a medical practitioner
7. Do not use numbers or asterisks
8. Give a disclaimer that this is ai generated and to approach a doctor for detailed analysis

Medical Inputs:
{input_text}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d %H:%M:%S")
        header = f"Report generated on {current_date}\n"
        full_report = header + response.text

        reports_collection.insert_one({
            "report": full_report,
            "generated_at": now,
            "email": email
        })

        return jsonify({
            'success': True,
            'analysis': full_report
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/history', methods=['GET'])
def history():
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400

        reports = list(reports_collection.find({"email": email}).sort("generated_at", -1))
        for r in reports:
            r["_id"] = str(r["_id"]) 
            r["generated_at"] = r["generated_at"].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"success": True, "reports": reports}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
