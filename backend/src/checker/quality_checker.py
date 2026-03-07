from typing import Dict, Any, List
import json
import re

# Use rapidfuzz for string similarity if available, fallback to basic jaccard
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

class QualityChecker:
    """
    Evaluates the generation quality of SEO articles based on the specification.
    Outputs a score (0-100), an action (INDEX, NOINDEX, SKIP_AND_REGENERATE),
    and a report of the evaluation.
    """
    
    def __init__(self, analysis_db: Dict[str, Any] = None):
        # In a real app, this might connect to a DB. For MVP, we can pass a dictionary.
        if analysis_db is None:
            self.analysis_db = {
                "existing_titles": set(),
                "same_topic_bodies": [],
                "all_repo_bodies": []
            }
        else:
            self.analysis_db = analysis_db
        self.last_report = {}

    def _strip_markdown_and_html(self, text: str) -> str:
        """Removes code blocks, HTML tags, and markdown formatting to count pure text words/chars."""
        if not text:
            return ""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove markdown headers and links
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Simple trigram jaccard similarity."""
        if not text1 or not text2:
            return 0.0
            
        def get_trigrams(s):
            s = s.lower()
            return set(s[i:i+3] for i in range(len(s)-2))
            
        set1 = get_trigrams(text1)
        set2 = get_trigrams(text2)
        
        if not set1 or not set2:
             return 0.0
             
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def _calculate_str_similarity(self, text1: str, text2: str) -> float:
        """Calculates similarity score (0.0 to 1.0) between two texts."""
        if HAS_RAPIDFUZZ:
            # RapidFuzz returns 0-100, normalize to 0.0-1.0
            return fuzz.token_sort_ratio(text1, text2) / 100.0
        else:
            return self._jaccard_similarity(text1, text2)

    def _get_max_similarity(self, target_text: str, text_list: List[str]) -> float:
        if not text_list:
            return 0.0
        max_sim = 0.0
        for text in text_list:
            sim = self._calculate_str_similarity(target_text, text)
            if sim > max_sim:
                max_sim = sim
        return max_sim

    def _extract_full_body_text(self, generated_data: Dict[str, Any]) -> str:
        """
        The generated_data has a 'content' dict with various fields (what_it_does, key_features, etc).
        We stitch them back together to evaluate length and similarity.
        """
        content = generated_data.get("content", {})
        parts = []
        for key, value in content.items():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list) and all(isinstance(v, str) for v in value):
                parts.append(" ".join(str(v) for v in value))
            elif isinstance(value, list) and all(isinstance(v, dict) for v in value):
                for item in value:
                     for k, v in item.items():
                          if isinstance(v, str):
                               parts.append(v)
        return "\n".join(parts)

    def evaluate(self, generated_repo_data: Dict[str, Any], raw_readme: str) -> Dict[str, Any]:
        """
        Evaluates the generated repository data and injects indexing metadata.
        """
        score = 100
        report = { "metrics": {}, "flags": {}, "warnings": [] }
        
        # We need to evaluate the generated text content.
        # It's currently structured as JSON fields in 'content'.
        text_body_raw = self._extract_full_body_text(generated_repo_data)
        text_body = self._strip_markdown_and_html(text_body_raw)
        
        # 1. content length check
        length = len(text_body)
        report["metrics"]["content_length"] = length
        if length < 800:
            score -= 50
            report["warnings"].append(f"文字数が極端に不足しています({length}字, 800字未満)。")
        elif length < 1500:
            score -= 20
        
        # 2. Duplicate check (Title & Body similarity)
        title = generated_repo_data.get("seo_metadata", {}).get("title", "")
        if title in self.analysis_db["existing_titles"]:
            score -= 50
            report["flags"]["is_title_duplicate"] = True
            report["warnings"].append("Titleが既存ページと完全に重複しています。")
        else:
            report["flags"]["is_title_duplicate"] = False
            if title:
                self.analysis_db["existing_titles"].add(title)

        # For MVP, we skip same_topic vs all_repos differentiation if we just maintain one big list of generated bodies
        # But we will implement the logic.
        max_sim_all_repos = self._get_max_similarity(text_body, self.analysis_db["all_repo_bodies"])
        
        if max_sim_all_repos > 0.80:
            score -= 40
            report["warnings"].append(f"サイト内の他の記事と非常に類似しています(>{max_sim_all_repos*100:.1f}%)。")
        # Store for future checks
        if text_body:
             self.analysis_db["all_repo_bodies"].append(text_body)

        # 3. README similarity
        readme_clean = self._strip_markdown_and_html(raw_readme)
        similarity = self._calculate_str_similarity(text_body, readme_clean)
        report["metrics"]["readme_similarity"] = similarity
        if similarity > 0.80:
            score -= 40
            report["warnings"].append(f"READMEとの類似度が高く、コピペ・焼き直しの疑いがあります({similarity*100:.1f}%)。")
        elif similarity >= 0.50:
            score -= 15
            report["warnings"].append(f"READMEの直訳になっている可能性があります({similarity*100:.1f}%)。")
        elif similarity < 0.10:
             # In small mock cases where README is 'Mock README', similarity is 0. 
             # We only deduct if README actually had content, else we penalize unrightfully.
            if len(readme_clean) > 50:
                 score -= 30
                 report["warnings"].append(f"READMEの内容がほとんど反映されていません(ハルシネーション疑惑、{similarity*100:.1f}%)。")

        # 4. Dependency / Tech Stack Check
        # For simplicity in generator MVP, these are not fully extracted from package.json yet but let's check primary_language and related_topics
        tech_stack = [generated_repo_data.get("primary_topic", "")] + generated_repo_data.get("related_topics", []) + generated_repo_data.get("related_languages", [])
        tech_stack = [t.lower() for t in tech_stack if t]
        
        mentioned_techs = [tech for tech in tech_stack if tech and tech in text_body_raw.lower()]
        report["metrics"]["dependencies_mentioned"] = mentioned_techs
        if len(tech_stack) > 0:
            if len(mentioned_techs) == 0:
                score -= 20
                report["warnings"].append("技術スタック（言語・トピック）への言及が皆無です。")
            elif len(mentioned_techs) >= 2:
                score += 10 # Bonus
                
        # 5. Required Sections (Schema Fields) Missing
        content_obj = generated_repo_data.get("content", {})
        
        required_fields = [
            "what_it_does",
            "key_features",
            "architecture_overview",
            "how_to_run",
            "use_cases",
            "alternatives"
        ]
        
        missing = []
        for field in required_fields:
            sec_val = content_obj.get(field)
            if not sec_val or (isinstance(sec_val, list) and len(sec_val) == 0):
                missing.append(field)
                
        if len(missing) >= 2:
            score -= (len(missing) * 15)
            report["flags"]["missing_sections"] = missing
            report["warnings"].append(f"必須フィールドが{len(missing)}個欠落しています ({', '.join(missing)})。")
        else:
             report["flags"]["missing_sections"] = []

        # Calculate final score
        final_score = max(0, min(100, score))
        report["quality_score"] = final_score
        
        if final_score >= 80:
            report["action"] = "INDEX"
        elif final_score >= 50:
            report["action"] = "NOINDEX"
        else:
            report["action"] = "SKIP_AND_REGENERATE"

        # Apply to the original data object
        generated_repo_data["quality_score"] = final_score
        generated_repo_data["warnings"] = report["warnings"]
        generated_repo_data["flags"] = report["flags"]
        
        is_indexable = report["action"] == "INDEX"
        reason = "quality_ok"
        if report["action"] == "NOINDEX":
            reason = "mediocre_quality_noindex"
        elif report["action"] == "SKIP_AND_REGENERATE":
            reason = "low_quality_skip"
            
        generated_repo_data["indexing"] = {
            "is_indexable": is_indexable,
            "reason": reason
        }

        import datetime
        # Keep a copy of the evaluation report for our global reports
        self.last_report = {
             "repo_name": generated_repo_data.get("id"),
             "generation_id": f"gen_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{final_score}",
             "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
             "quality_score": final_score,
             "action": report["action"],
             "metrics": report["metrics"],
             "flags": report["flags"],
             "warnings": report["warnings"]
        }
        
        return generated_repo_data

    def get_last_report(self) -> Dict[str, Any]:
         return self.last_report
