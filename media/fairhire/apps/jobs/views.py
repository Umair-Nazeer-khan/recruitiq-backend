# fairhire/apps/jobs/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Job
from .serializers import JobSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def job_list_create(request):
    """
    GET  /api/v1/jobs/  — list all jobs for this HR user
    POST /api/v1/jobs/  — create a new job post
    """
    if request.method == 'GET':
        jobs = Job.objects.filter(created_by=request.user)
        return Response(JobSerializer(jobs, many=True).data)

    serializer = JobSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def job_detail(request, pk):
    """
    GET    /api/v1/jobs/<id>/  — get one job
    PUT    /api/v1/jobs/<id>/  — update job
    DELETE /api/v1/jobs/<id>/  — delete job
    """
    try:
        job = Job.objects.get(pk=pk, created_by=request.user)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=404)

    if request.method == 'GET':
        return Response(JobSerializer(job).data)

    if request.method == 'PUT':
        serializer = JobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=400)

    if request.method == 'DELETE':
        job.delete()
        return Response({'message': 'Job deleted.'}, status=204)
