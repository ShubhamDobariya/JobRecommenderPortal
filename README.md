# Job Recommender Portal

A modern web application that helps users find personalized job recommendations by uploading their resume. Built with FastAPI, MongoDB, and Bootstrap.

---

## Features

- **User Authentication:** Secure sign up, login, and logout.
- **Resume Upload:** Upload your resume in PDF or DOCX format.
- **AI-Powered Resume Parsing:** Extracts relevant skills and keywords using Google Gemini AI (or TF-IDF fallback).
- **Job Recommendations:** Matches your skills to real job listings using the JSearch API (or other job APIs).
- **Job Application:** View job details and apply directly from the portal.
- **Resume Update:** Update your resume anytime to get new recommendations.
- **Responsive UI:** Clean, modern interface with Bootstrap and custom CSS.
- **Cloud Storage:** Resumes are stored securely using Cloudinary.
- **MongoDB Database:** Stores user data and resume information.

---

## Screenshots

<!-- Add screenshots of your app here if available -->

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/JobRecommenderPortal.git
cd JobRecommenderPortal
```

### 2. Set Up the Virtual Environment

```bash
python -m venv Jobvenv
Jobvenv\Scripts\activate  # On Windows
# Or
source Jobvenv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add:

```
MONGO_URI=your_mongodb_uri
DATABASE_NAME=your_db_name
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# JSearch API (or your job API)
RAPIDAPI_KEY=your_rapidapi_key
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Project Structure

```
app/
  controllers/        # Business logic (auth, job, resume parsing)
  core/               # Config, DB, security, cloudinary
  routes/             # FastAPI route definitions
  schemas/            # Pydantic schemas
  static/             # CSS, JS, images
  templates/          # Jinja2 HTML templates
  main.py             # FastAPI app entry point
requirements.txt
run.py
```

---

## Deployment

- You can deploy this app for free on [Render.com](https://render.com/), [Railway](https://railway.app/), or similar platforms.
- For production, serve static files with a CDN or web server (e.g., Nginx).

---

## Credits

- [FastAPI](https://fastapi.tiangolo.com/)
- [MongoDB](https://www.mongodb.com/)
- [Cloudinary](https://cloudinary.com/)
- [Bootstrap](https://getbootstrap.com/)
- [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- [Google Gemini AI](https://ai.google.dev/)

---

## License

MIT License

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## Contact

For questions or support, open an issue or contact [your email/contact info]. 
