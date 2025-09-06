# HAWKMOTH Google Custom Search Integration
import os
import json
import time
from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class HAWKMOTHGoogleSearch:
    def __init__(self):
        # Get API credentials from environment
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_CSE_ID')
        
        # Initialize Google Custom Search service
        self.service = None
        self.search_available = False
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Custom Search service"""
        try:
            if self.api_key and self.search_engine_id:
                self.service = build("customsearch", "v1", developerKey=self.api_key)
                self.search_available = True
                print("✅ Google Custom Search initialized successfully")
            else:
                print("⚠️ Google Search not available - missing API credentials")
                print("   Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables")
        except Exception as e:
            print(f"❌ Google Search initialization failed: {e}")
            self.search_available = False
    
    def search(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """Execute Google Custom Search"""
        
        if not self.search_available:
            return {
                'success': False,
                'error': 'Google Custom Search not available - missing API credentials',
                'fallback_message': f"🔍 **Search needed for**: {query}\n\nTo enable real web search, configure GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables."
            }
        
        try:
            # Execute search
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=num_results
            ).execute()
            
            # Parse results
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'displayLink': item.get('displayLink', '')
                    })
            
            # Format response
            if search_results:
                formatted_response = self._format_search_results(query, search_results)
                return {
                    'success': True,
                    'response': formatted_response,
                    'raw_results': search_results,
                    'total_results': result.get('searchInformation', {}).get('totalResults', '0'),
                    'search_time': result.get('searchInformation', {}).get('searchTime', '0'),
                    'cost': 0.005  # $5 per 1000 searches
                }
            else:
                return {
                    'success': True,
                    'response': f"🔍 **No results found for**: {query}\n\nTry rephrasing your search or using different keywords.",
                    'raw_results': [],
                    'cost': 0.005
                }
        
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            error_message = error_details.get('error', {}).get('message', str(e))
            
            return {
                'success': False,
                'error': f'Google Search API error: {error_message}',
                'fallback_message': f"🔍 **Search failed for**: {query}\n\nAPI Error: {error_message}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Search execution failed: {str(e)}',
                'fallback_message': f"🔍 **Search failed for**: {query}\n\nError: {str(e)}"
            }
    
    def _format_search_results(self, query: str, results: List[Dict]) -> str:
        """Format search results for display"""
        
        formatted = f"🔍 **Web Search Results for**: {query}\n\n"
        
        for i, result in enumerate(results, 1):
            title = result['title']
            snippet = result['snippet']
            link = result['link']
            domain = result['displayLink']
            
            # Clean up snippet (remove extra whitespace, truncate if too long)
            snippet = ' '.join(snippet.split())
            if len(snippet) > 150:
                snippet = snippet[:147] + "..."
            
            formatted += f"**{i}. {title}**\n"
            formatted += f"*{domain}*\n"
            formatted += f"{snippet}\n"
            formatted += f"🔗 [Read more]({link})\n\n"
        
        return formatted
    
    def search_with_fallback(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """Search with graceful fallback if API unavailable"""
        
        # Try real search first
        result = self.search(query, num_results)
        
        if result['success']:
            return result
        else:
            # Fallback to helpful message
            fallback_response = result.get('fallback_message', f"🔍 **Search needed**: {query}")
            
            return {
                'success': True,  # Mark as success to continue escalation
                'response': fallback_response,
                'method': 'fallback',
                'cost': 0.0,
                'escalation_successful': True
            }
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search service statistics"""
        return {
            'service_available': self.search_available,
            'api_key_configured': bool(self.api_key),
            'search_engine_configured': bool(self.search_engine_id),
            'service_initialized': self.service is not None
        }
