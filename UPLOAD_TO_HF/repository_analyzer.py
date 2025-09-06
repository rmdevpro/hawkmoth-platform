# HAWKMOTH Repository Analyzer
# Production-ready GitHub repository analysis for deployment

import requests
import json
from typing import Dict, Any, List
import re

class GitHubAnalyzer:
    """
    Analyzes GitHub repositories for deployment readiness.
    Production version with fallback support.
    """
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        
    def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze a GitHub repository and return deployment information.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract owner and repo from URL
            owner, repo = self._parse_github_url(repo_url)
            
            # Get repository information
            repo_info = self._get_repo_info(owner, repo)
            
            # Get repository contents
            contents = self._get_repo_contents(owner, repo)
            
            # Analyze tech stack
            tech_stack = self._analyze_tech_stack(contents)
            
            # Determine deployment type
            deployment_type = self._determine_deployment_type(contents, tech_stack)
            
            # Estimate complexity and cost
            complexity = self._estimate_complexity(repo_info, contents, tech_stack)
            estimated_cost = self._estimate_monthly_cost(complexity, deployment_type)
            
            return {
                'name': repo_info.get('name', 'Unknown'),
                'description': repo_info.get('description', 'No description available'),
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0),
                'language': repo_info.get('language', 'Unknown'),
                'tech_stack': tech_stack,
                'deployment_type': deployment_type,
                'complexity': complexity,
                'estimated_cost': estimated_cost,
                'repo_url': repo_url,
                'clone_url': repo_info.get('clone_url', repo_url),
                'default_branch': repo_info.get('default_branch', 'main')
            }
            
        except Exception as e:
            # Fallback analysis for when API is unavailable
            return self._fallback_analysis(repo_url, str(e))
    
    def _parse_github_url(self, url: str) -> tuple:
        """Extract owner and repository name from GitHub URL."""
        # Remove protocol and trailing slashes
        clean_url = url.replace('https://', '').replace('http://', '').strip('/')
        
        if clean_url.startswith('github.com/'):
            parts = clean_url.split('/')
            if len(parts) >= 3:
                return parts[1], parts[2]
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def _get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information from GitHub API."""
        url = f"{self.github_api_base}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch repository info: {e}")
    
    def _get_repo_contents(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get repository contents from GitHub API."""
        url = f"{self.github_api_base}/repos/{owner}/{repo}/contents"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except requests.RequestException:
            return []
    
    def _analyze_tech_stack(self, contents: List[Dict[str, Any]]) -> List[str]:
        """Analyze tech stack based on repository contents."""
        tech_stack = set()
        
        # File patterns that indicate specific technologies
        tech_indicators = {
            'Python': [r'\.py$', r'requirements\.txt$', r'setup\.py$', r'Pipfile$'],
            'JavaScript': [r'\.js$', r'package\.json$', r'yarn\.lock$'],
            'TypeScript': [r'\.ts$', r'\.tsx$', r'tsconfig\.json$'],
            'React': [r'package\.json$'],  # Will be refined by content analysis
            'Vue.js': [r'\.vue$', r'vue\.config\.js$'],
            'Node.js': [r'package\.json$', r'server\.js$'],
            'Docker': [r'Dockerfile$', r'docker-compose\.yml$'],
            'Streamlit': [r'streamlit.*\.py$', r'.*streamlit.*'],
            'Gradio': [r'gradio.*\.py$', r'.*gradio.*'],
            'FastAPI': [r'.*fastapi.*', r'main\.py$'],
            'Flask': [r'app\.py$', r'.*flask.*'],
            'Django': [r'manage\.py$', r'settings\.py$'],
            'Next.js': [r'next\.config\.js$'],
            'HTML/CSS': [r'\.html$', r'\.css$'],
            'Java': [r'\.java$', r'pom\.xml$'],
            'Go': [r'\.go$', r'go\.mod$'],
            'Rust': [r'\.rs$', r'Cargo\.toml$'],
            'PHP': [r'\.php$', r'composer\.json$']
        }
        
        # Analyze filenames
        for file_info in contents:
            filename = file_info.get('name', '')
            
            for tech, patterns in tech_indicators.items():
                for pattern in patterns:
                    if re.search(pattern, filename, re.IGNORECASE):
                        tech_stack.add(tech)
        
        # Default to HTML if no specific tech detected
        if not tech_stack:
            tech_stack.add('Static HTML')
        
        return sorted(list(tech_stack))
    
    def _determine_deployment_type(self, contents: List[Dict[str, Any]], tech_stack: List[str]) -> str:
        """Determine the best deployment type based on tech stack."""
        
        # Priority-based deployment type detection
        if 'Streamlit' in tech_stack:
            return 'Streamlit App'
        elif 'Gradio' in tech_stack:
            return 'Gradio App'
        elif 'FastAPI' in tech_stack:
            return 'FastAPI Service'
        elif 'Flask' in tech_stack:
            return 'Flask Web App'
        elif 'Django' in tech_stack:
            return 'Django Web App'
        elif 'React' in tech_stack or 'Next.js' in tech_stack:
            return 'React/Next.js App'
        elif 'Vue.js' in tech_stack:
            return 'Vue.js App'
        elif 'Node.js' in tech_stack:
            return 'Node.js App'
        elif 'Python' in tech_stack:
            return 'Python Application'
        elif 'JavaScript' in tech_stack:
            return 'JavaScript App'
        elif 'Docker' in tech_stack:
            return 'Docker Container'
        else:
            return 'Static Website'
    
    def _estimate_complexity(self, repo_info: Dict[str, Any], contents: List[Dict[str, Any]], tech_stack: List[str]) -> str:
        """Estimate project complexity."""
        
        # Calculate complexity score
        score = 0
        
        # Repository metrics
        stars = repo_info.get('stargazers_count', 0)
        if stars > 1000:
            score += 3
        elif stars > 100:
            score += 2
        elif stars > 10:
            score += 1
        
        # File count
        file_count = len(contents)
        if file_count > 50:
            score += 3
        elif file_count > 20:
            score += 2
        elif file_count > 5:
            score += 1
        
        # Tech stack complexity
        complex_techs = ['Docker', 'Django', 'React', 'TypeScript', 'FastAPI']
        simple_techs = ['Streamlit', 'Gradio', 'Flask', 'Static HTML']
        
        for tech in tech_stack:
            if tech in complex_techs:
                score += 2
            elif tech in simple_techs:
                score += 1
        
        # Determine complexity level
        if score >= 8:
            return 'High'
        elif score >= 4:
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_monthly_cost(self, complexity: str, deployment_type: str) -> float:
        """Estimate monthly hosting cost in USD."""
        
        # Base costs by deployment type
        base_costs = {
            'Streamlit App': 0.0,  # Free on HuggingFace
            'Gradio App': 0.0,     # Free on HuggingFace
            'Static Website': 0.0,  # Free on many platforms
            'FastAPI Service': 5.0,
            'Flask Web App': 5.0,
            'Django Web App': 10.0,
            'React/Next.js App': 5.0,
            'Vue.js App': 5.0,
            'Node.js App': 5.0,
            'Python Application': 5.0,
            'JavaScript App': 5.0,
            'Docker Container': 10.0
        }
        
        base_cost = base_costs.get(deployment_type, 5.0)
        
        # Complexity multipliers
        multipliers = {
            'Low': 1.0,
            'Medium': 1.5,
            'High': 2.5
        }
        
        multiplier = multipliers.get(complexity, 1.0)
        
        return round(base_cost * multiplier, 2)
    
    def _fallback_analysis(self, repo_url: str, error: str) -> Dict[str, Any]:
        """Provide fallback analysis when API calls fail."""
        
        # Extract repo name from URL for basic info
        try:
            parts = repo_url.split('/')
            repo_name = parts[-1] if parts else 'unknown-repo'
        except:
            repo_name = 'unknown-repo'
        
        return {
            'name': repo_name,
            'description': f'Repository analysis unavailable: {error}',
            'stars': 0,
            'forks': 0,
            'language': 'Unknown',
            'tech_stack': ['Unknown'],
            'deployment_type': 'General Application',
            'complexity': 'Medium',
            'estimated_cost': 5.0,
            'repo_url': repo_url,
            'clone_url': repo_url,
            'default_branch': 'main',
            'error': error,
            'fallback_mode': True
        }

# Test function
def test_analyzer():
    """Test the repository analyzer with a known repository."""
    analyzer = GitHubAnalyzer()
    
    test_repos = [
        "https://github.com/streamlit/streamlit-example",
        "https://github.com/gradio-app/gradio",
        "https://github.com/fastapi/fastapi"
    ]
    
    print("🔍 Testing Repository Analyzer")
    print("=" * 50)
    
    for repo_url in test_repos:
        try:
            analysis = analyzer.analyze_repo(repo_url)
            print(f"\n📊 Analysis for: {repo_url}")
            print(f"   Name: {analysis['name']}")
            print(f"   Tech Stack: {', '.join(analysis['tech_stack'])}")
            print(f"   Deployment: {analysis['deployment_type']}")
            print(f"   Complexity: {analysis['complexity']}")
            print(f"   Est. Cost: ${analysis['estimated_cost']}/month")
            print(f"   Stars: {analysis['stars']:,}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing {repo_url}: {e}")

if __name__ == "__main__":
    test_analyzer()
