import fs from "fs";
import path from "path";

const REPOS_DIR = path.join(process.cwd(), "content", "repos");
const TOPICS_DIR = path.join(process.cwd(), "content", "topics");
const LANGUAGES_DIR = path.join(process.cwd(), "content", "languages");

export async function getRepoData(owner: string, repo: string) {
  const filePath = path.join(REPOS_DIR, `${owner}__${repo}.json`);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export async function getAllRepos() {
  if (!fs.existsSync(REPOS_DIR)) return [];
  const files = fs.readdirSync(REPOS_DIR).filter(file => file.endsWith(".json"));
  return files.map(file => {
    const [owner, ...rest] = file.replace('.json', '').split('__');
    return { owner, repo: rest.join('__') };
  });
}

export async function getTopicData(topic: string) {
  const filePath = path.join(TOPICS_DIR, `${topic}.json`);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export async function getAllTopics() {
  if (!fs.existsSync(TOPICS_DIR)) return [];
  const files = fs.readdirSync(TOPICS_DIR).filter(file => file.endsWith(".json"));
  return files.map(file => ({ topic: file.replace('.json', '') }));
}

export async function getLanguageData(language: string) {
  const filePath = path.join(LANGUAGES_DIR, `${language}.json`);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export async function getAllLanguages() {
  if (!fs.existsSync(LANGUAGES_DIR)) return [];
  const files = fs.readdirSync(LANGUAGES_DIR).filter(file => file.endsWith(".json"));
  return files.map(file => ({ language: file.replace('.json', '') }));
}
