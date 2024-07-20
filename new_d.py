import requests
import json
import base64

def upload_text_to_github(new_content, token, repo, file_path='Res_d.txt', branch='main', commit_message='Append new text content'):
    # Prepare headers
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Prepare API endpoint
    url = f'https://api.github.com/repos/{repo}/contents/{file_path}'

    # Step 1: Fetch the existing file content
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        existing_file = response.json()
        existing_content_base64 = existing_file['content']
        existing_content = base64.b64decode(existing_content_base64).decode('utf-8')
        sha = existing_file['sha']
    elif response.status_code == 404:
        # File doesn't exist, start with empty content
        existing_content = ""
        sha = None
    else:
        print(f'Failed to fetch file {file_path}. Status code: {response.status_code}')
        print(f'Response: {response.text}')
        return False

    # Step 2: Append the new text content to the existing content
    combined_content = existing_content + ',\n' + new_content if existing_content else new_content

    # Step 3: Encode the combined content to Base64
    encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')

    # Prepare JSON payload
    payload = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch,
    }
    if sha:
        payload['sha'] = sha

    # Make PUT request to create or update the file
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f'File {file_path} successfully updated in {repo}!')
        return True
    else:
        print(f'Failed to update file {file_path}. Status code: {response.status_code}')
        print(f'Response: {response.text}')
        return False