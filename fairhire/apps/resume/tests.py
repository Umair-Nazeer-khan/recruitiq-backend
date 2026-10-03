from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import update_status


class CandidateStatusTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)
        self.candidate = SimpleNamespace(
            id=1,
            match_score=None,
            status='pending',
            hr_notes='',
            save=Mock(),
        )

    def patch_status(self, status):
        request = self.factory.patch(
            '/api/v1/resumes/1/status/',
            {'status': status},
            format='json',
        )
        force_authenticate(request, user=self.user)
        with patch(
            'fairhire.apps.resume.views.Candidate.objects.get',
            return_value=self.candidate,
        ):
            return update_status(request, pk=1)

    def test_accept_reject_are_not_candidate_level_statuses(self):
        for status in ('accepted', 'rejected'):
            with self.subTest(status=status):
                self.candidate.status = 'pending'
                self.candidate.save.reset_mock()

                response = self.patch_status(status)

                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.candidate.status, 'pending')
                self.candidate.save.assert_not_called()

    def test_unscored_candidate_can_be_shortlisted(self):
        response = self.patch_status('shortlisted')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.candidate.status, 'shortlisted')
        self.candidate.save.assert_called_once()

    def test_candidate_level_status_remains_separate_after_scoring(self):
        self.candidate.match_score = 74.5

        response = self.patch_status('shortlisted')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.candidate.status, 'shortlisted')
        self.candidate.save.assert_called_once()