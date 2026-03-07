from abc import ABC, abstractmethod
from typing import Dict, Any, List

class GeneratorProvider(ABC):
    """
    Abstract base class for content generation providers (e.g., Rule-Based, Local LLM, OpenAI).
    Providers are responsible for generating ONLY the content dict portion of the schema.
    """

    @abstractmethod
    def generate_repo_content(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content for a repository page.
        
        Expected Return Schema (RepoContent):
        {
            "what_it_does": str,
            "key_features": List[str],
            "architecture_overview": str,
            "how_to_run": str,
            "use_cases": List[str],
            "alternatives": List[str]
        }
        """
        pass

    @abstractmethod
    def generate_topic_content(self, topic: str, repos: List[str]) -> Dict[str, Any]:
        """
        Generate content for a topic page.
        
        Expected Return Schema (TopicContent):
        {
            "intro": str,
            "who_this_topic_is_for": str,
            "common_architecture": str,
            "pros_cons": str,
            "learning_resources": List[str]
        }
        """
        pass

    @abstractmethod
    def generate_language_content(self, language: str, repos: List[str]) -> Dict[str, Any]:
        """
        Generate content for a language page.
        
        Expected Return Schema (LanguageContent):
        {
            "intro": str,
            "common_use_cases": List[str]
        }
        """
        pass
