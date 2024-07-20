import requests
import base64
import time
from requests.exceptions import RequestException

def upload_text_to_github(new_content, token, repo, file_path='Res_d.txt', branch='main', commit_message='Append new text content', max_retries=3, retry_delay=5):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/repos/{repo}/contents/{file_path}'

    for attempt in range(max_retries):
        try:
            # Fetch existing content
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                existing_file = response.json()
                existing_content = base64.b64decode(existing_file['content']).decode('utf-8')
                sha = existing_file['sha']
            else:
                existing_content = ""
                sha = None

            # Append new content
            combined_content = existing_content + ',' + new_content if existing_content else new_content
            encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')

            # Prepare payload
            payload = {
                'message': commit_message,
                'content': encoded_content,
                'branch': branch,
            }
            if sha:
                payload['sha'] = sha

            # Upload content
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()

            print(f'File {file_path} successfully updated in {repo}!')
            return True

        except RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Upload failed.")
                return False

    return False


