# FairHire Backend API Contract for Frontend

## Base URL

Production:
https://proud-wholeness-production-2929.up.railway.app/api/v1

Local:
http://localhost:8000/api/v1

All authenticated endpoints require:

```http
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

For file upload:

```http
Authorization: Bearer ACCESS_TOKEN
Content-Type: multipart/form-data
```

---

## Authentication Rules

- JWT is used for authentication.
- Access token is sent in the Authorization header.
- Refresh token is returned on login/register.
- Refresh endpoint is: POST /api/v1/auth/token/refresh/
- Frontend should store access and refresh tokens in secure storage.

---

## 1) Register

### Endpoint
POST /api/v1/auth/register/

### Request body
```json
{
  "name": "Umair",
  "email": "umair@company.com",
  "password": "password123"
}
```

### Required fields
- name: string
- email: valid email
- password: string, minimum 6 characters

### Response
Status: 201 Created

```json
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
```

### Error response
Status: 400 Bad Request

```json
{
  "errors": {
    "email": ["This field is required."],
    "password": ["Ensure this field has at least 6 characters."]
  }
}
```

---

## 2) Login

### Endpoint
POST /api/v1/auth/login/

### Request body
```json
{
  "email": "umair@company.com",
  "password": "password123",
  "fcm_token": "optional-device-token"
}
```

### Required fields
- email: valid email
- password: string

### Optional field
- fcm_token: string

### Response
Status: 200 OK

```json
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
```

### Error response
```json
{
  "errors": {
    "non_field_errors": ["Invalid email or password."]
  }
}
```

---

## 3) Logout

### Endpoint
POST /api/v1/auth/logout/

### Request body
```json
{
  "refresh": "JWT_REFRESH_TOKEN"
}
```

### Response
Status: 200 OK

```json
{
  "message": "Logged out successfully."
}
```

---

## 4) Get Profile

### Endpoint
GET /api/v1/auth/profile/

### Response
Status: 200 OK

```json
{
  "id": 1,
  "name": "Umair",
  "email": "umair@company.com",
  "role": "hr_manager",
  "created_at": "2026-09-23T10:00:00Z"
}
```

---

## 5) Update FCM Token

### Endpoint
PATCH /api/v1/auth/update-fcm/

### Request body
```json
{
  "fcm_token": "new-device-token"
}
```

### Response
Status: 200 OK

```json
{
  "message": "FCM token updated."
}
```

### Error response
```json
{
  "error": "No token provided."
}
```

---

## 6) Refresh Access Token

### Endpoint
POST /api/v1/auth/token/refresh/

### Request body
```json
{
  "refresh": "JWT_REFRESH_TOKEN"
}
```

### Response
```json
{
  "access": "NEW_JWT_ACCESS_TOKEN"
}
```

---

# Resume / Candidate APIs

## 7) List Candidates

### Endpoint
GET /api/v1/resumes/

Optional filter:
```http
GET /api/v1/resumes/?status=shortlisted
```

### Response
Status: 200 OK

```json
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
```

### Notes
- Dashboard and candidate list screens use this.
- Status filter is optional.

---

## 8) Upload Resume

### Endpoint
POST /api/v1/resumes/upload/

### Form-data
Field name:
- file

Example:
```http
file = resume.pdf
```

### Response
Status: 201 Created

```json
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
      {
        "name": "FairHire App",
        "description": "Recruitment platform"
      }
    ],
    "certifications": ["AWS Certified"],
    "awards": ["Best Intern 2022"],
    "work_history": [
      {
        "company": "ABC Tech",
        "role": "Flutter Developer",
        "duration": "2022 - 2024"
      }
    ],
    "match_score": null,
    "skill_score": null,
    "experience_score": null,
    "education_score": null,
    "missing_skills": [],
    "score_explanation": "",
    "status": "pending",
    "hr_notes": "",
    "original_name": "john_resume.pdf",
    "created_at": "2026-09-23T10:00:00Z",
    "resume_file_url": "https://backend-url/api/v1/resumes/1/download/"
  }
}
```

### Supported file types
- PDF
- DOCX
- TXT

### Important note
- This is multipart upload, not JSON.
- Only field is file.

---

## 9) Get Candidate Detail

### Endpoint
GET /api/v1/resumes/{candidate_id}/

### Response
Status: 200 OK

```json
{
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
    {
      "name": "FairHire App",
      "description": "Recruitment platform"
    }
  ],
  "certifications": ["AWS Certified"],
  "awards": ["Best Intern 2022"],
  "work_history": [
    {
      "company": "ABC Tech",
      "role": "Flutter Developer",
      "duration": "2022 - 2024"
    }
  ],
  "match_score": 87.5,
  "skill_score": 90.0,
  "experience_score": 80.0,
  "education_score": 85.0,
  "missing_skills": ["Node.js"],
  "score_explanation": "Strong mobile skillset with minor gap in backend stack.",
  "status": "shortlisted",
  "hr_notes": "Strong fit for mobile role.",
  "original_name": "john_resume.pdf",
  "created_at": "2026-09-23T10:00:00Z",
  "resume_file_url": "https://backend-url/api/v1/resumes/1/download/"
}
```

### Notes
- Candidate detail screen should render all arrays dynamically.
- Do not assume fixed length or fixed indexes.

---

## 10) Update Candidate Status

### Endpoint
PATCH /api/v1/resumes/{candidate_id}/status/

### Request body
```json
{
  "status": "accepted",
  "hr_notes": "Good candidate"
}
```

### Valid statuses
- pending
- shortlisted
- accepted
- rejected
- on_hold

### Response
Status: 200 OK

```json
{
  "message": "Status updated.",
  "id": 1,
  "status": "accepted"
}
```

---

## 11) Resume Statistics

### Endpoint
GET /api/v1/resumes/stats/

### Response
Status: 200 OK

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

### Notes
- Use for dashboard summary cards.

---

## 12) Download Resume

### Endpoint
GET /api/v1/resumes/{candidate_id}/download/

### Response
- Returns the actual file as attachment
- Content-Type depends on file type

### Optional token-based download
This is also accepted:
```http
GET /api/v1/resumes/{candidate_id}/download/?token=ACCESS_TOKEN
```

### Notes
- Use this when opening the file in browser or PDF viewer.
- Frontend may use a file preview or download button.

---

# Job APIs

## 13) List Jobs

### Endpoint
GET /api/v1/jobs/

### Response
```json
[
  {
    "id": 1,
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
    "education_weight": 0.2,
    "is_active": true,
    "created_at": "2026-09-23T10:00:00Z"
  }
]
```

---

## 14) Create Job

### Endpoint
POST /api/v1/jobs/

### Request body
```json
{
  "title": "Flutter Developer",
  "department": "Mobile",
  "location": "Lahore",
  "job_type": "full_time",
  "required_skills": ["Flutter", "Dart"],
  "optional_skills": ["Firebase", "Node.js"],
  "min_experience": 2,
  "education_level": "BSc / BE",
  "salary_min": 80000,
  "salary_max": 120000,
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2
}
```

### Response
Status: 201 Created

```json
{
  "id": 1,
  "title": "Flutter Developer",
  "department": "Mobile",
  "location": "Lahore",
  "job_type": "full_time",
  "required_skills": ["Flutter", "Dart"],
  "optional_skills": ["Firebase", "Node.js"],
  "min_experience": 2,
  "education_level": "BSc / BE",
  "salary_min": 80000,
  "salary_max": 120000,
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2,
  "is_active": true,
  "created_at": "2026-09-23T10:00:00Z"
}
```

### Validation rules
- skill_weight + experience_weight + education_weight must sum to 1.0
- salary_min and salary_max cannot be negative
- salary_min cannot be greater than salary_max
- min_experience cannot be negative

---

## 15) Get Single Job

### Endpoint
GET /api/v1/jobs/{job_id}/

### Response
Same shape as single job object.

---

## 16) Update Job

### Endpoint
PUT /api/v1/jobs/{job_id}/

### Request body
Same as create, partial or full update is accepted.

### Response
```json
{
  "id": 1,
  "title": "Senior Flutter Developer",
  "department": "Mobile",
  "location": "Islamabad",
  "job_type": "remote",
  "required_skills": ["Flutter", "Dart", "Bloc"],
  "optional_skills": ["Firebase"],
  "min_experience": 3,
  "education_level": "MSc / MS",
  "salary_min": 100000,
  "salary_max": 150000,
  "skill_weight": 0.5,
  "experience_weight": 0.3,
  "education_weight": 0.2,
  "is_active": true,
  "created_at": "2026-09-23T10:00:00Z"
}
```

---

## 17) Delete Job

### Endpoint
DELETE /api/v1/jobs/{job_id}/

### Response
Status: 204 No Content

---

# Matching APIs

## 18) Match Candidates Against Job

### Endpoint
POST /api/v1/matching/

This endpoint can take either:
- a saved job id, or
- inline job details

### Option A: saved job
```json
{
  "job_id": 1
}
```

### Option B: inline job
```json
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
```

### Response
Status: 200 OK

```json
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
```

### Notes
- This is the main endpoint for the candidate matching screen.
- For inline matching, required fields are:
  - required_skills
  - min_experience
  - education_level
- Weights must total to 1.0
- Candidates are scored and saved in DB.

---

## 19) Get Previous Match Results

### Endpoint
GET /api/v1/matching/results/

Optional filter:
```http
GET /api/v1/matching/results/?min_score=60
```

### Response
```json
{
  "count": 10,
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
```

---

# Common Response Formats

## Success shape
```json
{
  "message": "Operation successful.",
  "data": {}
}
```

## Error shape
```json
{
  "error": "Something went wrong.",
  "errors": {
    "field_name": ["validation message"]
  }
}
```

---

# Status Codes

- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 401 Unauthorized
- 404 Not Found
- 500 Internal Server Error

---

# Frontend Implementation Notes

## Recommended frontend model mapping
Map backend JSON to these frontend models:

- AuthResponse
- UserModel
- CandidateModel
- DashboardStats
- JobModel
- MatchResultModel

## Important naming rules
Use backend field names as the source of truth:
- name not userName
- email
- skills
- status
- match_score
- education_level
- job_type
- final_score
- candidate_id

Do not invent custom keys unless you convert them in a model layer.

## Example
Bad:
```dart
response['userData']['name']
```

Good:
```dart
UserModel.fromJson(response['user'])
```

---

# CORS / Hosting Note for Frontend

If the frontend runs from another domain or local device, backend must allow that origin. In local development:
- For Android emulator, use:
  http://10.0.2.2:PORT
- For iOS simulator, use:
  http://localhost:PORT
- For real device, use your LAN IP like:
  http://192.168.1.20:PORT

---

# Final Checklist for Frontend Developer

Before integration, make sure the frontend supports:

- JWT auth flow
- Multipart upload for resumes
- Authorization header on every protected call
- Candidate status values:
  - pending
  - shortlisted
  - accepted
  - rejected
  - on_hold
- Weight validation:
  - skill_weight + experience_weight + education_weight = 1.0
- Dashboard stats keys:
  - total_cvs
  - shortlisted
  - accepted
  - rejected
  - pending
  - on_hold

---

If you want, I can next turn this into a ready-to-use Flutter model file or a Dart API service file.
