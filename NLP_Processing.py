import spacy
from sentence_transformers import SentenceTransformer
import re
import json

nlp = spacy.load("en_core_web_sm")

embedder = SentenceTransformer('all-MiniLM-L6-v2')

skill_Keywords: dict[str, list[str]] = {
    "Python": ["python", "py"],
    "Data Analysis": ["data analysis", "data analytics", "data scientist"],
    "Machine Learning": ["machine learning", "ml", "artificial intelligence", "ai"],
    "Web Development": ["web development", "frontend", "backend", "fullstack", "html", "css", "javascript"],
    "Cloud Computing": ["cloud computing", "aws", "azure", "gcp", "cloud services"],
    "Cybersecurity": ["cybersecurity", "information security", "infosec", "network security"],
    "Project Management": ["project management", "pm", "agile", "scrum", "kanban"],
    "DevOps": ["devops", "continuous integration", "continuous deployment", "ci/cd"],
    "Deep Learning": ["deep learning", "neural networks", "dl"],
    "Data Visualization": ["data visualization", "data viz", "tableau", "power bi", "d3.js"],
    "GenAI": ["generative ai", "genai", "gpt", "dall-e", "midjourney"], 
    "Natural Language Processing": ["natural language processing", "nlp", "text mining", "sentiment analysis"]
}

def extract_skills_from_text(text: str) -> list[str]:
    text = text.lower()
    found_skills = set()
    for skill, keywords in skill_Keywords.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                found_skills.add(skill)
                break
    return list(found_skills)

def clean_text(text: str) -> str:
    doc = nlp(text)
    cleaned_tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(cleaned_tokens)

def preprocess_user_profile(user_json):
    raw = user_json["raw_text"]

    cleaned = clean_text(raw)
    extracted = extract_skills_from_text(cleaned)
    embedding = embedder.encode(cleaned).tolist()
    return {
        "cleaned_text": cleaned,
        "extracted_skills": extract_skills_from_text(cleaned),
        "embedding": embedding,
        "original_data": user_json
    }

if __name__ == "__main__":
    with open("user_data_GPT.json") as f:
        sample = json.load(f)

    output = preprocess_user_profile(sample)
    print(output)
