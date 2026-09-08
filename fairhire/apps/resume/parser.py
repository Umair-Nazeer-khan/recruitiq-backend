# fairhire/apps/resume/parser.py
# ─────────────────────────────────────────────────────────────────
#  AI Resume Parser.
#  Extracts structured data from raw resume text using NLP.
#
#  HOW IT WORKS:
#  1. Read PDF/DOCX/TXT file → get raw text
#  2. Split text into sections (Education / Experience / Skills / etc.)
#     so each extractor only looks at its own section — this is the
#     fix for "education counted as work experience" bugs.
#  3. If GEMINI_API_KEY is configured, try LLM-based structured
#     extraction first (much higher accuracy on messy formats).
#  4. Always fall back to the rule-based (regex + spaCy) parser if
#     the LLM is unavailable or fails — so the app never breaks.
# ─────────────────────────────────────────────────────────────────

import re
import json
import datetime
import fitz          # PyMuPDF for PDF
import docx          # python-docx for DOCX
import spacy
from pathlib import Path
from decouple import config


# ── Load spaCy model ──────────────────────────
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    nlp = spacy.blank('en')
    print("spaCy model not found. Run: python -m spacy download en_core_web_sm")


# ── Common skills list (longest phrases first so multi-word skills
#    are matched before their substrings, e.g. 'rest api' before 'api') ──
SKILLS_LIST = sorted([
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'swift',
    'kotlin', 'dart', 'go', 'rust', 'ruby', 'scala',
    'flutter', 'react native', 'android', 'ios', 'xamarin',
    'react', 'vue', 'angular', 'html', 'css', 'bootstrap', 'tailwind',
    'django', 'flask', 'fastapi', 'node.js', 'express', 'spring boot', 'laravel',
    'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'firebase',
    'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
    'scikit-learn', 'pandas', 'numpy', 'keras',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github', 'ci/cd',
    'rest api', 'graphql', 'api', 'postman',
    'linux', 'agile', 'scrum', 'sql', 'excel', 'figma',
], key=len, reverse=True)

EDU_LEVELS = {
    'phd': 5, 'doctorate': 5,
    'msc': 4, 'mba': 4, 'ms': 4, 'masters': 4,
    'bsc': 3, 'be': 3, 'bcs': 3, 'bachelor': 3,
    'intermediate': 2, 'fsc': 2, 'a level': 2,
    'matric': 1, 'ssc': 1, 'o level': 1,
}

# ── Section header keywords, used to split the resume into blocks ──
SECTION_HEADERS = {
    'experience': ['professional experience', 'work experience', 'experience',
                   'employment history', 'employment', 'internships', 'internship',
                   'work history'],
    'education':  ['education', 'academic background', 'academic qualifications',
                    'qualification'],
    'skills':     ['technical skills', 'skills', 'core competencies', 'competencies'],
    'projects':   ['key projects', 'projects'],
    'summary':    ['professional summary', 'summary', 'objective'],
}


# ════════════════════════════════════════════════════════════════
#  STEP 1 — Extract raw text from file
# ════════════════════════════════════════════════════════════════

def extract_text(file_path: str) -> str:
    path = Path(file_path)
    ext  = path.suffix.lower()
    if ext == '.pdf':
        return _text_from_pdf(file_path)
    elif ext in ('.docx', '.doc'):
        return _text_from_docx(file_path)
    elif ext == '.txt':
        return path.read_text(encoding='utf-8', errors='ignore')
    else:
        raise ValueError(f'Unsupported file type: {ext}')


def _text_from_pdf(path: str) -> str:
    text = ''
    try:
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f'PDF error: {e}')
    return text


def _text_from_docx(path: str) -> str:
    text = ''
    try:
        doc = docx.Document(path)
        for para in doc.paragraphs:
            text += para.text + '\n'
    except Exception as e:
        print(f'DOCX error: {e}')
    return text


# ════════════════════════════════════════════════════════════════
#  STEP 2 — Split resume into sections (THE KEY FIX)
# ════════════════════════════════════════════════════════════════

