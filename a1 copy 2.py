import io
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash
import google.generativeai as genai
import base64
import pdfplumber


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


model = genai.GenerativeModel('models/gemini-pro-vision')

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
 
"""

input_prompt2 = """
You are an Technical Human Resource Manager with expertise in data science, 
your role is to scrutinize the resume in light of the job description provided. 
Share your insights on the candidate's suitability for the role from an HR perspective. 
Additionally, offer advice on enhancing the candidate's skills and identify areas where improvement is needed.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. As a Human Resource manager,
 assess the compatibility of the resume with the role. Give me what are the keywords that are missing
 Also, provide recommendations for enhancing the candidate's skills and identify which areas require further development.
"""

input_prompt4 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Define the path to save the uploaded PDF file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        
        # Save the uploaded PDF file
        uploaded_file.save(filepath)
        
        # Open the PDF file
        with pdfplumber.open(filepath) as pdf:
            # Check if the PDF has at least one page
            if len(pdf.pages) < 1:
                raise ValueError("The PDF file has no pages.")
            
            # Convert the first page to an image
            first_page = pdf.pages[0]
            first_page_image = first_page.to_image(resolution=200).original
            
            # Convert the image mode to RGB
            first_page_image = first_page_image.convert("RGB")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'page-1.jpg')
            first_page_image.save(image_path, format="JPEG")
            
            # Open the saved image file and read it as binary
            with open(image_path, "rb") as image_file:
                img_byte_arr = image_file.read()
            
            # Encode the image to base64
            pdf_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }]
            
            # Save PDF file to MongoDB
            with open(filepath, "rb") as file:
                encoded_pdf = base64.b64encode(file.read()).decode()
                pdf_data = {
                    "filename": uploaded_file.filename,
                    "filedata": encoded_pdf
                }
                pdf_id = pdf_collection.insert_one(pdf_data).inserted_id
            
            return pdf_parts, pdf_id
    else:
        raise FileNotFoundError("No file uploaded")

@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    if request.method == 'POST':
        input_text = request.form['job_description']
        uploaded_file = request.files['resume']
        action = request.form['action']

        if uploaded_file:
            pdf_content, pdf_id = input_pdf_setup(uploaded_file)
            if action == 'tell_me':
                prompt = input_prompt1
            elif action == 'improvise':
                prompt = input_prompt2
            elif action == 'keywords':
                prompt = input_prompt3
            elif action == 'percentage':
                prompt = input_prompt4
            elif action == 'query':
                prompt = request.form['query']
            else:
                flash('Invalid action selected', 'error')
                return redirect(url_for('index'))

            response = get_gemini_response(input_text, pdf_content, prompt)
            # You can also store the response in MongoDB if needed
            flash(f"Successfully retrieved response", 'success')
            flash(f"Response: {response}", 'success')
        else:
            flash('Please upload a PDF file to proceed.', 'error')

    return render_template('index.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
