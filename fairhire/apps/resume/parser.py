# fairhire/apps/resume/parser.py
# ─────────────────────────────────────────────────────────────────
#  AI Resume Parser.
#  Extracts structured data from raw resume text using NLP.
#
#  HOW IT WORKS:
#  1. Read PDF/DOCX/TXT file → get raw text
#  2. Use regex + spaCy NER → extract name, email, phone
#  3. Use keyword matching  → extract skills
#  4. Use pattern matching  → extract experience years, education
# ─────────────────────────────────────────────────────────────────

import re
import fitz          # PyMuPDF for PDF
import docx          # python-docx for DOCX
import spacy
from pathlib import Path


# ── Load spaCy model ──────────────────────────
# First time: run  python -m spacy download en_core_web_sm
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # If model not downloaded, use blank pipeline
    nlp = spacy.blank('en')
    print("⚠  spaCy model not found. Run: python -m spacy download en_core_web_sm")


# ── Common skills list ───────────────────────
SKILLS_LIST = [
    # Programming
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'swift',
    'kotlin', 'dart', 'go', 'rust', 'ruby', 'scala',
    # Mobile
    'flutter', 'react native', 'android', 'ios', 'xamarin',
    # Web Frontend
    'react', 'vue', 'angular', 'html', 'css', 'bootstrap', 'tailwind',
    # Backend
    'django', 'flask', 'fastapi', 'node.js', 'express', 'spring boot', 'laravel',
    # Database
    'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'firebase',
    # AI/ML
    'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
    'scikit-learn', 'pandas', 'numpy', 'keras',
    # Cloud / DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github', 'ci/cd',
    # APIs
    'rest api', 'graphql', 'api', 'postman',
    # Other
    'linux', 'agile', 'scrum', 'sql', 'excel', 'figma',
]

# Education levels (highest wins)
EDU_LEVELS = {
    'phd':          5,
    'doctorate':    5,
    'msc':          4,
    'mba':          4,
    'ms':           4,
    'masters':      4,
    'bsc':          3,
    'be':           3,
    'bcs':          3,
    'bachelor':     3,
    'intermediate': 2,
    'fsc':          2,
    'a level':      2,
    'matric':       1,
    'ssc':          1,
    'o level':      1,
}


# ════════════════════════════════════════════════════════════════
#  STEP 1 — Extract raw text from file
# ════════════════════════════════════════════════════════════════

def extract_text(file_path: str) -> str:
    """Extract plain text from PDF, DOCX, or TXT file."""
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
#  STEP 2 — Parse structured data from text
# ════════════════════════════════════════════════════════════════

def parse_resume(text: str) -> dict:
    """
    Main parser function.
    Returns a dict that maps directly to the Candidate model fields.
    """
    text_lower = text.lower()

    return {
        'name':             _extract_name(text),
        'email':            _extract_email(text),
        'phone':            _extract_phone(text),
        'skills':           _extract_skills(text_lower),
        'experience_years': _extract_experience_years(text_lower),
        'education':        _extract_education(text),
        'education_level':  _extract_education_level(text_lower),
        'work_history':     _extract_work_history(text),
        'location':         _extract_location(text),
        'raw_text':         text,
    }


def _extract_email(text: str) -> str:
    match = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ''


def _extract_phone(text: str) -> str:
    # Matches Pakistani and international phone numbers
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
    """Use spaCy NER to find PERSON entity, fallback to first line."""
    doc = nlp(text[:500])  # only check first 500 chars
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text.strip()
            if 2 < len(name) < 50:
                return name

    # Fallback: first non-empty line that looks like a name
    for line in text.split('\n')[:5]:
        line = line.strip()
        if line and 2 < len(line) < 50 and not any(c in line for c in ['@', ':', '/']):
            if re.match(r'^[A-Za-z\s]+$', line):
                return line
    return ''


def _extract_skills(text_lower: str) -> list:
    found = []
    for skill in SKILLS_LIST:
        if skill in text_lower:
            found.append(skill.title() if ' ' not in skill else skill.upper() if len(skill) <= 3 else skill.title())
    return list(dict.fromkeys(found))  # deduplicate preserving order


def _extract_experience_years(text_lower: str) -> float:
    """Extract total years of experience."""
    # Pattern: "5 years", "3+ years", "2.5 years experience"
    patterns = [
        r'(\d+\.?\d*)\+?\s*years?\s*(?:of\s+)?(?:work\s+)?experience',
        r'experience\s*:?\s*(\d+\.?\d*)\+?\s*years?',
        r'(\d+\.?\d*)\s*yrs?\s*(?:of\s+)?(?:work\s+)?experience',
    ]
    for p in patterns:
        match = re.search(p, text_lower)
        if match:
            return float(match.group(1))

    # Count year ranges like "2019 – 2024" = 5 years
    ranges = re.findall(r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|present|current|now)', text_lower)
    total = 0
    import datetime
    current_year = datetime.datetime.now().year
    for start, end in ranges:
        try:
            s = int(start)
            e = current_year if end in ('present', 'current', 'now') else int(end)
            total += max(0, e - s)
        except ValueError:
            pass
    return float(min(total, 30))  # cap at 30 years


def _extract_education(text: str) -> str:
    """Return the education section as a string."""
    lines = text.split('\n')
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
    """Return highest education level found."""
    best_level = ''
    best_rank  = 0
    for keyword, rank in EDU_LEVELS.items():
        if keyword in text_lower and rank > best_rank:
            best_rank  = rank
            best_level = keyword.title()
    return best_level


def _extract_work_history(text: str) -> list:
    """Extract list of {company, role, duration} from text."""
    jobs = []
    # Look for year patterns near company/job lines
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'(20\d{2}|19\d{2})', line):
            duration = re.search(r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|Present|present|Current)', line)
            if duration:
                # try to get company/role from nearby lines
                context_lines = lines[max(0,i-1):i+2]
                context = ' | '.join(l.strip() for l in context_lines if l.strip())
                jobs.append({
                    'duration': duration.group(0),
                    'details':  context[:120],
                })
    return jobs[:5]  # max 5 jobs


def _extract_location(text: str) -> str:
    """Extract city/location using spaCy GPE (Geopolitical Entity)."""
    doc = nlp(text[:800])
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            return ent.text
    # Fallback: check for common Pakistani cities
    cities = ['Lahore', 'Karachi', 'Islamabad', 'Rawalpindi', 'Faisalabad',
              'Multan', 'Peshawar', 'Quetta', 'Sialkot', 'Gujranwala']
    for city in cities:
        if city.lower() in text.lower():
            return city
    return ''
