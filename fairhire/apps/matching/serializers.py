from rest_framework import serializers


class MatchRequestSerializer(serializers.Serializer):
    """Validate a saved-job match request or an inline job definition."""

    job_id = serializers.IntegerField(required=False, min_value=1)
    title = serializers.CharField(required=False, allow_blank=True, max_length=200)
    required_skills = serializers.ListField(
        required=False,
        child=serializers.CharField(allow_blank=False, trim_whitespace=True),
        allow_empty=True,
    )
    optional_skills = serializers.ListField(
        required=False,
        child=serializers.CharField(allow_blank=False, trim_whitespace=True),
        allow_empty=True,
    )
    min_experience = serializers.FloatField(required=False, min_value=0)
    education_level = serializers.CharField(required=False, allow_blank=True, max_length=50)
    skill_weight = serializers.FloatField(required=False, min_value=0, max_value=1)
    experience_weight = serializers.FloatField(required=False, min_value=0, max_value=1)
    education_weight = serializers.FloatField(required=False, min_value=0, max_value=1)

    def validate(self, data):
        if data.get('job_id') is not None:
            return data

        missing = [
            field for field in ('required_skills', 'min_experience', 'education_level')
            if field not in data
        ]
        if missing:
            raise serializers.ValidationError({field: 'This field is required for inline matching.' for field in missing})

        weights = [
            data.get('skill_weight', 0.5),
            data.get('experience_weight', 0.3),
            data.get('education_weight', 0.2),
        ]
        if abs(sum(weights) - 1.0) > 0.02:
            raise serializers.ValidationError(
                'skill_weight, experience_weight, and education_weight must sum to 1.0.'
            )
        return data
