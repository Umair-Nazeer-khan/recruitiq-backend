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
    """
    Convert education level string to numeric rank.
    Handles combined labels like 'MSc / MS' or 'BSc / BE' by splitting
    on common separators and taking the highest rank found among the
    parts — a plain exact-match lookup was silently failing for any
    label that wasn't a pre-listed exact string (e.g. 'msc / ms' was
    never in the dict, only 'msc' and 'ms' separately), which made the
    requirement act as if it were unset.
    """
    if not level:
        return 0
    level = level.lower().strip()

    if level in EDU_RANK:
        return EDU_RANK[level]

    best = 0
    for part in re.split(r'[/,&]', level):
        part = part.strip()
        if part in EDU_RANK:
            best = max(best, EDU_RANK[part])
    return best


def _normalize_skill(s: str) -> str:
    """
    Normalize a skill string for comparison so trivial differences like
    'REST APIs' vs 'rest api' don't cause a false 'missing skill' —
    lowercase, strip punctuation, collapse whitespace, and drop a
    trailing 's' for simple pluralization (but not for short words like
    'js' or 'css', where the 's' is part of the name itself).
    """
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > 3 and s.endswith('s') and not s.endswith('ss'):
        s = s[:-1]
    return s


def score_candidate(candidate, job) -> dict:
    """
    Score a single candidate against a job.

    Args:
        candidate : Candidate model instance
        job       : Job model instance (or dict with same fields)

    Returns:
        dict with skill_score, experience_score, education_score,
             final_score, missing_skills, explanation
    """
    # ── Get job data ───────────────────────────────────────────
    if isinstance(job, dict):
        required_skills   = [s.lower() for s in job.get('required_skills', [])]
        optional_skills   = [s.lower() for s in job.get('optional_skills', [])]
        min_experience    = job.get('min_experience', 0)
        required_edu      = job.get('education_level', '')
        skill_weight      = job.get('skill_weight', 0.5)
        experience_weight = job.get('experience_weight', 0.3)
        education_weight  = job.get('education_weight', 0.2)
        job_description   = ' '.join(required_skills + optional_skills)
    else:
        required_skills   = [s.lower() for s in (job.required_skills or [])]
        optional_skills   = [s.lower() for s in (job.optional_skills or [])]
        min_experience    = job.min_experience or 0
        required_edu      = job.education_level or ''
        skill_weight      = job.skill_weight or 0.5
        experience_weight = job.experience_weight or 0.3
        education_weight  = job.education_weight or 0.2
        job_description   = ' '.join(required_skills + optional_skills)

    # ── Get candidate data ─────────────────────────────────────
    cand_skills      = [s.lower() for s in (candidate.skills or [])]
    cand_exp_years   = candidate.experience_years or 0
    cand_edu_level   = candidate.education_level or ''
    cand_raw_text    = candidate.raw_text or ''

    # ══════════════════════════════════════════════════════════
    #  1. SKILL SCORE
    # ══════════════════════════════════════════════════════════
    cand_skills_norm     = [_normalize_skill(s) for s in cand_skills]
    required_skills_norm = [_normalize_skill(s) for s in required_skills]
    optional_skills_norm = [_normalize_skill(s) for s in optional_skills]

    matched_required = [orig for orig, norm in zip(required_skills, required_skills_norm)
                        if norm in cand_skills_norm]
    matched_optional = [orig for orig, norm in zip(optional_skills, optional_skills_norm)
                        if norm in cand_skills_norm]
    missing_skills   = [orig for orig, norm in zip(required_skills, required_skills_norm)
                        if norm not in cand_skills_norm]

    if required_skills:
        # Required skills = 80% of skill score
        # Optional skills = 20% of skill score
        req_score  = len(matched_required) / len(required_skills) * 80
        opt_score  = (len(matched_optional) / len(optional_skills) * 20) if optional_skills else 20
        skill_base = req_score + opt_score
    else:
        skill_base = 100.0

    # Boost with TF-IDF cosine similarity if we have resume text
    tfidf_score = 0.0
    if cand_raw_text and job_description:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([job_description, cand_raw_text])
            similarity   = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            tfidf_score  = float(similarity) * 100
        except Exception:
            tfidf_score = 0.0

    # Combine: 70% keyword match + 30% TF-IDF similarity
    skill_score = (skill_base * 0.7) + (tfidf_score * 0.3)
    skill_score = min(100.0, round(skill_score, 1))

    # ══════════════════════════════════════════════════════════
    #  2. EXPERIENCE SCORE
    # ══════════════════════════════════════════════════════════
    if min_experience == 0:
        experience_score = 100.0
    elif cand_exp_years >= min_experience:
        # Give bonus for extra experience (max 100)
        experience_score = min(100.0, 100 + (cand_exp_years - min_experience) * 5)
    else:
        # Partial score for less experience
        experience_score = round((cand_exp_years / min_experience) * 100, 1)

    experience_score = round(experience_score, 1)

    # ══════════════════════════════════════════════════════════
    #  3. EDUCATION SCORE
    # ══════════════════════════════════════════════════════════
    required_rank = get_edu_rank(required_edu)
    cand_rank     = get_edu_rank(cand_edu_level)

    if required_rank == 0:
        education_score = 100.0
    elif cand_rank >= required_rank:
        education_score = 100.0  # meets or exceeds requirement
    elif cand_rank == 0:
        education_score = 50.0   # unknown education level
    else:
        education_score = round((cand_rank / required_rank) * 100, 1)

    # ══════════════════════════════════════════════════════════
    #  4. FINAL WEIGHTED SCORE
    # ══════════════════════════════════════════════════════════
    final_score = (
        skill_score      * skill_weight +
        experience_score * experience_weight +
        education_score  * education_weight
    )
    final_score = round(final_score, 1)

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