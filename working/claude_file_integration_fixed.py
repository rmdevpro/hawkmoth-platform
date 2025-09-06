# HAWKMOTH Claude File Integration - Fixed Version
# Component 3: Send workspace files TO Claude via Anthropic API with multipart streaming

import os
import io
import json
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import mimetypes
from dataclasses import dataclass
from enum import Enum

class ClaudeFileError(Exception):
    """Custom exception for Claude file operations"""
    pass

class FileProcessingStatus(Enum):
    PENDING = "pending"
    UPLOADING = "uploading" 
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class FileProcessingResult:
    """Result of Claude file processing"""
    success: bool
    file_name: str
    claude_response: str
    processing_time: float
    cost_estimate: Optional[float] = None
    error_message: Optional[str] = None
    file_id: Optional[str] = None

class ClaudeFileIntegration:
    """
    HAWKMOTH Claude File Integration System
    Handles sending workspace files to Claude via Anthropic API using multipart streaming
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude file integration"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ClaudeFileError("ANTHROPIC_API_KEY environment variable required")
        
        # Ensure API key is a string, not bytes
        if isinstance(self.api_key, bytes):
            self.api_key = self.api_key.decode('utf-8')
        self.api_key = str(self.api_key).strip()
        
        self.base_url = "https://api.anthropic.com/v1"
        self.api_version = "2023-06-01"
        
        # Supported file types for Claude
        self.supported_types = {
            # Text files
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
            '.csv', '.tsv', '.log', '.sql', '.sh', '.bat', '.ps1', '.cfg', '.conf', '.ini',
            
            # Documents
            '.pdf', '.docx', '.xlsx', '.pptx', '.rtf',
            
            # Images  
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
            
            # Code files
            '.c', '.cpp', '.h', '.hpp', '.java', '.php', '.rb', '.go', '.rs', '.swift',
            '.kt', '.scala', '.clj', '.pl', '.r', '.matlab', '.m'
        }
        
        # File size limits (bytes)
        self.max_file_size = 32 * 1024 * 1024  # 32MB
        self.max_text_size = 1024 * 1024  # 1MB for text files
        
        # Processing status tracking
        self.processing_status: Dict[str, FileProcessingStatus] = {}
        
    async def upload_file_to_claude(self, file_path: str, purpose: str = "file-processing") -> Dict[str, Any]:
        """Upload file to Claude using multipart streaming (not base64)"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ClaudeFileError(f"File not found: {file_path}")
            
        # Validate file type and size
        self._validate_file(file_path)
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Read file for streaming
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Prepare multipart form data
                files = {
                    'file': (file_path.name, io.BytesIO(file_content), mime_type)
                }
                
                data = {
                    'purpose': purpose
                }
                
                headers = {
                    'anthropic-version': self.api_version,
                    'anthropic-beta': 'files-api-2025-04-14',
                    'x-api-key': self.api_key
                }
                
                # Upload using multipart streaming
                response = await client.post(
                    f"{self.base_url}/files",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise ClaudeFileError(f"Upload failed: {response.status_code} - {error_detail}")
                
                upload_result = response.json()
                
                return {
                    'success': True,
                    'file_id': upload_result.get('id'),
                    'file_name': file_path.name,
                    'size': len(file_content),
                    'mime_type': mime_type,
                    'upload_info': upload_result
                }
                
        except httpx.TimeoutException:
            raise ClaudeFileError(f"Upload timeout for file: {file_path.name}")
        except Exception as e:
            raise ClaudeFileError(f"Upload error: {str(e)}")
    
    async def process_file_with_claude(self, file_path: str, instruction: str = "Analyze this file") -> FileProcessingResult:
        """Complete workflow: Upload file to Claude and get analysis"""
        import time
        start_time = time.time()
        file_name = Path(file_path).name
        
        try:
            # Update status
            self.processing_status[file_name] = FileProcessingStatus.UPLOADING
            
            # Upload file to Claude
            upload_result = await self.upload_file_to_claude(file_path)
            
            if not upload_result['success']:
                raise ClaudeFileError("File upload failed")
            
            file_id = upload_result['file_id']
            
            # Update status
            self.processing_status[file_name] = FileProcessingStatus.PROCESSING
            
            # Send message to Claude with file reference (pass file_path for type detection)
            claude_response = await self._send_message_with_file(file_id, instruction, file_path)
            
            # Update status
            self.processing_status[file_name] = FileProcessingStatus.COMPLETE
            
            processing_time = time.time() - start_time
            
            return FileProcessingResult(
                success=True,
                file_name=file_name,
                claude_response=claude_response,
                processing_time=processing_time,
                file_id=file_id,
                cost_estimate=self._estimate_cost(claude_response)
            )
            
        except Exception as e:
            self.processing_status[file_name] = FileProcessingStatus.ERROR
            processing_time = time.time() - start_time
            
            return FileProcessingResult(
                success=False,
                file_name=file_name,
                claude_response="",
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _send_message_with_file(self, file_id: str, instruction: str, file_path: str = "") -> str:
        """Send message to Claude with file attachment"""
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                
                headers = {
                    'content-type': 'application/json',
                    'anthropic-version': self.api_version,
                    'x-api-key': self.api_key
                }
                
                # Determine content block type based on file extension
                content_type = self._get_content_block_type(file_path) if file_path else 'document'
                
                # Create message with file attachment
                payload = {
                    "model": "claude-sonnet-4-20250514",  # Latest Claude Sonnet 4 model
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": instruction
                                },
                                {
                                    "type": content_type,
                                    "source": {
                                        "type": "file",
                                        "file_id": file_id
                                    }
                                }
                            ]
                        }
                    ]
                }
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise ClaudeFileError(f"Claude API error: {response.status_code} - {error_detail}")
                
                result = response.json()
                
                # Extract Claude's response
                if 'content' in result and len(result['content']) > 0:
                    return result['content'][0].get('text', 'No response from Claude')
                else:
                    return "Empty response from Claude"
                    
        except httpx.TimeoutException:
            raise ClaudeFileError("Claude processing timeout")
        except Exception as e:
            raise ClaudeFileError(f"Claude processing error: {str(e)}")
    
    async def process_multiple_files(self, file_paths: List[str], instruction: str = "Analyze these files") -> List[FileProcessingResult]:
        """Process multiple files with Claude concurrently"""
        
        # Process files concurrently (max 3 at a time to avoid rate limits)
        semaphore = asyncio.Semaphore(3)
        
        async def process_single_file(file_path: str):
            async with semaphore:
                return await self.process_file_with_claude(file_path, instruction)
        
        tasks = [process_single_file(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    FileProcessingResult(
                        success=False,
                        file_name=Path(file_paths[i]).name,
                        claude_response="",
                        processing_time=0.0,
                        error_message=str(result)
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_processing_status(self, file_name: str) -> FileProcessingStatus:
        """Get current processing status for a file"""
        return self.processing_status.get(file_name, FileProcessingStatus.PENDING)
    
    def get_all_processing_status(self) -> Dict[str, str]:
        """Get processing status for all files"""
        return {name: status.value for name, status in self.processing_status.items()}
    
    def _validate_file(self, file_path: Path) -> None:
        """Validate file type and size"""
        
        # Check file extension
        if file_path.suffix.lower() not in self.supported_types:
            raise ClaudeFileError(f"Unsupported file type: {file_path.suffix}")
        
        # Check file size
        file_size = file_path.stat().st_size
        
        if file_size > self.max_file_size:
            raise ClaudeFileError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        # Additional check for text files
        if file_path.suffix.lower() in {'.txt', '.md', '.py', '.js', '.html', '.css', '.json'}:
            if file_size > self.max_text_size:
                raise ClaudeFileError(f"Text file too large: {file_size} bytes (max: {self.max_text_size})")
    
    def _get_content_block_type(self, file_path: str) -> str:
        """Determine the correct content block type based on file extension"""
        file_ext = Path(file_path).suffix.lower()
        
        # Image files use 'image' content block
        image_types = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        if file_ext in image_types:
            return 'image'
        
        # Document files use 'document' content block
        document_types = {'.pdf', '.docx', '.xlsx', '.pptx', '.rtf'}
        if file_ext in document_types:
            return 'document'
        
        # Text and code files - Claude may prefer these as plain text
        # But we'll try document type first
        return 'document'
    
    def _estimate_cost(self, response: str) -> float:
        """Estimate cost based on response length (rough estimate)"""
        
        # Rough cost estimation for Claude Sonnet 4
        # Input: ~$3/1M tokens, Output: ~$15/1M tokens
        
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        output_tokens = len(response) / 4
        
        # Assume input was ~500 tokens (file + instruction)
        input_tokens = 500
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        
        return round(input_cost + output_cost, 4)
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file extensions"""
        return sorted(list(self.supported_types))
    
    def is_file_supported(self, file_path: str) -> bool:
        """Check if file type is supported"""
        return Path(file_path).suffix.lower() in self.supported_types


# Utility functions for easy integration
async def quick_analyze_file(file_path: str, instruction: str = "Analyze this file", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Quick utility function to analyze a single file with Claude"""
    
    try:
        claude_integration = ClaudeFileIntegration(api_key)
        result = await claude_integration.process_file_with_claude(file_path, instruction)
        
        return {
            'success': result.success,
            'response': result.claude_response,
            'file_name': result.file_name,
            'processing_time': result.processing_time,
            'cost_estimate': result.cost_estimate,
            'error': result.error_message
        }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'file_name': Path(file_path).name,
            'processing_time': 0.0,
            'cost_estimate': 0.0,
            'error': str(e)
        }


# Example usage and testing
if __name__ == "__main__":
    async def test_claude_integration():
        """Test the Claude file integration"""
        
        # Initialize (requires ANTHROPIC_API_KEY environment variable)
        try:
            claude = ClaudeFileIntegration()
            
            print("✅ Claude File Integration initialized")
            print(f"📁 Supported file types: {len(claude.get_supported_file_types())}")
            
            # Test file validation
            print(f"🧪 Testing file type validation...")
            print(f"   Python file supported: {claude.is_file_supported('test.py')}")
            print(f"   Executable not supported: {claude.is_file_supported('test.exe')}")
            
        except ClaudeFileError as e:
            print(f"❌ Initialization failed: {e}")
            print("💡 Make sure ANTHROPIC_API_KEY environment variable is set")
    
    # Run test if script is executed directly
    import asyncio
    asyncio.run(test_claude_integration())
