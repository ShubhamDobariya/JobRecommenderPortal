import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import time


def extract_keywords_from_resume(resume_text, top_k=5):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
    tfidf = vectorizer.fit_transform([resume_text])
    scores = zip(vectorizer.get_feature_names_out(), tfidf.toarray()[0])
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_keywords[:top_k]]


def fetch_jobs_from_jsearch(query):
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": query, "page": "1", "num_pages": "1"}
    url = "https://jsearch.p.rapidapi.com/search"

    jobs = []

    for attempt in range(2):  # Try 2 times
        try:
            print(f"Fetching jobs for query: {query} (Attempt {attempt+1})")
            response = requests.get(url, headers=headers, params=params, timeout=20)

            if response.status_code == 200:
                data = response.json()
                print(f"Jobs found: {len(data.get('data', []))}")
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
                return jobs  # ✅ Successful return
            else:
                print(f"API Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            print("⏳ Request timed out.")
            time.sleep(1)  # Wait and retry

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

    # 🛠️ Fallback if both attempts fail
    print("❗ Using fallback job list.")
    return get_sample_jobs()


def get_sample_jobs():
    """Return sample jobs when API is not available"""
    return [
        {
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "apply_url": "https://example.com/apply",
            "job_text": "Python developer with experience in web development",
        },
        {
            "title": "Software Engineer",
            "company": "StartUp Inc",
            "location": "New York",
            "apply_url": "https://example.com/apply2",
            "job_text": "Full stack software engineer position",
        },
        {
            "title": "Data Analyst",
            "company": "Data Solutions",
            "location": "California",
            "apply_url": "https://example.com/apply3",
            "job_text": "Data analyst with Python and SQL skills",
        },
    ]


def recommend_jobs(resume_text, top_n=5):
    keywords = extract_keywords_from_resume(resume_text)
    keywords = [
        kw
        for kw in keywords
        if len(kw) > 3 and kw.lower() not in ["data", "event", "end", "web"]
    ]
    query = " ".join(keywords) if keywords else "python developer"

    jobs = fetch_jobs_from_jsearch(query)
    if not jobs:
        return []

    documents = [resume_text] + [job["job_text"] for job in jobs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    for i, job in enumerate(jobs):
        job["score"] = round(float(similarities[i]) * 100, 2)

    return sorted(jobs, key=lambda x: x["score"], reverse=True)[:top_n]
