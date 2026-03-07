import requests
import json
import os
import base64

class GithubFetcher:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            
    def fetch_repo_metadata(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
        
    def fetch_readme(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 404:
            return ""
        response.raise_for_status()
        data = response.json()
        if 'content' in data:
            return base64.b64decode(data['content']).decode('utf-8')
        return ""

    def fetch_file_tree(self, owner, repo, default_branch):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=0"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json().get("tree", [])

    def fetch_all(self, owner, repo):
        print(f"Fetching data for {owner}/{repo}...")
        metadata = self.fetch_repo_metadata(owner, repo)
        readme = self.fetch_readme(owner, repo)
        default_branch = metadata.get("default_branch", "main")
        tree = self.fetch_file_tree(owner, repo, default_branch)
        
        # Determine dependency files
        files = [item['path'] for item in tree if item['type'] == 'blob']
        dependency_files_found = [f for f in files if f in ['requirements.txt', 'package.json', 'pyproject.toml', 'Cargo.toml']]

        return {
            "owner": owner,
            "name": repo,
            "metadata": metadata,
            "readme": readme,
            "tree": tree,
            "dependency_files_found": dependency_files_found
        }

if __name__ == "__main__":
    fetcher = GithubFetcher()
    data = fetcher.fetch_all("langchain-ai", "langchain")
    print(f"Fetched {data['metadata']['name']}. Stars: {data['metadata']['stargazers_count']}")
