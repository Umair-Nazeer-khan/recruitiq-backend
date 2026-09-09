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

        name = (value.name or '').strip().strip('"').strip("'")
        ext = os.path.splitext(name)[1].lower()

        if ext not in allowed:
            # Filename/extension can get lost or mangled by some mobile
            # file-picker + multipart-upload combinations even though the
            # file itself is a valid, supported type. Fall back to
            # checking the actual file content ("magic bytes") before
            # rejecting it outright.
            detected_ext = self._detect_extension_from_content(value)
            if detected_ext:
                ext = detected_ext
            else:
                raise serializers.ValidationError(
                    f'File type not supported. Use: {", ".join(allowed)}')

        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('File too large. Max size: 10 MB')
        return value

    @staticmethod
    def _detect_extension_from_content(value):
        """Peek at the first bytes of the file to identify its real type,
        regardless of what the filename/extension says."""
        try:
            value.seek(0)
            header = value.read(8)
            value.seek(0)
        except Exception:
            return None

        if header.startswith(b'%PDF'):
            return '.pdf'
        if header.startswith(b'PK\x03\x04'):
            # DOCX (and modern .doc saved as OOXML) are zip-based
            return '.docx'
        if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
            # Legacy .doc (OLE compound file)
            return '.doc'
        # Plain text has no reliable signature — accept if it decodes as text
        try:
            header.decode('utf-8')
            return '.txt'
        except UnicodeDecodeError:
            return None


class UpdateStatusSerializer(serializers.Serializer):
    """Used to update candidate status."""
    status   = serializers.ChoiceField(choices=['pending', 'shortlisted', 'accepted', 'rejected', 'on_hold'])
    hr_notes = serializers.CharField(required=False, allow_blank=True)
