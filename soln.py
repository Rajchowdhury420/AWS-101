import os
import json
import requests
from datetime import datetime

BITBUCKET_BASE_URL = 'https://api.bitbucket.org/2.0'
BITBUCKET_USERNAME = 'Simran'
BITBUCKET_APP_PASSWORD = '*********************'

def get_nested_accounts(folder_path):
    accounts = []
    for account_dir in os.listdir(folder_path):
        if os.path.isdir(os.path.join(folder_path, account_dir)):
            accounts.append(account_dir)
    return accounts

def create_pull_request(repo_slug, source_branch, destination_branch, title, description):
    url = f'{BITBUCKET_BASE_URL}/repositories/{BITBUCKET_USERNAME}/{repo_slug}/pullrequests'
    auth = (BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)
    data = {
        'title': 'Right sized policy PR',
        'description': 'Automated policy right-sizing update.',
        'source': {
            'branch': {
                'name': 'IAM-Development'
            }
        },
        'destination': {
            'branch': {
                'name': 'develop'
            }
        }
    }
    response = requests.post(url, json=data, auth=auth)
    response.raise_for_status()
    return response.json()['id']

def replace_json_policy(original_folder, right_sized_folder, repo_slug):
    nested_accounts = get_nested_accounts(right_sized_folder)
    counter = 1

    for account in nested_accounts:
        account_folder_path = os.path.join(original_folder, account)
        right_sized_account_folder_path = os.path.join(right_sized_folder, account)

        for role_file in os.listdir(right_sized_account_folder_path):
            role_name = os.path.splitext(role_file)[0]
            original_role_path = os.path.join(account_folder_path, f"{role_name}.json")
            right_sized_role_path = os.path.join(right_sized_account_folder_path, role_file)

            if os.path.isfile(original_role_path) and os.path.isfile(right_sized_role_path):
                # Read the original and right-sized JSON policies
                with open(original_role_path, 'r') as f:
                    original_policy = json.load(f)
                with open(right_sized_role_path, 'r') as f:
                    right_sized_policy = json.load(f)

                # Check if there are any differences between the two policies
                if original_policy != right_sized_policy:
                    # Replace the original JSON policy with the right-sized one
                    with open(original_role_path, 'w') as f:
                        json.dump(right_sized_policy, f, indent=2)

                    # Git workflow for the pull request
                    branch_name = f"rightsize_{account}_{role_name}_{counter}"
                    os.system(f"git checkout -b {branch_name}")
                    os.system("git add -u")
                    os.system(f'git commit -m "Change JSON policy for {role_name}"')
                    os.system(f"git push origin {branch_name}")

                    # Create a custom pull request
                    create_pull_request(repo_slug, branch_name, 'develop', 'Right-size policy update', 'Automated policy right-sizing update.')

                    # Increment the counter for the next pull request
                    counter += 1
                    break  # Create one pull request at a time

def main():
    original_folder_path = '/path/to/Original'
    right_sized_folder_path = '/path/to/RightSized'
    bitbucket_repo_slug = 'your-bitbucket-repo-slug'

    replace_json_policy(original_folder_path, right_sized_folder_path, bitbucket_repo_slug)

if __name__ == '__main__':
    main()
