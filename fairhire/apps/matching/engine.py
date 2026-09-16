# ─────────────────────────────────────────────────────────────────
#  Fair Hire AI — Matching Engine
#
#  HOW THE SCORING WORKS:
#  1. Skill Score      = matched skills / required skills × 100
#  2. Experience Score = candidate years / required years × 100 (max 100)
#  3. Education Score  = level match (PhD=5, MSc=4, BSc=3, etc.)
#  4. Final Score      = (skill × 0.5) + (exp × 0.3) + (edu × 0.2)
#  5. Explanation      = written text explaining the score
# ─────────────────────────────────────────────────────────────────

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re


SKILL_ALIASES = {
    'rest apis': 'rest api',
    'rest api': 'rest api',
    'apis': 'api',
    'api': 'api',
    'nodejs': 'node.js',
    'node js': 'node.js',
    'node': 'node.js',
    'reactjs': 'react',
    'react js': 'react',
    'flutter dart': 'flutter',
    'django rest framework': 'django',
    'machine-learning': 'machine learning',
    'ml': 'machine learning',
    'deep-learning': 'deep learning',
    'bscs': 'bsc',
    'bs cs': 'bsc',
    'bs': 'bsc',
    'mscs': 'msc',
    'master': 'masters',
    'masters degree': 'masters',
    'bachelor degree': 'bachelor',
    'software engineer': 'software engineering',
}


