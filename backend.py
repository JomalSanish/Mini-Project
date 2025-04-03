from flask import Flask, request, jsonify #connecting to front end
from flask_cors import CORS
from google import genai #gemini
import PyPDF2 #for parsing pdf
from docx import Document #for parsing document format


app = Flask(__name__)
CORS(app)
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

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        text_input = request.form.get('text')
        file = request.files.get('file')
        
        input_text = text_input or ''
        if file:
            input_text += '\n' + extract_text_from_file(file)

        prompt = f"""Analyze these medical inputs and provide:
        1. Possible diseases (list top 3 with likelihood percentage)
        2. Urgency level (low/medium/high)
        3. Whether to consult a doctor (yes/no)
        4. Recommended specialist type
        5. Brief explanation
        6. Keep the result as if its comming from a medical practitioner
        7. Dont't use asterics or numbers, keep the response short

        Medical Inputs:
        {input_text}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return jsonify({
            'success': True,
            'analysis': response.text
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)