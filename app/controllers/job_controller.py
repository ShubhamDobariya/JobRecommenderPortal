import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_keywords_from_resume(resume_text, top_k=5):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
    tfidf = vectorizer.fit_transform([resume_text])
    scores = zip(vectorizer.get_feature_names_out(), tfidf.toarray()[0])
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_keywords[:top_k]]


def fetch_jobs_from_jsearch(query):
    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": query, "page": "1", "num_pages": "1"}
    url = "https://jsearch.p.rapidapi.com/search"
    response = requests.get(url, headers=headers, params=params)

    jobs = []
    if response.status_code == 200:
        for job in response.json().get("data", []):
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