# Education level ranking
EDU_RANK = {
    'phd':          5,
    'doctorate':    5,
    'msc':          4,
    'mba':          4,
    'ms':           4,
    'masters':      4,
    'bsc / be':     3,
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


def get_edu_rank(level: str) -> int:
    """Normalize degree strings and return a numeric rank."""
    if not level:
        return 0

    level = level.lower().strip()
    level = level.replace('degree', '').replace('education', '').strip()
    level = re.sub(r'\s+', ' ', level)

    for alias, canonical in {
        'bscs': 'bsc', 'bs cs': 'bsc', 'bsc / be': 'bsc', 'be / bsc': 'bsc',
        'bachelor of science': 'bsc', 'bachelor of engineering': 'be',
        'msc / ms': 'msc', 'm.s': 'msc', 'm s': 'msc',
        'masters': 'masters', 'master': 'masters',
        'phd / doctorate': 'phd', 'doctorate': 'phd',
        'intermediate / fsc': 'intermediate', 'fsc / intermediate': 'intermediate'
    }.items():
        if alias in level:
            level = canonical
            break

    if level in EDU_RANK:
        return EDU_RANK[level]

    best = 0
    for part in re.split(r'[/,&]', level):
        part = part.strip().replace(' ', '')
        if part in EDU_RANK:
            best = max(best, EDU_RANK[part])
        elif part in {'bs', 'bscs'}:
            best = max(best, EDU_RANK['bsc'])
        elif part in {'ms', 'msc', 'mscs'}:
            best = max(best, EDU_RANK['msc'])
    return best


def _normalize_skill(s: str) -> str:
    """Normalize skill names across common CV spelling variations."""
    s = (s or '').lower().strip()
    s = s.replace('&', ' and ')
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()

    s = SKILL_ALIASES.get(s, s)

    if len(s) > 3 and s.endswith('s') and not s.endswith('ss'):
        s = s[:-1]

    if s in {'reactjs', 'react js'}:
        s = 'react'
    if s in {'node js', 'nodejs'}:
        s = 'node.js'
    return s


def score_candidate(candidate, job) -> dict:
    """Score a candidate against a job while keeping scores realistic."""
    if isinstance(job, dict):
        required_skills = [str(s).strip() for s in job.get('required_skills', [])]
        optional_skills = [str(s).strip() for s in job.get('optional_skills', [])]
        min_experience = max(0, float(job.get('min_experience', 0) or 0))
        required_edu = str(job.get('education_level', '') or '')
        skill_weight = float(job.get('skill_weight', 0.5) or 0.5)
        experience_weight = float(job.get('experience_weight', 0.3) or 0.3)
        education_weight = float(job.get('education_weight', 0.2) or 0.2)
        job_description = ' '.join(required_skills + optional_skills)
    else:
        required_skills = [str(s).strip() for s in (job.required_skills or [])]
        optional_skills = [str(s).strip() for s in (job.optional_skills or [])]
        min_experience = max(0, float(job.min_experience or 0))
        required_edu = str(job.education_level or '')
        skill_weight = float(job.skill_weight or 0.5)
        experience_weight = float(job.experience_weight or 0.3)
        education_weight = float(job.education_weight or 0.2)
        job_description = ' '.join(required_skills + optional_skills)

    weights = [max(0.0, min(1.0, skill_weight)),
               max(0.0, min(1.0, experience_weight)),
               max(0.0, min(1.0, education_weight))]
    total_weight = sum(weights)
    if total_weight <= 0:
        weights = [0.5, 0.3, 0.2]
    else:
        weights = [w / total_weight for w in weights]

    skill_weight, experience_weight, education_weight = weights

    cand_skills = [str(s).strip() for s in (candidate.skills or [])]
    cand_exp_years = max(0.0, float(candidate.experience_years or 0))
    cand_edu_level = str(candidate.education_level or '')
    cand_raw_text = candidate.raw_text or ''

    cand_skills_norm = [_normalize_skill(s) for s in cand_skills]
    required_skills_norm = [_normalize_skill(s) for s in required_skills]
    optional_skills_norm = [_normalize_skill(s) for s in optional_skills]

    matched_required = [orig for orig, norm in zip(required_skills, required_skills_norm) if norm in cand_skills_norm]
    matched_optional = [orig for orig, norm in zip(optional_skills, optional_skills_norm) if norm in cand_skills_norm]
    missing_skills = [orig for orig, norm in zip(required_skills, required_skills_norm) if norm not in cand_skills_norm]

    if required_skills:
        req_score = len(matched_required) / len(required_skills) * 80
        opt_score = (len(matched_optional) / len(optional_skills) * 20) if optional_skills else 0
        skill_base = req_score + opt_score
    else:
        skill_base = 100.0

    tfidf_score = 0.0
    if cand_raw_text and job_description:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([job_description, cand_raw_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            tfidf_score = float(similarity) * 100
        except Exception:
            tfidf_score = 0.0

    skill_score = (skill_base * 0.7) + (tfidf_score * 0.3)
    skill_score = max(0.0, min(100.0, round(skill_score, 1)))

    if min_experience == 0:
        experience_score = 100.0
    elif cand_exp_years >= min_experience:
        experience_score = min(100.0, 100 + (cand_exp_years - min_experience) * 5)
    else:
        experience_score = min(100.0, round((cand_exp_years / max(min_experience, 0.1)) * 100, 1))

    experience_score = round(experience_score, 1)

    required_rank = get_edu_rank(required_edu)
    cand_rank = get_edu_rank(cand_edu_level)

    if required_rank == 0:
        education_score = 100.0
    elif cand_rank >= required_rank:
        education_score = 100.0
    elif cand_rank == 0:
        education_score = 50.0
    else:
        education_score = round(max(0.0, (cand_rank / required_rank) * 100), 1)

    final_score = (
        skill_score * skill_weight +
        experience_score * experience_weight +
        education_score * education_weight
    )
    final_score = max(0.0, min(100.0, round(final_score, 1)))

    # ══════════════════════════════════════════════════════════
    #  5. TRANSPARENCY EXPLANATION
    #     This is the unique feature — written reason for score
    # ══════════════════════════════════════════════════════════
    explanation = _generate_explanation(
        candidate_name   = candidate.name or 'Candidate',
        skill_score      = skill_score,
        experience_score = experience_score,
        education_score  = education_score,
        final_score      = final_score,
        matched_required = matched_required,
        missing_skills   = missing_skills,
        cand_exp_years   = cand_exp_years,
        min_experience   = min_experience,
        cand_edu_level   = cand_edu_level,
        required_edu     = required_edu,
    )

    return {
        'final_score':      final_score,
        'skill_score':      skill_score,
        'experience_score': experience_score,
        'education_score':  education_score,
        'missing_skills':   missing_skills,
        'matched_skills':   matched_required,
        'explanation':      explanation,
    }


def _generate_explanation(candidate_name, skill_score, experience_score,
                           education_score, final_score, matched_required,
                           missing_skills, cand_exp_years, min_experience,
                           cand_edu_level, required_edu) -> str:
    """
    Generate a human-readable explanation of the score.
    This is the TRANSPARENCY feature of Fair Hire AI.
    """
    lines = [f"Score Breakdown for {candidate_name}:"]
    lines.append(f"Overall Match: {final_score}%")
    lines.append("")

    # Skills explanation
    lines.append(f"Skills ({skill_score}%):")
    if matched_required:
        lines.append(f"  ✓ Matched: {', '.join(matched_required)}")
    if missing_skills:
        lines.append(f"  ✗ Missing: {', '.join(missing_skills)}")
    if not missing_skills:
        lines.append("  ✓ All required skills present")

    # Experience explanation
    lines.append(f"\nExperience ({experience_score}%):")
    if min_experience == 0:
        lines.append("  ✓ No minimum experience required")
    elif cand_exp_years >= min_experience:
        lines.append(f"  ✓ Has {cand_exp_years} years (required: {min_experience}+)")
    else:
        lines.append(f"  ✗ Has {cand_exp_years} years (required: {min_experience}+)")

    # Education explanation
    lines.append(f"\nEducation ({education_score}%):")
    if education_score == 100:
        lines.append(f"  ✓ {cand_edu_level or 'Education'} meets requirement ({required_edu})")
    else:
        lines.append(f"  ✗ {cand_edu_level or 'Unknown'} — required: {required_edu}")

    # Final verdict
    lines.append("")
    if final_score >= 80:
        lines.append("Verdict: Strong match — recommended for interview.")
    elif final_score >= 60:
        lines.append("Verdict: Partial match — consider for review.")
    elif final_score >= 40:
        lines.append("Verdict: Weak match — missing key requirements.")
    else:
        lines.append("Verdict: Poor match — does not meet requirements.")

    return "\n".join(lines)


def rank_candidates(candidates, job, adaptive_threshold=True) -> list:
    """
    Score and rank all candidates against a job.

    ADAPTIVE THRESHOLD FEATURE:
    If no candidate scores above 60%, automatically lower the bar
    so HR always gets some results.

    Args:
        candidates : list of Candidate model instances
        job        : Job model instance or dict
        adaptive_threshold : if True, auto-adjust when results are empty

    Returns:
        list of dicts sorted by final_score descending
    """
    results = []

    for candidate in candidates:
        scores = score_candidate(candidate, job)
        results.append({
            'candidate_id':   candidate.id,
            'candidate_name': candidate.name or candidate.original_name,
            'email':          candidate.email,
            'phone':          candidate.phone,
            'location':       candidate.location,
            'experience_years': candidate.experience_years,
            'education_level':  candidate.education_level,
            'skills':         candidate.skills,
            'status':         candidate.status,
            **scores,
        })

    # Sort by final score (highest first)
    results.sort(key=lambda x: x['final_score'], reverse=True)

    # ── ADAPTIVE THRESHOLD ENGINE ──────────────────────────
    # If all candidates score below 60, lower threshold
    # This is a unique feature of Fair Hire AI
    if adaptive_threshold and results:
        good_matches = [r for r in results if r['final_score'] >= 60]
        if not good_matches:
            # No good matches — add a note to all results
            for r in results:
                r['explanation'] += (
                    "\n\n[Adaptive Threshold] No candidate met the 60% threshold. "
                    "Showing best available matches. Consider updating job requirements."
                )

    return results