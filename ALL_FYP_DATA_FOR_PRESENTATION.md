# FairHire FYP - Complete Presentation and Defense Data

## 1. Project Title
FairHire - AI-Powered Recruitment and Candidate Matching System

## 2. Project Type
Final Year Project / Capstone Project

## 3. Domain
Recruitment, HR Management, AI-Based Matching, Web and Mobile Application

## 4. Problem Statement
Traditional recruitment processes are slow, manual, and inconsistent. HR managers receive a large number of resumes, but manually reviewing each one is time consuming and prone to human error. Recruiters often struggle to compare candidate skills with job requirements efficiently. This leads to delays in hiring, missed talent, and poor decision-making.

Our project solves this problem by providing an intelligent recruitment platform where resumes are uploaded, parsed, and matched against job requirements automatically.

## 5. Motivation
The motivation behind this project is to reduce the time and effort required for hiring while improving decision quality. Recruitment is a critical process for organizations, and an automated system can improve accuracy, consistency, and speed.

## 6. Objectives
- To automate the resume screening process
- To extract key candidate information from resumes
- To create and manage job requirements
- To match candidates with appropriate jobs using intelligent scoring
- To reduce manual workload for HR managers
- To provide a dashboard for candidate tracking and shortlist decisions
- To improve the quality and speed of recruitment

## 7. Scope
The project covers the following modules:
- User authentication and profile management
- Resume upload and parsing
- Candidate detail management
- Job creation and management
- Candidate-job matching
- Dashboard analytics
- Candidate status updates
- API-based communication between frontend and backend

## 8. Project Significance
This project is significant because it addresses a realistic and valuable business problem. It helps organizations make hiring decisions faster and more effectively using data-driven matching.

## 9. Technologies Used

### Frontend
- Flutter
- Dart

### Backend
- Python
- Django
- Django REST Framework

### Database
- MySQL / Django ORM

### Additional Tools
- JWT Authentication
- CORS for cross-origin API access
- REST API integration

## 10. System Architecture
The project follows a layered architecture:

1. Frontend Layer
   - Flutter application
   - HR user interface for login, dashboard, resume upload, job management, and match results

2. Backend Layer
   - Django REST Framework
   - Handles API requests, business logic, validation, and authentication

3. Database Layer
   - Stores HR data, jobs, candidates, candidate scores, and recruitment decisions

4. Matching Engine
   - Compares candidate skills with job requirements
   - Calculates score based on relevant factors

## 11. Functional Modules

### a) Authentication Module
- User registration
- Login and logout
- JWT token generation
- Profile access
- FCM token support for push notifications

### b) Resume Management Module
- Resume upload
- Supported formats: PDF, DOCX, TXT
- Resume parsing
- Extraction of name, email, education, skills, experience, projects, and work history
- Candidate detail retrieval

### c) Job Management Module
- Create jobs
- Update jobs
- Delete jobs
- Add required and optional skills
- Set required experience and education level
- Set salary details and matching weights

### d) Matching Module
- Compare candidate profile with job requirements
- Score candidate based on skill fit, experience, and education
- Rank candidates according to match percentage
- Return results to frontend dashboard

### e) Dashboard Module
- Total CVs count
- Shortlisted candidates
- Accepted candidates
- Rejected candidates
- Pending applications
- Candidate status tracking

## 12. Workflow of the System
1. HR manager logs in.
2. HR creates a job requirement.
3. Candidate resumes are uploaded.
4. Resume content is parsed and structured.
5. Candidate data is stored in the database.
6. Matching engine compares candidate data with job requirements.
7. Candidates are ranked based on match score.
8. HR reviews candidates and updates their status.
9. Results and insights are displayed on the dashboard.

## 12.1 Resume Parsing Engine: How the CV Upload Process Works
The resume parsing engine is the core intelligence layer of the system. It transforms unstructured CV text into clean, structured candidate data that can be used for job matching.