def _split_sections(text: str) -> dict:
    """
    Splits the resume into {section_name: section_text} blocks based on
    header lines. This is what prevents an Education date range from
    being read as Experience, and a Tools section from leaking into Skills.

    A line counts as a header if it's short and matches a known keyword
    as a standalone line (not buried mid-sentence in a bullet point).
    """
    lines = text.split('\n')
    sections = {name: [] for name in SECTION_HEADERS}
    sections['other'] = []
    current = 'other'

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower().strip(':').strip()

        matched_header = None
        if 0 < len(lower) <= 40:
            for section_name, keywords in SECTION_HEADERS.items():
                if lower in keywords:
                    matched_header = section_name
                    break
            if not matched_header:
                for section_name, keywords in SECTION_HEADERS.items():
                    for kw in keywords:
                        if kw in lower and len(lower) <= len(kw) + 10:
                            matched_header = section_name
                            break
                    if matched_header:
                        break

        if matched_header:
            current = matched_header
            continue

        if stripped:
            sections[current].append(stripped)

    return {name: '\n'.join(body) for name, body in sections.items()}


# ════════════════════════════════════════════════════════════════
#  STEP 3 — Rule-based parser (regex + spaCy), now section-aware
# ════════════════════════════════════════════════════════════════

def parse_resume_rule_based(text: str) -> dict:
    text_lower = text.lower()
    sections = _split_sections(text)

    experience_text = sections['experience'] or text
    skills_text     = (sections['skills'] or text).lower()
    education_text  = sections['education'] or ''

    return {
        'name':             _extract_name(text),
        'email':            _extract_email(text),
        'phone':            _extract_phone(text),
        'skills':           _extract_skills(skills_text),
        'experience_years': _extract_experience_years(experience_text.lower()),
        'education':        _extract_education(text, education_text),
        'education_level':  _extract_education_level(text_lower),
        'work_history':     _extract_work_history(experience_text),
        'location':         _extract_location(text),
        'raw_text':         text,
    }


def _extract_email(text: str) -> str:
    match = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ''


def _extract_phone(text: str) -> str:
    patterns = [
        r'(\+92[\s\-]?\d{3}[\s\-]?\d{7})',
        r'(0\d{3}[\s\-]?\d{7})',
        r'(\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{4})',
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            return match.group(0).strip()
    return ''


def _extract_name(text: str) -> str:
    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text.strip()
            if 2 < len(name) < 50:
                return name
    for line in text.split('\n')[:5]:
        line = line.strip()
        if line and 2 < len(line) < 50 and not any(c in line for c in ['@', ':', '/']):
            if re.match(r'^[A-Za-z\s]+$', line):
                return line
    return ''


def _extract_skills(skills_text_lower: str) -> list:
    """
    Matches longest skill phrases first and marks their character span as
    'claimed' so a shorter overlapping skill (e.g. 'api' inside 'rest api')
    isn't also added as a separate, redundant entry.
    """
    found = []
    claimed = [False] * len(skills_text_lower)

    for skill in SKILLS_LIST:
        for m in re.finditer(re.escape(skill), skills_text_lower):
            start, end = m.start(), m.end()
            if any(claimed[start:end]):
                continue
            before_ok = start == 0 or not skills_text_lower[start - 1].isalnum()
            after_ok  = end == len(skills_text_lower) or not skills_text_lower[end].isalnum()
            if before_ok and after_ok:
                for i in range(start, end):
                    claimed[i] = True
                found.append(skill.upper() if len(skill) <= 3 else skill.title())
                break

    return list(dict.fromkeys(found))


def _extract_experience_years(experience_text_lower: str) -> float:
    """Extract total years of experience — scoped to the experience
    section only, so education date ranges are never included."""
    patterns = [
        r'(\d+\.?\d*)\+?\s*years?\s*(?:of\s+)?(?:work\s+)?experience',
        r'experience\s*:?\s*(\d+\.?\d*)\+?\s*years?',
        r'(\d+\.?\d*)\s*yrs?\s*(?:of\s+)?(?:work\s+)?experience',
    ]
    for p in patterns:
        match = re.search(p, experience_text_lower)
        if match:
            return float(match.group(1))

    ranges = re.findall(r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|present|current|now)',
                         experience_text_lower)
    total = 0
    current_year = datetime.datetime.now().year
    for start, end in ranges:
        try:
            s = int(start)
            e = current_year if end in ('present', 'current', 'now') else int(end)
            total += max(0, e - s)
        except ValueError:
            pass
    return float(min(total, 30))


