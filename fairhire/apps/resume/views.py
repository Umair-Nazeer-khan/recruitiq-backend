# fairhire/apps/resume/views.py
# ─────────────────────────────────────────────────────────────────
#  Resume / Candidate views.
# ─────────────────────────────────────────────────────────────────

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Candidate
from .serializers import (
    CandidateSerializer, CandidateListSerializer,
    UploadResumeSerializer, UpdateStatusSerializer
)
from .parser import extract_text, parse_resume


# ──────────────────────────────────────────────
#  POST /api/v1/resumes/upload/
# ──────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_resume(request):
    """
    Upload a resume file. AI parses it and returns structured data.

    Flutter sends:
        multipart/form-data  with field: file = <resume.pdf>

    Returns:
        { candidate: { id, name, email, skills, ... } }
    """
    serializer = UploadResumeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=400)

    file = serializer.validated_data['file']

    # Save to disk first
    candidate = Candidate.objects.create(
        uploaded_by   = request.user,
        resume_file   = file,
        original_name = file.name,
    )

    # Parse with AI
    try:
        file_path = candidate.resume_file.path
        raw_text  = extract_text(file_path)
        parsed    = parse_resume(raw_text)

        candidate.name             = parsed.get('name', '')
        candidate.email            = parsed.get('email', '')
        candidate.phone            = parsed.get('phone', '')
        candidate.location         = parsed.get('location', '')
        candidate.education        = parsed.get('education', '')
        candidate.education_level  = parsed.get('education_level', '')
        candidate.experience_years = parsed.get('experience_years', 0)
        candidate.skills           = parsed.get('skills', [])
        candidate.work_history     = parsed.get('work_history', [])
        candidate.raw_text         = parsed.get('raw_text', '')
        candidate.save()

        return Response({
            'message':   'Resume parsed successfully.',
            'candidate': CandidateSerializer(
                candidate, context={'request': request}
            ).data,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        candidate.delete()
        return Response({'error': f'Failed to parse resume: {str(e)}'}, status=500)


# ──────────────────────────────────────────────
#  GET /api/v1/resumes/
# ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_candidates(request):
    """
    Get all candidates uploaded by this HR user.
    Optional filter: ?status=shortlisted

    Flutter Dashboard and Shortlist screens use this.
    """
    qs = Candidate.objects.filter(uploaded_by=request.user)

    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    serializer = CandidateListSerializer(qs, many=True)
    return Response({
        'count':      qs.count(),
        'candidates': serializer.data,
    })


# ──────────────────────────────────────────────
#  GET /api/v1/resumes/<id>/
# ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidate_detail(request, pk):
    """
    Get full candidate details.
    Flutter Candidate Profile screen uses this.
    """
    try:
        candidate = Candidate.objects.get(pk=pk, uploaded_by=request.user)
        return Response(
            CandidateSerializer(candidate, context={'request': request}).data
        )
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found.'}, status=404)


# ──────────────────────────────────────────────
#  PATCH /api/v1/resumes/<id>/status/
# ──────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_status(request, pk):
    """
    Update candidate status (shortlist/accept/reject/hold).

    Flutter Shortlist screen uses this.

    Flutter sends:
        { "status": "accepted", "hr_notes": "Great fit for backend role" }
    """
    try:
        candidate = Candidate.objects.get(pk=pk, uploaded_by=request.user)
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found.'}, status=404)

    serializer = UpdateStatusSerializer(data=request.data)
    if serializer.is_valid():
        candidate.status   = serializer.validated_data['status']
        candidate.hr_notes = serializer.validated_data.get('hr_notes', candidate.hr_notes)
        candidate.save(update_fields=['status', 'hr_notes'])
        return Response({
            'message':  'Status updated.',
            'id':       candidate.id,
            'status':   candidate.status,
        })
    return Response({'errors': serializer.errors}, status=400)


# ──────────────────────────────────────────────
#  GET /api/v1/resumes/stats/
# ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Summary stats for the Flutter Dashboard screen.

    Returns:
        { total_cvs, shortlisted, accepted, rejected, pending }
    """
    qs = Candidate.objects.filter(uploaded_by=request.user)
    return Response({
        'total_cvs':   qs.count(),
        'shortlisted': qs.filter(status='shortlisted').count(),
        'accepted':    qs.filter(status='accepted').count(),
        'rejected':    qs.filter(status='rejected').count(),
        'pending':     qs.filter(status='pending').count(),
        'on_hold':     qs.filter(status='on_hold').count(),
    })