### Step-by-step flow
1. Candidate uploads a resume in PDF, DOCX, or TXT format.
2. The system validates the uploaded file type and, if needed, checks the file signature to detect the real format even when the extension is missing or incorrect.
3. The parser reads the file and extracts raw text content.
4. The extracted content is split into sections such as Experience, Education, Skills, Projects, Languages, Certifications, and Awards.
5. Section-based parsing is important because it prevents incorrect extraction. For example, education details are not counted as work experience, and skills are not confused with project descriptions.
6. The system then extracts meaningful data, including candidate name, email, phone number, skills, education level, experience years, projects, certifications, awards, and work history.
7. The extracted data is normalized and standardized. Common variations such as "React JS", "NodeJS", and "Django REST Framework" are mapped to consistent skill names.
8. The parsed profile is saved to the database and made available for the matching engine.

### Why the parsing engine is effective
- It handles multiple resume formats.
- It works with both structured and unstructured CV text.
- It reduces human error in manual screening.
- It improves the accuracy of candidate data before matching.
- It supports both AI-assisted parsing and traditional rule-based backup systems.

### AI and rule-based hybrid approach
The parser uses a hybrid model:
- Primary attempt: AI-based extraction using LLM support if a Gemini API key is configured.
- Backup mechanism: Rule-based parsing using regex patterns, NLP, and section detection.

This ensures the system remains reliable even if AI services are unavailable. The fallback design makes FairHire robust and production-friendly.

## 12.2 Complete AI Matching Engine Workflow
Once the candidate profile is created, the AI matching engine starts the ranking process.

### Matching process
1. A job is created with required skills, optional skills, minimum experience, education level, and weights.
2. The candidate profile is compared against the job description.
3. Skill matching is calculated by checking how many required and optional skills the candidate has.
4. Experience matching compares the candidate's total years of experience with the job requirement.
5. Education matching compares the candidate's education rank with the required education level.
6. A similarity score is computed using TF-IDF and cosine similarity to compare the candidate's CV text with the job description.
7. Final score is generated using weighted formulas:
  - Skill score: 50%
  - Experience score: 30%
  - Education score: 20%
8. The result is ranked from the strongest to weakest match.
9. The system generates an explanation such as: which skills matched, which skills were missing, and why the candidate received that final score.

### Example formula
Final Score = (Skill Score × Skill Weight) + (Experience Score × Experience Weight) + (Education Score × Education Weight)

This helps HR managers not only see who ranked highest, but also understand why a candidate is recommended.

### Transparency feature
One of the strongest features of the project is the explanation layer. Instead of showing only a percentage, the engine provides a reasoned breakdown:
- matched skills
- missing skills
- experience adequacy
- education suitability
- overall match result

This makes the decision process more understandable and trustworthy for recruiters.

### Real project value
This end-to-end process reduces manual resume screening, speeds recruitment decisions, and improves hiring quality. In real-world recruitment, companies receive hundreds of CVs for one position. FairHire helps filter and rank candidates quickly based on objective, data-driven evaluation.

## 13. Matching Logic
The matching logic evaluates candidates against a job using weighted criteria:
- Skill match
- Experience match
- Education match

Example weight distribution:
- Skill weight: 0.5
- Experience weight: 0.3
- Education weight: 0.2

The total must sum to 1.0. The system calculates a final score and ranks candidates from strongest to weakest match.

## 14. Key Features
- Resume upload and parsing
- Automated candidate data extraction
- HR dashboard
- Candidate profile viewing
- Job creation and management
- Candidate-job matching
- Score-based ranking
- Candidate status updates
- Secure access using JWT
- API-driven frontend-backend integration

## 15. Benefits of the System
- Saves time in the hiring process
- Reduces manual resume screening effort
- Improves candidate-job matching quality
- Makes recruitment more consistent and objective
- Provides transparent score explanations
- Helps HR managers make informed decisions
- Reduces administrative burden

## 16. Problems Encountered During Development
During development, some challenges were faced:
- Different resume formats and unstructured text
- Inconsistent data extraction from resumes
- Need to align frontend and backend API payloads
- Matching logic validation and weight consistency
- Ensuring secure access and valid authentication

These challenges were solved through data standardization, validation rules, API contract alignment, and careful backend logic implementation.

## 17. Impact of the Project
The project has practical value for real-world recruitment scenarios. It helps organizations reduce hiring delays and become more efficient in candidate selection.

## 18. Future Enhancements
- Advanced NLP-based resume parsing
- Better candidate recommendation engine
- Interview scheduling module
- Real-time notifications
- More detailed analytics dashboard
- Cloud deployment
- Candidate recommendation to job seekers

