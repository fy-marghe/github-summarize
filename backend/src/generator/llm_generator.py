from typing import Dict, Any, List, Optional
import json
import os
import datetime

from .provider_interface import GeneratorProvider
from .rule_based_provider import RuleBasedProvider
from .local_model_provider import LocalModelProvider
from .openai_provider import OpenAIProvider

class LLMGenerator:
    """
    Orchestrates content generation using the configured provider (Local LLM, Rule-Based, OpenAI).
    Handles aggregation of topics and languages, and structuring the final JSON schema.
    """
    
    primary_provider: GeneratorProvider
    fallback_provider: Optional[GeneratorProvider]
    current_provider_name: str
    
    def __init__(self, api_key: Optional[str] = None):
        self._init_providers(api_key)
        
        # In memory state to aggregate topics and languages across the run
        self.topics = {}
        self.languages = {}

    def _init_providers(self, api_key: str):
        # Determine providers from environment variables
        provider_type = os.getenv("GENERATOR_PROVIDER", "rule_based").lower()
        fallback_type = os.getenv("GENERATOR_FALLBACK_PROVIDER", "rule_based").lower()
        
        # Instantiate fallback
        self.fallback_provider = self._create_provider(fallback_type, default_to_rule=True)
        
        # Instantiate primary
        if provider_type == fallback_type:
             self.primary_provider = self.fallback_provider
        else:
             # Prevent infinite recursion / circular fallback by passing None or RuleBased if it's the primary
             self.primary_provider = self._create_provider(provider_type, fallback=self.fallback_provider, api_key=api_key)
             
        self.current_provider_name = provider_type
        print(f"[LLMGenerator] Initialized with primary='{provider_type}', fallback='{fallback_type}'")

    def _create_provider(self, p_type: str, default_to_rule: bool = False, fallback: GeneratorProvider = None, api_key: str = None) -> GeneratorProvider:
        if p_type == "local_model":
            model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
            return LocalModelProvider(api_url=url, model=model, fallback_provider=fallback)
        elif p_type == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            return OpenAIProvider(api_key=api_key, fallback_provider=fallback)
        elif p_type == "rule_based":
            return RuleBasedProvider()
        else:
            print(f"[LLMGenerator] Unknown provider '{p_type}'. Defaulting to rule_based.")
            return RuleBasedProvider()

    def _get_generation_meta(self, provider: GeneratorProvider, provider_name: str) -> Dict[str, Any]:
        """Extract metadata about the generation process."""
        used_fallback = getattr(provider, "used_fallback", False)
        active_name = provider_name
        
        # Get the original intended model before overriding active_name
        model = "none"
        if provider_name == "local_model":
             model = getattr(provider, "model", "unknown")
        elif provider_name == "openai":
             model = getattr(provider, "model", "gpt-4o-mini")

        if used_fallback:
             # Override the provider attribute to show what actually fulfilled the request
             active_name = os.getenv("GENERATOR_FALLBACK_PROVIDER", "rule_based").lower()

        return {
            "provider": active_name,
            "model": model,
            "fallback_used": used_fallback
        }

    def generate_content(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Generating repo content for {repo_data['owner']}/{repo_data['name']} using {self.current_provider_name}...")
        
        # Generate the specific content (dict) via the provider
        content_data = self.primary_provider.generate_repo_content(repo_data)
        
        # Ensure fallback mechanism generated *something*
        if not content_data:
             print(f"[LLMGenerator] CRITICAL: Content generation failed entirely. Resorting to basic stub.")
             content_data = {
                 "what_it_does": f"{repo_data['name']} is a repository by {repo_data['owner']}.",
                 "key_features": [],
                 "architecture_overview": "",
                 "how_to_run": "",
                 "use_cases": [],
                 "alternatives": []
             }
        
        primary_topic = repo_data["metadata"].get("topics", ["uncategorized"])[0] if repo_data["metadata"].get("topics") else "uncategorized"
        primary_lang = repo_data["metadata"].get("language", "Unknown")
        repo_slug = f"{repo_data['owner']}--{repo_data['name']}" # Use -- or __ to separate
        
        # Aggregate into topics
        if primary_topic not in self.topics:
            self.topics[primary_topic] = []
        self.topics[primary_topic].append(repo_slug)
        
        # Aggregate into languages
        if primary_lang not in self.languages:
            self.languages[primary_lang] = []
        self.languages[primary_lang].append(repo_slug)

        return {
            "id": f"{repo_data['owner']}/{repo_data['name']}",
            "slug": f"{repo_data['owner']}-{repo_data['name']}",
            "canonical_path": f"/repo/{repo_data['owner']}/{repo_data['name']}",
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "source_updated_at": repo_data["metadata"].get("updated_at", ""),
            "generation_meta": self._get_generation_meta(self.primary_provider, self.current_provider_name),
            "repo_metadata": {
                "owner": repo_data["owner"],
                "name": repo_data["name"],
                "description": repo_data["metadata"].get("description", ""),
                "stars": repo_data["metadata"].get("stargazers_count", 0),
                "forks": repo_data["metadata"].get("forks_count", 0),
                "primary_language": primary_lang,
                "default_branch": repo_data["metadata"].get("default_branch", "main"),
                "license": repo_data["metadata"].get("license", {}).get("spdx_id", "") if repo_data["metadata"].get("license") else ""
            },
            "primary_topic": primary_topic,
            "related_topics": repo_data["metadata"].get("topics", [])[1:4],
            "related_languages": [primary_lang],
            "dependencies": {
                "files": repo_data["dependency_files_found"],
                "detected_packages": []
            },
            "seo_metadata": { 
                "title": f"{repo_data['name']} by {repo_data['owner']} - Explain, Architecture & Alternatives", 
                "description": repo_data["metadata"].get("description", "")
            },
            "content": content_data, # Use the generated dict here
            "use_cases": content_data.get("use_cases", []), # Lift out if necessary or keep inside content
            "alternatives": content_data.get("alternatives", []),
            "related_repos": []
        }

    def remove_repo_from_aggregations(self, repo_slug: str):
        """Removes a skipped repository from the topics and languages aggregations so it isn't listed."""
        for topic in self.topics:
            if repo_slug in self.topics[topic]:
                self.topics[topic].remove(repo_slug)
                
        for lang in self.languages:
            if repo_slug in self.languages[lang]:
                self.languages[lang].remove(repo_slug)

    def generate_topics_data(self):
        print("Generating consolidated topics data...")
        topic_data_list = []
        for topic, repos in self.topics.items():
            topic_data_list.append({
                "id": topic,
                "slug": topic,
                "canonical_path": f"/topic/{topic}",
                "name": topic.replace('-', ' ').title(),
                "description": f"Curated list of github repositories related to {topic}.",
                "generation_meta": self._get_generation_meta(self.primary_provider, self.current_provider_name),
                "content": self.primary_provider.generate_topic_content(topic, repos),
                "use_cases": ["Production deployment", "Prototyping"],
                "top_repos": repos,
                "related_topics": ["machine-learning", "python-tools"],
                "comparison_links": [],
                "seo_metadata": {
                    "title": f"Best {topic.replace('-', ' ').title()} GitHub Repositories",
                    "description": f"Explore the top {topic} repositories. Compare architectures, use cases, and pick the best tool."
                }
            })
        return topic_data_list

    def generate_languages_data(self):
        print("Generating consolidated languages data...")
        lang_data_list = []
        for lang, repos in self.languages.items():
            lang_slug = lang.lower()
            lang_data_list.append({
                "id": lang_slug,
                "slug": lang_slug,
                "canonical_path": f"/language/{lang_slug}",
                "name": lang,
                "generation_meta": self._get_generation_meta(self.primary_provider, self.current_provider_name),
                "content": self.primary_provider.generate_language_content(lang, repos),
                "representative_repos": repos,
                "related_topics": list(self.topics.keys())[:3] if self.topics else [], # Just mock related topics
                "seo_metadata": {
                    "title": f"Top {lang} GitHub Repositories",
                    "description": f"Discover amazing {lang} projects on GitHub. View popular frameworks and libraries."
                }
            })
        return lang_data_list