def _extract_education(full_text: str, education_section: str) -> str:
    """Prefer the pre-split education section; fall back to the old
    keyword-scan approach only if section splitting found nothing."""
    if education_section:
        lines = [l for l in education_section.split('\n') if l.strip()]
        return ' | '.join(lines[:6])

    lines = full_text.split('\n')
    edu_section = []
    in_edu = False
    for line in lines:
        lower = line.lower().strip()
        if any(kw in lower for kw in ['education', 'qualification', 'degree', 'academic']):
            in_edu = True
        elif in_edu and any(kw in lower for kw in ['experience', 'skills', 'projects', 'work history', 'employment']):
            break
        if in_edu and line.strip():
            edu_section.append(line.strip())
    return ' | '.join(edu_section[:5]) if edu_section else ''


def _extract_education_level(text_lower: str) -> str:
    best_level = ''
    best_rank  = 0
    for keyword, rank in EDU_LEVELS.items():
        if keyword in text_lower and rank > best_rank:
            best_rank  = rank
            best_level = keyword.title()
    return best_level


def _extract_work_history(experience_text: str) -> list:
    """Extract {duration, details} — scoped to the experience section
    only, so education entries never appear here."""
    jobs = []
    lines = experience_text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'(20\d{2}|19\d{2})', line):
            duration = re.search(r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|Present|present|Current)', line)
            if duration:
                context_lines = lines[max(0, i - 1):i + 2]
                context = ' | '.join(l.strip() for l in context_lines if l.strip())
                jobs.append({
                    'duration': duration.group(0),
                    'details':  context[:120],
                })
    return jobs[:5]


def _extract_location(text: str) -> str:
    doc = nlp(text[:800])
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            return ent.text
    cities = ['Lahore', 'Karachi', 'Islamabad', 'Rawalpindi', 'Faisalabad',
              'Multan', 'Peshawar', 'Quetta', 'Sialkot', 'Gujranwala']
    for city in cities:
        if city.lower() in text.lower():
            return city
    return ''


# ════════════════════════════════════════════════════════════════
#  STEP 4 — Optional: Gemini-based extraction (higher accuracy)
# ════════════════════════════════════════════════════════════════
#
#  Set GEMINI_API_KEY in your .env / Railway variables to enable this.
#  Get a free key at: https://aistudio.google.com/app/apikey
#  If the key isn't set, or the call fails for any reason, the parser
#  silently falls back to the rule-based parser above — the app never
#  breaks because of this.
# ════════════════════════════════════════════════════════════════

GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

_EXTRACTION_PROMPT = """You are a resume-parsing engine. Read the resume text
below and return ONLY a single valid JSON object (no markdown, no commentary)
with exactly these fields:

{{
  "name": "full name of the candidate",
  "email": "email address",
  "phone": "phone number",
  "location": "city, if mentioned",
  "skills": ["list", "of", "technical", "skills", "only - do not include soft skills"],
  "experience_years": <number, total years of paid/professional work experience only
                        - do NOT count education duration as experience>,
  "education": "highest degree, institution, and years, as one line",
  "education_level": "one of: PhD, Masters, Bachelor, Intermediate, Matric",
  "work_history": [
    {{"company": "...", "role": "...", "duration": "e.g. 2023 - Present"}}
  ]
}}

Rules:
- Never place an education entry inside work_history.
- Deduplicate skills (e.g. do not list both "API" and "REST API" if they
  refer to the same mention).
- If a field is not found, use an empty string, empty list, or 0.

Resume text:
---
{resume_text}
---
"""


def _parse_with_gemini(text: str):
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            _EXTRACTION_PROMPT.format(resume_text=text[:8000]),
            generation_config={'response_mime_type': 'application/json'},
        )
        data = json.loads(response.text)

        return {
            'name':             data.get('name', ''),
            'email':            data.get('email', ''),
            'phone':            data.get('phone', ''),
            'skills':           data.get('skills', []) or [],
            'experience_years': float(data.get('experience_years', 0) or 0),
            'education':        data.get('education', ''),
            'education_level':  data.get('education_level', ''),
            'work_history':     data.get('work_history', []) or [],
            'location':         data.get('location', ''),
            'raw_text':         text,
        }
    except Exception as e:
        print(f'Gemini parsing failed, falling back to rule-based parser: {e}')
        return None


# ════════════════════════════════════════════════════════════════
#  Public entry point — used by views.py
# ════════════════════════════════════════════════════════════════

def parse_resume(text: str) -> dict:
    """
    Main parser function. Tries Gemini first (if configured) for higher
    accuracy, and always falls back to the rule-based parser so resume
    upload never fails outright.
    """
    llm_result = _parse_with_gemini(text)
    if llm_result is not None:
        return llm_result
    return parse_resume_rule_based(text)
