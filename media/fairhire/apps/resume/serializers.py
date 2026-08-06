# fairhire/apps/resume/serializers.py
from rest_framework import serializers
from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    """Full candidate data — used for detail view."""
    class Meta:
        model  = Candidate
        fields = [
            'id', 'name', 'email', 'phone', 'location',
            'education', 'education_level', 'experience_years',
            'skills', 'work_history', 'match_score', 'skill_score',
            'experience_score', 'education_score', 'missing_skills',
            'score_explanation', 'status', 'hr_notes',
            'original_name', 'created_at',
        ]


class CandidateListSerializer(serializers.ModelSerializer):
    """Compact candidate data — used for list/dashboard views."""
    class Meta:
        model  = Candidate
        fields = [
            'id', 'name', 'email', 'experience_years', 'education_level',
            'skills', 'match_score', 'status', 'created_at',
        ]


class UploadResumeSerializer(serializers.Serializer):
    """Used for the upload endpoint."""
    file = serializers.FileField()

    def validate_file(self, value):
        allowed = ['.pdf', '.docx', '.doc', '.txt']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed:
            raise serializers.ValidationError(f'File type not supported. Use: {", ".join(allowed)}')
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('File too large. Max size: 10 MB')
        return value


class UpdateStatusSerializer(serializers.Serializer):
    """Used to update candidate status."""
    status   = serializers.ChoiceField(choices=['pending', 'shortlisted', 'accepted', 'rejected', 'on_hold'])
    hr_notes = serializers.CharField(required=False, allow_blank=True)
