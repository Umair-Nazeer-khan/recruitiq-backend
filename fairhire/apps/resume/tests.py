from types import SimpleNamespace
import json
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import update_status
from . import parser


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


class ResumeProviderFallbackTests(SimpleTestCase):
    def test_gemini_success_skips_groq(self):
        gemini_result = {'name': 'Maya Chen'}
        with (
            patch.object(parser, '_parse_with_gemini', return_value=gemini_result),
            patch.object(parser, '_parse_with_groq') as groq_parser,
        ):
            result = parser.parse_resume('resume text')

        self.assertIs(result, gemini_result)
        groq_parser.assert_not_called()

    def test_groq_runs_when_gemini_fails(self):
        groq_result = {'name': 'Maya Chen'}
        with (
            patch.object(parser, '_parse_with_gemini', return_value=None),
            patch.object(parser, '_parse_with_groq', return_value=groq_result) as groq_parser,
            patch.object(parser, 'parse_resume_rule_based') as rule_parser,
        ):
            result = parser.parse_resume('resume text')

        self.assertIs(result, groq_result)
        groq_parser.assert_called_once_with('resume text')
        rule_parser.assert_not_called()

    def test_rule_parser_runs_when_both_providers_fail(self):
        rule_result = {'name': 'Maya Chen'}
        with (
            patch.object(parser, '_parse_with_gemini', return_value=None),
            patch.object(parser, '_parse_with_groq', return_value=None),
            patch.object(parser, 'parse_resume_rule_based', return_value=rule_result) as rule_parser,
        ):
            result = parser.parse_resume('resume text')

        self.assertIs(result, rule_result)
        rule_parser.assert_called_once_with('resume text')

    @patch.object(parser, 'GROQ_API_KEY', 'test-key')
    @patch('requests.post')
    def test_groq_response_is_normalized(self, post):
        post.return_value.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'name': 'Maya Chen',
                        'email': 'maya@example.com',
                        'skills': ['Python'],
                        'experience_years': 4,
                        'education_level': 'Bachelor',
                        'work_history': [{'company': 'Example Co', 'role': 'Engineer'}],
                    }),
                },
            }],
        }

        result = parser._parse_with_groq('Maya Chen resume text')

        self.assertEqual(result['name'], 'Maya Chen')
        self.assertEqual(result['email'], 'maya@example.com')
        self.assertEqual(result['skills'], ['Python'])
        self.assertEqual(result['experience_years'], 4.0)
        self.assertEqual(result['raw_text'], 'Maya Chen resume text')
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Bearer test-key')