from rest_framework import serializers


class MatchRequestSerializer(serializers.Serializer):
    """An evaluation must always belong to a saved job requirement."""

    job_id = serializers.IntegerField(required=True, min_value=1)
    candidate_id = serializers.IntegerField(required=False, min_value=1)


class EvaluationDecisionSerializer(serializers.Serializer):
    decision_status = serializers.ChoiceField(choices=['accepted', 'rejected', 'on_hold'])
