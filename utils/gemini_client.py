"""Gemini client wrapper with Google Search grounding support."""

import os
from typing import Dict, Optional
from google import genai
from google.genai import types


class GeminiClient:
    """Wrapper for Gemini API with grounding and thinking level support."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key. If not provided, reads from environment.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
    
    def generate_emails(
        self, 
        prompt: str, 
        thinking_level: str = "low"
    ) -> Dict:
        """
        Generate email content using Gemini with Google Search grounding.
        
        Args:
            prompt: The prompt to send to the model
            thinking_level: Either "low" or "high" for model thinking depth
            
        Returns:
            Dictionary containing:
                - text: Generated email content
                - input_tokens: Number of input tokens used
                - output_tokens: Number of output tokens used
                - total_tokens: Total tokens used
                - grounding_metadata: Search grounding information
        """
        # Configure Google Search grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        
        # Configure generation with tools and thinking level
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level)
        )
        
        # Generate content
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        
        # Extract token usage
        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count if hasattr(usage, 'prompt_token_count') else 0
        output_tokens = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else 0
        total_tokens = usage.total_token_count if hasattr(usage, 'total_token_count') else (input_tokens + output_tokens)
        
        # Extract grounding metadata if available
        grounding_metadata = None
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding_metadata = candidate.grounding_metadata
        
        return {
            "text": response.text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "grounding_metadata": grounding_metadata
        }
