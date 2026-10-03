from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fairhire.apps.jobs.models import Job
from fairhire.apps.resume.models import Candidate
from .engine import rank_candidates
from .models import CandidateEvaluation
from .serializers import EvaluationDecisionSerializer, MatchRequestSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def match_candidates(request):
    serializer = MatchRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    job = get_object_or_404(Job, pk=data['job_id'], created_by=request.user)
    if not job.is_active:
        return Response({'error': 'This job is inactive.'}, status=status.HTTP_400_BAD_REQUEST)

    candidates = Candidate.objects.filter(uploaded_by=request.user)
    if data.get('candidate_id') is not None:
        candidates = candidates.filter(pk=data['candidate_id'])
        if not candidates.exists():
            return Response({'error': 'Candidate not found.'}, status=status.HTTP_404_NOT_FOUND)

    candidates = list(candidates)
    if not candidates:
        return Response({
            'message': 'No candidates found. Upload resumes first.',
            'job_id': job.id,
            'job_title': job.title,
            'results': [],
            'stats': {'total': 0, 'good_match': 0, 'partial': 0, 'no_match': 0},
        })

    evaluations = {}
    for candidate in candidates:
        evaluation, _ = CandidateEvaluation.objects.get_or_create(
            candidate=candidate,
            job=job,
            defaults={'evaluation_status': 'processing'},
        )
        evaluation.evaluation_status = 'processing'
        evaluation.decision_status = 'new'
        evaluation.save(update_fields=['evaluation_status', 'decision_status', 'updated_at'])
        evaluations[candidate.id] = evaluation

    try:
        ranked = rank_candidates(candidates, job)
    except Exception:
        CandidateEvaluation.objects.filter(pk__in=[e.pk for e in evaluations.values()]).update(
            evaluation_status='failed',
            updated_at=timezone.now(),
        )
        return Response(
            {'error': 'Candidate evaluation failed. Please retry.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    results = []
    with transaction.atomic():
        for result in ranked:
            evaluation = evaluations[result['candidate_id']]
            evaluation.evaluation_status = 'evaluated'
            evaluation.match_score = result['final_score']
            evaluation.skill_score = result['skill_score']
            evaluation.experience_score = result['experience_score']
            evaluation.education_score = result['education_score']
            evaluation.matched_skills = result['matched_skills']
            evaluation.missing_skills = result['missing_skills']
            evaluation.explanation = result['explanation']
            evaluation.evaluated_at = timezone.now()
            evaluation.save()

            result.update({
                'evaluation_id': evaluation.id,
                'evaluation_status': evaluation.evaluation_status,
                'decision_status': evaluation.decision_status,
                'job_id': job.id,
                'job_title': job.title,
            })
            candidate = next(item for item in candidates if item.id == result['candidate_id'])
            result['original_name'] = candidate.original_name
            result['education'] = candidate.education
            results.append(result)

    good_match = sum(1 for result in results if result['final_score'] >= 80)
    partial_match = sum(1 for result in results if 60 <= result['final_score'] < 80)
    no_match = sum(1 for result in results if result['final_score'] < 60)

    return Response({
        'message': f'Evaluated {len(results)} candidate(s) for {job.title}.',
        'job_id': job.id,
        'job_title': job.title,
        'stats': {
            'total': len(results),
            'good_match': good_match,
            'partial': partial_match,
            'no_match': no_match,
        },
        'results': results,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_results(request):
    job_id = request.query_params.get('job_id')
    if not job_id:
        return Response({'error': 'job_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    job = get_object_or_404(Job, pk=job_id, created_by=request.user)
    evaluations = CandidateEvaluation.objects.filter(
        job=job,
        evaluation_status='evaluated',
    ).select_related('candidate')

    min_score = request.query_params.get('min_score')
    if min_score:
        try:
            evaluations = evaluations.filter(match_score__gte=float(min_score))
        except ValueError:
            return Response({'error': 'min_score must be numeric.'}, status=status.HTTP_400_BAD_REQUEST)

    results = [{
        'evaluation_id': evaluation.id,
        'evaluation_status': evaluation.evaluation_status,
        'decision_status': evaluation.decision_status,
        'job_id': job.id,
        'job_title': job.title,
        'candidate_id': evaluation.candidate_id,
        'candidate_name': evaluation.candidate.name or evaluation.candidate.original_name,
        'original_name': evaluation.candidate.original_name,
        'email': evaluation.candidate.email,
        'phone': evaluation.candidate.phone,
        'location': evaluation.candidate.location,
        'education': evaluation.candidate.education,
        'experience_years': evaluation.candidate.experience_years,
        'education_level': evaluation.candidate.education_level,
        'skills': evaluation.candidate.skills,
        'final_score': evaluation.match_score,
        'skill_score': evaluation.skill_score,
        'experience_score': evaluation.experience_score,
        'education_score': evaluation.education_score,
        'matched_skills': evaluation.matched_skills,
        'missing_skills': evaluation.missing_skills,
        'explanation': evaluation.explanation,
        'status': evaluation.candidate.status,
    } for evaluation in evaluations.order_by('-match_score')]

    good_match = sum(1 for result in results if result['final_score'] >= 80)
    partial_match = sum(1 for result in results if 60 <= result['final_score'] < 80)
    no_match = sum(1 for result in results if result['final_score'] < 60)

    return Response({
        'job_id': job.id,
        'job_title': job.title,
        'count': len(results),
        'stats': {
            'total': len(results),
            'good_match': good_match,
            'partial': partial_match,
            'no_match': no_match,
        },
        'results': results,
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_evaluation_decision(request, evaluation_id):
    evaluation = get_object_or_404(
        CandidateEvaluation.objects.select_related('job'),
        pk=evaluation_id,
        job__created_by=request.user,
    )
    if evaluation.evaluation_status != 'evaluated':
        return Response(
            {'error': 'Complete the job evaluation before making a decision.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = EvaluationDecisionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    evaluation.decision_status = serializer.validated_data['decision_status']
    evaluation.save(update_fields=['decision_status', 'updated_at'])
    return Response({
        'evaluation_id': evaluation.id,
        'job_id': evaluation.job_id,
        'decision_status': evaluation.decision_status,
    })