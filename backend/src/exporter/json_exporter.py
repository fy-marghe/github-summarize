import json
import os
from pathlib import Path

class JsonExporter:
    def __init__(self):
        # Resolve backend root by going up from backend/src/exporter/json_exporter.py
        # __file__ -> json_exporter.py (parent: exporter, parent: src, parent: backend)
        backend_dir = Path(__file__).resolve().parent.parent.parent
        self.output_dir = backend_dir / "output"
        
        self.repos_dir = self.output_dir / "repos"
        self.topics_dir = self.output_dir / "topics"
        self.languages_dir = self.output_dir / "languages"

        os.makedirs(self.repos_dir, exist_ok=True)
        os.makedirs(self.topics_dir, exist_ok=True)
        os.makedirs(self.languages_dir, exist_ok=True)

    def export_repo(self, repo_data):
        filename = f"{repo_data['repo_metadata']['owner']}__{repo_data['repo_metadata']['name']}.json"
        filepath = os.path.join(self.repos_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(repo_data, f, ensure_ascii=False, indent=2)
            
        print(f"Exported {filepath}")
        return filepath
        
    def export_topic(self, topic_data):
        filename = f"{topic_data['slug']}.json"
        filepath = os.path.join(self.topics_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(topic_data, f, ensure_ascii=False, indent=2)
            
        print(f"Exported {filepath}")
        return filepath
        
    def export_language(self, lang_data):
        filename = f"{lang_data['slug']}.json"
        filepath = os.path.join(self.languages_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, ensure_ascii=False, indent=2)
            
        print(f"Exported {filepath}")
        return filepath

    def export_quality_reports(self, reports_list):
        filename = "quality_check_report.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reports_list, f, ensure_ascii=False, indent=2)
            
        print(f"Exported Quality Reports to {filepath}")
        return filepath
