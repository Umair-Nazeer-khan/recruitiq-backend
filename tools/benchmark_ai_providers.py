import json
import os
import time
from urllib.parse import quote

import requests


GEMINI_MODEL = 'gemini-3.6-flash'
GROQ_MODEL = 'openai/gpt-oss-120b'
PROMPT = (
    'Extract resume facts. Return only a JSON object with exactly these fields: '
    'name (string), email (string), skills (array of technical skills only), '
    'experience_years (number; paid professional work only; do not count education '
    'or projects), education_level (one of PhD, Masters, Bachelor, Intermediate, '
    'Matric, or empty string), work_history (array of objects with company and role '
    'strings). Do not infer missing facts. Keep work_history empty when there is no '
    'professional employment. Resume:\n'
)

CASES = [
    {
        'label': 'layout and experience',
        'expected': {
            'name': 'Maya Chen',
            'email': 'maya.chen@example.com',
            'skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
            'experience_years': 4,
            'education_level': 'Bachelor',
            'work_history': [
                {'company': 'Meridian Labs', 'role': 'Backend Engineer'},
            ],
        },
        'resume': (
            'MAYA CHEN\nmaya.chen@example.com | +1 555 010 2200\n\n'
            'PROFILE\nBackend engineer with four years of professional experience '
            'building web services.\n\nTECHNICAL SKILLS\n'
            'Python, Django, PostgreSQL, Docker\n\nEXPERIENCE\n'
            'Meridian Labs | Backend Engineer | 2022 - Present\n'
            'Built and maintained internal APIs.\n\nEDUCATION\n'
            'BSc Computer Science, North Coast University, 2018 - 2022'
        ),
    },
    {
        'label': 'education versus paid work',
        'expected': {
            'name': 'Samir Khan',
            'email': 'samir.khan@example.com',
            'skills': ['React', 'TypeScript', 'Flutter'],
            'experience_years': 2.5,
            'education_level': 'Masters',
            'work_history': [{'company': 'BrightPath', 'role': 'Mobile Developer'}],
        },
        'resume': (
            'Samir Khan\nsamir.khan@example.com\n\nSUMMARY\n'
            '2.5 years of full-time professional software experience.\n\nSKILLS\n'
            'React, TypeScript, Flutter\n\nWORK EXPERIENCE\n'
            'BrightPath - Mobile Developer - 2023 to 2025\n'
            'Delivered customer-facing mobile features.\n\nEDUCATION\n'
            'MSc Computer Science, City University, 2021 - 2023'
        ),
    },
    {
        'label': 'title and projects are not employment',
        'expected': {
            'name': 'Nora Williams',
            'email': 'nora.williams@example.com',
            'skills': ['Figma', 'HTML', 'CSS', 'React'],
            'experience_years': 0,
            'education_level': 'Bachelor',
            'work_history': [],
        },
        'resume': (
            'NORA WILLIAMS | PRODUCT DESIGNER\nnora.williams@example.com\n\n'
            'PROFILE\nRecent graduate seeking a first full-time role. No paid '
            'professional employment to date.\n\nTECHNICAL SKILLS\n'
            'Figma, HTML, CSS, React\n\nPROJECTS\n'
            'Student portfolio redesign - UX lead, 2023 - 2024\n\nEDUCATION\n'
            'Bachelor of Design, Lakeside College, 2020 - 2024'
        ),
    },
    {
        'label': 'multiple roles and explicit total',
        'expected': {
            'name': 'Luis Ortega',
            'email': 'luis.ortega@example.com',
            'skills': ['Go', 'AWS', 'Kubernetes', 'PostgreSQL'],
            'experience_years': 7,
            'education_level': 'Masters',
            'work_history': [
                {'company': 'Northstar Systems', 'role': 'Senior Platform Engineer'},
                {'company': 'Blue Oak Tech', 'role': 'Platform Engineer'},
            ],
        },
        'resume': (
            'Luis Ortega\nluis.ortega@example.com\n\nSUMMARY\n'
            'Platform engineer with 7 years of professional experience.\n\nSKILLS\n'
            'Go, AWS, Kubernetes, PostgreSQL\n\nPROFESSIONAL EXPERIENCE\n'
            'Northstar Systems | Senior Platform Engineer | 2022 - Present\n'
            'Blue Oak Tech | Platform Engineer | 2019 - 2022\n\nEDUCATION\n'
            'MSc Software Engineering, Western Institute, 2017 - 2019'
        ),
    },
]


def _normalize(value):
    return ' '.join(''.join(char.lower() if char.isalnum() else ' ' for char in str(value or '')).split())


