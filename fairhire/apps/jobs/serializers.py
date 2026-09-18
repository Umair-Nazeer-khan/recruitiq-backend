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
        sw = data.get('skill_weight',      0.5)
        ew = data.get('experience_weight', 0.3)
        dw = data.get('education_weight',  0.2)

        for name, value in [('skill_weight', sw), ('experience_weight', ew),
                            ('education_weight', dw)]:
            if value < 0:
                raise serializers.ValidationError(f'{name} cannot be negative.')

        total = round(sw + ew + dw, 2)
        if not (0.98 <= total <= 1.02):
            raise serializers.ValidationError(
                f'Skill + Experience + Education weights must sum to 1.0 (got {total})'
            )

        min_exp = data.get('min_experience', 0)
        if min_exp is not None and min_exp < 0:
            raise serializers.ValidationError('min_experience cannot be negative.')

        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min is not None and salary_min < 0:
            raise serializers.ValidationError('salary_min cannot be negative.')
        if salary_max is not None and salary_max < 0:
            raise serializers.ValidationError('salary_max cannot be negative.')
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError('salary_min cannot be greater than salary_max.')

        return data
