import json
import requests
import re
from typing import Dict, Any, List
from .provider_interface import GeneratorProvider

class LocalModelProvider(GeneratorProvider):
    """
    LLM generator that uses a local Ollama instance to generate structured content.
    Includes robust fallback mechanisms for JSON parsing and schema validation.
    """

    def __init__(self, api_url: str = "http://localhost:11434/api/generate", model: str = "llama3.1:8b", fallback_provider: GeneratorProvider = None, max_retries: int = 2):
        self.api_url = api_url
        self.model = model
        self.max_retries = max_retries
        self.fallback_provider = fallback_provider
        self.used_fallback = False

    def _clean_json_response(self, text: str) -> str:
        """Attempt to clean the text to extract just the JSON."""
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return text

    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Call the Ollama API with the given prompt and retry logic."""
        self.used_fallback = False
        
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json" # Ollama supports enforcing JSON format natively in recent versions
                }
                
                response = requests.post(self.api_url, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                raw_text = result.get("response", "")
                
                cleaned_text = self._clean_json_response(raw_text)
                
                # Try parsing JSON
                parsed_json = json.loads(cleaned_text)
                return parsed_json
                
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                print(f"[LocalModelProvider] Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    print(f"[LocalModelProvider] Max retries reached. Falling back.")
                    break
        
        # If we reach here, we failed and need to fallback
        self.used_fallback = True
        return {}

    def generate_repo_content(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        metadata = repo_data.get("metadata", {})
        name = repo_data.get("name", "")
        desc = metadata.get("description", "")
        lang = metadata.get("language", "")
        topics = metadata.get("topics", [])
        
        # Truncate README to avoid context length limits
        readme = repo_data.get("readme", "")[:2000] 

        prompt = f"""
        You are an expert technical writer. Analyze the following GitHub repository and provide a detailed overview.
        Do NOT copy the README directly. Synthesize the information.
        
        Repository Name: {name}
        Description: {desc}
        Language: {lang}
        Topics: {', '.join(topics)}
        
        README Snippet:
        {readme}
        
        Respond with ONLY a valid JSON object matching this schema exactly:
        {{
            "what_it_does": "A concise paragraph explaining what this project does and the problem it solves.",
            "key_features": ["feature 1", "feature 2", "feature 3"],
            "architecture_overview": "A brief explanation of how it is built or structured.",
            "how_to_run": "Basic steps to get started or run the project.",
            "use_cases": ["use case 1", "use case 2"],
            "alternatives": ["alternative tool 1", "alternative tool 2"]
        }}
        """

        result = self._call_ollama(prompt)
        
        if result and self._validate_repo_schema(result):
            return result
            
        if self.fallback_provider:
            self.used_fallback = True
            return self.fallback_provider.generate_repo_content(repo_data)
        
        return {} # Should theoretically never happen if fallback is configured correctly

    def _validate_repo_schema(self, data: Dict[str, Any]) -> bool:
        required_keys = ["what_it_does", "key_features", "architecture_overview", "how_to_run", "use_cases", "alternatives"]
        return all(key in data for key in required_keys)

    def generate_topic_content(self, topic: str, repos: List[str]) -> Dict[str, Any]:
        prompt = f"""
        You are an expert technical writer. Write an overview of the technical topic '{topic}'.
        The following popular repositories belong to this topic: {', '.join(repos[:5] if repos else [])}.
        
        Respond with ONLY a valid JSON object matching this schema exactly:
        {{
            "intro": "A strong introductory paragraph about what this topic is.",
            "who_this_topic_is_for": "Who benefits from tools in this category.",
            "common_architecture": "Common architectural patterns seen in tools for this topic.",
            "pros_cons": "General pros and cons of using frameworks in this space.",
            "learning_resources": ["resource type 1", "resource type 2"]
        }}
        """
        
        result = self._call_ollama(prompt)
        
        if result and self._validate_topic_schema(result):
            return result
            
        if self.fallback_provider:
            self.used_fallback = True
            return self.fallback_provider.generate_topic_content(topic, repos)
            
        return {}
        
    def _validate_topic_schema(self, data: Dict[str, Any]) -> bool:
        required_keys = ["intro", "who_this_topic_is_for", "common_architecture", "pros_cons", "learning_resources"]
        return all(key in data for key in required_keys)

    def generate_language_content(self, language: str, repos: List[str]) -> Dict[str, Any]:
        prompt = f"""
        You are an expert technical writer. Write a brief overview of the programming language '{language}'.
        Popular repositories using this language include: {', '.join(repos[:5] if repos else [])}.
        
        Respond with ONLY a valid JSON object matching this schema exactly:
        {{
            "intro": "A strong introductory paragraph about the language and its ecosystem.",
            "common_use_cases": ["use case 1", "use case 2", "use case 3"]
        }}
        """
        
        result = self._call_ollama(prompt)
        
        if result and self._validate_lang_schema(result):
            return result
            
        if self.fallback_provider:
            self.used_fallback = True
            return self.fallback_provider.generate_language_content(language, repos)
            
        return {}

    def _validate_lang_schema(self, data: Dict[str, Any]) -> bool:
        required_keys = ["intro", "common_use_cases"]
        return all(key in data for key in required_keys)