## 19. Conclusion
FairHire is designed to make recruitment more efficient, objective, and intelligent. It combines modern frontend technology, secure backend architecture, and automated candidate matching to solve a real business problem. The project demonstrates practical software development skills and provides a strong foundation for future expansion.

---

# API Contract Summary for Frontend

## Base URL
Production:
https://recruitiq-backend-production-d702.up.railway.app/api/v1

Local:
http://localhost:8000/api/v1

## Authentication Endpoints

### Register
POST /api/v1/auth/register/
Request JSON:
{
  "name": "Umair",
  "email": "umair@company.com",
  "password": "password123"
}

Response:
{
  "user": {
    "id": 1,
    "name": "Umair",
    "email": "umair@company.com",
    "role": "hr_manager",
    "created_at": "2026-09-23T10:00:00Z"
  },
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN",
  "message": "Account created successfully."
}

### Login
POST /api/v1/auth/login/
Request JSON:
{
  "email": "umair@company.com",
  "password": "password123",
  "fcm_token": "optional-device-token"
}

Response:
{
  "user": {
    "id": 1,
    "name": "Umair",
    "email": "umair@company.com",
    "role": "hr_manager",
    "created_at": "2026-09-23T10:00:00Z"
  },
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN",
  "message": "Login successful."
}

### Logout
POST /api/v1/auth/logout/
Request JSON:
{
  "refresh": "JWT_REFRESH_TOKEN"
}

### Get Profile
GET /api/v1/auth/profile/

### Update FCM Token
PATCH /api/v1/auth/update-fcm/
Request JSON:
{
  "fcm_token": "new-device-token"
}

### Refresh Access Token
POST /api/v1/auth/token/refresh/
Request JSON:
{
  "refresh": "JWT_REFRESH_TOKEN"
}

## Resume Endpoints

### List Candidates
GET /api/v1/resumes/
Optional filter:
GET /api/v1/resumes/?status=shortlisted

Response example:
{
  "count": 1,
  "candidates": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "experience_years": 4.5,
      "education_level": "BSc / BE",
      "skills": ["Flutter", "Dart", "Firebase"],
      "match_score": 87.5,
      "status": "shortlisted",
      "created_at": "2026-09-23T10:00:00Z"
    }
  ]
}

### Upload Resume
POST /api/v1/resumes/upload/
Form-data field: file

Example response:
{
  "message": "Resume parsed successfully.",
  "candidate": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+923001234567",
    "location": "Lahore",
    "education": "BSc Computer Science",
    "education_level": "BSc / BE",
    "experience_years": 4.5,
    "skills": ["Flutter", "Dart", "Firebase"],
    "languages": ["English", "Urdu"],
    "projects": [
      { "name": "FairHire App", "description": "Recruitment platform" }
    ],
    "certifications": ["AWS Certified"],
    "awards": ["Best Intern 2022"],
    "work_history": [
      { "company": "ABC Tech", "role": "Flutter Developer", "duration": "2022 - 2024" }
    ],
    "match_score": null,
    "status": "pending",
    "hr_notes": "",
    "original_name": "john_resume.pdf",
    "created_at": "2026-09-23T10:00:00Z",
    "resume_file_url": "https://backend-url/api/v1/resumes/1/download/"
  }
}

### Get Candidate Detail
GET /api/v1/resumes/{candidate_id}/

### Update Candidate Status
PATCH /api/v1/resumes/{candidate_id}/status/
Request JSON:
{
  "status": "accepted",
  "hr_notes": "Good candidate"
}

Valid statuses:
- pending
- shortlisted
- accepted
- rejected
- on_hold

### Resume Stats
GET /api/v1/resumes/stats/
Response:
{
  "total_cvs": 10,
  "shortlisted": 3,
  "accepted": 2,
  "rejected": 1,
  "pending": 4,
  "on_hold": 0
}

### Download Resume
GET /api/v1/resumes/{candidate_id}/download/

## Job Endpoints

### List Jobs
GET /api/v1/jobs/

### Create Job
POST /api/v1/jobs/
Request JSON:
{
  "title": "Flutter Developer",
  "department": "Mobile",
  "location": "Lahore",
  "job_type": "full_time",
  "required_skills": ["Flutter", "Dart"],
  "optional_skills": ["Firebase"],
  "min_experience": 2,
  "education_level": "BSc / BE",
  "salary_min": 80000,
  "salary_max": 120000,
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2
}

