# fairhire/apps/jobs/serializers.py
from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'department', 'location', 'job_type',
            'required_skills', 'optional_skills', 'min_experience',
            'education_level', 'salary_min', 'salary_max',
            'skill_weight', 'experience_weight', 'education_weight',
            'is_active', 'created_at',
        ]

    def validate(self, data):
        # Weights must sum to ~1.0
        sw = data.get('skill_weight',      0.5)
        ew = data.get('experience_weight', 0.3)
        dw = data.get('education_weight',  0.2)
        total = round(sw + ew + dw, 2)
        if not (0.98 <= total <= 1.02):
            raise serializers.ValidationError(
                f'Skill + Experience + Education weights must sum to 1.0 (got {total})'
            )
        return data
