import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import magic
from langchain_community.document_loaders import PyPDFLoader
import apis as a

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

# Prompts
pdf_prompt = """
You have to find these things from the resume:
Basic Information, Full Name, Contact Information, Phone Number, Email Address, Address (if available),
LinkedIn Profile (if available), Personal Website or Portfolio (if available), Professional Summary or Objective,
Education, Work Experience, Skills, Projects, Awards and Honors, Professional Development, Publications and Research,
Professional Affiliations, Languages, References, Additional Sections
"""

input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are a Technical Human Resource Manager with expertise in data science,
your role is to scrutinize the resume in light of the job description provided.
Share your insights on the candidate's suitability for the role from an HR perspective.
Additionally, offer advice on enhancing the candidate's skills and identify areas where improvement is needed.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality,
your task is to evaluate the resume against the provided job description. As a Human Resource manager,
assess the compatibility of the resume with the role. Give me what are the keywords that are missing.
Also, provide recommendations for enhancing the candidate's skills and identify which areas require further development.
"""

input_prompt4 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality,
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_pdf(file_stream):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_stream.read(1024))
    file_stream.seek(0)  # Reset file pointer
    return mime_type == 'application/pdf'

def oth(text):
    return f"""
    I have a specific query that requires expert assistance, and you have to make a prompt in which you have the experience and skills necessary to address it effectively. Below is the query:

    {text}

    I am seeking a solution that is not only theoretically sound but also practical and actionable. Given your expertise in solving similar queries, I would appreciate it if you could provide a comprehensive response, including any necessary steps, resources, or considerations to ensure the solution works effectively in a real-world scenario.
    """

def get_response(job_desc, pdf_content, prompt):
    pmp = f"""{prompt} 
job description 
--------
     {job_desc} 
--------
User's Resume Information
{pdf_content} 
"""
    return a.final(pmp)

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
        uploaded_file.save(filepath)
        loader = PyPDFLoader(file_path=filepath)
        pages = loader.load_and_split()
        if len(pages) < 1:
            raise ValueError("The PDF file has no pages.")
        text = " ".join(list(map(lambda page: page.page_content, pages)))
        content = f"{pdf_prompt} here is the content of resume {text}"
        return a.final(content)
    else:
        raise FileNotFoundError("No file uploaded")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Please upload a file smaller than 16 MB.', 'error')
    return redirect(url_for('index')), 413

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if request.method == 'POST':
            job_desc = request.form['job_description']
            uploaded_file = request.files['resume']
            action = request.form['action']

            if not job_desc.strip():
                raise ValueError("Job description is empty")

            if not uploaded_file:
                raise FileNotFoundError("No file uploaded")

            if not allowed_file(uploaded_file.filename) or not is_pdf(uploaded_file):
                raise ValueError("Invalid file type. Please upload a PDF.")

            pdf_content = input_pdf_setup(uploaded_file)
            
            if action == 'tell_me':
                prompt = input_prompt1
            elif action == 'improvise':
                prompt = input_prompt2
            elif action == 'keywords':
                prompt = input_prompt3
            elif action == 'percentage':
                prompt = input_prompt4
            elif action == 'query':
                prompt = oth(request.form['query'])
            else:
                raise ValueError('Invalid action selected')

            response = get_response(job_desc, pdf_content, prompt)
            return redirect(url_for('result', response=response))

    except ValueError as ve:
        flash(str(ve), 'error')
    except FileNotFoundError as fnf:
        flash(str(fnf), 'error')
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'error')
        app.logger.error(f"Unexpected error in analyze route: {str(e)}")

    return redirect(url_for('index'))

@app.route('/result')
def result():
    response = request.args.get('response')
    return render_template('result.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)