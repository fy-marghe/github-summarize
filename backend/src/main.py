import os
from dotenv import load_dotenv
from crawler.github_fetcher import GithubFetcher
from generator.llm_generator import LLMGenerator
from checker.quality_checker import QualityChecker
from exporter.json_exporter import JsonExporter

load_dotenv()

def main():
    print("Starting GitHub SEO Pipeline MVP...")
    
    # 1. Target Discovery (Mock list for MVP)
    targets = [
        {"owner": "langchain-ai", "repo": "langchain"},
        {"owner": "tiangolo", "repo": "fastapi"},
        {"owner": "huggingface", "repo": "transformers"},
        {"owner": "pytorch", "repo": "pytorch"},
        {"owner": "scikit-learn", "repo": "scikit-learn"},
        {"owner": "run-llama", "repo": "llama_index"},
        {"owner": "ray-project", "repo": "ray"},
        {"owner": "mlflow", "repo": "mlflow"},
        {"owner": "PrefectHQ", "repo": "prefect"},
        {"owner": "apache", "repo": "airflow"},
        {"owner": "vercel", "repo": "ai"}
    ]
    
    # Initialize modules
    fetcher = GithubFetcher()
    generator = LLMGenerator()
    checker = QualityChecker()
    exporter = JsonExporter()
    
    # Store global quality reports
    all_reports = []

    for target in targets:
        try:
            # 2. Scraper
            repo_data = fetcher.fetch_all(target["owner"], target["repo"])
            
            # 3. Generator
            generated_data = generator.generate_content(repo_data)
            
            # 4. Quality Checker
            checked_data = checker.evaluate(generated_data, repo_data["readme"])
            
            last_report = checker.get_last_report()
            if last_report:
                all_reports.append(last_report)
            
            # Check action rule
            action = last_report.get("action", "INDEX")
            
            if action == "SKIP_AND_REGENERATE":
                print(f"Skipping export for {target['owner']}/{target['repo']} due to SKIP_AND_REGENERATE action (Score: {last_report.get('quality_score')}).")
                # Remove from generator's topic/lang aggregations to prevent it showing up in topics
                generator.remove_repo_from_aggregations(checked_data["slug"])
                continue
            
            # 5. Exporter (for INDEX and NOINDEX, we still export the JSON)
            exporter.export_repo(checked_data)
            
            if action == "NOINDEX":
                 print(f"Exported {target['owner']}/{target['repo']} but marked as NOINDEX (Score: {last_report.get('quality_score')}).")
                
        except Exception as e:
            import traceback
            print(f"Error processing {target['owner']}/{target['repo']}:")
            traceback.print_exc()

    # Export Quality Reports
    exporter.export_quality_reports(all_reports)

    # After all targets are processed, generate and export topic and language JSONs
    # Note: Skipped repos were removed from aggregations, NOINDEX ones are included to allow site navigation.
    topics_data = generator.generate_topics_data()
    for topic in topics_data:
        exporter.export_topic(topic)
        
    languages_data = generator.generate_languages_data()
    for lang in languages_data:
        exporter.export_language(lang)

    print("Pipeline execution completed.")

if __name__ == "__main__":
    main()
