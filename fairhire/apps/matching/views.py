# fairhire/apps/matching/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fairhire.apps.resume.models import Candidate
from fairhire.apps.jobs.models import Job
from .engine import rank_candidates, score_candidate


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def match_candidates(request):
    """
    Run AI matching — score all candidates against a job.

    Flutter Job Requirements screen calls this after
    the HR manager fills in the job form.

    Flutter sends:
    {
        "job_id": 1,              ← optional, if job already saved
        "title": "Flutter Dev",
        "required_skills": ["Flutter", "Dart"],
        "optional_skills": ["Python"],
        "min_experience": 2,
        "education_level": "BSc / BE",
        "skill_weight": 0.5,
        "experience_weight": 0.3,
        "education_weight": 0.2
    }

    Returns ranked list of all candidates with scores.
    """
    data = request.data

    # Get all candidates for this HR user
    candidates = Candidate.objects.filter(uploaded_by=request.user)

    if not candidates.exists():
        return Response({
            'message': 'No candidates found. Upload resumes first.',
            'results': [],
            'stats':   {'total': 0, 'good_match': 0, 'partial': 0, 'no_match': 0},
        })

    # If job_id provided, load from DB
    job_id = data.get('job_id')
    if job_id:
        try:
            job = Job.objects.get(pk=job_id, created_by=request.user)
            ranked = rank_candidates(list(candidates), job)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found.'}, status=404)
    else:
        # Use job data directly from request
        ranked = rank_candidates(list(candidates), data)

    # Save scores back to each candidate in DB
    for result in ranked:
        try:
            candidate = Candidate.objects.get(pk=result['candidate_id'])
            candidate.match_score       = result['final_score']
            candidate.skill_score       = result['skill_score']
            candidate.experience_score  = result['experience_score']
            candidate.education_score   = result['education_score']
            candidate.missing_skills    = result['missing_skills']
            candidate.score_explanation = result['explanation']
            candidate.save(update_fields=[
                'match_score', 'skill_score', 'experience_score',
                'education_score', 'missing_skills', 'score_explanation'
            ])
        except Candidate.DoesNotExist:
            pass

    # Calculate summary stats
    good_match = len([r for r in ranked if r['final_score'] >= 80])
    partial    = len([r for r in ranked if 60 <= r['final_score'] < 80])
    no_match   = len([r for r in ranked if r['final_score'] < 60])

    return Response({
        'message': f'Matched {len(ranked)} candidates.',
        'stats': {
            'total':      len(ranked),
            'good_match': good_match,
            'partial':    partial,
            'no_match':   no_match,
        },
        'results': ranked,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_results(request):
    """
    Get previously matched candidates sorted by score.

    Flutter Match Results screen uses this to reload results.
    Optional: ?min_score=60  to filter by minimum score
    """
    qs = Candidate.objects.filter(
        uploaded_by=request.user,
        match_score__isnull=False
    ).order_by('-match_score')

    # Optional score filter
    min_score = request.query_params.get('min_score')
    if min_score:
        try:
            qs = qs.filter(match_score__gte=float(min_score))
        except ValueError:
            pass

    results = []
    for c in qs:
        results.append({
            'candidate_id':     c.id,
            'candidate_name':   c.name,
            'email':            c.email,
            'experience_years': c.experience_years,
            'education_level':  c.education_level,
            'skills':           c.skills,
            'final_score':      c.match_score,
            'skill_score':      c.skill_score,
            'experience_score': c.experience_score,
            'education_score':  c.education_score,
            'missing_skills':   c.missing_skills,
            'explanation':      c.score_explanation,
            'status':           c.status,
        })

    return Response({
        'count':   len(results),
        'results': results,
    })