### Update Job
PUT /api/v1/jobs/{job_id}/

### Delete Job
DELETE /api/v1/jobs/{job_id}/

## Matching Endpoints

### Match Candidates
POST /api/v1/matching/
Option A with saved job:
{
  "job_id": 1
}

Option B inline job:
{
  "title": "Flutter Dev",
  "required_skills": ["Flutter", "Dart"],
  "optional_skills": ["Python"],
  "min_experience": 2,
  "education_level": "BSc / BE",
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2
}

Response:
{
  "message": "Matched 10 candidates.",
  "stats": {
    "total": 10,
    "good_match": 4,
    "partial": 3,
    "no_match": 3
  },
  "results": [
    {
      "candidate_id": 1,
      "candidate_name": "John Doe",
      "email": "john@example.com",
      "experience_years": 4.5,
      "education_level": "BSc / BE",
      "skills": ["Flutter", "Dart", "Firebase"],
      "final_score": 87.5,
      "skill_score": 90.0,
      "experience_score": 80.0,
      "education_score": 85.0,
      "missing_skills": ["Node.js"],
      "explanation": "Strong mobile skillset with minor gap in backend stack.",
      "status": "shortlisted"
    }
  ]
}

### Match Results
GET /api/v1/matching/results/

---

# External Defense Q&A / Short Answers

## Q: What is your project about?
A: FairHire is an AI-powered recruitment and candidate matching system designed to help HR managers manage resumes, jobs, and candidate screening more efficiently.

## Q: What problem does it solve?
A: It reduces manual resume screening time and helps HR teams match candidates based on skills and experience more accurately.

## Q: Why is the project useful?
A: It saves time, improves hiring quality, reduces workload, and makes recruitment more data-driven and objective.

## Q: What are the technologies used?
A: Flutter for frontend, Django REST Framework for backend, and MySQL for database storage.

## Q: What was the main challenge?
A: Extracting structured data from different resume formats and coordinating frontend-backend data contracts.

## Q: How does the matching work?
A: It compares candidates against job requirements using weighted scores for skills, experience, and education.

## Q: Is the project scalable?
A: Yes, the architecture is modular and can be extended with better AI, analytics, notifications, and deployment features.

## Q: What are your future improvements?
A: NLP-based resume parsing, improved recommendation engine, analytics, and cloud deployment.

## Q: How is your project different from a traditional app?
A: It combines recruitment logic, matching intelligence, and dashboard analytics, not just CRUD operations.

## Q: How did you ensure security?
A: JWT authentication and protected endpoints were used to ensure authorized access only.

## Q: What did you learn?
A: I learned full-stack development, API integration, backend logic, validation, and how to build a practical system that solves a real-world problem.

---

# Final External Defense Speech (Short)

“My project, FairHire, is an AI-powered recruitment and matching system designed to help HR managers manage resumes and jobs more efficiently. The system allows recruiters to upload resumes, extract candidate details, create job requirements, and match applicants with suitable jobs based on skills, education, and experience. It reduces manual effort, improves consistency, and speeds up the hiring process.

The frontend is built with Flutter, while the backend is built using Django REST Framework. The system uses a scoring model to rank candidates based on relevant job criteria. This project addresses a real-world business problem and shows practical application of software engineering, API development, and intelligent data processing.

The main challenges involved resume parsing and integration between frontend and backend. These were addressed through validation, structured data handling, and consistent API design. In the future, this system can be expanded with more advanced AI, notifications, analytics, and better recruitment automation.

Overall, this project is useful, practical, and scalable, and it demonstrates a complete end-to-end solution for modern recruitment management.”

---

# Final Presentation Tips
- Keep your answer practical and real-world.
- Show how the project helps people and organizations.
- Explain the workflow clearly.
- Speak confidently and simply.
- Prepare to answer questions on architecture, data flow, challenges, and future work.
- Show that your project is useful beyond just a classroom assignment.

---

# Best One-Line Summary for Your Presentation
FairHire is a smart recruitment platform that helps HR managers automate resume review, match candidates with jobs, and make faster and more informed hiring decisions.
