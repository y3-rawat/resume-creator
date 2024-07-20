import requests
import json
import base64
token = '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'
repo = 'company2candidate/Resume_data'

# Optionally, specify branch and commit message
branch_name = 'main'
commit_msg = 'Append new text content'

def upload_text_to_github( new_content):
    print("calling from upload_text to github")
    file_path = 'Res_d.txt'
    # Prepare headers
    headers = {
        'Authorization': f'token {token}',
        'Content-Type': 'application/json'
    }

    # Prepare API endpoint
    url = f'https://api.github.com/repos/{repo}/contents/{file_path.lstrip("/")}'

    # Step 1: Fetch the existing file content
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        existing_file = response.json()
        existing_content_base64 = existing_file['content']
        existing_content = base64.b64decode(existing_content_base64).decode('utf-8')
    else:
        print(f'Failed to fetch file {file_path}. Status code: {response.status_code}')
        print(f'Response: {response.text}')
        return

    # Step 2: Append the new text content to the existing content
    combined_content = existing_content + ',\n' + new_content

    # Step 3: Encode the combined content to Base64
    encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')

    # Prepare JSON payload
    payload = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch,
        'sha': existing_file['sha']  # required to update the file
    }

    # Convert payload to JSON string
    payload_str = json.dumps(payload)

    # Make PUT request to update the file
    response = requests.put(url, headers=headers, data=payload_str)

    if response.status_code == 200:
        print(f'File {file_path} successfully updated in {repo}!')
    else:
        print(f'Failed to update file {file_path}. Status code: {response.status_code}')
        print(f'Response: {response.text}')




def upload_pdf_to_github( file_path, branch='main', commit_message='Upload PDF file'):
    # Prepare headers
    headers = {
        'Authorization': f'token {token}',
        'Content-Type': 'application/json'
    }

    # Prepare API endpoint
    url = f'https://api.github.com/repos/{repo}/contents/{file_path.lstrip("/")}'

    # Load PDF file content
    with open(file_path, 'rb') as file:
        pdf_content = file.read()

    # Encode file content to Base64
    encoded_content = base64.b64encode(pdf_content).decode('utf-8')

    # Prepare JSON payload
    payload = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch
    }

    # Convert payload to JSON string
    payload_str = json.dumps(payload)

    # Make PUT request to create new file
    response = requests.put(url, headers=headers, data=payload_str)

    if response.status_code == 201:
        print(f'File {file_path} successfully uploaded to {owner}/{repo}!')
    else:
        print(f'Failed to upload file {file_path}. Status code: {response.status_code}')
        print(f'Response: {response.text}')

