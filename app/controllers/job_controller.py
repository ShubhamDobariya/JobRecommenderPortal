import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from functools import lru_cache
import asyncio
import aiohttp

# import httpx


# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Fallback TF-IDF keyword extractor
def extract_keywords_tfidf(resume_text: str, top_k=10):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
    tfidf = vectorizer.fit_transform([resume_text])
    scores = zip(vectorizer.get_feature_names_out(), tfidf.toarray()[0])
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_keywords[:top_k]]


# Gemini-powered keyword extractor (non-cached core logic)
def extract_text_from_resume(resume_text: str, top_k=5):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        prompt = f"""
        You are a resume parsing expert helping extract **only the most relevant keywords** from resumes to match with job listings.

        Given the resume below, extract exactly {top_k} focused keywords that best represent the candidate's:
        - Job roles or career titles (e.g., Software Engineer, Data Analyst)
        - Programming languages (e.g., Python, JavaScript)
        - Technical skills and tools (e.g., ReactJS, MongoDB, Power BI)

        🛑 Avoid generic/soft terms like 'developed', 'team', 'application', 'experience', 'project', or anything vague or unrelated to job listings.

        ✅ Output must be a **clean, comma-separated list of only {top_k} most relevant keywords** — suitable for a job search query.

        Resume:
        \"\"\" 
        {resume_text[:3000]}
        \"\"\"
        """

        response = model.generate_content(prompt)
        output = response.text.strip()

        keywords = [
            kw.strip().lower()
            for kw in output.replace("\n", "").split(",")
            if len(kw.strip()) > 2
        ]

        return list(dict.fromkeys(keywords))[:top_k]

    except Exception as e:
        print(f"Gemini keyword extraction failed: {e}")
        return extract_keywords_tfidf(resume_text, top_k)


# Cached Gemini keyword extractor
@lru_cache(maxsize=100)
def extract_keywords_from_resume(resume_text: str, top_k: int = 10):
    return extract_text_from_resume(resume_text, top_k)


async def fetch_jobs_from_jsearch(query):
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": query, "page": "1", "num_pages": "1"}
    url = "https://jsearch.p.rapidapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, params=params, timeout=15
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = []
                    for job in data.get("data", []):
                        title = job.get("job_title", "")
                        description = job.get("job_description", "")
                        skills = (
                            " ".join(job.get("job_required_skills", []))
                            if job.get("job_required_skills")
                            else ""
                        )
                        combined_text = f"{title} {description} {skills}"
                        jobs.append(
                            {
                                "title": title,
                                "company": job.get("employer_name", ""),
                                "location": job.get("job_city", "Remote"),
                                "apply_url": job.get("job_apply_link", ""),
                                "job_text": combined_text,
                            }
                        )
                    return jobs
                else:
                    print(f"API Error: {response.status}")
    except Exception as e:
        print(f"Fetch error for query '{query}': {e}")

    return []  # fallback empty


async def recommend_jobs(resume_text, top_n=10):
    keywords = extract_keywords_from_resume(resume_text, top_k=5)

    keywords = [
        kw
        for kw in keywords
        if len(kw) > 3 and kw.lower() not in ["data", "event", "end", "web"]
    ]
    print("keywords:", keywords)

    # Fetch all jobs in parallel
    tasks = [fetch_jobs_from_jsearch(kw) for kw in keywords]
    all_results = await asyncio.gather(*tasks)

    # Flatten and deduplicate
    all_jobs = []
    seen = set()
    for job_list in all_results:
        for job in job_list:
            if job["apply_url"] not in seen:
                seen.add(job["apply_url"])
                all_jobs.append(job)

    if not all_jobs:
        return []

    # Vectorize and rank
    documents = [resume_text] + [job["job_text"] for job in all_jobs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    for i, job in enumerate(all_jobs):
        job["score"] = round(float(similarities[i]) * 100, 2)

    return sorted(all_jobs, key=lambda x: x["score"], reverse=True)[:top_n]
