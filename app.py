import requests
import base64
import time
from requests.exceptions import RequestException


from langchain_community.document_loaders import PyPDFLoader
import os
from flask import Flask, request, render_template, redirect, url_for, flash
import apis as a
import json





def oth(text):
    other_prompt = f"""
    I have a specific query that requires expert assistance, and you have to make a prompt in which you have the experience and skills necessary to address it effectively. Below is the query:

    {text}

    I am seeking a solution that is not only theoretically sound but also practical and actionable. Given your expertise in solving similar queries, I would appreciate it if you could provide a comprehensive response, including any necessary steps, resources, or considerations to ensure the solution works effectively in a real-world scenario.
    """
    return other_prompt

app = Flask(__name__)
app.secret_key = "none"
app.config['UPLOAD_FOLDER'] = '/tmp'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
 assess the compatibility of the resume with the role. Give me what are the keywords that are missing
 Also, provide recommendations for enhancing the candidate's skills and identify which areas require further development.
"""

input_prompt4 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

def get_response(job_desc, pdf_content,filepath, prompt,api):
    pmp = f"""{prompt} 
    job description 
    --------
        {job_desc} 
    --------
    User's Resume Information
    {pdf_content} 
    """
    txt = a.final(pmp,api)
    
    return txt


@app.errorhandler(504)  # HTTP Status Code for Request Timeout
def handle_timeout(error):
    app.logger.error(f"504 error: {error}")
    return render_template('504.html'), 504


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(filepath)
        loader = PyPDFLoader(file_path=filepath)
        pages = loader.load_and_split()
        if len(pages) > 3:
            flash("Please enter the Resume which should less then 3 pages.")
        text = " ".join(list(map(lambda page: page.page_content, pages)))
        return text, filepath
    else:
        raise FileNotFoundError("No file uploaded")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/analyze', methods=['POST'])
def analyze():
    response = None
    if request.method == 'POST':
        job_desc = request.form['job_description']
        uploaded_file = request.files['resume']
        action = request.form['action']
        api = request.form['groq-api']
        

        if uploaded_file:
            try:
                pdf_content, filepath = input_pdf_setup(uploaded_file)
                if action == 'tell_me':
                    prompt = input_prompt1
                elif action == 'improvise':
                    prompt = input_prompt2
                elif action == 'keywords':
                    prompt = input_prompt3
                elif action == 'percentage':
                    prompt = input_prompt4
                elif action == 'query':
                    query_text = request.form['query']
                    prompt = oth(query_text)
                else:
                    flash('Invalid action selected', 'error')
                    return redirect(url_for('index'))
                
                response = get_response(job_desc, pdf_content, filepath,prompt,api)
                
                # Start a new thread to write users in the background
                
                
                return redirect(url_for('result', response=response))
                
            except Exception as e:
                flash(f"Error processing file: {e}", 'error')
        else:
            flash('Please upload a PDF file to proceed.', 'error')
    return redirect(url_for('index'))

@app.route('/result')
def result():
    response = request.args.get('response')
    print(response, "  response ")
    return render_template('result.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
