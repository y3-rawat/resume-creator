import json
import requests
import json
import base64

from github import Github, InputGitAuthor
github="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"
g = Github(github)
repo = g.get_repo("company2candidate/Resume_data")

def repository():
    repo = g.get_repo("company2candidate/Resume_data")
    return repo

import base64
branch = 'main'
def update_file(new_content, fpth):
    try:
        print("under databse")
        file_content = repo.get_contents(fpth, ref=branch)
        decoded_content = base64.b64decode(file_content.content).decode('utf-8')
        c = json.loads(decoded_content)
        c.update(new_content)
        print("updateing file")
        new_content_str = json.dumps(c)  # Convert the dictionary to a string
        repo.update_file(fpth, "COMMIT_MESSAGE", new_content_str, file_content.sha)
        print("File updated successfully!")

    except github.GithubException as e:
        if e.status == 404:
            # File does not exist, create it
            new_content_str = json.dumps(new_content)
            repo.create_file(fpth, "COMMIT_MESSAGE", new_content_str)
            print("File created successfully!")
        else:
            print("Error updating file:", e)



def get_file(path):

    file_content = repo.get_contents(path, ref=branch)
    decoded_content = base64.b64decode(file_content.content).decode('utf-8')
    
    return decoded_content

def rename_file(old_path, new_path):
    try:
        # Get the file content and SHA
        file_content = repo.get_contents(old_path, ref=branch)
        decoded_content = base64.b64decode(file_content.content).decode('utf-8')

        # Create a new file with the desired name
        repo.create_file(new_path, f"Renaming file to {new_path}", decoded_content, branch=branch)
        
        # Delete the old file
        repo.delete_file(old_path, f"Deleting old file {old_path}", file_content.sha, branch=branch)

        print("File renamed successfully!")
    except Exception as e:
        print("Error renaming file:", e)

    
def list_files_in_directory( path, branch):
    try:
        contents = repo.get_contents(path, ref=branch)
        files = []
        final_file = []
        
        for content in contents:
            if content.type == 'file':
                files.append(content.path)
            elif content.type == 'dir':
                files += list_files_in_directory(repo, content.path, branch)
        for i in files:
            final_file.append(i.split("/")[1])
        return final_file
    except Exception as e:
        print("Error listing files:", e)
        return []

# List files in the specified directory
