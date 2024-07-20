import json
import requests
import base64

from github import Github, InputGitAuthor

github = "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"
g = Github(github)
repo = g.get_repo("company2candidate/Resume_data")

def repository():
    repo = g.get_repo("company2candidate/Resume_data")
    return repo

branch = 'main'

def update_file(new_content, fpth):
    try:
        print("under database")
        file_content = repo.get_contents(fpth, ref=branch)
        decoded_content = base64.b64decode(file_content.content).decode('utf-8')
        # existing_content = json.loads(decoded_content)

        # # Ensure new_content is a dictionary
        # if isinstance(new_content, str):
        #     new_content = json.loads(new_content)

        # Update the existing content with new content
        # existing_content.update(new_content)
        
        new_content_str = json.dumps(existing_content, indent=4)  # Convert the dictionary to a formatted string
        repo.update_file(fpth, "COMMIT_MESSAGE", new_content)
        print("File updated successfully!")

    except github.GithubException as e:
        if e.status == 404:
            # File does not exist, create it
            new_content_str = json.dumps(new_content, indent=4)
            repo.create_file(fpth, "COMMIT_MESSAGE", new_content_str)
            print("File created successfully!")
        else:
            print("Error updating file:", e)
    except Exception as e:
        print("Unexpected error:", e)

def get_file(path):
    try:
        file_content = repo.get_contents(path, ref=branch)
        decoded_content = base64.b64decode(file_content.content).decode('utf-8')
        return decoded_content
    except Exception as e:
        print("Error getting file:", e)
        return None

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

def list_files_in_directory(path, branch):
    try:
        contents = repo.get_contents(path, ref=branch)
        files = []
        final_file = []
        
        for content in contents:
            if content.type == 'file':
                files.append(content.path)
            elif content.type == 'dir':
                files += list_files_in_directory(content.path, branch)
        for i in files:
            final_file.append(i.split("/")[1])
        return final_file
    except Exception as e:
        print("Error listing files:", e)
        return []
