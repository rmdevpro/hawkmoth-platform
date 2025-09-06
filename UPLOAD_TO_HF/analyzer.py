# GitHub Repository Analyzer
import os
import re
import base64
import requests

class GitHubAnalyzer:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})

    def analyze_repo(self, repo_url: str) -> dict:
        try:
            owner, repo = self._parse_url(repo_url)
            repo_data = self._get_repo_data(owner, repo)
            files = self._get_key_files(owner, repo)
            
            tech_stack = self._detect_tech_stack(files, repo_data)
            deployment_type = self._get_deployment_type(tech_stack)
            complexity = self._assess_complexity(tech_stack, files)
            cost = self._estimate_cost(complexity, deployment_type)
            
            return {
                'name': repo_data['name'],
                'description': repo_data.get('description', 'No description'),
                'language': repo_data.get('language', 'Unknown'),
                'tech_stack': tech_stack,
                'deployment_type': deployment_type,
                'complexity': complexity,
                'estimated_cost': cost,
                'stars': repo_data.get('stargazers_count', 0),
                'repo_url': repo_url,
                'owner': owner
            }
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    def _parse_url(self, url):
        url = url.strip().rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        match = re.search(r'github\.com/([^/]+)/([^/\s?]+)', url)
        if not match:
            raise ValueError("Invalid GitHub URL")
        
        return match.groups()

    def _get_repo_data(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = self.session.get(url)
        if response.status_code == 404:
            raise Exception("Repository not found or private")
        response.raise_for_status()
        return response.json()

    def _get_key_files(self, owner, repo):
        files = {}
        key_filenames = ['package.json', 'requirements.txt', 'Dockerfile', 'app.py', 'main.py', 'streamlit_app.py']
        
        for filename in key_filenames:
            content = self._get_file_content(owner, repo, filename)
            if content:
                files[filename] = content[:1000]
        
        return files

    def _get_file_content(self, owner, repo, filepath):
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                content_data = response.json()
                content = content_data.get('content', '')
                return base64.b64decode(content).decode('utf-8', errors='ignore')
        except:
            pass
        return None

    def _detect_tech_stack(self, files, repo_data):
        stack = set()
        language = repo_data.get('language', '').lower()
        
        if language == 'python':
            stack.add('Python')
        elif language == 'javascript':
            stack.add('JavaScript')
        
        for filename, content in files.items():
            content_lower = content.lower()
            
            if filename == 'package.json':
                stack.add('Node.js')
                if 'react' in content_lower:
                    stack.add('React')
            elif filename == 'requirements.txt':
                if 'streamlit' in content_lower:
                    stack.add('Streamlit')
                if 'fastapi' in content_lower:
                    stack.add('FastAPI')
        
        return list(stack) if stack else ['Unknown']

    def _get_deployment_type(self, tech_stack):
        if 'Streamlit' in tech_stack:
            return 'Streamlit App'
        elif 'FastAPI' in tech_stack:
            return 'FastAPI Service'
        elif 'React' in tech_stack:
            return 'Static Site'
        return 'Generic App'

    def _assess_complexity(self, tech_stack, files):
        score = len(tech_stack) + len(files)
        if score <= 3:
            return 'Simple'
        elif score <= 7:
            return 'Moderate'
        return 'Complex'

    def _estimate_cost(self, complexity, deployment_type):
        base_costs = {
            'Streamlit App': 4.0,
            'FastAPI Service': 6.0,
            'Static Site': 2.0,
            'Generic App': 5.0
        }
        
        base_cost = base_costs.get(deployment_type, 5.0)
        
        if complexity == 'Moderate':
            base_cost *= 1.3
        elif complexity == 'Complex':
            base_cost *= 1.8
        
        return round(base_cost, 2)
