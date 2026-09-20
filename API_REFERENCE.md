# FairHire API Reference

## Base URL

```text
https://recruitiq-backend-production-d702.up.railway.app/api/v1
```

Protected endpoints require:

```http
Authorization: Bearer ACCESS_TOKEN
```

## Authentication

### Register

```http
POST /auth/register/
Content-Type: application/json
```

```json
{
  "name": "Umair",
  "email": "umair@company.com",
  "password": "password123"
}
```

### Login

```http
POST /auth/login/
Content-Type: application/json
```

```json
{
  "email": "umair@company.com",
  "password": "password123",
  "fcm_token": "optional-device-token"
}
```

Register and login return:

```json
{
  "user": {},
  "access": "ACCESS_TOKEN",
  "refresh": "REFRESH_TOKEN",
  "message": "..."
}
```

### Logout

```http
POST /auth/logout/
Authorization: Bearer ACCESS_TOKEN
```

```json
{
  "refresh": "REFRESH_TOKEN"
}
```

### Get Profile

```http
GET /auth/profile/
Authorization: Bearer ACCESS_TOKEN
```

### Update FCM Token

```http
PATCH /auth/update-fcm/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

```json
{
  "fcm_token": "NEW_DEVICE_TOKEN"
}
```

### Refresh Access Token

```http
POST /auth/token/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "REFRESH_TOKEN"
}
```

## Candidates and Resumes

### List Candidates

```http
GET /resumes/
GET /resumes/?status=shortlisted
Authorization: Bearer ACCESS_TOKEN
```

Response:

```json
{
  "count": 1,
  "candidates": []
}
```

### Upload Resume

```http
POST /resumes/upload/
Authorization: Bearer ACCESS_TOKEN
Content-Type: multipart/form-data
```

Multipart field:

```text
file = resume.pdf | resume.docx | resume.doc | resume.txt
```

Response:

```json
{
  "message": "Resume parsed successfully.",
  "candidate": {}
}
```

### Get Complete Candidate Detail

```http
GET /resumes/{candidate_id}/
Authorization: Bearer ACCESS_TOKEN
```

The candidate object can contain:

```text
id
name
email
phone
location
education
education_level
experience_years
skills
technical_skills
languages
projects
certifications
awards
work_history / work_experience
additional_information
match_score
skill_score
experience_score
education_score
missing_skills
score_explanation
status
hr_notes
original_name
created_at
resume_file_url
```

Render all returned arrays dynamically. Do not use fixed indexes or truncation such as `skills[0]`, `.take()`, `.slice()`, or `.sublist()`.

### Update Candidate Status

```http
PATCH /resumes/{candidate_id}/status/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

```json
{
  "status": "accepted",
  "hr_notes": "Good candidate"
}
```

Valid statuses:

```text
pending
shortlisted
accepted
rejected
on_hold
```

### Resume Statistics

```http
GET /resumes/stats/
Authorization: Bearer ACCESS_TOKEN
```

Response:

```json
{
  "total_cvs": 10,
  "shortlisted": 3,
  "accepted": 2,
  "rejected": 1,
  "pending": 4,
  "on_hold": 0
}
```

### Download Original Resume

```http
GET /resumes/{candidate_id}/download/
Authorization: Bearer ACCESS_TOKEN
```

For an external browser or PDF viewer, the backend also accepts:

```text
/resumes/{candidate_id}/download/?token=ACCESS_TOKEN
```

## Jobs

### List Jobs

```http
GET /jobs/
Authorization: Bearer ACCESS_TOKEN
```

### Create Job

```http
POST /jobs/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

```json
{
  "title": "Flutter Developer",
  "department": "Engineering",
  "location": "Lahore",
  "job_type": "Full Time",
  "required_skills": ["Flutter", "Dart"],
  "optional_skills": ["Firebase"],
  "min_experience": 2,
  "education_level": "BSc",
  "salary_min": 100000,
  "salary_max": 200000,
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2
}
```

The three weights must add up to `1.0`.

### Get Job

```http
GET /jobs/{job_id}/
Authorization: Bearer ACCESS_TOKEN
```

### Update Job

```http
PUT /jobs/{job_id}/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

The same job fields can be sent. Partial updates are supported by the backend.

### Delete Job

```http
DELETE /jobs/{job_id}/
Authorization: Bearer ACCESS_TOKEN
```

## Matching

### Match Candidates

```http
POST /matching/match/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

Send either a saved `job_id` or the complete job data:

```json
{
  "job_id": 1,
  "title": "Flutter Developer",
  "required_skills": ["Flutter", "Dart"],
  "optional_skills": ["Firebase"],
  "min_experience": 2,
  "education_level": "BSc / BE",
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2
}
```

Response:

```json
{
  "message": "Matched candidates.",
  "stats": {
    "total": 10,
    "good_match": 3,
    "partial": 4,
    "no_match": 3
  },
  "results": []
}
```

### Get Match Results

```http
GET /matching/results/
GET /matching/results/?min_score=60
Authorization: Bearer ACCESS_TOKEN
```

Response:

```json
{
  "count": 10,
  "results": [
    {
      "candidate_id": 1,
      "candidate_name": "Candidate Name",
      "email": "candidate@example.com",
      "experience_years": 3,
      "education_level": "BSc",
      "skills": ["Flutter", "Dart"],
      "final_score": 87.5,
      "skill_score": 90,
      "experience_score": 85,
      "education_score": 80,
      "missing_skills": [],
      "explanation": "...",
      "status": "pending"
    }
  ]
}
```

## Flutter Frontend Notes

The Flutter API service should include methods for:

- Login, register, logout, profile, FCM update, and token refresh
- Candidate list, upload, detail, status update, statistics, and download
- Job list, create, detail, update, and delete
- Candidate matching and match-result loading

Important status URL:

```text
PATCH /resumes/{candidate_id}/status/
```

Do not use:

```text
PATCH /resumes/{candidate_id}/
```

For complete candidate rendering, map every returned collection:

```text
technical_skills
work_experience / work_history
education
projects
certifications
awards
languages
additional_information
```
