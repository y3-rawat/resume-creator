import requests
import json
import base64

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

