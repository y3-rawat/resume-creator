from flask import Flask, request, render_template, redirect, url_for, flash
from langchain_community.document_loaders import PyPDFLoader
from github import Github, InputGitAuthor
import os
import json
import base64
import time
import apis as a

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key")

# Vercel uses /tmp for writable storage
UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_file_to_github(file_path, token, repo, max_retries=3, retry_delay=5):
    g = Github(token)
    repository = g.get_repo(repo)
    author = InputGitAuthor(
        os.environ.get("GITHUB_AUTHOR_NAME", "Your Name"),
        os.environ.get("GITHUB_AUTHOR_EMAIL", "your_email@example.com")
    )

    with open(file_path, 'rb') as file:
        content = base64.b64encode(file.read()).decode('utf-8')

    file_name = os.path.basename(file_path)

    for _ in range(max_retries):
        try:
            try:
                contents = repository.get_contents(file_name)
                repository.update_file(contents.path, "Update file", content, contents.sha, author=author)
            except:
                repository.create_file(file_name, "Create file", content, author=author)
            return True
        except Exception as e:
            print(f"Error uploading to GitHub: {str(e)}")
            time.sleep(retry_delay)
    
    return False

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(filepath)
        
        success = upload_file_to_github(
            file_path=filepath,
            token=os.environ.get('GITHUB_TOKEN'),
            repo='company2candidate/Resume_data',
            max_retries=3,
            retry_delay=5
        )
        
        if success:
            print(f"Successfully uploaded {uploaded_file.filename} to GitHub")
        else:
            print(f"Failed to upload {uploaded_file.filename} to GitHub after retries")
        
        loader = PyPDFLoader(file_path=filepath)
        pages = loader.load_and_split()
        if len(pages) < 1:
            raise ValueError("The PDF file has no pages.")
        text = " ".join(list(map(lambda page: page.page_content, pages)))
        
        return text, filepath
    else:
        raise FileNotFoundError("No file uploaded")

def get_response(job_desc, pdf_content, filepath, prompt):
    pmp = f"""{prompt} 
    job description 
    --------
        {job_desc} 
    --------
    User's Resume Information
    {pdf_content} 
    """
    txt = a.final(pmp)
    return txt

def oth(text):
    return f"""
    I have a specific query that requires expert assistance, and you have to make a prompt in which you have the experience and skills necessary to address it effectively. Below is the query:

    {text}

    I am seeking a solution that is not only theoretically sound but also practical and actionable. Given your expertise in solving similar queries, I would appreciate it if you could provide a comprehensive response, including any necessary steps, resources, or considerations to ensure the solution works effectively in a real-world scenario.
    """

input_prompts = {
    'tell_me': """
    You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role. 
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """,
    'improvise': """
    You are a Technical Human Resource Manager with expertise in data science, 
    your role is to scrutinize the resume in light of the job description provided. 
    Share your insights on the candidate's suitability for the role from an HR perspective. 
    Additionally, offer advice on enhancing the candidate's skills and identify areas where improvement is needed.
    """,
    'keywords': """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
    your task is to evaluate the resume against the provided job description. As a Human Resource manager,
    assess the compatibility of the resume with the role. Give me what are the keywords that are missing
    Also, provide recommendations for enhancing the candidate's skills and identify which areas require further development.
    """,
    'percentage': """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
    your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
    the job description. First the output should come as percentage and then keywords missing and last final thoughts.
    """
}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        job_desc = request.form['job_description']
        uploaded_file = request.files['resume']
        action = request.form['action']

        if uploaded_file:
            try:
                pdf_content, filepath = input_pdf_setup(uploaded_file)
                if action in input_prompts:
                    prompt = input_prompts[action]
                elif action == 'query':
                    prompt = oth(request.form['query'])
                else:
                    flash('Invalid action selected', 'error')
                    return redirect(url_for('index'))
                
                response = get_response(job_desc, pdf_content, filepath, prompt)
                return redirect(url_for('result', response=response))
            except Exception as e:
                flash(f"Error processing file: {str(e)}", 'error')
        else:
            flash('Please upload a PDF file to proceed.', 'error')
    return redirect(url_for('index'))

@app.route('/result')
def result():
    response = request.args.get('response')
    return render_template('result.html', response=response)

# For local development
if __name__ == '__main__':
    app.run(debug=True)

# For Vercel
from vercel_app import app