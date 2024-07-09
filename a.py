from github import Github
import base64
def upload_git(file_path):
    
    token = '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'
    g = Github(token)

    import numpy as np
    # Step 2: Define repository and file details
    repo_name = "y3-rawat/Resumes"

    upload_path = f'PDFs/{np.random.randint(90000000)}__{file_path}'
    commit_message = 'Upload PDF file'

    # Step 3: Read the PDF file and encode it in Base64
    with open(file_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

    # Step 4: Get the repository
    repo = g.get_repo(repo_name)

    # Step 5: Check if the file already exists
    try:
        contents = repo.get_contents(upload_path)
        # If the file exists, update it
        repo.update_file(contents.path, commit_message, pdf_base64, contents.sha, branch="main")
        print('File updated successfully')
    except:
        
        # If the file does not exist, create it
        repo.create_file(upload_path, commit_message, pdf_base64, branch="main")
        print('File uploaded successfully')
upload_git("Yash_Rawat-Resume.pdf")