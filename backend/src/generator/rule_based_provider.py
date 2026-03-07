from typing import Dict, Any, List
from .provider_interface import GeneratorProvider

class RuleBasedProvider(GeneratorProvider):
    """
    Rule-based generator that uses repository metadata, file trees, and README extracts
    to assemble template-based structured content without requiring an external AI API.
    """

    def generate_repo_content(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce template-based RepoContent.
        """
        import re
        metadata = repo_data.get("metadata", {})
        name = repo_data.get("name", "Unknown Project")
        owner = repo_data.get("owner", "Unknown Owner")
        desc = metadata.get("description", "") or "No description provided."
        lang = metadata.get("language", "Unknown Language")
        topics = metadata.get("topics", [])
        dependency_files = repo_data.get("dependency_files_found", [])
        readme_raw = repo_data.get("readme", "")
        
        # Helper: Extract sentences from README
        def extract_readme_intro(text: str) -> str:
            if not text: return ""
            # Remove html tags and code blocks roughly to just get textual paragraphs
            text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', '', text)
            # Find paragraphs that look like actual description text
            paras = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 40 and not p.strip().startswith(('#', '!', '[', '|', '<', '>'))]
            # Remove markdown links but keep text
            clean_paras = [re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', p) for p in paras]
            return " ".join(clean_paras[:3])

        readme_intro = extract_readme_intro(readme_raw)
        
        # 1. What it does
        what_it_does = f"{name} is a comprehensive {lang}-based software project developed and maintained by {owner}. "
        what_it_does += f"The primary focus of this repository is to provide robust solutions in the domain of: {desc} "
        if topics:
            top_topics = [topics[i] for i in range(min(5, len(topics)))]
            what_it_does += f"It heavily intersects with key technological areas including {', '.join(top_topics)}. "
        if readme_intro:
            what_it_does += f"According to the project documentation: {readme_intro} "
            
        # 2. Key features (Rule based extraction/guessing)
        key_features = [
            f"Built natively with {lang} for optimal performance and ecosystem compatibility.",
            "Open source architecture allowing for extensive community contributions on GitHub."
        ]
        if topics:
            feat_topics = [topics[i] for i in range(min(3, len(topics)))]
            key_features.append(f"Supports and implements modern paradigms such as {', '.join(feat_topics)}.")
        key_features.append("Provides a systematic approach to solving standard domain-specific challenges.")
        
        # 3. Architecture Overview
        arch = f"The {name} repository is organized following industry standard {lang} conventions to ensure maintainability and scalability. "
        arch += "The codebase is logically grouped around its core functionalities, offering a main entry point and modular components. "
        if dependency_files:
            arch += f"It leverages modern software package management systems, explicitly relying on configurations found in {', '.join(dependency_files)}. "
            if "requirements.txt" in dependency_files or "pyproject.toml" in dependency_files or "setup.py" in dependency_files:
                arch += "This indicates a canonical Python environment setup where dependencies and scripts are isolated and managed robustly. "
            if "package.json" in dependency_files:
                arch += "The presence of standard web ecosystem manifests signifies a Node or frontend-facing architecture relying on npm/yarn for package resolution. "
            if "Cargo.toml" in dependency_files:
                arch += "Rust-based build configurations dictate strict memory-safe system-level architectural constraints. "
        else:
             arch += "The repository structure appears self-contained, handling its execution context directly without explicit third-party dependency file footprints. "

        # 4. How to run
        how_to_run = f"To deploy or interact with {name} locally, you should typically follow these standard sequential steps:\n"
        how_to_run += f"1. Clone the repository directly from GitHub: `git clone https://github.com/{owner}/{name}.git`\n"
        how_to_run += "2. Navigate into the freshly cloned directory via your terminal.\n"
        if "requirements.txt" in dependency_files:
            how_to_run += "3. Install the required Python dependencies in a virtual environment by executing `pip install -r requirements.txt`.\n"
        elif "package.json" in dependency_files:
            how_to_run += "3. Install the required Node modules by executing `npm install` or `yarn install`.\n"
        elif "Cargo.toml" in dependency_files:
            how_to_run += "3. Build the binary using Rust's package manager by executing `cargo build` and then run it using `cargo run`.\n"
        else:
            how_to_run += "3. Carefully inspect the root README.md file for highly specific installation prerequisites or build scripts.\n"
        how_to_run += "4. Execute the primary run command or entry script to instantiate the service or utilize the library."

        # 5. Use Cases
        use_cases = []
        if topics:
             use_cases.append(f"Implementing production-grade systems focused strictly on {topics[0]}.")
        use_cases.append(f"Serving as a foundational building block for developers working with {lang} architectures.")
        if len(topics) > 1:
             use_cases.append(f"Integrating custom workflows that require robust {topics[1]} capabilities.")
        else:
             use_cases.append("Analyzing reference open-source code to establish architectural best practices.")
        
        # 6. Alternatives
        alternatives = []
        lowered_name = name.lower()
        if "fastapi" in lowered_name or "flask" in lowered_name or "django" in lowered_name or (topics and "web" in topics):
             alternatives.extend(["Flask", "Django REST Framework", "Express.js"])
        elif "machine-learning" in topics or "ai" in topics or "agents" in topics:
             alternatives.extend(["TensorFlow Ecosystem", "Various other HuggingFace community models", "Other domain specific AI/ML frameworks"])
        elif "react" in topics or "vue" in topics:
             alternatives.extend(["Vue.js", "Angular", "Svelte"])
        else:
             primary_t = topics[0] if topics else lang
             alternatives.append(f"Other widely-adopted solutions utilizing {primary_t}.")
             alternatives.append("Enterprise or proprietary tools operating within the same market sector.")

        return {
            "what_it_does": what_it_does,
            "key_features": key_features,
            "architecture_overview": arch,
            "how_to_run": how_to_run,
            "use_cases": use_cases,
            "alternatives": alternatives
        }

    def generate_topic_content(self, topic: str, repos: List[str]) -> Dict[str, Any]:
        """
        Produce template-based TopicContent.
        """
        formatted_topic = topic.replace('-', ' ').title()
        repo_count = len(repos)
        
        return {
            "intro": f"The {formatted_topic} topic encompasses tools, frameworks, and libraries that address common challenges in this domain.",
            "who_this_topic_is_for": f"Developers, data scientists, and engineers interested in implementing {formatted_topic} capabilities into their applications.",
            "common_architecture": f"Projects in the {formatted_topic} space typically involve specialized processing pipelines or standardized APIs tailored for these specific use cases.",
            "pros_cons": f"Pros: Access to specialized, community-driven tools. Cons: Ecosystem can be fragmented, requiring careful evaluation of {repo_count} or more alternative repositories.",
            "learning_resources": [
                f"Official GitHub Topics page for {topic}",
                "Community tutorials and blog posts on Medium or Dev.to",
                "Documentation of the top repositories listed below"
            ]
        }

    def generate_language_content(self, language: str, repos: List[str]) -> Dict[str, Any]:
        """
        Produce template-based LanguageContent.
        """
        repo_count = len(repos)
        
        return {
            "intro": f"{language} is a powerful programming language backed by a large ecosystem. This page highlights some of the most notable open-source repositories built using {language}.",
            "common_use_cases": [
                f"Core backend and infrastructure services utilizing {language}'s strengths.",
                "Tooling and automation scripts widely adopted by the community.",
                "Specialized frameworks and libraries."
            ]
        }
