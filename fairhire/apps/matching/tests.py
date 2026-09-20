from types import SimpleNamespace

from django.test import SimpleTestCase

from .engine import _normalize_weights, get_edu_rank, score_candidate
from fairhire.apps.resume.parser import parse_resume_rule_based


def _fake_candidate(**overrides):
    defaults = dict(
        id=1,
        name='Test Candidate',
        original_name='resume.pdf',
        email='t@example.com',
        phone='',
        location='Lahore',
        skills=['Python', 'Django'],
        experience_years=2,
        education_level='BSc',
        raw_text='Python Django developer with REST API experience',
        status='pending',
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class MatchScoreBoundsTests(SimpleTestCase):
    def test_normal_job_produces_valid_score(self):
        result = score_candidate(_fake_candidate(), {
            'required_skills': ['python'], 'min_experience': 1,
            'education_level': 'BSc / BE',
            'skill_weight': 0.5, 'experience_weight': 0.3, 'education_weight': 0.2,
        })
        self.assertLessEqual(result['final_score'], 100)
        self.assertGreaterEqual(result['final_score'], 0)

    def test_negative_and_oversized_weights_still_bounded(self):
        result = score_candidate(_fake_candidate(), {
            'required_skills': ['python'], 'min_experience': 0,
            'education_level': 'BSc / BE',
            'skill_weight': -10, 'experience_weight': 5, 'education_weight': 6,
        })
        self.assertLessEqual(result['final_score'], 100)
        self.assertGreaterEqual(result['final_score'], 0)

    def test_negative_min_experience_does_not_crash(self):
        result = score_candidate(_fake_candidate(), {
            'required_skills': ['python'], 'min_experience': -5,
            'education_level': 'BSc / BE',
            'skill_weight': 0.5, 'experience_weight': 0.3, 'education_weight': 0.2,
        })
        self.assertLessEqual(result['final_score'], 100)

    def test_all_zero_weights_falls_back_to_defaults(self):
        weights = _normalize_weights(0, 0, 0)
        self.assertAlmostEqual(sum(weights), 1.0, places=2)

    def test_weights_always_sum_to_one_after_normalization(self):
        weights = _normalize_weights(2, 5, 13)
        self.assertAlmostEqual(sum(weights), 1.0, places=2)


class EducationRankTests(SimpleTestCase):
    def test_combined_bachelor_label(self):
        self.assertEqual(get_edu_rank('BSc / BE'), 3)

    def test_combined_masters_label(self):
        self.assertEqual(get_edu_rank('MSc / MS'), 4)

    def test_unknown_label_returns_zero(self):
        self.assertEqual(get_edu_rank('Some Made Up Degree'), 0)

    def test_empty_string_returns_zero(self):
        self.assertEqual(get_edu_rank(''), 0)


class SkillMatchingTests(SimpleTestCase):
    def test_required_skill_matched(self):
        result = score_candidate(_fake_candidate(skills=['REST APIs', 'Python']), {
            'required_skills': ['rest api'], 'min_experience': 0,
            'education_level': '',
            'skill_weight': 1.0, 'experience_weight': 0.0, 'education_weight': 0.0,
        })
        self.assertIn('rest api', [skill.lower() for skill in result['matched_skills']])

    def test_missing_skill_reported(self):
        result = score_candidate(_fake_candidate(skills=['Python']), {
            'required_skills': ['java'], 'min_experience': 0,
            'education_level': '',
            'skill_weight': 1.0, 'experience_weight': 0.0, 'education_weight': 0.0,
        })
        self.assertIn('java', [skill.lower() for skill in result['missing_skills']])


class ResumeParsingTests(SimpleTestCase):
    def test_work_history_keeps_all_bullets_without_leaking_next_company(self):
        text = '''
EXPERIENCE
First Company
Engineer | 2022 - 2023
\uf0b7 Built the API
\uf0b7 Improved response time
Second Company
Developer | 2023 - Present
\uf0b7 Delivered the mobile app
'''

        parsed = parse_resume_rule_based(text)

        self.assertEqual(parsed['work_history'][0]['bullets'], [
            'Built the API',
            'Improved response time',
        ])
        self.assertNotIn('Second Company', parsed['work_history'][0]['bullets'])
        self.assertEqual(parsed['work_history'][1]['bullets'], ['Delivered the mobile app'])

    def test_real_cv_structure_is_parsed_cleanly(self):
        text = '''
MUHAMMAD ALI
Email: ali@gmail.com | Phone: +92 300 1234567
Lahore, Pakistan

PROFESSIONAL SUMMARY
Python and Django developer with 3 years experience in web applications.

SKILLS
Python, Django, REST API, React, SQL, Docker, Git

EDUCATION
BSCS, University of Lahore, 2018 - 2022

EXPERIENCE
Software Engineer
ABC Tech | Lahore | 2022 - Present
- Built APIs with Django and REST framework
'''
        parsed = parse_resume_rule_based(text)
        self.assertEqual(parsed['name'], 'MUHAMMAD ALI')
        self.assertIn('python', [skill.lower() for skill in parsed['skills']])
        self.assertEqual(parsed['experience_years'], 3.0)
        self.assertEqual(parsed['work_history'][0]['company'], 'ABC Tech')
        self.assertEqual(parsed['work_history'][0]['role'], 'Software Engineer')