def _f1(expected, actual):
    expected = [_normalize(value) for value in expected]
    actual = [_normalize(value) for value in actual]
    if not expected and not actual:
        return 1.0
    if not expected or not actual:
        return 0.0
    matches = sum(value in actual for value in expected)
    precision = matches / len(actual)
    recall = matches / len(expected)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _score(expected, actual):
    actual_skills = actual.get('skills') or []
    actual_jobs = actual.get('work_history') or []
    expected_jobs = [
        f"{job['company']} {job['role']}" for job in expected['work_history']
    ]
    actual_jobs = [
        f"{job.get('company', '')} {job.get('role', '')}"
        for job in actual_jobs if isinstance(job, dict)
    ]
    try:
        experience = abs(float(actual.get('experience_years', 0)) - expected['experience_years']) <= 0.75
    except (TypeError, ValueError):
        experience = False

    scores = {
        'name': float(_normalize(actual.get('name')) == _normalize(expected['name'])),
        'email': float(_normalize(actual.get('email')) == _normalize(expected['email'])),
        'skills_f1': _f1(expected['skills'], actual_skills),
        'experience': float(experience),
        'education': float(
            _normalize(actual.get('education_level')) == _normalize(expected['education_level'])
        ),
        'work_history_f1': _f1(expected_jobs, actual_jobs),
    }
    scores['overall_percent'] = round(sum(scores.values()) / len(scores) * 100, 2)
    return scores


def _json_object(text):
    start, end = text.find('{'), text.rfind('}')
    if start < 0 or end < start:
        raise ValueError('response did not contain a JSON object')
    return json.loads(text[start:end + 1])


def _post_with_retry(url, **kwargs):
    for attempt in range(3):
        response = requests.post(url, **kwargs)
        if response.status_code not in {429, 500, 502, 503, 504} or attempt == 2:
            return response
        time.sleep(2 ** attempt)


def _call_gemini(resume, api_key):
    response = _post_with_retry(
        f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent',
        params={'key': api_key},
        json={
            'contents': [{'parts': [{'text': PROMPT + resume}]}],
            'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0},
        },
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f'HTTP {response.status_code}')
    content = response.json()['candidates'][0]['content']['parts']
    return _json_object(''.join(part.get('text', '') for part in content))


def _call_groq(resume, api_key):
    response = _post_with_retry(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'model': GROQ_MODEL,
            'temperature': 0,
            'response_format': {'type': 'json_object'},
            'messages': [
                {'role': 'system', 'content': PROMPT},
                {'role': 'user', 'content': resume},
            ],
        },
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f'HTTP {response.status_code}')
    return _json_object(response.json()['choices'][0]['message']['content'])


def _benchmark(provider, model, call, api_key):
    started = time.monotonic()
    rows = []
    for case in CASES:
        try:
            output = call(case['resume'], api_key)
            rows.append({
                'case': case['label'],
                'metrics': _score(case['expected'], output),
                'output': output,
            })
        except Exception as error:
            rows.append({'case': case['label'], 'error': type(error).__name__})

    valid_rows = [row for row in rows if 'metrics' in row]
    averages = {}
    if valid_rows:
        for metric in valid_rows[0]['metrics']:
            averages[metric] = round(
                sum(row['metrics'][metric] for row in valid_rows) / len(valid_rows), 4
            )
    return {
        'provider': provider,
        'model': model,
        'elapsed_seconds': round(time.monotonic() - started, 2),
        'scored_cases': len(valid_rows),
        'average': averages,
        'cases': rows,
    }


def main():
    gemini_key = os.environ.get('GEMINI_API_KEY')
    groq_key = os.environ.get('GROQ_API_KEY')
    if not gemini_key or not groq_key:
        raise SystemExit('Both GEMINI_API_KEY and GROQ_API_KEY must be configured.')

    # The production parser references this model; check it separately from the valid-model comparison.
    configured_model = 'gemini-3.6-flash'
    configured_response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/{quote(configured_model)}:generateContent',
        params={'key': gemini_key},
        json={
            'contents': [{'parts': [{'text': 'Reply with OK.'}]}],
            'generationConfig': {'maxOutputTokens': 8},
        },
        timeout=60,
    )
    results = [
        {
            'production_configured_gemini_model': configured_model,
            'http_status': configured_response.status_code,
        },
        _benchmark('Gemini', GEMINI_MODEL, _call_gemini, gemini_key),
        _benchmark('Groq', GROQ_MODEL, _call_groq, groq_key),
    ]
    print(json.dumps({
        'method': (
            'Four synthetic resumes; six equally weighted fields. Skills and work history '
            'use F1; experience is correct within 0.75 years. This small benchmark is '
            'directional, not a general accuracy guarantee.'
        ),
        'results': results,
    }, indent=2))


if __name__ == '__main__':
    main()